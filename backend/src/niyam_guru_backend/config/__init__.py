# backend/src/niyam_guru_backend/config/__init__.py
from .settings import (
    BASE_DIR,
    DATA_DIR,
    RAW_JUDGMENTS_DIR,
    PROCESSED_DATA_DIR,
    VECTORSTORE_DIR,
    CONSUMER_LAWS_CSV,
    CONSUMER_CASES_CSV,
    GOOGLE_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
    DEBUG,
)

__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "RAW_JUDGMENTS_DIR",
    "PROCESSED_DATA_DIR",
    "VECTORSTORE_DIR",
    "CONSUMER_LAWS_CSV",
    "CONSUMER_CASES_CSV",
    "GOOGLE_API_KEY",
    "EMBEDDING_MODEL",
    "LLM_MODEL",
    "DEBUG",
]
