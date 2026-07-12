"""RAG Pipeline - Real Family Office Data (ChromaDB)"""
import csv
from pathlib import Path
import chromadb

class FamilyOfficeRAG:
    def __init__(self, persist_dir="chromadb_data"):
        self.persist_dir = persist_dir
        Path(persist_dir).mkdir(exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None

    def load_data(self, csv_path="output/family_offices_extracted.csv"):
        """Load REAL family office data from extracted CSV"""
        records = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)
        print(f"✓ Loaded {len(records)} REAL records from {csv_path}")
        return records

    def create_chunks(self, records):
        chunks = []
        for record in records:
            name = record.get('name', 'Unknown')
            chunks.append({
                "id": f"{name}_entity",
                "text": f"Family Office: {name}\nDescription: {record.get('description','')}\nThesis: {record.get('investment_thesis','')}\nSectors: {record.get('sectors','')}\nLocation: {record.get('city','')}, {record.get('state_region','')}, {record.get('country','')}\nWebsite: {record.get('website','')}",
                "metadata": {"name": name, "sectors": str(record.get('sectors',''))[:200], "city": record.get('city',''), "country": record.get('country','')}
            })
            chunks.append({
                "id": f"{name}_principal",
                "text": f"Principal: {record.get('contact_full_name','')}\nTitle: {record.get('contact_job_title','')}\nFamily Office: {name}\nLocation: {record.get('contact_location','')}",
                "metadata": {"principal": record.get('contact_full_name',''), "title": record.get('contact_job_title',''), "name": name}
            })
            chunks.append({
                "id": f"{name}_full",
                "text": f"Family Office: {name}\nFull Description: {record.get('description','')}\nInvestment Thesis: {record.get('investment_thesis','')}",
                "metadata": {"name": name}
            })
        print(f"✓ Created {len(chunks)} semantic chunks from {len(records)} REAL records")
        return chunks

    def ingest_data(self, records):
        chunks = self.create_chunks(records)
        self.collection = self.client.get_or_create_collection(name="family_offices", metadata={"hnsw:space": "cosine"})
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            self.collection.add(ids=[c['id'] for c in batch], documents=[c['text'] for c in batch], metadatas=[c['metadata'] for c in batch])
        print(f"✓ Ingested {len(chunks)} chunks into ChromaDB")
        return self.collection

    def search(self, query, top_k=5):
        if not self.collection:
            raise ValueError("Collection not initialized.")
        results = self.collection.query(query_texts=[query], n_results=top_k)
        formatted_results = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i, doc_id in enumerate(results['ids'][0]):
                formatted_results.append({"id": doc_id, "text": results['documents'][0][i], "distance": results['distances'][0][i], "metadata": results['metadatas'][0][i]})
        return formatted_results

    def get_all_offices(self):
        if not self.collection:
            return []
        all_data = self.collection.get()
        offices = set()
        if all_data and all_data['metadatas']:
            for metadata in all_data['metadatas']:
                if 'name' in metadata:
                    offices.add(metadata['name'])
        return sorted(list(offices))

if __name__ == "__main__":
    rag = FamilyOfficeRAG()
    records = rag.load_data()
    rag.ingest_data(records)
    print(f"\n✓ Offices indexed: {len(rag.get_all_offices())}")
    print(f"✓ Offices: {rag.get_all_offices()[:5]}...")
    print("\n[TEST QUERIES]")
    for query in ["Which family offices invest in real estate?", "Tech investment family offices", "Family offices in California"]:
        print(f"\nQuery: {query}")
        results = rag.search(query, top_k=3)
        for r in results:
            print(f"  - {r['id']}: {r['text'][:150]}")
