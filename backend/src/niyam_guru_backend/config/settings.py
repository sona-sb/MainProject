# backend/src/niyam_guru_backend/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parents[3]  # backend/
PROJECT_ROOT = BASE_DIR.parent  # niyam-guru/
DATA_DIR = PROJECT_ROOT / "data"  # niyam-guru/data/ (for raw data and CSVs)
BACKEND_DATA_DIR = BASE_DIR / "data"  # backend/data/ (for vectorstore)

RAW_JUDGMENTS_DIR = DATA_DIR / "raw_judgements"  # Note: British spelling with 'e'
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTORSTORE_DIR = BACKEND_DATA_DIR / "vectorstore" / "consumer_act_gemini_db"

# Dataset files
CONSUMER_LAWS_CSV = PROCESSED_DATA_DIR / "consumer_laws.csv"
CONSUMER_CASES_CSV = PROCESSED_DATA_DIR / "consumer_cases_extracted.csv"

# LLM / Embeddings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-pro")

# Misc app options
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
