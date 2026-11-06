from pathlib import Path
from pypdf import PdfReader
import pandas as pd

RAW_DIR = Path("data/raw")
df = pd.read_csv("data/sources.csv")

for pdf_path in sorted(RAW_DIR.glob("*.pdf")):
    reader = PdfReader(pdf_path)
    text = "".join(page.extract_text() or "" for page in reader.pages)
    print(f"\n=== {pdf_path.name} | {len(reader.pages)} pages | {len(text)} chars")
    print(text[:300].replace("\n", " "))

files_on_disk = {pdf_path.name for pdf_path in RAW_DIR.glob("*.pdf")}
files_in_csv = set(df["filename"])

print(f"\nFiles on disk: {len(files_on_disk)}")
print(f"Files in CSV: {len(files_in_csv)}")
print(f"Files in CSV but not on disk: {files_in_csv - files_on_disk}")
print(f"Files on disk but not in CSV: {files_on_disk - files_in_csv}")
