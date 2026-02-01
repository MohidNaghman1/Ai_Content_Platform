FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ai_content_platform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn ai_content_platform.app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
