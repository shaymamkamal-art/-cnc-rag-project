"""
02_preprocessing.py
--------------------
Stage 2 of the pipeline: PREPROCESSING / CLEANING.

Takes the raw documents from 01_documents.py and turns each one into a
single clean, human-readable text string that is safe to chunk, embed,
and eventually show to an LLM as retrieved context.

Two very different raw formats need two different cleaners:
    1. G-code (.NC) raw text -> needs to be *parsed* into machining
       "operations" (comment-delimited sections) and then turned into
       one clean sentence per operation.
    2. Catalog / drawing text -> already clean prose, just needs
       whitespace normalization.

Import 01_documents at runtime rather than hard-coding paths again.
"""

import re
import importlib.util
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(_THIS_DIR, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


documents_mod = _import_module("01_documents.py", "documents_mod")


# ---------------------------------------------------------------------------
# G-code specific preprocessing
# ---------------------------------------------------------------------------

_COMMENT_RE = re.compile(r"\(([^)]+)\)")
_TOOL_RE = re.compile(r"\bT(\d{3,4})\b")
_SPEED_RE = re.compile(r"\bS(\d+(?:\.\d+)?)")
_FEED_RE = re.compile(r"\bF(\d+(?:\.\d+)?)")


def parse_nc_sections(raw_text: str) -> list[dict]:
    """Split a raw .NC file's text into comment-delimited machining sections.

    Each section = one logical operation (Facing, Finish OD, Broaching, ...),
    identified by the G-code comments that precede/accompany it.
    """
    sections = []
    current = None

    def flush():
        if current is not None and (current["tools"] or current["comments"]):
            sections.append(current)

    for raw in raw_text.splitlines():
        line = raw.strip().lstrip("/").strip()
        if not line or line == "%":
            continue

        m = re.fullmatch(_COMMENT_RE, line)
        if m:
            text = m.group(1).strip()
            if current is None or current["line_count"] > 0:
                flush()
                current = {"title": text, "comments": [text], "tools": set(),
                           "speeds": [], "feeds": [], "line_count": 0}
            else:
                current["comments"].append(text)
            continue

        if current is None:
            current = {"title": "HEADER / SETUP", "comments": [], "tools": set(),
                       "speeds": [], "feeds": [], "line_count": 0}

        current["line_count"] += 1
        for t in _TOOL_RE.findall(line):
            current["tools"].add(t)
        for s in _SPEED_RE.findall(line):
            current["speeds"].append(float(s))
        for fnum in _FEED_RE.findall(line):
            current["feeds"].append(float(fnum))

    flush()
    return sections


def clean_gcode_section(section: dict, program: str, path_label: str) -> str:
    """Turn one parsed section dict into one clean natural-language sentence."""
    short_titles = [c for c in section["comments"]
                     if len(c) <= 24 and re.match(r"^[A-Za-z0-9 .\-]+$", c)]
    title_raw = short_titles[0] if short_titles else section["title"]
    title = title_raw.strip().rstrip(".").title()

    tools = ", ".join("T" + t for t in sorted(section["tools"]))
    extra_comments = [c for c in section["comments"] if c not in (section["title"], title_raw)]
    speeds = sorted(set(section["speeds"]))
    feeds = sorted(set(section["feeds"]))
    line_count = section["line_count"]

    parts = [f"Operation '{title}' in {program} ({path_label})"]
    if tools:
        parts.append(f"uses tool(s) {tools}")
    if extra_comments:
        parts.append(f"tool/spec note: {'; '.join(extra_comments)}")
    if speeds:
        parts.append(f"spindle speed up to S{max(speeds):.0f} RPM")
    if feeds:
        parts.append(f"feed rate(s) around F{min(feeds)}-{max(feeds)}")
    parts.append(f"({line_count} G-code motion lines in this cycle)")
    return ", ".join(parts) + "."


def preprocess_gcode_doc(raw_doc: dict) -> list[dict]:
    """A single .NC raw document can expand into MANY clean documents
    (one per machining operation/section) -- this is intentional and is
    what lets the retriever point at a specific operation, e.g. GC-19 for
    'Broaching', instead of one giant undifferentiated blob per file.
    """
    program = raw_doc["metadata"]["filename"]
    path_label = raw_doc["metadata"]["path_label"]
    sections = parse_nc_sections(raw_doc["raw_text"])

    clean_docs = []
    op_index = 0
    for s in sections:
        if s["line_count"] < 4:
            continue  # skip trivial/near-empty sections (noise, not signal)
        clean_text = clean_gcode_section(s, program, path_label)
        clean_docs.append({
            "doc_id": f"{raw_doc['doc_id']}-OP{op_index}",
            "source": raw_doc["source"],
            "clean_text": clean_text,
            "metadata": {**raw_doc["metadata"], "operation_title": s["title"], "operation_index": op_index},
        })
        op_index += 1
    return clean_docs


# ---------------------------------------------------------------------------
# Catalog / drawing preprocessing (already clean prose -> just normalize)
# ---------------------------------------------------------------------------

def clean_prose(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_prose_doc(raw_doc: dict) -> dict:
    return {
        "doc_id": raw_doc["doc_id"],
        "source": raw_doc["source"],
        "clean_text": clean_prose(raw_doc["raw_text"]),
        "metadata": raw_doc["metadata"],
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def preprocess_all() -> list[dict]:
    """Run the full preprocessing stage over every raw document.

    Returns a flat list of "clean documents":
        {"doc_id", "source", "clean_text", "metadata"}
    """
    raw_docs = documents_mod.load_raw_documents()
    clean_docs = []
    for raw_doc in raw_docs:
        doc_type = raw_doc["metadata"]["type"]
        if doc_type == "gcode":
            clean_docs.extend(preprocess_gcode_doc(raw_doc))
        else:  # "catalog" or "drawing"
            clean_docs.append(preprocess_prose_doc(raw_doc))
    return clean_docs


if __name__ == "__main__":
    docs = preprocess_all()
    print(f"Preprocessed into {len(docs)} clean documents:")
    for d in docs:
        print(f"  {d['doc_id']:14s} {d['clean_text'][:80]}")
