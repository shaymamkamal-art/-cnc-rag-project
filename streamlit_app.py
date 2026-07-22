"""
07_prompting.py
-----------------
Stage 7 of the pipeline: PROMPTING (context -> LLM answer).

Builds a grounded prompt from the chunks returned by
06_retrieve_context.py and calls an LLM through OpenRouter to produce
the final answer, with source citations.

Per the project's API-key rules:
    - The real key is NEVER hard-coded here.
    - OPENROUTER_API_KEY / OPENROUTER_MODEL are read from environment
      variables first (local .env via python-dotenv), and the
      Streamlit app (streamlit_app.py) additionally falls back to
      st.secrets when deployed on Streamlit Cloud.
"""

import os
import importlib.util
import requests

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(_THIS_DIR, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


retrieve_mod = _import_module("06_retrieve_context.py", "retrieve_mod")

# Try to load a local .env for local development only (safe to be absent).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a CNC/manufacturing assistant for the EG Medical ZI 1 dental "
    "implant system. Answer ONLY using the provided context chunks. "
    "Every factual claim in your answer must be traceable to one of the "
    "given chunk IDs. If the context does not contain the answer, say so "
    "plainly instead of guessing. Always end your answer with a "
    "'Sources:' line listing the chunk IDs you used."
)


def build_prompt(query: str, chunks: list[dict]) -> str:
    context_block = "\n\n".join(
        f"[{c['chunk_id']}] {c['text']}" for c in chunks
    )
    return (
        f"Context:\n{context_block}\n\n"
        f"Question: {query}\n\n"
        "Answer the question using only the context above, and cite the "
        "chunk IDs you relied on."
    )


def call_openrouter(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        return (
            "[No OPENROUTER_API_KEY configured -- showing retrieved context "
            "only. Set OPENROUTER_API_KEY to get a generated answer.]\n\n" + prompt
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def answer_question(query: str, top_k: int = 3) -> dict:
    """Full RAG call: retrieve -> prompt -> generate.

    Returns {"answer": str, "chunks": list[dict]} so the caller (e.g.
    streamlit_app.py) can show both the answer and the retrieved
    evidence separately.
    """
    chunks = retrieve_mod.retrieve_context(query, top_k=top_k)
    prompt = build_prompt(query, chunks)
    answer = call_openrouter(prompt)
    return {"answer": answer, "chunks": chunks}


if __name__ == "__main__":
    demo_query = "What internal hex wrench size is broached into the implant?"
    result = answer_question(demo_query)
    print("Q:", demo_query)
    print("\nA:", result["answer"])
    print("\nRetrieved chunks:")
    for c in result["chunks"]:
        print(f"  [{c['chunk_id']}] {c['text'][:80]}")
