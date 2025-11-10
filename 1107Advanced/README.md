# OCR 메뉴판 번역기 웹앱 - 개발 일지 (Debug Log)

본 문서는 Ruby on Rails를 사용하여 OCR 메뉴판 번역기 웹앱을 개발하는 과정에서 발생한 모든 환경 설정 문제와 오류, 그리고 이를 해결한 과정을 상세히 기록함.
이 프로젝트는 로컬 macOS 환경에서 `rbenv`를 사용한 Ruby 3.3.0과 Rails 7.1.x 버전을 기반으로 Tesseract OCR과 DeepL API를 연동하는 것을 목표로 함.

## 프로젝트 기술 스택

* **Language**: Ruby 3.3.0 (rbenv)
* **Framework**: Ruby on Rails 7.1.x
* **Database**: SQLite3
* **Package Management**: Bundler
* **OCR Engine**: Tesseract OCR (with `rtesseract` Gem)
* **Translation API**: DeepL API Free (with `faraday` Gem)
* **File Handling**: Active Storage
* **Environment**: macOS (Local Development)

---

## 1. 개발 환경 설정 및 초기 오류

### Phase 1: 카카오클라우드 점프 호스트 시도 (실패)

* **작업 내용**: RVM을 사용하여 Ruby 환경 구성을 시도함.
* **문제 발생**: RVM GPG 키를 가져오는 과정에서 키 서버 연결 오류 발생.
    ```bash
    gpg: keyserver receive failed: No data
    ```
* **원인 분석**: 클라우드 환경의 방화벽 또는 네트워크 문제로 인해 기본 GPG 키 서버(port 80) 접근이 차단된 것으로 추정됨.
* **해결 과정**: `hkps://keys.openpgp.org` (port 443)로 키 서버 주소를 변경하여 시도했으나, 로컬 환경의 안정성을 위해 개발 환경을 로컬(macOS)로 전환하기로 결정함.

### Phase 2: 로컬(macOS) Ruby 환경 설정 및 권한 문제

* **작업 내용**: 로컬 macOS 환경에서 `rbenv` (1.3.2) 및 Ruby (3.3.0)가 설치되어 있음을 확인함. Rails 프레임워크 설치를 시도함.
* **문제 발생 1**: `gem install rails` 실행 시, 시스템 Ruby 경로에 대한 권한 오류 발생.
    ```bash
    ERROR:  You don't have write permissions for the /Library/Ruby/Gems/2.6.0 directory.
    ```
* **원인 분석 1**: 터미널이 `rbenv` 환경이 아닌 macOS의 시스템 기본 Ruby(2.6.0)를 바라보고 있었음.
* **문제 발생 2**: `rbenv` 환경으로 전환 후 `gem install rails` 재시도 시, `rbenv` 경로 내에서 권한 오류 발생.
    ```bash
    ERROR:  While executing gem ... (Gem::FilePermissionError)
    You don't have write permissions for the /Users/apple/.rbenv/versions/3.3.0/lib/ruby/gems/3.3.0/gems/rails-8.1.1/...
    ```
* **원인 분석 2**: `rbenv`로 Ruby를 설치했음에도 불구하고, 해당 디렉토리의 소유권(ownership)이 비정상적으로 설정되어 사용자 계정(`apple`)이 쓰기 권한을 갖지 못하는 특이 케이스 발생.
* **해결 과정**: `sudo chown` 명령을 사용하여 `rbenv` 관련 디렉토리 전체의 소유권을 현재 사용자에게 재귀적으로 부여하여 문제를 해결함.
    ```bash
    sudo chown -R $(whoami) $(rbenv root)
    ```

---

## 2. Rails 프로젝트 생성 및 버전 충돌

### Phase 3: Rails 프로젝트 생성 오류

* **작업 내용**: `gem install rails` (Success) 이후 프로젝트 생성을 시도함.
* **문제 발생 1**: `rails new .` 실행 시, Rails가 설치되지 않았다는 오류 발생.
    ```bash
    Rails is not currently installed on this system.
    ```
* **원인 분석 1**: `rbenv` 환경에서 Gem을 설치한 후, 쉘이 Gem의 실행 파일(shim)을 즉시 인식하지 못함.
* **해결 과정 1**: `rbenv rehash` 명령을 실행하여 `rbenv`의 shim을 갱신함.

* **문제 발생 2**: `rails new .` 재시도 시, 애플리케이션 이름 오류 발생.
    ```bash
    Invalid application name 1107Advanced. Please give a name which does not start with numbers.
    ```
* **원인 분석 2**: Rails 애플리케이션(Ruby 모듈) 이름은 숫자로 시작할 수 없으나, 현재 폴더(`1107Advanced`) 이름이 숫자로 시작함.
* **해결 과정 2**: `rails new menu_translator` 명령으로 하위 디렉토리에 정상적인 이름의 프로젝트를 생성함.

### Phase 4: Rails 8.1과 7.1의 대규모 충돌 (핵심 디버깅)

* **작업 내용**: `gem install rails`가 기본값으로 최신 버전인 **Rails 8.1.1**을 설치함.
* **문제 발생 1 (Syntax Error)**: `rails active_storage:install` 실행 시, `actionview-8.1.1` Gem 내부에서 문법 오류 발생.
    ```bash
    SyntaxError: anonymous rest parameter is also used within block
    ```
