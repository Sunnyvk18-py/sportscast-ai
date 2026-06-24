FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY dashboard/backend/requirements.txt /app/dashboard/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt

COPY pyproject.toml /app/
COPY pipeline /app/pipeline
COPY dashboard /app/dashboard

ENV PYTHONPATH=/app

WORKDIR /app/dashboard/backend
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
