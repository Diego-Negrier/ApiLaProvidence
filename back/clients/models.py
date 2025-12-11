<<<<<<< HEAD
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
from produits.models import Produit
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.
# ---------------------------- MODELE CLIENT ----------------------------

class Client(AbstractUser):
    username = models.CharField(max_length=30, unique=True, default="anonymes")  # Valeur par défaut "anonymes"

    prenom = models.CharField(max_length=30, blank=True, null=True)
    nom = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128)
    session_token = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='clients/', blank=True, null=True)
    # Récupérer les adresses de livraison et facturation du client
    groups = models.ManyToManyField('auth.Group', related_name='clients_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='clients_permissions', blank=True)

    
    def save(self, *args, **kwargs):
        # Si le mot de passe a été modifié, le hacher avant la sauvegarde
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """Vérifier le mot de passe saisi avec le mot de passe haché."""
        return check_password(raw_password, self.password)
    def __str__(self):
        return self.email

    def generate_session_token(self):
        """Générer un nouveau token de session avec une expiration."""
        self.session_token = uuid.uuid4().hex
        self.token_expiration = timezone.now() + timedelta(minutes=300)
        self.save()

    def is_token_valid(self):
        """Vérifier si le token de session est encore valide."""
        if self.username == "anonymes":
            return True
        return self.token_expiration and self.token_expiration > timezone.now()
    

class NavigationLog(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    produit = models.ForeignKey(Produit, null=True, blank=True, on_delete=models.SET_NULL)
    path = models.CharField(max_length=1024)
    user_agent = models.CharField(max_length=1024)
    referrer = models.CharField(max_length=1024, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    os_info = models.CharField(max_length=255, null=True, blank=True)
    device_type = models.CharField(max_length=50, default='desktop')
    timestamp = models.DateTimeField(default=timezone.now)  # Utilise UTC
    session_duration = models.PositiveIntegerField(default=0)  # Durée de la session en secondes
    fingerprint = models.CharField(max_length=1024, null=True, blank=True)
    def __str__(self):
        return f"Log de navigation pour {self.produit}"
    


class AdresseFacturation(models.Model):
    client = models.ForeignKey(Client, related_name='adresse_facturation', on_delete=models.CASCADE)
    adresse = models.TextField(blank=True, null=True)  # Champ non requis
    code_postal = models.CharField(max_length=20, blank=True, null=True)  # Champ non requis
    ville = models.CharField(max_length=100, blank=True, null=True)  # Champ non requis
    pays = models.CharField(max_length=100, blank=True, null=True)  # Champ non requis
    date_ajoutee = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adresse}, {self.ville}, {self.code_postal}, {self.pays}"
    def to_dict(self):
            return {
                "pk": self.pk,
                "adresse": self.adresse,
                "code_postal": self.code_postal,
                "ville": self.ville,
                "pays": self.pays,
                "date_ajoutee": self.date_ajoutee.isoformat() if self.date_ajoutee else None,
            }

class AdresseLivraison(models.Model):
    client = models.ForeignKey(Client, related_name='adresse_livraison', on_delete=models.CASCADE)
    adresse = models.TextField(blank=True, null=True)  # Champ non requis
    code_postal = models.CharField(max_length=20, blank=True, null=True)  # Champ non requis
    ville = models.CharField(max_length=100, blank=True, null=True)  # Champ non requis
    pays = models.CharField(max_length=100, blank=True, null=True)  # Champ non requis
    date_ajoutee = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adresse}, {self.ville}, {self.code_postal}, {self.pays}"
    def to_dict(self):
            return {
                "pk": self.pk,
                "adresse": self.adresse,
                "code_postal": self.code_postal,
                "ville": self.ville,
                "pays": self.pays,
                "date_ajoutee": self.date_ajoutee.isoformat() if self.date_ajoutee else None,
        }

=======
import uuid
import logging
from datetime import timedelta
from typing import Any, Optional, TYPE_CHECKING

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify

from produits.models import Produit

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


# ===================================
# UTILITAIRES
# ===================================

def client_image_upload_path(instance: models.Model, filename: str) -> str:
    """Génère le chemin de stockage pour l'image du client"""
    ext = filename.split('.')[-1]
    client_id = getattr(instance, 'id', 'new')
    email_slug = slugify(getattr(instance, 'email', 'client'))
    return f"clients/{client_id}/{email_slug}.{ext}"


# ===================================
# MODÈLE CLIENT
# ===================================

class Client(AbstractUser):
    """
    Modèle utilisateur personnalisé pour les clients
    Hérite de AbstractUser pour bénéficier des fonctionnalités Django
    """
    
    if TYPE_CHECKING:
        # Relations inverses
        adresse_facturation: 'QuerySet[AdresseFacturation]'
        adresse_livraison: 'QuerySet[AdresseLivraison]'
        navigation_logs: 'QuerySet[NavigationLog]'
        paniers: 'QuerySet[Any]'
        commandes: 'QuerySet[Any]'
    
    # ===================================
    # CHAMPS DE BASE
    # ===================================
    
    username = models.CharField(
        max_length=150,  # Standard Django
        unique=True,
        default='anonyme',
        verbose_name='Nom d\'utilisateur',
        help_text='Requis. 150 caractères max. Lettres, chiffres et @/./+/-/_ uniquement.',
        validators=[MinLengthValidator(3)],
        db_index=True
    )
    
    prenom = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Prénom'
    )
    
    nom = models.CharField(
        max_length=50,
        verbose_name='Nom de famille',
                blank=True,

    )
    
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        db_index=True,
        error_messages={
            'unique': 'Un compte avec cet email existe déjà.',
        }
    )
    
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Téléphone',
        help_text='Format: +33 6 12 34 56 78'
    )
    
    # ===================================
    # IMAGE PROFIL
    # ===================================
    
    image = models.ImageField(
        upload_to=client_image_upload_path,
        blank=True,
        null=True,
        verbose_name='Photo de profil',
        help_text='Format recommandé: 300x300px, JPG/PNG'
    )
    
    # ===================================
    # AUTHENTIFICATION ET SESSION
    # ===================================
    
    session_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Token de session',
        db_index=True
    )
    
    token_expiration = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expiration du token',
        db_index=True
    )
    
    # ===================================
    # DATES ET STATUTS
    # ===================================
    
    date_inscription = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'inscription'
    )
    
    date_derniere_connexion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Dernière connexion'
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Compte actif',
        help_text='Décocher pour désactiver le compte sans le supprimer',
        db_index=True
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Email vérifié',
        help_text='True si l\'email a été vérifié'
    )
    
    # ===================================
    # PRÉFÉRENCES
    # ===================================
    
    newsletter = models.BooleanField(
        default=False,
        verbose_name='Newsletter',
        help_text='Recevoir les actualités et promotions'
    )
    
    notifications_commande = models.BooleanField(
        default=True,
        verbose_name='Notifications commandes',
        help_text='Recevoir les notifications de suivi de commande'
    )
    
    langue = models.CharField(
        max_length=10,
        default='fr',
        choices=[
            ('fr', 'Français'),
            ('en', 'English'),
            ('es', 'Español'),
        ],
        verbose_name='Langue préférée'
    )
    
    # ===================================
    # RELATIONS MANY-TO-MANY (PERMISSIONS)
    # ===================================
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='clients_set',
        blank=True,
        verbose_name='Groupes',
        help_text='Les groupes auxquels appartient cet utilisateur.'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='clients_set',
        blank=True,
        verbose_name='Permissions',
        help_text='Permissions spécifiques pour cet utilisateur.'
    )

    # ===================================
    # META ET CONFIGURATION
    # ===================================

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-date_inscription']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['session_token']),
            models.Index(fields=['is_active', '-date_inscription']),
        ]

    # ===================================
    # MÉTHODES STANDARD
    # ===================================

    def __str__(self) -> str:
        if self.prenom and self.nom:
            return f"{self.prenom} {self.nom}"
        return self.email

    def clean(self) -> None:
        """Validation des données"""
        super().clean()
        
        # Email en minuscules
        if self.email:
            self.email = self.email.lower().strip()
        
        # Validation username
        if self.username == 'anonyme' and self.is_active:
            raise ValidationError({
                'username': 'Le nom d\'utilisateur "anonyme" est réservé.'
            })
        
        # Validation téléphone
        if self.telephone:
            # Nettoyer le téléphone
            self.telephone = self.telephone.strip()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save pour hasher le mot de passe et nettoyer les données"""
        
        # Hasher le mot de passe si modifié
        if self.pk is None:  # Nouveau client
            if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
                self.password = make_password(self.password)
        else:  # Client existant
            old_instance = Client.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.password != self.password:
                if not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
                    self.password = make_password(self.password)
        
        # Validation
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        logger.info(f"✅ Client sauvegardé: {self.email}")

    # ===================================
    # AUTHENTIFICATION
    # ===================================

    def check_password(self, raw_password: str) -> bool:
        """Vérifier le mot de passe saisi avec le mot de passe haché"""
        return check_password(raw_password, self.password)

    def set_password(self, raw_password: str) -> None:
        """Définir un nouveau mot de passe"""
        if not raw_password or len(raw_password) < 8:
            raise ValidationError('Le mot de passe doit contenir au moins 8 caractères.')
        
        self.password = make_password(raw_password)
        self.save(update_fields=['password'])
        logger.info(f"🔐 Mot de passe modifié pour {self.email}")

    # ===================================
    # GESTION DES SESSIONS
    # ===================================

    def generate_session_token(self, duration_minutes: int = 300) -> str:
        """
        Génère un nouveau token de session avec une expiration
        
        Args:
            duration_minutes: Durée de validité du token en minutes (défaut: 5h)
        
        Returns:
            Le token généré
        """
        self.session_token = uuid.uuid4().hex
        self.token_expiration = timezone.now() + timedelta(minutes=duration_minutes)
        self.date_derniere_connexion = timezone.now()
        self.save(update_fields=['session_token', 'token_expiration', 'date_derniere_connexion'])
        
        logger.info(f"🔑 Token généré pour {self.email} (expire: {self.token_expiration})")
        return self.session_token

    def is_token_valid(self) -> bool:
        """Vérifier si le token de session est encore valide"""
        # Utilisateur anonyme toujours valide
        if self.username == 'anonyme':
            return True
        
        # Pas de token
        if not self.session_token or not self.token_expiration:
            return False
        
        # Token expiré
        if self.token_expiration <= timezone.now():
            logger.warning(f"⏰ Token expiré pour {self.email}")
            return False
        
        return True

    def invalidate_token(self) -> None:
        """Invalider le token de session (déconnexion)"""
        self.session_token = None
        self.token_expiration = None
        self.save(update_fields=['session_token', 'token_expiration'])
        logger.info(f"🚪 Déconnexion de {self.email}")

    def refresh_token(self, duration_minutes: int = 300) -> str:
        """
        Rafraîchit le token si encore valide
        
        Returns:
            Le nouveau token ou le token actuel
        """
        if self.is_token_valid():
            return self.generate_session_token(duration_minutes)
        
        raise ValidationError('Token expiré ou invalide. Veuillez vous reconnecter.')

    # ===================================
    # MÉTHODES UTILITAIRES
    # ===================================

    def get_nom_complet(self) -> str:
        """Retourne le nom complet du client"""
        if self.prenom and self.nom:
            return f"{self.prenom} {self.nom}"
        if self.nom:
            return self.nom
        return self.email.split('@')[0]

    def get_nom_court(self) -> str:
        """Retourne le prénom ou le début de l'email"""
        if self.prenom:
            return self.prenom
        return self.email.split('@')[0]

    def get_initiales(self) -> str:
        """Retourne les initiales (pour avatar)"""
        if self.prenom and self.nom:
            return f"{self.prenom[0]}{self.nom[0]}".upper()
        if self.nom:
            return self.nom[0].upper()
        return self.email[0].upper()

    def get_adresse_facturation_principale(self) -> Optional['AdresseFacturation']:
        """Retourne l'adresse de facturation la plus récente"""
        return self.adresse_facturation.order_by('-date_ajoutee').first()

    def get_adresse_livraison_principale(self) -> Optional['AdresseLivraison']:
        """Retourne l'adresse de livraison la plus récente"""
        return self.adresse_livraison.order_by('-date_ajoutee').first()

    def nombre_commandes(self) -> int:
        """Retourne le nombre de commandes du client"""
        return self.commandes.count() if hasattr(self, 'commandes') else 0

    def a_deja_commande(self) -> bool:
        """Vérifie si le client a déjà passé une commande"""
        return self.nombre_commandes() > 0


