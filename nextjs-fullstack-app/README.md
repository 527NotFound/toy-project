# 🚀 Next.js 통합 로그인 서비스 구축 및 Docker 배포 일지

이 문서는 React 컴포넌트 이미지를 기반으로 Next.js 풀스택 로그인 서비스를 구축하고, Docker를 사용하여 카카오클라우드(Ubuntu/AMD64) 서버 환경에 배포하는 과정에서 발생한 주요 문제와 해결 과정을 기록합니다.

---

## 1. ⚙️ 프로젝트 개요 및 환경 설정

| 구분 | 내용 |
| :--- | :--- |
| **프로젝트** | Next.js 통합 로그인 폼 (Frontend UI + Backend API Routes) |
| **목표** | NGINX Reverse Proxy를 통해 Docker 컨테이너 서비스 |
| **로컬 환경** | macOS (ARM64) |
| **서버 환경** | 카카오클라우드 Ubuntu VM (AMD64) |
| **도메인** | `badboy.kakaolab.cloud` |

---

## 2. 🚨 주요 장애 및 해결 과정 (개발 일지)

### 2.1. 초반 환경 구성 및 인증 문제

| 발생 오류 | 원인 | 해결 |
| :--- | :--- | :--- |
| **`TLS Handshake Timeout`** | Docker Hub 로그인/푸시 시 네트워크 인증 시간 초과. | Colima 재시작 및 네트워크 환경 점검 후 **액세스 토큰(PAT)**을 사용하여 `docker login` 강제 갱신. |
| **`push access denied`** | GitHub 연동 계정 사용으로 Docker 로그인 세션 만료. | Docker Hub에서 **Write 권한의 액세스 토큰**을 생성하여 비밀번호 대신 사용. |
| **`address already in use (8080)`** | 기존 Jenkins 서비스가 호스트 포트 8080을 점유. | `sudo systemctl stop jenkins` 명령으로 서비스 중지 후 포트 확보. |

### 2.2. 플랫폼 및 컨테이너 런타임 문제 (가장 큰 난관)

| 발생 오류 | 원인 | 해결 |
| :--- | :--- | :--- |
| **`Exec format error` / `Restarting`** | macOS(ARM64)에서 빌드된 이미지를 AMD64 서버에서 실행하여 플랫폼 불일치 발생. | **`docker buildx build --platform linux/amd64`** 명령으로 AMD64 전용 이미지 생성 후 재배포. (`docker-buildx` 플러그인 설치 필수) |
| **`npm: not found`** | 통합 이미지의 `runner` 단계에서 `nginx:alpine`에 **Node.js/npm 런타임이 없어** `npm start` 실행 실패. | **`Dockerfile`의 `runner` 단계**에 `RUN apk add --no-cache nodejs npm tini` 명령을 추가하여 Node.js 환경 재구성. |
| **`NotFound: content digest`** | AMD64 빌드 시 캐시와의 충돌 발생. | **`--no-cache --pull`** 옵션을 함께 사용하여 캐시를 완전히 무시하고 빌드하도록 강제. |

### 2.3. 🤯 최종 오류 및 해결 (스크립트 형식 문제)

플랫폼 불일치와 런타임 문제가 해결된 후에도 `502 Bad Gateway` 및 `Exec format error`가 지속되었습니다.

| 발생 오류 | 최종 원인 | 해결 |
| :--- | :--- | :--- |
| **`[FATAL tini] exec /usr/bin/start.sh failed: Exec format error` (지속)** | **`start.sh` 파일의 맨 앞에 불필요한 문자열(`// nextjs-fullstack-app/start.sh` 등)이 삽입**되어 스크립트의 첫 줄(`#!/bin/sh`)이 무효화됨. 리눅스 셸이 스크립트를 실행하지 못하고 실패함. | **로컬 `start.sh` 파일**에서 **`#!/bin/sh` 앞에 있는 모든 문자열을 삭제**하여 셔뱅 라인이 파일의 첫 번째 문자로 시작하도록 수정 후 재빌드 및 푸시. **(최종 접속 성공)** |

---

## 3. ✅ 최종 배포 성공 구성

* **최종 Docker 이미지:** `fivetwoseven/nextjs-combined-app:amd64`
* **호스트 NGINX 설정:** 포트 80 트래픽을 호스트 포트 **8080**으로 리버스 프록시.
* **결과:** **`badboy.kakaolab.cloud/login` 접속 시 Next.js 로그인 폼 정상 렌더링.**

---
**최종 문제 분석 및 해결**

* **502 Bad Gateway** 및 **Exec format error**의 최종 원인:
    * `start.sh` 파일의 맨 앞에 원치 않는 문자열이 삽입되어 스크립트의 첫 줄(`#!/bin/sh`)이 무효화되었습니다.
    * 리눅스 셸은 스크립트의 첫 줄에서 `#!`를 찾지 못했기 때문에 스크립트가 아닌 일반 텍스트 파일로 인식했고, `Exec format error`를 발생시키며 실패했습니다.
* **현재 상태:**
    * `start.sh` 파일이 올바르게 수정되면서 `npm start`가 성공적으로 실행되었고, Next.js 앱이 3000 포트에서 구동되었습니다.
    * 호스트 NGINX → 컨테이너 NGINX (80 포트) → Next.js (3000 포트)로의 트래픽 흐름이 **완벽하게 확립**되었습니다.