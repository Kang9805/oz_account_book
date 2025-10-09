FROM python:3.12.2-slim

# 파이썬 출력 버퍼링 비활성화 및 개발 설정 모듈 지정
ENV PYTHONUNBUFFERED 1
# [최종 반영] 설정 파일 분리 구조 (config.settings.dev) 사용
ENV DJANGO_SETTINGS_MODULE=config.settings.dev

# 작업 디렉토리 설정
WORKDIR /app

# 1. uv 설치
RUN pip install uv

# 🚨 [새로운 단계: psql 클라이언트 설치] 🚨
# apt-get을 업데이트하고, postgresql-client를 설치합니다.
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# 2. 의존성 정의 파일 복사
COPY ./pyproject.toml .
COPY ./uv.lock .

# 3. run.sh 스크립트 복사 및 실행 권한 부여
COPY ./scripts/run.sh /app/scripts/run.sh
RUN chmod +x /app/scripts/run.sh

# 4. uv를 사용하여 코어 및 개발 의존성 설치
ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN uv sync --extra dev

# 5. 나머지 프로젝트 파일 복사 (가장 마지막에)
COPY . .

# 포트 노출
EXPOSE 8000
