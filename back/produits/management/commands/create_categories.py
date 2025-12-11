# produits/management/commands/create_categories.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from produits.models import Categorie, SousCategorie, SousSousCategorie


class Command(BaseCommand):
    help = 'Crée la hiérarchie complète des catégories pour la plateforme Habitat Autonome Premium'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏡 Création des catégories Habitat Autonome Premium...'))

        # ===================================
        # STRUCTURE COMPLÈTE
        # ===================================
        categories_data = {
            '🏡 HABITAT AUTONOME PREMIUM': {
                'description': 'Habitat écologique, autonome et de prestige',
                'descripteurs': {
                    'certification': ['Passivhaus', 'BEPOS', 'HQE', 'E+C-', 'BBC'],
                    'surface': ['< 50m²', '50-100m²', '100-200m²', '200-300m²', '300m²+'],
                    'zone_climatique': ['H1', 'H2', 'H3'],
                    'terrain': ['Plat', 'Pente', 'Montagne', 'Bord de mer'],
                },
                'sous_categories': {
                    '🏠 Maisons Passives': {
                        'description': 'Maisons à très haute performance énergétique',
                        'descripteurs': {
                            'besoin_chauffage': ['< 15 kWh/m²/an'],
                            'etancheite': ['n50 < 0.6'],
                            'type': ['Plain-pied', 'Étage', 'Multi-niveaux'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Maison passive sur-mesure', 'descripteurs': {}},
                            {'nom': 'Kit maison passive', 'descripteurs': {}},
                            {'nom': 'Extension passive', 'descripteurs': {}},
                        ]
                    },
                    '🏘️ Villas Autonomes': {
                        'description': 'Villas haut de gamme autonomes en énergie',
                        'descripteurs': {
                            'standing': ['Premium', 'Luxe', 'Prestige'],
                            'autonomie': ['50%', '75%', '100%'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Villa contemporaine autonome', 'descripteurs': {}},
                            {'nom': 'Villa traditionnelle rénovée', 'descripteurs': {}},
                            {'nom': 'Villa bioclimatique', 'descripteurs': {}},
                        ]
                    },
                    '🌿 Architecture Écologique': {
                        'description': 'Conception architecturale durable et respectueuse',
                        'descripteurs': {
                            'style': ['Contemporain', 'Traditionnel', 'Moderne', 'Bioclimatique'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Maison bois massif', 'descripteurs': {}},
                            {'nom': 'Maison paille/terre', 'descripteurs': {}},
                            {'nom': 'Maison pierres', 'descripteurs': {}},
                        ]
                    },
                    '🏕️ Tiny House Luxe': {
                        'description': 'Habitat compact de haute qualité',
                        'descripteurs': {
                            'mobilite': ['Mobile', 'Fixe', 'Semi-mobile'],
                            'surface': ['< 20m²', '20-30m²', '30-40m²'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Tiny house sur-mesure', 'descripteurs': {}},
                            {'nom': 'Tiny house modulaire', 'descripteurs': {}},
                            {'nom': 'Studio de jardin', 'descripteurs': {}},
                        ]
                    },
                    '♻️ Éco-Rénovation': {
                        'description': 'Rénovation énergétique et écologique',
                        'descripteurs': {
                            'type_travaux': ['Isolation', 'Chauffage', 'Étanchéité', 'Ventilation'],
                            'gain_energetique': ['30-50%', '50-70%', '70%+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Rénovation passive', 'descripteurs': {}},
                            {'nom': 'Isolation écologique', 'descripteurs': {}},
                            {'nom': 'Menuiserie performante', 'descripteurs': {}},
                        ]
                    },
                    '👷 Constructeurs Locaux': {
                        'description': 'Constructeurs et architectes de la région',
                        'descripteurs': {
                            'zone': ['20km', '50km', '100km'],
                            'specialite': ['Bois', 'Pierre', 'Paille', 'Mixte'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Constructeur bois local', 'descripteurs': {}},
                            {'nom': 'Maçon écologique', 'descripteurs': {}},
                            {'nom': 'Architecte bioclimatique', 'descripteurs': {}},
                        ]
                    },
                    '🪚 Menuiserie Régionale': {
                        'description': 'Menuisiers et ébénistes du territoire',
                        'descripteurs': {
                            'essence': ['Chêne', 'Châtaignier', 'Douglas', 'Mélèze'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Fenêtres bois local', 'descripteurs': {}},
                            {'nom': 'Volets artisanaux', 'descripteurs': {}},
                            {'nom': 'Portes sur-mesure', 'descripteurs': {}},
                        ]
                    },
                    '🛠️ Artisans du Territoire': {
                        'description': 'Artisans locaux du bâtiment',
                        'sous_sous_categories': [
                            {'nom': 'Charpentier local', 'descripteurs': {}},
                            {'nom': 'Couvreur traditionnel', 'descripteurs': {}},
                            {'nom': 'Électricien domotique', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '🌳 MATÉRIAUX NOBLES ET LOCAUX': {
                'description': 'Matériaux naturels, durables et de proximité',
                'descripteurs': {
                    'provenance': ['< 50km', '< 100km', '< 200km', 'France'],
                    'certification': ['PEFC', 'FSC', 'AB', 'Nature Plus'],
                    'transformation': ['Brut', 'Semi-fini', 'Fini'],
                },
                'sous_categories': {
                    '🪵 Bois Massif Local': {
                        'description': 'Bois de la région, première transformation locale',
                        'descripteurs': {
                            'essence': ['Chêne', 'Châtaignier', 'Douglas', 'Mélèze', 'Épicéa'],
                            'usage': ['Structure', 'Menuiserie', 'Bardage', 'Charpente'],
                            'humidite': ['Vert', 'Sec air', 'Sec étuve'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Chêne français massif', 'descripteurs': {}},
                            {'nom': 'Douglas régional', 'descripteurs': {}},
                            {'nom': 'Châtaignier local', 'descripteurs': {}},
                        ]
                    },
                    '🌰 Chêne Français': {
                        'description': 'Chêne de nos forêts françaises',
                        'descripteurs': {
                            'origine': ['Bourgogne', 'Centre', 'Limousin', 'Auvergne'],
                            'qualite': ['Choix 1', 'Choix 2', 'Rustique'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Chêne massif brut', 'descripteurs': {}},
                            {'nom': 'Parquet chêne', 'descripteurs': {}},
                            {'nom': 'Lambris chêne', 'descripteurs': {}},
                        ]
                    },
                    '🌾 Chanvre Français': {
                        'description': 'Chanvre cultivé et transformé en France',
                        'descripteurs': {
                            'usage': ['Isolation', 'Enduit', 'Béton', 'Laine'],
                            'forme': ['Vrac', 'Panneau', 'Rouleau', 'Bloc'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Laine de chanvre', 'descripteurs': {}},
                            {'nom': 'Béton de chanvre', 'descripteurs': {}},
                            {'nom': 'Enduit chanvre-chaux', 'descripteurs': {}},
                        ]
                    },
                    '🏺 Terre Crue': {
                        'description': 'Terre locale non cuite, pisé, adobe',
                        'descripteurs': {
                            'technique': ['Pisé', 'Adobe', 'Bauge', 'Torchis'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Terre à pisé', 'descripteurs': {}},
                            {'nom': 'Briques adobe', 'descripteurs': {}},
                            {'nom': 'Enduit terre', 'descripteurs': {}},
                        ]
                    },
                    '🪨 Pierre Naturelle': {
                        'description': 'Pierres de carrières locales',
                        'descripteurs': {
                            'type': ['Calcaire', 'Granit', 'Grès', 'Schiste'],
                            'finition': ['Brute', 'Taillée', 'Polie'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Pierre de taille locale', 'descripteurs': {}},
                            {'nom': 'Lauze traditionnelle', 'descripteurs': {}},
                            {'nom': 'Granit régional', 'descripteurs': {}},
                        ]
                    },
                    '⚪ Marbre': {
                        'description': 'Marbre français et européen',
                        'sous_sous_categories': [
                            {'nom': 'Marbre blanc', 'descripteurs': {}},
                            {'nom': 'Marbre noir', 'descripteurs': {}},
                            {'nom': 'Marbre veiné', 'descripteurs': {}},
                        ]
                    },
                    '⚒️ Métal Forgé': {
                        'description': 'Métallerie artisanale locale',
                        'sous_sous_categories': [
                            {'nom': 'Fer forgé', 'descripteurs': {}},
                            {'nom': 'Acier brut', 'descripteurs': {}},
                            {'nom': 'Bronze', 'descripteurs': {}},
                        ]
                    },
                    '♻️ Matériaux Biosourcés': {
                        'description': 'Matériaux d\'origine végétale ou animale',
                        'sous_sous_categories': [
                            {'nom': 'Laine de mouton', 'descripteurs': {}},
                            {'nom': 'Ouate de cellulose', 'descripteurs': {}},
                            {'nom': 'Liège expansé', 'descripteurs': {}},
                            {'nom': 'Paille de construction', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '⚡ ÉNERGIE AUTONOME': {
                'description': 'Solutions pour l\'autonomie énergétique',
                'descripteurs': {
                    'puissance': ['< 3kW', '3-6kW', '6-9kW', '9-12kW', '12kW+'],
                    'taux_autonomie': ['30-50%', '50-75%', '75-90%', '90-100%'],
                    'type_installation': ['Autoconsommation', 'Revente surplus', 'Autonome'],
                },
                'sous_categories': {
                    '☀️ Solaire Premium': {
                        'description': 'Panneaux photovoltaïques haut rendement',
                        'descripteurs': {
                            'technologie': ['Monocristallin', 'Bifacial', 'Back-contact'],
                            'rendement': ['18-20%', '20-22%', '22%+'],
                            'garantie': ['10 ans', '20 ans', '25 ans'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Panneaux solaires premium', 'descripteurs': {}},
                            {'nom': 'Tuiles solaires intégrées', 'descripteurs': {}},
                            {'nom': 'Ombrières solaires', 'descripteurs': {}},
                        ]
                    },
                    '🔋 Batteries Intelligentes': {
                        'description': 'Stockage d\'énergie nouvelle génération',
                        'descripteurs': {
                            'technologie': ['Lithium-ion', 'LiFePO4', 'Flow battery'],
                            'capacite': ['5-10 kWh', '10-15 kWh', '15-20 kWh', '20+ kWh'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Batterie lithium domestique', 'descripteurs': {}},
                            {'nom': 'Batterie virtuelle', 'descripteurs': {}},
                            {'nom': 'Power wall', 'descripteurs': {}},
                        ]
                    },
                    '💨 Éoliennes Design': {
                        'description': 'Petit éolien esthétique et performant',
                        'descripteurs': {
                            'puissance': ['< 1kW', '1-5kW', '5-10kW'],
                            'type': ['Verticale', 'Horizontale'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Éolienne verticale urbaine', 'descripteurs': {}},
                            {'nom': 'Éolienne domestique', 'descripteurs': {}},
                        ]
                    },
                    '🔥 Poêles Haut Rendement': {
                        'description': 'Chauffage au bois haute performance',
                        'descripteurs': {
                            'rendement': ['75-85%', '85-90%', '90%+'],
                            'type': ['Bûches', 'Granulés', 'Mixte'],
                            'puissance': ['5-8kW', '8-12kW', '12-15kW'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Poêle à bois suspendu', 'descripteurs': {}},
                            {'nom': 'Poêle à granulés silencieux', 'descripteurs': {}},
                            {'nom': 'Poêle de masse artisanal', 'descripteurs': {}},
                        ]
                    },
                    '🌡️ Chauffage Autonome': {
                        'description': 'Solutions de chauffage indépendantes',
                        'sous_sous_categories': [
                            {'nom': 'Pompe à chaleur', 'descripteurs': {}},
                            {'nom': 'Chaudière biomasse', 'descripteurs': {}},
                            {'nom': 'Radiateurs inertiels', 'descripteurs': {}},
                        ]
                    },
                    '🏠 Domotique Énergétique': {
                        'description': 'Gestion intelligente de l\'énergie',
                        'sous_sous_categories': [
                            {'nom': 'Box domotique énergie', 'descripteurs': {}},
                            {'nom': 'Gestion chauffage', 'descripteurs': {}},
                            {'nom': 'Monitoring consommation', 'descripteurs': {}},
                        ]
                    },
                    '🏔️ Solutions Off-Grid': {
                        'description': 'Autonomie énergétique totale',
                        'sous_sous_categories': [
                            {'nom': 'Kit autonomie complète', 'descripteurs': {}},
                            {'nom': 'Générateur secours', 'descripteurs': {}},
                            {'nom': 'Micro-hydro électricité', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '💧 EAU ET TRAITEMENT LOCAL': {
                'description': 'Gestion autonome et traitement de l\'eau',
                'descripteurs': {
                    'debit': ['< 1m³/j', '1-3m³/j', '3-5m³/j', '5m³/j+'],
                    'usage': ['Potable', 'Sanitaire', 'Arrosage', 'Tous usages'],
                },
                'sous_categories': {
                    '🔬 Filtration Haut de Gamme': {
                        'description': 'Systèmes de filtration avancés',
                        'descripteurs': {
                            'technologie': ['Charbon actif', 'Céramique', 'UV', 'Multi-étages'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Filtre sous-évier premium', 'descripteurs': {}},
                            {'nom': 'Station filtration maison', 'descripteurs': {}},
                            {'nom': 'Filtre gravitaire design', 'descripteurs': {}},
                        ]
                    },
                    '💎 Osmose Inverse': {
                        'description': 'Purification maximale de l\'eau',
                        'sous_sous_categories': [
                            {'nom': 'Osmoseur compact', 'descripteurs': {}},
                            {'nom': 'Osmoseur avec réservoir', 'descripteurs': {}},
                        ]
                    },
                    '🌧️ Récupération d\'Eau': {
                        'description': 'Collecte et stockage eau de pluie',
                        'descripteurs': {
                            'capacite': ['500-1000L', '1000-3000L', '3000-5000L', '5000L+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Cuve enterrée', 'descripteurs': {}},
                            {'nom': 'Réservoir hors-sol design', 'descripteurs': {}},
                            {'nom': 'Citerne souple', 'descripteurs': {}},
                        ]
                    },
                    '🌿 Purification Naturelle': {
                        'description': 'Traitement écologique de l\'eau',
                        'sous_sous_categories': [
                            {'nom': 'Phytoépuration', 'descripteurs': {}},
                            {'nom': 'Lagunage naturel', 'descripteurs': {}},
                            {'nom': 'Toilettes sèches premium', 'descripteurs': {}},
                        ]
                    },
                    '♻️ Gestion Autonome': {
                        'description': 'Systèmes complets de gestion eau',
                        'sous_sous_categories': [
                            {'nom': 'Pompage solaire', 'descripteurs': {}},
                            {'nom': 'Régulation automatique', 'descripteurs': {}},
                            {'nom': 'Monitoring qualité eau', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '🌱 AUTONOMIE ALIMENTAIRE': {
                'description': 'Produire son alimentation locale et saine',
                'descripteurs': {
                    'saison': ['Printemps', 'Été', 'Automne', 'Hiver', 'Toute saison'],
                    'niveau': ['Débutant', 'Intermédiaire', 'Expert'],
                },
                'sous_categories': {
                    '🥬 Potagers Terroir': {
                        'description': 'Potagers productifs et esthétiques',
                        'descripteurs': {
                            'type': ['Carré', 'Ligne', 'Permaculture', 'Mandala'],
                            'surface': ['< 20m²', '20-50m²', '50-100m²', '100m²+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Carré potager surélevé', 'descripteurs': {}},
                            {'nom': 'Potager permaculture', 'descripteurs': {}},
                            {'nom': 'Potager urbain', 'descripteurs': {}},
                        ]
                    },
                    '🏡 Serres Premium': {
                        'description': 'Serres de culture haut de gamme',
                        'descripteurs': {
                            'materiau': ['Verre', 'Polycarbonate', 'Mixte'],
                            'surface': ['< 10m²', '10-20m²', '20-30m²', '30m²+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Serre verre et bois', 'descripteurs': {}},
                            {'nom': 'Serre tunnel pro', 'descripteurs': {}},
                            {'nom': 'Serre bioclimatique', 'descripteurs': {}},
                        ]
                    },
                    '🛠️ Outils Artisans': {
                        'description': 'Outils de jardin de qualité professionnelle',
                        'sous_sous_categories': [
                            {'nom': 'Outils forgés main', 'descripteurs': {}},
                            {'nom': 'Grelinette premium', 'descripteurs': {}},
                            {'nom': 'Sécateur professionnel', 'descripteurs': {}},
                        ]
                    },
                    '🍎 Verger Régional': {
                        'description': 'Arbres fruitiers adaptés au climat local',
                        'sous_sous_categories': [
                            {'nom': 'Pommiers haute tige', 'descripteurs': {}},
                            {'nom': 'Poiriers anciens', 'descripteurs': {}},
                            {'nom': 'Fruitiers basse tige', 'descripteurs': {}},
                        ]
                    },
                    '🐝 Ruches Locales': {
                        'description': 'Apiculture naturelle',
                        'sous_sous_categories': [
                            {'nom': 'Ruche Warré', 'descripteurs': {}},
                            {'nom': 'Ruche Dadant', 'descripteurs': {}},
                            {'nom': 'Ruche horizontale', 'descripteurs': {}},
                        ]
                    },
                    '🐔 Poulaillers Premium': {
                        'description': 'Poulaillers design et fonctionnels',
                        'sous_sous_categories': [
                            {'nom': 'Poulailler bois local', 'descripteurs': {}},
                            {'nom': 'Poulailler mobile', 'descripteurs': {}},
                            {'nom': 'Poulailler design', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '🌿 PLANTES & VÉGÉTAUX': {
                'description': 'Plantes, arbres et végétaux pour l\'autonomie et le bien-être',
                'descripteurs': {
                    'type_culture': ['Bio', 'Biodynamie', 'Permaculture', 'Naturel'],
                    'provenance': ['Local', 'Régional', 'France'],
                    'conditionnement': ['Graine', 'Plant', 'Pot', 'Motte', 'Racine nue'],
                },
                'sous_categories': {
                    '🌾 Semences Anciennes & Patrimoine': {
                        'description': 'Graines anciennes et variétés paysannes',
                        'descripteurs': {
                            'type': ['Reproductible', 'Non hybride', 'Patrimoine'],
                            'conservation': ['Court terme', 'Moyen terme', 'Long terme'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Graines anciennes certifiées', 'descripteurs': {}},
                            {'nom': 'Variétés paysannes', 'descripteurs': {}},
                            {'nom': 'Semences reproductibles', 'descripteurs': {}},
                            {'nom': 'Variétés locales du terroir', 'descripteurs': {}},
                            {'nom': 'Patrimoine végétal', 'descripteurs': {}},
                            {'nom': 'Variétés rares et oubliées', 'descripteurs': {}},
                        ]
                    },
                    '🥕 Légumes Anciens': {
                        'description': 'Légumes traditionnels et variétés oubliées',
                        'descripteurs': {
                            'saison': ['Printemps', 'Été', 'Automne', 'Hiver'],
                            'difficulte': ['Facile', 'Moyen', 'Expert'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Tomates anciennes', 'descripteurs': {}},
                            {'nom': 'Courges anciennes', 'descripteurs': {}},
                            {'nom': 'Haricots patrimoine', 'descripteurs': {}},
                            {'nom': 'Légumes oubliés', 'descripteurs': {}},
                            {'nom': 'Salades anciennes', 'descripteurs': {}},
                            {'nom': 'Choux anciens', 'descripteurs': {}},
                        ]
                    },
                    '🌿 Aromatiques Régionales': {
                        'description': 'Herbes aromatiques du terroir',
                        'descripteurs': {
                            'usage': ['Cuisine', 'Tisane', 'Médicinal', 'Décoratif'],
                            'exposition': ['Plein soleil', 'Mi-ombre', 'Ombre'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Thym ancien', 'descripteurs': {}},
                            {'nom': 'Basilic ancien', 'descripteurs': {}},
                            {'nom': 'Romarin terroir', 'descripteurs': {}},
                            {'nom': 'Menthe paysanne', 'descripteurs': {}},
                            {'nom': 'Sauge ancestrale', 'descripteurs': {}},
                            {'nom': 'Lavande locale', 'descripteurs': {}},
                        ]
                    },
                    '🍏 Fruitiers Anciens': {
                        'description': 'Arbres fruitiers variétés anciennes',
                        'descripteurs': {
                            'port': ['Haute tige', 'Demi-tige', 'Basse tige', 'Colonnaire'],
                            'pollinisation': ['Auto-fertile', 'Nécessite pollinisateur'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Pommiers anciens', 'descripteurs': {}},
                            {'nom': 'Poiriers anciens', 'descripteurs': {}},
                            {'nom': 'Cerisiers anciens', 'descripteurs': {}},
                            {'nom': 'Pruniers anciens', 'descripteurs': {}},
                            {'nom': 'Fruits rustiques', 'descripteurs': {}},
                            {'nom': 'Petits fruits anciens', 'descripteurs': {}},
                        ]
                    },
                    '🌳 Arbres & Arbustes Locaux': {
                        'description': 'Essences locales pour haies et agroforesterie',
                        'descripteurs': {
                            'usage': ['Haie', 'Bosquet', 'Isolé', 'Agroforesterie'],
                            'taille_adulte': ['< 5m', '5-10m', '10-15m', '15m+'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Chênes locaux', 'descripteurs': {}},
                            {'nom': 'Châtaigniers', 'descripteurs': {}},
                            {'nom': 'Noisetiers', 'descripteurs': {}},
                            {'nom': 'Haies champêtres', 'descripteurs': {}},
                            {'nom': 'Arbustes mellifères', 'descripteurs': {}},
                            {'nom': 'Bois d\'œuvre local', 'descripteurs': {}},
                        ]
                    },
                    '🌸 Plantes Médicinales': {
                        'description': 'Plantes à vertus thérapeutiques',
                        'descripteurs': {
                            'usage': ['Tisane', 'Infusion', 'Décoction', 'Macération'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Plantes digestives', 'descripteurs': {}},
                            {'nom': 'Plantes apaisantes', 'descripteurs': {}},
                            {'nom': 'Plantes immunitaires', 'descripteurs': {}},
                        ]
                    },
                    '🪴 Plantes d\'Intérieur': {
                        'description': 'Plantes dépolluantes et décoratives',
                        'sous_sous_categories': [
                            {'nom': 'Plantes dépolluantes', 'descripteurs': {}},
                            {'nom': 'Plantes tropicales', 'descripteurs': {}},
                            {'nom': 'Cactées et succulentes', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '🎨 ARTISANAT LOCAL PREMIUM': {
                'description': 'Créations artisanales de qualité par des artisans du territoire',
                'descripteurs': {
                    'provenance': ['< 20km', '< 50km', '< 100km'],
                    'type_artisan': ['Artisan d\'art', 'Maître artisan', 'MOF'],
                    'materiau_principal': ['Bois', 'Métal', 'Terre', 'Textile', 'Cuir', 'Verre'],
                },
                'sous_categories': {
                    '🪚 Menuiserie': {
                        'description': 'Créations bois sur-mesure',
                        'sous_sous_categories': [
                            {'nom': 'Meubles sur-mesure', 'descripteurs': {}},
                            {'nom': 'Agencement intérieur', 'descripteurs': {}},
                            {'nom': 'Escaliers bois', 'descripteurs': {}},
                        ]
                    },
                    '⚒️ Métallerie': {
                        'description': 'Ferronnerie et métallerie d\'art',
                        'sous_sous_categories': [
                            {'nom': 'Garde-corps artisanal', 'descripteurs': {}},
                            {'nom': 'Portails forgés', 'descripteurs': {}},
                            {'nom': 'Luminaires métal', 'descripteurs': {}},
                        ]
                    },
                    '🏺 Céramique': {
                        'description': 'Poterie et céramique artisanale',
                        'sous_sous_categories': [
                            {'nom': 'Vaisselle artisanale', 'descripteurs': {}},
                            {'nom': 'Carrelage artisanal', 'descripteurs': {}},
                            {'nom': 'Objets déco céramique', 'descripteurs': {}},
                        ]
                    },
                    '👜 Cuir': {
                        'description': 'Maroquinerie artisanale',
                        'sous_sous_categories': [
                            {'nom': 'Sacs cuir artisanal', 'descripteurs': {}},
                            {'nom': 'Ceintures cuir', 'descripteurs': {}},
                            {'nom': 'Accessoires cuir', 'descripteurs': {}},
                        ]
                    },
                    '🧺 Vannerie': {
                        'description': 'Travail de l\'osier et des fibres végétales',
                        'sous_sous_categories': [
                            {'nom': 'Paniers artisanaux', 'descripteurs': {}},
                            {'nom': 'Mobilier osier', 'descripteurs': {}},
                            {'nom': 'Objets déco vannerie', 'descripteurs': {}},
                        ]
                    },
                    '🧶 Tissage': {
                        'description': 'Textiles tissés main',
                        'sous_sous_categories': [
                            {'nom': 'Plaids laine', 'descripteurs': {}},
                            {'nom': 'Tapis tissés', 'descripteurs': {}},
                            {'nom': 'Tissus d\'ameublement', 'descripteurs': {}},
                        ]
                    },
                    '🧵 Textiles Naturels': {
                        'description': 'Textiles en matières naturelles',
                        'sous_sous_categories': [
                            {'nom': 'Lin local', 'descripteurs': {}},
                            {'nom': 'Chanvre textile', 'descripteurs': {}},
                            {'nom': 'Laine régionale', 'descripteurs': {}},
                        ]
                    },
                    '🎨 Artisanat d\'Art': {
                        'description': 'Créations artistiques uniques',
                        'sous_sous_categories': [
                            {'nom': 'Sculptures', 'descripteurs': {}},
                            {'nom': 'Tableaux artisanaux', 'descripteurs': {}},
                            {'nom': 'Objets d\'art', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '🏡 ART DE VIVRE LOCAL': {
                'description': 'Décoration et accessoires pour un intérieur authentique',
                'descripteurs': {
                    'style': ['Contemporain', 'Traditionnel', 'Rustique', 'Moderne', 'Mixte'],
                    'piece': ['Salon', 'Chambre', 'Cuisine', 'Salle de bain', 'Extérieur'],
                },
                'sous_categories': {
                    '🌿 Décoration Naturelle': {
                        'description': 'Objets déco en matériaux naturels',
                        'sous_sous_categories': [
                            {'nom': 'Vases artisanaux', 'descripteurs': {}},
                            {'nom': 'Cadres bois', 'descripteurs': {}},
                            {'nom': 'Miroirs naturels', 'descripteurs': {}},
                        ]
                    },
                    '🪑 Mobilier Sur-Mesure': {
                        'description': 'Meubles créés sur-mesure par artisans locaux',
                        'sous_sous_categories': [
                            {'nom': 'Tables bois massif', 'descripteurs': {}},
                            {'nom': 'Bibliothèques sur-mesure', 'descripteurs': {}},
                            {'nom': 'Literie naturelle', 'descripteurs': {}},
                        ]
                    },
                    '💡 Luminaires Artisanaux': {
                        'description': 'Éclairage artisanal et design',
                        'sous_sous_categories': [
                            {'nom': 'Suspensions bois', 'descripteurs': {}},
                            {'nom': 'Lampes métal forgé', 'descripteurs': {}},
                            {'nom': 'Appliques artisanales', 'descripteurs': {}},
                        ]
                    },
                    '🕯️ Parfums de Maison Terroir': {
                        'description': 'Senteurs naturelles et locales',
                        'sous_sous_categories': [
                            {'nom': 'Bougies cire naturelle', 'descripteurs': {}},
                            {'nom': 'Diffuseurs huiles essentielles', 'descripteurs': {}},
                            {'nom': 'Parfums d\'ambiance', 'descripteurs': {}},
                        ]
                    },
                    '🎁 Accessoires Nobles': {
                        'description': 'Petits objets de qualité',
                        'sous_sous_categories': [
                            {'nom': 'Coussins textiles naturels', 'descripteurs': {}},
                            {'nom': 'Plaids laine', 'descripteurs': {}},
                            {'nom': 'Tapis artisanaux', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '🍷 GASTRONOMIE DU TERROIR': {
                'description': 'Produits gastronomiques d\'exception du territoire',
                'descripteurs': {
                    'label': ['AB', 'AOP', 'IGP', 'Label Rouge', 'Nature & Progrès', 'Demeter'],
                    'provenance': ['< 20km', '< 50km', '< 100km', 'Région'],
                    'conservation': ['Frais', 'Conserve', 'Sec', 'Réfrigéré'],
                },
                'sous_categories': {
                    '🍷 Vins Régionaux': {
                        'description': 'Vins de vignerons locaux',
                        'descripteurs': {
                            'type': ['Rouge', 'Blanc', 'Rosé', 'Effervescent'],
                            'culture': ['Bio', 'Biodynamie', 'Nature', 'Raisonnée'],
                            'millesime': list(range(2015, 2024)),
                        },
                        'sous_sous_categories': [
                            {'nom': 'Vins bio locaux', 'descripteurs': {}},
                            {'nom': 'Vins nature terroir', 'descripteurs': {}},
                            {'nom': 'Vins biodynamiques', 'descripteurs': {}},
                            {'nom': 'Cuvées prestige', 'descripteurs': {}},
                        ]
                    },
                    '🍾 Champagne Bio Luxe': {
                        'description': 'Champagnes et effervescents premium',
                        'descripteurs': {
                            'type': ['Brut', 'Extra-brut', 'Blanc de blancs', 'Blanc de noirs', 'Rosé'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Champagne bio', 'descripteurs': {}},
                            {'nom': 'Crémant premium', 'descripteurs': {}},
                            {'nom': 'Bulles artisanales', 'descripteurs': {}},
                        ]
                    },
                    '🧀 Fromageries Fermes': {
                        'description': 'Fromages fermiers au lait cru',
                        'descripteurs': {
                            'lait': ['Vache', 'Chèvre', 'Brebis', 'Mixte'],
                            'pate': ['Molle', 'Pressée', 'Persillée'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Fromages au lait cru', 'descripteurs': {}},
                            {'nom': 'Tommes fermières', 'descripteurs': {}},
                            {'nom': 'Fromages affinés', 'descripteurs': {}},
                        ]
                    },
                    '🍯 Miel Premium': {
                        'description': 'Miels d\'apiculteurs locaux',
                        'descripteurs': {
                            'type': ['Toutes fleurs', 'Acacia', 'Châtaignier', 'Lavande', 'Forêt'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Miel de fleurs', 'descripteurs': {}},
                            {'nom': 'Miel de forêt', 'descripteurs': {}},
                            {'nom': 'Miel rare', 'descripteurs': {}},
                        ]
                    },
                    '🥖 Épicerie Locale': {
                        'description': 'Produits d\'épicerie fine du terroir',
                        'sous_sous_categories': [
                            {'nom': 'Huiles artisanales', 'descripteurs': {}},
                            {'nom': 'Vinaigres terroir', 'descripteurs': {}},
                            {'nom': 'Confitures maison', 'descripteurs': {}},
                            {'nom': 'Pâtes artisanales', 'descripteurs': {}},
                            {'nom': 'Farines anciennes', 'descripteurs': {}},
                        ]
                    },
                    '🥃 Spiritueux Artisanaux': {
                        'description': 'Distillerie et spiritueux locaux',
                        'descripteurs': {
                            'type': ['Whisky', 'Gin', 'Vodka', 'Liqueur', 'Eau-de-vie'],
                        },
                        'sous_sous_categories': [
                            {'nom': 'Whisky local', 'descripteurs': {}},
                            {'nom': 'Gin artisanal', 'descripteurs': {}},
                            {'nom': 'Liqueurs terroir', 'descripteurs': {}},
                            {'nom': 'Eaux-de-vie', 'descripteurs': {}},
                        ]
                    },
                    '☕ Café & Thé': {
                        'description': 'Torréfaction locale et thés premium',
                        'sous_sous_categories': [
                            {'nom': 'Café torréfaction locale', 'descripteurs': {}},
                            {'nom': 'Thés biologiques', 'descripteurs': {}},
                            {'nom': 'Tisanes terroir', 'descripteurs': {}},
                        ]
                    },
                    '🍫 Chocolat Artisanal': {
                        'description': 'Chocolaterie artisanale locale',
                        'sous_sous_categories': [
                            {'nom': 'Chocolat bean-to-bar', 'descripteurs': {}},
                            {'nom': 'Tablettes artisanales', 'descripteurs': {}},
                            {'nom': 'Bonbons chocolat', 'descripteurs': {}},
                        ]
                    },
                }
            },

            '🌍 EXPÉRIENCE & PROXIMITÉ': {
                'description': 'Rencontres, découvertes et expériences locales',
                'descripteurs': {
                    'type_experience': ['Visite', 'Atelier', 'Dégustation', 'Formation', 'Séjour'],
                    'duree': ['1-2h', '1/2 journée', 'Journée', 'Week-end', 'Semaine'],
                    'public': ['Adulte', 'Famille', 'Enfant', 'Groupe', 'Entreprise'],
                },
                'sous_categories': {
                    '🚜 Circuit Court': {
                        'description': 'Achat direct producteur',
                        'sous_sous_categories': [
                            {'nom': 'Vente à la ferme', 'descripteurs': {}},
                            {'nom': 'Paniers producteurs', 'descripteurs': {}},
                            {'nom': 'AMAP locales', 'descripteurs': {}},
                        ]
                    },
                    '👨‍🌾 Rencontre Producteurs': {
                        'description': 'Échanges avec les artisans et producteurs',
                        'sous_sous_categories': [
                            {'nom': 'Visite ferme', 'descripteurs': {}},
                            {'nom': 'Rencontre vigneron', 'descripteurs': {}},
                            {'nom': 'Visite atelier artisan', 'descripteurs': {}},
                        ]
                    },
                    '🛠️ Visite Atelier': {
                        'description': 'Découverte des ateliers de production',
                        'sous_sous_categories': [
                            {'nom': 'Atelier menuiserie', 'descripteurs': {}},
                            {'nom': 'Atelier poterie', 'descripteurs': {}},
                            {'nom': 'Atelier métallerie', 'descripteurs': {}},
                        ]
                    },
                    '🍷 Découverte Terroir': {
                        'description': 'Expériences gastronomiques',
                        'sous_sous_categories': [
                            {'nom': 'Dégustation vins', 'descripteurs': {}},
                            {'nom': 'Dégustation fromages', 'descripteurs': {}},
                            {'nom': 'Cours cuisine terroir', 'descripteurs': {}},
                        ]
                    },
                    '🏡 Produits Régionaux': {
                        'description': 'Sélection de produits du territoire',
                        'sous_sous_categories': [
                            {'nom': 'Coffrets terroir', 'descripteurs': {}},
                            {'nom': 'Paniers découverte', 'descripteurs': {}},
                            {'nom': 'Abonnements locaux', 'descripteurs': {}},
                        ]
                    },
                    '⭐ Qualité Locale': {
                        'description': 'Labels et certifications locales',
                        'sous_sous_categories': [
                            {'nom': 'Artisan reconnu', 'descripteurs': {}},
                            {'nom': 'Producteur certifié', 'descripteurs': {}},
                            {'nom': 'Savoir-faire d\'exception', 'descripteurs': {}},
                        ]
                    },
                }
            },
        }

        # ===================================
        # CRÉATION DES CATÉGORIES
        # ===================================
        total_categories = 0
        total_sous_categories = 0
        total_sous_sous_categories = 0

        for cat_nom, cat_data in categories_data.items():
            # Créer la catégorie principale
            categorie, created = Categorie.objects.get_or_create(
                nom=cat_nom,
                defaults={
                    'slug': slugify(cat_nom),
                    'description': cat_data.get('description', ''),
                    'descripteurs': cat_data.get('descripteurs', {}),
                    'ordre': total_categories,
                    'est_active': True,
                }
            )

            if created:
                total_categories += 1
                self.stdout.write(self.style.SUCCESS(f'\n✅ Catégorie créée : {cat_nom}'))
            else:
                self.stdout.write(self.style.WARNING(f'\nℹ️  Catégorie existe déjà : {cat_nom}'))

            # Créer les sous-catégories
            ordre_sous_cat = 0
            for sous_cat_nom, sous_cat_data in cat_data.get('sous_categories', {}).items():
                sous_categorie, created = SousCategorie.objects.get_or_create(
                    nom=sous_cat_nom,
                    categorie=categorie,
                    defaults={
                        'slug': slugify(sous_cat_nom),
                        'description': sous_cat_data.get('description', ''),
                        'descripteurs': sous_cat_data.get('descripteurs', {}),
                        'ordre': ordre_sous_cat,
                        'est_active': True,
                    }
                )

                if created:
                    total_sous_categories += 1
                    self.stdout.write(f'  ✅ Sous-catégorie créée : {sous_cat_nom}')
                else:
                    self.stdout.write(f'  ℹ️  Sous-catégorie existe : {sous_cat_nom}')

                ordre_sous_cat += 1

                # Créer les sous-sous-catégories
                ordre_sous_sous_cat = 0
                for sous_sous_cat_data in sous_cat_data.get('sous_sous_categories', []):
                    sous_sous_nom = sous_sous_cat_data['nom']

                    sous_sous_categorie, created = SousSousCategorie.objects.get_or_create(
                        nom=sous_sous_nom,
                        souscategorie=sous_categorie,
                        defaults={
                            'slug': slugify(sous_sous_nom),
                            'descripteurs': sous_sous_cat_data.get('descripteurs', {}),
                            'ordre': ordre_sous_sous_cat,
                            'est_active': True,
                        }
                    )

                    if created:
                        total_sous_sous_categories += 1
                        self.stdout.write(f'    ✅ Sous-sous-catégorie créée : {sous_sous_nom}')
                    else:
                        self.stdout.write(f'    ℹ️  Sous-sous-catégorie existe : {sous_sous_nom}')

                    ordre_sous_sous_cat += 1

        # ===================================
        # RÉSUMÉ
        # ===================================
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ CRÉATION TERMINÉE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'📁 Catégories créées : {total_categories}')
        self.stdout.write(f'📂 Sous-catégories créées : {total_sous_categories}')
        self.stdout.write(f'📄 Sous-sous-catégories créées : {total_sous_sous_categories}')
        self.stdout.write(self.style.SUCCESS('=' * 60))
