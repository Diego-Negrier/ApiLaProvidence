from django.db import models

# Create your models here.
class Livreur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    adresse = models.TextField(blank=True, null=True)
    cle_api = models.CharField(max_length=100, unique=True, blank=True, null=True)
    date_ajoutee = models.DateTimeField(auto_now_add=True)
    date_modifiee = models.DateTimeField(auto_now=True)
    
    TYPE_SERVICE_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
    ]
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
            poids_min__lte=poids_total,
            poids_max__gte=poids_total
        ).first()

        if tarif:
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