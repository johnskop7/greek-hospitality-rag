from pathlib import Path
from pypdf import PdfReader
import pandas as pd

RAW_DIR = Path("data/raw")
data = pd.read_csv(RAW_DIR / "sources.csv")
df = pd.DataFrame(data)

for pdf_path in sorted(RAW_DIR.glob("*.pdf")):
    reader = PdfReader(pdf_path)
    text = "".join(page.extract_text() or "" for page in reader.pages)
    print(f"\n=== {pdf_path.name} | {len(reader.pages)} pages | {len(text)} chars")
    print(text[:300].replace("\n", " "))

    assert pdf_path.name in df["filename"].values, f"{pdf_path.name} not found in sources.csv"

