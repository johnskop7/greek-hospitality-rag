"""Run from the project root:  python -m pytest   (no API calls: the LLM is replaced by a fake)"""
import pandas as pd

import src.generation as gen
from src.llm import LLMResponse

SOURCES = pd.DataFrame([
    {"filename": "faq.pdf", "title": "FAQ", "publisher": "ΑΑΔΕ", "url": "u1", "published_date": "2025-09-23"},
    {"filename": "pol.pdf", "title": "ΠΟΛ", "publisher": "ΑΑΔΕ", "url": "u2", "published_date": "2017-11-23"},
]).set_index("filename")
CHUNKS = [
    {"chunk_id": "faq.pdf_p16_c3", "filename": "faq.pdf", "page": 16, "text": "μέχρι τις 20 του επόμενου μήνα"},
    {"chunk_id": "pol.pdf_p8_c1", "filename": "pol.pdf", "page": 8, "text": "επομένης εργάσιμης ημέρας"},
]


class FakeRetriever:
    chunks = CHUNKS

    def search(self, question, k):
        return [1, 0][:k]          # the 2017 chunk is ranked first on purpose


def test_user_message_has_numbered_excerpts_with_dates_and_question_last():
    msg = gen.build_user_message("Μέχρι πότε;", [1, 0], CHUNKS, SOURCES)
    assert msg.index('id="1"') < msg.index('id="2"')
    assert 'date="2017-11-23"' in msg and 'date="2025-09-23"' in msg
    assert msg.endswith("Ερώτηση: Μέχρι πότε;")


def test_citations_map_to_the_right_chunk_and_flag_invented_numbers():
    text = "Μέχρι τις 20 του επόμενου μήνα [2]. Επίσης [2][9]."
    citations, invalid = gen.extract_citations(text, [1, 0], CHUNKS, SOURCES)
    assert [c["chunk_id"] for c in citations] == ["faq.pdf_p16_c3"]   # [2] -> second retrieved = chunk 0
    assert citations[0]["page"] == 16 and citations[0]["url"] == "u1"
    assert invalid == [9]


def test_answer_and_refusal(monkeypatch):
    monkeypatch.setattr(gen, "ask_llm", lambda s, u: LLMResponse("Έως τις 20 [2].", 500, 10))
    r = gen.answer("Μέχρι πότε;", FakeRetriever(), SOURCES, k=2)
    assert not r["refused"] and r["citations"][0]["filename"] == "faq.pdf"
    assert r["retrieved"] == ["pol.pdf_p8_c1", "faq.pdf_p16_c3"]

    monkeypatch.setattr(gen, "ask_llm", lambda s, u: LLMResponse(gen.REFUSAL, 500, 10))
    r = gen.answer("Ιταλία;", FakeRetriever(), SOURCES, k=2)
    assert r["refused"] and r["citations"] == []


def test_truncated_answer_is_flagged(monkeypatch):
    monkeypatch.setattr(gen, "ask_llm",
                        lambda s, u: LLMResponse("Έως τις 20 [2", 500, 2000, "max_tokens"))
    assert gen.answer("Μέχρι πότε;", FakeRetriever(), SOURCES, k=2)["truncated"]
