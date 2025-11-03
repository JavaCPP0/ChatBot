"""
chap04/summary.py

이 파일은 PDF 파일을 텍스트로 변환한 뒤(헤더/푸터 제거),
OpenAI를 사용해 텍스트를 요약하는 간단한 스크립트입니다.

주요 흐름:
 1. `pdf_to_txt(pdf_path)` : PDF를 열어 페이지별 텍스트를 추출하고
     헤더/푸터를 제거한 뒤 단일 텍스트 파일로 저장합니다.
 2. `summarize_txt(txt_path)` : 텍스트 파일을 읽어 OpenAI에 요약을 요청합니다.
 3. `summarize_pdf(file_path, output_file_path)` : PDF(또는 TXT)를 받아 요약을 생성하고
     결과를 지정한 출력 파일에 씁니다.

환경/의존성:
 - OpenAI Python SDK (import OpenAI)
 - python-dotenv (환경변수 로드용, .env에 OPENAI_API_KEY 등)
 - PyMuPDF (pymupdf) : PDF 텍스트 추출

사용 예:
 1) .env에 `OPENAI_API_KEY=sk-...` 를 설정
 2) python chap04/summary.py (스크립트의 __main__ 블록에서 파일 경로 지정)

주의:
 - 이 스크립트는 간단한 처리만 하므로 대형 PDF(수천 페이지)는 메모리/요금 이슈가 발생할 수 있습니다.
 - OpenAI 모델 이름(`gpt-4o`)은 계정/권한에 따라 사용 불가할 수 있습니다.
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
import pymupdf

# .env 파일에서 OPENAI_API_KEY 등을 불러옵니다. (있으면 로드)
load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("OPENAI_API_KEY")

def pdf_to_txt(pdf_file_path: str):
    """
    PDF 파일을 읽어 텍스트로 변환하고, 변환된 텍스트를 로컬 텍스트 파일로 저장합니다.

    동작:
    - PyMuPDF(pymupdf)를 사용해 PDF를 연 뒤 페이지별로 텍스트를 추출합니다.
    - 각 페이지에서 상단(header)과 하단(footer) 영역을 잘라내고(숫자: 80px),
      중앙 본문 텍스트만 취합하여 `full_text`에 붙입니다.
    - 모든 페이지를 합친 텍스트를 `chap04/output/{pdf_filename}.txt` 로 저장합니다.

    입력:
    - pdf_file_path: 변환할 PDF 파일의 경로(문자열)

    출력/반환값:
    - 생성된 텍스트 파일의 경로 문자열을 반환합니다.

    주의사항/에지케이스:
    - 이 함수는 입력 파일 존재 검사를 하지 않습니다(호출자가 검사해야 함).
    - 헤더/푸터 높이(`header_height`, `footer_height`)는 단순 픽셀 값이며
      문서 레이아웃에 따라 조정이 필요할 수 있습니다.
    - 복잡한 레이아웃(다단, 표 등)은 올바르게 추출되지 않을 수 있습니다.
    """

    # PDF 파일 열기 (PyMuPDF의 문서 객체 반환)
    doc = pymupdf.open(pdf_file_path)

    # 문서에서 제거할 헤더/푸터의 높이(픽셀 단위) — 필요시 조정
    header_height = 80  # Height of the header to be removed
    footer_height = 80  # Height of the footer to be removed

    full_text = ""

    # 각 페이지를 순회하며 텍스트 추출
    for page in doc:
        # 페이지 전체 영역 정보(rect) — 좌표/너비/높이 접근에 사용
        rect = page.rect

        # (선택) 상단 헤더 영역의 텍스트를 가져옵니다. 현재는 사용하지 않지만
        # 필요하면 헤더를 따로 저장하거나 분석할 수 있습니다.
        header = page.get_text(clip=(0, 0, rect.width, header_height))

        # (선택) 하단 푸터 영역의 텍스트를 가져옵니다.
        footer = page.get_text(clip=(0, rect.height - footer_height, rect.width, rect.height))

        # 본문 텍스트만 추출 (헤더/푸터 영역을 제외한 영역)
        text = page.get_text(clip=(0, header_height, rect.width, rect.height - footer_height))

        # 페이지별로 구분선을 추가해 연결 — 필요에 따라 제거 가능
        full_text += text + "\n------------------------------------------------\n"

    # PDF 파일 이름(확장자 제외)을 기반으로 출력 텍스트 파일명 생성
    pdf_file_name = os.path.basename(pdf_file_path)
    pdf_file_name = os.path.splitext(os.path.basename(pdf_file_name))[0]

    txt_file_path = f"chap04/output/{pdf_file_name}.txt"

    # 추출한 전체 텍스트를 파일로 저장
    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(full_text)

    # 호출자에서 결과 텍스트 경로를 사용하도록 반환
    return txt_file_path




def summarize_txt(file_path: str):
    """
    주어진 텍스트 파일을 읽어 OpenAI에 요약을 요청하고, 응답 텍스트를 반환합니다.

    입력:
    - file_path: 요약할 텍스트 파일 경로

    반환값:
    - OpenAI가 생성한 요약 문자열

    구현 노트:
    - OpenAI 클라이언트를 인스턴스화할 때 `api_key`를 사용합니다.
    - 현재는 system 메시지로 전체 텍스트를 보내는 단순 방식입니다. 큰 텍스트는
      모델의 입력 한도를 초과할 수 있으므로 실제로는 분할(chunks) 처리가 필요합니다.
    """

    # OpenAI 클라이언트 생성 (환경변수에서 api_key를 읽어야 함)
    client = OpenAI(api_key=api_key)

    # 파일을 열어 전체 텍스트를 읽습니다.
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

        # 시스템 프롬프트: 요약의 형식과 요구사항을 모델에 설명
        system_prompt = f'''\
        너는 다음 글을 요약하는 봇이다. 아래 글을 읽고, 저자의 문제 인식과 주장을 파악하고, 주요 내용을 요약하라.
        작성해야 하는 포맷은 다음과 같다.

        # 제목
        ## 저자의 문제 인식 및 주장 (15문장 이내)

        ## 저자 소개

        ==============이하 텍스트 ================
        {text}
        '''

        # 디버그용: 콘솔에 보낼 프롬프트를 출력 (필요시 제거)
        print(system_prompt)
        print('=========================================')

        # OpenAI 호출: chat.completions.create 사용
        # - model: 실제 사용 가능한 모델로 교체 필요
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[{
                "role": "system",
                "content": system_prompt
            }]
        )

        # 응답에서 텍스트를 추출하여 반환
        return response.choices[0].message.content

def summarize_pdf(file_path: str, output_file_path: str):
    """
    PDF 파일(또는 이미 텍스트 파일)을 받아 요약을 생성하고, 결과를 출력 파일로 씁니다.

    동작:
    - `pdf_to_txt()`를 사용해 PDF를 텍스트로 변환하고,
    - `summarize_txt()`로 요약을 생성한 뒤 지정한 출력 파일에 저장합니다.

    입력:
    - file_path: 요약 대상 파일 경로 (현재 구현은 PDF를 예상)
    - output_file_path: 생성된 요약을 쓸 출력 파일 경로
    """

    # PDF -> TXT 변환
    txt_file_path = pdf_to_txt(file_path)
    # 변환된 텍스트 파일을 요약
    summary = summarize_txt(txt_file_path)

    # 요약 결과를 출력 파일에 저장
    with open(output_file_path, "w", encoding="utf-8") as summary_file:
        summary_file.write(summary)


if __name__ == "__main__":
    file_path = "chap04/data/생성형 AI 시대, AI 리터러시 교육의 방향.pdf"
    summary = summarize_pdf(file_path, "chap04/output/summary.txt")
