import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back.settings")
django.setup()
from produits.models import Categorie, SousCategorie

# Créer les catégories
fruits_legumes = Categorie.objects.create(nom="Fruits et légumes")
viandes_poissons_oeufs = Categorie.objects.create(nom="Viandes, poissons, oeufs") 
produits_laitiers = Categorie.objects.create(nom="Produits laitiers")

produits_secs_conserves = Categorie.objects.create(nom="Produits secs/conserves")
cereales_pates_riz = SousCategorie.objects.create(nom="Céréales, pâtes, riz", categorie=produits_secs_conserves)
conserves = SousCategorie.objects.create(nom="Conserves", categorie=produits_secs_conserves)
condiments_epices_huiles = SousCategorie.objects.create(nom="Condiments, épices, huiles", categorie=produits_secs_conserves)

surgelés = Categorie.objects.create(nom="Surgelés")
plats_prepares = SousCategorie.objects.create(nom="Plats préparés", categorie=surgelés)
legumes_fruits_surgeles = SousCategorie.objects.create(nom="Légumes, fruits", categorie=surgelés)
poissons_viandes_surgeles = SousCategorie.objects.create(nom="Poissons, viandes", categorie=surgelés)

boissons = Categorie.objects.create(nom="Boissons")
eaux_sodas_jus = SousCategorie.objects.create(nom="Eaux, sodas, jus", categorie=boissons)
cafe_the_infusions = SousCategorie.objects.create(nom="Café, thé, infusions", categorie=boissons)
vins_bieres_spiritueux = SousCategorie.objects.create(nom="Vins, bières, spiritueux", categorie=boissons)

produits_boulangerie = Categorie.objects.create(nom="Produits de boulangerie")
pains_viennoiseries = SousCategorie.objects.create(nom="Pains, viennoiseries", categorie=produits_boulangerie)
gateaux_biscuits = SousCategorie.objects.create(nom="Gâteaux, biscuits", categorie=produits_boulangerie)

produits_hygiene_entretien = Categorie.objects.create(nom="Produits d'hygiène et d'entretien")