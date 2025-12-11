from django.db import models
<<<<<<< HEAD

# Create your models here.
class Livreur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    adresse = models.TextField(blank=True, null=True)
    cle_api = models.CharField(max_length=100, unique=True, blank=True, null=True)
=======
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


class Livreur(models.Model):
    """Modèle représentant un livreur partenaire"""
    
    # ✅ Type hint avec string literal (forward reference)
    if TYPE_CHECKING:
        tarifs: 'QuerySet[Tarif]'  # ✅ Guillemets = référence différée
    
    nom = models.CharField(max_length=100, verbose_name="Nom du livreur")
    telephone = models.CharField(max_length=15, verbose_name="Téléphone")
    email = models.EmailField(unique=True, verbose_name="Email", db_index=True)
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse complète")
    
    cle_api = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Clé API",
        db_index=True
    )
    
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
    date_ajoutee = models.DateTimeField(auto_now_add=True)
    date_modifiee = models.DateTimeField(auto_now=True)
    
    TYPE_SERVICE_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
    ]
<<<<<<< HEAD
    type_service = models.CharField(max_length=20, choices=TYPE_SERVICE_CHOICES, default='standard')

    def __str__(self):
        return f"{self.nom} ({self.email})"

    def calculer_prix_livraison(self, poids_total):
        """
        Calculer le prix de la livraison en fonction du poids.
        """
        # Récupérer le tarif correspondant au poids
        tarif = Tarif.objects.filter(
            livreur=self,
=======
    
    type_service = models.CharField(
        max_length=20,
        choices=TYPE_SERVICE_CHOICES,
        default='standard',
        db_index=True
    )
    
    est_actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Livreur"
        verbose_name_plural = "Livreurs"
        ordering = ['nom']
        indexes = [
            models.Index(fields=['email', 'est_actif']),
            models.Index(fields=['type_service', 'est_actif']),
        ]

    def __str__(self) -> str:
        return f"{self.nom} ({self.email})"

    def calculer_prix_livraison(self, poids_total: float) -> Optional[Decimal]:
        """
        Calcule le prix de la livraison en fonction du poids
        
        Args:
            poids_total: Poids total du colis en kg
        
        Returns:
            Prix TTC en Decimal, ou None si aucun tarif trouvé
        """
        if poids_total <= 0 or not self.est_actif:
            return None
        
        tarif = self.tarifs.filter(
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
            poids_min__lte=poids_total,
            poids_max__gte=poids_total
        ).first()

        if tarif:
<<<<<<< HEAD
            prix = tarif.prix_ttc 
            # Ajouter des frais supplémentaires si nécessaire
            return prix
        else:
            # Gérer le cas où aucun tarif ne correspond
            return None

class Tarif(models.Model):
    livreur = models.ForeignKey(Livreur, on_delete=models.CASCADE, related_name='tarifs')
    poids_min = models.FloatField()  # Poids minimum pour ce tarif
    poids_max = models.FloatField()  # Poids maximum pour ce tarif
    prix_ht = models.DecimalField(max_digits=10, decimal_places=2)  # Prix standard
    prix_ttc = models.DecimalField(max_digits=10, decimal_places=2)  # Prix express

    def __str__(self):
        return f"Tarif pour {self.livreur.nom}: {self.poids_min}kg - {self.poids_max}kg, Prix HT: {self.prix_ht}€, Prix TTC: {self.prix_ttc}€"

class PointRelais(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)  # Assurez-vous que ce champ existe
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.nom
=======
            if self.type_service == 'express':
                return tarif.prix_ttc * Decimal('1.30')
            return tarif.prix_ttc
        
        return None

    def peut_livrer(
        self,
        poids: float,
        code_postal: Optional[str] = None
    ) -> bool:
        """Vérifie si le livreur peut effectuer une livraison"""
        if not self.est_actif:
            return False
        
        if code_postal is not None:
            if not code_postal.isdigit() or len(code_postal) != 5:
                return False
        
        return self.calculer_prix_livraison(poids) is not None


# ✅ Déclaration de Tarif APRÈS Livreur
class Tarif(models.Model):
    """Grille tarifaire d'un livreur"""
    
    livreur = models.ForeignKey(
        Livreur,
        on_delete=models.CASCADE,
        related_name='tarifs',
        verbose_name="Livreur"
    )
    
    poids_min = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Poids minimum (kg)"
    )
    
    poids_max = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Poids maximum (kg)"
    )
    
    prix_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix HT"
    )
    
    prix_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix TTC"
    )
    
    taux_tva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name="Taux TVA (%)"
    )

    class Meta:
        verbose_name = "Tarif"
        verbose_name_plural = "Tarifs"
        ordering = ['livreur', 'poids_min']
        constraints = [
            models.CheckConstraint(
                check=models.Q(poids_max__gt=models.F('poids_min')),
                name='poids_max_superieur_poids_min'
            ),
        ]
        indexes = [
            models.Index(fields=['livreur', 'poids_min', 'poids_max']),
        ]

    def __str__(self) -> str:
        return (
            f"Tarif {self.livreur.nom}: "
            f"{self.poids_min}-{self.poids_max}kg → {self.prix_ttc}€"
        )

    def clean(self):
        """Validation des données"""
        from django.core.exceptions import ValidationError
        
        if self.poids_max <= self.poids_min:
            raise ValidationError({
                'poids_max': 'Le poids maximum doit être supérieur au poids minimum'
            })
        
        # Calculer automatiquement le prix TTC si non fourni
        if not self.prix_ttc and self.prix_ht and self.taux_tva:
            self.prix_ttc = self.prix_ht * (1 + self.taux_tva / 100)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PointRelais(models.Model):
    """Point de retrait pour les colis"""
    
    nom = models.CharField(max_length=255, verbose_name="Nom du point relais")
    adresse = models.CharField(max_length=255, verbose_name="Adresse")
    code_postal = models.CharField(max_length=10, db_index=True, verbose_name="Code postal")
    ville = models.CharField(max_length=100, db_index=True, verbose_name="Ville")
    pays = models.CharField(max_length=100, default='France', verbose_name="Pays")
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal('-90.0')),
            MaxValueValidator(Decimal('90.0'))
        ],
        verbose_name="Latitude"
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal('-180.0')),
            MaxValueValidator(Decimal('180.0'))
        ],
        verbose_name="Longitude"
    )
    
    horaires_ouverture = models.TextField(
        blank=True,
        verbose_name="Horaires d'ouverture",
        help_text="Exemple: Lun-Ven: 9h-18h, Sam: 9h-12h"
    )
    
    telephone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Téléphone"
    )
    
    capacite_max = models.PositiveIntegerField(
        default=50,
        verbose_name="Capacité maximale",
        help_text="Nombre de colis maximum stockables"
    )
    
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    class Meta:
        verbose_name = "Point relais"
        verbose_name_plural = "Points relais"
        ordering = ['ville', 'nom']
        indexes = [
            models.Index(fields=['code_postal', 'ville', 'est_actif']),
        ]

    def __str__(self) -> str:
        return f"{self.nom} - {self.ville} ({self.code_postal})"

    def adresse_complete(self) -> str:
        """Retourne l'adresse complète formatée"""
        return f"{self.adresse}, {self.code_postal} {self.ville}, {self.pays}"

    def calculer_distance_vers(
        self,
        latitude: Optional[float],
        longitude: Optional[float]
    ) -> Optional[float]:
        """
        Calcule la distance vers un point en km (formule de Haversine)
        
        Args:
            latitude: Latitude du point de destination
            longitude: Longitude du point de destination
        
        Returns:
            Distance en kilomètres, ou None si coordonnées invalides
        """
        if latitude is None or longitude is None:
            return None
        
        try:
            from math import radians, sin, cos, sqrt, atan2
            
            R = 6371  # Rayon de la Terre en km
            
            lat1 = radians(float(self.latitude))
            lon1 = radians(float(self.longitude))
            lat2 = radians(latitude)
            lon2 = radians(longitude)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            return round(R * c, 2)
            
        except (ValueError, TypeError):
            return None
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
