import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _flag(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 12  # 12 hours
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    MONGO_URI = os.getenv("MONGO_URI", "").strip()
    MONGO_DB = os.getenv("MONGO_DB", "ragnosis")
    USE_MOCK_DB = _flag("USE_MOCK_DB")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    ENABLE_NER = _flag("ENABLE_NER")
    NER_MODEL = os.getenv("NER_MODEL", "alvaroalon2/biobert_diseases_ner")
    ENABLE_SUMMARY = _flag("ENABLE_SUMMARY")
    SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "facebook/bart-large-cnn")

    UPLOAD_DIR = BASE_DIR / "data" / "uploads"
    INDEX_DIR = BASE_DIR / "data" / "indexes"
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]

    CHUNK_WORDS = 180
    CHUNK_OVERLAP = 40
    TOP_K = 4
