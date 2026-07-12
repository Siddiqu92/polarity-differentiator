"""Micro-RAG Pipeline - ChromaDB based"""
import pandas as pd
import chromadb
import json
from pathlib import Path

class FORAGPipeline:
    def __init__(self, db_path="./chromadb_data"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None

    def chunk_fo_record(self, record):
        chunks = []

        entity_chunk = f"""Family Office: {record.get('name','')}
Description: {record.get('description','')}
Thesis: {record.get('investment_thesis','')}
Sectors: {record.get('sectors','')}
Location: {record.get('city','')}, {record.get('state_region','')}, {record.get('country','')}
Website: {record.get('website','')}
"""
        chunks.append(("entity", entity_chunk))

        principal_chunk = f"""Principal: {record.get('contact_full_name','')}
Title: {record.get('contact_job_title','')}
Location: {record.get('contact_location','')}
Email: {record.get('contact_email','')}
Phone: {record.get('contact_phone','')}
"""
        chunks.append(("principal", principal_chunk))

        full_chunk = json.dumps({k: str(v) for k, v in record.items()})
        chunks.append(("full", full_chunk))

        return chunks

    def ingest_dataset(self, csv_file="output/family_offices_extracted.csv"):
        df = pd.read_csv(csv_file)
        df = df.fillna("")

        self.collection = self.client.get_or_create_collection(
            name="family_offices",
            metadata={"hnsw:space": "cosine"}
        )

        print(f"Ingesting {len(df)} records...")

        ids, docs, metas = [], [], []

        for idx, record in df.iterrows():
            chunks = self.chunk_fo_record(record)
            for chunk_type, chunk_text in chunks:
                doc_id = f"{record['name']}_{chunk_type}_{idx}".replace(" ", "_").replace("/", "-")
                ids.append(doc_id)
                docs.append(chunk_text)
                metas.append({
                    "fo_name": str(record['name']),
                    "chunk_type": chunk_type
                })

        self.collection.add(ids=ids, documents=docs, metadatas=metas)
        print(f"✓ Ingested {len(ids)} chunks into ChromaDB")

    def query(self, query_text, n_results=5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results


def main():
    print("Initializing RAG Pipeline...")
    rag = FORAGPipeline()
    rag.ingest_dataset()

    print("\nTesting query: 'family offices in real estate'")
    results = rag.query("family offices in real estate", n_results=3)

    for i, doc in enumerate(results['documents'][0]):
        print(f"\n--- Result {i+1} ---")
        print(doc[:200])

if __name__ == "__main__":
    main()
