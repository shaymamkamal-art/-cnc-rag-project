"""
07_prompting.py
-----------------
Stage 7: PROMPTING (context -> LLM answer).

Builds a grounded prompt from retrieved chunks and calls an LLM
through OpenRouter. Supports automatic language detection so the
assistant replies in the same language the user asked in.
"""

import os
import re
import importlib.util
import requests

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(_THIS_DIR, filename)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


retrieve_mod = _import_module("06_retrieve_context.py", "retrieve_mod")

# Load .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# -------------------------------------------------------------------
# Language detection
# -------------------------------------------------------------------
def _is_arabic(text: str) -> bool:
    """Check if the text contains Arabic characters."""
    arabic_pattern = re.compile(
        r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF'
        r'\uFB50-\uFDFF\uFE70-\uFEFF]'
    )
    arabic_chars = len(arabic_pattern.findall(text))
    total_chars = len(text.strip())
    if total_chars == 0:
        return False
    return (arabic_chars / total_chars) > 0.3


# -------------------------------------------------------------------
# System prompts
# -------------------------------------------------------------------
SYSTEM_PROMPT_EN = (
    "You are a professional CNC and manufacturing assistant for the "
    "EG Medical ZI 1 dental implant system.\n\n"
    "Rules:\n"
    "1. Answer ONLY using the provided context chunks.\n"
    "2. Every factual claim must be traceable to a chunk ID.\n"
    "3. If the context does not contain the answer, say so clearly.\n"
    "4. Always end with a 'Sources:' line listing chunk IDs used.\n"
    "5. Use clear formatting with bullet points or numbered steps.\n"
    "6. Be precise with dimensions, codes, and specifications.\n"
    "7. Reply in English."
)

SYSTEM_PROMPT_AR = (
    "أنت مساعد احترافي متخصص في ماكينات CNC والتصنيع لنظام "
    "EG Medical ZI 1 لزراعة الأسنان.\n\n"
    "القواعد:\n"
    "1. أجب فقط باستخدام السياق المقدم (chunks).\n"
    "2. كل معلومة يجب أن تكون مرتبطة بـ chunk ID معين.\n"
    "3. إذا لم يحتوِ السياق على الإجابة، قل ذلك بوضوح.\n"
    "4. اختم إجابتك دائماً بسطر 'المصادر:' مع أرقام الـ chunks.\n"
    "5. استخدم تنسيقاً واضحاً مع نقاط أو خطوات مرقمة.\n"
    "6. كن دقيقاً في الأبعاد والأكواد والمواصفات.\n"
    "7. أجب باللغة العربية."
)


# -------------------------------------------------------------------
# Prompt builder
# -------------------------------------------------------------------
def build_prompt(query: str, chunks: list[dict], is_arabic: bool) -> str:
    """Build the user prompt from query and retrieved chunks."""
    context_block = "\n\n".join(
        f"[{c['chunk_id']}] {c['text']}" for c in chunks
    )

    if is_arabic:
        return (
            f"السياق:\n{context_block}\n\n"
            f"السؤال: {query}\n\n"
            "أجب عن السؤال باستخدام السياق أعلاه فقط، "
            "واذكر أرقام الـ chunks التي اعتمدت عليها. "
            "أجب باللغة العربية."
        )
    else:
        return (
            f"Context:\n{context_block}\n\n"
            f"Question: {query}\n\n"
            "Answer the question using only the context above, "
            "and cite the chunk IDs you relied on. "
            "Reply in English."
        )


# -------------------------------------------------------------------
# LLM call
# -------------------------------------------------------------------
def call_openrouter(prompt: str, system_prompt: str) -> str:
    """Send prompt to OpenRouter and return the response."""
    if not OPENROUTER_API_KEY:
        return (
            "[No OPENROUTER_API_KEY configured — showing retrieved "
            "context only. Set OPENROUTER_API_KEY to get a generated "
            "answer.]\n\n" + prompt
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. Please try again."

    except requests.exceptions.HTTPError as e:
        return f"⚠️ API Error: {str(e)}"

    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"


# -------------------------------------------------------------------
# Main function
# -------------------------------------------------------------------
def answer_question(query: str, top_k: int = 3) -> dict:
    """Full RAG call: retrieve -> detect language -> prompt -> generate.

    Returns:
        {
            "answer": str,
            "chunks": list[dict],
            "language": str
        }
    """
    # Step 1: Retrieve
    chunks = retrieve_mod.retrieve_context(query, top_k=top_k)

    # Step 2: Detect language
    arabic = _is_arabic(query)
    language = "ar" if arabic else "en"

    # Step 3: Build prompt
    prompt = build_prompt(query, chunks, is_arabic=arabic)

    # Step 4: Select system prompt
    system_prompt = SYSTEM_PROMPT_AR if arabic else SYSTEM_PROMPT_EN

    # Step 5: Generate answer
    answer = call_openrouter(prompt, system_prompt)

    return {
        "answer": answer,
        "chunks": chunks,
        "language": language
    }


# -------------------------------------------------------------------
# Quick test
# -------------------------------------------------------------------
if __name__ == "__main__":
    # English test
    print("=== English Test ===")
    en_result = answer_question(
        "What internal hex wrench size is broached into the implant?"
    )
    print("Q: What internal hex wrench size?")
    print(f"Language: {en_result['language']}")
    print(f"A: {en_result['answer']}\n")

    # Arabic test
    print("=== Arabic Test ===")
    ar_result = answer_question(
        "ما هو حجم مفتاح الهكس الداخلي؟"
    )
    print("Q: ما هو حجم مفتاح الهكس الداخلي؟")
    print(f"Language: {ar_result['language']}")
    print(f"A: {ar_result['answer']}")
