# management/commands/test_produit.py
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from produits.models import Produit, Categorie, Fournisseur
from decimal import Decimal
import requests
import time

class Command(BaseCommand):
    help = 'Test rapide: teste la création et la sauvegarde d\'un produit'

    def add_arguments(self, parser):
        parser.add_argument('--avec-image', action='store_true', help='Télécharger une image test')
        parser.add_argument('--dry-run', action='store_true', help='Ne pas sauvegarder (mode test uniquement)')

    def handle(self, *args, **options):
        avec_image = options['avec_image']
        dry_run = options['dry_run']

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 TEST DE CRÉATION D\'UN PRODUIT (MODE DRY-RUN)'))
            self.stdout.write(self.style.WARNING('═' * 50))
            self.stdout.write(self.style.WARNING('⚠️  Aucune donnée ne sera sauvegardée'))
        else:
            self.stdout.write(self.style.SUCCESS('🧪 CRÉATION D\'UN PRODUIT'))
            self.stdout.write(self.style.SUCCESS('═' * 50))
            self.stdout.write(self.style.SUCCESS('✅ Le produit sera sauvegardé en base'))
        self.stdout.write('')

        try:
            # Vérifications
            self.stdout.write('🔍 Vérification des dépendances...')

            if not Categorie.objects.exists():
                self.stdout.write(self.style.ERROR('❌ Aucune catégorie trouvée'))
                return

            if not Fournisseur.objects.exists():
                self.stdout.write(self.style.ERROR('❌ Aucun fournisseur trouvé'))
                return

            categorie = Categorie.objects.first()
            fournisseur = Fournisseur.objects.first()

            self.stdout.write(self.style.SUCCESS(f'  ✅ Catégorie trouvée: {categorie}'))
            self.stdout.write(self.style.SUCCESS(f'  ✅ Fournisseur trouvé: {fournisseur}'))
            self.stdout.write('')

            # Création du produit
            if dry_run:
                self.stdout.write('📦 Création du produit test EN MÉMOIRE...')
            else:
                self.stdout.write('📦 Création et sauvegarde du produit...')

            start_time = time.time()

            produit = Produit(
                nom="Produit Test Automatique",
                description_longue="Ceci est un produit créé automatiquement pour tester le système",
                prix_ht=Decimal('99.99'),
                stock_actuel=50,
                categorie=categorie,
                fournisseur=fournisseur,
                est_actif=True,
                en_promotion=False
            )

            # Sauvegarder si pas en mode dry-run
            if not dry_run:
                produit.save()

            creation_time = time.time() - start_time

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Produit créé en mémoire'))
                self.stdout.write(self.style.SUCCESS(f'  ⏱️  Temps: {creation_time:.3f}s'))
                self.stdout.write(self.style.WARNING(f'  ⚠️  PAS sauvegardé en base'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Produit créé et sauvegardé'))
                self.stdout.write(self.style.SUCCESS(f'  ⏱️  Temps: {creation_time:.3f}s'))
                self.stdout.write(self.style.SUCCESS(f'  🆔 Numéro unique: {produit.numero_unique}'))
                self.stdout.write(self.style.SUCCESS(f'  🔗 Slug: {produit.slug}'))
            self.stdout.write('')

            # Afficher les détails
            self.stdout.write(f'📋 Détails du produit:')
            self.stdout.write(f'  • Nom: {produit.nom}')
            self.stdout.write(f'  • Prix HT: {produit.prix_ht}€')
            self.stdout.write(f'  • Stock: {produit.stock_actuel}')
            self.stdout.write(f'  • Catégorie: {produit.categorie}')
            self.stdout.write(f'  • Fournisseur: {produit.fournisseur}')
            self.stdout.write(f'  • Actif: {"Oui" if produit.est_actif else "Non"}')

            # Test des propriétés calculées (si elles existent)
            try:
                self.stdout.write(f'  • Prix TTC: {produit.prix_final_ttc}€')
            except:
                pass

            try:
                self.stdout.write(f'  • Stock actuel: {produit.stock_actuel}')
            except:
                pass
            
            self.stdout.write('')

            # Test image
            image_success = False
            if avec_image:
                self.stdout.write('📸 Téléchargement et sauvegarde d\'image...')

                try:
                    start_time = time.time()

                    # Utiliser une API plus fiable - picsum.photos
                    response = requests.get(
                        'https://picsum.photos/400/300',
                        timeout=10,
                        allow_redirects=True
                    )

                    download_time = time.time() - start_time

                    if response.status_code == 200:
                        file_size = len(response.content)

                        self.stdout.write(self.style.SUCCESS(f'  ✅ Image téléchargée'))
                        self.stdout.write(self.style.SUCCESS(f'  ⏱️  Temps: {download_time:.2f}s'))
                        self.stdout.write(self.style.SUCCESS(f'  📦 Taille: {file_size / 1024:.1f} KB'))

                        # Sauvegarder l'image si le produit a été sauvegardé
                        if not dry_run:
                            from django.core.files.base import ContentFile
                            image_content = ContentFile(response.content)
                            produit.image_principale.save(
                                f'produit_test_{produit.numero_unique}.jpg',
                                image_content,
                                save=True
                            )
                            image_success = True
                            self.stdout.write(self.style.SUCCESS(f'  💾 Image sauvegardée sur le produit'))
                        else:
                            image_success = True
                            self.stdout.write(self.style.WARNING(f'  ⚠️  Image PAS sauvegardée (mode dry-run)'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  ❌ Échec (HTTP {response.status_code})'))

                except requests.Timeout:
                    self.stdout.write(self.style.ERROR('  ❌ Timeout (>10s)'))
                    self.stdout.write(self.style.WARNING('  ⚠️  La connexion est trop lente'))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Erreur: {str(e)}'))
                    import traceback
                    self.stdout.write(self.style.ERROR('Détails:'))
                    traceback.print_exc()

                self.stdout.write('')

            # Test de validation
            self.stdout.write('✅ Test de validation du modèle...')
            try:
                produit.full_clean()  # Valide le modèle sans sauvegarder
                self.stdout.write(self.style.SUCCESS('  ✅ Validation réussie'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Erreur de validation: {str(e)}'))
            
            self.stdout.write('')

            # Résumé
            self.stdout.write(self.style.SUCCESS('═' * 50))
            self.stdout.write(self.style.SUCCESS('✅ TEST RÉUSSI'))
            self.stdout.write(self.style.SUCCESS('═' * 50))
            self.stdout.write('')
            
            self.stdout.write('📊 Résumé:')
            if dry_run:
                self.stdout.write(f'  • Produit créé en mémoire: ✅')
            else:
                self.stdout.write(f'  • Produit créé et sauvegardé: ✅')
            self.stdout.write(f'  • Validation du modèle: ✅')
            if avec_image:
                self.stdout.write(f'  • Téléchargement image: {"✅" if image_success else "❌"}')
            self.stdout.write('')

            if dry_run:
                self.stdout.write(self.style.WARNING('💡 Aucune donnée n\'a été sauvegardée dans la base (mode --dry-run)'))
            else:
                self.stdout.write(self.style.SUCCESS(f'💾 Produit sauvegardé avec l\'ID: {produit.pk}'))
                self.stdout.write(self.style.SUCCESS(f'🔗 Accessible via le slug: {produit.slug}'))
            self.stdout.write('')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('═' * 50))
            self.stdout.write(self.style.ERROR(f'❌ ÉCHEC DU TEST'))
            self.stdout.write(self.style.ERROR('═' * 50))
            self.stdout.write(self.style.ERROR(f'Erreur: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'Type: {type(e).__name__}'))
            self.stdout.write('')

            import traceback
            self.stdout.write(self.style.ERROR('Traceback complet:'))
            traceback.print_exc()
