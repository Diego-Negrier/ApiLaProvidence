"""

Command Django pour générer automatiquement des produits avec images

Usage: python manage.py generer_produits --nombre=50

"""

 

import random

import requests

from io import BytesIO

from decimal import Decimal

from django.core.management.base import BaseCommand

from django.core.files import File

from django.db import transaction

from produits.models import Produit, Categorie, SousCategorie, SousSousCategorie, ImageProduit

from fournisseur.models import Fournisseur

 

 

class Command(BaseCommand):

    help = 'Génère automatiquement des produits avec des images depuis Unsplash'

 

    def add_arguments(self, parser):

        parser.add_argument(

            '--nombre',

            type=int,

            default=20,

            help='Nombre de produits à générer (défaut: 20)'

        )

        parser.add_argument(

            '--clean',

            action='store_true',

            help='Supprimer tous les produits existants avant de générer'

        )

 

    def handle(self, *args, **options):

        nombre = options['nombre']

        clean = options['clean']

 

        if clean:

            self.stdout.write(self.style.WARNING('Suppression des produits existants...'))

            Produit.objects.all().delete()

            self.stdout.write(self.style.SUCCESS('✓ Produits supprimés'))

 

        self.stdout.write(self.style.SUCCESS(f'Génération de {nombre} produits...'))



        # Créer les catégories de base si elles n'existent pas

        categories = self._creer_categories()



        # Récupérer ou créer des fournisseurs

        fournisseurs = self._obtenir_fournisseurs()



        if not fournisseurs:

            self.stdout.write(self.style.ERROR('❌ Aucun fournisseur disponible'))

            return



        self.stdout.write(self.style.SUCCESS(f'✓ {len(fournisseurs)} fournisseur(s) disponible(s)'))



        # Générer les produits

        produits_crees = 0

        for i in range(nombre):

            try:

                with transaction.atomic():

                    # Choisir un fournisseur aléatoire pour chaque produit

                    fournisseur = random.choice(fournisseurs)

                    produit = self._generer_produit(i + 1, categories, fournisseur)

                    produits_crees += 1

                    self.stdout.write(

                        self.style.SUCCESS(f'✓ [{produits_crees}/{nombre}] {produit.nom}')

                    )

            except Exception as e:

                self.stdout.write(

                    self.style.ERROR(f'✗ Erreur lors de la génération du produit {i + 1}: {str(e)}')

                )

 

        self.stdout.write(

            self.style.SUCCESS(f'\n✓ {produits_crees} produits créés avec succès!')

        )

 

    def _creer_categories(self):

        """Crée les catégories de base"""

        categories_data = [

            {

                'nom': 'Fruits & Légumes',

                'icone': '🥬',

                'sous_categories': [

                    {'nom': 'Fruits frais', 'icone': '🍎'},

                    {'nom': 'Légumes frais', 'icone': '🥕'},

                    {'nom': 'Fruits secs', 'icone': '🥜'},

                ]

            },

            {

                'nom': 'Produits laitiers',

                'icone': '🥛',

                'sous_categories': [

                    {'nom': 'Fromages', 'icone': '🧀'},

                    {'nom': 'Yaourts', 'icone': '🥛'},

                    {'nom': 'Beurre & Crème', 'icone': '🧈'},

                ]

            },

            {

                'nom': 'Boulangerie',

                'icone': '🍞',

                'sous_categories': [

                    {'nom': 'Pain', 'icone': '🥖'},

                    {'nom': 'Viennoiseries', 'icone': '🥐'},

                    {'nom': 'Pâtisseries', 'icone': '🍰'},

                ]

            },

            {

                'nom': 'Épicerie',

                'icone': '🥫',

                'sous_categories': [

                    {'nom': 'Pâtes & Riz', 'icone': '🍝'},

                    {'nom': 'Conserves', 'icone': '🥫'},

                    {'nom': 'Huiles & Condiments', 'icone': '🫗'},

                ]

            },

            {

                'nom': 'Boissons',

                'icone': '🥤',

                'sous_categories': [

                    {'nom': 'Jus de fruits', 'icone': '🧃'},

                    {'nom': 'Eaux', 'icone': '💧'},

                    {'nom': 'Vins & Spiritueux', 'icone': '🍷'},

                    {'nom': 'Cafés & Thés', 'icone': '☕'},

                ]

            },

            {

                'nom': 'Viandes & Poissons',

                'icone': '🥩',

                'sous_categories': [

                    {'nom': 'Viandes fraîches', 'icone': '🥩'},

                    {'nom': 'Volailles', 'icone': '🍗'},

                    {'nom': 'Poissons & Fruits de mer', 'icone': '🐟'},

                    {'nom': 'Charcuterie', 'icone': '🥓'},

                ]

            },

            {

                'nom': 'Surgelés',

                'icone': '❄️',

                'sous_categories': [

                    {'nom': 'Légumes surgelés', 'icone': '🥦'},

                    {'nom': 'Plats préparés', 'icone': '🍲'},

                    {'nom': 'Glaces & Desserts', 'icone': '🍨'},

                ]

            },

            {

                'nom': 'Snacks & Confiseries',

                'icone': '🍫',

                'sous_categories': [

                    {'nom': 'Chocolats', 'icone': '🍫'},

                    {'nom': 'Bonbons & Friandises', 'icone': '🍬'},

                    {'nom': 'Biscuits & Gâteaux', 'icone': '🍪'},

                    {'nom': 'Chips & Apéritifs', 'icone': '🥜'},

                ]

            },

            {

                'nom': 'Bio & Diététique',

                'icone': '🌱',

                'sous_categories': [

                    {'nom': 'Produits bio', 'icone': '🌱'},

                    {'nom': 'Sans gluten', 'icone': '🌾'},

                    {'nom': 'Végétarien & Vegan', 'icone': '🥗'},

                    {'nom': 'Compléments alimentaires', 'icone': '💊'},

                ]

            },

            {

                'nom': 'Matériaux de Construction',

                'icone': '🏗️',

                'sous_categories': [

                    {'nom': 'Matériaux naturels', 'icone': '🌾'},

                    {'nom': 'Isolation écologique', 'icone': '🧱'},

                    {'nom': 'Bois & Charpente', 'icone': '🪵'},

                    {'nom': 'Pierre & Terre', 'icone': '🪨'},

                ]

            },

            {

                'nom': 'Énergie & Écologie',

                'icone': '⚡',

                'sous_categories': [

                    {'nom': 'Panneaux solaires', 'icone': '☀️'},

                    {'nom': 'Éoliennes', 'icone': '💨'},

                    {'nom': 'Batteries & Stockage', 'icone': '🔋'},

                    {'nom': 'Chauffage écologique', 'icone': '🔥'},

                ]

            },

        ]

 

        categories = []

        for cat_data in categories_data:

            categorie, created = Categorie.objects.get_or_create(

                nom=cat_data['nom'],

                defaults={

                    'icone': cat_data['icone'],

                    'description': f'Catégorie {cat_data["nom"]}',

                    'est_active': True,

                }

            )

 

            # Créer les sous-catégories

            for sous_cat_data in cat_data['sous_categories']:

                SousCategorie.objects.get_or_create(

                    nom=sous_cat_data['nom'],

                    categorie=categorie,

                    defaults={

                        'icone': sous_cat_data['icone'],

                        'description': f'Sous-catégorie {sous_cat_data["nom"]}',

                        'est_active': True,

                    }

                )

 

            categories.append(categorie)

 

        return categories

 

    def _obtenir_fournisseurs(self):

        """Récupère les fournisseurs existants ou en crée quelques-uns par défaut"""

        # Vérifier s'il y a déjà des fournisseurs

        fournisseurs_existants = list(Fournisseur.objects.all())



        if fournisseurs_existants:

            self.stdout.write(

                self.style.SUCCESS(f'✓ Utilisation de {len(fournisseurs_existants)} fournisseur(s) existant(s)')

            )

            return fournisseurs_existants



        # Créer des fournisseurs par défaut

        self.stdout.write(self.style.WARNING('⚠ Aucun fournisseur trouvé, création de fournisseurs par défaut...'))



        fournisseurs_data = [

            {

                'nom': 'Dubois',

                'prenom': 'Jean',

                'email': 'jean.dubois@ferme-terroir.fr',

                'metier': 'Agriculteur',

                'contact': 'Jean Dubois',

                'ville': 'Lyon',

            },

            {

                'nom': 'Martin',

                'prenom': 'Sophie',

                'email': 'sophie.martin@bio-provence.fr',

                'metier': 'Maraîchère',

                'contact': 'Sophie Martin',

                'ville': 'Avignon',

            },

            {

                'nom': 'Bernard',

                'prenom': 'Pierre',

                'email': 'pierre.bernard@fromagerie.fr',

                'metier': 'Fromager',

                'contact': 'Pierre Bernard',

                'ville': 'Roquefort',

            },

            {

                'nom': 'Leroy',

                'prenom': 'Marie',

                'email': 'marie.leroy@boulangerie-artisanale.fr',

                'metier': 'Boulangère',

                'contact': 'Marie Leroy',

                'ville': 'Paris',

            },

            {

                'nom': 'Moreau',

                'prenom': 'Thomas',

                'email': 'thomas.moreau@vins-loire.fr',

                'metier': 'Viticulteur',

                'contact': 'Thomas Moreau',

                'ville': 'Tours',

            },

        ]



        fournisseurs = []

        for data in fournisseurs_data:

            try:

                fournisseur = Fournisseur.objects.create(

                    nom=data['nom'],

                    prenom=data['prenom'],

                    email=data['email'],

                    tel='0123456789',

                    metier=data['metier'],

                    contact=data['contact'],

                    adresse=f'123 Route de la Campagne',

                    ville=data['ville'],

                    code_postal='69000',

                    pays='France',

                    password='pbkdf2_sha256$870000$default$hash',

                )

                fournisseurs.append(fournisseur)

                self.stdout.write(self.style.SUCCESS(f'  ✓ Fournisseur créé: {data["prenom"]} {data["nom"]}'))

            except Exception as e:

                self.stdout.write(self.style.ERROR(f'  ✗ Erreur: {str(e)}'))



        return fournisseurs

 

    def _generer_produit(self, index, categories, fournisseur):

        """Génère un produit aléatoire"""

 

        # Produits templates par catégorie

        produits_templates = {

            'Fruits & Légumes': [

                'Pommes bio', 'Tomates cerises', 'Carottes', 'Salade verte',

                'Pommes de terre', 'Courgettes', 'Aubergines', 'Poivrons',

                'Bananes', 'Oranges', 'Citrons', 'Fraises'

            ],

            'Produits laitiers': [

                'Fromage de chèvre', 'Camembert', 'Comté', 'Roquefort',

                'Yaourt nature', 'Yaourt aux fruits', 'Beurre doux', 'Crème fraîche'

            ],

            'Boulangerie': [

                'Baguette tradition', 'Pain complet', 'Croissant', 'Pain au chocolat',

                'Brioche', 'Pain de campagne', 'Ficelle', 'Baguette aux céréales'

            ],

            'Épicerie': [

                'Pâtes italiennes', 'Riz basmati', 'Huile d\'olive', 'Sauce tomate',

                'Miel de provence', 'Confiture de fraises', 'Thon en conserve', 'Haricots verts'

            ],

            'Boissons': [

                'Jus d\'orange', 'Eau minérale', 'Vin rouge', 'Cidre artisanal',

                'Jus de pomme', 'Eau gazeuse', 'Sirop de menthe', 'Thé vert',

                'Café arabica', 'Tisane verveine', 'Bière artisanale', 'Champagne brut'

            ],

            'Viandes & Poissons': [

                'Bœuf haché', 'Côte de bœuf', 'Poulet fermier', 'Escalope de dinde',

                'Saumon frais', 'Truite arc-en-ciel', 'Crevettes roses', 'Jambon blanc',

                'Saucisson sec', 'Pâté de campagne', 'Rillettes', 'Bacon fumé'

            ],

            'Surgelés': [

                'Haricots verts surgelés', 'Petits pois', 'Épinards en branches', 'Ratatouille',

                'Lasagnes bolognaise', 'Pizza margherita', 'Glace vanille', 'Sorbet framboise',

                'Crème glacée chocolat', 'Tarte aux pommes', 'Beignets surgelés', 'Frites'

            ],

            'Snacks & Confiseries': [

                'Chocolat noir 70%', 'Chocolat au lait', 'Tablette noisettes', 'Bonbons gélifiés',

                'Caramels au beurre salé', 'Sucettes', 'Cookies pépites chocolat', 'Madeleines',

                'Sablés bretons', 'Chips nature', 'Chips saveur barbecue', 'Cacahuètes salées',

                'Amandes grillées', 'Noix de cajou', 'Pop-corn caramel', 'Biscuits apéritif'

            ],

            'Bio & Diététique': [

                'Quinoa bio', 'Graines de chia', 'Lait d\'amande bio', 'Tofu nature',

                'Steak végétal', 'Pain sans gluten', 'Pâtes sans gluten', 'Muesli bio',

                'Barres protéinées', 'Spiruline', 'Comprimés vitamine C', 'Tisane détox',

                'Huile de coco bio', 'Sirop d\'agave', 'Sucre de coco', 'Farine de sarrasin'

            ],

            'Matériaux de Construction': [

                'Paille de construction', 'Bottes de paille', 'Briques de terre crue', 'Briques monomur',

                'Pierre naturelle', 'Pierre de taille', 'Ardoise naturelle', 'Tuiles en terre cuite',

                'Bois de charpente', 'Poutres en chêne', 'Planches de pin', 'Madriers douglas',

                'Laine de bois', 'Chanvre isolant', 'Ouate de cellulose', 'Liège expansé',

                'Torchis', 'Enduit à la chaux', 'Plâtre naturel', 'Mortier écologique'

            ],

            'Énergie & Écologie': [

                'Panneau solaire 300W', 'Kit solaire autonome', 'Onduleur photovoltaïque', 'Panneau monocristallin',

                'Éolienne domestique', 'Micro-éolienne 1kW', 'Kit éolien complet', 'Régulateur éolien',

                'Batterie lithium 12V', 'Batterie gel solaire', 'Pack batteries 48V', 'Convertisseur 12V-220V',

                'Poêle à granulés', 'Chaudière biomasse', 'Insert à bois', 'Récupérateur de chaleur',

                'Chauffe-eau solaire', 'Pompe à chaleur', 'Ballon thermodynamique', 'Régulateur de charge'

            ],

        }

 

        # Choisir une catégorie aléatoire

        categorie = random.choice(categories)

        templates = produits_templates.get(categorie.nom, ['Produit artisanal'])

        nom_base = random.choice(templates)

        nom = f"{nom_base} #{index}"

 

        # Choisir une sous-catégorie si disponible

        sous_categories = list(categorie.souscategories.filter(est_active=True))

        sous_categorie = random.choice(sous_categories) if sous_categories else None

 

        # Prix aléatoire

        prix_ht = Decimal(random.uniform(2.0, 50.0)).quantize(Decimal('0.01'))

        tva = Decimal('5.5') if 'bio' in nom_base.lower() else Decimal('20.0')

 

        # Stock aléatoire

        stock = random.randint(10, 200)

 

        # Caractéristiques aléatoires

        est_bio = random.choice([True, False])

        est_local = random.choice([True, False])

        est_nouveaute = random.choice([True, False, False])  # 33% de chance

        en_promotion = random.choice([True, False, False, False])  # 25% de chance

 

        # Créer le produit

        produit = Produit.objects.create(

            nom=nom,

            description_courte=f"{nom_base} de qualité supérieure",

            description_longue=f"""

            {nom_base} sélectionné avec soin pour sa qualité exceptionnelle.

 

            Caractéristiques:

            - Origine: France

            - Qualité: Premium

            {'- Label: Agriculture Biologique' if est_bio else ''}

            {'- Production locale' if est_local else ''}

 

            Conditionnement adapté pour une fraîcheur optimale.

            """,

            prix_ht=prix_ht,

            tva=tva,

            categorie=categorie,

            souscategorie=sous_categorie,

            fournisseur=fournisseur,

            stock_actuel=stock,

            stock_minimum=10,

            est_actif=True,

            est_bio=est_bio,

            est_local=est_local,

            est_nouveaute=est_nouveaute,

            en_promotion=en_promotion,

            pourcentage_promotion=Decimal('10.0') if en_promotion else Decimal('0.0'),

            poids=random.randint(100, 2000),

            unite_mesure=random.choice(['g', 'kg', 'L', 'pièce']),

            origine='France',

            statut='disponible',

        )

 

        # Télécharger et associer une image depuis Unsplash

        self._ajouter_image(produit, nom_base)

        # Ajouter des images additionnelles (2 à 4 images)

        nombre_images = random.randint(2, 4)

        self._ajouter_images_additionnelles(produit, nom_base, nombre_images)



        return produit

 

    def _ajouter_image(self, produit, keyword):

        """Télécharge et ajoute une image thématique de nourriture depuis Foodish API ou placeholder.com"""

        try:

            # Mapper les mots-clés aux catégories d'aliments de l'API Foodish
            foodish_categories = {
                'pomme': 'apple-pie', 'poire': 'apple-pie', 'fruits': 'apple-pie',
                'pain': 'bread', 'baguette': 'bread', 'brioche': 'bread',
                'burger': 'burger', 'viande': 'burger', 'bœuf': 'burger', 'boeuf': 'burger',
                'beurre': 'butter', 'crème': 'butter',
                'dessert': 'dessert', 'gâteau': 'dessert', 'tarte': 'dessert', 'madeleine': 'dessert',
                'oeuf': 'egg', 'omelette': 'egg',
                'fromage': 'cheese', 'comté': 'cheese', 'camembert': 'cheese',
                'pizza': 'pizza',
                'pâtes': 'pasta', 'spaghetti': 'pasta', 'lasagnes': 'pasta',
                'riz': 'rice',
                'poulet': 'chicken', 'volaille': 'chicken', 'dinde': 'chicken',
                'poisson': 'seafood', 'saumon': 'seafood', 'truite': 'seafood', 'crevettes': 'seafood',
                'salade': 'salad', 'légumes': 'salad', 'tomate': 'salad',
                'soupe': 'soup',
                'sandwich': 'sandwich',
                'donuts': 'dosa', 'beignet': 'dosa',
                'glace': 'icecream', 'sorbet': 'icecream',
                'chocolat': 'dessert',
                'chips': 'burger',  # Pas de catégorie spécifique, utiliser burger comme fallback
                'frites': 'burger'
            }

            # Trouver une catégorie correspondante
            category = None
            keyword_lower = keyword.lower()
            for key, cat in foodish_categories.items():
                if key in keyword_lower:
                    category = cat
                    break

            # Si on a trouvé une catégorie, utiliser Foodish API
            if category:
                url = f'https://foodish-api.com/api/images/{category}'
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get('image')
                    if image_url:
                        # Télécharger l'image depuis l'URL retournée
                        img_response = requests.get(image_url, timeout=10, allow_redirects=True)
                        if img_response.status_code == 200:
                            image_data = img_response.content
                        else:
                            # Fallback sur placeholder
                            url = f'https://via.placeholder.com/800x600/4CAF50/FFFFFF?text={keyword[:20]}'
                            response = requests.get(url, timeout=10, allow_redirects=True)
                            image_data = response.content if response.status_code == 200 else None
                    else:
                        url = f'https://via.placeholder.com/800x600/4CAF50/FFFFFF?text={keyword[:20]}'
                        response = requests.get(url, timeout=10, allow_redirects=True)
                        image_data = response.content if response.status_code == 200 else None
                else:
                    # Fallback sur placeholder avec texte
                    url = f'https://via.placeholder.com/800x600/4CAF50/FFFFFF?text={keyword[:20]}'
                    response = requests.get(url, timeout=10, allow_redirects=True)
                    image_data = response.content if response.status_code == 200 else None
            else:
                # Pas de catégorie alimentaire trouvée, créer un placeholder thématique
                # Déterminer la couleur et le style selon le type de produit
                keyword_lower = keyword.lower()

                # Matériaux de construction - tons naturels
                if any(word in keyword_lower for word in ['brique', 'pierre', 'paille', 'bois', 'terre', 'charpente', 'tuile', 'ardoise']):
                    color_bg = '8B7355'  # Marron terre
                    color_text = 'FFFFFF'
                    icon = '🏗️'
                # Isolation - tons clairs
                elif any(word in keyword_lower for word in ['laine', 'chanvre', 'ouate', 'liège', 'isolant']):
                    color_bg = 'D4A574'  # Beige
                    color_text = '000000'
                    icon = '🧊'
                # Énergie solaire - tons jaunes/orange
                elif any(word in keyword_lower for word in ['panneau', 'solaire', 'photovoltaïque', 'photovoltaique']):
                    color_bg = 'FFA500'  # Orange
                    color_text = 'FFFFFF'
                    icon = '☀️'
                # Éoliennes - tons bleus
                elif any(word in keyword_lower for word in ['éolienne', 'eolienne', 'éolien', 'eolien']):
                    color_bg = '1E90FF'  # Bleu
                    color_text = 'FFFFFF'
                    icon = '💨'
                # Batteries et électrique - tons gris foncé
                elif any(word in keyword_lower for word in ['batterie', 'lithium', 'convertisseur', 'onduleur', 'régulateur', 'regulateur']):
                    color_bg = '696969'  # Gris foncé
                    color_text = 'FFFFFF'
                    icon = '🔋'
                # Chauffage - tons rouges/orangés
                elif any(word in keyword_lower for word in ['poêle', 'poele', 'chaudière', 'chaudiere', 'chauffage', 'granulés', 'granules', 'insert']):
                    color_bg = 'DC143C'  # Rouge
                    color_text = 'FFFFFF'
                    icon = '🔥'
                # Produits bio/diététique - tons verts
                elif any(word in keyword_lower for word in ['bio', 'quinoa', 'tofu', 'végétal', 'vegetal', 'gluten', 'spiruline']):
                    color_bg = '228B22'  # Vert forêt
                    color_text = 'FFFFFF'
                    icon = '🌱'
                # Par défaut - vert standard
                else:
                    color_bg = '4CAF50'
                    color_text = 'FFFFFF'
                    icon = '📦'

                # Créer un texte plus court et lisible
                product_name = keyword[:25] if len(keyword) <= 25 else keyword[:22] + '...'
                # Encoder le texte pour l'URL
                import urllib.parse
                encoded_text = urllib.parse.quote(f'{icon} {product_name}')

                url = f'https://via.placeholder.com/800x600/{color_bg}/{color_text}?text={encoded_text}'
                response = requests.get(url, timeout=10, allow_redirects=True)
                image_data = response.content if response.status_code == 200 else None

            if image_data:



                # 1. Sauvegarder l'image principale sur le produit

                image_content = BytesIO(image_data)

                file_name = f'produit_{produit.pk}_{random.randint(1000, 9999)}.jpg'

                produit.image_principale.save(

                    file_name,

                    File(image_content),

                    save=True

                )

                self.stdout.write(f'  → Image principale ajoutée: {file_name}')



                # 2. Créer aussi un objet ImageProduit avec la même image

                try:

                    # Réutiliser les mêmes données d'image

                    image_content2 = BytesIO(image_data)

                    file_name2 = f'produit_{produit.pk}_principale_{random.randint(1000, 9999)}.jpg'



                    # Créer l'objet ImageProduit

                    image_produit = ImageProduit.objects.create(

                        produit=produit,

                        legende='Image principale',

                        ordre=0,  # Ordre 0 pour qu'elle soit en premier

                        est_principale=True

                    )



                    image_produit.image.save(

                        file_name2,

                        File(image_content2),

                        save=True

                    )



                    self.stdout.write(f'  → Image principale ajoutée à la galerie (ImageProduit créé)')



                except Exception as e:

                    self.stdout.write(

                        self.style.WARNING(f'  ⚠ Erreur ajout image principale à la galerie: {str(e)}')

                    )



        except Exception as e:

            self.stdout.write(

                self.style.WARNING(f'  ⚠ Impossible de télécharger l\'image: {str(e)}')

            )



    def _ajouter_images_additionnelles(self, produit, keyword, nombre):

        """Télécharge et ajoute plusieurs images additionnelles depuis picsum.photos"""

        try:

            # Légendes possibles pour les images

            legendes = [

                'Vue détaillée du produit',

                'Présentation du produit',

                'Vue d\'ensemble',

                'Gros plan',

                'Packaging du produit',

                'Produit en situation'

            ]



            for i in range(nombre):

                try:

                    # Utiliser la même logique que pour l'image principale
                    foodish_categories = {
                        'pomme': 'apple-pie', 'poire': 'apple-pie', 'fruits': 'apple-pie',
                        'pain': 'bread', 'baguette': 'bread', 'brioche': 'bread',
                        'burger': 'burger', 'viande': 'burger', 'bœuf': 'burger', 'boeuf': 'burger',
                        'beurre': 'butter', 'crème': 'butter',
                        'dessert': 'dessert', 'gâteau': 'dessert', 'tarte': 'dessert', 'madeleine': 'dessert',
                        'oeuf': 'egg', 'omelette': 'egg',
                        'fromage': 'cheese', 'comté': 'cheese', 'camembert': 'cheese',
                        'pizza': 'pizza',
                        'pâtes': 'pasta', 'spaghetti': 'pasta', 'lasagnes': 'pasta',
                        'riz': 'rice',
                        'poulet': 'chicken', 'volaille': 'chicken', 'dinde': 'chicken',
                        'poisson': 'seafood', 'saumon': 'seafood', 'truite': 'seafood', 'crevettes': 'seafood',
                        'salade': 'salad', 'légumes': 'salad', 'tomate': 'salad',
                        'soupe': 'soup',
                        'sandwich': 'sandwich',
                        'donuts': 'dosa', 'beignet': 'dosa',
                        'glace': 'icecream', 'sorbet': 'icecream',
                        'chocolat': 'dessert',
                        'chips': 'burger',
                        'frites': 'burger'
                    }

                    # Trouver une catégorie correspondante
                    category = None
                    keyword_lower = keyword.lower()
                    for key, cat in foodish_categories.items():
                        if key in keyword_lower:
                            category = cat
                            break

                    # Si on a trouvé une catégorie, utiliser Foodish API
                    if category:
                        url = f'https://foodish-api.com/api/images/{category}'
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            image_url = data.get('image')
                            if image_url:
                                response = requests.get(image_url, timeout=10, allow_redirects=True)
                            else:
                                url = f'https://via.placeholder.com/800x600/4CAF50/FFFFFF?text={keyword[:15]}'
                                response = requests.get(url, timeout=10, allow_redirects=True)
                        else:
                            url = f'https://via.placeholder.com/800x600/4CAF50/FFFFFF?text={keyword[:15]}'
                            response = requests.get(url, timeout=10, allow_redirects=True)
                    else:
                        # Pas de catégorie alimentaire trouvée, créer un placeholder thématique
                        keyword_lower = keyword.lower()

                        # Matériaux de construction
                        if any(word in keyword_lower for word in ['brique', 'pierre', 'paille', 'bois', 'terre', 'charpente', 'tuile', 'ardoise']):
                            color_bg = '8B7355'
                            color_text = 'FFFFFF'
                            icon = '🏗️'
                        # Isolation
                        elif any(word in keyword_lower for word in ['laine', 'chanvre', 'ouate', 'liège', 'isolant']):
                            color_bg = 'D4A574'
                            color_text = '000000'
                            icon = '🧊'
                        # Énergie solaire
                        elif any(word in keyword_lower for word in ['panneau', 'solaire', 'photovoltaïque', 'photovoltaique']):
                            color_bg = 'FFA500'
                            color_text = 'FFFFFF'
                            icon = '☀️'
                        # Éoliennes
                        elif any(word in keyword_lower for word in ['éolienne', 'eolienne']):
                            color_bg = '1E90FF'
                            color_text = 'FFFFFF'
                            icon = '💨'
                        # Batteries
                        elif any(word in keyword_lower for word in ['batterie', 'lithium', 'convertisseur', 'onduleur', 'régulateur', 'regulateur']):
                            color_bg = '696969'
                            color_text = 'FFFFFF'
                            icon = '🔋'
                        # Chauffage
                        elif any(word in keyword_lower for word in ['poêle', 'poele', 'chaudière', 'chaudiere', 'chauffage', 'granulés', 'granules']):
                            color_bg = 'DC143C'
                            color_text = 'FFFFFF'
                            icon = '🔥'
                        # Bio
                        elif any(word in keyword_lower for word in ['bio', 'quinoa', 'tofu', 'végétal', 'vegetal', 'gluten', 'spiruline']):
                            color_bg = '228B22'
                            color_text = 'FFFFFF'
                            icon = '🌱'
                        else:
                            color_bg = '4CAF50'
                            color_text = 'FFFFFF'
                            icon = '📦'

                        product_name = keyword[:20] if len(keyword) <= 20 else keyword[:17] + '...'
                        import urllib.parse
                        encoded_text = urllib.parse.quote(f'{icon} {product_name}')
                        url = f'https://via.placeholder.com/800x600/{color_bg}/{color_text}?text={encoded_text}'
                        response = requests.get(url, timeout=10, allow_redirects=True)

                    if response.status_code == 200:

                        # Créer un fichier Django depuis le contenu téléchargé

                        image_content = BytesIO(response.content)

                        file_name = f'produit_{produit.pk}_add_{i}_{random.randint(1000, 9999)}.jpg'



                        # Créer une ImageProduit

                        image_produit = ImageProduit.objects.create(

                            produit=produit,

                            legende=random.choice(legendes),

                            ordre=i + 1,

                            est_principale=False

                        )



                        image_produit.image.save(

                            file_name,

                            File(image_content),

                            save=True

                        )



                        self.stdout.write(f'  → Image additionnelle {i+1}/{nombre} ajoutée: {file_name}')



                except Exception as e:

                    self.stdout.write(

                        self.style.WARNING(f'  ⚠ Erreur image additionnelle {i+1}: {str(e)}')

                    )



        except Exception as e:

            self.stdout.write(

                self.style.WARNING(f'  ⚠ Erreur lors de l\'ajout des images additionnelles: {str(e)}')

            )