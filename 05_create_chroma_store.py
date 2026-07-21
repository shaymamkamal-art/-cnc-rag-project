"""
05_create_chroma_store.py
---------------------------
Stage 5 of the pipeline: VECTOR STORE.

Builds (or rebuilds) a persistent ChromaDB collection from every chunk
produced in 03_chunking.py, using the embeddings from
04_vector_representation.py.

Run this file directly whenever the source documents change:
    python 05_create_chroma_store.py

It persists to ./chroma_store/ so 06_retrieve_context.py (and the
Streamlit app) can just open the existing collection without
re-embedding everything on every query.
"""

import os
import importlib.util

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(_THIS_DIR, "chroma_store")
COLLECTION_NAME = "cnc_rag_collection"


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(_THIS_DIR, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


chunking_mod = _import_module("03_chunking.py", "chunking_mod")
vector_mod = _import_module("04_vector_representation.py", "vector_mod")


def get_chroma_client():
    import chromadb
    return chromadb.PersistentClient(path=CHROMA_DIR)


def build_store(chunks: list[dict] | None = None):
    """(Re)create the Chroma collection from scratch and populate it."""
    import chromadb

    if chunks is None:
        chunks = chunking_mod.chunk_all()

    client = get_chroma_client()

    # Start clean every time this script is run, so stale chunks never linger.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    # Chroma metadata values must be str/int/float/bool -- flatten anything else.
    metadatas = []
    for c in chunks:
        meta = dict(c["metadata"])
        meta["source"] = c["source"]
        meta["doc_id"] = c["doc_id"]
        metadatas.append({k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool))})

    embeddings = vector_mod.embed_texts(texts)

    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    return collection


if __name__ == "__main__":
    collection = build_store()
    print(f"Chroma collection '{COLLECTION_NAME}' built at {CHROMA_DIR}")
    print(f"Total chunks stored: {collection.count()}")
