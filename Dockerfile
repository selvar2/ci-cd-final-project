# syntax=docker/dockerfile:1.6

# Builder image installs dependencies
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# Final runtime image
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PYTHONPATH=/app/src
WORKDIR /app
RUN adduser --disabled-password --gecos "" appuser && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY src ./src
COPY README.md ./README.md

ENV APP_ENVIRONMENT=production \
    APP_ENFORCE_HTTPS=true

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s CMD curl -f http://localhost:${PORT}/health || exit 1

USER appuser
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "app.main:app", "--timeout", "120"]
