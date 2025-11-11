# config/routes.rb

Rails.application.routes.draw do
  # index 액션 추가
  resources :image_processes, only: [:index, :new, :create, :show] 
  
  # 루트 페이지를 목록(index)으로 설정
  root 'image_processes#index' 
end