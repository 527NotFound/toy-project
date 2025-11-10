import cv2
import numpy as np
import os # 파일 존재 여부 확인을 위해 추가

def segment_largest_object(image_path):
    """
    이미지에서 가장 큰 윤곽선을 찾아 해당 객체를 분할하는 함수.
    """
    print(f"--- 윤곽선 기반 분할 시작: {image_path} ---")
    
    # 1. 이미지 로드
    image = cv2.imread(image_path)

    # 이미지가 제대로 로드되었는지 확인
    if image is None:
        if not os.path.exists(image_path):
            print(f"Error: Image file '{image_path}' not found in the current directory.")
        else:
            print(f"Error: Image file '{image_path}' could not be loaded. Check file permissions or integrity.")
        return

    # 2. 그레이스케일 변환
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 3. 이진화 (역이진 + Otsu): 배경은 검은색, 객체는 흰색이 되도록 시도
    # 토마스 기차의 경우, 배경이 흰색이므로 THRESH_BINARY_INV를 사용하면 객체가 흰색이 됩니다.
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # 

    # 4. 윤곽선 찾기 (외곽선만)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 5. 가장 큰 윤곽선 선택
        largest_contour = max(contours, key=cv2.contourArea)

        # 6. 빈 마스크 생성 (원본 이미지 크기, 단일 채널)
        mask = np.zeros(image.shape[:2], dtype=np.uint8)

        # 7. 가장 큰 윤곽선을 흰색(255)으로 마스크에 그림
        # thickness=-1 은 내부를 채우는 것을 의미합니다.
        cv2.drawContours(mask, [largest_contour], -1, 255, thickness=-1)

        # 8. 원본 이미지에 마스크 적용하여 객체만 추출
        segmented_object = cv2.bitwise_and(image, image, mask=mask)

        # 결과 출력
        cv2.imshow('Original Image', image)
        cv2.imshow('Thresholded Image (Otsu)', thresh)
        cv2.imshow('Mask (Largest Contour)', mask)
        cv2.imshow('Segmented Object (Contour)', segmented_object)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("윤곽선이 감지되지 않았습니다. 이진화 설정 확인이 필요합니다.")
        cv2.imshow('Original Image', image)
        cv2.imshow('Thresholded Image (Otsu)', thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# 토마스 기차 이미지 경로
tomas_image_path = 'tomas_train.jpg'

# 함수 실행
segment_largest_object(tomas_image_path)