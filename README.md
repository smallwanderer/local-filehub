# OpenShelf

개인별로 파일을 관리할 수 있는 **클라우드 스토리지 서비스**입니다.  
라즈베리파이, NAS, 개인 서버 같은 홈서버 환경에서도 **Docker Compose로 빠르게 배포**할 수 있도록 구현하는 것을 목표로 합니다.

---

## 주요 기능

- **세션 기반 로그인**을 통해 외부에서도 안전하게 파일에 접근
- **파일 검색 고도화**  
  - 파일명
  - 날짜
  - 확장자  
  등의 조건으로 원하는 파일을 빠르게 탐색
- **유연한 UI/구조 확장성**  
  화면 구성과 서비스 구조를 자유롭게 변경 가능
- **홈서버 친화적 배포**  
  라즈베리파이, NAS, 개인 서버 환경에서 간편하게 실행 가능

---

## 기술 스택

- **app**: Django + Gunicorn (WSGI)
- **was**: Nginx (Reverse Proxy)
- **db**: PostgreSQL/PGVector

---

## 시작하기

### 1. 사전 설치

- Docker Engine / Docker Desktop
- Docker Compose v2

#### Windows / macOS

Docker Desktop을 설치하면 Docker Engine도 함께 설치됩니다.

- Docker Desktop: [Docker 공식 다운로드 페이지](https://www.docker.com/products/docker-desktop/)

Windows 환경에서는 경우에 따라 **WSL2** 설정이 필요할 수 있습니다.

#### Linux

```bash
curl -fL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

### 2. 프로젝트 클론

이거 설치:
```
git clone https://github.com/smallwanderer/local-filehub.git
cd filehub
```

### 3) 환경변수 설정
프로젝트 폴더에 .env 파일을 생성하세요.
.env.example 파일을 참고

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

## 배포 목표 환경

OpenShelf는 다음과 같은 환경에서의 운영을 염두에 두고 있습니다.

라즈베리파이
개인 서버
Docker Compose 기반 홈서버 환경
프로젝트 목표

OpenShelf는 단순한 파일 업로드 기능을 넘어,
개인이 직접 소유하고 운영할 수 있는 파일 스토리지 서비스를 지향합니다.

### 향후 확장 가능성

- RAG 기반 파일 지식 저장소
- 팀별 파일 공유
