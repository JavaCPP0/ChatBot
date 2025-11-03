import pymupdf
import os

pdf_file_path = "chap04\data\생성형 AI 시대, AI 리터러시 교육의 방향.pdf"  # Path to your PDF file
doc = pymupdf.open(pdf_file_path)

header_height = 80  # Height of the header to be removed
footer_height = 80  # Height of the footer to be removed

full_text = ""

for page in doc:
    rect = page.rect
    
    header = page.get_text(clip=(0,0,rect.width,header_height))
    
    footer = page.get_text(clip=(0,rect.height - footer_height, rect.width, rect.height))
    
    text = page.get_text(clip=(0,header_height,rect.width, rect.height - footer_height))
    
    full_text += text + "\n------------------------------------------------\n"
    
pdf_file_name = os.path.basename(pdf_file_path)
pdf_file_name = os.path.splitext(os.path.basename(pdf_file_name))[0]

txt_file_path = f"chap04/output/{pdf_file_name}.txt"
with open(txt_file_path, "w", encoding="utf-8") as txt_file:
    txt_file.write(full_text)