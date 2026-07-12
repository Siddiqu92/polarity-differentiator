"""FastAPI backend for Family Office RAG"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from pydantic import BaseModel
from src.rag_pipeline import FORAGPipeline

app = FastAPI(title="Family Office Intelligence RAG")

print("Loading RAG pipeline...")
rag = FORAGPipeline()
rag.ingest_dataset()
print("✓ RAG pipeline ready")

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
            "/health": "GET - API health"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/query")
def query_rag(request: QueryRequest):
    results = rag.query(request.query, n_results=request.n_results)

    documents = results['documents'][0] if results['documents'] else []
    metadatas = results['metadatas'][0] if results['metadatas'] else []

    return {
        "query": request.query,
        "results": documents,
        "metadata": metadatas,
        "count": len(documents)
    }

@app.get("/offices")
def list_offices():
    try:
        all_data = rag.collection.get(include=["metadatas"])
        fo_names = set()
        for meta in all_data.get('metadatas', []):
            if meta and 'fo_name' in meta:
                fo_names.add(meta['fo_name'])
        return {"total_offices": len(fo_names), "offices": sorted(list(fo_names))}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
