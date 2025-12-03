#!/bin/sh

# Activer le mode debug
export DEBUG=False

# Appliquer les migrations
echo "Applying migrations..."
python back/manage.py makemigrations
python back/manage.py migrate
# Collecter les fichiers statiques
echo "Collecting static files..."
python back/manage.py collectstatic


# Démarrer le serveur de développement Django
echo "Starting Django development server..."
exec python back/manage.py runserver 127.0.0.1:8004
