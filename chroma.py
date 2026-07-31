import shutil
from pathlib import Path

from langchain_chroma import Chroma

from openai_embeddings import embeddings

PERSIST_DIRECTORY = Path("emb")
COLLECTION_NAME = "documents"

_db: Chroma | None = None


def get_chroma_instance() -> Chroma:
    """Return a single persistent Chroma instance (reused across the app)."""
    global _db
    if _db is None:
        PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)
        _db = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(PERSIST_DIRECTORY),
        )
    return _db


def reset_chroma_instance() -> Chroma:
    """Delete the on-disk Chroma store and create a fresh empty instance."""
    global _db
    if _db is not None:
        try:
            _db.delete_collection()
        except Exception:
            pass
        _db = None

    if PERSIST_DIRECTORY.exists():
        shutil.rmtree(PERSIST_DIRECTORY)

    return get_chroma_instance()
