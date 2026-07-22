import importlib.util
import os
import streamlit as st
from datetime import datetime

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
# LOGIN SYSTEM
# ----------------------------
def check_login():
    """Simple login system using Streamlit secrets."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if st.session_state.logged_in:
        return True

    # Login page styling
    st.markdown("""
    <style>
    .login-box {
        background: linear-gradient(145deg,
            rgba(15, 23, 42, 0.9) 0%,
            rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 20px;
        padding: 2.5rem;
        max-width: 420px;
        margin: 4rem auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }

    .login-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f1f5f9;
        text-align: center;
        margin-bottom: 0.3rem;
    }

    .login-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .login-icon {
        text-align: center;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-box">
            <div class="login-icon">⚙️</div>
            <div class="login-title">CNC RAG Assistant</div>
            <div class="login-subtitle">Sign in to access the system</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 10px;
        padding: 0.7rem;
        margin-bottom: 0.5rem;
    ">
        <div style="font-size:0.78rem; color:#64748b;">Signed in as</div>
        <div style="font-size:0.95rem; font-weight:600; color:#e2e8f0;">
            👤 {st.session_state.username}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.history = []
        st.rerun()
        if st.button("🔐 Sign In", use_container_width=True):
            try:
                users = dict(st.secrets.get("users", {}))
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            except Exception:
                st.error("❌ Login system not configured")

        st.markdown(
            "<div style='text-align:center; margin-top:1rem; "
            "color:#475569; font-size:0.78rem;'>"
            "Contact admin for access credentials"
            "</div>",
            unsafe_allow_html=True
        )

    return False


# Check login before showing anything
if not check_login():
    st.stop()

# ----------------------------
# Load API key
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
# Page config with custom icon
# ----------------------------
st.set_page_config(
    page_title="CNC Industrial RAG Assistant",
    page_icon="https://img.icons8.com/fluency/48/cnc-machine.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Professional Industrial Theme CSS
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

/* Main background */
.stApp {
    background: linear-gradient(160deg, #080d13 0%, #0f1923 40%, #152232 100%);
    color: #e6edf3;
}

/* Remove default padding */
.block-container {
    padding-top: 1rem !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1118 0%, #131d28 50%, #172535 100%);
    border-right: 1px solid rgba(100, 130, 160, 0.15);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #94a3b8 !important;
    font-weight: 600 !important;
}

/* Titles */
h1, h2, h3 {
    color: #e2e8f0 !important;
    letter-spacing: 0.2px;
}

/* Chat input */
[data-testid="stChatInput"] {
    background-color: rgba(20, 30, 42, 0.95) !important;
    border: 1px solid rgba(100, 130, 170, 0.3) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

[data-testid="stChatInput"]:focus-within {
    border: 1px solid rgba(59, 130, 246, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.1rem !important;
    box-shadow: 0 3px 12px rgba(59, 130, 246, 0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #3b82f6 100%);
    box-shadow: 0 5px 20px rgba(59, 130, 246, 0.35) !important;
    transform: translateY(-1px);
}

/* Warning */
.stWarning {
    background-color: rgba(120, 53, 15, 0.28) !important;
    border: 1px solid rgba(245, 158, 11, 0.35) !important;
    border-radius: 12px !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: rgba(15, 23, 35, 0.65);
    border: 1px solid rgba(100, 130, 170, 0.12);
    border-radius: 16px;
    padding: 0.5rem 0.8rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Expander */
/* Expander - fixed professional spacing */
div[data-testid="stExpander"] {
    border-radius: 12px !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"] details {
    background-color: rgba(15, 22, 32, 0.75) !important;
    border: 1px solid rgba(100, 130, 170, 0.15) !important;
    border-radius: 12px !important;
    padding: 0 !important;
}

div[data-testid="stExpander"] summary {
    padding: 0.85rem 1rem !important;
    min-height: 52px !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    white-space: normal !important;
    line-height: 1.4 !important;
}

div[data-testid="stExpander"] summary p {
    margin: 0 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #cbd5e1 !important;
    line-height: 1.4 !important;
}

div[data-testid="stExpander"] summary svg {
    flex-shrink: 0 !important;
}

div[data-testid="stExpander"] details[open] summary {
    border-bottom: 1px solid rgba(100, 130, 170, 0.12) !important;
}

/* Code */
code {
    color: #7dd3fc !important;
    background-color: rgba(15, 23, 42, 0.65) !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
}

/* Slider */
.stSlider label {
    color: #cbd5e1 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.3);
}

::-webkit-scrollbar-thumb {
    background: rgba(100, 130, 170, 0.3);
    border-radius: 999px;
}

/* Hero Box */
.hero-box {
    background: linear-gradient(145deg,
        rgba(15, 23, 42, 0.85) 0%,
        rgba(30, 41, 59, 0.75) 50%,
        rgba(51, 65, 85, 0.6) 100%);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 20px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 35px rgba(0, 0, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.04);
    position: relative;
    overflow: hidden;
}

.hero-box::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle,
        rgba(59, 130, 246, 0.08) 0%,
        transparent 70%);
    border-radius: 50%;
}

.hero-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #60a5fa;
    margin-bottom: 0.55rem;
}

.hero-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
    line-height: 1.25;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.65;
    max-width: 700px;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 0.7rem;
}

.status-ok {
    background: rgba(34, 197, 94, 0.12);
    color: #86efac;
    border: 1px solid rgba(34, 197, 94, 0.25);
}

.status-warn {
    background: rgba(245, 158, 11, 0.12);
    color: #fcd34d;
    border: 1px solid rgba(245, 158, 11, 0.25);
}

/* Metric cards */
.metric-card {
    background: linear-gradient(145deg,
        rgba(15, 23, 42, 0.7) 0%,
        rgba(30, 41, 59, 0.5) 100%);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    min-height: 100px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    transition: all 0.25s ease;
}

.metric-card:hover {
    border-color: rgba(59, 130, 246, 0.3);
    box-shadow: 0 6px 24px rgba(59, 130, 246, 0.1);
    transform: translateY(-2px);
}

.metric-icon {
    font-size: 1.8rem;
    margin-bottom: 0.4rem;
}

.metric-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}

.metric-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
}

.metric-desc {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.2rem;
}

/* Quick prompt buttons */
.prompt-section {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}

.prompt-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.6rem;
}

