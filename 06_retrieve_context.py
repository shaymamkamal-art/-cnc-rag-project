"""
06_retrieve_context.py
------------------------
Stage 6 of the pipeline: CONTEXT RETRIEVAL.
"""

import os
import importlib.util

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(_THIS_DIR, filename)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


store_mod = _import_module("05_create_chroma_store.py", "store_mod")
vector_mod = _import_module("04_vector_representation.py", "vector_mod")

_collection = None


def _get_collection():
    """Open the existing persisted collection (build it once if missing)."""
    global _collection

    if _collection is not None:
        return _collection

    client = store_mod.get_chroma_client()

    try:
        _collection = client.get_collection(store_mod.COLLECTION_NAME)
    except Exception:
        _collection = store_mod.build_store()

    return _collection


def retrieve_context(query: str, top_k: int = 3) -> list[dict]:
    """Return the top_k most relevant chunks."""

    collection = _get_collection()
    query_vec = vector_mod.embed_query(query)

    result = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k
    )

    hits = []

    for i in range(len(result["ids"][0])):
        hits.append({
            "chunk_id": result["ids"][0][i],
            "text": result["documents"][0][i],
            "metadata": result["metadatas"][0][i],
            "source": result["metadatas"][0][i].get("source"),
            "distance": result["distances"][0][i],
        })

    # ================= DEBUG ==================
    print("=" * 80)
    print("QUERY:", query)

    for h in hits:
        print()
        print("Distance:", h["distance"])
        print("Source:", h["source"])
        print("Metadata:", h["metadata"])
        print("Text:")
        print(h["text"][:600])

    print("=" * 80)
    # ==========================================

    return hits


if __name__ == "__main__":
    demo_query = "What internal hex wrench size is broached into the implant?"

    hits = retrieve_context(demo_query, top_k=3)

    print(f"\nQuery: {demo_query}\n")

    for h in hits:
        print(f"[{h['chunk_id']}] ({h['distance']:.3f})")
        print(h["text"][:100])
        print()
