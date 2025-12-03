#!/bin/sh

#!/bin/bash

# Activer le mode debug pour l'environnement local
export DEBUG=True
export DJANGO_ENV=local

# Appliquer les migrations
echo "Applying migrations..."
python back/manage.py makemigrations
python back/manage.py migrate

# Collecter les fichiers statiques sans confirmation
echo "Collecting static files..."
python back/manage.py collectstatic --noinput

# Démarrer le serveur de développement Django
echo "Starting Django development server..."
exec python back/manage.py runserver 0.0.0.0:8007


# # 2. Appliquer les migrations
# python manage.py migrate

# # 3. Configurer les permissions
# python manage.py setup_permissions