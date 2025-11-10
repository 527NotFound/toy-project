# HSV를 활용한 파란색 객체 분할
import cv2
import numpy as np

# 1. 이미지 로드
image = cv2.imread('tomas_train.jpg')

# 2. BGR 이미지를 HSV로 변환
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 3. 흰색 범위 정의 (HSV)
lower_white = np.array([0, 0, 200])    # H: 0~179 (전체), S: 0 (매우 낮음), V: 200 (높음)
upper_white = np.array([179, 30, 255]) # S: 30 (낮음), V: 255 (최대)

# 4. HSV 이미지에서 흰색 범위에 해당하는 픽셀만 추출하여 마스크 생성
mask = cv2.inRange(hsv_image, lower_white, upper_white)

# 5. 원본 이미지에 마스크 적용 (흰색 영역만 남김)
result = cv2.bitwise_and(image, image, mask=mask)

mask_inv = cv2.bitwise_not(mask)

result2 = cv2.bitwise_and(image, image, mask=mask_inv)

result3 = cv2.cvtColor(result2, cv2.COLOR_BGR2GRAY)

# 6. 결과 이미지 표시
cv2.imshow('Original Image', image)
cv2.imshow('Blue Mask', mask)
cv2.imshow('Segmented Blue Object', result)
cv2.imshow('Non-Blue Object', result2)
cv2.waitKey(0)
cv2.destroyAllWindows()