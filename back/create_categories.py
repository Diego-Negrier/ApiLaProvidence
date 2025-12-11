# scripts/create_categories.py

"""
Script pour créer les catégories, sous-catégories et sous-sous-catégories
Usage: python manage.py shell < scripts/create_categories.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from produits.models import Categorie, SousCategorie, SousSousCategorie

def create_all_categories():
    """Crée toutes les catégories avec leur hiérarchie complète"""
    
    print("🚀 CRÉATION DES CATÉGORIES À 3 NIVEAUX")
    print("=" * 60)
    
    # Structure complète : Catégorie > Sous-catégorie > Sous-sous-catégorie
    categories_data = {
        '🍖 BOUCHERIE': {
            'description': 'Viandes fraîches et produits de boucherie',
            'sous_categories': {
                'Bœuf': [
                    'Steaks et pavés',
                    'Rôtis',
                    'Bourguignon',
                    'Viande hachée',
                    'Côtes et entrecôtes',
                    'Morceaux braisés'
                ],
                'Veau': [
                    'Escalopes',
                    'Rôtis',
                    'Blanquette',
                    'Côtes',
                    'Osso bucco',
                    'Foie'
                ],
                'Porc': [
                    'Côtes et échines',
                    'Rôtis',
                    'Filet mignon',
                    'Travers',
                    'Jambon frais',
                    'Sauté'
                ],
                'Agneau': [
                    'Gigot',
                    'Côtelettes',
                    'Épaule',
                    'Navarin',
                    'Merguez',
                    'Brochettes'
                ],
                'Volaille': [
                    'Poulet entier',
                    'Découpes de poulet',
                    'Canard',
                    'Pintade',
                    'Dinde',
                    'Cailles'
                ],
                'Abats': [
                    'Foie',
                    'Rognons',
                    'Cœur',
                    'Langue',
                    'Tripes',
                    'Ris de veau'
                ]
            }
        },
        
        '🥓 CHARCUTERIE': {
            'description': 'Charcuterie artisanale et traditionnelle',
            'sous_categories': {
                'Jambons': [
                    'Jambon blanc',
                    'Jambon cru',
                    'Jambon fumé',
                    'Jambon de Bayonne',
                    'Jambon Serrano',
                    'Jambon Ibérique'
                ],
                'Saucissons': [
                    'Saucisson sec',
                    'Saucisson à l\'ail',
                    'Saucisson aux herbes',
                    'Chorizo',
                    'Fuet',
                    'Rosette'
                ],
                'Saucisses': [
                    'Saucisses de Toulouse',
                    'Merguez',
                    'Chipolatas',
                    'Saucisses fumées',
                    'Saucisses italiennes',
                    'Andouillettes'
                ],
                'Pâtés et Terrines': [
                    'Pâté de campagne',
                    'Terrine de canard',
                    'Pâté en croûte',
                    'Rillettes',
                    'Foie gras',
                    'Mousses'
                ],
                'Lardons et Poitrines': [
                    'Lardons fumés',
                    'Lardons nature',
                    'Poitrine fumée',
                    'Pancetta',
                    'Bacon',
                    'Guanciale'
                ],
                'Spécialités': [
                    'Boudin noir',
                    'Boudin blanc',
                    'Andouille',
                    'Cervelas',
                    'Mortadelle',
                    'Coppa'
                ]
            }
        },
        
        '🧀 FROMAGES': {
            'description': 'Fromages français et étrangers',
            'sous_categories': {
                'Pâtes molles': [
                    'Camembert',
                    'Brie',
                    'Coulommiers',
                    'Chaource',
                    'Mont d\'Or',
                    'Époisses'
                ],
                'Pâtes pressées': [
                    'Comté',
                    'Beaufort',
                    'Abondance',
                    'Tomme de Savoie',
                    'Cantal',
                    'Mimolette'
                ],
                'Fromages de chèvre': [
                    'Crottin de Chavignol',
                    'Sainte-Maure',
                    'Rocamadour',
                    'Valençay',
                    'Picodon',
                    'Cabécou'
                ],
                'Fromages de brebis': [
                    'Roquefort',
                    'Ossau-Iraty',
                    'Brebis basque',
                    'Pérail',
                    'Manchego',
                    'Pecorino'
                ],
                'Pâtes persillées': [
                    'Roquefort',
                    'Bleu d\'Auvergne',
                    'Fourme d\'Ambert',
                    'Bleu de Gex',
                    'Gorgonzola',
                    'Stilton'
                ],
                'Fromages italiens': [
                    'Parmigiano Reggiano',
                    'Mozzarella di Bufala',
                    'Grana Padano',
                    'Burrata',
                    'Provolone',
                    'Taleggio'
                ]
            }
        },
        
        '🐟 POISSONNERIE': {
            'description': 'Poissons frais et fruits de mer',
            'sous_categories': {
                'Poissons nobles': [
                    'Saumon',
                    'Bar de ligne',
                    'Daurade',
                    'Turbot',
                    'Saint-Pierre',
                    'Sole'
                ],
                'Poissons de mer': [
                    'Cabillaud',
                    'Lieu',
                    'Merlan',
                    'Rouget',
                    'Maquereau',
                    'Sardines'
                ],
                'Crustacés': [
                    'Homard',
                    'Langoustines',
                    'Tourteaux',
                    'Araignées de mer',
                    'Crevettes roses',
                    'Écrevisses'
                ],
                'Coquillages': [
                    'Huîtres',
                    'Moules',
                    'Palourdes',
                    'Coques',
                    'Saint-Jacques',
                    'Bulots'
                ],
                'Poissons fumés': [
                    'Saumon fumé',
                    'Truite fumée',
                    'Haddock',
                    'Maquereau fumé',
                    'Hareng fumé',
                    'Anguille fumée'
                ],
                'Préparations': [
                    'Filets marinés',
                    'Tartares',
                    'Carpaccios',
                    'Rillettes de poisson',
                    'Brandade',
                    'Tarama'
                ]
            }
        },
        
        '🥖 BOULANGERIE': {
            'description': 'Pains frais et viennoiseries',
            'sous_categories': {
                'Pains traditionnels': [
                    'Baguette tradition',
                    'Pain de campagne',
                    'Pain complet',
                    'Pain aux céréales',
                    'Pain de seigle',
                    'Boule de pain'
                ],
                'Pains spéciaux': [
                    'Pain aux noix',
                    'Pain aux olives',
                    'Pain au levain',
                    'Fougasse',
                    'Pain brié',
                    'Pain d\'épices'
                ],
                'Viennoiseries': [
                    'Croissants',
                    'Pains au chocolat',
                    'Pains aux raisins',
                    'Chaussons aux pommes',
                    'Brioches',
                    'Pains viennois'
                ],
                'Pâtisseries': [
                    'Éclairs',
                    'Tartes aux fruits',
                    'Paris-Brest',
                    'Millefeuilles',
                    'Saint-Honoré',
                    'Fraisiers'
                ],
                'Pains du monde': [
                    'Pain pita',
                    'Ciabatta',
                    'Focaccia',
                    'Bagels',
                    'Pain suédois',
                    'Pain polaire'
                ],
                'Sans gluten': [
                    'Pain sans gluten',
                    'Baguette sans gluten',
                    'Viennoiseries sans gluten',
                    'Gâteaux sans gluten',
                    'Biscuits sans gluten',
                    'Crackers sans gluten'
                ]
            }
        },
        
        '🍷 ÉPICERIE FINE': {
            'description': 'Produits gastronomiques d\'exception',
            'sous_categories': {
                'Huiles et vinaigres': [
                    'Huile d\'olive extra-vierge',
                    'Huile de noix',
                    'Huile de truffe',
                    'Vinaigre balsamique',
                    'Vinaigre de vin',
                    'Vinaigre de Xérès'
                ],
                'Condiments': [
                    'Moutardes',
                    'Cornichons',
                    'Câpres',
                    'Olives',
                    'Tapenades',
                    'Pickles'
                ],
                'Conserves premium': [
                    'Foie gras en conserve',
                    'Confits',
                    'Cassoulet',
                    'Terrines',
                    'Plats cuisinés',
                    'Soupes gastronomiques'
                ],
                'Épices et aromates': [
                    'Safran',
                    'Vanille',
                    'Poivre rare',
                    'Fleur de sel',
                    'Herbes de Provence',
                    'Mélanges d\'épices'
                ],
                'Produits truffés': [
                    'Truffes fraîches',
                    'Brisures de truffes',
                    'Huile de truffe',
                    'Sel à la truffe',
                    'Pâtes truffées',
                    'Miel à la truffe'
                ],
                'Produits italiens': [
                    'Pâtes artisanales',
                    'Risotto',
                    'Polenta',
                    'Pesto',
                    'Tomates séchées',
                    'Grissini'
                ]
            }
        },
        
        '🍫 CONFISERIE': {
            'description': 'Chocolats et confiseries artisanales',
            'sous_categories': {
                'Chocolats': [
                    'Chocolats noirs',
                    'Chocolats au lait',
                    'Chocolats blancs',
                    'Pralinés',
                    'Ganaches',
                    'Truffes au chocolat'
                ],
                'Confiseries': [
                    'Calissons',
                    'Nougats',
                    'Pâtes de fruits',
                    'Guimauves',
                    'Caramels',
                    'Berlingots'
                ],
                'Biscuits': [
                    'Sablés',
                    'Macarons',
                    'Madeleines',
                    'Financiers',
                    'Cookies',
                    'Biscuits aux amandes'
                ],
                'Spécialités régionales': [
                    'Calissons d\'Aix',
                    'Nougat de Montélimar',
                    'Bêtises de Cambrai',
                    'Bergamotes de Nancy',
                    'Pruneaux d\'Agen',
                    'Fruits confits'
                ],
                'Chocolats de couverture': [
                    'Noir 70%',
                    'Noir 85%',
                    'Lait 40%',
                    'Blanc',
                    'Caramel',
                    'Ruby'
                ],
                'Collections': [
                    'Ballotins assortis',
                    'Coffrets cadeaux',
                    'Chocolats de Noël',
                    'Chocolats de Pâques',
                    'Éditions limitées',
                    'Créations du chef'
                ]
            }
        },
        
        '🍾 CAVE': {
            'description': 'Vins et spiritueux sélectionnés',
            'sous_categories': {
                'Vins rouges': [
                    'Bordeaux',
                    'Bourgogne',
                    'Côtes du Rhône',
                    'Languedoc',
                    'Beaujolais',
                    'Vins du Sud-Ouest'
                ],
                'Vins blancs': [
                    'Alsace',
                    'Loire',
                    'Bourgogne',
                    'Bordeaux',
                    'Côtes du Rhône',
                    'Provence'
                ],
                'Champagnes': [
                    'Brut',
                    'Rosé',
                    'Blanc de blancs',
                    'Millésimés',
                    'Cuvées prestige',
                    'Demi-sec'
                ],
                'Spiritueux': [
                    'Cognac',
                    'Armagnac',
                    'Whisky',
                    'Rhum',
                    'Gin',
                    'Vodka'
                ],
                'Apéritifs': [
                    'Porto',
                    'Pineau des Charentes',
                    'Vermouth',
                    'Pastis',
                    'Kir',
                    'Liqueurs'
                ],
                'Bières artisanales': [
                    'Blondes',
                    'Ambrées',
                    'Brunes',
                    'Blanches',
                    'IPA',
                    'Triple'
                ]
            }
        },
        
        '🥗 TRAITEUR': {
            'description': 'Plats préparés et salades',
            'sous_categories': {
                'Entrées froides': [
                    'Salades composées',
                    'Carpaccios',
                    'Tartares',
                    'Verrines',
                    'Terrines',
                    'Aspics'
                ],
                'Entrées chaudes': [
                    'Quiches',
                    'Feuilletés',
                    'Bouchées',
                    'Mini-gratins',
                    'Soufflés',
                    'Vol-au-vent'
                ],
                'Plats cuisinés': [
                    'Couscous',
                    'Paella',
                    'Blanquette',
                    'Bourguignon',
                    'Tajines',
                    'Pot-au-feu'
                ],
                'Accompagnements': [
                    'Gratins',
                    'Légumes farcis',
                    'Purées maison',
                    'Riz pilaf',
                    'Pâtes fraîches',
                    'Ratatouille'
                ],
                'Buffets': [
                    'Plateaux apéritifs',
                    'Plateaux de fromages',
                    'Plateaux de charcuterie',
                    'Plateaux de fruits de mer',
                    'Cocktails dinatoires',
                    'Buffets froids'
                ],
                'Desserts': [
                    'Tiramisus',
                    'Mousses au chocolat',
                    'Crèmes brûlées',
                    'Îles flottantes',
                    'Tartes maison',
                    'Verrines sucrées'
                ]
            }
        },
        
        '🌱 BIO & SANTÉ': {
            'description': 'Produits biologiques et diététiques',
            'sous_categories': {
                'Fruits et légumes bio': [
                    'Légumes de saison',
                    'Fruits de saison',
                    'Herbes aromatiques',
                    'Champignons',
                    'Graines germées',
                    'Micro-pousses'
                ],
                'Produits laitiers bio': [
                    'Lait',
                    'Yaourts',
                    'Fromages bio',
                    'Beurre',
                    'Crème fraîche',
                    'Fromage blanc'
                ],
                'Céréales et légumineuses': [
                    'Riz bio',
                    'Quinoa',
                    'Lentilles',
                    'Pois chiches',
                    'Haricots',
                    'Graines'
                ],
                'Sans gluten': [
                    'Pains',
                    'Pâtes',
                    'Farines',
                    'Biscuits',
                    'Céréales',
                    'Snacks'
                ],
                'Végétarien/Vegan': [
                    'Tofu',
                    'Tempeh',
                    'Seitan',
                    'Laits végétaux',
                    'Alternatives fromages',
                    'Protéines végétales'
                ],
                'Superaliments': [
                    'Baies de goji',
                    'Spiruline',
                    'Graines de chia',
                    'Açaï',
                    'Matcha',
                    'Maca'
                ]
            }
        },
        
        '🍽️ ARTS DE LA TABLE': {
            'description': 'Accessoires et décoration',
            'sous_categories': {
                'Vaisselle': [
                    'Assiettes',
                    'Plats de service',
                    'Bols',
                    'Tasses',
                    'Mugs',
                    'Services complets'
                ],
                'Couverts': [
                    'Couverts en inox',
                    'Couverts dorés',
                    'Couverts argent',
                    'Couverts à poisson',
                    'Couverts à dessert',
                    'Services complets'
                ],
                'Verrerie': [
                    'Verres à vin',
                    'Verres à eau',
                    'Flûtes à champagne',
                    'Verres à whisky',
                    'Carafes',
                    'Services'
                ],
                'Linge de table': [
                    'Nappes',
                    'Serviettes',
                    'Sets de table',
                    'Chemins de table',
                    'Torchons',
                    'Tabliers'
                ],
                'Ustensiles': [
                    'Couteaux',
                    'Planches à découper',
                    'Tire-bouchons',
                    'Ouvre-huîtres',
                    'Accessoires fromage',
                    'Accessoires cocktail'
                ],
                'Décoration': [
                    'Bougeoirs',
                    'Vases',
                    'Centres de table',
                    'Porte-menus',
                    'Marque-places',
                    'Décorations saisonnières'
                ]
            }
        }
    }
    
    # Compteurs
    total_cat = 0
    total_sous_cat = 0
    total_sous_sous_cat = 0
    
    # Création des catégories
    for ordre_cat, (nom_cat, data_cat) in enumerate(categories_data.items(), 1):
        # Créer/Récupérer la catégorie principale
        categorie, created = Categorie.objects.get_or_create(
            nom=nom_cat,
            defaults={
                'description': data_cat['description'],
                'ordre': ordre_cat,
                'est_active': True
            }
        )
        
        if created:
            total_cat += 1
            print(f"\n✅ Catégorie créée : {nom_cat}")
        else:
            print(f"\n⏭️  Catégorie existante : {nom_cat}")
        
        # Créer les sous-catégories
        for ordre_sous, (nom_sous, liste_sous_sous) in enumerate(data_cat['sous_categories'].items(), 1):
            sous_categorie, created_sous = SousCategorie.objects.get_or_create(
                nom=nom_sous,
                categorie=categorie,
                defaults={
                    'ordre': ordre_sous,
                    'est_active': True
                }
            )
            
            if created_sous:
                total_sous_cat += 1
                print(f"   └─ ✅ Sous-catégorie créée : {nom_sous}")
            else:
                print(f"   └─ ⏭️  Sous-catégorie existante : {nom_sous}")
            
            # Créer les sous-sous-catégories
            for ordre_sous_sous, nom_sous_sous in enumerate(liste_sous_sous, 1):
                sous_sous_categorie, created_sous_sous = SousSousCategorie.objects.get_or_create(
                    nom=nom_sous_sous,
                    sous_categorie=sous_categorie,
                    defaults={
                        'ordre': ordre_sous_sous,
                        'est_active': True
                    }
                )
                
                if created_sous_sous:
                    total_sous_sous_cat += 1
                    print(f"      └─ ✅ Sous-sous-catégorie créée : {nom_sous_sous}")
                else:
                    print(f"      └─ ⏭️  Sous-sous-catégorie existante : {nom_sous_sous}")
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA CRÉATION")
    print("=" * 60)
    print(f"✅ Catégories créées : {total_cat}")
    print(f"✅ Sous-catégories créées : {total_sous_cat}")
    print(f"✅ Sous-sous-catégories créées : {total_sous_sous_cat}")
    print(f"📁 Total catégories : {Categorie.objects.count()}")
    print(f"📁 Total sous-catégories : {SousCategorie.objects.count()}")
    print(f"📁 Total sous-sous-catégories : {SousSousCategorie.objects.count()}")
    print("=" * 60)
    print("✨ Création terminée avec succès !\n")

# Exécution
if __name__ == '__main__':
    create_all_categories()