# ===================================
# MODÈLE NAVIGATION LOG
# ===================================

class NavigationLog(models.Model):
    """
    Enregistre les navigations des utilisateurs pour analyse
    """
    
    TYPE_DEVICE_CHOICES = [
        ('desktop', '🖥️ Desktop'),
        ('tablet', '📱 Tablette'),
        ('mobile', '📱 Mobile'),
        ('bot', '🤖 Bot'),
    ]
    
    client = models.ForeignKey(
        Client,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='navigation_logs',
        verbose_name='Client'
    )
    
    produit = models.ForeignKey(
        Produit,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='navigation_logs',
        verbose_name='Produit consulté'
    )
    
    path = models.CharField(
        max_length=1024,
        verbose_name='Chemin URL',
        db_index=True
    )
    
    user_agent = models.CharField(
        max_length=1024,
        verbose_name='User Agent'
    )
    
    referrer = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        verbose_name='Référent',
        db_index=True
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Adresse IP',
        db_index=True
    )
    
    os_info = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Système d\'exploitation'
    )
    
    device_type = models.CharField(
        max_length=50,
        choices=TYPE_DEVICE_CHOICES,
        default='desktop',
        verbose_name='Type d\'appareil',
        db_index=True
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date et heure',
        db_index=True
    )
    
    session_duration = models.PositiveIntegerField(
        default=0,
        verbose_name='Durée de session (secondes)'
    )
    
    fingerprint = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        verbose_name='Empreinte navigateur',
        db_index=True
    )

    class Meta:
        verbose_name = 'Log de navigation'
        verbose_name_plural = 'Logs de navigation'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'client']),
            models.Index(fields=['produit', '-timestamp']),
            models.Index(fields=['device_type', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
        ]

    def __str__(self) -> str:
        client_info = self.client.email if self.client else 'Anonyme'
        produit_info = f" - {self.produit.nom}" if self.produit else ""
        return f"{client_info} | {self.path}{produit_info} | {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


# ===================================
# MODÈLE ADRESSE FACTURATION
# ===================================

class AdresseFacturation(models.Model):
    """Adresse de facturation d'un client"""
    
    client = models.ForeignKey(
        Client,
        related_name='adresse_facturation',
        on_delete=models.CASCADE,
        verbose_name='Client'
    )
    
    adresse = models.TextField(
        verbose_name='Adresse',
        help_text='Numéro et nom de rue'
    )
    
    complement = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Complément d\'adresse',
        help_text='Appartement, bâtiment, etc.'
    )
    
    code_postal = models.CharField(
        max_length=20,
        verbose_name='Code postal',
        db_index=True
    )
    
    ville = models.CharField(
        max_length=100,
        verbose_name='Ville',
        db_index=True
    )
    
    pays = models.CharField(
        max_length=100,
        default='France',
        verbose_name='Pays'
    )
    
    est_principale = models.BooleanField(
        default=False,
        verbose_name='Adresse principale',
        help_text='Une seule adresse principale par client'
    )
    
    date_ajoutee = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'ajout'
    )
    
    date_modifiee = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )

    class Meta:
        verbose_name = 'Adresse de facturation'
        verbose_name_plural = 'Adresses de facturation'
        ordering = ['-est_principale', '-date_ajoutee']
        indexes = [
            models.Index(fields=['client', '-date_ajoutee']),
            models.Index(fields=['code_postal', 'ville']),
        ]

    def __str__(self) -> str:
        principale = " ⭐" if self.est_principale else ""
        return f"{self.adresse}, {self.code_postal} {self.ville}{principale}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Si définie comme principale, retirer le flag des autres"""
        if self.est_principale:
            AdresseFacturation.objects.filter(
                client=self.client,
                est_principale=True
            ).exclude(pk=self.pk).update(est_principale=False)
        
        super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        """Convertit l'adresse en dictionnaire"""
        return {
            "id": self.pk,
            "adresse": self.adresse,
            "complement": self.complement,
            "code_postal": self.code_postal,
            "ville": self.ville,
            "pays": self.pays,
            "est_principale": self.est_principale,
            "date_ajoutee": self.date_ajoutee.isoformat() if self.date_ajoutee else None,
        }


