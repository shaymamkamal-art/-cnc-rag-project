"""
04_vector_representation.py
-----------------------------
Stage 4 of the pipeline: VECTOR REPRESENTATION.

Turns chunk text into embedding vectors.

We use a local, free sentence-transformers model
(`all-MiniLM-L6-v2`) for embeddings -- this needs NO API key and works
fully offline, which keeps the required OPENROUTER_API_KEY reserved for
what it is actually needed for: the generation step in 07_prompting.py.

If you would rather use OpenAI/OpenRouter embeddings instead, swap the
implementation of `embed_texts()` below -- everything downstream
(05_create_chroma_store.py, 06_retrieve_context.py) only calls this
function and does not care how the vectors were produced.
"""

from functools import lru_cache

_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings. Returns a list of float vectors (same order)."""
    model = _get_model()
    vectors = model.encode(list(texts), show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string (used at retrieval time)."""
    return embed_texts([query])[0]


if __name__ == "__main__":
    sample = [
        "What internal hex wrench size is broached into the implant?",
        "Operation 'Broaching' in Platform3_4.NC (Path 2 (sub-spindle - internal hex/thread)), uses tool(s) T2300.",
    ]
    vecs = embed_texts(sample)
    print(f"Embedded {len(vecs)} texts, each of dimension {len(vecs[0])}.")
