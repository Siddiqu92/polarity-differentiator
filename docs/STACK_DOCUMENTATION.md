# Stack Documentation — Family Office Intelligence RAG

**Version:** 1.0.0  
**Deployment:** Streamlit Cloud / Local / Replit  
**Dataset:** 50 family offices, up to 200 vector chunks  
**Last Updated:** June 2026  

---

## 1. System Architecture

### 1.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER LAYER                                │
│  Streamlit UI (dropdown + semantic search)  │  FastAPI REST      │
└──────────────────────────┬──────────────────┴─────────┬─────────┘
                           │                            │
                           ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│              src/rag.py — FamilyOfficeRAG                        │
│   load_data() → create_chunks() → ingest_data() → search()      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  FO-MAX Excel → extraction → enriched CSV → ChromaDB vectors    │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Breakdown

| Component | File | Role |
|-----------|------|------|
| Data extraction | `src/data_extraction.py` | Excel → CSV (50 records) |
| Verification enrichment | `src/enrich_verification_metadata.py` | Adds sources, confidence, signals |
| RAG core | `src/rag.py` | Chunking, embedding, retrieval |
| API | `rag_app/main.py` | FastAPI endpoints |
| UI | `rag_app/streamlit_app.py` | Interactive demo |
| Paths | `src/paths.py` | Root-relative file resolution |

### 1.3 Data Flow

```
FO-MAX-data-sample-2.0.xlsx
    → family_offices_extracted.csv (50 rows)
    → family_offices_enriched_verified.csv (+6 metadata columns)
    → 4 chunks/office (entity, principal, full, verification)
    → ChromaDB (chromadb_data/)
    → Semantic query → ranked results
```

---

## 2. Technology Stack Justification

### 2.1 Python 3.10+

| | |
|---|---|
| **Why chosen** | Single language for ETL, ML, API, and UI |
| **Advantages** | Fast iteration, rich data ecosystem |
| **Limitations** | GIL limits CPU parallelism |
| **Alternatives rejected** | Node.js (weaker data/ML tooling) |
| **Trade-off** | Simplicity over microservice polyglot |

### 2.2 Streamlit 1.28+

| | |
|---|---|
| **Why chosen** | Zero frontend JS for data demo; ideal for assessment |
| **Advantages** | Dropdown + search in <100 lines; Streamlit Cloud deploy |
| **Limitations** | Not suitable for multi-tenant SaaS UI |
| **Alternatives rejected** | Next.js (overengineering for 48hr assessment) |
| **Trade-off** | Speed to demo vs custom UX |

### 2.3 ChromaDB

| | |
|---|---|
| **Why chosen** | Local-first, embedded vectors, zero ops for 50 records |
| **Advantages** | PersistentClient, cosine similarity built-in |
| **Limitations** | Not ideal for 10K+ concurrent users |
| **Alternatives rejected** | Pinecone (cost, external dependency) |
| **Trade-off** | Free local vs managed scale |

### 2.4 FastAPI

| | |
|---|---|
| **Why chosen** | Async, OpenAPI docs, Pydantic validation |
| **Advantages** | 4 endpoints in minimal code |
| **Limitations** | Requires separate process from Streamlit |
| **Alternatives rejected** | Flask (less modern typing/validation) |

### 2.5 pandas + openpyxl

| | |
|---|---|
| **Why chosen** | Industry standard for Excel extraction |
| **Advantages** | Direct FO-MAX column mapping |
| **Limitations** | Memory-bound for very large files |

---

## 3. Data Pipeline

| Stage | Process |
|-------|---------|
| **Ingestion** | `openpyxl` reads row 4 headers, row 5+ data |
| **Cleaning** | `_cell()` normalizes None → string; strip whitespace |
| **Selection** | Top 50 by completeness |
| **Enrichment** | Verification metadata + recent signals JSON |
| **Chunking** | 4 semantic chunks per office |
| **Embedding** | ChromaDB default (all-MiniLM-L6-v2) |
| **Storage** | `chromadb_data/` persistent directory |
| **Retrieval** | Cosine similarity, top-K (1–50) |

---

## 4. Embedding and Retrieval

| Parameter | Value |
|-----------|-------|
| **Model** | SentenceTransformers `all-MiniLM-L6-v2` (ChromaDB default) |
| **Dimensions** | 384 |
| **Distance metric** | Cosine similarity |
| **Algorithm** | Semantic search only (no hybrid) |
| **Top-K** | Default 10 (Streamlit slider 1–50) |
| **Latency** | ~50ms for 50 records (local) |

