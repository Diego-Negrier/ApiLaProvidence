#!/usr/bin/env python3
"""
Script de test pour vérifier la récupération des images de produits

Usage: python test_images_produit.py
"""

import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from produits.models import Produit, ImageProduit


def test_methodes_images():
    """Teste les méthodes de récupération d'images"""

    print("\n" + "="*60)
    print("TEST DES MÉTHODES DE RÉCUPÉRATION D'IMAGES")
    print("="*60 + "\n")

    # Compter les produits
    nb_produits = Produit.objects.count()
    print(f"📦 Nombre de produits dans la base: {nb_produits}")

    if nb_produits == 0:
        print("⚠️  Aucun produit trouvé. Générez des produits avec:")
        print("   python manage.py generer_produits --nombre=5")
        return

    # Tester sur les 3 premiers produits
    produits = Produit.objects.all()[:3]

    for i, produit in enumerate(produits, 1):
        print(f"\n{'─'*60}")
        print(f"🔍 Test du produit #{i}: {produit.nom}")
        print(f"{'─'*60}")

        # Test 1: Image principale
        if produit.image_principale:
            print(f"✅ Image principale: {produit.image_principale.url}")
        else:
            print("❌ Pas d'image principale")

        # Test 2: get_nombre_images()
        try:
            nb_images = produit.get_nombre_images()
            print(f"✅ get_nombre_images(): {nb_images} images")
        except Exception as e:
            print(f"❌ Erreur get_nombre_images(): {e}")

        # Test 3: get_images_additionnelles()
        try:
            images_add = produit.get_images_additionnelles()
            count = images_add.count()
            print(f"✅ get_images_additionnelles(): {count} images")

            for j, img in enumerate(images_add[:3], 1):  # Limiter à 3
                legende = img.legende or "(sans légende)"
                print(f"   {j}. {legende} - ordre: {img.ordre}")

        except Exception as e:
            print(f"❌ Erreur get_images_additionnelles(): {e}")

        # Test 4: get_toutes_images()
        try:
            toutes_urls = produit.get_toutes_images()
            print(f"✅ get_toutes_images(): {len(toutes_urls)} URLs")

            for j, url in enumerate(toutes_urls[:3], 1):  # Limiter à 3
                print(f"   {j}. {url}")

        except Exception as e:
            print(f"❌ Erreur get_toutes_images(): {e}")

        # Test 5: get_image_principale_obj()
        try:
            img_principale = produit.get_image_principale_obj()
            if img_principale:
                print(f"✅ get_image_principale_obj(): Trouvée (ID: {img_principale.id})")
            else:
                print("ℹ️  get_image_principale_obj(): Aucune image marquée comme principale")
        except Exception as e:
            print(f"❌ Erreur get_image_principale_obj(): {e}")

    # Statistiques globales
    print(f"\n{'═'*60}")
    print("📊 STATISTIQUES GLOBALES")
    print(f"{'═'*60}")

    total_images = ImageProduit.objects.count()
    print(f"Total d'images additionnelles: {total_images}")

    produits_avec_images = Produit.objects.filter(images__isnull=False).distinct().count()
    print(f"Produits avec images additionnelles: {produits_avec_images}/{nb_produits}")

    produits_avec_principale = Produit.objects.exclude(image_principale='').count()
    print(f"Produits avec image principale: {produits_avec_principale}/{nb_produits}")

    print(f"\n{'═'*60}")
    print("✅ Tests terminés avec succès!")
    print(f"{'═'*60}\n")


if __name__ == '__main__':
    test_methodes_images()
