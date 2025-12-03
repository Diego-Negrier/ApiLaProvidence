from django.db import models
import os 
import uuid
import secrets
from django.dispatch import receiver
import qrcode
from django.utils.safestring import mark_safe
from django.utils import timezone
import stat

from django.urls import reverse
import logging
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


logger = logging.getLogger(__name__)
ENV = os.getenv('ENV', 'local')  # Définit l'environnement par défaut à 'local'

# Définir les chemins MEDIA_ROOT dynamiquement
if ENV == 'production':
    BASE_MEDIA_PATH = "/volume1/web/web_images/OcciDelice/media/"
else:
    BASE_MEDIA_PATH = "/Users/diego-negrier/Pictures/SynologyDrive/web_images/OcciDelice/media/"

# Create your models here.
# ---------------------------- MODELE CATEGORIE ----------------------------
class Categorie(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom
    
class SousCategorie(models.Model):
    nom = models.CharField(max_length=255)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='sous_categories')
    
    def __str__(self):
        return f"{self.categorie.nom} - {self.nom}"
def produit_image_upload_path(instance, filename):
    """Génère le chemin relatif pour l'image du produit."""
    
    # Nettoyer le nom du produit
    clean_nom = "".join(e for e in instance.nom if e.isalnum() or e in ['-', '_']) or "produit_sans_nom"

    try:
        # Vérifier si le produit existe déjà dans la base de données
        produit_existant = Produit.objects.get(nom=instance.nom)
        unique_number = produit_existant.numero_unique  # Utiliser le numéro unique existant
    except ObjectDoesNotExist:
        # Si le produit n'existe pas, générer un nouveau numéro unique
        unique_number = instance.numero_unique or str(uuid.uuid4())

    # Construire le chemin relatif
    dir_path = f"produits/{clean_nom}-{unique_number}"
    full_dir_path = os.path.join(BASE_MEDIA_PATH, dir_path)

    # Créer les répertoires si nécessaire
    if not os.path.exists(full_dir_path):
        os.makedirs(full_dir_path, exist_ok=True)
        # Appliquer les permissions 777 sur le répertoire
        os.chmod(full_dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    # Chemin complet pour le fichier
    image_path = os.path.join(dir_path, filename)
    image_full_path = os.path.join(BASE_MEDIA_PATH, image_path)

    # Retourner le chemin relatif pour stockage
    return image_path


def qr_code_upload_path(instance, filename="qrcode.png"):
    """Génère le chemin relatif pour le QR code du produit."""

    # Nettoyer le nom du produit
    clean_nom = "".join(e for e in instance.nom if e.isalnum() or e in ['-', '_']) or "produit_sans_nom"

    try:
        # Vérifier si le produit existe déjà dans la base de données
        produit_existant = Produit.objects.get(nom=instance.nom)
        unique_number = produit_existant.numero_unique  # Utiliser le numéro unique existant
    except ObjectDoesNotExist:
        # Si le produit n'existe pas, générer un nouveau numéro unique
        unique_number = instance.numero_unique or str(uuid.uuid4())

    # Construire le chemin relatif
    dir_path = f"produits/{clean_nom}-{unique_number}"
    full_dir_path = os.path.join(BASE_MEDIA_PATH, dir_path)

    # Créer les répertoires si nécessaire
    if not os.path.exists(full_dir_path):
        os.makedirs(full_dir_path, exist_ok=True)
        # Appliquer les permissions 777 sur le répertoire
        os.chmod(full_dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    # Chemin complet pour le fichier
    qr_code_path = os.path.join(dir_path, filename)
    qr_code_full_path = os.path.join(BASE_MEDIA_PATH, qr_code_path)

    # Retourner le chemin relatif pour stockage
    return qr_code_path


def generate_token():
    """Fonction pour générer un token sécurisé."""
    return secrets.token_hex(16)



def fournisseur_photo_upload_path(instance, filename):
    """Génère un chemin de sauvegarde unique pour la photo du fournisseur sans inclure le nom du fournisseur."""

    dir_path = os.path.join('fournisseurs', 'photos')
    full_path = os.path.join(dir_path, filename)

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    except Exception as e:
        print(f"Erreur lors de la création du répertoire : {e}")

    return full_path
# ---------------------------- MODELE FOURNISSEUR ----------------------------

class Logo(models.Model):
    nom = models.CharField(max_length=100)
    image = models.ImageField(upload_to='logos/')
    
    def __str__(self):
        return self.nom
    
class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    metier = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    tel = models.CharField(max_length=15)
    adresse = models.TextField()
    description = models.TextField(blank=True, null=True)
    date_ajoutee = models.DateTimeField(auto_now_add=True)
    date_modifiee = models.DateTimeField(auto_now=True)
    
    # Ajouter localisation pour la région du fournisseur
    type_production = models.CharField(
        max_length=100, 
        choices=[
            ('permaculture', 'Permaculture'),
            ('biologique', 'Biologique'),
            ('raisonnee', 'Agriculture Raisonnée'),
            ('autre', 'Autre')
        ],
        default='autre'  # Valeur par défaut
    )
    experience_annees = models.PositiveIntegerField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)  # Exemple : "AB, Ecocert, Fairtrade"
    engagement_ecologique = models.TextField(blank=True, null=True)
    conditions_travail = models.TextField(blank=True, null=True)
    objectifs_durables = models.TextField(blank=True, null=True)
    produits_principaux = models.TextField(blank=True, null=True)  # Exemple : "Tomates, Courges, Laitue"
    calendrier_production = models.TextField(blank=True, null=True)  # Exemple : "Mars à Novembre"
    saisonnalite_respectee = models.BooleanField(default=True)
    temoignages_clients = models.TextField(blank=True, null=True)  # Peut être extrait des avis
    impact_local = models.TextField(blank=True, null=True)
    
    pays = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)  # Optionnel : pour des localisations précises
    longitude = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Photo optionnelle pour chaque fournisseur
    photo = models.ImageField(upload_to=fournisseur_photo_upload_path, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.metier}"
    
