from pypdf import PdfReader, PdfWriter

reader = PdfReader("data/raw/law_5170_2025.pdf")
writer = PdfWriter()
for i in range(1, 3):        # your page range, 0-indexed
    writer.add_page(reader.pages[i])
writer.write("data/raw/law_5170_2025_art3.pdf")