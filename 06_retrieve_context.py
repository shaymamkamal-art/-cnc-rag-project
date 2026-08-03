def retrieve_context(query: str, top_k: int = 3) -> list[dict]:
    """Return the top_k most relevant chunks for `query`.

    Each result: {"chunk_id", "text", "source", "metadata", "distance"}
    """
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

    # ================= Debug =================
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
    # =========================================

    return hits
