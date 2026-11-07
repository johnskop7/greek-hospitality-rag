"""Run from the project root:  python -m pytest"""
import pandas as pd

from src.eval_retrieval import compare_results, evaluate_retrieval, summarize, validate_phrases

CHUNKS = [
    {"filename": "faq.pdf", "text": "η δήλωση υποβάλλεται μέχρι τις 20 του επόμενου μήνα"},
    {"filename": "faq.pdf", "text": "ορισμός βραχυχρόνιας μίσθωσης"},
    {"filename": "law.pdf", "text": "πρόστιμο 5.000 ευρώ"},
]
QUESTIONS = pd.DataFrame([
    {"id": "Q1", "question": "προθεσμία;", "expected_file": "faq.pdf",
     "evidence_phrase": "20 του επόμενου"},
    {"id": "Q2", "question": "πρόστιμο;", "expected_file": "law.pdf",
     "evidence_phrase": "5\\.000 ευρώ|πέντε χιλιάδων"},
])


def fixed_order(order):
    """A fake search function that always returns the same ranking."""
    return lambda question, k: order[:k]


def test_validate_phrases():
    assert validate_phrases(CHUNKS, QUESTIONS) == []
    bad = QUESTIONS.assign(evidence_phrase=["δεν υπάρχει", "5\\.000"])
    assert validate_phrases(CHUNKS, bad) == ["Q1"]


def test_evaluate_ranks_and_hits_for_several_k():
    res = evaluate_retrieval(fixed_order([1, 0, 2]), CHUNKS, QUESTIONS, ks=(1, 2))
    q1, q2 = res.iloc[0], res.iloc[1]
    assert q1["first_rank"] == 2 and not q1["hit@1"] and q1["hit@2"]
    assert q1["doc_hit@1"]                       # chunk 1 is from faq.pdf: right file, wrong chunk
    assert q2["first_rank"] == 3 and not q2["hit@2"] and not q2["doc_hit@2"]


def test_missing_rank_is_na():
    res = evaluate_retrieval(fixed_order([1]), CHUNKS, QUESTIONS, ks=1, depth=1)
    assert res["first_rank"].isna().all()


def test_summarize():
    res = evaluate_retrieval(fixed_order([0, 2, 1]), CHUNKS, QUESTIONS, ks=(1, 2))
    table = summarize(res)
    assert list(table.index) == [1, 2]
    assert table.loc[1, "hit"] == 0.5 and table.loc[2, "hit"] == 1.0


def test_compare_labels():
    a = evaluate_retrieval(fixed_order([1, 0, 2]), CHUNKS, QUESTIONS, ks=1)
    b = evaluate_retrieval(fixed_order([0, 1, 2]), CHUNKS, QUESTIONS, ks=1)
    cmp = compare_results(a, b, "a", "b", k=1).set_index("id")
    assert cmp.loc["Q1", "change"] == "fixed" and cmp.loc["Q1", "rank_change"] == 1
    assert cmp.loc["Q2", "change"] == "both_miss"
