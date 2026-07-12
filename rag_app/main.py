"""FastAPI backend for Family Office RAG."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.rag import FamilyOfficeRAG

app = FastAPI(title="Family Office Intelligence RAG")

print("Loading RAG pipeline...")
rag = FamilyOfficeRAG()
records = rag.load_data()
rag.ingest_data(records)
print("[OK] RAG pipeline ready")


class QueryRequest(BaseModel):
    query: str
    n_results: int = 5


@app.get("/")
def root():
    return {
        "status": "online",
        "api": "Family Office Intelligence RAG",
        "version": "1.0.0",
        "endpoints": {
            "/query": "POST - Query family offices",
            "/offices": "GET - List all indexed offices",
            "/health": "GET - API health",
        },
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "indexed_offices": len(rag.get_all_offices()),
        "total_chunks": rag.chunk_count(),
    }


@app.post("/query")
def query_rag(request: QueryRequest):
    if not request.query or len(request.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")
    results = rag.search(request.query, top_k=request.n_results)
    return {
        "query": request.query,
        "results": [r["text"] for r in results],
        "metadata": [r["metadata"] for r in results],
        "ids": [r["id"] for r in results],
        "count": len(results),
    }


@app.get("/offices")
def list_offices():
    offices = rag.get_all_offices()
    return {"total_offices": len(offices), "offices": offices}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
