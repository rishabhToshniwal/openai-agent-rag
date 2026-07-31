from datetime import datetime, timezone
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter

from chroma import get_chroma_instance


def ingest_documents(file_path: str) -> bool:
    """Load a file, split into chunks, embed, and store in the shared Chroma DB."""
    try:
        if file_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)

        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        print("Creating chunks...")
        chunks = text_splitter.split_documents(documents)

        path = Path(file_path).resolve()
        ingested_at = datetime.now(timezone.utc).isoformat()
        
        print("Adding metadata to chunks...")
        for chunk in chunks:
                chunk.metadata.update(
                    {
                        "source": str(path),
                        "file_name": path.name,
                        "file_type": path.suffix.lstrip(".").lower() or "unknown",
                        "ingested_at": ingested_at,
                        "page" : chunk.metadata.get("page", None)
                    }
                )

        chroma = get_chroma_instance()
        print("Adding chunks to Chroma...")
        ids = chroma.add_documents(chunks)
        print(f"Ingested {len(ids)} chunks from {file_path}")
        return True
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        return False
