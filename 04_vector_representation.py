"""
04_vector_representation.py
-----------------------------
Stage 4 of the pipeline: VECTOR REPRESENTATION.

Turns chunk text into embedding vectors.

We use a local, free sentence-transformers multilingual model
(`intfloat/multilingual-e5-small`) for embeddings -- this needs NO API
key, works fully offline, and supports both English and Arabic queries,
which keeps the required OPENROUTER_API_KEY reserved for what it is
actually needed for: the generation step in 07_prompting.py.

NOTE: e5 models require a "query: " / "passage: " prefix on the input
text to work correctly -- this is not optional, it's how the model was
trained. Do not remove the prefixing below.

If you change this model, you MUST rebuild the Chroma store afterwards
by running 05_create_chroma_store.py again, otherwise the collection
will still hold embeddings from the old model.
"""
from functools import lru_cache

_MODEL_NAME = "intfloat/multilingual-e5-small"


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings (used for documents/chunks at index time).

    Returns a list of float vectors (same order).
    """
    model = _get_model()
    prefixed = [f"passage: {t}" for t in texts]
    vectors = model.encode(prefixed, show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string (used at retrieval time)."""
    model = _get_model()
    vector = model.encode([f"query: {query}"], show_progress_bar=False, normalize_embeddings=True)
    return vector.tolist()[0]


if __name__ == "__main__":
    sample = [
        "What internal hex wrench size is broached into the implant?",
        "Operation 'Broaching' in Platform3_4.NC (Path 2 (sub-spindle - internal hex/thread)), uses tool(s) T2300.",
    ]
    vecs = embed_texts(sample)
    print(f"Embedded {len(vecs)} texts, each of dimension {len(vecs[0])}.")
