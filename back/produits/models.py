<<<<<<< HEAD
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

=======
# produits/models.py

import os
import uuid
import qrcode
import logging
from io import BytesIO
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from fournisseur.models import Fournisseur

logger = logging.getLogger(__name__)


# ===================================
# TYPE HINTS
# ===================================

if TYPE_CHECKING:
    from django.db.models import QuerySet as QuerySetType
else:
    QuerySetType = models.QuerySet


# ===================================
# FONCTIONS UTILITAIRES
# ===================================

def image_upload_path(instance: models.Model, filename: str) -> str:
    """
    Génère le chemin de stockage pour les images
    Format: produits/{slug}/{numero_unique}/image.ext
    """
    ext = filename.split('.')[-1]
    clean_nom = slugify(getattr(instance, 'nom', 'produit'))
    unique_number = getattr(instance, 'numero_unique', str(uuid.uuid4())[:8])
    
    return f"produits/{clean_nom}/{unique_number}/image.{ext}"


def qr_code_upload_path(instance: models.Model, filename: str = "qrcode.png") -> str:
    """
    Génère le chemin de stockage pour le QR code
    Format: produits/{slug}/{numero_unique}/qrcode.png
    """
    clean_nom = slugify(getattr(instance, 'nom', 'produit'))
    unique_number = getattr(instance, 'numero_unique', str(uuid.uuid4())[:8])
    
    return f"produits/{clean_nom}/{unique_number}/{filename}"


# ===================================
# STATUTS
# ===================================

class StatutProduit(models.TextChoices):
    """Statuts possibles pour un produit"""
    EN_ATTENTE = 'en_attente', '⏳ En attente'
    EN_PREPARATION = 'en_preparation', '🔄 En préparation'
    EN_LIVRAISON = 'en_livraison', '🚚 En livraison'
    EN_STOCK = 'en_stock', '✅ En stock'
    ARRIVEE = 'arrivee', '📥 Arrivé'
    RUPTURE = 'rupture', '❌ Rupture de stock'
    ARCHIVE = 'archive', '📦 Archivé'


# ===================================
# TEMPLATES DE DESCRIPTEURS PAR CATÉGORIE
# ===================================



# ===================================
# MODÈLES DE CATÉGORISATION (3 NIVEAUX)
# ===================================

class Categorie(models.Model):
    """Catégorie principale de produits (niveau 1)"""
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Emoji ou classe d'icône (ex: 🍷 ou fa-wine)"
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    ordre = models.IntegerField(default=0)
    est_active = models.BooleanField(default=True)
        # ✅ NOUVEAU CHAMP
    descripteurs = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Descripteurs",
        help_text="Descripteurs communs à tous les produits de cette catégorie"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_template_descripteurs(self) -> Dict[str, Any]:
        """
        Retourne le template de descripteurs pour cette catégorie
        """
        return self.descripteurs.copy() if self.descripteurs else {}

    def get_nombre_souscategories(self) -> int:
        """Retourne le nombre de sous-catégories dans cette catégorie"""
        return self.souscategories.filter(est_active=True).count()

    def get_nombre_produits(self) -> int:
        """Retourne le nombre de produits dans cette catégorie"""
        return self.produits.filter(est_actif=True).count()




