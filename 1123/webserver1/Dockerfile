# 베이스 이미지
FROM nginx:alpine

# 웹서버 루트 디렉토리에 index.html 복사
COPY index.html /usr/share/nginx/html/
COPY shinobu.jpeg /usr/share/nginx/html/

# 포트 노출 (Nginx 기본 포트)
EXPOSE 80

# Nginx 시작 (기본 CMD 사용)