from django.db import models
from clients.models import Client
from produits.models import Produit,StatutProduit
from produits.forms import StatutProduit
# Create your models here.
# ---------------------------- MODELE PANIER ----------------------------


class Panier(models.Model):

    

    statut = models.CharField(max_length=20, choices=[('actif', 'Actif'), ('termine', 'Terminé')], default='actif')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='panier')
    date_creation = models.DateTimeField(auto_now_add=True)

    def ajouter_produit(self, produit, quantite=1):
        """Ajouter ou mettre à jour un produit dans le panier."""
        ligne_panier, created = LignePanier.objects.get_or_create(
            panier=self, produit=produit, defaults={'quantite': quantite}
        )
        if not created:
            ligne_panier.quantite += quantite
            ligne_panier.save()

    def enlever_produit(self, produit, quantite=1):
        """Enlever un produit du panier."""
        try:
            ligne_panier = LignePanier.objects.get(panier=self, produit=produit)
            if ligne_panier.quantite <= quantite:
                ligne_panier.delete()
            else:
                ligne_panier.quantite -= quantite
                ligne_panier.save()
        except LignePanier.DoesNotExist:
            pass

    def supprimer_produit(self, produit):
        """Supprimer complètement un produit du panier."""
        LignePanier.objects.filter(panier=self, produit=produit).delete()
    def calculer_poids_total(self):
        poids_total = 0
        for ligne in self.lignes.all():
            poids_total += ligne.produit.poids * ligne.quantite
        return poids_total
    

    def vider_panier(self):
        """Vider complètement le panier."""
        self.lignes.all().delete()


    def afficher_lignes(self):
        """Afficher les lignes de produit dans le panier avec leur quantité et nom."""
        lignes = self.lignes.all()  # Récupérer toutes les lignes du panier
        return [(ligne.produit.nom, ligne.quantite, ligne.statut) for ligne in lignes]
    def __str__(self):
        return f"Panier {self.pk}"

class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, related_name='lignes', on_delete=models.CASCADE)

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    date_ajoutee = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutProduit.choices,
        default=StatutProduit.EN_ATTENTE
    )

    def fournisseur(self):
        """Retourner le fournisseur du produit associé à cette ligne de panier."""
        return self.produit.fournisseur
    
    def __str__(self):
        return f"Panier# {self.pk} {self.produit.nom}-x {self.produit.fournisseur})"