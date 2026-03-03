from pathlib import Path

# ===============================
# PATHS
# ===============================

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR.parent.parent / "storage"

JSON_PATH = STORAGE_DIR / "result.json"
XLSX_PATH = STORAGE_DIR / "source.xlsx"
OUTPUT_PATH = STORAGE_DIR / "result_filled.xlsx"