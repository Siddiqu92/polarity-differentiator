"""RAG Pipeline - Real Family Office Data (ChromaDB)."""
import csv
import re
from pathlib import Path

import chromadb

from src.paths import get_default_csv, CHROMA_DIR

COLLECTION_NAME = "family_offices"


def _safe_id(name: str, suffix: str, idx: int) -> str:
    base = re.sub(r"[^\w\-]", "_", name).strip("_")
    return f"{base}_{suffix}_{idx}"


class FamilyOfficeRAG:
    def __init__(self, persist_dir=None):
        self.persist_dir = str(persist_dir or CHROMA_DIR)
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = None

    def load_data(self, csv_path=None):
        """Load family office records from extracted CSV."""
        csv_path = Path(csv_path or get_default_csv())
        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSV not found: {csv_path}. Run: python -m src.data_extraction"
            )

        with open(csv_path, "r", encoding="utf-8") as f:
            records = list(csv.DictReader(f))
        print(f"[OK] Loaded {len(records)} records from {csv_path}")
        return records

    def create_chunks(self, records):
        chunks = []
        for idx, record in enumerate(records):
            name = record.get("name", "Unknown")
            chunks.append({
                "id": _safe_id(name, "entity", idx),
                "text": (
                    f"Family Office: {name}\n"
                    f"Description: {record.get('description', '')}\n"
                    f"Thesis: {record.get('investment_thesis', '')}\n"
                    f"Sectors: {record.get('sectors', '')}\n"
                    f"Location: {record.get('city', '')}, {record.get('state_region', '')}, {record.get('country', '')}\n"
                    f"Website: {record.get('website', '')}"
                ),
                "metadata": {
                    "name": name,
                    "sectors": str(record.get("sectors", ""))[:200],
                    "city": record.get("city", ""),
                    "country": record.get("country", ""),
                    "chunk_type": "entity",
                },
            })
            chunks.append({
                "id": _safe_id(name, "principal", idx),
                "text": (
                    f"Principal: {record.get('contact_full_name', '')}\n"
                    f"Title: {record.get('contact_job_title', '')}\n"
                    f"Family Office: {name}\n"
                    f"Location: {record.get('contact_location', '')}"
                ),
                "metadata": {
                    "name": name,
                    "principal": record.get("contact_full_name", ""),
                    "title": record.get("contact_job_title", ""),
                    "chunk_type": "principal",
                },
            })
            chunks.append({
                "id": _safe_id(name, "full", idx),
                "text": (
                    f"Family Office: {name}\n"
                    f"Full Description: {record.get('description', '')}\n"
                    f"Investment Thesis: {record.get('investment_thesis', '')}"
                ),
                "metadata": {"name": name, "chunk_type": "full"},
            })
            if record.get("confidence_score"):
                chunks.append({
                    "id": _safe_id(name, "verification", idx),
                    "text": (
                        f"Family Office: {name}\n"
                        f"Data Sources: {record.get('data_sources', '')}\n"
                        f"Verification Method: {record.get('verification_method', '')}\n"
                        f"Confidence Score: {record.get('confidence_score', '')}\n"
                        f"Verification Date: {record.get('verification_date', '')}\n"
                        f"Gaps Noted: {record.get('gaps_noted', '')}\n"
                        f"Recent Signals: {record.get('recent_signals_flag', '')}\n"
                        f"Recent Activity: {record.get('recent_activity_signals', '')}"
                    ),
                    "metadata": {
                        "name": name,
                        "chunk_type": "verification",
                        "confidence_score": record.get("confidence_score", ""),
                    },
                })
        print(f"[OK] Created {len(chunks)} chunks from {len(records)} records")
        return chunks

    def ingest_data(self, records, reset=True):
        """Ingest chunks into ChromaDB."""
        chunks = self.create_chunks(records)

        if reset:
            try:
                self.client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            self.collection.add(
                ids=[c["id"] for c in batch],
                documents=[c["text"] for c in batch],
                metadatas=[c["metadata"] for c in batch],
            )
        print(f"[OK] Ingested {len(chunks)} chunks into ChromaDB")
        return self.collection

    def chunk_count(self):
        if not self.collection:
            return 0
        return self.collection.count()

    def search(self, query, top_k=5):
        if not self.collection:
            raise ValueError("Collection not initialized. Call ingest_data() first.")
        results = self.collection.query(query_texts=[query], n_results=top_k)
        formatted = []
        if results and results.get("ids") and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                formatted.append({
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                })
        return formatted

    def get_all_offices(self):
        if not self.collection:
            return []
        all_data = self.collection.get()
        offices = set()
        for metadata in all_data.get("metadatas") or []:
            if metadata and "name" in metadata:
                offices.add(metadata["name"])
        return sorted(offices)


if __name__ == "__main__":
    rag = FamilyOfficeRAG()
    data = rag.load_data()
    rag.ingest_data(data)
    print(f"\n[OK] Offices indexed: {len(rag.get_all_offices())}")
    print(f"[OK] Chunks: {rag.chunk_count()}")
    print("\n[TEST QUERIES]")
    for query in [
        "Which family offices invest in real estate?",
        "Tech investment family offices",
        "Family offices in California",
    ]:
        print(f"\nQuery: {query}")
        for r in rag.search(query, top_k=3):
            print(f"  - {r['id']}: {r['text'][:150]}")
