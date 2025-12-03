import os
import django

# Définir la variable d'environnement
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back.settings")
django.setup()

from livraisons.models import Livreur, Tarif

# Supposons que vous ayez déjà un livreur avec l'ID 1
livreur = Livreur.objects.get(pk=1)  # Remplacez par l'ID approprié de votre livreur

# Liste de vos tarifs
tarifs_data = [
    (2, 29.17, 35.00),
    (5, 33.33, 40.00),
    (10, 40.83, 49.00),
    (15, 48.33, 58.00),
    (20, 55.83, 67.00),
    (25, 63.33, 76.00),
    (30, 70.83, 85.00),
]

# Boucle pour enregistrer chaque tarif
for poids, prix_ht, prix_ttc in tarifs_data:
    tarif = Tarif(
        livreur=livreur,
        poids_min=poids,
        poids_max=poids,
        prix_ht=prix_ht,
        prix_ttc=prix_ttc,
    )
    tarif.save()

print("Tarifs ajoutés avec succès.")