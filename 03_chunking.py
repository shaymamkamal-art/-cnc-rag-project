"""
03_chunking.py
---------------
Stage 3 of the pipeline: CHUNKING.

Splits each clean document's text into retrieval-sized chunks with a
word-count window and overlap, so that:
    - short documents (most of ours: one G-code operation, one catalog
      fact) stay as a single chunk,
    - any long document (e.g. a full catalog page pasted in one block)
      gets split into overlapping windows so no single chunk is too big
      for the embedding model / LLM context.

Each output chunk keeps a link back to its parent document via
`doc_id` + `chunk_index`, and copies the parent's metadata so citations
in 07_prompting.py can always point back to a real source.
"""

import importlib.util
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(_THIS_DIR, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preprocessing_mod = _import_module("02_preprocessing.py", "preprocessing_mod")

CHUNK_SIZE_WORDS = 120   # max words per chunk
CHUNK_OVERLAP_WORDS = 20  # words repeated between consecutive chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_WORDS,
               overlap: int = CHUNK_OVERLAP_WORDS) -> list[str]:
    """Word-based sliding-window chunking with overlap."""
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
        start = end - overlap  # step back for overlap
    return chunks


def chunk_all(clean_docs: list[dict] | None = None) -> list[dict]:
    """Run chunking over every clean document.

    Returns a flat list of chunk records:
        {"chunk_id", "doc_id", "source", "text", "metadata"}
    """
    if clean_docs is None:
        clean_docs = preprocessing_mod.preprocess_all()

    chunks = []
    for d in clean_docs:
        pieces = chunk_text(d["clean_text"])
        for i, piece in enumerate(pieces):
            chunk_id = d["doc_id"] if len(pieces) == 1 else f"{d['doc_id']}-C{i}"
            chunks.append({
                "chunk_id": chunk_id,
                "doc_id": d["doc_id"],
                "source": d["source"],
                "text": piece,
                "metadata": d["metadata"],
            })
    return chunks


if __name__ == "__main__":
    chunks = chunk_all()
    print(f"Produced {len(chunks)} chunks from the clean documents:")
    for c in chunks:
        print(f"  {c['chunk_id']:16s} ({len(c['text'].split())} words)  {c['text'][:60]}")
