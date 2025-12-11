# produits/management/commands/setup_initial_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.text import slugify
from decimal import Decimal
from produits.models import Categorie, SousCategorie, SousSousCategorie
from fournisseur.models import Fournisseur
import random


class Command(BaseCommand):
    help = '🚀 Script unifié pour initialiser toutes les données La Providence (catégories + fournisseurs)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories-only',
            action='store_true',
            help='Créer uniquement les catégories'
        )
        parser.add_argument(
            '--fournisseurs-only',
            action='store_true',
            help='Créer uniquement les fournisseurs'
        )
        parser.add_argument(
            '--nombre-fournisseurs',
            type=int,
            default=30,
            help='Nombre de fournisseurs à créer (défaut: 30)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Supprimer toutes les données existantes avant de générer'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Mettre à jour les catégories existantes'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler l\'exécution sans créer de données'
        )

    def handle(self, *args, **options):
        categories_only = options['categories_only']
        fournisseurs_only = options['fournisseurs_only']
        nombre_fournisseurs = options['nombre_fournisseurs']
        clean = options['clean']
        update = options['update']
        dry_run = options['dry_run']

        # Si ni categories-only ni fournisseurs-only, faire les deux
        do_categories = not fournisseurs_only
        do_fournisseurs = not categories_only

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODE SIMULATION - Aucune donnée ne sera créée'))

        # ===================================
        # NETTOYAGE SI DEMANDÉ
        # ===================================
        if clean and not dry_run:
            self.stdout.write(self.style.WARNING('🗑️  Suppression des données existantes...'))
            if do_fournisseurs:
                Fournisseur.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Fournisseurs supprimés'))
            if do_categories:
                SousSousCategorie.objects.all().delete()
                SousCategorie.objects.all().delete()
                Categorie.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('✓ Catégories supprimées'))

        # ===================================
        # PARTIE 1: CRÉATION DES CATÉGORIES
        # ===================================
        if do_categories:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('=' * 70))
            self.stdout.write(self.style.WARNING('📂 CRÉATION DE LA HIÉRARCHIE DES CATÉGORIES'))
            self.stdout.write(self.style.WARNING('=' * 70))

            stats = self._creer_categories(update, dry_run)

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('📊 STATISTIQUES CATÉGORIES:'))
            self.stdout.write(self.style.SUCCESS(f'  ├─ Catégories: {stats["categories"]}'))
            self.stdout.write(self.style.SUCCESS(f'  ├─ Sous-catégories: {stats["sous_categories"]}'))
            self.stdout.write(self.style.SUCCESS(f'  └─ Sous-sous-catégories: {stats["sous_sous_categories"]}'))

        # ===================================
        # PARTIE 2: CRÉATION DES FOURNISSEURS
        # ===================================
        if do_fournisseurs:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('=' * 70))
            self.stdout.write(self.style.WARNING('👨‍🌾 CRÉATION DES FOURNISSEURS'))
            self.stdout.write(self.style.WARNING('=' * 70))

            nb_crees = self._creer_fournisseurs(nombre_fournisseurs, dry_run)

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('📊 STATISTIQUES FOURNISSEURS:'))
            self.stdout.write(self.style.SUCCESS(f'  ├─ Créés: {nb_crees}'))
            if not dry_run:
                self.stdout.write(self.style.SUCCESS(f'  └─ Total dans la base: {Fournisseur.objects.count()}'))

        # ===================================
        # RÉSUMÉ FINAL
        # ===================================
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        if dry_run:
            self.stdout.write(self.style.SUCCESS('🔍 SIMULATION TERMINÉE - Aucune donnée créée'))
        else:
            self.stdout.write(self.style.SUCCESS('🎉 INITIALISATION COMPLÈTE TERMINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def _creer_categories(self, update, dry_run):
        """Crée la hiérarchie complète des catégories"""

        categories_data = {
            '🏡 Habitat Autonome Premium': {
                'description': 'Habitat écologique, autonome et de prestige',
                'icone': '🏡',
                'couleur': '#2E7D32',
                'priorite': 1,
                'visible_home': True,
                'descripteurs': {
                    'certification': ['Passivhaus', 'BEPOS', 'HQE'],
                    'surface': ['< 50m²', '50-100m²', '100-200m²', '> 200m²'],
                    'type_construction': ['Neuf', 'Rénovation'],
                },
                'sous_categories': {
                    '🏠 Maisons Passives': {
                        'icone': '🏠',
                        'sous_sous_categories': [
                            {'nom': 'Maison passive sur-mesure', 'icone': '🎯'},
                            {'nom': 'Kit maison passive', 'icone': '📦'},
                            {'nom': 'Extension passive', 'icone': '➕'},
                        ]
                    },
                    '🏘️ Tiny Houses & Habitats Légers': {
                        'icone': '🏘️',
                        'sous_sous_categories': [
                            {'nom': 'Tiny house sur roues', 'icone': '🚐'},
                            {'nom': 'Tiny house fixe', 'icone': '🏡'},
                            {'nom': 'Yourte moderne', 'icone': '⛺'},
                            {'nom': 'Cabane bois', 'icone': '🛖'},
                        ]
                    },
                    '🔨 Rénovation Écologique': {
                        'icone': '🔨',
                        'sous_sous_categories': [
                            {'nom': 'Isolation thermique', 'icone': '🧱'},
                            {'nom': 'Fenêtres triple vitrage', 'icone': '🪟'},
                            {'nom': 'Étanchéité à l\'air', 'icone': '💨'},
                            {'nom': 'Ventilation double flux', 'icone': '🌬️'},
                        ]
                    },
                }
            },

            '🌳 Matériaux Nobles et Locaux': {
                'description': 'Matériaux durables, biosourcés et d\'exception',
                'icone': '🌳',
                'couleur': '#6D4C41',
                'priorite': 2,
                'visible_home': True,
                'descripteurs': {
                    'origine': ['Local < 100km', 'Régional', 'National'],
                    'certification': ['FSC', 'PEFC', 'Cradle to Cradle'],
                },
                'sous_categories': {
                    '🪵 Bois Massif Local': {
                        'icone': '🪵',
                        'sous_sous_categories': [
                            {'nom': 'Chêne massif', 'icone': '🌰'},
                            {'nom': 'Douglas local', 'icone': '🌲'},
                            {'nom': 'Épicéa massif', 'icone': '🎄'},
                            {'nom': 'Châtaignier', 'icone': '🌰'},
                        ]
                    },
                    '🌾 Matériaux Biosourcés': {
                        'icone': '🌾',
                        'sous_sous_categories': [
                            {'nom': 'Chanvre (isolant)', 'icone': '🌿'},
                            {'nom': 'Paille compressée', 'icone': '🌾'},
                            {'nom': 'Laine de mouton', 'icone': '🐑'},
                            {'nom': 'Liège expansé', 'icone': '🍾'},
                        ]
                    },
                    '🪨 Pierre Naturelle': {
                        'icone': '🪨',
                        'sous_sous_categories': [
                            {'nom': 'Pierre de taille locale', 'icone': '🏛️'},
                            {'nom': 'Ardoise naturelle', 'icone': '⬛'},
                            {'nom': 'Granit régional', 'icone': '💎'},
                        ]
                    },
                }
            },

            '⚡ Énergie Autonome': {
                'description': 'Solutions pour l\'indépendance énergétique',
                'icone': '⚡',
                'couleur': '#FFB300',
                'priorite': 3,
                'visible_home': True,
                'descripteurs': {
                    'puissance': ['< 3kW', '3-6kW', '6-9kW', '> 9kW'],
                    'stockage': ['Batteries lithium', 'Hydrogène', 'Volant inertie'],
                },
                'sous_categories': {
                    '☀️ Solaire Photovoltaïque': {
                        'icone': '☀️',
                        'sous_sous_categories': [
                            {'nom': 'Panneaux monocristallins', 'icone': '🔆'},
                            {'nom': 'Installation complète autoconso', 'icone': '🏠'},
                            {'nom': 'Kit solaire nomade', 'icone': '🎒'},
                        ]
                    },
                    '🔋 Stockage Énergie': {
                        'icone': '🔋',
                        'sous_sous_categories': [
                            {'nom': 'Batterie lithium-ion', 'icone': '🔋'},
                            {'nom': 'Batterie sodium-ion', 'icone': '⚡'},
                            {'nom': 'Système de gestion', 'icone': '🖥️'},
                        ]
                    },
                    '🌬️ Éolien Domestique': {
                        'icone': '🌬️',
                        'sous_sous_categories': [
                            {'nom': 'Éolienne verticale', 'icone': '🌀'},
                            {'nom': 'Éolienne horizontale', 'icone': '💨'},
                        ]
                    },
                    '🔥 Chauffage Bois': {
                        'icone': '🔥',
                        'sous_sous_categories': [
                            {'nom': 'Poêle à bois massif', 'icone': '🪵'},
                            {'nom': 'Poêle de masse', 'icone': '🏔️'},
                            {'nom': 'Insert cheminée', 'icone': '🔥'},
                        ]
                    },
                }
            },

            '💧 Eau et Traitement Local': {
                'description': 'Gestion autonome de l\'eau potable et usée',
                'icone': '💧',
                'couleur': '#0288D1',
                'priorite': 4,
                'visible_home': True,
                'sous_categories': {
                    '🚰 Filtration Eau Potable': {
                        'icone': '🚰',
                        'sous_sous_categories': [
                            {'nom': 'Filtre charbon actif', 'icone': '⚫'},
                            {'nom': 'Osmose inverse', 'icone': '💧'},
                            {'nom': 'UV stérilisation', 'icone': '☀️'},
                        ]
                    },
                    '🌿 Phytoépuration': {
                        'icone': '🌿',
                        'sous_sous_categories': [
                            {'nom': 'Station phytoépuration individuelle', 'icone': '🏡'},
                            {'nom': 'Filtre planté de roseaux', 'icone': '🌾'},
                        ]
                    },
                    '☔ Récupération Eau de Pluie': {
                        'icone': '☔',
                        'sous_sous_categories': [
                            {'nom': 'Cuve enterrée', 'icone': '⬇️'},
                            {'nom': 'Cuve aérienne', 'icone': '🛢️'},
                            {'nom': 'Système de filtration', 'icone': '🔄'},
                        ]
                    },
                }
            },

            '🌱 Autonomie Alimentaire': {
                'description': 'Production locale et autosuffisance',
                'icone': '🌱',
                'couleur': '#388E3C',
                'priorite': 5,
                'visible_home': True,
                'sous_categories': {
                    '🥕 Potager & Permaculture': {
                        'icone': '🥕',
                        'sous_sous_categories': [
                            {'nom': 'Kit potager surélevé', 'icone': '📦'},
                            {'nom': 'Composteur', 'icone': '♻️'},
                            {'nom': 'Outils de jardinage', 'icone': '🔧'},
                        ]
                    },
                    '🌳 Verger Fruitiers': {
                        'icone': '🌳',
                        'sous_sous_categories': [
                            {'nom': 'Pommiers anciens', 'icone': '🍎'},
                            {'nom': 'Poiriers locaux', 'icone': '🍐'},
                            {'nom': 'Petits fruits', 'icone': '🍓'},
                        ]
                    },
                    '🐝 Apiculture': {
                        'icone': '🐝',
                        'sous_sous_categories': [
                            {'nom': 'Ruche complète', 'icone': '🏠'},
                            {'nom': 'Essaim d\'abeilles', 'icone': '🐝'},
                            {'nom': 'Matériel apiculteur', 'icone': '🧤'},
                        ]
                    },
                    '🏡 Serre Bioclimatique': {
                        'icone': '🏡',
                        'sous_sous_categories': [
                            {'nom': 'Serre tunnel', 'icone': '🏗️'},
                            {'nom': 'Serre adossée', 'icone': '🏠'},
                            {'nom': 'Mini-serre urbaine', 'icone': '🏙️'},
                        ]
                    },
                }
            },

            '🌿 Plantes & Végétaux': {
                'description': 'Plants, semences et végétaux premium',
                'icone': '🌿',
                'couleur': '#4CAF50',
                'priorite': 6,
                'visible_home': True,
                'sous_categories': {
                    '🌱 Semences Paysannes': {
                        'icone': '🌱',
                        'sous_sous_categories': [
                            {'nom': 'Légumes anciens', 'icone': '🥬'},
                            {'nom': 'Aromatiques', 'icone': '🌿'},
                            {'nom': 'Fleurs mellifères', 'icone': '🌸'},
                        ]
                    },
                    '🌳 Arbres & Arbustes': {
                        'icone': '🌳',
                        'sous_sous_categories': [
                            {'nom': 'Arbres fruitiers', 'icone': '🍎'},
                            {'nom': 'Haie champêtre', 'icone': '🌿'},
                            {'nom': 'Arbres d\'ornement', 'icone': '🌲'},
                        ]
                    },
                }
            },

            '🎨 Artisanat Local Premium': {
                'description': 'Créations artisanales d\'exception',
                'icone': '🎨',
                'couleur': '#9C27B0',
                'priorite': 7,
                'visible_home': True,
                'sous_categories': {
                    '🪑 Mobilier Artisanal': {
                        'icone': '🪑',
                        'sous_sous_categories': [
                            {'nom': 'Table bois massif', 'icone': '🪵'},
                            {'nom': 'Chaise artisanale', 'icone': '🪑'},
                            {'nom': 'Meuble sur-mesure', 'icone': '🎯'},
                        ]
                    },
                    '🏺 Céramique & Poterie': {
                        'icone': '🏺',
                        'sous_sous_categories': [
                            {'nom': 'Vaisselle artisanale', 'icone': '🍽️'},
                            {'nom': 'Décoration céramique', 'icone': '🎨'},
                        ]
                    },
                    '🧺 Vannerie': {
                        'icone': '🧺',
                        'sous_sous_categories': [
                            {'nom': 'Paniers osier', 'icone': '🧺'},
                            {'nom': 'Mobilier tressé', 'icone': '🪑'},
                        ]
                    },
                }
            },

            '🍷 Gastronomie du Terroir': {
                'description': 'Produits gourmets d\'exception',
                'icone': '🍷',
                'couleur': '#D32F2F',
                'priorite': 8,
                'visible_home': True,
                'sous_categories': {
                    '🍷 Vins & Spiritueux': {
                        'icone': '🍷',
                        'sous_sous_categories': [
                            {'nom': 'Vin biodynamique', 'icone': '🍇'},
                            {'nom': 'Cidre artisanal', 'icone': '🍎'},
                            {'nom': 'Bière craft', 'icone': '🍺'},
                        ]
                    },
                    '🧀 Fromages Fermiers': {
                        'icone': '🧀',
                        'sous_sous_categories': [
                            {'nom': 'Fromage de chèvre', 'icone': '🐐'},
                            {'nom': 'Fromage de brebis', 'icone': '🐑'},
                            {'nom': 'Fromage de vache', 'icone': '🐄'},
                        ]
                    },
                    '🍯 Miel & Produits Ruche': {
                        'icone': '🍯',
                        'sous_sous_categories': [
                            {'nom': 'Miel toutes fleurs', 'icone': '🌸'},
                            {'nom': 'Miel de lavande', 'icone': '💜'},
                            {'nom': 'Propolis', 'icone': '💊'},
                        ]
                    },
                }
            },

            '🌍 Expérience & Proximité': {
                'description': 'Ateliers, formations et services locaux',
                'icone': '🌍',
                'couleur': '#00796B',
                'priorite': 9,
                'visible_home': False,
                'sous_categories': {
                    '👨‍🏫 Formations': {
                        'icone': '👨‍🏫',
                        'sous_sous_categories': [
                            {'nom': 'Stage permaculture', 'icone': '🌱'},
                            {'nom': 'Formation apiculture', 'icone': '🐝'},
                            {'nom': 'Atelier construction bois', 'icone': '🪵'},
                        ]
                    },
                    '🛠️ Services Locaux': {
                        'icone': '🛠️',
                        'sous_sous_categories': [
                            {'nom': 'Installation solaire', 'icone': '☀️'},
                            {'nom': 'Conseil habitat écologique', 'icone': '🏡'},
                        ]
                    },
                }
            },
        }

        stats = {
            'categories': 0,
            'sous_categories': 0,
            'sous_sous_categories': 0,
        }

        for cat_nom, cat_data in categories_data.items():
            try:
                with transaction.atomic():
                    if dry_run:
                        self.stdout.write(f'[DRY-RUN] Catégorie: {cat_nom}')
                        stats['categories'] += 1
                    else:
                        if update:
                            categorie, created = Categorie.objects.update_or_create(
                                nom=cat_nom,
                                defaults={
                                    'slug': slugify(cat_nom),
                                    'description': cat_data.get('description', ''),
                                    'icone': cat_data.get('icone', ''),
                                    'descripteurs': cat_data.get('descripteurs', {}),
                                    'ordre': cat_data.get('priorite', 0),
                                    'est_active': True,
                                }
                            )
                        else:
                            categorie, created = Categorie.objects.get_or_create(
                                nom=cat_nom,
                                defaults={
                                    'slug': slugify(cat_nom),
                                    'description': cat_data.get('description', ''),
                                    'icone': cat_data.get('icone', ''),
                                    'descripteurs': cat_data.get('descripteurs', {}),
                                    'ordre': cat_data.get('priorite', 0),
                                    'est_active': True,
                                }
                            )

                        action = '✨ Créée' if created else '♻️  Existante'
                        self.stdout.write(
                            self.style.SUCCESS(f'{action} Catégorie: {cat_nom}')
                        )
                        stats['categories'] += 1

                    # Sous-catégories
                    for scat_nom, scat_data in cat_data.get('sous_categories', {}).items():
                        if dry_run:
                            self.stdout.write(f'  [DRY-RUN] Sous-catégorie: {scat_nom}')
                            stats['sous_categories'] += 1
                        else:
                            if update:
                                sous_cat, created = SousCategorie.objects.update_or_create(
                                    nom=scat_nom,
                                    categorie=categorie,
                                    defaults={
                                        'slug': slugify(scat_nom),
                                        'icone': scat_data.get('icone', ''),
                                    }
                                )
                            else:
                                sous_cat, created = SousCategorie.objects.get_or_create(
                                    nom=scat_nom,
                                    categorie=categorie,
                                    defaults={
                                        'slug': slugify(scat_nom),
                                        'icone': scat_data.get('icone', ''),
                                    }
                                )

                            action = '  ✨' if created else '  ♻️ '
                            self.stdout.write(f'{action} {scat_nom}')
                            stats['sous_categories'] += 1

                        # Sous-sous-catégories
                        for sscat_data in scat_data.get('sous_sous_categories', []):
                            sscat_nom = sscat_data['nom']
                            if dry_run:
                                self.stdout.write(f'    [DRY-RUN] {sscat_nom}')
                                stats['sous_sous_categories'] += 1
                            else:
                                if update:
                                    ss_cat, created = SousSousCategorie.objects.update_or_create(
                                        nom=sscat_nom,
                                        souscategorie=sous_cat,
                                        defaults={
                                            'slug': slugify(sscat_nom),
                                            'icone': sscat_data.get('icone', ''),
                                        }
                                    )
                                else:
                                    ss_cat, created = SousSousCategorie.objects.get_or_create(
                                        nom=sscat_nom,
                                        souscategorie=sous_cat,
                                        defaults={
                                            'slug': slugify(sscat_nom),
                                            'icone': sscat_data.get('icone', ''),
                                        }
                                    )

                                action = '    ✨' if created else '    ♻️ '
                                self.stdout.write(f'{action} {sscat_nom}')
                                stats['sous_sous_categories'] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur sur {cat_nom}: {str(e)}')
                )
                continue

        return stats

    def _creer_fournisseurs(self, nombre, dry_run):
        """Crée les fournisseurs cohérents avec les catégories"""

        noms = [
            'Dubois', 'Martin', 'Bernard', 'Thomas', 'Robert', 'Petit', 'Richard',
            'Durand', 'Leroy', 'Moreau', 'Simon', 'Laurent', 'Lefebvre', 'Michel',
            'Garcia', 'David', 'Bertrand', 'Roux', 'Vincent', 'Fournier', 'Morel',
            'Girard', 'Andre', 'Lefevre', 'Mercier', 'Blanc', 'Guerin', 'Boyer',
            'Garnier', 'Chevalier', 'François', 'Legrand', 'Gauthier', 'Rousseau',
        ]

        prenoms = [
            'Pierre', 'Sophie', 'Jean', 'Marie', 'Luc', 'Claire', 'Antoine',
            'Camille', 'François', 'Julie', 'Philippe', 'Isabelle', 'Nicolas',
            'Élise', 'Laurent', 'Nathalie', 'Thierry', 'Valérie', 'Olivier',
            'Sandrine', 'Éric', 'Céline', 'Patrick', 'Sylvie', 'Alain', 'Catherine',
        ]

        # Métiers cohérents avec nos catégories La Providence
        metiers = [
            # Habitat Autonome Premium
            'Constructeur de maisons passives',
            'Créateur de Tiny Houses',
            'Architecte bioclimatique',
            'Éco-rénovateur certifié',
            'Constructeur bois local',
            'Maçon écologique',

            # Matériaux Nobles
            'Scierie bois massif',
            'Chanvrier transformateur',
            'Carrier pierre naturelle',
            'Métallier forgeron',
            'Fournisseur matériaux biosourcés',

            # Énergie Autonome
            'Installateur solaire certifié RGE',
            'Fabricant batteries lithium',
            'Installateur éolien',
            'Artisan poêlier',
            'Expert domotique énergétique',

            # Eau et Traitement
            'Spécialiste filtration eau',
            'Installateur phytoépuration',
            'Concepteur récupération eau',

            # Autonomie Alimentaire
            'Maraîcher bio & permaculture',
            'Pépiniériste fruitiers anciens',
            'Apiculteur professionnel',
            'Fabricant serres bioclimatiques',
            'Artisan outils de jardin',

            # Plantes & Végétaux
            'Semencier variétés anciennes',
            'Pépiniériste arbres locaux',
            'Producteur plants aromatiques',

            # Artisanat Local
            'Menuisier ébéniste',
            'Potier céramiste',
            'Artisan vannier',
            'Tisserand textile naturel',
            'Maroquinier',

            # Gastronomie
            'Viticulteur biodynamique',
            'Fromager fermier',
            'Brasseur artisanal',
            'Chocolatier bean-to-bar',
            'Apiculteur miel premium',
            'Torréfacteur café',
        ]

        villes = [
            ('Paris', '75001', 48.8566, 2.3522),
            ('Lyon', '69000', 45.7640, 4.8357),
            ('Marseille', '13000', 43.2965, 5.3698),
            ('Toulouse', '31000', 43.6047, 1.4442),
            ('Nice', '06000', 43.7102, 7.2620),
            ('Nantes', '44000', 47.2184, -1.5536),
            ('Strasbourg', '67000', 48.5734, 7.7521),
            ('Montpellier', '34000', 43.6108, 3.8767),
            ('Bordeaux', '33000', 44.8378, -0.5792),
            ('Lille', '59000', 50.6292, 3.0573),
            ('Rennes', '35000', 48.1173, -1.6778),
            ('Reims', '51100', 49.2583, 4.0317),
            ('Le Havre', '76600', 49.4944, 0.1079),
            ('Saint-Étienne', '42000', 45.4397, 4.3872),
            ('Toulon', '83000', 43.1242, 5.9280),
            ('Grenoble', '38000', 45.1885, 5.7245),
            ('Dijon', '21000', 47.3220, 5.0415),
            ('Angers', '49000', 47.4784, -0.5632),
            ('Nîmes', '30000', 43.8367, 4.3601),
            ('Villeurbanne', '69100', 45.7667, 4.8833),
        ]

        types_production = ['bio', 'biodynamie', 'permaculture', 'artisanal', 'traditionnel', 'autre']
        zones_livraison = ['rayon', 'departements', 'villes', 'national']

        certifications_list = [
            'AB Agriculture Biologique',
            'Label Rouge',
            'AOP Appellation Origine Protégée',
            'Demeter (Biodynamie)',
            'RGE Reconnu Garant Environnement',
            'Passivhaus',
            'PEFC',
            'FSC',
            'Artisan d\'Art',
            'Maître Artisan',
            'Nature & Progrès',
        ]

        descriptions_templates = [
            "Artisan passionné depuis {exp} ans, spécialisé dans {metier}.",
            "Expert reconnu en {metier}, avec {exp} années d'expérience.",
            "Créateur innovant proposant des solutions uniques en {metier}.",
            "Professionnel certifié offrant des produits d'exception en {metier}.",
        ]

        fournisseurs_crees = 0

        for i in range(nombre):
            try:
                with transaction.atomic():
                    nom = random.choice(noms)
                    prenom = random.choice(prenoms)
                    metier = random.choice(metiers)
                    ville_data = random.choice(villes)
                    ville, code_postal, lat, lon = ville_data

                    # Email unique
                    base_email = f"{prenom.lower()}.{nom.lower()}"
                    domain = metier.split()[0].lower().replace('é', 'e').replace('è', 'e')
                    email = f"{base_email}{i}@{domain}.fr"

                    if not dry_run and Fournisseur.objects.filter(email=email).exists():
                        continue

                    # Zone de livraison
                    zone_type = random.choice(zones_livraison)
                    rayon_km = None
                    dept_livraison = ''
                    villes_livraison = ''

                    if zone_type == 'rayon':
                        rayon_km = random.choice([50, 100, 150, 200, 300])
                    elif zone_type == 'departements':
                        depts = random.sample(range(1, 96), random.randint(3, 6))
                        dept_livraison = ', '.join([f"{d:02d}" for d in sorted(depts)])
                    elif zone_type == 'villes':
                        villes_echantillon = random.sample(villes, min(random.randint(5, 10), len(villes)))
                        villes_livraison = ', '.join([v[0] for v in villes_echantillon])

                    # Frais de livraison (jamais None)
                    frais_base = Decimal(random.choice([50, 100, 150, 200, 250, 300]))

                    if zone_type == 'rayon':
                        frais_par_km = Decimal(random.choice(['0.50', '1.00', '1.50', '2.00', '2.50']))
                    else:
                        frais_par_km = Decimal('0.00')

                    # Montants limités à 9999.99
                    livraison_gratuite = Decimal(random.choice([500, 1000, 1500, 2000, 3000, 5000, 8000, 9000]))

                    delai_livraison = random.choice([1, 2, 3, 5, 7, 10, 14, 21, 30, 60, 90])
                    jours_livraison = random.choice([
                        'Lundi au Vendredi',
                        'Du lundi au samedi',
                        'Tous les jours',
                        'Sur rendez-vous',
                    ])

                    experience = random.randint(3, 40)
                    nb_certif = random.randint(1, 3)
                    certifications = ', '.join(random.sample(certifications_list, nb_certif))
                    description = random.choice(descriptions_templates).format(
                        exp=experience,
                        metier=metier.lower()
                    )
                    type_prod = random.choice(types_production)

                    engagement = random.choice([
                        'Circuits courts exclusifs',
                        'Zéro déchet',
                        'Énergie 100% renouvelable',
                        'Matériaux locaux uniquement',
                        'Production artisanale française',
                    ])

                    produits = f'Solutions professionnelles en {metier.lower()}'

                    if dry_run:
                        self.stdout.write(
                            f'[DRY-RUN] {prenom} {nom} ({metier}) à {ville}'
                        )
                        fournisseurs_crees += 1
                    else:
                        # Créer le fournisseur
                        fournisseur = Fournisseur.objects.create(
                            nom=nom,
                            prenom=prenom,
                            password=make_password('DefaultPassword123!'),
                            email=email,
                            metier=metier,
                            contact=f"{prenom} {nom}",
                            tel=f"+336{random.randint(10000000, 99999999)}",
                            adresse=f"{random.randint(1, 150)} {random.choice(['Rue', 'Avenue', 'Chemin', 'Route'])} {random.choice(['du Commerce', 'de la Gare', 'du Moulin', 'des Artisans'])}",
                            code_postal=code_postal,
                            ville=ville,
                            pays='France',
                            latitude=lat + random.uniform(-0.1, 0.1),
                            longitude=lon + random.uniform(-0.1, 0.1),
                            zone_livraison_type=zone_type,
                            rayon_livraison_km=rayon_km,
                            departements_livraison=dept_livraison,
                            villes_livraison=villes_livraison,
                            frais_livraison_base=frais_base,
                            frais_livraison_par_km=frais_par_km,
                            livraison_gratuite_montant=livraison_gratuite,
                            delai_livraison_jours=delai_livraison,
                            jours_livraison=jours_livraison,
                            description=description,
                            type_production=type_prod,
                            experience_annees=experience,
                            certifications=certifications,
                            engagement_ecologique=engagement,
                            produits_principaux=produits,
                        )

                        fournisseurs_crees += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ {fournisseurs_crees}/{nombre} - {prenom} {nom} ({metier}) créé à {ville}'
                            )
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur : {str(e)}')
                )
                continue

        return fournisseurs_crees