class StatutProduit(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    EN_PREPARATION = 'en_preparation', 'En préparation'
    EN_LIVRAISON = 'en_livraison', 'En livraison'
    TERMINE = 'termine', 'Terminé'
    EN_STOCK = 'en_stock', 'En stock'  # Ajout du statut "En stock"


# ---------------------------- MODELE PRODUIT ----------------------------
class Produit(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    description_longue = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=produit_image_upload_path, blank=True, null=True)
    grande_image = models.ImageField(upload_to=produit_image_upload_path, blank=True, null=True)
    date_ajoute = models.DateTimeField(auto_now_add=True)
    date_modifie = models.DateTimeField(auto_now=True)
    categorie = models.ForeignKey('Categorie', on_delete=models.CASCADE, related_name='produits')
    qr_code = models.ImageField(upload_to=qr_code_upload_path, blank=True, null=True)
    numero_unique = models.CharField(max_length=100, unique=True, blank=True, null=True)
    souscategorie = models.ForeignKey('SousCategorie', on_delete=models.CASCADE, related_name='produits')
    logos = models.ManyToManyField('Logo', blank=True)
    adresse_produit = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    poids = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
        # Ajout du champ statut pour le produit

    
    # Nouveau champ : Cycle de fabrication
    cycle_fabrication = models.TextField(
        blank=True, 
        null=True, 
        help_text="Décrire le cycle de fabrication (ex : plantation, récolte, pressage, etc.)"
    )

    # Nouveau champ : Méthode de préparation (spécifique aux produits comme l'huile d'olive)
    preparation = models.TextField(
        blank=True, 
        null=True, 
        help_text="Détails sur les méthodes de préparation ou de transformation (ex : extraction à froid)."
    )

    # Champ pour date de récolte (si applicable)
    date_recolte = models.DateField(
        blank=True,
        null=True,
        help_text="Date de récolte (utile pour des produits comme l'huile d'olive ou les fruits)."
    )

    # Champ pour l'origine géographique
    origine = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Origine géographique du produit (ex : Provence, France)."
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutProduit.choices,
        default=StatutProduit.EN_ATTENTE
    )
    # Nouveau champ pour la TVA
    taux_tva = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=20.00,  # Par défaut, 20% pour la France
        help_text="Taux de TVA en pourcentage (ex : 20 pour 20%)"
    )

    def prix_ttc(self):
        """Calcule le prix TTC du produit."""
        return round(self.prix * (1 + self.taux_tva / 100), 2)    
    # Clé étrangère pour lier le produit au fournisseur
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='produits', null=True, blank=True)
    def __str__(self):
        return f"{self.nom}- {self.numero_unique}"
    
    def qr_code_tag(self):
        """Renvoie une balise HTML pour afficher le QR code."""
        if self.qr_code:
            return mark_safe(f'<img src="{self.qr_code.url}" width="100" height="100" />')
        return "Pas de QR code"
    
    def generate_numero_unique(self):
        """Génère un numéro unique pour le produit."""
        if not self.numero_unique:
            self.numero_unique = str(uuid.uuid4())[:8]

    def save(self, *args, **kwargs):
        self.generate_numero_unique()
        super().save(*args, **kwargs)


@receiver(post_save, sender=Produit)
def generate_qr_code(sender, instance, created, **kwargs):
    """Génère et sauvegarde le QR code pour un produit après sauvegarde."""
    logger.info(f"Generate QR code called for {instance.nom} (ID: {instance.id})")

    if not instance.qr_code:  # Vérifie si le QR code est vide
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        product_url = reverse('ajouter-produit', args=[instance.numero_unique])
        full_url = f"https://dev.occidelice-back.data-worlds.com{product_url}"

        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        file_name = f"qrcode_{instance.numero_unique}.png"
        instance.qr_code.save(file_name, File(buffer), save=False)
        instance.save()
        logger.info("QR code generated and saved successfully.")
    else:
        logger.info("QR code already exists; no generation needed.")

