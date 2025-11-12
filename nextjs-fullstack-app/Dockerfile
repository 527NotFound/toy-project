# 1단계: Next.js 빌드 환경 (Builder Stage)
# 플랫폼 지정은 buildx 명령어에 맡기고, Dockerfile은 깨끗하게 유지
FROM node:20-alpine AS builder

WORKDIR /app
# Node.js 런타임이 포함된 이미지이므로 npm이 존재합니다.
COPY package.json package-lock.json* ./

# 프로덕션 의존성만 설치 (개발 의존성 설치 방지)
RUN npm install --production=false

# 모든 소스 파일 복사 (start.sh 포함)
COPY . .

# Next.js 애플리케이션 빌드
RUN npm run build


# 2단계: NGINX 및 프로덕션 환경 (Runner Stage)
# NGINX 이미지를 베이스로 사용
FROM nginx:alpine AS runner

# 필수: NGINX Alpine 이미지에 Node.js, npm, tini 설치
# tini는 프로세스 관리를 위해 필요합니다.
RUN apk add --no-cache nodejs npm tini

# NGINX 설정 파일 복사
# Host의 NGINX 설정을 Docker 내부 NGINX에 적용
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Next.js 실행 환경 복사
WORKDIR /usr/app/
# Next.js 빌드 결과물과 런타임 의존성 복사
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Next.js와 NGINX를 동시에 실행할 스크립트 파일 복사
# 빌더 단계의 /app/start.sh를 복사합니다.
COPY start.sh /usr/bin/start.sh

# 💡 핵심 수정 1: 줄바꿈 변환을 먼저 시도
RUN sed -i 's/\r$//' /usr/bin/start.sh

# 💡 핵심 수정 2: 실행 권한을 독립적인 명령으로 부여
RUN chmod +x /usr/bin/start.sh

# 컨테이너가 80 포트를 노출합니다.
EXPOSE 80

# NGINX와 Node.js를 함께 시작하는 스크립트를 tini로 실행
CMD ["tini", "--", "/usr/bin/start.sh"]