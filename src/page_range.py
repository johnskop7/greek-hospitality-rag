from pypdf import PdfReader, PdfWriter

reader = PdfReader("data/raw/fek_A1202_2024.pdf")
writer = PdfWriter()
for i in range(0, 2):        # your page range, 0-indexed
    writer.add_page(reader.pages[i])
writer.write("data/raw/fek_A1202_2024.pdf")