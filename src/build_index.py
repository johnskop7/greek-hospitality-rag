"""Build the FAISS index from data/raw and save it to index/.

Run from the project root:  python -m src.build_index
Re-run whenever documents, cleaning, chunking or the embedding model change.
"""
from collections import Counter

from src.config import INDEX_DIR
from src.ingest import build_chunks, load_pages
from src.retrieval import Retriever, get_device


def main() -> None:
    pages = load_pages()
    chunks = build_chunks(pages)
    print(f"{len(pages)} pages -> {len(chunks)} chunks")
    for filename, n in sorted(Counter(c["filename"] for c in chunks).items()):
        print(f"  {n:4d}  {filename}")

    print(f"Embedding on {get_device()} ...")
    retriever = Retriever.build(chunks)
    retriever.save(INDEX_DIR)
    print(f"Saved index ({retriever.index.ntotal} vectors) to {INDEX_DIR}")


if __name__ == "__main__":
    main()
