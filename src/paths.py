"""Project root paths — run scripts from any working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DOCS_DIR = ROOT / "docs"
LOGS_DIR = ROOT / "logs"
CHROMA_DIR = ROOT / "chromadb_data"

EXCEL_FILE = DATA_DIR / "FO-MAX-data-sample-2.0.xlsx"
EXTRACTED_CSV = OUTPUT_DIR / "family_offices_extracted.csv"
ENRICHED_CSV = OUTPUT_DIR / "family_offices_enriched_verified.csv"


def get_default_csv():
    """Prefer enriched verified CSV when available."""
    return ENRICHED_CSV if ENRICHED_CSV.exists() else EXTRACTED_CSV
VALIDATION_CHAINS = DOCS_DIR / "validation_chains.json"
VALIDATION_REPORT = DOCS_DIR / "validation_report.json"
BUILD_LOG = LOGS_DIR / "build_log.txt"
