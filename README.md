# MyFileHub (FileHub)

-----

유저별로 관리할 수 있는 개인 파일 허브입니다.
홈서버(라즈베리파이/NAS/개인 서버)에서 Docker Compose로 빠르게 배포할 수 있게 구현하는 것을 목표로 합니다.
지금은 안됨 ㅎ;

## 주요기능
- 로그인(세션 기반)을 통해 언제든지 외부에서 쉽게 파일 엑세스 가능!
- 파일 검색 고도화(날짜/이름/파일 확장자)하여 나만의 파일 탐색 가능
- 자유롭게 바꿀 수 있는 화면과 구조
- 
----

## 무슨 기반?
- app: Django & Gunicorn(WSGI)
- was: Nginx (리버스 프록시)
- db: PostgreSQL
  
----

## 어떻게 시작함?
### 1) 설치해야 하는 것
- Docker Engine / Docker Desktop
- Docker Compose v2

#### Window/macOS
-> [Docker 공식 다운로드 페이지](https://www.docker.com/products/docker-desktop/, "Docker 설치경로:") 
에서 Docker Desktop 설치하면 Docker Engine이랑 같이 설치됩니다. Window는 **WSL2**(윈도우 사용자를 위한 리눅스 시스템)을 설치해야 할 수도 있음

#### Linux
```
curl -fL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2) 이거 설치
```
git clone https://github.com/smallwanderer/local-filehub.git
cd filehub
```

### 3) 환경변수 설정
프로젝트 폴더에 .env 파일을 생성하세요.
예시 폴더 .env.example을 참고
```
cp .env.example .env
```

### 4) 빌드 및 실행
```
docker compose up -d --build
```
빌드가 되었다면 http://localhost/로 접속해보세요.

### 5) Django DB Migrate
컨테이너가 만들어지고 DB랑 Django랑 연동시켜야됩니다.
```
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
```
관리자 페이지: http://localhost/admin/

----
