# app/models/image_result.rb

class ImageResult < ApplicationRecord
  # 사용자가 업로드한 원본 파일을 'original_image'라는 이름으로 첨부합니다.
  has_one_attached :original_image
  
  # status 컬럼에 대한 enum 설정 (이전에 진행됨)
  enum status: { pending: 0, success: 1, failed: 2 }

  # 원본 파일이 반드시 첨부되어야 함을 검증합니다.
  validates :original_image, presence: true
end