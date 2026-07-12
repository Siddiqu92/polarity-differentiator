# Polarity IQ Differentiator Assessment

**Author:** Siddique Khan ([@Siddiqu92](https://github.com/Siddiqu92))  
**Email:** Siddiqkhaan92@gmail.com  
**Status:** Complete — locally verified

## Task 1: Family Office Intelligence RAG

Production RAG pipeline over **50 verified family offices** extracted from the FO-MAX Excel database.

### Stack

| Layer | Technology |
|-------|------------|
| Data source | FO-MAX Excel (`data/FO-MAX-data-sample-2.0.xlsx`) |
| Extraction | Python + openpyxl + pandas |
| Vector DB | ChromaDB (cosine similarity) |
| API | FastAPI (`rag_app/main.py` or `src/api.py`) |
| UI | Streamlit (`rag_app/streamlit_app.py`) |

See [docs/STACK.md](docs/STACK.md) for full architecture.

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Extract 50 family offices from Excel
python -m src.data_extraction

# 3. Build validation chains + quality report
python -m src.build_validation_chains

# 4. Ingest into ChromaDB and test RAG
python -m src.rag

# 5. Start API (port 8000)
python rag_app/main.py

# 6. Start Streamlit UI (port 8501)
streamlit run rag_app/streamlit_app.py
```

### Deliverables

- `output/family_offices_extracted.csv` — 50 real records
- `docs/validation_chains.json` — 3 full validation chains with sources
- `docs/validation_report.json` — data quality report
- `chromadb_data/` — persisted vector index (150 chunks)

## Task 2: SaaS Conversion Analysis

See [docs/TASK_2_SAAS_ANALYSIS.md](docs/TASK_2_SAAS_ANALYSIS.md)

## Verification

See [docs/REQUIREMENTS_CHECKLIST.md](docs/REQUIREMENTS_CHECKLIST.md)

## Architecture

```
FO-MAX Excel → data_extraction.py → CSV (50 records)
                                        ↓
                              build_validation_chains.py
                                        ↓
                              validation_chains.json + report
                                        ↓
                              rag.py → ChromaDB (150 chunks)
                                        ↓
                         FastAPI API  +  Streamlit UI
```
