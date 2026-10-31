from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-2.0-flash"
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    chroma_dir: str = "chroma_db"
    chroma_collection_name: str = "nusantaracare_kb"
    source_doc_path: str = "data/raw_docs/nusantaracare_panduan_operasional_internal_v2.md"
    top_k: int = 4
    similarity_threshold: float = 0.35

    @property
    def chroma_dir_path(self) -> Path:
        path = Path(self.chroma_dir)
        return path if path.is_absolute() else BASE_DIR / path

    @property
    def source_doc_full_path(self) -> Path:
        path = Path(self.source_doc_path)
        return path if path.is_absolute() else BASE_DIR / path


settings = Settings()
