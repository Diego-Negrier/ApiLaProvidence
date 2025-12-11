#!/usr/bin/env python3
"""
Script pour créer des livreurs de test dans la base de données
Usage: python3 create_livreurs.py
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from livraisons.models import Livreur, Tarif
from decimal import Decimal


def create_livreurs():
    """Crée des livreurs de test s'ils n'existent pas déjà"""

    if not Livreur.objects.exists():
        print("📦 Création des livreurs de test...")

        # Livreur 1: Colissimo Standard
        livreur1 = Livreur.objects.create(
            nom="Colissimo",
            telephone="0800123456",
            email="contact@colissimo.fr",
            type_service="standard",
            est_actif=True
        )

        # Tarifs pour Colissimo
        Tarif.objects.create(
            livreur=livreur1,
            poids_min=Decimal('0.01'),
            poids_max=Decimal('5.00'),
            prix_ht=Decimal('4.95'),
            prix_ttc=Decimal('5.94'),
            taux_tva=Decimal('20.00')
        )

        Tarif.objects.create(
            livreur=livreur1,
            poids_min=Decimal('5.01'),
            poids_max=Decimal('10.00'),
            prix_ht=Decimal('6.95'),
            prix_ttc=Decimal('8.34'),
            taux_tva=Decimal('20.00')
        )

        # Livreur 2: Chronopost Express
        livreur2 = Livreur.objects.create(
            nom="Chronopost",
            telephone="0800789012",
            email="contact@chronopost.fr",
            type_service="express",
            est_actif=True
        )

        # Tarifs pour Chronopost
        Tarif.objects.create(
            livreur=livreur2,
            poids_min=Decimal('0.01'),
            poids_max=Decimal('5.00'),
            prix_ht=Decimal('12.50'),
            prix_ttc=Decimal('15.00'),
            taux_tva=Decimal('20.00')
        )

        Tarif.objects.create(
            livreur=livreur2,
            poids_min=Decimal('5.01'),
            poids_max=Decimal('10.00'),
            prix_ht=Decimal('16.67'),
            prix_ttc=Decimal('20.00'),
            taux_tva=Decimal('20.00')
        )

        # Livreur 3: Mondial Relay
        livreur3 = Livreur.objects.create(
            nom="Mondial Relay",
            telephone="0800345678",
            email="contact@mondialrelay.fr",
            type_service="standard",
            est_actif=True
        )

        # Tarifs pour Mondial Relay
        Tarif.objects.create(
            livreur=livreur3,
            poids_min=Decimal('0.01'),
            poids_max=Decimal('5.00'),
            prix_ht=Decimal('3.99'),
            prix_ttc=Decimal('4.79'),
            taux_tva=Decimal('20.00')
        )

        Tarif.objects.create(
            livreur=livreur3,
            poids_min=Decimal('5.01'),
            poids_max=Decimal('10.00'),
            prix_ht=Decimal('5.99'),
            prix_ttc=Decimal('7.19'),
            taux_tva=Decimal('20.00')
        )

        print("✅ 3 livreurs créés avec succès:")
        print(f"  - {livreur1.nom} (Standard) - Premier tarif: {Decimal('5.94')}€")
        print(f"  - {livreur2.nom} (Express) - Premier tarif: {Decimal('15.00')}€")
        print(f"  - {livreur3.nom} (Standard) - Premier tarif: {Decimal('4.79')}€")
    else:
        print("ℹ️ Des livreurs existent déjà dans la base de données")
        print(f"Nombre de livreurs: {Livreur.objects.count()}")
        for livreur in Livreur.objects.all():
            tarif_count = livreur.tarifs.count()
            premier_tarif = livreur.tarifs.first()
            prix = premier_tarif.prix_ttc if premier_tarif else "N/A"
            print(f"  - {livreur.nom} ({livreur.type_service}) - {tarif_count} tarifs - Prix: {prix}€")


if __name__ == '__main__':
    try:
        create_livreurs()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