**Why semantic only:** Dataset is small; queries are natural language; keyword index adds complexity without measurable gain at N=50.

**Ranking:** Lower cosine distance = higher relevance. Streamlit displays `1 - distance` as relevance %.

---

## 5. Chunking Strategy

| Chunk Type | Content | Purpose |
|------------|---------|---------|
| `entity` | Name, description, thesis, sectors, location, website | Entity queries |
| `principal` | Contact name, title, location | People queries |
| `full` | Description + thesis combined | Broad semantic match |
| `verification` | Sources, confidence, gaps, recent signals | Trust/quality queries |

| Parameter | Value |
|-----------|-------|
| **Chunks per office** | 4 |
| **Total chunks** | 200 (50 × 4) |
| **Overlap** | None (intentional — metadata separation) |
| **Logic** | Field-group semantic chunks |

**Trade-off:** More chunks = better query precision but 4× storage. At 50 offices, cost is negligible.

---

## 6. User Interface Design

### 6.1 Interaction Flows

1. **Dropdown path:** Select office → semantic search on office name → all related chunks
2. **Keyword path:** Free-text query → cross-office semantic search
3. **Results:** Ranked text + metadata JSON expander

### 6.2 UX Principles

- Zero login friction (assessment demo)
- Immediate feedback (spinner + result count)
- Metadata transparency (verification chunk visible in results)
- Mobile-responsive via Streamlit defaults

---

## 7. What Works Well ✓

| Feature | Performance |
|---------|-------------|
| Dropdown with 50 offices | Instant load |
| Semantic search quality | Relevant for sector/geo queries |
| Load time (local) | <5s cold start including ingest |
| Metadata display | Confidence + sources in verification chunk |
| Real Excel grounding | No fabricated entity names |
| Dual search modes | Office-specific + exploratory |

---

## 8. What Doesn't Work / Limitations ✗

| Limitation | Impact |
|------------|--------|
| Scale ceiling ~1,000 offices | Needs pgvector/ Pinecone migration |
| No real-time data feed | Manual re-extraction required |
| Contact verification gaps | Hidden fields in source |
| No user authentication | Not production SaaS ready |
| No query audit log | Compliance gap for enterprise |
| Cold start re-ingest | Streamlit session rebuilds index |
| California query imprecision | Semantic overlap with non-CA offices |

---

## 9. Future Improvements / Roadmap 🚀

| Priority | Improvement |
|----------|-------------|
| P0 | PostgreSQL + pgvector for scale |
| P0 | Authentication + API keys |
| P1 | Live news/SEC ingestion pipeline |
| P1 | Named entity recognition for principals |
| P2 | Hybrid search (BM25 + semantic) |
| P2 | Deal matching engine (fund ↔ FO thesis) |
| P3 | CRM connectors (Salesforce export) |
| P3 | Query analytics dashboard |

---

## 10. Deployment Information

### 10.1 Current State

| Environment | Status |
|-------------|--------|
| Local (Windows/Mac) | Tested ✓ |
| Streamlit Cloud | Configured (requirements.txt) |
| Replit | `.replit` configured for API |
| Live URL | Deploy via Streamlit Cloud |

### 10.2 Infrastructure Requirements

| Resource | Minimum |
|----------|---------|
| RAM | 2 GB |
| Disk | 500 MB (embeddings + Excel) |
| Python | 3.10+ |
| Ports | 8000 (API), 8501 (Streamlit) |

### 10.3 Performance Metrics

| Metric | Value |
|--------|-------|
| Records indexed | 50 |
| Chunks | 200 |
| Ingest time | ~3–5s |
| Query latency | ~50ms |
| API endpoints | 4 |

---

## 11. Security Considerations

| Area | Current State |
|------|---------------|
| Data privacy | Public FO data only; no PII invented |
| Access control | None (demo) |
| Encryption | HTTPS at deployment layer |
| API security | No auth (demo) |
| Compliance | Not GDPR/SOC2 certified |

---

## 12. Cost Analysis

| Item | Cost |
|------|------|
| Development | Assessment-time (48hr window) |
| ChromaDB local | $0/month |
| Streamlit Cloud free tier | $0/month |
| OpenAI embeddings | $0 (local SentenceTransformers) |
| Scale to 10K records | ~$50–200/month (managed vector DB) |

**ROI for fund manager:** One qualified FO introduction likely exceeds annual tool cost — value is in actionability of verified entity intelligence, not contact guessing.

---

## Quick Reference Commands

```bash
python -m src.data_extraction
python -m src.enrich_verification_metadata
python -m src.rag
streamlit run rag_app/streamlit_app.py
python rag_app/main.py
```
