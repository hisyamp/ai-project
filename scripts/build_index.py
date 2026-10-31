import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ingest import build_or_load_index  # noqa: E402

if __name__ == "__main__":
    collection = build_or_load_index(force_rebuild=True)
    print(f"Index built. Total chunks: {collection.count()}")
