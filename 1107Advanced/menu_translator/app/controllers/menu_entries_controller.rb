class MenuEntriesController < ApplicationController
  # 새 메뉴 항목 생성 폼 (루트 경로)
  def new
    @menu_entry = MenuEntry.new
  end

  # 폼 제출 처리 (이미지 업로드 및 OCR/번역 실행)
  def create
    @menu_entry = MenuEntry.new(menu_entry_params)

    if @menu_entry.save
      # --- 핵심 로직: MenuTranslatorService 호출 ---
      # MenuTranslatorService를 인스턴스화하고 call 메서드를 호출하여 OCR 및 번역을 수행합니다.
      # 이 메서드는 MenuEntry 객체를 업데이트합니다.
      MenuTranslatorService.new(@menu_entry).call
      # --------------------------------------------------------------------

      redirect_to @menu_entry, notice: '메뉴판 업로드 및 번역이 완료되었습니다.'
    else
      # 이미지 파일 첨부가 없을 경우 등 오류 처리
      flash.now[:alert] = "이미지 업로드에 실패했습니다."
      render :new
    end
  end

  # 번역 결과 보기 페이지
  def show
    @menu_entry = MenuEntry.find(params[:id])
  end

  private

  def menu_entry_params
    # 이미지 파일 첨부를 허용
    params.require(:menu_entry).permit(:image)
  end
end