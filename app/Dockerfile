FROM python:3.12-slim

# 1. 시스템 패키지 설치 (OCR + PDF + ML 라이브러리)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-kor \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 2. HuggingFace 캐시 위치 설정
ENV HF_HOME=/app/.cache/huggingface

WORKDIR /app

# 3. Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Docling 모델 사전 다운로드
RUN python -c "from docling.document_converter import DocumentConverter; DocumentConverter()"

# 5. 프로젝트 복사
COPY ./ /app/

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]