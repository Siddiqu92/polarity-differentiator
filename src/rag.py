"""RAG Pipeline - ChromaDB + Hybrid Retrieval"""
import csv
import json
from pathlib import Path
from datetime import datetime
import chromadb

class FamilyOfficeRAG:
    def __init__(self, persist_dir="chromadb_data"):
        """Initialize RAG system with ChromaDB (new API)"""
        self.persist_dir = persist_dir
        Path(persist_dir).mkdir(exist_ok=True)
        
        # New ChromaDB API - simpler approach
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None
        
    def load_data(self, csv_path="output/family_offices_enriched.csv"):
        """Load family office data from CSV"""
        records = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)
        print(f"✓ Loaded {len(records)} records from {csv_path}")
        return records
    
    def create_chunks(self, records):
        """Create logical chunks for each family office"""
        chunks = []
        for record in records:
            # Create 4 chunks per family office for semantic diversity
            chunks.append({
                "id": f"{record['name']}_entity",
                "text": f"Family Office: {record['name']}\nAUM: ${record['aum']}M\nGeography: {record['geography']}\nSectors: {record['sectors']}\nFounded: {record['founded']}",
                "source": record['name'],
                "type": "entity",
                "metadata": {
                    "name": record['name'],
                    "aum": record['aum'],
                    "geography": record['geography'],
                    "sectors": record['sectors']
                }
            })
            
            chunks.append({
                "id": f"{record['name']}_principal",
                "text": f"Principal: {record['principal']}\nTitle: {record['title']}\nFamily Office: {record['name']}\nLocation: {record['geography']}",
                "source": record['name'],
                "type": "principal",
                "metadata": {
                    "principal": record['principal'],
                    "title": record['title'],
                    "name": record['name']
                }
            })
            
            chunks.append({
                "id": f"{record['name']}_investment_thesis",
                "text": f"Investment Focus: {record['sectors']}\nInvestment Thesis: Sectors include {record['sectors']}\nFamily Office: {record['name']}\nGeographic Focus: {record['geography']}",
                "source": record['name'],
                "type": "thesis",
                "metadata": {
                    "sectors": record['sectors'],
                    "geography": record['geography'],
                    "name": record['name']
                }
            })
            
            chunks.append({
                "id": f"{record['name']}_verification",
                "text": f"Verification Status: {record['data_quality_score']}\nEntity Verified: {record['entity_verified']}\nPrincipal Verified: {record['principal_verified']}\nData Completeness: {record['data_completeness']}\nVerification Method: {record['verification_method']}",
                "source": record['name'],
                "type": "verification",
                "metadata": {
                    "data_quality": record['data_quality_score'],
                    "verification_method": record['verification_method'],
                    "name": record['name']
                }
            })
        
        print(f"✓ Created {len(chunks)} semantic chunks from {len(records)} records")
        return chunks
    
    def ingest_data(self, records):
        """Ingest chunks into ChromaDB"""
        chunks = self.create_chunks(records)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="family_offices",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add chunks in batches
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            ids = [c['id'] for c in batch]
            docs = [c['text'] for c in batch]
            metadatas = [c['metadata'] for c in batch]
            
            self.collection.add(
                ids=ids,
                documents=docs,
                metadatas=metadatas
            )
        
        print(f"✓ Ingested {len(chunks)} chunks into ChromaDB collection")
        return self.collection
    
    def search(self, query, top_k=5):
        """Semantic search"""
        if not self.collection:
            raise ValueError("Collection not initialized. Call ingest_data() first.")
        
        # Semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Process results
        formatted_results = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i, doc_id in enumerate(results['ids'][0]):
                formatted_results.append({
                    "id": doc_id,
                    "text": results['documents'][0][i] if i < len(results['documents'][0]) else "",
                    "distance": results['distances'][0][i] if i < len(results['distances'][0]) else 0,
                    "metadata": results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                })
        
        return formatted_results
    
    def get_all_offices(self):
        """Get all unique family offices"""
        if not self.collection:
            return []
        
        # Get all data from collection
        all_data = self.collection.get()
        offices = set()
        if all_data and all_data['metadatas']:
            for metadata in all_data['metadatas']:
                if 'name' in metadata:
                    offices.add(metadata['name'])
        
        return sorted(list(offices))

def initialize_rag():
    """Initialize RAG system"""
    rag = FamilyOfficeRAG()
    records = rag.load_data()
    rag.ingest_data(records)
    
    print("\n✓ RAG Pipeline initialized and ready!")
    print(f"✓ Collection: family_offices")
    print(f"✓ Offices indexed: {len(rag.get_all_offices())}")
    print(f"✓ Persistent storage: chromadb_data/")
    
    return rag

if __name__ == "__main__":
    rag = initialize_rag()
    
    # Test queries
    print("\n[TEST QUERIES]")
    test_queries = [
        "Which family offices invest in real estate?",
        "Find principals with CIO titles",
        "Tech investment family offices in California"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = rag.search(query, top_k=3)
        for result in results:
            print(f"  - {result['id']}: {result['text'][:100]}...")
