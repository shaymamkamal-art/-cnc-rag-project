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

# ----------------------------
# Load API key from Streamlit secrets
# ----------------------------
try:
    if not rag.OPENROUTER_API_KEY:
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get(
        "OPENROUTER_MODEL", rag.OPENROUTER_MODEL
    )
except Exception:
    pass

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="CNC Industrial RAG Assistant",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Industrial Theme CSS
# ----------------------------
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #0f1720 0%, #18222d 45%, #1d2b36 100%);
    color: #e6edf3;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111820 0%, #1a2530 100%);
    border-right: 1px solid rgba(140, 160, 180, 0.25);
}

/* Main titles */
h1, h2, h3 {
    color: #dce6ee !important;
    letter-spacing: 0.3px;
}

/* Paragraphs */
p, label, div {
    color: #d9e2ea;
}

/* Chat input */
[data-testid="stChatInput"] {
    background-color: rgba(28, 38, 49, 0.95) !important;
    border: 1px solid rgba(120, 145, 170, 0.35) !important;
    border-radius: 14px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #64748b 100%);
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #475569 100%);
    color: white !important;
}

/* Slider text */
.stSlider label {
    color: #dce6ee !important;
}

/* Expander */
details {
    background-color: rgba(22, 30, 40, 0.7);
    border: 1px solid rgba(120, 145, 170, 0.25);
    border-radius: 10px;
    padding: 0.4rem;
}

/* Warning box */
.stWarning {
    background-color: rgba(120, 53, 15, 0.35) !important;
    border: 1px solid rgba(245, 158, 11, 0.45) !important;
    border-radius: 10px !important;
}

/* Chat message blocks */
[data-testid="stChatMessage"] {
    background-color: rgba(18, 26, 34, 0.7);
    border: 1px solid rgba(120, 145, 170, 0.18);
    border-radius: 14px;
    padding: 0.4rem 0.7rem;
    margin-bottom: 0.8rem;
}

/* Code block */
code {
    color: #93c5fd !important;
}

/* Hero card */
.hero-box {
    background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(51,65,85,0.85) 100%);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.18);
}

.hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.4rem;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 1rem;
    line-height: 1.6;
}

/* Info cards */
.info-card {
    background: rgba(19, 28, 36, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    padding: 1rem;
    min-height: 120px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.14);
}

.info-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.35rem;
}

.info-text {
    color: #cbd5e1;
    font-size: 0.94rem;
    line-height: 1.5;
}

/* Status badge */
.status-badge {
    display: inline-block;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.4rem;
}

.status-ok {
    background: rgba(34,197,94,0.14);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.3);
}

.status-warn {
    background: rgba(245,158,11,0.14);
    color: #fcd34d;
    border: 1px solid rgba(245,158,11,0.3);
}

/* Section label */
.section-label {
    color: #93c5fd;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin-top: 0.2rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Session state
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = ""

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown("## ⚙️ CNC Control Panel")
    st.markdown("Industrial assistant settings and tools.")

    st.markdown("---")
    st.markdown("### Retrieval Settings")
    top_k = st.slider(
        "Retrieved chunks",
        min_value=1,
        max_value=8,
        value=3,
        help="Higher values provide more evidence, but may slow response time."
    )

    st.markdown("---")
    st.markdown("### Assistant Scope")
    st.markdown("""
- CNC programs and machining logic  
- Engineering drawings and dimensions  
- Technical specifications  
- Maintenance and troubleshooting  
- Arabic / English questions
""")

    st.markdown("---")
    if st.button("🗑 Clear Conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.selected_prompt = ""
        st.rerun()

# ----------------------------
# Header / Hero
# ----------------------------
status_html = """
<span class="status-badge status-ok">LLM Ready</span>
""" if rag.OPENROUTER_API_KEY else """
<span class="status-badge status-warn">Retrieval Only</span>
"""

st.markdown(f"""
<div class="hero-box">
    <div class="section-label">Industrial Knowledge Assistant</div>
    <div class="hero-title">⚙️ CNC Industrial RAG Assistant</div>
    <div class="hero-subtitle">
        A professional AI assistant for CNC-related technical guidance, verified program context,
        engineering references, and manufacturing support for the EG Medical ZI 1 system.
        Ask in English or Arabic — the assistant should respond accordingly.
    </div>
    {status_html}
</div>
""", unsafe_allow_html=True)

if not rag.OPENROUTER_API_KEY:
    st.warning(
        "No OPENROUTER_API_KEY found. The app can retrieve relevant context, "
        "but it will not generate a full AI answer until the API key is configured in Streamlit Secrets."
    )

# ----------------------------
# Top cards
# ----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">📐 Engineering Context</div>
        <div class="info-text">
            Retrieve dimensions, drawings, specifications, and verified design-related references.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">🧠 Grounded AI Answers</div>
        <div class="info-text">
            Answers are built from retrieved chunks to reduce hallucination and keep responses traceable.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">🌍 Bilingual Usage</div>
        <div class="info-text">
            The interface is professional and English-based, while users can ask questions in Arabic or English.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ----------------------------
# Quick prompts
# ----------------------------
st.markdown("### Suggested Questions")

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("Internal hex size?", use_container_width=True):
        st.session_state.selected_prompt = "What internal hex wrench size is broached into the implant?"
with q2:
    if st.button("Platform dimensions", use_container_width=True):
        st.session_state.selected_prompt = "What are the main platform dimensions in the ZI 1 system?"
with q3:
    if st.button("CNC program guidance", use_container_width=True):
        st.session_state.selected_prompt = "What CNC programs are referenced for the ZI 1 implant system?"
with q4:
    if st.button("اسأل بالعربي", use_container_width=True):
        st.session_state.selected_prompt = "ما هي أهم المواصفات أو الأبعاد المتعلقة بنظام ZI 1؟"

# ----------------------------
# Show old conversation
# ----------------------------
for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

# ----------------------------
# Chat input
# ----------------------------
query = st.chat_input(
    "Ask your CNC question here... / اكتب سؤالك هنا..."
)

if not query and st.session_state.selected_prompt:
    query = st.session_state.selected_prompt
    st.session_state.selected_prompt = ""

# ----------------------------
# Ask
# ----------------------------
if query:
    st.session_state.history.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing retrieved context and generating answer..."):
            result = rag.answer_question(query, top_k=top_k)

        st.markdown(result["answer"])

        with st.expander("📚 Retrieved Sources"):
            for c in result["chunks"]:
                st.markdown(
                    f"**Chunk ID:** `{c['chunk_id']}` &nbsp;&nbsp; "
                    f"**Distance:** `{c['distance']:.3f}`"
                )
                st.code(c["text"], language="text")

    st.session_state.history.append(
        {"role": "assistant", "content": result["answer"]}
    )
