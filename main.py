import csv
import pdfplumber

content = ''

def normalize_header(header):
    #print(header)
    """
    Chuẩn hóa tên cột để dễ truy cập (xóa \n, lowercase)
    """
    return [col.replace("\n", " ").strip().lower() for col in header]

def normalize_combined_header(header_rows):
    """
    Gộp nhiều dòng header thành một dòng duy nhất.
    """
    combined=[]
    for i in range(2):
        for j in range(1, len(header_rows[0])):
            if(header_rows[i][j] == None):
                header_rows[i][j] = header_rows[i][j-1]
    combined = [str(header_rows[0][i]).strip() + " " + str(header_rows[1][i]).strip() for i in range(len(header_rows[0]))]
    #print(combined)
    return combined

def row_to_text(row, header):
    """
    Chuyển 1 dòng thành mô tả văn bản dựa trên header
    """
    parts = []
    for col_name, value in zip(header, row):
        value = value.strip() if isinstance(value, str) else str(value)
        if value == '-' or value == '':
            value = "không công bố"
        parts.append(f"{col_name}: {value}")
    return "; ".join(parts) + "."

def table_to_docs(table):
    """
    Nhận vào bảng dạng list of lists → list văn bản
    """

    if any(cell is None for cell in table[0]):
        raw_header = table[0:2]
        rows = table[2:]
        header = normalize_combined_header(raw_header)
    else:
        raw_header = table[0]
        rows = table[1:]
        header = normalize_header(raw_header)

    docs = []
    for row in rows:
        if len(row) != len(header):
            # Bỏ qua dòng không khớp số cột
            continue
        doc = row_to_text(row, header)
        docs.append(doc)
    return docs

with pdfplumber.open("fixed.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"Trang {i+1}:")

        # 1. Tìm tất cả bảng và lấy tọa độ (bounding boxes)
        table_bboxes = []
        tables = page.extract_tables()
        for table in page.find_tables():
            table_bboxes.append(table.bbox)

        # 2. Lấy tất cả các dòng chữ
        non_table_words = []
        for word in page.extract_words():
            x0, top, x1, bottom = word["x0"], word["top"], word["x1"], word["bottom"]

            in_table = False
            for (bx0, btop, bx1, bbottom) in table_bboxes:
                if x0 >= bx0 and x1 <= bx1 and top >= btop and bottom <= bbottom:
                    in_table = True
                    break

            if not in_table:
                non_table_words.append(word)

        # 3. Ghép lại thành văn bản (nếu cần)
        text = " ".join(w["text"] for w in non_table_words)
        content += text

        # 4. Xử lý bảng riêng
        for table in tables:
            docs = table_to_docs(table=table)
            for doc in docs:
                content+=doc
        
        content+='\n'
            
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(content)


