# Stack Documentation

## Overview

Family Office Intelligence RAG — semantic search over 50 verified family office records.

## Data Layer

| Component | File | Purpose |
|-----------|------|---------|
| Source | `data/FO-MAX-data-sample-2.0.xlsx` | FO-MAX verified family office database (111 rows, top 50 selected) |
| Extraction | `src/data_extraction.py` | Parse Excel row 4 headers, row 5+ data |
| Output | `output/family_offices_extracted.csv` | 50 records, 31 fields each |
| Validation | `src/build_validation_chains.py` | 3 sample validation chains + quality report |

## RAG Layer

| Component | File | Purpose |
|-----------|------|---------|
| Core | `src/rag.py` | `FamilyOfficeRAG` class |
| Chunking | 3 chunks per office | entity, principal, full |
| Storage | `chromadb_data/` | ChromaDB PersistentClient, cosine space |
| Index size | 50 offices × 3 chunks = **150 chunks** |

## API Layer

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health + office/chunk counts |
| `/offices` | GET | List all indexed family offices |
| `/query` | POST | Semantic search (`query`, `n_results`) |

**Entry points:**
- `rag_app/main.py` — primary (Replit)
- `src/api.py` — alternate with Pydantic response models

## UI Layer

| Component | File | Port |
|-----------|------|------|
| Streamlit | `rag_app/streamlit_app.py` | 8501 |

## Dependencies

```
pandas, openpyxl     — Excel extraction
chromadb             — vector storage + embedding
fastapi, uvicorn     — REST API
streamlit            — demo UI
pydantic             — request validation
```

## Deployment

- **Local:** Run API + Streamlit as above
- **Replit:** `.replit` configured for `python rag_app/main.py`
- **Live URL:** Deploy Replit or Streamlit Cloud; provide URL in submission email

## Paths

All scripts use `src/paths.py` for root-relative paths — safe to run from any directory via `python -m src.<module>`.
