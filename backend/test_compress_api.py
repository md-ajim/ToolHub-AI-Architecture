from pypdf import PdfWriter, PdfReader
writer = PdfWriter()
writer.add_blank_page(width=72, height=72)
with open("real_dummy.pdf", "wb") as f:
    writer.write(f)

reader = PdfReader("real_dummy.pdf")
print("Has compress_content_streams?", hasattr(reader.pages[0], 'compress_content_streams'))
