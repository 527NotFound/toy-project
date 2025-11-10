import cv2
import numpy as np
from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
# 세션 관리를 위한 비밀 키 설정 (실제 배포 시에는 복잡하고 안전한 값 사용 필수)
app.secret_key = 'super_secret_key_for_captcha'

# 이미지 저장 경로 설정
UPLOAD_FOLDER = 'static/challenges'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- 이미지 처리 함수: 파란색 객체를 분할하고 마스크 이미지를 생성 ---
def segment_blue_object(image_path):
    """
    HSV를 활용하여 이미지에서 파란색 객체를 분할하고
    실루엣 마스크 및 합성된 이미지를 생성합니다.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 파란색 범위 정의 (첫 번째 코드를 참고)
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    # 파란색 마스크 생성 (실루엣 역할을 함)
    mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

    # 1. 분할된 파란색 객체 이미지 (Result)
    result_image = cv2.bitwise_and(image, image, mask=mask)
    
    # 2. 마스크 이미지 (실루엣) - 흑백
    # 3채널로 변환하여 저장
    mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # 파일명 설정 (고유성을 위해 세션 ID 등을 활용할 수 있지만, 여기서는 간단하게 처리)
    base_name = os.path.basename(image_path).split('.')[0]
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{base_name}_segmented.jpg')
    mask_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{base_name}_mask.jpg')

    cv2.imwrite(result_path, result_image)
    cv2.imwrite(mask_path, mask_colored)
    
    return result_path, mask_path, mask

@app.route('/')
def index():
    # 1. 도전 과제 이미지 (캐릭터와 배경이 합성된 원본)
    # 실제로는 여러 이미지를 랜덤으로 선택해야 합니다.
    challenge_image_name = 'bear.jpg' 
    challenge_image_path = challenge_image_name # 프로젝트 루트에 있다고 가정

    try:
        # 2. 이미지 처리 함수 호출 및 결과 경로 얻기
        result_path, mask_path, mask_data = segment_blue_object(challenge_image_path)
    except FileNotFoundError as e:
        return f"파일 오류: {e}", 500

    # 3. 마스크를 3x3 격자로 분할하여 정답 타일 인덱스 결정
    H, W = mask_data.shape
    tile_h, tile_w = H // 3, W // 3
    
    # 정답 타일 인덱스를 저장할 리스트 (0부터 8까지)
    correct_tiles = []
    
    for i in range(3):
        for j in range(3):
            tile_index = i * 3 + j
            # 각 타일 영역의 마스크 픽셀 합계를 계산
            tile_mask = mask_data[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w]
            # 파란색 영역(흰색 픽셀, 값=255)이 특정 임계값 이상이면 정답 타일로 간주
            if np.sum(tile_mask) > (tile_h * tile_w * 255 * 0.1): # 10% 이상이 파란색이면 정답
                correct_tiles.append(tile_index)

    # 4. 세션에 정답 저장 및 뷰 렌더링
    session['correct_tiles'] = correct_tiles
    session['challenge_image_name'] = challenge_image_name
    
    # 뷰에 전달할 이미지 경로 (Flask의 static 폴더 기준)
    static_result_path = os.path.join('challenges', os.path.basename(result_path))
    static_mask_path = os.path.join('challenges', os.path.basename(mask_path))

    return render_template('index.html', 
                           challenge_image=challenge_image_name, 
                           segmented_image=static_result_path,
                           silhouette_image=static_mask_path,
                           correct_tiles=correct_tiles) # 디버깅용으로 정답도 함께 전달

@app.route('/verify', methods=['POST'])
def verify():
    # 사용자가 선택한 타일 인덱스 목록
    # HTML 폼에서 'selected_tiles' 이름으로 여러 개의 값을 받습니다.
    user_selections = set(int(x) for x in request.form.getlist('selected_tiles'))
    
    # 세션에서 정답 가져오기
    correct_tiles = set(session.pop('correct_tiles', []))

    # 사용자의 선택이 정답과 정확히 일치하는지 확인
    is_robot = user_selections != correct_tiles
    
    if is_robot:
        message = "🤖 로봇으로 의심됩니다. 다시 시도해 주세요."
    else:
        message = "✅ 로봇이 아닙니다. 인증에 성공했습니다!"

    return render_template('result.html', message=message, 
                           user_selections=sorted(list(user_selections)), 
                           correct_tiles=sorted(list(correct_tiles)))

if __name__ == '__main__':
    app.run(debug=True)