class SousCategorie(models.Model):
    """Sous-catégorie de produits (niveau 2)"""
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        related_name='souscategories',
        verbose_name='Catégorie parente'
    )
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='souscategories/', blank=True, null=True)
    ordre = models.IntegerField(default=0)
    est_active = models.BooleanField(default=True)
    
    # Descripteurs spécifiques pour cette sous-catégorie
    descripteurs = models.JSONField(
        default=dict,
        blank=True,
        help_text="Descripteurs additionnels propres à cette sous-catégorie"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sous-catégorie'
        verbose_name_plural = 'Sous-catégories'
        ordering = ['categorie__ordre', 'ordre', 'nom']
        unique_together = ['categorie', 'slug']

    def __str__(self):
        return f"{self.categorie.nom} > {self.nom}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_template_descripteurs(self) -> Dict[str, Any]:
        """
        Retourne le template de descripteurs (hérité de la catégorie + spécifiques)
        """
        template = self.categorie.get_template_descripteurs().copy()
        template.update(self.descripteurs)
        return template

    def get_nombre_produits(self) -> int:
        """Retourne le nombre de produits dans cette sous-catégorie"""
        return self.produits.filter(est_actif=True).count()

    def get_nombre_sousssouscategories(self) -> int:
        """Retourne le nombre de sous-sous-catégories"""
        return self.soussouscategories.filter(est_active=True).count()

    def get_arborescence(self) -> str:
        """Retourne l'arborescence complète"""
        return f"{self.categorie.nom} > {self.nom}"

    def get_absolute_url(self) -> str:
        """URL de la sous-catégorie"""
        return reverse('produits:souscategorie', kwargs={
            'categorie_slug': self.categorie.slug,
            'slug': self.slug
        })


class SousSousCategorie(models.Model):
    """Sous-sous-catégorie de produits (niveau 3)"""
    souscategorie = models.ForeignKey(
        SousCategorie,
        on_delete=models.CASCADE,
        related_name='soussouscategories',
        verbose_name='Sous-catégorie parente'
    )
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='soussouscategories/', blank=True, null=True)
    ordre = models.IntegerField(default=0)
    est_active = models.BooleanField(default=True)
    
    # Descripteurs spécifiques pour cette sous-sous-catégorie
    descripteurs = models.JSONField(
        default=dict,
        blank=True,
        help_text="Descripteurs additionnels propres à cette sous-sous-catégorie"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sous-sous-catégorie'
        verbose_name_plural = 'Sous-sous-catégories'
        ordering = ['souscategorie__categorie__ordre', 'souscategorie__ordre', 'ordre', 'nom']
        unique_together = ['souscategorie', 'slug']

    def __str__(self):
        return f"{self.get_arborescence()}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_categorie(self) -> Categorie:
        """Retourne la catégorie principale"""
        return self.souscategorie.categorie

    def get_template_descripteurs(self) -> Dict[str, Any]:
        """
        Retourne le template de descripteurs complet
        (hérité de la catégorie + sous-catégorie + spécifiques)
        """
        template = self.souscategorie.get_template_descripteurs().copy()
        template.update(self.descripteurs)
        return template

    def get_nombre_produits(self) -> int:
        """Retourne le nombre de produits dans cette sous-sous-catégorie"""
        return self.produits.filter(est_actif=True).count()

    def get_arborescence(self) -> str:
        """Retourne l'arborescence complète"""
        return f"{self.souscategorie.categorie.nom} > {self.souscategorie.nom} > {self.nom}"

    def get_absolute_url(self) -> str:
        """URL de la sous-sous-catégorie"""
        return reverse('produits:soussouscategorie', kwargs={
            'categorie_slug': self.souscategorie.categorie.slug,
            'souscategorie_slug': self.souscategorie.slug,
            'slug': self.slug
        })


# ===================================
# MODÈLE PRINCIPAL PRODUIT
# ===================================

class Produit(models.Model):
    """Modèle principal pour un produit"""
    
    # Identifiants uniques
    numero_unique = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="Numéro unique"
    )
    code_barre = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        verbose_name="Code-barres (EAN/UPC)"
    )
    reference_interne = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Référence interne"
    )
    
    # Informations de base
    nom = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description_courte = models.TextField(
        max_length=300,
        blank=True,
        verbose_name="Description courte",
        help_text="Description courte pour les listes (max 300 caractères)"
    )
    description_longue = models.TextField(
        blank=True,
        verbose_name="Description détaillée"
    )
    
    # Catégorisation (3 niveaux)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produits',
        verbose_name="Catégorie principale"
    )
    souscategorie = models.ForeignKey(
        SousCategorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produits',
        verbose_name="Sous-catégorie"
    )
    soussouscategorie = models.ForeignKey(
        SousSousCategorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produits',
        verbose_name="Sous-sous-catégorie"
    )
    
    # Images
    image_principale = models.ImageField(
        upload_to=image_upload_path,
        blank=True,
        null=True,
        verbose_name="Image principale"
    )
    
    # Prix et stock
    prix_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix HT (€)"
    )
    tva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name="TVA (%)",
        help_text="Taux de TVA applicable"
    )
    
    stock_actuel = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock actuel"
    )
    stock_minimum = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock minimum",
        help_text="Seuil d'alerte pour le réapprovisionnement"
    )
    
    # Promotion
    en_promotion = models.BooleanField(
        default=False,
        verbose_name="En promotion"
    )
    pourcentage_promotion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name="Réduction (%)",
        help_text="Pourcentage de réduction"
    )
    
    # Statut et visibilité
    statut = models.CharField(
        max_length=20,
        choices=StatutProduit.choices,
        default=StatutProduit.EN_STOCK,
        verbose_name="Statut"
    )
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Décocher pour désactiver le produit sans le supprimer"
    )
    est_nouveaute = models.BooleanField(
        default=False,
        verbose_name="Nouveauté"
    )
    est_bio = models.BooleanField(
        default=False,
        verbose_name="Bio"
    )
    est_local = models.BooleanField(
        default=False,
        verbose_name="Produit local"
    )
    
    # Poids et dimensions
    poids = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Poids (kg)"
    )
    unite_mesure = models.CharField(
        max_length=20,
        default='unité',
        verbose_name="Unité de mesure",
        help_text="Ex: kg, L, unité, boîte"
    )
    
    # Relation fournisseur
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produits',
        verbose_name="Fournisseur"
    )
    
    # Origine et provenance
    origine = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Origine/Provenance",
        help_text="Pays ou région d'origine"
    )
    
    # QR Code
    qr_code = models.ImageField(
        upload_to=qr_code_upload_path,
        blank=True,
        null=True,
        verbose_name="QR Code"
    )
    
    # Métadonnées
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="Meta titre",
        help_text="Titre pour le SEO (max 70 caractères)"
    )
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        verbose_name="Meta description",
        help_text="Description pour le SEO (max 160 caractères)"
    )
    
    # Horodatage
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_ajout_stock = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'ajout au stock"
    )

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['numero_unique']),
            models.Index(fields=['slug']),
            models.Index(fields=['code_barre']),
            models.Index(fields=['statut']),
            models.Index(fields=['est_actif']),
            models.Index(fields=['categorie', 'souscategorie', 'soussouscategorie']),
        ]

    def __str__(self):
        return f"{self.nom} ({self.numero_unique})"

    def save(self, *args, **kwargs):
        """Surcharge de save pour générer les champs automatiques"""
        # Génération du numéro unique
        if not self.numero_unique:
            self.numero_unique = self._generer_numero_unique()
        
        # Génération du slug
        if not self.slug:
            self.slug = slugify(self.nom)
            # Vérifier l'unicité du slug
            original_slug = self.slug
            counter = 1
            while Produit.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Validation de la cohérence des catégories
        self._valider_categories()
        
        super().save(*args, **kwargs)
        
        # Génération du QR code après sauvegarde
        if not self.qr_code:
            self._generer_qr_code()

    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Valider que la promotion ne dépasse pas 100%
        if self.en_promotion and self.pourcentage_promotion > 100:
            raise ValidationError({
                'pourcentage_promotion': 'La réduction ne peut pas dépasser 100%'
            })
        
        # Valider que le stock minimum n'est pas supérieur au stock actuel
        if self.stock_minimum > self.stock_actuel:
            logger.warning(
                f"Le stock minimum ({self.stock_minimum}) est supérieur "
                f"au stock actuel ({self.stock_actuel}) pour {self.nom}"
            )

    def _generer_numero_unique(self) -> str:
        """
        Génère un numéro unique au format: YYYY-MMDD-XXXX
        Exemple: 2024-1215-A7B3
        """
        today = datetime.now()
        date_part = today.strftime('%Y-%m%d')
        
        # Générer la partie aléatoire
        random_part = str(uuid.uuid4())[:4].upper()
        
        numero = f"{date_part}-{random_part}"
        
        # Vérifier l'unicité
        while Produit.objects.filter(numero_unique=numero).exists():
            random_part = str(uuid.uuid4())[:4].upper()
            numero = f"{date_part}-{random_part}"
        
        return numero

    def _valider_categories(self):
        """Valide la cohérence de la hiérarchie des catégories"""
        if self.soussouscategorie:
            if not self.souscategorie:
                self.souscategorie = self.soussouscategorie.souscategorie
            if not self.categorie:
                self.categorie = self.souscategorie.categorie
            
            # Vérifier la cohérence
            if self.souscategorie != self.soussouscategorie.souscategorie:
                raise ValidationError(
                    "La sous-catégorie ne correspond pas à la sous-sous-catégorie sélectionnée"
                )
        
        if self.souscategorie and not self.categorie:
            self.categorie = self.souscategorie.categorie
        
        if self.souscategorie and self.categorie:
            if self.souscategorie.categorie != self.categorie:
                raise ValidationError(
                    "La catégorie ne correspond pas à la sous-catégorie sélectionnée"
                )

    def _generer_qr_code(self):
        """Génère le QR code pour le produit"""
        try:
            # Créer le QR code avec l'URL du produit
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # URL absolue du produit (à adapter selon votre configuration)
            url = f"https://votresite.com/produits/{self.slug}"
            qr.add_data(url)
            qr.make(fit=True)
            
            # Créer l'image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Sauvegarder dans un buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Sauvegarder le fichier
            filename = f"qrcode_{self.numero_unique}.png"
            self.qr_code.save(filename, File(buffer), save=False)
            
            # Sauvegarder le modèle (sans déclencher save() à nouveau)
            Produit.objects.filter(pk=self.pk).update(qr_code=self.qr_code)
            
            logger.info(f"QR code généré pour {self.nom}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du QR code pour {self.nom}: {str(e)}")

    def regenerer_qr_code(self):
        """Régénère le QR code (utile pour les mises à jour)"""
        if self.qr_code:
            # Supprimer l'ancien QR code
            old_path = self.qr_code.path
            if os.path.exists(old_path):
                os.remove(old_path)
        
        self.qr_code = None
        self._generer_qr_code()

    # ===================================
    # PROPRIÉTÉS CALCULÉES
    # ===================================

    @property
    def montant_tva(self) -> Decimal:
        """Calcule le montant de la TVA"""
        return self.prix_ht * (self.tva / 100)

    @property
    def prix_ttc(self) -> Decimal:
        """Calcule le prix TTC"""
        return self.prix_ht * (1 + self.tva / 100)

    @property
    def prix_promo_ht(self) -> Optional[Decimal]:
        """Calcule le prix promotionnel HT"""
        if self.en_promotion and self.pourcentage_promotion > 0:
            reduction = self.prix_ht * (self.pourcentage_promotion / 100)
            return self.prix_ht - reduction
        return None

    @property
    def prix_promo_ttc(self) -> Optional[Decimal]:
        """Calcule le prix promotionnel TTC"""
        if self.prix_promo_ht:
            return self.prix_promo_ht * (1 + self.tva / 100)
        return None

    @property
    def prix_final_ttc(self) -> Decimal:
        """Retourne le prix final TTC (avec ou sans promo)"""
        return self.prix_promo_ttc or self.prix_ttc

    @property
    def economie(self) -> Optional[Decimal]:
        """Calcule l'économie réalisée avec la promotion"""
        if self.en_promotion and self.prix_promo_ttc:
            return self.prix_ttc - self.prix_promo_ttc
        return None

    @property
    def est_en_rupture(self) -> bool:
        """Vérifie si le produit est en rupture de stock"""
        return self.stock_actuel == 0 or self.statut == StatutProduit.RUPTURE

    @property
    def est_stock_faible(self) -> bool:
        """Vérifie si le stock est en dessous du minimum"""
        return 0 < self.stock_actuel <= self.stock_minimum

    @property
    def pourcentage_stock(self) -> float:
        """Calcule le pourcentage de stock restant par rapport au minimum"""
        if self.stock_minimum > 0:
            return (self.stock_actuel / self.stock_minimum) * 100
        return 100.0

    @property
    def arborescence_complete(self) -> str:
        """Retourne l'arborescence complète des catégories"""
        parts = []
        if self.categorie:
            parts.append(self.categorie.nom)
        if self.souscategorie:
            parts.append(self.souscategorie.nom)
        if self.soussouscategorie:
            parts.append(self.soussouscategorie.nom)
        return " > ".join(parts) if parts else "Non catégorisé"

    # ===================================
    # MÉTHODES MÉTIER
    # ===================================

    def get_template_descripteurs(self) -> Dict[str, Any]:
        """
        Retourne le template de descripteurs applicable à ce produit
        basé sur sa catégorisation la plus précise
        """
        if self.soussouscategorie:
            return self.soussouscategorie.get_template_descripteurs()
        elif self.souscategorie:
            return self.souscategorie.get_template_descripteurs()
        elif self.categorie:
            return self.categorie.get_template_descripteurs()
        return {}

    def ajuster_stock(self, quantite: int, operation: str = 'ajouter') -> None:
        """
        Ajuste le stock du produit
        
        Args:
            quantite: Quantité à ajouter ou retirer
            operation: 'ajouter' ou 'retirer'
        """
        if operation == 'ajouter':
            self.stock_actuel += quantite
            logger.info(f"Ajout de {quantite} unités au stock de {self.nom}")
        elif operation == 'retirer':
            if self.stock_actuel >= quantite:
                self.stock_actuel -= quantite
                logger.info(f"Retrait de {quantite} unités du stock de {self.nom}")
            else:
                logger.warning(
                    f"Stock insuffisant pour retirer {quantite} unités de {self.nom}. "
                    f"Stock actuel: {self.stock_actuel}"
                )
                raise ValidationError(f"Stock insuffisant ({self.stock_actuel} disponibles)")
        
        # Mettre à jour le statut si nécessaire
        if self.stock_actuel == 0:
            self.statut = StatutProduit.RUPTURE
        elif self.statut == StatutProduit.RUPTURE and self.stock_actuel > 0:
            self.statut = StatutProduit.EN_STOCK
        
        self.save()

    def appliquer_promotion(self, pourcentage: Decimal) -> None:
        """
        Applique une promotion au produit
        
        Args:
            pourcentage: Pourcentage de réduction (0-100)
        """
        if not 0 <= pourcentage <= 100:
            raise ValidationError("Le pourcentage doit être entre 0 et 100")
        
        self.en_promotion = True
        self.pourcentage_promotion = pourcentage
        self.save()
        logger.info(f"Promotion de {pourcentage}% appliquée à {self.nom}")

    def retirer_promotion(self) -> None:
        """Retire la promotion du produit"""
        self.en_promotion = False
        self.pourcentage_promotion = Decimal('0.00')
        self.save()
        logger.info(f"Promotion retirée pour {self.nom}")

    def get_descripteurs(self) -> 'QuerySetType[DescripteurProduit]':
        """Retourne tous les descripteurs du produit, triés par ordre"""
        return self.descripteurs.all().order_by('ordre', 'cle')

    def get_descripteurs_dict(self) -> Dict[str, str]:
        """Retourne les descripteurs sous forme de dictionnaire"""
        return {
            desc.cle: desc.valeur
            for desc in self.get_descripteurs()
        }

    def get_images_additionnelles(self) -> 'QuerySetType[ImageProduit]':
        """Retourne toutes les images additionnelles, triées par ordre"""
        return self.images.all().order_by('ordre')

    def get_toutes_images(self) -> List[str]:
        """
        Retourne toutes les URLs des images du produit (principale + additionnelles)
        """
        images_urls = []

        # Ajouter l'image principale
        if self.image_principale:
            images_urls.append(self.image_principale.url)

        # Ajouter les images additionnelles
        for image in self.get_images_additionnelles():
            if image.image:
                images_urls.append(image.image.url)

        return images_urls

    def get_image_principale_obj(self) -> Optional['ImageProduit']:
        """
        Retourne l'objet ImageProduit marqué comme principal, si existant
        """
        return self.images.filter(est_principale=True).first()

    def get_nombre_images(self) -> int:
        """Retourne le nombre total d'images (principale + additionnelles)"""
        count = 1 if self.image_principale else 0
        count += self.images.count()
        return count

    def get_absolute_url(self) -> str:
        """URL détaillée du produit"""
        return reverse('produits:detail', kwargs={'slug': self.slug})

    def get_admin_url(self) -> str:
        """URL d'administration du produit"""
        return reverse('admin:produits_produit_change', args=[self.pk])


