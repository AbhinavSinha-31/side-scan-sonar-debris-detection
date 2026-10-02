# Sonar Debris AI — backend production image.
# Python 3.14 + CPU-only torch/torchvision (wheels verified for cp314).
# Real data (SQLite + sonar images) is baked in and seeded into the persistent
# /app/data volume on first boot by docker/entrypoint.sh.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies: OpenCV (libgl/libglib), torch CPU (libgomp), build tools
# for any source builds during pip install.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python runtime dependencies (pins from the proven training env, CPU torch).
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Backend application.
COPY backend /app/backend

# Trained model.
COPY models /app/models

# Seed data: real SQLite DB + all sonar images / processed / exports / demo.
# Layout of data/ mirrors what the runtime expects under /app/data.
COPY data/ /app/data-seed/
COPY sonar_debris.db /app/data-seed/sonar_debris.db

# Entrypoint seeds /app/data (the persistent volume) on first boot.
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Production defaults (overridable via environment variables on the platform).
ENV DATABASE_URL=sqlite:////app/data/sonar_debris.db \
    DATA_DIR=/app/data \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    API_RELOAD=false \
    DETECTION_MODEL_PATH=/app/models/best.pt \
    LLM_PROVIDER=disabled \
    DEBUG=false

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]