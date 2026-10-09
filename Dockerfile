# ──────────────────────────────────────────────
# Agentic ML Experimentation System — Backend
# ──────────────────────────────────────────────
FROM python:3.13-slim

# Prevent .pyc files and enable unbuffered stdout/stderr for container logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Install Python dependencies (cached unless requirements.txt changes) ──
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy the application package ──
COPY app/ app/

# ── Create a non-root user and prepare the data directory ──
#    UID 1000 matches the default 'ubuntu' user on EC2, which
#    simplifies bind-mount permissions for the data volume.
RUN groupadd --gid 1000 appgroup \
 && useradd  --uid 1000 --gid appgroup --no-create-home appuser \
 && mkdir -p /app/data \
 && chown appuser:appgroup /app/data

USER appuser

EXPOSE 8000

# ── Production ASGI server ──
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
