Rails.application.routes.draw do
  # CRUD 라우트를 자동으로 생성
  resources :menu_entries, only: [:new, :create, :show]

  # 웹앱의 시작 페이지를 MenuEntriesController의 new 액션으로 설정
  root "menu_entries#new"
end