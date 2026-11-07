"""Retrieval evaluation with evidence phrases.

A question counts as a hit@k if any of the top-k retrieved chunks contains its
evidence phrase (a regex; alternatives separated by "|"). Labels are phrases,
not chunk IDs, so they keep working when the chunking changes.

- hit@k      chunk level: the right *passage* is in the top k
- doc_hit@k  document level: a chunk from an expected *file* is in the top k
             (easier; it hides chunk-level misses, so we report both)
- first_rank where the first matching chunk is, within the top `depth`
"""
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Callable

import pandas as pd
from tqdm.auto import tqdm

from src.config import QUESTIONS_PATH

SearchFn = Callable[[str, int], list[int]]  # (question, k) -> ordered chunk indices


def load_questions(path: Path = QUESTIONS_PATH) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")


def validate_phrases(chunks: list[dict], questions: pd.DataFrame) -> list[str]:
    """Return IDs of questions whose evidence phrase matches no chunk at all.

    Run after any change to cleaning or chunking.
    """
    return [q["id"] for _, q in questions.iterrows()
            if not any(re.search(q["evidence_phrase"], c["text"]) for c in chunks)]


def evaluate_retrieval(search: SearchFn, chunks: list[dict], questions: pd.DataFrame,
                       ks: int | Sequence[int] = 5, depth: int = 50,
                       progress: bool = False) -> pd.DataFrame:
    """Run every question through `search` once and score it for every k in `ks`.

    Returns one row per question with first_rank and, for each k,
    hit@k and doc_hit@k. `search` is called once per question with `depth`,
    so evaluating several k values costs no extra searches.
    """
    ks = [ks] if isinstance(ks, int) else list(ks)
    rows = []
    iterator = questions.iterrows()
    if progress:
        iterator = tqdm(iterator, total=len(questions), desc="Evaluating retrieval")
    for _, q in iterator:
        ranked = search(q["question"], max(depth, *ks))
        expected_files = set(q["expected_file"].split("|"))
        first_rank = next(
            (r for r, idx in enumerate(ranked, start=1)
             if re.search(q["evidence_phrase"], chunks[idx]["text"])),
            None,
        )
        row = {"id": q["id"], "first_rank": first_rank}
        for k in ks:
            row[f"hit@{k}"] = first_rank is not None and first_rank <= k
            row[f"doc_hit@{k}"] = any(chunks[i]["filename"] in expected_files
                                      for i in ranked[:k])
        rows.append(row)
    df = pd.DataFrame(rows)
    df["first_rank"] = df["first_rank"].astype("Int64")   # integer column that allows missing values
    return df


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    """Mean of every hit@k / doc_hit@k column, as a small table indexed by k."""
    table = {}
    for col in results.columns:
        if col.startswith(("hit@", "doc_hit@")):
            metric, k = col.split("@")
            table.setdefault(int(k), {})[metric] = results[col].mean()
    return pd.DataFrame(table).T.rename_axis("k").sort_index()


def compare_results(results_a: pd.DataFrame, results_b: pd.DataFrame,
                    name_a: str = "a", name_b: str = "b", k: int = 5) -> pd.DataFrame:
    """Compare two evaluate_retrieval() outputs question by question.

    Each question gets a `change` label:
      fixed      miss in A, hit in B
      broken     hit in A, miss in B
      both_hit   hit in both
      both_miss  miss in both
    `rank_change` = rank in A - rank in B (positive = B moved the correct chunk up).
    A missing rank (not in the top `depth`) gives an empty rank_change.
    """
    hit = f"hit@{k}"
    a = results_a[["id", hit, "first_rank"]].rename(
        columns={hit: f"hit_{name_a}", "first_rank": f"rank_{name_a}"})
    b = results_b[["id", hit, "first_rank"]].rename(
        columns={hit: f"hit_{name_b}", "first_rank": f"rank_{name_b}"})
    df = a.merge(b, on="id", how="outer", validate="one_to_one")

    labels = {(False, True): "fixed", (True, False): "broken",
              (True, True): "both_hit", (False, False): "both_miss"}
    df["change"] = [labels[(bool(x), bool(y))]
                    for x, y in zip(df[f"hit_{name_a}"], df[f"hit_{name_b}"])]

    for col in (f"rank_{name_a}", f"rank_{name_b}"):
        df[col] = df[col].astype("Int64")
    df["rank_change"] = df[f"rank_{name_a}"] - df[f"rank_{name_b}"]

    order = {"fixed": 0, "broken": 1, "both_miss": 2, "both_hit": 3}
    df = df.sort_values(["change", "id"],
                        key=lambda s: s.map(order) if s.name == "change" else s)
    return df.reset_index(drop=True)
