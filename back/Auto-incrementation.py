from django.db import connection
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back.settings")
django.setup()
def reset_auto_increment():
    # Récupérer la liste des tables
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Pour chaque table, réinitialiser l'auto-incrément
        for table in tables:
            table_name = table[0]
            print(table_name)
            # Ignorer les tables du système et celles sans clé primaire
            if table_name not in ['information_schema', 'performance_schema'] and table_name != 'django_migrations':
                try:
                    # Réinitialiser l'auto-incrément
                    cursor.execute(f"ALTER TABLE `{table_name}` AUTO_INCREMENT = 1")
                    print(f"Auto-incrément réinitialisé pour la table {table_name}")
                except Exception as e:
                    print(f"Erreur lors de la réinitialisation de {table_name}: {e}")
reset_auto_increment()