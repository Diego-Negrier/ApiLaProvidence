# fournisseur/management/commands/generate_fournisseurs_improved.py

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction
from decimal import Decimal
from fournisseur.models import Fournisseur
import random


class Command(BaseCommand):
    help = '👨‍🌾 Génère des fournisseurs cohérents avec la structure de catégories La Providence'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nombre',
            type=int,
            default=30,
            help='Nombre de fournisseurs à créer (défaut: 30)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Supprimer tous les fournisseurs existants avant de générer'
        )

    def handle(self, *args, **options):
        nombre = options['nombre']
        clean = options['clean']

        if clean:
            self.stdout.write(self.style.WARNING('🗑️  Suppression des fournisseurs existants...'))
            Fournisseur.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Fournisseurs supprimés'))

        self.stdout.write(self.style.WARNING(f'🚀 Génération de {nombre} fournisseurs...'))

        # ===================================
        # DONNÉES RÉALISTES ET COHÉRENTES
        # ===================================

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

        # Métiers cohérents avec nos catégories
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

        # ===================================
        # GÉNÉRATION
        # ===================================

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

                    if Fournisseur.objects.filter(email=email).exists():
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

        # RÉSUMÉ
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'🎉 {fournisseurs_crees} fournisseurs créés'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total dans la base : {Fournisseur.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
