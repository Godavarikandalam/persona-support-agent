"""
config.py
---------
Central place for API keys, model names, and tunable thresholds.
Keeping these here means no other module hardcodes a magic number.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file at project root

# --- API ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --- Models ---
# NOTE: Gemini model names change over time. If a model below 404s,
# check https://ai.google.dev/gemini-api/docs/models for the current name.
GENERATION_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "gemini-embedding-001"

# --- RAG / Chunking ---
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

# --- Vector DB ---
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "support_kb"

# --- Escalation thresholds ---
# If the best retrieved chunk's similarity score is below this, we don't
# trust the context enough to answer -> escalate to a human instead.
RETRIEVAL_CONFIDENCE_THRESHOLD = 0.35

# Topics that should always be escalated regardless of retrieval quality,
# because they involve money, legal exposure, or account-level changes.
SENSITIVE_KEYWORDS = [
    "refund", "chargeback", "lawsuit", "legal", "sue", "cancel my account",
    "delete my account", "dispute", "fraud", "unauthorized charge",
]

# How many consecutive "Frustrated User" turns before we escalate purely
# on sentiment grounds, even if retrieval looked fine.
MAX_CONSECUTIVE_FRUSTRATION = 3

# --- Personas ---
PERSONAS = ["Technical Expert", "Frustrated User", "Business Executive"]
