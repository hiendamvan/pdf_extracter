from pypdf import PdfReader, PdfWriter

reader = PdfReader("tuyensinh.pdf")
writer = PdfWriter()
cnt = 0

for page in reader.pages:
    cnt+=1
    # Nếu không có CropBox thì đặt bằng MediaBox
    if "/CropBox" not in page:
        page.cropbox = page.mediabox
    writer.add_page(page)

with open("fixed.pdf", "wb") as f:
    writer.write(f)
