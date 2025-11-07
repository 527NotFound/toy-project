# app.py

from flask import Flask, request, redirect, url_for, session, render_template
from flask_mysqldb import MySQL 
from flask_bcrypt import Bcrypt  
import MySQLdb.cursors
import os

# 파일 업로드 관련 설정
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
# 실제 운영에서는 더 복잡하고 안전한 키를 사용해야 합니다.
app.secret_key = 'your_secret_key' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# uploads 폴더 생성 (없다면)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 💡 MySQL 데이터베이스 연결 설정 (사용자 환경에 맞게 변경)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'         
app.config['MYSQL_PASSWORD'] = 'doochul'  # 🔑 성공적으로 설정된 비밀번호
app.config['MYSQL_DB'] = 'ocr_users_db'
app.config['MYSQL_CHARSET'] = 'utf8mb4'

app.config['MYSQL_OPTS'] = {
    'auth_plugin': 'caching_sha2_password' # 🚨 이 설정이 핵심
}

# MySQL 및 Bcrypt 객체 초기화
mysql = MySQL(app)
bcrypt = Bcrypt(app) 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## --- 라우트 --- ##

@app.route('/')
def index():
    """앱 시작 시, 터치 대기 화면 렌더링"""
    background_image = url_for('static', filename='login_background.jpg')
    login_url = url_for('home') 
    
    return render_template('index.html', background_image=background_image, login_url=login_url)

@app.route('/home')
def home():
    """실제 로그인 상태 확인 및 리다이렉트 처리"""
    if 'username' in session:
        # 로그인 상태면 OCR 서비스 페이지로 리다이렉트
        return redirect(url_for('ocr_service'))
    else:
        # 로그인 상태가 아니면 로그인 페이지로 리다이렉트
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # 사용자 정보 조회
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        # Bcrypt를 사용한 비밀번호 해시 비교
        if account and bcrypt.check_password_hash(account['password'], password):
            session['username'] = account['username']
            print(f"{username} 로그인 성공 (bcrypt 인증)")
            return redirect(url_for('ocr_service')) 
        else:
            error = "아이디 또는 비밀번호가 틀렸습니다."
            # 로그인 실패 시 에러 메시지와 함께 폼을 다시 렌더링
            background_image = url_for('static', filename='login_background.jpg')
            return render_template('login.html', error=error, background_image=background_image)
            
    # GET 요청 시 로그인 폼 제공
    background_image = url_for('static', filename='login_background.jpg')
    return render_template('login.html', background_image=background_image)

@app.route('/logout')
def logout():
    username = session.pop('username', None)
    print(f"{username} 로그아웃")
    return redirect(url_for('login'))

@app.route('/ocr_service', methods=['GET'])
def ocr_service():
    """로그인된 사용자만 접근 가능한 OCR 서비스 페이지"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # OCR 서비스 페이지에 배경 이미지 전달
    background_image = url_for('static', filename='ocr_background.jpg')
    return render_template('ocr_service.html', 
                           username=session['username'],
                           background_image=background_image)

if __name__ == '__main__':
    app.run(debug=True)