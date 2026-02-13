FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ /app/
EXPOSE 8000

# 처음엔 프로젝트가 없으니, compose에서 command를 sleep으로 줄 거라 여기 CMD는 나중에 사용됨
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
