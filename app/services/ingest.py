import re
from dataclasses import dataclass, field

import chromadb
import google.generativeai as genai
import yaml
from chromadb import Documents, EmbeddingFunction, Embeddings

from app.config import settings

ARCHIVE_HEADING_MARKERS = ("arsip kebijakan v1.4",)
MAX_CHUNK_CHARS = 1400
CHUNK_OVERLAP_CHARS = 200


@dataclass
class Chunk:
    chunk_id: str
    text: str
    section_title: str
    doc_id: str
    doc_title: str
    doc_version: str
    is_active: bool
    effective_date: str = ""


@dataclass
class ParsedDoc:
    frontmatter: dict = field(default_factory=dict)
    body: str = ""


def _parse_frontmatter(raw_text: str) -> ParsedDoc:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw_text, flags=re.DOTALL)
    if not match:
        return ParsedDoc(frontmatter={}, body=raw_text)
    fm_raw, body = match.groups()
    frontmatter = yaml.safe_load(fm_raw) or {}
    return ParsedDoc(frontmatter=frontmatter, body=body)


def _split_into_sections(body: str) -> list[tuple[str, str]]:
    """Split document body on '##' headings (h2). Returns list of (heading, section_text)."""
    lines = body.split("\n")
    sections: list[tuple[str, str]] = []
    current_heading = "Pendahuluan"
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    return [(h, t) for h, t in sections if t]


def _split_into_subsections(heading: str, text: str) -> list[tuple[str, str]]:
    """Within a section, further split on '###' subheadings if present."""
    lines = text.split("\n")
    has_subheadings = any(line.startswith("### ") for line in lines)
    if not has_subheadings:
        return [(heading, text)]

    subsections: list[tuple[str, str]] = []
    current_sub = heading
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("### "):
            if current_lines:
                subsections.append((current_sub, "\n".join(current_lines).strip()))
            current_sub = f"{heading} — {line[4:].strip()}"
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        subsections.append((current_sub, "\n".join(current_lines).strip()))

    return [(h, t) for h, t in subsections if t]


def _split_long_text(text: str) -> list[str]:
    """Fallback splitter for sub-sections still longer than MAX_CHUNK_CHARS, paragraph-aware."""
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]

    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    pieces: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= MAX_CHUNK_CHARS:
            current = candidate
        else:
            if current:
                pieces.append(current)
            if len(para) <= MAX_CHUNK_CHARS:
                current = para
            else:
                for i in range(0, len(para), MAX_CHUNK_CHARS - CHUNK_OVERLAP_CHARS):
                    pieces.append(para[i : i + MAX_CHUNK_CHARS])
                current = ""

    if current:
        pieces.append(current)

    overlapped: list[str] = []
    for i, piece in enumerate(pieces):
        if i == 0:
            overlapped.append(piece)
        else:
            prev_tail = pieces[i - 1][-CHUNK_OVERLAP_CHARS:]
            overlapped.append(prev_tail + "\n\n" + piece)

    return overlapped


def _is_archive_section(heading: str) -> bool:
    heading_lower = heading.lower()
    return any(marker in heading_lower for marker in ARCHIVE_HEADING_MARKERS)


def build_chunks(raw_text: str) -> list[Chunk]:
    parsed = _parse_frontmatter(raw_text)
    fm = parsed.frontmatter

    base_doc_id = fm.get("doc_id", "UNKNOWN")
    doc_title = fm.get("doc_title", "Dokumen")
    base_version = str(fm.get("doc_version", "unknown"))
    base_effective_date = str(fm.get("effective_date", ""))

    chunks: list[Chunk] = []
    chunk_counter = 0

    for heading, section_text in _split_into_sections(parsed.body):
        for sub_heading, sub_text in _split_into_subsections(heading, section_text):
            is_archive = _is_archive_section(sub_heading)
            doc_version = "1.4" if is_archive else base_version
            doc_id = f"{base_doc_id}-v1.4-ARCHIVE" if is_archive else base_doc_id
            effective_date = "2025-01-01" if is_archive else base_effective_date
            is_active = not is_archive

            for piece in _split_long_text(sub_text):
                chunk_counter += 1
                chunks.append(
                    Chunk(
                        chunk_id=f"chunk-{chunk_counter:03d}",
                        text=piece,
                        section_title=sub_heading,
                        doc_id=doc_id,
                        doc_title=doc_title,
                        doc_version=doc_version,
                        is_active=is_active,
                        effective_date=effective_date,
                    )
                )

    return chunks


class GeminiEmbeddingFunction(EmbeddingFunction[Documents]):
    """Embedding function backed by the Gemini Embedding API.

    Avoids loading a local torch/sentence-transformers model, which keeps
    the service's memory footprint small enough for constrained cloud
    instances (loading a local multilingual model pushes RSS past 1GB).
    """

    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        genai.configure(api_key=api_key)

    def _embed(self, texts: list[str], task_type: str) -> Embeddings:
        result = genai.embed_content(model=self.model_name, content=texts, task_type=task_type)
        return result["embedding"]

    def __call__(self, input: Documents) -> Embeddings:
        return self._embed(list(input), task_type="retrieval_document")

    def embed_query(self, input: Documents) -> Embeddings:
        return self._embed(list(input), task_type="retrieval_query")

    @staticmethod
    def name() -> str:
        return "gemini_embedding_function"


def _get_embedding_function() -> GeminiEmbeddingFunction:
    return GeminiEmbeddingFunction(
        model_name=settings.embedding_model_name,
        api_key=settings.gemini_api_key,
    )


def build_or_load_index(force_rebuild: bool = False):
    client = chromadb.PersistentClient(path=str(settings.chroma_dir_path))
    embedding_fn = _get_embedding_function()

    existing_names = [c.name for c in client.list_collections()]
    if force_rebuild and settings.chroma_collection_name in existing_names:
        client.delete_collection(settings.chroma_collection_name)
        existing_names.remove(settings.chroma_collection_name)

    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() > 0 and not force_rebuild:
        return collection

    if collection.count() > 0:
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)

    raw_text = settings.source_doc_full_path.read_text(encoding="utf-8")
    chunks = build_chunks(raw_text)

    collection.add(
        ids=[c.chunk_id for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[
            {
                "section_title": c.section_title,
                "doc_id": c.doc_id,
                "doc_title": c.doc_title,
                "doc_version": c.doc_version,
                "is_active": c.is_active,
                "effective_date": c.effective_date,
            }
            for c in chunks
        ],
    )

    return collection
