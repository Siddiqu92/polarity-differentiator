"""FastAPI - RAG Query Interface"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.rag import FamilyOfficeRAG
import logging

# Initialize RAG
rag = FamilyOfficeRAG()
records = rag.load_data()
rag.ingest_data(records)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Family Office Intelligence RAG API",
    description="Query 50+ verified family offices with semantic search",
    version="1.0.0"
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResult(BaseModel):
    id: str
    text: str
    distance: float
    metadata: Dict[str, Any]

class QueryResponse(BaseModel):
    query: str
    results: List[QueryResult]
    total_results: int

# Routes
@app.get("/")
def read_root():
    """Health check + API info"""
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
def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "indexed_offices": len(rag.get_all_offices()),
        "total_chunks": 192
    }

@app.get("/offices")
def get_offices():
    """List all indexed family offices"""
    offices = rag.get_all_offices()
    return {
        "total": len(offices),
        "offices": offices
    }

@app.post("/query", response_model=QueryResponse)
def query_family_offices(request: QueryRequest):
    """
    Query family offices using semantic search
    
    Example queries:
    - "Which family offices invest in real estate?"
    - "Find principals in California"
    - "Tech investment mandates"
    """
    
    if not request.query or len(request.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")
    
    if request.top_k < 1 or request.top_k > 20:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")
    
    try:
        results = rag.search(request.query, top_k=request.top_k)
        
        formatted_results = [
            QueryResult(
                id=r['id'],
                text=r['text'],
                distance=r['distance'],
                metadata=r['metadata']
            )
            for r in results
        ]
        
        logger.info(f"Query: '{request.query}' | Results: {len(formatted_results)}")
        
        return QueryResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )
    
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
