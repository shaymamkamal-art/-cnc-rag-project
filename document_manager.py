"""
document_manager.py
--------------------
Handles adding new PDF documents to the existing Chroma store
at runtime (from the Streamlit UI) without rebuilding everything.
"""

import os
import re
import importlib.util
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(_THIS_DIR, filename)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


store_mod = _import_module("05_create_chroma_store.py", "store_mod")
vector_mod = _import_module("04_vector_representation.py", "vector_mod")
chunking_mod = _import_module("03_chunking.py", "chunking_mod")


# -------------------------------------------------------------------
# PDF reading
# -------------------------------------------------------------------
def extract_text_from_pdf(pdf_bytes: bytes, filename: str) -> str:
    """Extract raw text from a PDF file (given as bytes)."""
    try:
        import pypdf
        import io
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n\n".join(pages)
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF '{filename}': {e}")


# -------------------------------------------------------------------
# Text cleaning (same logic as 02_preprocessing.py)
# -------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Basic cleaning: normalize whitespace and remove junk chars."""
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text


# -------------------------------------------------------------------
# Chunking (same logic as 03_chunking.py)
# -------------------------------------------------------------------
def chunk_text(text: str,
               chunk_size: int = 120,
               overlap: int = 20) -> list[str]:
    """Word-based sliding-window chunking."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks


# -------------------------------------------------------------------
# Main function: add PDF to Chroma
# -------------------------------------------------------------------
def add_pdf_to_store(pdf_bytes: bytes, filename: str) -> dict:
    """
    Full pipeline for a new PDF:
    read -> clean -> chunk -> embed -> add to Chroma

    Returns:
        {
            "filename": str,
            "chunks_added": int,
            "doc_id": str,
            "status": str
        }
    """
    # 1. Read PDF
    raw_text = extract_text_from_pdf(pdf_bytes, filename)

    if not raw_text.strip():
        return {
            "filename": filename,
            "chunks_added": 0,
            "doc_id": None,
            "status": "error: PDF appears to be empty or image-based (no text found)"
        }

    # 2. Clean text
    clean = clean_text(raw_text)

    # 3. Make doc_id from filename
    doc_id = re.sub(r'[^a-zA-Z0-9_-]', '_', filename.replace('.pdf', ''))

    # 4. Chunk
    pieces = chunk_text(clean)

    # 5. Build chunk records
    chunk_records = []
    for i, piece in enumerate(pieces):
        chunk_id = doc_id if len(pieces) == 1 else f"{doc_id}-C{i}"
        chunk_records.append({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "source": filename,
            "text": piece,
            "metadata": {
                "source": filename,
                "doc_id": doc_id,
                "chunk_index": i,
                "uploaded": True,
            }
        })

    # 6. Get existing Chroma collection
    client = store_mod.get_chroma_client()
    try:
        collection = client.get_collection(store_mod.COLLECTION_NAME)
    except Exception:
        collection = store_mod.build_store()

    # 7. Check for duplicate doc_id and remove old version
    try:
        existing = collection.get(where={"doc_id": doc_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    # 8. Embed and add
    texts = [c["text"] for c in chunk_records]
    embeddings = vector_mod.embed_texts(texts)

    ids = [c["chunk_id"] for c in chunk_records]
    metadatas = [
        {k: v for k, v in c["metadata"].items()
         if isinstance(v, (str, int, float, bool))}
        for c in chunk_records
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "filename": filename,
        "chunks_added": len(chunk_records),
        "doc_id": doc_id,
        "status": "success"
    }


# -------------------------------------------------------------------
# List uploaded documents
# -------------------------------------------------------------------
def list_uploaded_docs() -> list[dict]:
    """Return list of documents currently in the Chroma store."""
    try:
        client = store_mod.get_chroma_client()
        collection = client.get_collection(store_mod.COLLECTION_NAME)
        results = collection.get()

        docs = {}
        for i, meta in enumerate(results["metadatas"]):
            doc_id = meta.get("doc_id", "unknown")
            if doc_id not in docs:
                docs[doc_id] = {
                    "doc_id": doc_id,
                    "source": meta.get("source", "unknown"),
                    "chunks": 0,
                    "uploaded": meta.get("uploaded", False)
                }
            docs[doc_id]["chunks"] += 1

        return list(docs.values())

    except Exception:
        return []


# -------------------------------------------------------------------
# Delete a document
# -------------------------------------------------------------------
def delete_doc_from_store(doc_id: str) -> dict:
    """Remove all chunks of a document from Chroma."""
    try:
        client = store_mod.get_chroma_client()
        collection = client.get_collection(store_mod.COLLECTION_NAME)

        existing = collection.get(where={"doc_id": doc_id})
        if not existing["ids"]:
            return {"status": "not found", "doc_id": doc_id}

        collection.delete(ids=existing["ids"])
        return {
            "status": "deleted",
            "doc_id": doc_id,
            "chunks_removed": len(existing["ids"])
        }
    except Exception as e:
        return {"status": f"error: {e}", "doc_id": doc_id}
