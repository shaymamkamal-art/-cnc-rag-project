"""
01_documents.py
----------------
Stage 1 of the pipeline: RAW DOCUMENT INGESTION.

Responsibility of this file ONLY:
    - Know where the raw source material lives (NC files + hand-extracted
      catalog / drawing facts).
    - Load it into memory as plain, un-cleaned "raw documents".
    - Do NOT clean, normalize, chunk, embed, or store anything here.
      That happens in the later pipeline stages (02, 03, 04, 05).

A "raw document" is a dict:
    {
        "doc_id":  str   -> stable id, e.g. "NC-O3710", "CAT-3"
        "source":  str   -> where it came from (filename or catalog page)
        "raw_text": str  -> untouched text
        "metadata": dict -> anything useful for filtering/citation later
    }

Domain context (CNC dental-implant manufacturing, EG Medical / ZI 1 system):
    - O3710.NC        -> Path 1 (main spindle) G-code for item IC3710 (3.7 x 10mm)
    - Platform3_4.NC  -> Path 2 (sub-spindle)  G-code for item IC3710 (3.7 x 10mm)
    - O3711.NC        -> Path 1 G-code for item IC3711_5 (3.7 x 11.5mm) -- a SECOND
                         verified length in the same 3.7mm diameter family.
    - Catalog facts and one engineering-drawing fact set, extracted by hand
      from the product catalog / drawing PDFs (see project README).
"""

import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _read_file(filename: str) -> str:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", errors="ignore") as f:
        return f.read()


