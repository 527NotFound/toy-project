import Levenshtein
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import requests
import json
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import os
import platform

# --- 1. Matplotlib 한글 폰트 설정 ---
# NanumGothic 폰트를 스크립트 폴더에 다운로드하고 설정합니다.
def setup_korean_font():
    """
    Matplotlib에서 한글을 표시하기 위해 NanumGothic 폰트를 다운로드하고 설정합니다.
    """
    font_name = 'NanumGothic.ttf'
    font_url = 'https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf'

    if not os.path.exists(font_name):
        print(f"'{font_name}' 폰트 파일이 없어 다운로드를 시작합니다...")
        try:
            response = requests.get(font_url)
            response.raise_for_status()  # 오류가 있으면 예외 발생
            with open(font_name, 'wb') as f:
                f.write(response.content)
            print("폰트 다운로드 완료.")
        except requests.exceptions.RequestException as e:
            print(f"폰트 다운로드 실패: {e}")
            print("수동으로 'NanumGothic.ttf' 파일을 스크립트 폴더에 넣어주세요.")
            return

    # 폰트 매니저에 폰트 추가
    try:
        font_path = os.path.abspath(font_name)
        fm.fontManager.addfont(font_path)
        
        # Matplotlib 설정에 폰트 적용
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 부호 깨짐 방지
        print(f"한글 폰트 '{font_prop.get_name()}' 설정이 완료되었습니다.")
    except Exception as e:
        print(f"폰트 설정 중 오류 발생: {e}")
        print("그래프의 한글이 깨질 수 있습니다.")

# --- 2. Tesseract 경로 설정 (macOS) ---
# Homebrew로 설치한 Tesseract 경로를 지정합니다.
if platform.system() == 'Darwin':  # 'Darwin'은 macOS를 의미합니다.
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
    print("macOS Homebrew Tesseract 경로가 설정되었습니다.")


# --- 3. OCR 함수들 ---

# 01.py: Pytesseract로 이미지 OCR
def ocr_pytesseract(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='kor')
        return text
    except FileNotFoundError:
        return f"오류: {image_path} 파일을 찾을 수 없습니다."
    except pytesseract.TesseractNotFoundError:
        return "오류: Tesseract 실행 파일을 찾을 수 없습니다. Tesseract가 설치 및 PATH에 등록되었는지 확인하세요."

# 02.py: OCR.space API로 이미지 OCR
def ocr_space_api(image_path, api_key='K81202886688957', language='kor'):
    url_api = "https://api.ocr.space/parse/image"
    try:
        with open(image_path, 'rb') as f:
            response = requests.post(
                url_api,
                files={"filename": (os.path.basename(image_path), f, 'image/jpeg')},
                data={"apikey": api_key, "language": language},
                timeout=30
            )
        response.raise_for_status()
        result = response.json()
        
        if result.get("IsErroredOnProcessing"):
            return f"OCR.space API 오류: {result.get('ErrorMessage')}"
        
        parsed = result.get("ParsedResults")
        if parsed and len(parsed) > 0:
            text_detected = parsed[0].get("ParsedText", "")
            return text_detected
        else:
            return "OCR.space API에서 텍스트를 찾지 못했습니다."
            
    except FileNotFoundError:
        return f"오류: {image_path} 파일을 찾을 수 없습니다."
    except requests.exceptions.RequestException as e:
        return f"API 요청 오류: {e}"