# ===================================
# MODÈLE IMAGES ADDITIONNELLES
# ===================================

class ImageProduit(models.Model):
    """Images additionnelles pour un produit"""
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Produit"
    )
    image = models.ImageField(
        upload_to=image_upload_path,
        verbose_name="Image"
    )
    legende = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Légende"
    )
    ordre = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    est_principale = models.BooleanField(
        default=False,
        verbose_name="Image principale"
    )
    
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Image produit'
        verbose_name_plural = 'Images produits'
        ordering = ['ordre', 'date_ajout']

    def __str__(self):
        return f"Image de {self.produit.nom} ({self.ordre})"

    def save(self, *args, **kwargs):
        # Si cette image est définie comme principale, retirer le flag des autres
        if self.est_principale:
            ImageProduit.objects.filter(
                produit=self.produit,
                est_principale=True
            ).exclude(pk=self.pk).update(est_principale=False)
            
            # Mettre à jour l'image principale du produit
            self.produit.image_principale = self.image
            self.produit.save(update_fields=['image_principale'])
        
        super().save(*args, **kwargs)


# ===================================
# MODÈLE DESCRIPTEURS RELATIONNELS
# ===================================

class DescripteurProduit(models.Model):
    """
    Descripteurs relationnels pour les caractéristiques spécifiques d'un produit
    Utilise les templates définis dans DescripteursTemplates
    """
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='descripteurs',
        verbose_name="Produit"
    )
    cle = models.CharField(
        max_length=100,
        verbose_name="Clé du descripteur",
        help_text="Ex: millesime, cepage, region"
    )
    valeur = models.TextField(
        verbose_name="Valeur",
        help_text="La valeur du descripteur"
    )
    ordre = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Descripteur produit'
        verbose_name_plural = 'Descripteurs produits'
        ordering = ['ordre', 'cle']
        unique_together = ['produit', 'cle']

    def __str__(self):
        return f"{self.get_label()}: {self.valeur}"

    def get_template_config(self) -> Dict[str, Any]:
        """Retourne la configuration du template pour ce descripteur"""
        template = self.produit.get_template_descripteurs()
        return template.get(self.cle, {})

    def get_label(self) -> str:
        """Retourne le label lisible du descripteur"""
        config = self.get_template_config()
        return config.get('label', self.cle.replace('_', ' ').title())

    def get_icon(self) -> str:
        """Retourne l'icône associée au descripteur"""
        config = self.get_template_config()
        return config.get('icon', '📋')

    def get_type(self) -> str:
        """Retourne le type du descripteur"""
        config = self.get_template_config()
        return config.get('type', 'text')

    def clean(self):
        """Validation personnalisée basée sur le template"""
        super().clean()
        
        config = self.get_template_config()
        
        # Vérifier si le descripteur est requis
        if config.get('required', False) and not self.valeur:
            raise ValidationError({
                'valeur': f"Le champ '{self.get_label()}' est requis"
            })
        
        # Validation selon le type
        field_type = config.get('type', 'text')
        
        if field_type == 'number':
            try:
                value = float(self.valeur)
                
                # Vérifier min/max
                min_val = config.get('min')
                max_val = config.get('max')
                
                if min_val is not None and value < min_val:
                    raise ValidationError({
                        'valeur': f"La valeur doit être supérieure ou égale à {min_val}"
                    })
                
                if max_val is not None and value > max_val:
                    raise ValidationError({
                        'valeur': f"La valeur doit être inférieure ou égale à {max_val}"
                    })
                    
            except ValueError:
                raise ValidationError({
                    'valeur': "La valeur doit être un nombre"
                })
        
        elif field_type == 'choice':
            choices = config.get('choices', [])
            if choices and self.valeur not in choices:
                raise ValidationError({
                    'valeur': f"La valeur doit être parmi: {', '.join(choices)}"
                })
        
        elif field_type == 'boolean':
            if self.valeur.lower() not in ['true', 'false', 'oui', 'non', '1', '0']:
                raise ValidationError({
                    'valeur': "La valeur doit être True/False ou Oui/Non"
                })


