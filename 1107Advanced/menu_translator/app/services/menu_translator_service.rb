# Tesseract OCR과 DeepL API를 통합하여 OCR 및 번역을 수행하는 서비스 객체

require 'rtesseract'
require 'faraday'
require 'json'
require 'dotenv/load' # .env 파일의 환경 변수를 로드

class MenuTranslatorService
  # DeepL API Free 엔드포인트
  DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"

  def initialize(menu_entry)
    @menu_entry = menu_entry
    # Active Storage의 첨부 파일 객체
    # 이미지 파일 자체에 접근하기 위해 key를 통해 경로를 얻을 예정
    @image_blob = menu_entry.image.blob 
  end

  # 메인 실행 메서드
  def call
    # 1. OCR을 통해 텍스트 추출
    original_text = perform_ocr
    
    # 2. 텍스트를 DeepL API로 번역
    translated_text = perform_translation(original_text)
    
    # 3. 모델에 결과 저장
    @menu_entry.update(
      original_text: original_text,
      translated_text: translated_text
    )
    
    # 성공 여부 반환 (여기서는 모델 저장이 성공했는지 확인)
    @menu_entry.persisted?
  end

  private

  # Tesseract OCR을 사용하여 텍스트 추출 로직
  def perform_ocr
    # Active Storage의 Blob 서비스에서 실제 파일 경로를 가져옵니다.
    image_path = ActiveStorage::Blob.service.path_for(@image_blob.key)
    
    # Tesseract에 이미지 파일 경로 전달 및 한국어(kor)로 인식 설정
    # OCR 결과가 없는 경우 빈 문자열 반환을 대비하여 strip 호출
    text = RTesseract.new(image_path, lang: "kor", psm: 6).to_s.strip
    
    # OCR 결과가 없는 경우 처리
    text.empty? ? "OCR 결과 텍스트를 찾을 수 없습니다." : text
  rescue RTesseract::ConversionError => e
    # Tesseract 실행 중 시스템 오류 발생 시 로깅
    Rails.logger.error "Tesseract OCR 실패: #{e.message}"
    "OCR 처리 중 오류가 발생했습니다."
  end

  # DeepL API를 호출하여 텍스트 번역 로직
  def perform_translation(text)
    # OCR 결과가 이미 오류 메시지인 경우 번역 시도 불필요
    return text if text.include?("OCR") 

    response = Faraday.post(DEEPL_ENDPOINT) do |req|
      # 인증 헤더 설정
      req.headers['Authorization'] = "DeepL-Auth-Key #{ENV.fetch('DEEPL_API_KEY')}"
      
      # 파라미터 설정
      req.params['text'] = text
      req.params['source_lang'] = 'KO' # 한국어
      req.params['target_lang'] = 'EN' # 영어 (기본: 영어)
    end

    if response.success?
      data = JSON.parse(response.body)
      # DeepL 응답 구조에서 번역된 텍스트 추출
      data['translations'][0]['text']
    else
      # API 호출 실패 시 에러 로깅
      Rails.logger.error "DeepL API 호출 실패: 상태 코드 #{response.status}, 응답: #{response.body}"
      "번역 API 호출 중 오류 발생: 상태 코드 #{response.status}"
    end
  rescue Faraday::Error => e
    # 네트워크 통신 오류 처리
    Rails.logger.error "DeepL 통신 오류: #{e.message}"
    "DeepL API 통신 중 오류 발생"
  end
end