# 03.py: PyMuPDF와 Pytesseract로 PDF OCR
def ocr_pdf_extract(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except FileNotFoundError:
        return f"오류: {pdf_path} 파일을 찾을 수 없습니다."
    except Exception as e:
        if "cannot open" in str(e):
             return f"오류: {pdf_path} 파일을 열 수 없습니다. 파일이 손상되었거나 PDF가 아닐 수 있습니다."
        raise e
        
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 1. 텍스트 레이어에서 텍스트 추출
        text = page.get_text()
        if text:
            full_text += f"[페이지 {page_num+1} 텍스트]\n{text}\n"

        # 2. 페이지 내 이미지 추출 및 OCR
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                img_pil = Image.open(io.BytesIO(image_bytes))
                
                # OCR 수행
                img_text = pytesseract.image_to_string(img_pil, lang='kor')
                if img_text.strip():
                    full_text += f"[페이지 {page_num+1}, 이미지 {img_index+1} 내 텍스트]\n{img_text}\n"
            except Exception as e:
                print(f"PDF 내 이미지 처리 중 오류 (페이지 {page_num+1}, 이미지 {img_index+1}): {e}")
                
    doc.close()
    return full_text

# --- 4. 정확도 계산 함수 ---
# 코드 1: Levenshtein 거리로 정확도 계산
def calculate_accuracy(original_text, ocr_text):
    """
    Levenshtein 거리를 사용하여 두 텍스트 간의 유사도(인식률)를 계산합니다.
    """
    # 전처리: 공백, 줄바꿈 정규화 (비교를 더 공정하게 만듦)
    original_clean = ' '.join(original_text.split())
    ocr_clean = ' '.join(ocr_text.split())

    if not original_clean and not ocr_clean:
        return 100.0  # 둘 다 비어있으면 100% 일치
        
    max_len = max(len(original_clean), len(ocr_clean))
    if max_len == 0:
        return 100.0 # 원문이 비어있는 경우 (드문 케이스)
        
    distance = Levenshtein.distance(original_clean, ocr_clean)
    accuracy = (1 - distance / max_len) * 100
    return accuracy

# --- 5. 메인 실행 로직 ---
def main():
    # --- !!! [필수] 정답 텍스트를 여기에 입력하세요 !!! ---
    
    # 'ocr/01.jpg' 이미지의 실제(정답) 텍스트
    GROUND_TRUTH_JPG = """2016학년도 연세대 논술- 인문계열
[문제 1] 예술적 성취에 대한 제시문 (가), (나), (다)의 논지를 비교, 분석하시오. (1000자 안팎, 50점)
[문제 2] 제시문 (라)를 바탕으로 제시문 (가), (나), (다)의 논지를 평가하시오. (1000자 안팎, 50점)
2016학년도 연세대 논술 -사회계열
[문제 1] 제시문 (가), (나), (다)는 '진정성 있는 사람'에 대한 서로 다른 관점을 보여준다.
이 세 가지 관점의 차이를 설명하시오. (1,000자 안팎, 50점)
[문제 2] 제시문 (라)의 <그림 1>과 <그림 2>에 나타난 특징들을 분석하고, 이를 제시문 (가)와 (나)에 근거하여 해석하시오 (1,000자 안팎, 50점)
2016학년도 서울시립대 논술
[문항 1] 제시문 (가)의 주장을 250자 내외로 요약한 뒤, 주된 견해나 관점이 [가]와 다른 제시문을 [나]~[라]에서
모두 찾아 [가] 와 각각 어떻게 차이가 나는지 구체적으로 밝히시오. (600자 내외, 배점 30점)
[문항2] <그림 1>과 <그림 2>를 근거로 마리엘리토의 유입이 마이애미 노동시장에 미친 영향을 추론하시오.
단, 그러한 추론을 위해 필요한 가정 (들)을 반드시 포함하여 서술하시오. (400자 내외, 배점 20점)
[문항 3]<보기>에 나타난 A씨의 태도에 찬성하는지 혹은 반대하는지 어느 한 입장을 정한 뒤, [가]~[라]의 모든 제시문을 활용하되 주된 견해나 관점이 자신의 입장과 같은 제시문의 논거는 지지하고 자신의 입장과 다른 제시문의 논거는 비판하면 서 자신의 입장을 옹호하시오. (1,000자 내외, 배점 50점)
2016학년도 동국대 논술
[문제 1] 제시문 [가]와 [나]를 참고로 하여, '남녀 대화의 대표적 특성'을 변화시킬 수 있는 요인에 대해 서술하시오. 11~12줄 (330~360자) [30점]
[문제 2] 제시문 [가]와 [나]의 핵심어를 찾아 맥락상의 공통적인 주장을 기술하시오. 8~9줄 (240~270자) (30점)
[문제 3] 제시문 [다], [라], [마], [바]를 시대 순에 따라 배열하여 민주주의의 발전 과정을 요약하시오
그리고 제시문 [라]를 참고하여 시민운동의 구체적인 사례를 제시하고
그것이 민주주의 발전에 끼친 긍정적 영향에 대해 기술하시오. 22~23줄 (660~690자) [40점]
2016학년도 홍익대 논술
[문제 1] 제시문 (가)에서 문자 문화의 특성을 찾아 요약하고, 이를 바탕으로 (나), (다), (라)에 나타난 독서 경험이나 책에 대한 태도를 분석하여 논술하시오. (800±100자)
[문과대학, 사범대학 및 예술학과 지원자에게는 타 문제의 2배의 배점]
[문제 2] 제시문 (마)와 (바)의 주요 개념이 (사), (아), (자)에 각각 어떻게 적용될 수 있는지 논술하시오. (800±100자) [경영대학, 경제학부 및 법학부 지원자에게는 타 문제의 2배의 배점]
2016학년도 경기대 논술
[문항 1] 나의 ᄀ에 대한 문제 해결책으로서 가 작품에 대해 설명하고, 그것의 한계를 다를 통해 논술하시오. (700±50자)
[문항 2] 가의 쓰레기 종량제가 사회 제도로서 가지는 의의를 나의 관점에서 설명하고,
이 제도가 이전의 제도에 비해 효과적이었던 까닭을 다에 제시된 소비의 특성을 활용하여 논술하시오. (700±50자)"""
    
    # 'ocr/sample.pdf' PDF의 실제(정답) 텍스트 (텍스트 레이어 + 이미지 내 텍스트 모두 포함)
    GROUND_TRUTH_PDF = """Pdf 파일샘플
Pdf 파일샘플입니다.
제목
• 내용"""

    # ---------------------------------------------------
    
    # 파일 경로
    image_file = 'ocr/01.jpg'
    pdf_file = 'ocr/sample.pdf'

    # 파일 존재 여부 확인
    if not os.path.exists(image_file) or not os.path.exists(pdf_file):
        print(f"오류: '{image_file}' 또는 '{pdf_file}' 파일을 찾을 수 없습니다.")
        print("스크립트와 동일한 폴더에 'ocr' 폴더를 만들고 파일을 넣어주세요.")
        return

    # 정답 텍스트 입력 확인
    if "여기에" in GROUND_TRUTH_JPG or "여기에" in GROUND_TRUTH_PDF:
        print("="*50)
        print("!! 경고 !!")
        print("스크립트 상단의 'GROUND_TRUTH_JPG'와 'GROUND_TRUTH_PDF' 변수에")
        print("정확한 원본(정답) 텍스트를 입력해야 인식률이 올바르게 계산됩니다.")
        print("현재 정답 텍스트가 입력되지 않아, 인식률이 0%에 가깝게 나올 수 있습니다.")
        print("="*50)

    # 1. OCR 실행
    print("OCR 1 (Pytesseract on JPG) 실행 중...")
    text_01 = ocr_pytesseract(image_file)
    
    print("OCR 2 (OCR.space API on JPG) 실행 중...")
    text_02 = ocr_space_api(image_file)
    
    print("OCR 3 (PyMuPDF + Pytesseract on PDF) 실행 중...")
    text_03 = ocr_pdf_extract(pdf_file)

    # 2. 정확도 계산
    print("정확도 계산 중...")
    acc_01 = calculate_accuracy(GROUND_TRUTH_JPG, text_01)
    acc_02 = calculate_accuracy(GROUND_TRUTH_JPG, text_02)
    acc_03 = calculate_accuracy(GROUND_TRUTH_PDF, text_03)

    print("\n--- 텍스트 추출 결과 요약 ---")
    print(f"[Pytesseract (JPG)]:\n{text_01[:100]}...\n")
    print(f"[OCR.space (JPG)]:\n{text_02[:100]}...\n")
    print(f"[PyMuPDF+Pytesseract (PDF)]:\n{text_03[:100]}...\n")

    print("--- 인식률 결과 ---")
    print(f"Pytesseract (JPG) 인식률: {acc_01:.2f}%")
    print(f"OCR.space (JPG) 인식률: {acc_02:.2f}%")
    print(f"PyMuPDF+Pytesseract (PDF) 인식률: {acc_03:.2f}%")

    # 3. 그래프 그리기
    print("그래프 생성 중...")
    setup_korean_font() # 한글 폰트 설정
    
    ocr_methods = ['Pytesseract (JPG)', 'OCR.space (JPG)', 'PyMuPDF+Pytesseract (PDF)']
    accuracies = [acc_01, acc_02, acc_03]
    colors = ['#1f77b4', '#2ca02c', '#d62728'] # 파랑, 초록, 빨강

    plt.figure(figsize=(12, 7))
    bars = plt.bar(ocr_methods, accuracies, color=colors)
    
    # 막대 그래프 위에 정확한 수치(%) 표시
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1.0, f'{yval:.2f}%', 
                 ha='center', va='bottom', fontsize=11)

    plt.title("OCR 방법별 한글 인식률 비교", fontsize=16)
    plt.xlabel("OCR 방법 및 대상 파일", fontsize=12)
    plt.ylabel("인식률 (Accuracy, %)", fontsize=12)
    plt.ylim(0, 105) # 100% 위에 텍스트가 보이도록 105%까지 표시
    
    # 참고: JPG와 PDF는 서로 다른 원본임을 알림
    plt.figtext(0.5, 0.01, 
                "참고: 'JPG'와 'PDF'는 서로 다른 원본 파일을 사용하므로 직접적인 성능 비교에 유의해야 합니다.", 
                ha="center", fontsize=9, style='italic', color='gray')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # figtext와 겹치지 않게 레이아웃 조정
    
    # 그래프를 'ocr_comparison_chart.png' 파일로 저장
    plt.savefig('ocr_comparison_chart.png')
    print("그래프가 'ocr_comparison_chart.png' 파일로 저장되었습니다.")
    
    # 그래프를 화면에 표시
    plt.show()


if __name__ == "__main__":
    main()