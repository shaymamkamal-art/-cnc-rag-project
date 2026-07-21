"""
streamlit_app.py
------------------
Final stage: STREAMLIT UI.

Wires the whole pipeline (01 -> 07) into a chat-style assistant for the
EG Medical ZI 1 CNC/RAG project.

Deployment notes (Streamlit Cloud):
    1. Push this whole project to a GitHub repo (see README for the
       required file list).
    2. On share.streamlit.io, create a new app pointing at this repo,
       main file = streamlit_app.py.
    3. In the deployed app: Manage app -> Secrets, paste:

           OPENROUTER_API_KEY = "your_openrouter_key_here"
           OPENROUTER_MODEL = "openai/gpt-4o-mini"

    4. Do NOT put your real key in this file or in a committed .env.
"""

import importlib.util
import os

import streamlit as st

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(_THIS_DIR, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rag = _import_module("07_prompting.py", "rag")

# ---------------------------------------------------------------------------
# Read the API key/model from Streamlit secrets when deployed (falls back to
# whatever 07_prompting.py already loaded from a local .env, if any).
# ---------------------------------------------------------------------------
try:
    if not rag.OPENROUTER_API_KEY:
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", rag.OPENROUTER_MODEL)
except Exception:
    pass

st.set_page_config(page_title="ZI 1 CNC RAG Assistant", page_icon="🛠️")
st.title("🛠️ ZI 1 Implant CNC RAG Assistant")
st.caption(
    "Ask about the EG Medical ZI 1 dental implant system: catalog specs, "
    "engineering drawings, and verified CNC machining programs "
    "(O3710.NC, Platform3_4.NC, O3711.NC)."
)

if not rag.OPENROUTER_API_KEY:
    st.warning(
        "No OPENROUTER_API_KEY found. The app will still retrieve and show "
        "context, but won't generate an LLM answer until a key is configured "
        "in Streamlit Secrets (or a local .env for development)."
    )

if "history" not in st.session_state:
    st.session_state.history = []

top_k = st.sidebar.slider("Number of retrieved chunks (top_k)", min_value=1, max_value=8, value=3)

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

query = st.chat_input("Ask a question about the ZI 1 system or its CNC programs...")

if query:
    st.session_state.history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating an answer..."):
            result = rag.answer_question(query, top_k=top_k)

        st.markdown(result["answer"])

        with st.expander("Show retrieved context (sources)"):
            for c in result["chunks"]:
                st.markdown(f"**[{c['chunk_id']}]** (distance={c['distance']:.3f})")
                st.code(c["text"], language="text")

    st.session_state.history.append({"role": "assistant", "content": result["answer"]})
