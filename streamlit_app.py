import importlib.util
import os
import streamlit as st

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(_THIS_DIR, filename)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rag = _import_module("07_prompting.py", "rag")

# Read secrets
try:
    if not rag.OPENROUTER_API_KEY:
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get(
        "OPENROUTER_MODEL", rag.OPENROUTER_MODEL
    )
except Exception:
    pass

st.set_page_config(
    page_title="CNC RAG Assistant",
    page_icon="⚙️",
    layout="wide"
)

# Simple safe styling
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
h1, h2, h3 {
    color: #4da6ff;
}
section[data-testid="stSidebar"] {
    background-color: #161b22;
}
</style>
""", unsafe_allow_html=True)

st.title("⚙️ CNC RAG Assistant")
st.caption("Ask questions about the EG Medical ZI 1 system in English or Arabic.")

if not rag.OPENROUTER_API_KEY:
    st.warning("No OPENROUTER_API_KEY found. Retrieval will work, but no AI answer will be generated.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Retrieved Chunks (top_k)", 1, 8, 3)

    if st.button("Clear Conversation"):
        st.session_state.history = []
        st.rerun()

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

query = st.chat_input("Ask in English or Arabic...")

if query:
    st.session_state.history.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating an answer..."):
            result = rag.answer_question(query, top_k=top_k)

        st.markdown(result["answer"])

        with st.expander("View Sources"):
            for c in result["chunks"]:
                st.markdown(f"**[{c['chunk_id']}]** (distance={c['distance']:.3f})")
                st.code(c["text"], language="text")

    st.session_state.history.append({"role": "assistant", "content": result["answer"]})
