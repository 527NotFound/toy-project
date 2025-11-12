#!/bin/sh

# Next.js 앱을 백그라운드에서 실행 (3000 포트)
npm start &

# NGINX를 포어그라운드에서 실행 (80 포트)
nginx -g 'daemon off;'