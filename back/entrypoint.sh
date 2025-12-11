#!/bin/bash
set -e

echo "🚀 Starting ApiLaProvidence..."

# Migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# ⬇️ Recollect statiques au démarrage
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✨ Starting application..."
exec "$@"