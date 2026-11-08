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

# --- LLM call settings -------------------------------------------------------
# Haiku 5.5 thinks by default and thinking tokens count toward max_tokens, so
# max_tokens must leave room for thinking *and* the answer.
LLM_MAX_TOKENS = 2000
LLM_EFFORT = "low"      # "low" | "medium" (Haiku 5.5 default) | "high" | ...; None = model default
LLM_THINKING = True     # False sends thinking={"type": "disabled"}

# --- Chunking ----------------------------------------------------------------
CHUNK_SIZE = 1000      # characters
OVERLAP = 200          # characters shared by neighbouring chunks

# --- Retrieval ---------------------------------------------------------------
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
TOP_K = 15             # chunks passed to the LLM (e5 hit@15 = 0.833, see eval/experiments.md)

# --- Context building (generation only; retrieval metrics are unaffected) -----
# Neighbours of the best chunks are added and consecutive chunks are merged, so a
# list keeps its heading (e.g. "Νοέμβριο έως Μάρτιο" in p2_c2 for the amounts in p2_c3).
EXPAND_TOP = 5         # add neighbours of the EXPAND_TOP best-ranked chunks ...
NEIGHBOR_WINDOW = 1    # ... up to this many chunks before and after, on the same page

# --- Reranker (experiment only: too slow on CPU for deployment) ---------------
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
N_CANDIDATES = 30


if __name__ == "__main__":
    # Never print the key itself, only whether it's set
    print("Project root:", ROOT)
    print("API key set:", bool(LLM_API_KEY))
    print("Model:", LLM_MODEL)
