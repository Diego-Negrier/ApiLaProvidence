# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Installation des dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libpq-dev \
    libmariadb-dev \
    libmariadb-dev-compat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copier requirements.txt en PREMIER (cache si non modifié)
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn>=21.2.0

# ==========================================
# STAGE 2: Runtime
# ==========================================
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=back.settings \
    DOCKER_ENV=production

# LAYER 1: Dépendances système (change rarement)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# LAYER 2: Packages Python du builder (change quand requirements.txt change)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# LAYER 3: Structure des dossiers (change rarement)
RUN mkdir -p /app/static /app/media /app/logs && \
    chmod -R 777 /app/static /app/media /app/logs

# LAYER 4: Script d'entrée (change rarement)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# LAYER 5: Code applicatif (change SOUVENT - doit être EN DERNIER)
COPY . .

# LAYER 6: Collectstatic (dépend du code, donc après COPY)
<<<<<<< HEAD
RUN echo "🔍 Running collectstatic..." && \
    python manage.py collectstatic --noinput --clear && \
    echo "✅ Collectstatic completed" && \
    ls -la /app/static/ || echo "⚠️  Collectstatic failed, continuing..."
=======
RUN python manage.py collectstatic --noinput --clear || echo "⚠️  Collectstatic failed, continuing..."
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8007/admin/login/ || exit 1

EXPOSE 8007

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", \
    "--bind", "0.0.0.0:8007", \
    "--workers", "4", \
    "--threads", "2", \
    "--worker-class", "gthread", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "--timeout", "120", \
    "--graceful-timeout", "30", \
    "back.wsgi:application"]
