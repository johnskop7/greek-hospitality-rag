"""Run from the project root:  python -m pytest   (no API calls: the LLM is replaced by a fake)"""
import pandas as pd

import src.generation as gen
from src.ingest import chunk_text
from src.llm import LLMResponse

SOURCES = pd.DataFrame([
    {"filename": "faq.pdf", "title": "FAQ", "publisher": "ΑΑΔΕ", "url": "u1", "published_date": "2025-09-23"},
    {"filename": "pol.pdf", "title": "ΠΟΛ", "publisher": "ΑΑΔΕ", "url": "u2", "published_date": "2017-11-23"},
    {"filename": "a.pdf", "title": "A", "publisher": "ΦΕΚ", "url": "u3", "published_date": "2024-12-31"},
]).set_index("filename")
CHUNKS = [
    {"chunk_id": "faq.pdf_p16_c3", "filename": "faq.pdf", "page": 16, "text": "μέχρι τις 20 του επόμενου μήνα"},
    {"chunk_id": "pol.pdf_p8_c1", "filename": "pol.pdf", "page": 8, "text": "επομένης εργάσιμης ημέρας"},
]
PAGE = [{"chunk_id": f"a.pdf_p2_c{i}", "filename": "a.pdf", "page": 2, "text": f"t{i}"}
        for i in range(4)]


class FakeRetriever:
    chunks = CHUNKS

    def search(self, question, k):
        return [1, 0][:k]          # the 2017 chunk is ranked first on purpose


# --- expand_neighbors ---------------------------------------------------------
def test_expand_adds_both_neighbours_of_top_chunks():
    assert gen.expand_neighbors([1], PAGE, window=1, top=5) == [1, 0, 2]


def test_expand_skips_missing_and_existing():
    assert gen.expand_neighbors([0, 1], PAGE, window=1, top=5) == [0, 1, 2]   # no c-1; c1 already present


def test_expand_only_top():
    assert gen.expand_neighbors([3, 0], PAGE, window=1, top=1) == [3, 0, 2]   # only c3 is expanded


def test_expand_never_crosses_pages_or_files():
    chunks = PAGE + [{"chunk_id": "a.pdf_p3_c0", "filename": "a.pdf", "page": 3, "text": "x"}]
    assert gen.expand_neighbors([3], chunks, window=1, top=5) == [3, 2]


# --- join_overlapping / merge_chunks -----------------------------------------
def test_join_overlapping():
    assert gen.join_overlapping("ένα δύο τρία τέσσερα", "τρία τέσσερα πέντε") == "ένα δύο τρία τέσσερα πέντε"
    assert gen.join_overlapping("ένα δύο", "τρία") == "ένα δύο τρία"           # no overlap: join with a space
    assert gen.join_overlapping("καλά", "αύριο") == "καλά αύριο"               # a shared letter is not an overlap


def test_merging_consecutive_chunks_restores_the_page():
    page_text = " ".join(f"λέξη{i}" for i in range(1500))
    pieces = chunk_text(page_text, chunk_size=1000, overlap=200)
    chunks = [{"chunk_id": f"a.pdf_p2_c{i}", "filename": "a.pdf", "page": 2, "text": t}
              for i, t in enumerate(pieces)]
    order = list(range(len(chunks)))[::-1]                     # any retrieval order
    excerpts = gen.merge_chunks(order, chunks)
    assert len(excerpts) == 1 and excerpts[0]["text"] == page_text


def test_merge_keeps_gaps_separate_and_orders_by_best_rank():
    excerpts = gen.merge_chunks([3, 0, 1], PAGE)              # c0+c1 merge; c3 is not next to them
    assert [e["chunk_ids"] for e in excerpts] == [["a.pdf_p2_c3"], ["a.pdf_p2_c0", "a.pdf_p2_c1"]]


# --- prompt, citations, answer -----------------------------------------------
def test_user_message_has_numbered_excerpts_with_dates_and_question_last():
    msg = gen.build_user_message("Μέχρι πότε;", gen.merge_chunks([1, 0], CHUNKS), SOURCES)
    assert msg.index('id="1"') < msg.index('id="2"')
    assert 'date="2017-11-23"' in msg and 'date="2025-09-23"' in msg
    assert msg.endswith("Ερώτηση: Μέχρι πότε;")


def test_citations_map_to_the_right_excerpt_and_flag_invented_numbers():
    excerpts = gen.merge_chunks([1, 0], CHUNKS)                # [1] = ΠΟΛ, [2] = FAQ
    citations, invalid = gen.extract_citations("Έως τις 20 [2]. Επίσης [2][9].", excerpts, SOURCES)
    assert [c["chunk_ids"] for c in citations] == [["faq.pdf_p16_c3"]]
    assert citations[0]["page"] == 16 and citations[0]["url"] == "u1"
    assert invalid == [9]


def test_answer_and_refusal(monkeypatch):
    monkeypatch.setattr(gen, "ask_llm", lambda s, u, **kw: LLMResponse("Έως τις 20 [2].", 500, 10))
    r = gen.answer("Μέχρι πότε;", FakeRetriever(), SOURCES, k=2)
    assert not r["refused"] and r["citations"][0]["filename"] == "faq.pdf"
    assert r["retrieved"] == ["pol.pdf_p8_c1", "faq.pdf_p16_c3"]

    monkeypatch.setattr(gen, "ask_llm", lambda s, u, **kw: LLMResponse(gen.REFUSAL, 500, 10))
    r = gen.answer("Ιταλία;", FakeRetriever(), SOURCES, k=2)
    assert r["refused"] and r["citations"] == []


def test_llm_options_are_passed_through(monkeypatch):
    seen = {}

    def fake(system, user, **kw):
        seen.update(kw)
        return LLMResponse("x [1].", 1, 1)
    monkeypatch.setattr(gen, "ask_llm", fake)
    gen.answer("q", FakeRetriever(), SOURCES, k=2, effort="medium")
    assert seen == {"effort": "medium"}


def test_truncated_answer_is_flagged(monkeypatch):
    monkeypatch.setattr(gen, "ask_llm",
                        lambda s, u, **kw: LLMResponse("Έως τις 20 [2", 500, 2000, "max_tokens"))
    assert gen.answer("Μέχρι πότε;", FakeRetriever(), SOURCES, k=2)["truncated"]
