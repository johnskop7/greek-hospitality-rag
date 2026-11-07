"""Project settings and secrets in one place.

Paths are built from the project root (the folder that contains `src/`), so the
same code works from a notebook in `notebooks/`, from a script, or later from
FastAPI and Docker, whatever the current working directory is.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# --- Paths -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SOURCES_PATH = ROOT / "data" / "sources.csv"
QUESTIONS_PATH = ROOT / "eval" / "retrieval_questions.csv"
INDEX_DIR = ROOT / "index"            # built artifacts, ignored by Git

# --- Secrets (from .env, never committed) ------------------------------------
# Load .env from the project root explicitly: load_dotenv() alone looks in the
# current folder, which is notebooks/ when running a notebook.
load_dotenv(ROOT / ".env")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

# --- Chunking ----------------------------------------------------------------
CHUNK_SIZE = 1000      # characters
OVERLAP = 200          # characters shared by neighbouring chunks

# --- Retrieval ---------------------------------------------------------------
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
TOP_K = 15             # chunks passed to the LLM (e5 hit@15 = 0.833, see eval/experiments.md)

# --- Reranker (experiment only: too slow on CPU for deployment) ---------------
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
N_CANDIDATES = 30


if __name__ == "__main__":
    # Never print the key itself, only whether it's set
    print("Project root:", ROOT)
    print("API key set:", bool(LLM_API_KEY))
    print("Model:", LLM_MODEL)
