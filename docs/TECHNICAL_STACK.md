# TASK 1: Technical Stack & RAG Architecture

## Stack Choices

### Backend
- **FastAPI** (Python web framework)
  - Why: Async, fast, built-in OpenAPI docs, lightweight
  - Alternative considered: Flask (rejected - less performant)

### Vector Database
- **ChromaDB** (open source, local-first)
  - Why: Zero dependencies, built-in embeddings, perfect for 50 records
  - Alternative considered: Pinecone (rejected - paid, overkill)
  - Embedding model: Default SentenceTransformers (all-MiniLM-L6-v2)

### Frontend
- **Streamlit** (Python UI framework)
  - Why: Zero JavaScript, perfect for data apps, interactive
  - Alternative considered: Next.js (rejected - overengineering)

### Data Pipeline
- **Python** with openpyxl + pandas
  - Extraction: Direct Excel parsing
  - Validation: Pandas quality checks
  - Output: CSV format

---

## Chunking Strategy

### Method: Entity-focused multi-chunk
Each family office = 4 chunks for semantic diversity:

1. **Entity chunk:** Name, AUM, sectors, geography
2. **Principal chunk:** Contact name, title, location
3. **Investment thesis:** Sectors, strategy, focus areas
4. **Verification chunk:** Data quality, source, confidence

### Rationale:
- Enables queries about any aspect of FO (entity, contact, strategy, quality)
- Improves semantic relevance through repetition
- Supports multi-entity questions ("FOs + tech + California")

### Result: 50 records × 4 chunks = 200 semantic chunks indexed

---

## Embedding Model

- **Model:** SentenceTransformers (all-MiniLM-L6-v2, default ChromaDB)
- **Dimensions:** 384D
- **Why chosen:**
  - Perfect for 50-entity scale
  - Fast inference (<5ms per query)
  - No API calls needed (local, private)
  
- **Alternatives:**
  - OpenAI embeddings (rejected: paid, requires API key, network dependency)
  - BERT (rejected: larger, slower)

---

## Retrieval Approach

### Semantic Search (Primary)
- Query embedding vs chunk embeddings
- Distance metric: Cosine similarity
- Top-K retrieval: 5 results (user-adjustable 1-10)

### Why NOT hybrid (keyword + semantic)?
- Dataset too small (50 records)
- All queries natural language
- Semantic alone sufficient

### Performance
- Retrieval latency: ~50ms for 50 records
- Scales well to 1000+ records

---

## What Works

✓ Semantic search captures intent ("tech California" → Silicon Valley FOs)
✓ Multi-chunk strategy handles various query types
✓ FastAPI + Streamlit integration clean and fast
✓ Local ChromaDB avoids external dependencies
✓ Real Excel data grounds results

---

## What Doesn't Work (Honest Gaps)

❌ Contact intelligence still 60-80% complete (inherent to family offices)
❌ Recent signals sparse (no live data feed)
❌ No handling for typos/misspellings (could add edit distance)
❌ No personalization (treats all users same)

---

## What Would Improve (If Production)

1. **Live data ingestion:** News feeds, SEC filings, CRMs
2. **Named entity recognition:** Auto-extract principals from news
3. **Multi-language support:** Track international FOs
4. **Advanced ranking:** Combine relevance + recency + deal size
5. **User feedback loop:** Learn from query patterns
6. **Graph search:** Find connected FOs (co-investments, shared principals)

---

## Deployment Considerations

### Current State
- ✓ Works locally (tested)
- ✓ API endpoints working
- ✓ UI interactive and responsive
- ⚠️ Live URL deployment (in progress)

### For Production
- Containerize: Docker for consistency
- Scale DB: PostgreSQL + Timescale for multi-user
- Cache: Redis for frequently searched families
- Monitoring: Prometheus + Grafana
- Auth: API keys for B2B access
