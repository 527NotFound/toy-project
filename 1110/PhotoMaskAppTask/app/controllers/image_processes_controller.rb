# app/controllers/image_processes_controller.rb

require 'tempfile'
require 'open3' # 이미지는 show 액션에서 처리하거나 별도 Worker에서 처리 가능

class ImageProcessesController < ApplicationController
  
  # A. 목록 페이지 (Index) 구현
  def index
    # 모든 처리 요청 목록을 최신 순으로 가져옵니다.
    @image_results = ImageResult.with_attached_original_image.order(created_at: :desc)
    @image_result = ImageResult.new # 업로드 폼에 사용하기 위해 새 객체 전달
  end

  def new
    # new는 index 페이지의 폼을 사용하므로 이제 필요하지 않을 수 있지만, 유지합니다.
    @image_result = ImageResult.new
  end

  # B. 업로드 (Create) 로직 수정
  def create
    @image_result = ImageResult.new(image_result_params)
    
    # 1. 파일 업로드 후 상태를 'pending' (처리 대기)로 설정하고 DB에 저장만 합니다.
    @image_result.status = :pending 

    if @image_result.save
      flash[:notice] = "파일이 성공적으로 업로드되었으며, 처리 대기 중입니다."
      
      # 여기서 Python 스크립트 실행 로직을 제거하고,
      # 나중에 사용자가 show 페이지에 접근했을 때 처리하도록 하거나, 
      # 별도 백그라운드 워커에서 처리하도록 설정할 수 있습니다.
      
      # 여기서는 index 페이지로 리디렉션하여 목록에서 확인하도록 합니다.
      redirect_to root_path 
    else
      # 파일이 첨부되지 않았을 때 등
      @image_results = ImageResult.with_attached_original_image.order(created_at: :desc)
      flash.now[:alert] = "파일 업로드에 실패했습니다."
      render :index # index 뷰에서 오류 메시지를 보여줍니다.
    end
  end
  
  # C. 결과 확인 (Show) 및 처리 (선택 사항)
  def show
    @image_result = ImageResult.find(params[:id])
    
    # 만약 'pending' 상태라면, 접근 시에 바로 처리를 시도합니다. (가장 간단한 방법)
    if @image_result.pending?
      process_image_on_demand(@image_result)
    end
  end

  # D. Private 메서드: 파일 처리 로직 (별도 함수로 분리)
  private
  
  def image_result_params
    params.require(:image_result).permit(:original_image)
  end
  
  def process_image_on_demand(image_result)
    # 이미 처리된 이미지 파일이 존재하면 재처리하지 않습니다.
    if image_result.processed_image_path.present? && File.exist?(Rails.root.join('public', image_result.processed_image_path.delete_prefix('/')))
      image_result.update(status: :success)
      return
    end
    
    # (이전 Controller 가이드에서 사용했던 Python 스크립트 실행 로직을 여기에 넣습니다)
    original_file = image_result.original_image
    relative_output_path = "processed_images/#{image_result.id}_processed.png"
    absolute_output_path = Rails.root.join('public', relative_output_path)
    
    original_file.blob.open do |tempfile|
        python_env = Rails.root.join('image_processor', 'venv', 'bin', 'python')
        python_script = Rails.root.join('image_processor', 'process.py')
        command = "#{python_env} #{python_script} #{tempfile.path} #{absolute_output_path}"
        
        stdout, stderr, status = Open3.capture3(command)
        
        if status.success? && File.exist?(absolute_output_path)
          image_result.update(
            original_filename: original_file.filename.to_s,
            processed_image_path: "/#{relative_output_path}",
            status: :success
          )
        else
          error_message = stderr.presence || "Python script failed."
          image_result.update(status: :failed, description: error_message.truncate(255))
        end
    end
  end
end