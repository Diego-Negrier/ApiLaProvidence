<<<<<<< HEAD
#!/bin/sh

# Désactiver le mode debug en production
export DEBUG=${DEBUG}
export DJANGO_SETTINGS_MODULE=back.settings



# Appliquer les migrations
echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate

# Collecter les fichiers statiques sans interaction
echo "Collecting static files..."
python manage.py collectstatic --noinput  # Ajout de --noinput pour éviter la demande de confirmation

# Démarrer uWSGI
echo "Starting uWSGI..."
exec uwsgi --ini /app/back.uwsgi.ini --http-socket :8007
=======
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
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