def load_raw_documents() -> list[dict]:
    """Return the full list of raw documents, ready for preprocessing (02)."""
    raw_docs = []

    # ---- 1. Raw G-code programs (three verified CNC files) -----------------
    nc_files = [
        ("O3710.NC", "Path 1 (main spindle - body/thread)", "IC3710", 10.0),
        ("Platform3_4.NC", "Path 2 (sub-spindle - internal hex/thread)", "IC3710", 10.0),
        ("O3711.NC", "Path 1 (main spindle - body/thread)", "IC3711_5", 11.5),
    ]
    for filename, path_label, item_code, length_mm in nc_files:
        raw_docs.append({
            "doc_id": f"NC-{filename.replace('.NC', '')}",
            "source": filename,
            "raw_text": _read_file(filename),
            "metadata": {
                "type": "gcode",
                "filename": filename,
                "path_label": path_label,
                "item_code": item_code,
                "length_mm": length_mm,
                "diameter_mm": 3.7,
            },
        })

    # ---- 2. Catalog facts (hand-extracted from Final_Cat__packing.pdf) -----
    catalog_facts = [
        ("CAT-0", "General Overview",
         "The ZI 1 Implant System is a universal internal hex-connection dental "
         "implant line manufactured by EG Medical in Cairo, Egypt, on Citizen/Star "
         "SR-20RIV Swiss-type CNC lathes. It offers three diameter categories "
         "(Narrow 3.2mm, Standard 3.7/4.3mm, Wide 5.2mm) and multiple lengths per diameter."),
        ("CAT-1", "Design Features",
         "The ZI 1 implant body includes micro-threads in the crestal region for "
         "bone-to-implant contact, a reverse coronal taper and expanding taper inner "
         "body for gradual bone condensation, a self-cutting thread for high primary "
         "stability at low torque, and apical cutting blades to engage a smaller osteotomy."),
        ("CAT-2", "Narrow Line Sizes (3.2mm)",
         "The Narrow Line has a diameter of 3.2 mm with a 3.0 mm prosthetic platform, "
         "offered in lengths 8, 10, 11.5, 13, and 15 mm. No verified CNC program exists "
         "yet for this diameter in our shop data."),
        ("CAT-3", "Standard Line Sizes (3.7mm & 4.3mm)",
         "The Standard Line has diameters 3.7 mm and 4.3 mm with a 3.4 mm prosthetic "
         "platform, offered in lengths 8, 10, 11.5, 13, and 15 mm (plus a 6 mm short "
         "option at 4.3 mm). Verified CNC programs exist for two lengths in the 3.7mm "
         "diameter: 3.7x10mm (item IC3710: O3710.NC + Platform3_4.NC) and "
         "3.7x11.5mm (item IC3711_5: O3711.NC)."),
        ("CAT-4", "Wide Line Sizes (5.2mm)",
         "The Wide Line has a diameter of 5.2 mm, offered in lengths 6, 8, 10, 11.5, "
         "13, and 15 mm. No verified CNC program exists yet for this diameter."),
        ("CAT-5", "RBM Surface Treatment",
         "After machining, ZI 1 implants receive Resorbable Blasted Media (RBM) and "
         "acid-etch surface treatment: resorbable calcium-phosphate particles are "
         "blasted onto the titanium surface, then acid-etched to add fine micron "
         "pits, giving a dual-scale roughness of Sa 1.75 +/- 0.5 microns to enhance "
         "osseointegration. This happens after CNC machining is complete, not during it."),
        ("CAT-6", "Stock Abutments - Standard Line (3.4mm Platform)",
         "Stock abutments for the Standard Line implants (3.7/4.3/5.2 mm body "
         "diameter) use a 3.4 mm prosthetic platform, matching the internal hex "
         "broached into the implant during Path 2 machining (Platform3_4.NC)."),
        ("CAT-7", "Healing Abutments",
         "Healing abutments for the Standard Line use a 1.8 mm retaining screw. "
         "This matches the internal thread cut in Platform3_4.NC (M1.8 P0.35 "
         "thread, cut in four passes: roughing, semi-finishing, finishing, and a "
         "finishing repeat pass)."),
        ("CAT-8", "Surgical Kit",
         "The ZI 1 surgical kit provides sequential drills (1.5 to 4.8 mm), "
         "parallel pins, implant drivers, and screwdrivers, used to prepare the "
         "osteotomy site and place the implant clinically. This is a separate "
         "clinical kit and unrelated to the CNC manufacturing tooling used inside "
         "the G-code programs."),
        ("CAT-9", "Company and Regulatory Info",
         "EG Medical is an Egyptian medical-technology company founded in 2023, "
         "based in Heliopolis, Cairo. The ZI 1 system is registered with the "
         "Egyptian Drug Authority (license R259061Lrn25V1) and produced under an "
         "ISO 13485:2016-certified quality system."),
    ]
    for doc_id, title, text in catalog_facts:
        raw_docs.append({
            "doc_id": doc_id,
            "source": "Final_Cat__packing.pdf",
            "raw_text": text,
            "metadata": {"type": "catalog", "title": title},
        })

    # ---- 3. Engineering drawing facts (hand-extracted from drawing PDFs) ---
    drawing_facts = [
        ("DWG-0", "IC3710.pdf", "IC3710", 3.7, 10.0,
         "Item code IC3710 (3.7 mm x 10 mm Standard Line fixture). Overall length "
         "10 mm. Major thread OD 3.75 mm, minor thread diameters 3.71 mm and 3.40 "
         "mm on the body, with a 45-degree top chamfer. Internal hex socket "
         "diameter 2.4 mm at a depth of 2.77 mm from the top face. Lower body "
         "taper 3.33 degrees, apex angle 7 degrees at the tip, tip diameter 2.4 mm."),
        ("DWG-1", "IC3711_5.pdf", "IC3711_5", 3.7, 11.5,
         "Item code IC3711.5 (3.7 mm x 11.5 mm Standard Line fixture). Overall "
         "length 11.5 mm. Major thread OD 3.75 mm, minor thread diameters 3.71 mm "
         "and 3.40 mm on the body, with a 45-degree top chamfer. Internal hex "
         "socket diameter 2.4 mm at a depth of 2.77 mm from the top face. Lower "
         "body taper 2.1 degrees, apex angle 7 degrees at the tip, tip diameter "
         "2.4 mm. Same head geometry as IC3710, longer tapered body."),
    ]
    for doc_id, source, item_code, diameter_mm, length_mm, text in drawing_facts:
        raw_docs.append({
            "doc_id": doc_id,
            "source": source,
            "raw_text": text,
            "metadata": {
                "type": "drawing",
                "item_code": item_code,
                "diameter_mm": diameter_mm,
                "length_mm": length_mm,
            },
        })

    return raw_docs


if __name__ == "__main__":
    docs = load_raw_documents()
    print(f"Loaded {len(docs)} raw documents:")
    for d in docs:
        preview = d["raw_text"].strip().replace("\n", " ")[:70]
        print(f"  {d['doc_id']:10s} [{d['metadata'].get('type'):8s}] {preview}...")