* **원인 분석 1**: Rails 8.1.1 버전이 현재 사용 중인 Ruby 3.3.0 버전과 문법적으로 충돌하거나 호환성 문제가 있었음.
* **해결 과정 1**: 안정적인 개발을 위해 Rails 8.1.1을 제거하고, Rails 7.1.x (7.1.6) 안정 버전을 명시하여 재설치함.
    ```bash
    gem uninstall rails
    gem install rails --version 7.1.6
    rbenv rehash
    ```
* **문제 발생 2 (Version Mismatch)**: `config/application.rb` 파일에서 `Unknown version "8.1"` 오류 발생.
* **원인 분석 2**: 프로젝트 생성 시 Rails 8.1.1 템플릿이 적용되어, 설정 파일에 `config.load_defaults 8.1` 코드가 남아있었음.
* **해결 과정 2**: `config/application.rb` 파일의 버전을 `config.load_defaults 7.1`로 수동 수정함.

* **문제 발생 3 (DB 경로 오류)**: `rails db:create` 실행 시, 데이터베이스 파일이 `db/` 폴더가 아닌 `storage/` 폴더에 생성됨.
    ```bash
    Created database 'storage/development.sqlite3'
    ```
* **원인 분석 3**: 이 역시 Rails 8.1 템플릿의 잔재임. Rails 8.1은 Docker/클라우드 배포를 기본으로 가정하여 영구 저장소 볼륨(`storage/`)에 DB 파일을 생성하도록 `config/database.yml` 파일의 기본값을 변경했음.
* **해결 과정 3**: `config/database.yml` 파일을 열어 `development` 및 `test` 환경의 `database:` 경로를 `storage/development.sqlite3`에서 **`db/development.sqlite3`**로 수동 수정함.

---

## 3. 데이터베이스 및 Active Storage 문제 해결

### Phase 5: 끈질긴 데이터베이스 오류 (The Final Boss)

* **작업 내용**: `config/database.yml` 경로 수정 후, `rm -f storage/*.sqlite3`, `rails db:create`, `rails db:migrate`를 실행함.
* **문제 발생 (The Unsolved Error)**: 이미지 업로드(`POST /menu_entries`) 시, 모든 마이그레이션과 캐시 클리어(`rails tmp:clear`)를 수행했음에도 불구하고 `ActiveModel::UnknownAttributeError`가 지속적으로 발생함.
    ```bash
    ActiveModel::UnknownAttributeError (unknown attribute 'image' for MenuEntry.):
    app/controllers/menu_entries_controller.rb:9:in `create'
    ```
* **원인 분석**:
    1.  `MenuEntry` 모델은 `has_one_attached :image`를 통해 `image` 속성을 Active Storage에 위임함.
    2.  `Active Storage`는 `active_storage_attachments` 테이블이 필요함.
    3.  `rails db:migrate` 로그 분석 결과, `CreateActiveStorageTables` 마이그레이션이 정상적으로 실행되지 않았거나, 실행되었더라도 Rails 애플리케이션이 로드될 때 `MenuEntry` 모델이 Active Storage Gem의 기능을 인식하지 못하는 **로드 순서 문제(Load Order Problem)**가 발생함.

* **최종 해결 과정**: `app/models/menu_entry.rb` 파일 최상단에 Active Storage의 핵심 모듈을 **수동으로 `require`** 하여, `MenuEntry` 클래스가 정의되기 전에 Active Storage의 기능이 메모리에 로드되도록 강제함.

    ```ruby
    # app/models/menu_entry.rb
    
    require 'active_storage' # ⬅️ 이 코드 추가로 문제 해결
    
    class MenuEntry < ApplicationRecord
      has_one_attached :image
    end
    ```

---

## 4. 핵심 기능 구현 및 성공

### Phase 6: 기능 구현 및 테스트

* **작업 내용**:
    1.  `MenuTranslatorService`를 생성하여 Tesseract OCR(`rtesseract`) 로직과 DeepL API(`faraday`) 호출 로직을 캡슐화함.
    2.  `MenuEntriesController`의 `create` 액션에서 이 서비스를 호출하도록 수정함.
    3.  `new.html.erb` (업로드 폼) 및 `show.html.erb` (결과 뷰)를 작성함.

* **최종 결과 (성공)**: Rails 서버 재시작 후 이미지 업로드 테스트.
    * 콘솔 로그에서 `MenuEntry Update` 쿼리가 Tesseract로 추출된 텍스트(예: `original_text" = '하이니 네일...'`)와 DeepL로 번역된 텍스트로 실행됨을 확인함.
    * `show` 페이지에서 원본 이미지와 OCR 텍스트, 번역된 텍스트가 정상적으로 출력됨.

* **최종 결과 스크린샷**:
    * <img width="2880" height="1638" alt="Image" src="https://github.com/user-attachments/assets/2724d7f2-c58f-4205-ad67-33c970cea006" />

    * <img width="2880" height="1634" alt="Image" src="https://github.com/user-attachments/assets/34aff6ba-7759-4bab-a64e-8b3c623bca6c" />

    * <img width="2880" height="1638" alt="Image" src="https://github.com/user-attachments/assets/5397eb9f-6019-45df-98c0-5a76209aeb4a" />

### Phase 7: API 사용량 모니터링
* **이슈**: DeepL 관리 페이지에서 API 사용량(`소모된 글자 수`)이 0으로 표시됨.
* **원인 분석**: API 사용량 통계는 실시간이 아니며, DeepL 서버에서 배치(Batch) 처리되므로 반영에 시간 지연(Caching)이 발생함.
* **결론**: 기능이 정상 작동(번역된 텍스트가 반환됨)하므로 API 키는 유효하며, 통계 반영을 기다리면 됨.