from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import time

# 🛠️ OCR 관련 라이브러리 추가
import pytesseract
from PIL import Image

app = Flask(__name__)

# Tesseract 설치 경로 설정 (Windows 사용자만 해당. macOS/Linux는 보통 생략 가능)
# 예시: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

UPLOAD_FOLDER = 'static/uploads' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    uploaded_image_url = None
    extracted_text = None  # 💡 OCR 결과를 저장할 변수

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url) 
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            timestamp = int(time.time())
            filename = f"{timestamp}_{original_filename}"
            
            # 파일 저장 경로
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # 🖼️ OCR 핵심 로직
            try:
                # 1. Pillow를 사용하여 저장된 이미지 파일을 엽니다.
                img = Image.open(file_path)
                config = r'--oem 3 --psm 6'
                # 2. pytesseract를 사용하여 이미지에서 텍스트를 추출합니다.
                # 한국어 OCR이 필요한 경우: pytesseract.image_to_string(img, lang='kor')
                extracted_text = pytesseract.image_to_string(img, lang='kor+eng', config=config)
                
            except Exception as e:
                # Tesseract 경로 설정 오류나 기타 OCR 오류 발생 시
                extracted_text = f"OCR 처리 중 오류 발생: {e}"
            
            # 저장된 파일의 URL 생성
            uploaded_image_url = url_for('static', filename=f'uploads/{filename}')
            
            # OCR 결과와 이미지 URL을 템플릿에 전달
            return render_template('upload.html', 
                                   image_url=uploaded_image_url, 
                                   ocr_result=extracted_text)
    
    # GET 요청 시
    return render_template('upload.html', image_url=uploaded_image_url, ocr_result=extracted_text)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)