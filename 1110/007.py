import cv2
import numpy as np
import os

# 파일 경로 정의
runner_path = 'run.jpg'   # 인물 이미지 (검은색 배경)
road_path = 'runroad.jpg' # 배경 이미지 (도로)

# 1. 배경 이미지 (도로) 로드
road_image = cv2.imread(road_path, cv2.IMREAD_COLOR)

if road_image is None:
    raise FileNotFoundError(f"Error: Background image '{road_path}' not found.")

# 2. 전경 이미지 (달리는 사람) 로드
runner_image = cv2.imread(runner_path, cv2.IMREAD_COLOR)

if runner_image is None:
    raise FileNotFoundError(f"Error: Foreground image '{runner_path}' not found.")

# --- 크기 조정 (배경 이미지 크기에 맞춰 전경 이미지 조정) ---
target_width = road_image.shape[1]
target_height = road_image.shape[0]

# runner_image의 크기를 road_image와 동일하게 조정
runner_image_resized = cv2.resize(runner_image, (target_width, target_height))

# --- 핵심 수정 부분: 검은색 배경을 투명으로 간주하고 합성 ---

# 3. runner_image_resized에서 검은색 픽셀을 제외한 마스크 생성
# 검은색 픽셀 (BGR: [0,0,0])을 배경으로 간주합니다.
# 픽셀 값이 [0,0,0]이 아닌 모든 픽셀을 흰색(255)으로 설정하여 마스크를 만듭니다.
# B, G, R 채널 중 하나라도 0이 아니면 마스크에 포함
mask = cv2.inRange(runner_image_resized, np.array([1,1,1]), np.array([255,255,255]))
# 또는 더 간단하게:
# gray_runner = cv2.cvtColor(runner_image_resized, cv2.COLOR_BGR2GRAY)
# _, mask = cv2.threshold(gray_runner, 1, 255, cv2.THRESH_BINARY)


# 4. 마스크 반전 (인물이 검은색이고 배경이 흰색인 마스크)
mask_inv = cv2.bitwise_not(mask)

# 5. 배경 이미지에서 인물이 들어갈 자리를 검은색으로 비웁니다.
# (배경 이미지의 해당 부분은 검은색이 되고, 나머지 배경은 그대로 남습니다)
background_area = cv2.bitwise_and(road_image, road_image, mask=mask_inv)

# 6. 인물 이미지에서 검은색 배경을 제외한 인물 부분만 추출합니다.
# (인물 부분만 남고, 검은색 배경은 제거됩니다)
foreground_person = cv2.bitwise_and(runner_image_resized, runner_image_resized, mask=mask)

# 7. 배경과 인물 부분을 더하여 최종 이미지 생성
final_composited_image = cv2.add(background_area, foreground_person)

# 결과 출력
cv2.imshow('1. Original Runner Image (Resized)', runner_image_resized)
cv2.imshow('2. Person Mask (Non-Black)', mask)
cv2.imshow('3. Road Background with Hole', background_area)
cv2.imshow('4. Final Composited Image', final_composited_image)
cv2.waitKey(0)
cv2.destroyAllWindows()