from openai import OpenAI
from dotenv import load_dotenv
import os
import pymupdf

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("OPENAI_API_KEY")

def pdf_to_txt(pdf_file_path: str):
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

    # Return the path to the created text file so callers can use it
    return txt_file_path




def summarize_txt(file_path: str):
    client = OpenAI(api_key=api_key)
    
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
        
        system_prompt = f'''
        너는 다음 글을 요약하는 봇이다. 아래 글을 읽고, 저자의 문제 인식과 주장을 파악하고, 주요 내용을 요약하라.
        작성해야 하는 포맷은 다음과 같다.
        
        # 제목
        ## 저자의 문제 인식 및 주장 (15문장 이내)
        
        ## 저자 소개
        
        ==============이하 텍스트 ================
        {text}
        '''
        
        print(system_prompt)
        print('=========================================')
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[{
                "role": "system",
                "content": system_prompt
            }]
        )
        
        return response.choices[0].message.content

def summarize_pdf(file_path: str, output_file_path: str):
    txt_file_path = pdf_to_txt(file_path)
    summary = summarize_txt(txt_file_path)
    
    with open(output_file_path, "w", encoding="utf-8") as summary_file:
        summary_file.write(summary)


if __name__ == "__main__":
    file_path = "chap04/data/생성형 AI 시대, AI 리터러시 교육의 방향.pdf"
    summary = summarize_pdf(file_path, "chap04/output/summary.txt")