/* Footer */
.footer {
    text-align: center;
    padding: 1.2rem 0;
    margin-top: 2rem;
    border-top: 1px solid rgba(100, 130, 170, 0.12);
    color: #475569;
    font-size: 0.8rem;
}

.footer a {
    color: #60a5fa;
    text-decoration: none;
}

/* Timestamp */
.msg-time {
    font-size: 0.7rem;
    color: #475569;
    margin-top: 0.3rem;
}

/* Divider */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(100, 130, 170, 0.2) 50%,
        transparent 100%);
    margin: 0.8rem 0;
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

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0.8rem 0;">
        <img src="https://img.icons8.com/fluency/64/cnc-machine.png"
             width="52" style="margin-bottom:0.3rem;">
        <div style="font-size:1.15rem; font-weight:700; color:#e2e8f0;">
            CNC Assistant
        </div>
        <div style="font-size:0.75rem; color:#64748b;">
            Industrial RAG Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 10px;
        padding: 0.7rem;
        margin-bottom: 0.5rem;
    ">
        <div style="font-size:0.78rem; color:#64748b;">Signed in as</div>
        <div style="font-size:0.95rem; font-weight:600; color:#e2e8f0;">
            👤 {st.session_state.username}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.history = []
        st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("### ⚙️ Retrieval Settings")
    top_k = st.slider(
        "Context chunks to retrieve",
        min_value=1,
        max_value=8,
        value=3,
        help="More chunks = more evidence, but slower."
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 📋 Capabilities")
    st.markdown("""
    <div style="font-size:0.88rem; color:#94a3b8; line-height:1.7;">
        ● CNC programs (G-code / M-code)<br>
        ● Engineering drawings & dimensions<br>
        ● Technical specifications<br>
        ● Maintenance & troubleshooting<br>
        ● Bilingual: English & Arabic
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 📊 Session Stats")
    st.markdown(f"""
    <div style="font-size:0.85rem; color:#94a3b8;">
        Questions asked: <strong style="color:#60a5fa;">{st.session_state.query_count}</strong><br>
        Chunks per query: <strong style="color:#60a5fa;">{top_k}</strong><br>
        Model: <strong style="color:#60a5fa;">{rag.OPENROUTER_MODEL.split('/')[-1]}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑 Clear Conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.query_count = 0
        st.session_state.selected_prompt = ""
        st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Add a PDF to the knowledge base",
        type=["pdf"],
        help="Upload a PDF and it will be added to the RAG knowledge base immediately."
    )

    if uploaded_file is not None:
        if st.button("➕ Add to Knowledge Base", use_container_width=True):
            with st.spinner("Processing PDF..."):
                try:
                    doc_mgr = _import_module("document_manager.py", "doc_mgr")
                    result = doc_mgr.add_pdf_to_store(
                        uploaded_file.read(),
                        uploaded_file.name
                    )

                    if result["status"] == "success":
                        st.success(
                            f"✅ Added **{result['filename']}**\n\n"
                            f"Chunks added: **{result['chunks_added']}**"
                        )
                    else:
                        st.error(f"❌ {result['status']}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 📚 Knowledge Base")

    if st.button("🔄 Refresh Document List", use_container_width=True):
        st.rerun()

    try:
        doc_mgr = _import_module("document_manager.py", "doc_mgr")
        docs = doc_mgr.list_uploaded_docs()

        if docs:
            for doc in docs:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    icon = "📤" if doc["uploaded"] else "📋"
                    st.markdown(
                        f"{icon} **{doc['source']}**\n\n"
                        f"<span style='color:#64748b; font-size:0.78rem;'>"
                        f"{doc['chunks']} chunks</span>",
                        unsafe_allow_html=True
                    )
                with col_b:
                    if st.button(
                        "🗑",
                        key=f"del_{doc['doc_id']}",
                        help=f"Remove {doc['source']}"
                    ):
                        result = doc_mgr.delete_doc_from_store(doc["doc_id"])
                        if result["status"] == "deleted":
                            st.success("Removed!")
                            st.rerun()
        else:
            st.markdown(
                "<span style='color:#475569; font-size:0.85rem;'>"
                "No documents found.</span>",
                unsafe_allow_html=True
            )

    except Exception as e:
        st.markdown(
            f"<span style='color:#ef4444;'>Error loading docs: {e}</span>",
            unsafe_allow_html=True
        )

    st.markdown("""
    <div style="text-align:center; margin-top:1.5rem;">
        <div style="font-size:0.7rem; color:#334155;">
            Powered by RAG + LLM<br>
            Built with Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# Hero Section
# ----------------------------
status_html = """
<span class="status-badge status-ok">● System Online</span>
""" if rag.OPENROUTER_API_KEY else """
<span class="status-badge status-warn">⚠ Retrieval Only</span>
"""

st.markdown(f"""
<div class="hero-box">
    <div class="hero-label">Industrial Knowledge System</div>
    <div class="hero-title">CNC Industrial RAG Assistant</div>
    <div class="hero-subtitle">
        AI-powered technical assistant for the EG Medical ZI 1 dental implant system.
        Get verified answers from CNC programs, engineering drawings,
        and manufacturing specifications — in English or Arabic.
    </div>
    {status_html}
</div>
""", unsafe_allow_html=True)

if not rag.OPENROUTER_API_KEY:
    st.warning(
        "No OPENROUTER_API_KEY found. Context retrieval is active, "
        "but AI-generated answers require a valid API key in Streamlit Secrets."
    )

# ----------------------------
# Metric Cards
# ----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">📐</div>
        <div class="metric-title">Engineering</div>
        <div class="metric-value">Drawings & Specs</div>
        <div class="metric-desc">Verified dimensions</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🔩</div>
        <div class="metric-title">CNC Programs</div>
        <div class="metric-value">G-code & M-code</div>
        <div class="metric-desc">Machining logic</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🛡️</div>
        <div class="metric-title">Grounded</div>
        <div class="metric-value">Source-cited</div>
        <div class="metric-desc">Traceable answers</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🌍</div>
        <div class="metric-title">Bilingual</div>
        <div class="metric-value">EN / AR</div>
        <div class="metric-desc">Ask in any language</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ----------------------------
# Quick Prompts
# ----------------------------
st.markdown("""
<div class="prompt-section">
    <div class="prompt-label">Quick Questions</div>
</div>
""", unsafe_allow_html=True)

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("🔧 Hex wrench size", use_container_width=True):
        st.session_state.selected_prompt = (
            "What internal hex wrench size is broached into the implant?"
        )
with q2:
    if st.button("📐 Platform dimensions", use_container_width=True):
        st.session_state.selected_prompt = (
            "What are the main platform dimensions in the ZI 1 system?"
        )
with q3:
    if st.button("💻 CNC programs", use_container_width=True):
        st.session_state.selected_prompt = (
            "What CNC programs are referenced for the ZI 1 implant?"
        )
with q4:
    if st.button("🇪🇬 اسأل بالعربي", use_container_width=True):
        st.session_state.selected_prompt = (
            "ما هي أهم المواصفات الفنية لنظام ZI 1؟"
        )

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ----------------------------
# Chat History
# ----------------------------
for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        if "time" in turn:
            st.markdown(
                f'<div class="msg-time">{turn["time"]}</div>',
                unsafe_allow_html=True
            )

# ----------------------------
# Chat Input
# ----------------------------
query = st.chat_input(
    "Ask your CNC question here... / اكتب سؤالك هنا..."
)

if not query and st.session_state.selected_prompt:
    query = st.session_state.selected_prompt
    st.session_state.selected_prompt = ""

# ----------------------------
# Process Query
# ----------------------------
# ----------------------------
# Process Query
# ----------------------------
if query:
    now = datetime.now().strftime("%H:%M")

    st.session_state.history.append({
        "role": "user",
        "content": query,
        "time": now
    })

    with st.chat_message("user"):
        st.markdown(query)
        st.markdown(
            f'<div class="msg-time">{now}</div>',
            unsafe_allow_html=True
        )

    with st.chat_message("assistant"):
        with st.spinner("🔍 Retrieving context and generating answer..."):
            result = rag.answer_question(query, top_k=top_k)

        st.markdown(result["answer"])

        ans_time = datetime.now().strftime("%H:%M")
        st.markdown(
            f'<div class="msg-time">{ans_time}</div>',
            unsafe_allow_html=True
        )

        with st.expander("📚 Retrieved Sources"):
            st.caption(f"{len(result['chunks'])} chunks retrieved")

            for i, c in enumerate(result["chunks"], 1):
                st.markdown(
                    f"**{i}. Chunk** `{c['chunk_id']}` "
                    f"&nbsp;|&nbsp; **Distance:** `{c['distance']:.3f}`"
                )
                st.code(c["text"], language="text")

                if i < len(result["chunks"]):
                    st.markdown(
                        '<div class="custom-divider"></div>',
                        unsafe_allow_html=True
                    )

    st.session_state.history.append({
        "role": "assistant",
        "content": result["answer"],
        "time": ans_time
    })

    st.session_state.query_count += 1

# ----------------------------
# Footer
# ----------------------------
st.markdown("""
<div class="footer">
    CNC Industrial RAG Assistant — Built for precision manufacturing intelligence.<br>
    <span style="color:#334155;">
        EG Medical ZI 1 System | Powered by RAG + LLM
    </span>
</div>
""", unsafe_allow_html=True)
