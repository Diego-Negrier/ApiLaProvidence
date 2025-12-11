# produits/management/commands/create_categories_improved.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from produits.models import Categorie, SousCategorie, SousSousCategorie
from typing import Dict, Any, List


class Command(BaseCommand):
    help = 'Crée une hiérarchie complète et enrichie des catégories pour La Providence'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Mettre à jour les catégories existantes au lieu de les ignorer',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler l\'exécution sans créer les données',
        )

    def handle(self, *args, **options):
        update_existing = options['update']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODE SIMULATION - Aucune donnée ne sera créée'))

        self.stdout.write(self.style.SUCCESS('🏡 Création des catégories La Providence...'))

        # ===================================
        # STRUCTURE COMPLÈTE AMÉLIORÉE
        # ===================================
        categories_data = {
            '🏡 Habitat Autonome Premium': {
                'description': 'Habitat écologique, autonome et de prestige',
                'icone': '🏡',
                'couleur': '#2E7D32',  # Vert foncé
                'priorite': 1,
                'visible_home': True,
                'descripteurs': {
                    'certification': ['Passivhaus', 'BEPOS', 'HQE', 'E+C-', 'BBC'],
                    'surface': ['< 50m²', '50-100m²', '100-200m²', '200-300m²', '300m²+'],
                    'zone_climatique': ['H1', 'H2', 'H3'],
                    'terrain': ['Plat', 'Pente', 'Montagne', 'Bord de mer'],
                },
                'sous_categories': {
                    '🏠 Maisons Passives': {
                        'description': 'Maisons à très haute performance énergétique',
                        'icone': '🏠',
                        'descripteurs': {
                            'besoin_chauffage': ['< 15 kWh/m²/an'],
                            'etancheite': ['n50 < 0.6'],
                            'type': ['Plain-pied', 'Étage', 'Multi-niveaux'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Maison passive sur-mesure', 'icone': '🎯'},
                            {'nom': 'Kit maison passive', 'icone': '📦'},
                            {'nom': 'Extension passive', 'icone': '➕'},
                        ]
                    },
                    '🏘️ Villas Autonomes': {
                        'description': 'Villas haut de gamme autonomes en énergie',
                        'icone': '🏘️',
                        'descripteurs': {
                            'standing': ['Premium', 'Luxe', 'Prestige'],
                            'autonomie': ['50%', '75%', '100%'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Villa contemporaine autonome', 'icone': '🏛️'},
                            {'nom': 'Villa traditionnelle rénovée', 'icone': '🏚️'},
                            {'nom': 'Villa bioclimatique', 'icone': '🌡️'},
                        ]
                    },
                    '🌿 Architecture Écologique': {
                        'description': 'Conception architecturale durable et respectueuse',
                        'icone': '🌿',
                        'descripteurs': {
                            'style': ['Contemporain', 'Traditionnel', 'Moderne', 'Bioclimatique'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Maison bois massif', 'icone': '🪵'},
                            {'nom': 'Maison paille/terre', 'icone': '🌾'},
                            {'nom': 'Maison pierres', 'icone': '🪨'},
                        ]
                    },
                    '🏕️ Tiny House Luxe': {
                        'description': 'Habitat compact de haute qualité',
                        'icone': '🏕️',
                        'descripteurs': {
                            'mobilite': ['Mobile', 'Fixe', 'Semi-mobile'],
                            'surface': ['< 20m²', '20-30m²', '30-40m²'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Tiny house sur-mesure', 'icone': '🎨'},
                            {'nom': 'Tiny house modulaire', 'icone': '🧩'},
                            {'nom': 'Studio de jardin', 'icone': '🌳'},
                        ]
                    },
                }
            },

            '🌳 Matériaux Nobles et Locaux': {
                'description': 'Matériaux naturels, durables et de proximité',
                'icone': '🌳',
                'couleur': '#6D4C41',  # Marron bois
                'priorite': 2,
                'visible_home': True,
                'descripteurs': {
                    'provenance': ['< 50km', '< 100km', '< 200km', 'France'],
                    'certification': ['PEFC', 'FSC', 'AB', 'Nature Plus'],
                    'transformation': ['Brut', 'Semi-fini', 'Fini'],
                },
                'sous_categories': {
                    '🪵 Bois Massif Local': {
                        'description': 'Bois de la région, première transformation locale',
                        'icone': '🪵',
                        'descripteurs': {
                            'essence': ['Chêne', 'Châtaignier', 'Douglas', 'Mélèze', 'Épicéa'],
                            'usage': ['Structure', 'Menuiserie', 'Bardage', 'Charpente'],
                            'humidite': ['Vert', 'Sec air', 'Sec étuve'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Chêne français massif', 'icone': '🌰'},
                            {'nom': 'Douglas régional', 'icone': '🌲'},
                            {'nom': 'Châtaignier local', 'icone': '🥜'},
                        ]
                    },
                    '🌾 Chanvre Français': {
                        'description': 'Chanvre cultivé et transformé en France',
                        'icone': '🌾',
                        'descripteurs': {
                            'usage': ['Isolation', 'Enduit', 'Béton', 'Laine'],
                            'forme': ['Vrac', 'Panneau', 'Rouleau', 'Bloc'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Laine de chanvre', 'icone': '🧶'},
                            {'nom': 'Béton de chanvre', 'icone': '🧱'},
                            {'nom': 'Enduit chanvre-chaux', 'icone': '🎨'},
                        ]
                    },
                    '🏺 Terre Crue': {
                        'description': 'Terre locale non cuite, pisé, adobe',
                        'icone': '🏺',
                        'descripteurs': {
                            'technique': ['Pisé', 'Adobe', 'Bauge', 'Torchis'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Terre à pisé', 'icone': '🏔️'},
                            {'nom': 'Briques adobe', 'icone': '🧱'},
                            {'nom': 'Enduit terre', 'icone': '🖌️'},
                        ]
                    },
                    '🪨 Pierre Naturelle': {
                        'description': 'Pierres de carrières locales',
                        'icone': '🪨',
                        'descripteurs': {
                            'type': ['Calcaire', 'Granit', 'Grès', 'Schiste'],
                            'finition': ['Brute', 'Taillée', 'Polie'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Pierre de taille locale', 'icone': '🏛️'},
                            {'nom': 'Lauze traditionnelle', 'icone': '🏔️'},
                            {'nom': 'Granit régional', 'icone': '💎'},
                        ]
                    },
                }
            },

            '⚡ Énergie Autonome': {
                'description': 'Solutions pour l\'autonomie énergétique',
                'icone': '⚡',
                'couleur': '#FFB300',  # Jaune or
                'priorite': 3,
                'visible_home': True,
                'descripteurs': {
                    'puissance': ['< 3kW', '3-6kW', '6-9kW', '9-12kW', '12kW+'],
                    'taux_autonomie': ['30-50%', '50-75%', '75-90%', '90-100%'],
                    'type_installation': ['Autoconsommation', 'Revente surplus', 'Autonome'],
                },
                'sous_categories': {
                    '☀️ Solaire Premium': {
                        'description': 'Panneaux photovoltaïques haut rendement',
                        'icone': '☀️',
                        'descripteurs': {
                            'technologie': ['Monocristallin', 'Bifacial', 'Back-contact'],
                            'rendement': ['18-20%', '20-22%', '22%+'],
                            'garantie': ['10 ans', '20 ans', '25 ans'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Panneaux solaires premium', 'icone': '🌟'},
                            {'nom': 'Tuiles solaires intégrées', 'icone': '🏠'},
                            {'nom': 'Ombrières solaires', 'icone': '☂️'},
                        ]
                    },
                    '🔋 Batteries Intelligentes': {
                        'description': 'Stockage d\'énergie nouvelle génération',
                        'icone': '🔋',
                        'descripteurs': {
                            'technologie': ['Lithium-ion', 'LiFePO4', 'Flow battery'],
                            'capacite': ['5-10 kWh', '10-15 kWh', '15-20 kWh', '20+ kWh'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Batterie lithium domestique', 'icone': '🏡'},
                            {'nom': 'Batterie virtuelle', 'icone': '☁️'},
                            {'nom': 'Power wall', 'icone': '🧱'},
                        ]
                    },
                    '🔥 Poêles Haut Rendement': {
                        'description': 'Chauffage au bois haute performance',
                        'icone': '🔥',
                        'descripteurs': {
                            'rendement': ['75-85%', '85-90%', '90%+'],
                            'type': ['Bûches', 'Granulés', 'Mixte'],
                            'puissance': ['5-8kW', '8-12kW', '12-15kW'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Poêle à bois suspendu', 'icone': '🎪'},
                            {'nom': 'Poêle à granulés silencieux', 'icone': '🤫'},
                            {'nom': 'Poêle de masse artisanal', 'icone': '🏺'},
                        ]
                    },
                }
            },

            '💧 Eau et Traitement Local': {
                'description': 'Gestion autonome et traitement de l\'eau',
                'icone': '💧',
                'couleur': '#0288D1',  # Bleu eau
                'priorite': 4,
                'visible_home': True,
                'descripteurs': {
                    'debit': ['< 1m³/j', '1-3m³/j', '3-5m³/j', '5m³/j+'],
                    'usage': ['Potable', 'Sanitaire', 'Arrosage', 'Tous usages'],
                },
                'sous_categories': {
                    '🔬 Filtration Haut de Gamme': {
                        'description': 'Systèmes de filtration avancés',
                        'icone': '🔬',
                        'descripteurs': {
                            'technologie': ['Charbon actif', 'Céramique', 'UV', 'Multi-étages'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Filtre sous-évier premium', 'icone': '🚰'},
                            {'nom': 'Station filtration maison', 'icone': '🏠'},
                            {'nom': 'Filtre gravitaire design', 'icone': '💎'},
                        ]
                    },
                    '🌧️ Récupération d\'Eau': {
                        'description': 'Collecte et stockage eau de pluie',
                        'icone': '🌧️',
                        'descripteurs': {
                            'capacite': ['500-1000L', '1000-3000L', '3000-5000L', '5000L+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Cuve enterrée', 'icone': '⬇️'},
                            {'nom': 'Réservoir hors-sol design', 'icone': '🎨'},
                            {'nom': 'Citerne souple', 'icone': '🎈'},
                        ]
                    },
                }
            },

            '🌱 Autonomie Alimentaire': {
                'description': 'Produire son alimentation locale et saine',
                'icone': '🌱',
                'couleur': '#388E3C',  # Vert printemps
                'priorite': 5,
                'visible_home': True,
                'descripteurs': {
                    'saison': ['Printemps', 'Été', 'Automne', 'Hiver', 'Toute saison'],
                    'niveau': ['Débutant', 'Intermédiaire', 'Expert'],
                },
                'sous_categories': {
                    '🥬 Potagers Terroir': {
                        'description': 'Potagers productifs et esthétiques',
                        'icone': '🥬',
                        'descripteurs': {
                            'type': ['Carré', 'Ligne', 'Permaculture', 'Mandala'],
                            'surface': ['< 20m²', '20-50m²', '50-100m²', '100m²+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Carré potager surélevé', 'icone': '📦'},
                            {'nom': 'Potager permaculture', 'icone': '🌀'},
                            {'nom': 'Potager urbain', 'icone': '🏙️'},
                        ]
                    },
                    '🏡 Serres Premium': {
                        'description': 'Serres de culture haut de gamme',
                        'icone': '🏡',
                        'descripteurs': {
                            'materiau': ['Verre', 'Polycarbonate', 'Mixte'],
                            'surface': ['< 10m²', '10-20m²', '20-30m²', '30m²+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Serre verre et bois', 'icone': '✨'},
                            {'nom': 'Serre tunnel pro', 'icone': '🎪'},
                            {'nom': 'Serre bioclimatique', 'icone': '🌡️'},
                        ]
                    },
                    '🍎 Verger Régional': {
                        'description': 'Arbres fruitiers adaptés au climat local',
                        'icone': '🍎',
                        'sous_sous_categories': [
                            {'nom': 'Pommiers haute tige', 'icone': '🍏'},
                            {'nom': 'Poiriers anciens', 'icone': '🍐'},
                            {'nom': 'Fruitiers basse tige', 'icone': '🌳'},
                        ]
                    },
                    '🐝 Ruches Locales': {
                        'description': 'Apiculture naturelle',
                        'icone': '🐝',
                        'sous_sous_categories': [
                            {'nom': 'Ruche Warré', 'icone': '📦'},
                            {'nom': 'Ruche Dadant', 'icone': '🏠'},
                            {'nom': 'Ruche horizontale', 'icone': '➡️'},
                        ]
                    },
                }
            },

            '🌿 Plantes & Végétaux': {
                'description': 'Plantes, arbres et végétaux pour l\'autonomie',
                'icone': '🌿',
                'couleur': '#4CAF50',  # Vert végétal
                'priorite': 6,
                'visible_home': True,
                'descripteurs': {
                    'type_culture': ['Bio', 'Biodynamie', 'Permaculture', 'Naturel'],
                    'provenance': ['Local', 'Régional', 'France'],
                    'conditionnement': ['Graine', 'Plant', 'Pot', 'Motte', 'Racine nue'],
                },
                'sous_categories': {
                    '🌾 Semences Anciennes': {
                        'description': 'Graines anciennes et variétés paysannes',
                        'icone': '🌾',
                        'descripteurs': {
                            'type': ['Reproductible', 'Non hybride', 'Patrimoine'],
                            'conservation': ['Court terme', 'Moyen terme', 'Long terme'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Graines anciennes certifiées', 'icone': '✅'},
                            {'nom': 'Variétés paysannes', 'icone': '👨‍🌾'},
                            {'nom': 'Semences reproductibles', 'icone': '♻️'},
                            {'nom': 'Variétés locales du terroir', 'icone': '🏡'},
                            {'nom': 'Patrimoine végétal', 'icone': '🏛️'},
                        ]
                    },
                    '🥕 Légumes Anciens': {
                        'description': 'Légumes traditionnels et variétés oubliées',
                        'icone': '🥕',
                        'descripteurs': {
                            'saison': ['Printemps', 'Été', 'Automne', 'Hiver'],
                            'difficulte': ['Facile', 'Moyen', 'Expert'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Tomates anciennes', 'icone': '🍅'},
                            {'nom': 'Courges anciennes', 'icone': '🎃'},
                            {'nom': 'Haricots patrimoine', 'icone': '🫘'},
                            {'nom': 'Légumes oubliés', 'icone': '🌿'},
                            {'nom': 'Salades anciennes', 'icone': '🥬'},
                        ]
                    },
                    '🌿 Aromatiques Régionales': {
                        'description': 'Herbes aromatiques du terroir',
                        'icone': '🌿',
                        'descripteurs': {
                            'usage': ['Cuisine', 'Tisane', 'Médicinal', 'Décoratif'],
                            'exposition': ['Plein soleil', 'Mi-ombre', 'Ombre'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Thym ancien', 'icone': '🌿'},
                            {'nom': 'Basilic ancien', 'icone': '🍃'},
                            {'nom': 'Romarin terroir', 'icone': '🌲'},
                            {'nom': 'Menthe paysanne', 'icone': '🍃'},
                            {'nom': 'Lavande locale', 'icone': '💜'},
                        ]
                    },
                }
            },

            '🎨 Artisanat Local Premium': {
                'description': 'Créations artisanales par des artisans du territoire',
                'icone': '🎨',
                'couleur': '#9C27B0',  # Violet artisanat
                'priorite': 7,
                'visible_home': True,
                'descripteurs': {
                    'provenance': ['< 20km', '< 50km', '< 100km'],
                    'type_artisan': ['Artisan d\'art', 'Maître artisan', 'MOF'],
                    'materiau_principal': ['Bois', 'Métal', 'Terre', 'Textile', 'Cuir'],
                },
                'sous_categories': {
                    '🪚 Menuiserie': {
                        'description': 'Créations bois sur-mesure',
                        'icone': '🪚',
                        'sous_sous_categories': [
                            {'nom': 'Meubles sur-mesure', 'icone': '🪑'},
                            {'nom': 'Agencement intérieur', 'icone': '🏠'},
                            {'nom': 'Escaliers bois', 'icone': '🪜'},
                        ]
                    },
                    '⚒️ Métallerie': {
                        'description': 'Ferronnerie et métallerie d\'art',
                        'icone': '⚒️',
                        'sous_sous_categories': [
                            {'nom': 'Garde-corps artisanal', 'icone': '🛡️'},
                            {'nom': 'Portails forgés', 'icone': '🚪'},
                            {'nom': 'Luminaires métal', 'icone': '💡'},
                        ]
                    },
                    '🏺 Céramique': {
                        'description': 'Poterie et céramique artisanale',
                        'icone': '🏺',
                        'sous_sous_categories': [
                            {'nom': 'Vaisselle artisanale', 'icone': '🍽️'},
                            {'nom': 'Carrelage artisanal', 'icone': '⬜'},
                            {'nom': 'Objets déco céramique', 'icone': '🎨'},
                        ]
                    },
                }
            },

            '🍷 Gastronomie du Terroir': {
                'description': 'Produits gastronomiques d\'exception',
                'icone': '🍷',
                'couleur': '#D32F2F',  # Rouge vin
                'priorite': 8,
                'visible_home': True,
                'descripteurs': {
                    'label': ['AB', 'AOP', 'IGP', 'Label Rouge', 'Nature & Progrès'],
                    'provenance': ['< 20km', '< 50km', '< 100km', 'Région'],
                    'conservation': ['Frais', 'Conserve', 'Sec', 'Réfrigéré'],
                },
                'sous_categories': {
                    '🍷 Vins Régionaux': {
                        'description': 'Vins de vignerons locaux',
                        'icone': '🍷',
                        'descripteurs': {
                            'type': ['Rouge', 'Blanc', 'Rosé', 'Effervescent'],
                            'culture': ['Bio', 'Biodynamie', 'Nature', 'Raisonnée'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Vins bio locaux', 'icone': '🌱'},
                            {'nom': 'Vins nature terroir', 'icone': '🍇'},
                            {'nom': 'Vins biodynamiques', 'icone': '🌙'},
                            {'nom': 'Cuvées prestige', 'icone': '👑'},
                        ]
                    },
                    '🧀 Fromageries Fermes': {
                        'description': 'Fromages fermiers au lait cru',
                        'icone': '🧀',
                        'descripteurs': {
                            'lait': ['Vache', 'Chèvre', 'Brebis', 'Mixte'],
                            'pate': ['Molle', 'Pressée', 'Persillée'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Fromages au lait cru', 'icone': '🥛'},
                            {'nom': 'Tommes fermières', 'icone': '🧀'},
                            {'nom': 'Fromages affinés', 'icone': '🕰️'},
                        ]
                    },
                    '🍯 Miel Premium': {
                        'description': 'Miels d\'apiculteurs locaux',
                        'icone': '🍯',
                        'descripteurs': {
                            'type': ['Toutes fleurs', 'Acacia', 'Châtaignier', 'Lavande'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Miel de fleurs', 'icone': '🌸'},
                            {'nom': 'Miel de forêt', 'icone': '🌲'},
                            {'nom': 'Miel rare', 'icone': '💎'},
                        ]
                    },
                }
            },

            '🌍 Expérience & Proximité': {
                'description': 'Rencontres, découvertes et expériences locales',
                'icone': '🌍',
                'couleur': '#00796B',  # Vert turquoise
                'priorite': 9,
                'visible_home': False,
                'descripteurs': {
                    'type_experience': ['Visite', 'Atelier', 'Dégustation', 'Formation'],
                    'duree': ['1-2h', '1/2 journée', 'Journée', 'Week-end'],
                    'public': ['Adulte', 'Famille', 'Enfant', 'Groupe'],
                },
                'sous_categories': {
                    '🚜 Circuit Court': {
                        'description': 'Achat direct producteur',
                        'icone': '🚜',
                        'sous_sous_categories': [
                            {'nom': 'Vente à la ferme', 'icone': '🏡'},
                            {'nom': 'Paniers producteurs', 'icone': '🧺'},
                            {'nom': 'AMAP locales', 'icone': '🤝'},
                        ]
                    },
                    '👨‍🌾 Rencontre Producteurs': {
                        'description': 'Échanges avec artisans et producteurs',
                        'icone': '👨‍🌾',
                        'sous_sous_categories': [
                            {'nom': 'Visite ferme', 'icone': '🐄'},
                            {'nom': 'Rencontre vigneron', 'icone': '🍇'},
                            {'nom': 'Visite atelier artisan', 'icone': '🔨'},
                        ]
                    },
                }
            },
        }

        # ===================================
        # CRÉATION DES CATÉGORIES
        # ===================================
        stats = {
            'categories_created': 0,
            'categories_updated': 0,
            'sous_categories_created': 0,
            'sous_categories_updated': 0,
            'sous_sous_categories_created': 0,
            'sous_sous_categories_updated': 0,
        }

        with transaction.atomic():
            for cat_nom, cat_data in categories_data.items():
                # Créer ou mettre à jour la catégorie principale
                defaults = {
                    'slug': slugify(cat_nom),
                    'description': cat_data.get('description', ''),
                    'icone': cat_data.get('icone', ''),
                    'descripteurs': cat_data.get('descripteurs', {}),
                    'ordre': cat_data.get('priorite', 0),
                    'est_active': True,
                }

                if update_existing:
                    categorie, created = Categorie.objects.update_or_create(
                        nom=cat_nom,
                        defaults=defaults
                    )
                else:
                    categorie, created = Categorie.objects.get_or_create(
                        nom=cat_nom,
                        defaults=defaults
                    )

                if not dry_run:
                    if created:
                        stats['categories_created'] += 1
                        self.stdout.write(self.style.SUCCESS(f'\n✅ Catégorie créée : {cat_nom}'))
                    elif update_existing and not created:
                        stats['categories_updated'] += 1
                        self.stdout.write(self.style.WARNING(f'\n🔄 Catégorie mise à jour : {cat_nom}'))
                    else:
                        self.stdout.write(self.style.NOTICE(f'\nℹ️  Catégorie existe : {cat_nom}'))

                # Créer les sous-catégories
                ordre_sous_cat = 0
                for sous_cat_nom, sous_cat_data in cat_data.get('sous_categories', {}).items():
                    defaults = {
                        'slug': slugify(sous_cat_nom),
                        'description': sous_cat_data.get('description', ''),
                        'icone': sous_cat_data.get('icone', ''),
                        'descripteurs': sous_cat_data.get('descripteurs', {}),
                        'ordre': ordre_sous_cat,
                        'est_active': True,
                    }

                    if not dry_run:
                        if update_existing:
                            sous_categorie, created = SousCategorie.objects.update_or_create(
                                nom=sous_cat_nom,
                                categorie=categorie,
                                defaults=defaults
                            )
                        else:
                            sous_categorie, created = SousCategorie.objects.get_or_create(
                                nom=sous_cat_nom,
                                categorie=categorie,
                                defaults=defaults
                            )

                        if created:
                            stats['sous_categories_created'] += 1
                            self.stdout.write(f'  ✅ Sous-catégorie créée : {sous_cat_nom}')
                        elif update_existing and not created:
                            stats['sous_categories_updated'] += 1
                            self.stdout.write(f'  🔄 Sous-catégorie mise à jour : {sous_cat_nom}')
                        else:
                            self.stdout.write(f'  ℹ️  Sous-catégorie existe : {sous_cat_nom}')

                        ordre_sous_cat += 1

                        # Créer les sous-sous-catégories
                        ordre_sous_sous_cat = 0
                        for sous_sous_cat_data in sous_cat_data.get('sous_sous_categories', []):
                            sous_sous_nom = sous_sous_cat_data['nom']

                            defaults = {
                                'slug': slugify(sous_sous_nom),
                                'icone': sous_sous_cat_data.get('icone', ''),
                                'descripteurs': sous_sous_cat_data.get('descripteurs', {}),
                                'ordre': ordre_sous_sous_cat,
                                'est_active': True,
                            }

                            if update_existing:
                                sous_sous_categorie, created = SousSousCategorie.objects.update_or_create(
                                    nom=sous_sous_nom,
                                    souscategorie=sous_categorie,
                                    defaults=defaults
                                )
                            else:
                                sous_sous_categorie, created = SousSousCategorie.objects.get_or_create(
                                    nom=sous_sous_nom,
                                    souscategorie=sous_categorie,
                                    defaults=defaults
                                )

                            if created:
                                stats['sous_sous_categories_created'] += 1
                                self.stdout.write(f'    ✅ Sous-sous-catégorie créée : {sous_sous_nom}')
                            elif update_existing and not created:
                                stats['sous_sous_categories_updated'] += 1
                                self.stdout.write(f'    🔄 Sous-sous-catégorie mise à jour : {sous_sous_nom}')
                            else:
                                self.stdout.write(f'    ℹ️  Sous-sous-catégorie existe : {sous_sous_nom}')

                            ordre_sous_sous_cat += 1
                    else:
                        self.stdout.write(f'  [DRY-RUN] Sous-catégorie : {sous_cat_nom}')
                        for sous_sous_cat_data in sous_cat_data.get('sous_sous_categories', []):
                            self.stdout.write(f'    [DRY-RUN] Sous-sous-catégorie : {sous_sous_cat_data["nom"]}')

        # ===================================
        # RÉSUMÉ
        # ===================================
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 RÉSUMÉ DE LA SIMULATION'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ CRÉATION TERMINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        self.stdout.write(f'📁 Catégories créées : {stats["categories_created"]}')
        if update_existing:
            self.stdout.write(f'🔄 Catégories mises à jour : {stats["categories_updated"]}')

        self.stdout.write(f'📂 Sous-catégories créées : {stats["sous_categories_created"]}')
        if update_existing:
            self.stdout.write(f'🔄 Sous-catégories mises à jour : {stats["sous_categories_updated"]}')

        self.stdout.write(f'📄 Sous-sous-catégories créées : {stats["sous_sous_categories_created"]}')
        if update_existing:
            self.stdout.write(f'🔄 Sous-sous-catégories mises à jour : {stats["sous_sous_categories_updated"]}')

        total_created = (stats["categories_created"] +
                        stats["sous_categories_created"] +
                        stats["sous_sous_categories_created"])

        self.stdout.write(f'\n🎯 Total créé : {total_created} éléments')
        self.stdout.write(self.style.SUCCESS('=' * 70))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n💡 Exécutez sans --dry-run pour créer les catégories'))
