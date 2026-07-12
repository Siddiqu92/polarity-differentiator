# Requirements Checklist — Falcon Scaling Differentiator

> Note: `Differentiator.docx` was not present in the workspace. Requirements below are derived from the assessment brief, deliverables list, and project documentation.

## Task 1: Family Office RAG Pipeline

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | 50 verified family office records from real Excel | ✅ | `output/family_offices_extracted.csv` (50 rows) |
| 2 | Data sourced from FO-MAX Excel (not fabricated) | ✅ | `src/data_extraction.py` reads `FO-MAX-data-sample-2.0.xlsx` |
| 3 | 3 full validation chains with sources | ✅ | `docs/validation_chains.json` (Walton, Emerson, Bezos) |
| 4 | Production RAG pipeline | ✅ | `src/rag.py` — ChromaDB, 150 chunks |
| 5 | FastAPI backend | ✅ | `rag_app/main.py` — 4 endpoints |
| 6 | Streamlit UI | ✅ | `rag_app/streamlit_app.py` |
| 7 | ChromaDB vector storage | ✅ | `chromadb_data/` |
| 8 | GitHub repo with commit history | ✅ | 12+ commits (discovery → extraction → RAG → Task 2) |
| 9 | Local demonstration | ✅ | API port 8000, Streamlit port 8501 |
| 10 | Stack documentation | ✅ | `docs/STACK.md`, `README.md` |

## Task 2: SaaS Conversion Analysis

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Root cause diagnosis (3 hypotheses + confidence %) | ✅ | `docs/TASK_2_SAAS_ANALYSIS.md` Part 1 |
| 2 | 3 testable experiments with success metrics | ✅ | Part 2 |
| 3 | Honest uncertainty statements | ✅ | Part 4 |
| 4 | Visible human reasoning (not generic AI) | ✅ | Part 3, 5, 6 |

## Verification Commands

```bash
# Data pipeline
python -m src.data_extraction
python -m src.build_validation_chains
python -c "import csv; print(len(list(csv.DictReader(open('output/family_offices_extracted.csv')))))"

# RAG
python -m src.rag

# API (separate terminal)
python rag_app/main.py
curl http://localhost:8000/health
curl http://localhost:8000/offices
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"query\":\"tech investments\",\"n_results\":3}"

# Streamlit (separate terminal)
streamlit run rag_app/streamlit_app.py
```

## Known Limitations (documented honestly)

- Contact email/phone often `Hidden` in FO-MAX source data
- `Bezos Exeditions` spelling matches FO-MAX source (not corrected)
- Live public URL requires Replit/Streamlit Cloud deployment by candidate
