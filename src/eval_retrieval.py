"""Retrieval evaluation with evidence phrases.

A question counts as a hit@k if any of the top-k retrieved chunks contains its
evidence phrase (a regex; alternatives separated by "|"). Labels are phrases,
not chunk IDs, so they keep working when the chunking changes.
"""

import re
from typing import Callable
from tqdm.auto import tqdm

import pandas as pd

SearchFn = Callable[[str, int], list[int]]  # (question, k) -> ordered chunk indices


def load_questions(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")


def validate_phrases(chunks: list[dict], questions: pd.DataFrame) -> list[str]:
    """Return IDs of questions whose evidence phrase matches no chunk at all."""
    missing = []
    for _, q in questions.iterrows():
        if not any(re.search(q["evidence_phrase"], c["text"]) for c in chunks):
            missing.append(q["id"])
    return missing


def evaluate_retrieval(search: SearchFn, chunks: list[dict], questions: pd.DataFrame,
                       k: int = 5, depth: int = 50, progress: bool = False) -> pd.DataFrame:
    """Run every question through `search` and score it.

    Columns: hit@k (chunk-level), doc_hit@k (document-level), and first_rank
    (1-based rank of the first chunk containing the phrase within `depth`,
    or None if it is not in the top `depth`).
    """
    rows = []
    iterator = questions.iterrows()
    if progress:
        iterator = tqdm(iterator, total=len(questions), desc="Evaluating retrieval")
    for _, q in iterator:
        ranked = search(q["question"], depth)
        expected_files = set(q["expected_file"].split("|"))
        first_rank = next(
            (r for r, idx in enumerate(ranked, start=1)
             if re.search(q["evidence_phrase"], chunks[idx]["text"])),
            None,
        )
        rows.append({
            "id": q["id"],
            f"hit@{k}": first_rank is not None and first_rank <= k,
            f"doc_hit@{k}": any(chunks[i]["filename"] in expected_files for i in ranked[:k]),
            "first_rank": first_rank,
        })
    return pd.DataFrame(rows)
