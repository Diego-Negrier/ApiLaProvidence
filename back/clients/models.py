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

