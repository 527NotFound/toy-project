import cv2
import numpy as np

# 1. 이미지 로드
# 주의: 이 코드를 실행하려면 'do.jpg' 파일이 스크립트와 같은 디렉토리에 있어야 합니다.
image = cv2.imread('do.jpg')

# 이미지가 제대로 로드되었는지 확인
if image is None:
    print("Error: Image not loaded. Check file path.")
    # 실제 환경에서는 예외 처리 후 종료
    # exit() 

# 2. BGR 이미지를 HSV로 변환
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 3. 갈색/어두운 배경색 범위 정의 (HSV)
# 배경과 도라야끼는 주로 채도(S)와 명도(V)가 낮은 어두운 갈색/붉은 갈색 계열입니다.
# OpenCV의 H(Hue) 범위는 0-179입니다.

# 첫 번째 갈색 범위 (주로 도라야끼와 일반적인 갈색)
# H: 0~25 (빨강~주황 계열), S: 30~255 (어느 정도의 채도), V: 20~255 (어두운/밝은 명도)
lower_brown1 = np.array([0, 30, 20])
upper_brown1 = np.array([25, 255, 255])

# 두 번째 갈색 범위 (어두운 배경 부분/짙은 갈색)
# H: 160~179 (붉은 계열의 어두운 갈색), S: 50~255, V: 20~255
# 이 범위는 H 값이 180을 넘어가는 빨간색 계열의 낮은 범위(0 근처)를 포함하기 위해 설정합니다.
lower_brown2 = np.array([160, 50, 20])
upper_brown2 = np.array([179, 255, 255])

# 4. 마스크 생성 (두 가지 갈색 범위를 OR 연산으로 합침)
mask_brown1 = cv2.inRange(hsv_image, lower_brown1, upper_brown1)
mask_brown2 = cv2.inRange(hsv_image, lower_brown2, upper_brown2)

# 두 마스크를 합쳐서 전체 갈색/배경 마스크를 만듭니다.
mask_background = cv2.bitwise_or(mask_brown1, mask_brown2)

# 5. 원본 이미지에 마스크 적용 (갈색 영역만 남김)
result_background = cv2.bitwise_and(image, image, mask=mask_background)

# 6. 갈색이 아닌 객체 분할 (도라에몽, 눈, 입 등)
# 마스크 반전: 갈색 영역 외의 모든 영역 (도라에몽)
mask_foreground = cv2.bitwise_not(mask_background)
result_foreground = cv2.bitwise_and(image, image, mask=mask_foreground)

# 7. 추가 분석을 위한 전경 객체(도라에몽) 흑백 처리
result_foreground_gray = cv2.cvtColor(result_foreground, cv2.COLOR_BGR2GRAY)

# 8. 결과 이미지 표시
cv2.imshow('1. Original Image', image)
cv2.imshow('2. Background Mask (Brown/Dark)', mask_background)
cv2.imshow('3. Segmented Background Object (Brown)', result_background)
cv2.imshow('4. Segmented Foreground Object (Non-Brown)', result_foreground)
cv2.imshow('5. Foreground Object (Grayscale)', result_foreground_gray)

cv2.waitKey(0)
cv2.destroyAllWindows()