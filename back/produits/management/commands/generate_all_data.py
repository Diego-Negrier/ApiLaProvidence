# produits/management/commands/generate_all_data.py

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from produits.models import Categorie, SousCategorie, SousSousCategorie, Produit
from fournisseur.models import Fournisseur
import sys
from io import StringIO
from faker import Faker
from decimal import Decimal

fake = Faker('fr_FR')

class Command(BaseCommand):
    help = '🚀 Script tout-en-un: génère catégories, fournisseurs et produits avec images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nombre-fournisseurs',
            type=int,
            default=30,
            help='Nombre de fournisseurs à créer (défaut: 30)'
        )
        parser.add_argument(
            '--nombre-produits',
            type=int,
            default=100,
            help='Nombre de produits à créer (défaut: 100)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Supprimer toutes les données existantes avant de générer'
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Ne pas télécharger les images Unsplash (plus rapide pour les tests)'
        )

    def handle(self, *args, **options):
        nombre_fournisseurs = options['nombre_fournisseurs']
        nombre_produits = options['nombre_produits']
        clean = options['clean']
        skip_images = options['skip_images']

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('🎯 GÉNÉRATION COMPLÈTE DES DONNÉES LA PROVIDENCE'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # ===================================
        # ÉTAPE 0: NETTOYAGE (si demandé)
        # ===================================
        if clean:
            self.stdout.write(self.style.WARNING('🗑️  ÉTAPE 0: Nettoyage des données existantes'))
            self.stdout.write('')

            counts_before = {
                'produits': Produit.objects.count(),
                'fournisseurs': Fournisseur.objects.count(),
                'categories': Categorie.objects.count(),
                'sous_categories': SousCategorie.objects.count(),
                'sous_sous_categories': SousSousCategorie.objects.count(),
            }

            self.stdout.write(f'📊 Données actuelles:')
            self.stdout.write(f'   • Produits: {counts_before["produits"]}')
            self.stdout.write(f'   • Fournisseurs: {counts_before["fournisseurs"]}')
            self.stdout.write(f'   • Catégories: {counts_before["categories"]}')
            self.stdout.write(f'   • Sous-catégories: {counts_before["sous_categories"]}')
            self.stdout.write(f'   • Sous-sous-catégories: {counts_before["sous_sous_categories"]}')
            self.stdout.write('')

            with transaction.atomic():
                Produit.objects.all().delete()
                Fournisseur.objects.all().delete()
                SousSousCategorie.objects.all().delete()
                SousCategorie.objects.all().delete()
                Categorie.objects.all().delete()

            self.stdout.write(self.style.SUCCESS('✅ Nettoyage terminé'))
            self.stdout.write('')

        # ===================================
        # ÉTAPE 1: CRÉATION DES CATÉGORIES
        # ===================================
        self.stdout.write(self.style.WARNING('📂 ÉTAPE 1: Création de la hiérarchie des catégories'))
        self.stdout.write('')

        try:
            # Capturer la sortie de la commande
            out = StringIO()
            call_command('setup_initial_data', '--categories-only', stdout=out)

            # Afficher uniquement les lignes importantes
            for line in out.getvalue().split('\n'):
                if '✨' in line or '♻️' in line or '📊' in line:
                    self.stdout.write(line)

            categories_count = Categorie.objects.count()
            sous_categories_count = SousCategorie.objects.count()
            sous_sous_categories_count = SousSousCategorie.objects.count()

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'✅ Catégories créées: {categories_count}'))
            self.stdout.write(self.style.SUCCESS(f'✅ Sous-catégories créées: {sous_categories_count}'))
            self.stdout.write(self.style.SUCCESS(f'✅ Sous-sous-catégories créées: {sous_sous_categories_count}'))
            self.stdout.write('')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la création des catégories: {str(e)}'))
            return

        # ===================================
        # ÉTAPE 2: CRÉATION DES FOURNISSEURS
        # ===================================
        self.stdout.write(self.style.WARNING(f'👨‍🌾 ÉTAPE 2: Création de {nombre_fournisseurs} fournisseurs'))
        self.stdout.write('')

        try:
            out = StringIO()
            call_command(
                'setup_initial_data',
                '--fournisseurs-only',
                f'--nombre-fournisseurs={nombre_fournisseurs}',
                stdout=out
            )

            # Compter les fournisseurs créés
            fournisseurs_count = Fournisseur.objects.count()

            self.stdout.write(self.style.SUCCESS(f'✅ {fournisseurs_count} fournisseurs créés'))
            self.stdout.write('')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la création des fournisseurs: {str(e)}'))
            return

        # ===================================
        # ÉTAPE 3: CRÉATION DES PRODUITS
        # ===================================

        self.stdout.write(self.style.WARNING(f'📦 ÉTAPE 3: Création de {nombre_produits} produits'))
        if skip_images:
            self.stdout.write(self.style.WARNING('⚠️  Images désactivées (mode rapide)'))
        else:
            self.stdout.write(self.style.WARNING('📸 Téléchargement des images Unsplash activé'))
        self.stdout.write('')

        try:
            # Vérifier qu'il y a au moins une catégorie et un fournisseur
            if not Categorie.objects.exists():
                self.stdout.write(self.style.ERROR('❌ Aucune catégorie trouvée. Impossible de créer des produits.'))
                return

            if not Fournisseur.objects.exists():
                self.stdout.write(self.style.ERROR('❌ Aucun fournisseur trouvé. Impossible de créer des produits.'))
                return

            # TEST: Créer d'abord UN produit pour vérifier
            self.stdout.write(self.style.WARNING('🧪 Test de création d\'un produit...'))
            
            try:
                categorie_test = Categorie.objects.first()
                fournisseur_test = Fournisseur.objects.first()
                
                produit_test = Produit.objects.create(
                    nom="Produit Test",
                    description_longue="Ceci est un produit de test",
                    prix_ht=Decimal('99.99'),
                    stock_actuel=10,
                    categorie=categorie_test,
                    fournisseur=fournisseur_test,
                    est_actif=True
                )
                
                self.stdout.write(self.style.SUCCESS(f'  ✅ Produit test créé: {produit_test.nom} (ID: {produit_test.pk})'))
                
                # Test image si activé
                if not skip_images:
                    self.stdout.write(self.style.WARNING('  📸 Test de téléchargement d\'image...'))
                    try:
                        import requests
                        from django.core.files.base import ContentFile
                        import time
                        
                        start_time = time.time()
                        response = requests.get(
                            f'https://source.unsplash.com/400x300/?product',
                            timeout=5,
                            stream=True
                        )
                        elapsed = time.time() - start_time
                        
                        if response.status_code == 200:
                            produit_test.image_principale.save(
                                'test.jpg',
                                ContentFile(response.content),
                                save=True
                            )
                            self.stdout.write(self.style.SUCCESS(f'  ✅ Image téléchargée en {elapsed:.1f}s'))
                        else:
                            self.stdout.write(self.style.WARNING(f'  ⚠️  Échec téléchargement image (status: {response.status_code})'))
                            
                    except requests.Timeout:
                        self.stdout.write(self.style.WARNING('  ⚠️  Timeout lors du téléchargement (>5s)'))
                        self.stdout.write(self.style.WARNING('  💡 Conseil: utilisez --skip-images pour accélérer'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠️  Erreur image: {str(e)}'))
                
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('✅ Test réussi! Création des autres produits...'))
                self.stdout.write('')
                
                # Supprimer le produit test
                produit_test.delete()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Échec du test de création: {str(e)}'))
                self.stdout.write(self.style.ERROR('Arrêt de la procédure.'))
                import traceback
                traceback.print_exc()
                return

            # Appeler la commande de génération de produits avec affichage de la progression
            cmd_args = ['generer_produits', f'--nombre={nombre_produits}']
            if skip_images:
                cmd_args.append('--skip-images')

            # Ne pas capturer stdout pour voir la progression en temps réel
            self.stdout.write(self.style.WARNING(f'⏳ Création de {nombre_produits} produits en cours...'))
            self.stdout.write('')
            
            import time
            start_time = time.time()
            
            try:
                call_command(*cmd_args, stdout=self.stdout)  # Afficher directement la progression
                
                elapsed_time = time.time() - start_time
                
                # Afficher un résumé
                produits_count = Produit.objects.count()
                produits_avec_images = Produit.objects.exclude(image_principale='').count()
                
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('═' * 60))
                self.stdout.write(self.style.SUCCESS(f'✅ {produits_count} produits créés avec succès'))
                if not skip_images:
                    self.stdout.write(self.style.SUCCESS(f'✅ {produits_avec_images} produits avec images ({(produits_avec_images/produits_count*100):.1f}%)'))
                self.stdout.write(self.style.SUCCESS(f'⏱️  Temps écoulé: {elapsed_time:.1f}s ({elapsed_time/nombre_produits:.2f}s/produit)'))
                self.stdout.write(self.style.SUCCESS('═' * 60))
                self.stdout.write('')
                
            except KeyboardInterrupt:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('⚠️  Interruption par l\'utilisateur'))
                produits_count = Produit.objects.count()
                self.stdout.write(self.style.WARNING(f'📊 {produits_count} produits créés avant l\'interruption'))
                self.stdout.write('')
                return

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la création des produits: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'Détails: {type(e).__name__}'))
            import traceback
            traceback.print_exc()
            return

        # ===================================
        # RÉSUMÉ FINAL
        # ===================================
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('🎉 GÉNÉRATION COMPLÈTE TERMINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # Statistiques finales
        stats = {
            'categories': Categorie.objects.count(),
            'sous_categories': SousCategorie.objects.count(),
            'sous_sous_categories': SousSousCategorie.objects.count(),
            'fournisseurs': Fournisseur.objects.count(),
            'produits': Produit.objects.count(),
            'produits_bio': Produit.objects.filter(est_bio=True).count(),
            'produits_local': Produit.objects.filter(est_local=True).count(),
            'produits_nouveaute': Produit.objects.filter(est_nouveaute=True).count(),
            'produits_promo': Produit.objects.filter(en_promotion=True).count(),
        }

        if not skip_images:
            stats['produits_avec_images'] = Produit.objects.exclude(image_principale='').count()

        self.stdout.write(self.style.SUCCESS('📊 STATISTIQUES FINALES:'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📂 Catégories:'))
        self.stdout.write(f'   • Catégories principales: {stats["categories"]}')
        self.stdout.write(f'   • Sous-catégories: {stats["sous_categories"]}')
        self.stdout.write(f'   • Sous-sous-catégories: {stats["sous_sous_categories"]}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('👨‍🌾 Fournisseurs:'))
        self.stdout.write(f'   • Total: {stats["fournisseurs"]}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📦 Produits:'))
        self.stdout.write(f'   • Total: {stats["produits"]}')
        self.stdout.write(f'   • Bio: {stats["produits_bio"]}')
        self.stdout.write(f'   • Locaux: {stats["produits_local"]}')
        self.stdout.write(f'   • Nouveautés: {stats["produits_nouveaute"]}')
        self.stdout.write(f'   • En promotion: {stats["produits_promo"]}')
        if not skip_images:
            self.stdout.write(f'   • Avec images: {stats["produits_avec_images"]}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✨ Votre base de données La Providence est prête !'))
        self.stdout.write('')
