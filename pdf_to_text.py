import pymupdf
import os

pdf_file_path = "chap04\data\생성형 AI 시대, AI 리터러시 교육의 방향.pdf"  # Path to your PDF file
doc = pymupdf.open(pdf_file_path)

full_text = ""

for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text = page.get_text()
    full_text += text + "\n"
    
pdf_file_name = os.path.basename(pdf_file_path)
pdf_file_name = os.path.splitext(os.path.basename(pdf_file_name))[0]

txt_file_path = f"chap04/output/{pdf_file_name}.txt"
with open(txt_file_path, "w", encoding="utf-8") as txt_file:
    txt_file.write(full_text)