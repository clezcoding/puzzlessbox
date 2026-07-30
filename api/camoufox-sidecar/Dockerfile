FROM python:3.14-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir fastapi==0.138.0 uvicorn==0.34.0 httpx==0.28.1

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
