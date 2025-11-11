# 🚀 PhotoMaskApp 개발 일지 (Ruby on Rails + Python/OpenCV 연동) - 업데이트됨

본 프로젝트는 카카오클라우드 VM 환경에 Ruby on Rails 웹 애플리케이션을 배포하고, Python/OpenCV를 활용하여 증명사진의 얼굴 영역을 검출 및 처리하는 기능을 구현하는 것을 목표로 합니다.

***

## 📋 프로젝트 개요 및 목표

* **배포 환경:** 카카오클라우드 VM (Ubuntu)
* **백엔드:** Ruby on Rails 7.1 + PostgreSQL
* **미들웨어:** Puma (Rails) + Nginx (리버스 프록시)
* **핵심 기능:** 이미지 파일 업로드 후, **HSV 기반 피부색 검출**을 통해 얼굴 영역을 검은색으로 덮어 마스킹 처리 (개인정보 보호 목적).
* **특징:** Ruby on Rails 환경에서 외부 Python 스크립트를 `Open3` 모듈로 호출하여 비동기적인 이미지 처리를 구현했습니다.

***

## 🛠️ I. 초기 환경 설정 및 기반 구축

| 내용 | 상세 |
| :--- | :--- |
| **VM 접속** | VS Code Remote SSH를 사용하여 카카오클라우드 VM에 접속. |
| **Ruby 환경** | **`rbenv`**를 사용하여 Ruby 3.3.0 버전을 설치. |
| **PostgreSQL** | 설치 및 설정. `pg_hba.conf`에서 로컬 접속 인증 방식을 `peer`에서 **`md5`**로 변경하여 인증 오류 해결. |
| **DB 테이블 오류** | `ImageResult` 마이그레이션 파일 누락으로 발생. 누락된 마이그레이션 파일 재생성 후 `rails db:migrate` 실행하여 테이블 구축. |

***

## 💻 II. 웹 서버 및 배포 연동 (Nginx + Puma)

| 내용 | 상세 |
| :--- | :--- |
| **Puma/Nginx 설정** | **`systemd`**에 `puma.service` 등록. Nginx `proxy_pass` 포트를 **`8000`**에서 **`3000`**으로 수정하여 통신 성공. |
| **`502 Bad Gateway` (재발)** | SCSS 테마 추가 후 **`cannot load such file -- sassc`** 오류로 Puma 서버 시작 실패. |
| **해결 (서버)** | **`Gemfile`에 `gem 'sassc-rails'` 추가** 및 `bundle install` 실행. `puma.service` 파일에 **`Environment=PATH="..."`** 를 명시적으로 설정하여 rbenv 환경 경로 불일치 문제 해결 후 Puma 재시작. |
| **HTTPS 및 권한** | Certbot으로 **HTTPS** 적용. 카카오클라우드 **보안 그룹 443 포트** 개방. Rails `config.hosts` 및 `config.action_dispatch.trust_proxy = true` 설정으로 인증 오류(CSRF) 해결. |
| **정적 파일 오류** | Nginx 실행 사용자 권한 문제로 정적 파일 및 이미지 깨짐 발생. `sudo chmod -R 755` 명령으로 프로젝트 **`public` 폴더에 권한** 부여하여 해결. |

***

## 🎨 III. UI/UX 개선 및 Asset 처리 (추가 과정)

| 내용 | 상세 |
| :--- | :--- |
| **UI 테마 적용** | 다크 모드, 보라색 계열의 SCSS (`custom_theme.scss`) 스타일 구현. |
| **`NoMethodError`** | `config/application.rb` 파일에서 Asset Pipeline 설정 시 **`config.asset.enabled = true`** 처럼 메서드 이름을 잘못 호출하여 서버 시작 실패. |
| **해결 (코드)** | 잘못된 호출을 **`config.assets.enabled = true`** (복수형)로 수정하여 코드 오류 해결 후 Puma 재시작. |
| **스타일 미적용** | SCSS 파일이 `production` 환경에서 **Precompile**되지 않아 UI 로드 실패. |
| **해결 (Asset)** | **`RAILS_ENV=production bundle exec rails assets:precompile`** 명령 강제 실행 후 서버 재시작하여 스타일 적용. |
| **파비콘 교체** | 브라우저 탭에 표시되는 **파비콘(Favicon)**을 Ruby 로고 이미지 파일로 교체하여 브랜딩 통일. |

***

## 💻 IV. 이미지 처리 기능 구현 및 최종 로직

| 내용 | 상세 |
| :--- | :--- |
| **Python/OpenCV 연동** | Rails Controller에서 **`Open3.capture3`**를 사용하여 **가상환경 내 Python 인터프리터의 절대 경로** 호출. |
| **최종 로직** | **HSV 색상 분할**을 사용하여 **인간의 피부색 범위**를 마스크로 생성. 마스크 영역을 순수 검은색으로 덮어 마스킹 처리 구현. |
| **결과** | **증명사진에서 피부색 영역만 정확히 검출되어 검은색으로 덮인 이미지**를 성공적으로 생성. |

***

## ✅ 개발 결과

모든 과제와 복잡한 서버/환경 연동 및 코드 오류(DB, Nginx/Puma, rbenv, CSRF, Asset Pipeline, UI 테마)가 성공적으로 해결되었습니다. 애플리케이션은 **`https://badboy.kakaolab.cloud`** 에서 안정적으로 작동하며, **다크 모드 UI**가 적용된 상태에서 파일을 업로드하면 **얼굴 영역이 검은색으로 마스킹된 이미지**를 확인할 수 있습니다.

<img width="1440" height="900" alt="스크린샷 2025-11-11 오전 12 34 44" src="https://github.com/user-attachments/assets/724c3ccb-f533-41c0-9ff2-03c66ea0b710" />

<img width="1440" height="900" alt="스크린샷 2025-11-11 오전 12 34 53" src="https://github.com/user-attachments/assets/aec43ea2-f3a7-4481-9c90-0a92a58fb43b" />
