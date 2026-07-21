# ZI 1 Implant CNC RAG Assistant

A simple retrieval-augmented generation (RAG) project for the EG Medical
ZI 1 dental implant system: catalog specs, one engineering drawing, and
three verified CNC machining programs (`O3710.NC`, `Platform3_4.NC`,
`O3711.NC`).

## Pipeline

```
01_documents.py            -> raw ingestion (NC files + catalog/drawing facts)
02_preprocessing.py        -> clean/normalize text (parses G-code into operations)
03_chunking.py             -> word-window chunking with overlap
04_vector_representation.py-> sentence-transformers embeddings (local, no API key)
05_create_chroma_store.py  -> build/persist the Chroma vector store
06_retrieve_context.py     -> embed query + semantic search -> top-k chunks
07_prompting.py            -> build grounded prompt + call OpenRouter -> answer + citations
streamlit_app.py           -> chat UI wiring all of the above together
```

Every stage only imports the stage before it (via `importlib`, since
the files start with digits and can't be `import`-ed with normal
syntax). Run any file directly to see it work in isolation, e.g.:

```bash
python 01_documents.py
python 02_preprocessing.py
python 03_chunking.py
python 04_vector_representation.py
python 05_create_chroma_store.py
python 06_retrieve_context.py
python 07_prompting.py
```

## Local setup

```bash
pip install -r requirements.txt
cp .env.example .env      # then edit .env and paste your real key locally
python 05_create_chroma_store.py   # builds ./chroma_store/
streamlit run streamlit_app.py
```

`.env` is git-ignored -- never commit your real key.

## Data

Raw CNC files live in `data/`:
- `O3710.NC` -- Path 1 (main spindle) for item IC3710 (3.7 x 10mm)
- `Platform3_4.NC` -- Path 2 (sub-spindle) for item IC3710 (3.7 x 10mm)
- `O3711.NC` -- Path 1 for item IC3711_5 (3.7 x 11.5mm), a second
  verified length in the same diameter family

Catalog and drawing facts are hand-extracted constants inside
`01_documents.py` (see that file's comments for where each fact came
from in the source PDFs).

## Deploying to Streamlit Cloud

1. Push this whole folder to a GitHub repository.
2. On [share.streamlit.io](https://share.streamlit.io), create a new
   app pointing at your repo, main file = `streamlit_app.py`.
3. In the deployed app: **Manage app -> Secrets**, paste:

   ```toml
   OPENROUTER_API_KEY = "your_openrouter_key_here"
   OPENROUTER_MODEL = "openai/gpt-4o-mini"
   ```

4. Redeploy / reboot the app. It will pick up the secrets automatically
   (see the `st.secrets` fallback at the top of `streamlit_app.py`).

## Final submission checklist

- [ ] All required Python files exist (`01_documents.py` ... `07_prompting.py`, `streamlit_app.py`)
- [ ] `requirements.txt` exists
- [ ] Real API key is **not** in the ZIP or in GitHub (check `.env` is git-ignored)
- [ ] Streamlit secrets configured in valid TOML format on Streamlit Cloud
- [ ] The Streamlit app runs successfully end-to-end
- [ ] The answer uses retrieved context (see the "Show retrieved context" expander)
- [ ] The answer cites sources (chunk IDs, e.g. `[NC-Platform3_4-OP19]`)
