from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password
from django.core.validators import RegexValidator, EmailValidator
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from decimal import Decimal
import os 
from typing import Optional
from decimal import Decimal
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class Logo(models.Model):
    nom = models.CharField(max_length=100)
    image = models.ImageField(upload_to='logos/')

    def __str__(self):
        return self.nom

def fournisseur_photo_upload_path(instance, filename):
    """Génère un chemin de sauvegarde unique pour la photo du fournisseur sans inclure le nom du fournisseur."""
    dir_path = os.path.join('fournisseurs', 'photos')
    full_path = os.path.join(dir_path, filename)

    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    except Exception as e:
        print(f"Erreur lors de la création du répertoire : {e}")

    return full_path

class Fournisseur(models.Model):
    # ===================================
    # INFORMATIONS PERSONNELLES
    # ===================================
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    password = models.CharField(max_length=128)  # Pour stocker le hash
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        validators=[EmailValidator(message="Entrez une adresse email valide.")])
    metier = models.CharField(max_length=100, verbose_name="Métier")
    contact = models.CharField(max_length=100, verbose_name="Contact")
    tel = models.CharField(
        max_length=15,
        verbose_name="Téléphone",
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    
    # ===================================
    # ADRESSE PRINCIPALE
    # ===================================
    adresse = models.TextField(verbose_name="Adresse complète")
    code_postal = models.CharField(max_length=10, verbose_name="Code postal", blank=True)
    ville = models.CharField(max_length=100, verbose_name="Ville")
    pays = models.CharField(max_length=100, verbose_name="Pays", default="France")
    
    # Coordonnées GPS
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    
    # ===================================
    # ZONES DE LIVRAISON
    # ===================================
    zone_livraison_type = models.CharField(
        max_length=50,
        choices=[
            ('rayon', 'Rayon kilométrique'),
            ('departements', 'Départements'),
            ('villes', 'Villes spécifiques'),
            ('national', 'National'),
        ],
        default='rayon',
        verbose_name="Type de zone de livraison"
    )
    
    # Rayon de livraison en km (si type = 'rayon')
    rayon_livraison_km = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Rayon de livraison (km)",
        help_text="Distance maximale de livraison depuis l'adresse principale"
    )
    
    # Départements desservis (si type = 'departements')
    departements_livraison = models.TextField(
        blank=True,
        verbose_name="Départements de livraison",
        help_text="Ex: 75, 77, 78, 91, 92, 93, 94, 95 (séparés par des virgules)"
    )
    
    # Villes desservies (si type = 'villes')
    villes_livraison = models.TextField(
        blank=True,
        verbose_name="Villes de livraison",
        help_text="Ex: Paris, Lyon, Marseille (séparées par des virgules)"
    )
    
    # Points de livraison fixes
    points_livraison = models.ManyToManyField(
        'PointLivraison',
        blank=True,
        verbose_name="Points de livraison",
        related_name='fournisseurs'
    )
    
    # Frais de livraison
    frais_livraison_base = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal(0.00),
        verbose_name="Frais de livraison de base (€)"
    )
    
    frais_livraison_par_km = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal(0.00),
        verbose_name="Frais par km supplémentaire (€)"
    )
    
    livraison_gratuite_montant = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Montant pour livraison gratuite (€)",
        help_text="Montant minimum de commande pour livraison gratuite"
    )
    
    # Jours de livraison
    jours_livraison = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Jours de livraison",
        help_text="Ex: Lundi, Mercredi, Vendredi"
    )
    
    delai_livraison_jours = models.PositiveIntegerField(
        default=2,
        verbose_name="Délai de livraison (jours)",
        help_text="Nombre de jours entre la commande et la livraison"
    )
    
    # ===================================
    # PRODUCTION ET CERTIFICATIONS
    # ===================================
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    type_production = models.CharField(
        max_length=100, 
        choices=[
            ('permaculture', 'Permaculture'),
            ('biologique', 'Biologique'),
            ('raisonnee', 'Agriculture Raisonnée'),
            ('autre', 'Autre')
        ],
        default='autre',
        verbose_name="Type de production"
    )
    
    experience_annees = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Années d'expérience"
    )
    
    certifications = models.TextField(
        blank=True,
        null=True,
        verbose_name="Certifications",
        help_text="Ex: AB, Ecocert, Fairtrade"
    )
    
    engagement_ecologique = models.TextField(blank=True, null=True, verbose_name="Engagement écologique")
    conditions_travail = models.TextField(blank=True, null=True, verbose_name="Conditions de travail")
    objectifs_durables = models.TextField(blank=True, null=True, verbose_name="Objectifs durables")
    
    # ===================================
    # PRODUITS ET SAISONNALITÉ
    # ===================================
    produits_principaux = models.TextField(
        blank=True,
        null=True,
        verbose_name="Produits principaux",
        help_text="Ex: Tomates, Courges, Laitue"
    )
    
    calendrier_production = models.TextField(
        blank=True,
        null=True,
        verbose_name="Calendrier de production",
        help_text="Ex: Mars à Novembre"
    )
    
    saisonnalite_respectee = models.BooleanField(
        default=True,
        verbose_name="Saisonnalité respectée"
    )
    
    # ===================================
    # RELATIONS ET MÉDIAS
    # ===================================
    temoignages_clients = models.TextField(
        blank=True,
        null=True,
        verbose_name="Témoignages clients"
    )
    
    impact_local = models.TextField(blank=True, null=True, verbose_name="Impact local")
    
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Client associé"
    )
    
    photo = models.ImageField(
        upload_to=fournisseur_photo_upload_path,
        blank=True,
        null=True,
        verbose_name="Photo"
    )
    
    # ===================================
    # DATES
    # ===================================
    date_ajoutee = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modifiee = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    # ===================================
    # META
    # ===================================
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['ville', 'code_postal']),
            models.Index(fields=['zone_livraison_type']),
        ]
    
    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.metier}"
    
    def set_password(self, raw_password):
        """
        Hash et enregistre le mot de passe
        """
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        """
        Vérifie si le mot de passe est correct
        """
        return check_password(raw_password, self.password)

    def enregistrer_connexion(self):
        """
        Met à jour la date de dernière connexion
        """
        self.derniere_connexion = timezone.now()
        self.save(update_fields=['derniere_connexion'])
    
    # ===================================
    # MÉTHODES DE VALIDATION
    # ===================================
    def clean(self):
        """Valide la cohérence des zones de livraison"""
        if self.zone_livraison_type == 'rayon' and not self.rayon_livraison_km:
            raise ValidationError({
                'rayon_livraison_km': 'Le rayon de livraison est obligatoire pour ce type de zone'
            })
        
        if self.zone_livraison_type == 'departements' and not self.departements_livraison:
            raise ValidationError({
                'departements_livraison': 'Les départements sont obligatoires pour ce type de zone'
            })
        
        if self.zone_livraison_type == 'villes' and not self.villes_livraison:
            raise ValidationError({
                'villes_livraison': 'Les villes sont obligatoires pour ce type de zone'
            })
    
    # ===================================
    # MÉTHODES UTILITAIRES
    # ===================================
    def get_departements_list(self):
        """Retourne la liste des départements desservis"""
        if not self.departements_livraison:
            return []
        return [dept.strip() for dept in self.departements_livraison.split(',')]
    
    def get_villes_list(self):
        """Retourne la liste des villes desservies"""
        if not self.villes_livraison:
            return []
        return [ville.strip() for ville in self.villes_livraison.split(',')]
    


    def peut_livrer_a(
        self,
        code_postal: Optional[str] = None,
        ville: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> bool:
        """Vérifie si le fournisseur peut livrer à une adresse donnée"""
        
        # Livraison nationale
        if self.zone_livraison_type == 'national':
            return True

        # Vérification par département
        if self.zone_livraison_type == 'departements' and code_postal:
            dept = code_postal[:2]
            return dept in self.get_departements_list()

        # Vérification par ville
        if self.zone_livraison_type == 'villes' and ville:
            villes_desservies = [v.lower() for v in self.get_villes_list()]
            return ville.lower() in villes_desservies

        # Vérification par rayon kilométrique
        if self.zone_livraison_type == 'rayon':
            distance = self.calculer_distance_vers(latitude, longitude)
            
            # ✅ Si distance est None, on ne peut pas livrer
            if distance is None or self.rayon_livraison_km is None:
                return False
            
            return distance <= float(self.rayon_livraison_km)

        return False


    def calculer_distance_vers(
        self,
        latitude: Optional[float],
        longitude: Optional[float]
    ) -> Optional[float]:
        """
        Calcule la distance entre le fournisseur et une adresse
        
        Args:
            latitude: Latitude de destination
            longitude: Longitude de destination
        
        Returns:
            Distance en km, ou None si impossible de calculer
        """
        # ✅ Validation stricte
        if (
            latitude is None or
            longitude is None or
            self.latitude is None or
            self.longitude is None
        ):
            return None
        
        try:
            from math import radians, sin, cos, sqrt, atan2
            
            # Rayon de la Terre en km
            R = 6371
            
            # Conversion en radians
            lat1 = radians(float(self.latitude))
            lon1 = radians(float(self.longitude))
            lat2 = radians(float(latitude))
            lon2 = radians(float(longitude))
            
            # Différences
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            # Formule de Haversine
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            return R * c
            
        except (ValueError, TypeError, ZeroDivisionError):
            return None


    
    def calculer_frais_livraison(self, montant_commande, distance_km=None):
        """
        Calcule les frais de livraison pour une commande
        
        Args:
            montant_commande: Montant total de la commande
            distance_km: Distance en km (optionnel)
        
        Returns:
            Decimal: Montant des frais de livraison
        """
        from decimal import Decimal
        
        # Livraison gratuite si montant minimum atteint
        if self.livraison_gratuite_montant and montant_commande >= self.livraison_gratuite_montant:
            return Decimal('0.00')
        
        # Frais de base
        frais = self.frais_livraison_base
        
        # Ajouter frais par km si applicable
        if distance_km and self.frais_livraison_par_km:
            frais += Decimal(str(distance_km)) * self.frais_livraison_par_km
        
        return frais
    
    def get_absolute_url(self):
        """URL de la page de détail du fournisseur"""
        return reverse('fournisseur:detail', kwargs={'pk': self.pk})


# ===================================
# MODÈLE POINT DE LIVRAISON
# ===================================
class PointLivraison(models.Model):
    """
    Représente un point de livraison fixe (marché, dépôt, etc.)
    """
    nom = models.CharField(max_length=200, verbose_name="Nom du point")
    adresse = models.TextField(verbose_name="Adresse")
    code_postal = models.CharField(max_length=10, verbose_name="Code postal")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    
    type_point = models.CharField(
        max_length=50,
        choices=[
            ('marche', 'Marché'),
            ('depot', 'Dépôt'),
            ('magasin', 'Magasin'),
            ('autre', 'Autre'),
        ],
        default='depot',
        verbose_name="Type de point"
    )
    
    horaires = models.TextField(
        blank=True,
        verbose_name="Horaires d'ouverture",
        help_text="Ex: Lundi-Vendredi: 9h-18h"
    )
    
    jours_disponibles = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Jours disponibles",
        help_text="Ex: Lundi, Mercredi, Vendredi"
    )
    
    instructions = models.TextField(
        blank=True,
        verbose_name="Instructions de retrait",
        help_text="Informations pour récupérer la commande"
    )
    
    actif = models.BooleanField(default=True, verbose_name="Point actif")
    
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Point de livraison"
        verbose_name_plural = "Points de livraison"
        ordering = ['ville', 'nom']
        indexes = [
            models.Index(fields=['ville', 'code_postal']),
            models.Index(fields=['actif']),
        ]
    
    def __str__(self):
        return f"{self.nom} - {self.ville}"
    
    def get_jours_list(self):
        """Retourne la liste des jours disponibles"""
        if not self.jours_disponibles:
            return []
        return [jour.strip() for jour in self.jours_disponibles.split(',')]