# ===================================
# MODÈLE ADRESSE LIVRAISON
# ===================================

class AdresseLivraison(models.Model):
    """Adresse de livraison d'un client"""
    
    client = models.ForeignKey(
        Client,
        related_name='adresse_livraison',
        on_delete=models.CASCADE,
        verbose_name='Client'
    )
    
    nom_destinataire = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nom du destinataire',
        help_text='Si différent du client'
    )
    
    adresse = models.TextField(
        verbose_name='Adresse',
        help_text='Numéro et nom de rue'
    )
    
    complement = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Complément d\'adresse',
        help_text='Appartement, bâtiment, code d\'accès, etc.'
    )
    
    code_postal = models.CharField(
        max_length=20,
        verbose_name='Code postal',
        db_index=True
    )
    
    ville = models.CharField(
        max_length=100,
        verbose_name='Ville',
        db_index=True
    )
    
    pays = models.CharField(
        max_length=100,
        default='France',
        verbose_name='Pays'
    )
    
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Téléphone de contact',
        help_text='Pour le livreur'
    )
    
    instructions = models.TextField(
        blank=True,
        verbose_name='Instructions de livraison',
        help_text='Digicode, étage, sonnette, etc.'
    )
    
    est_principale = models.BooleanField(
        default=False,
        verbose_name='Adresse principale',
        help_text='Une seule adresse principale par client'
    )
    
    date_ajoutee = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'ajout'
    )
    
    date_modifiee = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )

    class Meta:
        verbose_name = 'Adresse de livraison'
        verbose_name_plural = 'Adresses de livraison'
        ordering = ['-est_principale', '-date_ajoutee']
        indexes = [
            models.Index(fields=['client', '-date_ajoutee']),
            models.Index(fields=['code_postal', 'ville']),
        ]

    def __str__(self) -> str:
        principale = " ⭐" if self.est_principale else ""
        destinataire = f" ({self.nom_destinataire})" if self.nom_destinataire else ""
        return f"{self.adresse}, {self.code_postal} {self.ville}{destinataire}{principale}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Si définie comme principale, retirer le flag des autres"""
        if self.est_principale:
            AdresseLivraison.objects.filter(
                client=self.client,
                est_principale=True
            ).exclude(pk=self.pk).update(est_principale=False)
        
        super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        """Convertit l'adresse en dictionnaire"""
        return {
            "id": self.pk,
            "nom_destinataire": self.nom_destinataire,
            "adresse": self.adresse,
            "complement": self.complement,
            "code_postal": self.code_postal,
            "ville": self.ville,
            "pays": self.pays,
            "telephone": self.telephone,
            "instructions": self.instructions,
            "est_principale": self.est_principale,
            "date_ajoutee": self.date_ajoutee.isoformat() if self.date_ajoutee else None,
        }


# ===================================
# TOKEN POUR CLIENT
# ===================================

class ClientToken(models.Model):
    """
    Token d'authentification pour les clients (alternative à rest_framework.authtoken)
    """
    key = models.CharField(
        max_length=40,
        primary_key=True,
        verbose_name='Clé'
    )
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name='auth_token',
        verbose_name='Client'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Token Client'
        verbose_name_plural = 'Tokens Clients'

    def save(self, *args, **kwargs):
        if not self.key:
            import binascii
            import os
            self.key = binascii.hexlify(os.urandom(20)).decode()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Token pour {self.client.username}'
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
