"""
Command Django pour supprimer des produits avec logging détaillé

Usage:
  python manage.py supprimer_produits --tous                    # Supprimer tous les produits
  python manage.py supprimer_produits --categorie="Fruits"      # Supprimer par catégorie
  python manage.py supprimer_produits --inactifs                # Supprimer produits inactifs
  python manage.py supprimer_produits --stock-zero               # Supprimer produits sans stock
  python manage.py supprimer_produits --ids 1,2,3                # Supprimer par IDs
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from produits.models import Produit, Categorie

# Configuration du logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Supprime des produits avec logging détaillé'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tous',
            action='store_true',
            help='Supprimer tous les produits'
        )
        parser.add_argument(
            '--categorie',
            type=str,
            help='Supprimer les produits d\'une catégorie spécifique'
        )
        parser.add_argument(
            '--inactifs',
            action='store_true',
            help='Supprimer uniquement les produits inactifs'
        )
        parser.add_argument(
            '--stock-zero',
            action='store_true',
            help='Supprimer les produits avec stock à zéro'
        )
        parser.add_argument(
            '--ids',
            type=str,
            help='Liste d\'IDs séparés par des virgules (ex: 1,2,3,4)'
        )
        parser.add_argument(
            '--confirmation',
            action='store_true',
            help='Passer la confirmation (dangereux!)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('🗑️  SUPPRESSION DE PRODUITS'))
        self.stdout.write(self.style.WARNING('=' * 60))

        # Construire la requête
        queryset = Produit.objects.all()
        description = "tous les produits"

        if options['categorie']:
            try:
                categorie = Categorie.objects.get(nom=options['categorie'])
                queryset = queryset.filter(categorie=categorie)
                description = f"les produits de la catégorie '{options['categorie']}'"
            except Categorie.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ Catégorie '{options['categorie']}' introuvable")
                )
                return

        elif options['inactifs']:
            queryset = queryset.filter(est_actif=False)
            description = "les produits inactifs"

        elif options['stock_zero']:
            queryset = queryset.filter(stock_actuel=0)
            description = "les produits avec stock à zéro"

        elif options['ids']:
            ids = [int(id.strip()) for id in options['ids'].split(',')]
            queryset = queryset.filter(pk__in=ids)
            description = f"les produits avec IDs: {', '.join(map(str, ids))}"

        elif not options['tous']:
            self.stdout.write(
                self.style.ERROR('❌ Vous devez spécifier une option de suppression')
            )
            self.stdout.write('Utilisez --help pour voir les options disponibles')
            return

        # Compter les produits
        count = queryset.count()

        if count == 0:
            self.stdout.write(self.style.WARNING('⚠️  Aucun produit trouvé avec ces critères'))
            return

        # Afficher le résumé
        self.stdout.write('')
        self.stdout.write(self.style.WARNING(f'Produits à supprimer: {description}'))
        self.stdout.write(self.style.WARNING(f'Nombre de produits: {count}'))
        self.stdout.write('')

        # Afficher les détails des produits
        self.stdout.write(self.style.HTTP_INFO('📋 Détails des produits:'))
        for produit in queryset[:10]:  # Limiter à 10 pour l'affichage
            self.stdout.write(
                f'  • [{produit.pk}] {produit.nom} - '
                f'Stock: {produit.stock_actuel} - '
                f'Actif: {"Oui" if produit.est_actif else "Non"}'
            )

        if count > 10:
            self.stdout.write(f'  ... et {count - 10} autres produits')

        self.stdout.write('')

        # Confirmation
        if not options['confirmation']:
            confirmation = input(
                self.style.WARNING(
                    f'⚠️  Êtes-vous sûr de vouloir supprimer {count} produit(s) ? '
                    'Cette action est IRRÉVERSIBLE! (oui/non): '
                )
            )

            if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(self.style.SUCCESS('✓ Suppression annulée'))
                return

        # Suppression avec logging détaillé
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🗑️  Suppression en cours...'))

        # Sauvegarder les informations avant suppression pour le rapport
        produits_supprimes = []
        try:
            # Récupérer les infos avant suppression (limité pour performance)
            if count <= 1000:  # Seulement si pas trop de produits
                produits_supprimes = list(queryset.values(
                    'id', 'nom', 'numero_unique', 'categorie__nom',
                    'stock_actuel', 'prix_ht', 'est_actif'
                ))
        except Exception as e:
            logger.warning(f"Impossible de récupérer les détails: {str(e)}")

        # Suppression en masse - BEAUCOUP PLUS RAPIDE
        try:
            with transaction.atomic():
                nombre_supprimes = queryset.delete()[0]

                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {nombre_supprimes} produits supprimés en masse')
                )
                logger.info(f"Suppression en masse: {nombre_supprimes} produits")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la suppression: {str(e)}')
            )
            logger.error(f"Erreur de suppression: {str(e)}")
            return

        # Résumé final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✓ SUPPRESSION TERMINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write(f'✓ Produits supprimés: {nombre_supprimes}')
        self.stdout.write('')

        # Logger le résumé
        logger.info(f"Suppression terminée: {nombre_supprimes} produits supprimés")

        # Sauvegarder un rapport détaillé (si on a les infos)
        if produits_supprimes:
            self._generer_rapport(produits_supprimes, nombre_supprimes)

    def _generer_rapport(self, produits_supprimes, erreurs):
        """Génère un rapport de suppression"""
        import json
        from datetime import datetime
        import os

        rapport_dir = 'logs/suppressions'
        os.makedirs(rapport_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rapport_file = f'{rapport_dir}/suppression_produits_{timestamp}.json'

        rapport = {
            'timestamp': datetime.now().isoformat(),
            'total_supprimes': len(produits_supprimes),
            'total_erreurs': len(erreurs),
            'produits': produits_supprimes,
            'erreurs': erreurs
        }

        with open(rapport_file, 'w', encoding='utf-8') as f:
            json.dump(rapport, f, ensure_ascii=False, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f'📄 Rapport sauvegardé: {rapport_file}')
        )
        logger.info(f"Rapport de suppression généré: {rapport_file}")