# ===================================
# MODÈLE LOGOS/LABELS
# ===================================

class LogoLabel(models.Model):
    """Logos et labels pour les produits (Bio, AOP, IGP, etc.)"""
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='logos',
        verbose_name="Produit"
    )
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom du label",
        help_text="Ex: Bio, AOP, IGP, Label Rouge"
    )
    image = models.ImageField(
        upload_to='labels/',
        verbose_name="Logo"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    ordre = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Logo/Label'
        verbose_name_plural = 'Logos/Labels'
        ordering = ['ordre', 'nom']

    def __str__(self):
        return f"{self.nom} - {self.produit.nom}"


# ===================================
# SIGNAUX
# ===================================

@receiver(post_save, sender=Produit)
def produit_post_save(sender, instance: Produit, created: bool, **kwargs):
    """Signal après sauvegarde d'un produit"""
    if created:
        logger.info(f"Nouveau produit créé: {instance.nom} ({instance.numero_unique})")

        # Générer automatiquement certains descripteurs si la catégorie est définie
        if instance.categorie and not instance.descripteurs.exists():
            template = instance.get_template_descripteurs()
            for cle, config in template.items():
                # Vérifier que config est un dictionnaire et non une liste
                if isinstance(config, dict) and config.get('auto_create', False):
                    DescripteurProduit.objects.create(
                        produit=instance,
                        cle=cle,
                        valeur=config.get('default', '')
                    )


@receiver(pre_delete, sender=Produit)
def produit_pre_delete(sender, instance: Produit, **kwargs):
    """Signal avant suppression d'un produit"""
    logger.info(f"Suppression du produit: {instance.nom} ({instance.numero_unique})")
    
    # Supprimer les fichiers associés
    if instance.image_principale:
        if os.path.isfile(instance.image_principale.path):
            os.remove(instance.image_principale.path)
    
    if instance.qr_code:
        if os.path.isfile(instance.qr_code.path):
            os.remove(instance.qr_code.path)


@receiver(pre_delete, sender=ImageProduit)
def image_produit_pre_delete(sender, instance: ImageProduit, **kwargs):
    """Signal avant suppression d'une image"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
