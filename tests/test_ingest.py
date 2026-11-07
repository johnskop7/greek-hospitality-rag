"""Run from the project root:  python -m pytest"""
from src.ingest import build_chunks, chunk_text, clean_text


def test_clean_joins_greek_hyphenation():
    assert clean_text("βραχυχρό-\nνιας") == "βραχυχρόνιας"
    assert clean_text("κα - ταλυμάτων") == "καταλυμάτων"
    assert clean_text("τουριστι - κών") == "τουριστικών"


def test_clean_keeps_real_dashes():
    assert clean_text("Α.1217/2023 - ΦΕΚ") == "Α.1217/2023 - ΦΕΚ"


def test_clean_collapses_whitespace():
    assert clean_text("ΑΑΔΕ   \n\n  ΦΕΚ") == "ΑΑΔΕ ΦΕΚ"


def test_clean_removes_toc_dot_leaders():
    assert clean_text("Βασικές Έννοιες........2") == "Βασικές Έννοιες 2"
    assert clean_text("Βασικές Έννοιες ........ 2") == "Βασικές Έννοιες 2"


def test_chunk_size_overlap_and_word_boundaries():
    words = [f"λέξη{i}" for i in range(2000)]
    chunks = chunk_text(" ".join(words), chunk_size=1000, overlap=200)
    assert all(len(c) <= 1000 for c in chunks)                  # size limit respected
    assert chunks[0].split()[-1] in chunks[1].split()           # overlap exists
    assert all(w in set(words) for c in chunks for w in c.split())   # no word cut in half
    assert chunks[-1].endswith("λέξη1999")                      # nothing lost at the end


def test_chunk_edge_cases():
    assert chunk_text("") == []
    assert chunk_text("σύντομο κείμενο") == ["σύντομο κείμενο"]


def test_build_chunks_ids_are_unique_and_text_is_cleaned():
    pages = [{"filename": "a.pdf", "page": 1, "text": "βραχυχρό-\nνιας " * 300},
             {"filename": "a.pdf", "page": 2, "text": "δεύτερη σελίδα"}]
    chunks = build_chunks(pages)
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))
    assert ids[0] == "a.pdf_p1_c0"
    assert chunks[-1] == {"chunk_id": "a.pdf_p2_c0", "filename": "a.pdf",
                          "page": 2, "text": "δεύτερη σελίδα"}
    assert "\n" not in chunks[0]["text"] and "βραχυχρόνιας" in chunks[0]["text"]
