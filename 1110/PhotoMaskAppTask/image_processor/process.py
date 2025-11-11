import sys
import cv2
import numpy as np
import os

def blackout_skin_color(input_path, output_path):
    # 1. 이미지 로드
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Could not read image from {input_path}", file=sys.stderr)
        return False

    # 2. BGR 이미지를 HSV로 변환
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 3. 피부색 범위 정의 (HSV)
    # 일반적인 인간의 피부색 범위 (다양한 조명과 인종에 따라 조정이 필요할 수 있습니다.)
    # H (Hue): 색상, S (Saturation): 채도, V (Value): 명도
    # 낮은 범위 (어두운 피부색)
    lower_skin = np.array([0, 48, 80], dtype=np.uint8) 
    # 높은 범위 (밝은 피부색)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8) 

    # 4. HSV 이미지에서 피부색 범위에 해당하는 픽셀만 추출하여 마스크 생성
    # 마스크는 피부색 영역만 흰색(255)으로 표시합니다.
    mask = cv2.inRange(hsv_image, lower_skin, upper_skin)

    # 5. 원본 이미지의 피부색 영역을 검은색으로 덮어쓰기
    # OpenCV에서는 마스크가 흰색(255)인 영역만 bitwise_and 등으로 처리하지만,
    # 여기서는 마스크를 이용해 직접 픽셀 값을 변경합니다.
    
    # 피부색 영역의 픽셀 위치를 가져옵니다.
    # mask > 0 인 곳이 피부색 영역입니다.
    img[mask > 0] = [0, 0, 0] # BGR 순서로 [검은색, 검은색, 검은색]

    # 6. 결과 이미지 저장
    success = cv2.imwrite(output_path, img)

    if not success:
        print(f"Error: Could not write image to {output_path}", file=sys.stderr)
        return False

    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process.py <input_path> <output_path>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if blackout_skin_color(input_file, output_file):
        sys.exit(0)
    else:
        sys.exit(1)