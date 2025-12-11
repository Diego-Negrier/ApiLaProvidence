# produits/management/commands/clear_data.py

from django.core.management.base import BaseCommand
from django.db import transaction
from produits.models import Categorie, SousCategorie, SousSousCategorie, Produit
from fournisseur.models import Fournisseur


class Command(BaseCommand):
    help = '🗑️  Commande pour vider les tables de données La Providence'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Supprimer uniquement les catégories (et leurs relations)'
        )
        parser.add_argument(
            '--produits',
            action='store_true',
            help='Supprimer uniquement les produits'
        )
        parser.add_argument(
            '--fournisseurs',
            action='store_true',
            help='Supprimer uniquement les fournisseurs'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Supprimer TOUTES les données (catégories, produits, fournisseurs)'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmer la suppression sans demander de confirmation'
        )

    def handle(self, *args, **options):
        categories_only = options['categories']
        produits_only = options['produits']
        fournisseurs_only = options['fournisseurs']
        delete_all = options['all']
        confirm = options['confirm']

        # Si aucune option spécifique, afficher l'aide
        if not (categories_only or produits_only or fournisseurs_only or delete_all):
            self.stdout.write(self.style.WARNING('❌ Veuillez spécifier ce que vous voulez supprimer:'))
            self.stdout.write('  --categories       Supprimer les catégories')
            self.stdout.write('  --produits         Supprimer les produits')
            self.stdout.write('  --fournisseurs     Supprimer les fournisseurs')
            self.stdout.write('  --all              Supprimer TOUTES les données')
            self.stdout.write('')
            self.stdout.write('  --confirm          Ne pas demander de confirmation')
            self.stdout.write('')
            self.stdout.write('Exemples:')
            self.stdout.write('  python manage.py clear_data --produits --confirm')
            self.stdout.write('  python manage.py clear_data --all')
            return

        # Compter les éléments avant suppression
        counts_before = {
            'categories': Categorie.objects.count(),
            'sous_categories': SousCategorie.objects.count(),
            'sous_sous_categories': SousSousCategorie.objects.count(),
            'produits': Produit.objects.count(),
            'fournisseurs': Fournisseur.objects.count(),
        }

        # Afficher ce qui va être supprimé
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('⚠️  ATTENTION - SUPPRESSION DE DONNÉES'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')

        if delete_all:
            self.stdout.write('Les éléments suivants vont être SUPPRIMÉS:')
            self.stdout.write(f'  • {counts_before["categories"]} Catégories')
            self.stdout.write(f'  • {counts_before["sous_categories"]} Sous-catégories')
            self.stdout.write(f'  • {counts_before["sous_sous_categories"]} Sous-sous-catégories')
            self.stdout.write(f'  • {counts_before["produits"]} Produits')
            self.stdout.write(f'  • {counts_before["fournisseurs"]} Fournisseurs')
        else:
            if categories_only:
                self.stdout.write('Les CATÉGORIES vont être supprimées:')
                self.stdout.write(f'  • {counts_before["categories"]} Catégories')
                self.stdout.write(f'  • {counts_before["sous_categories"]} Sous-catégories')
                self.stdout.write(f'  • {counts_before["sous_sous_categories"]} Sous-sous-catégories')
            if produits_only:
                self.stdout.write('Les PRODUITS vont être supprimés:')
                self.stdout.write(f'  • {counts_before["produits"]} Produits')
            if fournisseurs_only:
                self.stdout.write('Les FOURNISSEURS vont être supprimés:')
                self.stdout.write(f'  • {counts_before["fournisseurs"]} Fournisseurs')

        self.stdout.write('')

        # Demander confirmation si --confirm n'est pas passé
        if not confirm:
            response = input('❓ Êtes-vous sûr de vouloir continuer? (tapez "OUI" pour confirmer): ')
            if response.upper() != 'OUI':
                self.stdout.write(self.style.SUCCESS('✅ Opération annulée'))
                return

        # Procéder à la suppression
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🗑️  Suppression en cours...'))
        self.stdout.write('')

        try:
            with transaction.atomic():
                if delete_all or categories_only:
                    self._delete_categories()

                if delete_all or produits_only:
                    self._delete_produits()

                if delete_all or fournisseurs_only:
                    self._delete_fournisseurs()

            # Compter après suppression
            counts_after = {
                'categories': Categorie.objects.count(),
                'sous_categories': SousCategorie.objects.count(),
                'sous_sous_categories': SousSousCategorie.objects.count(),
                'produits': Produit.objects.count(),
                'fournisseurs': Fournisseur.objects.count(),
            }

            # Afficher le résumé
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write(self.style.SUCCESS('✅ SUPPRESSION TERMINÉE'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
            self.stdout.write('')

            if delete_all or categories_only:
                deleted_cat = counts_before['categories'] - counts_after['categories']
                deleted_scat = counts_before['sous_categories'] - counts_after['sous_categories']
                deleted_sscat = counts_before['sous_sous_categories'] - counts_after['sous_sous_categories']
                self.stdout.write(self.style.SUCCESS(f'🗑️  Catégories supprimées: {deleted_cat}'))
                self.stdout.write(self.style.SUCCESS(f'🗑️  Sous-catégories supprimées: {deleted_scat}'))
                self.stdout.write(self.style.SUCCESS(f'🗑️  Sous-sous-catégories supprimées: {deleted_sscat}'))

            if delete_all or produits_only:
                deleted_prod = counts_before['produits'] - counts_after['produits']
                self.stdout.write(self.style.SUCCESS(f'🗑️  Produits supprimés: {deleted_prod}'))

            if delete_all or fournisseurs_only:
                deleted_fourn = counts_before['fournisseurs'] - counts_after['fournisseurs']
                self.stdout.write(self.style.SUCCESS(f'🗑️  Fournisseurs supprimés: {deleted_fourn}'))

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('📊 État actuel de la base:'))
            self.stdout.write(self.style.SUCCESS(f'  • Catégories: {counts_after["categories"]}'))
            self.stdout.write(self.style.SUCCESS(f'  • Sous-catégories: {counts_after["sous_categories"]}'))
            self.stdout.write(self.style.SUCCESS(f'  • Sous-sous-catégories: {counts_after["sous_sous_categories"]}'))
            self.stdout.write(self.style.SUCCESS(f'  • Produits: {counts_after["produits"]}'))
            self.stdout.write(self.style.SUCCESS(f'  • Fournisseurs: {counts_after["fournisseurs"]}'))
            self.stdout.write('')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('=' * 70))
            self.stdout.write(self.style.ERROR(f'❌ ERREUR lors de la suppression: {str(e)}'))
            self.stdout.write(self.style.ERROR('=' * 70))
            self.stdout.write('')

    def _delete_categories(self):
        """Supprime toutes les catégories et leurs relations"""
        self.stdout.write('  └─ Suppression des sous-sous-catégories...')
        count_sscat = SousSousCategorie.objects.count()
        SousSousCategorie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'     ✓ {count_sscat} sous-sous-catégories supprimées'))

        self.stdout.write('  └─ Suppression des sous-catégories...')
        count_scat = SousCategorie.objects.count()
        SousCategorie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'     ✓ {count_scat} sous-catégories supprimées'))

        self.stdout.write('  └─ Suppression des catégories...')
        count_cat = Categorie.objects.count()
        Categorie.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'     ✓ {count_cat} catégories supprimées'))

    def _delete_produits(self):
        """Supprime tous les produits"""
        self.stdout.write('  └─ Suppression des produits...')
        count = Produit.objects.count()
        Produit.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'     ✓ {count} produits supprimés'))

    def _delete_fournisseurs(self):
        """Supprime tous les fournisseurs"""
        self.stdout.write('  └─ Suppression des fournisseurs...')
        count = Fournisseur.objects.count()
        Fournisseur.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'     ✓ {count} fournisseurs supprimés'))