# ===================================
# MODÈLE ZONE DE LIVRAISON (Optionnel)
# ===================================
class ZoneLivraison(models.Model):
    """
    Définit une zone de livraison complexe avec tarification
    """
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.CASCADE,
        related_name='zones_livraison',
        verbose_name="Fournisseur"
    )
    
    nom = models.CharField(max_length=200, verbose_name="Nom de la zone")
    
    departements = models.TextField(
        blank=True,
        verbose_name="Départements",
        help_text="Codes départements séparés par des virgules"
    )
    
    villes = models.TextField(
        blank=True,
        verbose_name="Villes",
        help_text="Noms de villes séparés par des virgules"
    )
    
    frais_livraison = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Frais de livraison (€)"
    )
    
    delai_livraison_jours = models.PositiveIntegerField(
        verbose_name="Délai de livraison (jours)"
    )
    
    montant_minimum = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal(0.00),
        verbose_name="Montant minimum de commande (€)"
    )
    
    actif = models.BooleanField(default=True, verbose_name="Zone active")
    
    class Meta:
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"
        ordering = ['fournisseur', 'nom']
    
    def __str__(self):
        return f"{self.fournisseur.nom} - {self.nom}"
    
    def get_departements_list(self):
        """Retourne la liste des départements"""
        if not self.departements:
            return []
        return [dept.strip() for dept in self.departements.split(',')]
    
    def get_villes_list(self):
        """Retourne la liste des villes"""
        if not self.villes:
            return []
        return [ville.strip() for ville in self.villes.split(',')]
