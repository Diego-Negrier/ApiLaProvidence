from django.db import models
from clients.models import Client
from produits.models import Produit, StatutProduit


# ===================================
# 1️⃣ LIGNE PANIER (EN PREMIER)
# ===================================
class LignePanier(models.Model):
    """Ligne de produit dans un panier"""
    
    panier = models.ForeignKey(
        'Panier',  # ⚠️ IMPORTANT : Guillemets car Panier n'existe pas encore
        related_name='lignes',  # ✅ Crée l'attribut panier.lignes
        on_delete=models.CASCADE
    )
    
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE
    )
    
    quantite = models.PositiveIntegerField(default=1)
    date_ajoutee = models.DateTimeField(auto_now_add=True)
    
    statut = models.CharField(
        max_length=20,
        choices=StatutProduit.choices,
        default=StatutProduit.EN_ATTENTE,
        verbose_name='Statut de préparation'
    )
    
    class Meta:
        verbose_name = 'Ligne de panier'
        verbose_name_plural = 'Lignes de panier'
        unique_together = ['panier', 'produit']
        ordering = ['date_ajoutee']
    
    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"
    
    @property
    def sous_total(self):
        """Calcul du sous-total HT"""
        return self.quantite * self.produit.prix_ht

    def sous_total_ttc(self):
        """Calcul du sous-total TTC"""
        return self.quantite * self.produit.prix_ttc
    
    @property
    def poids_total(self):
        """Calcul du poids total de cette ligne"""
        return self.quantite * (self.produit.poids or 0)
    
    def fournisseur(self):
        """Retourne le fournisseur du produit"""
        return self.produit.fournisseur


# ===================================
# 2️⃣ PANIER (EN SECOND)
# ===================================
class Panier(models.Model):
    """Panier d'achat d'un client"""
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('termine', 'Terminé'),
        ('archive', 'Archivé'),
    ]
    
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='paniers'
    )
    
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='actif'
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Panier #{self.pk} - {self.client.username}"
    
    # ===================================
    # GESTION DES PRODUITS
    # ===================================
    
    def ajouter_produit(self, produit, quantite=1):
        """Ajoute ou met à jour un produit dans le panier"""
        ligne, created = LignePanier.objects.get_or_create(
            panier=self,
            produit=produit,
            defaults={'quantite': quantite}
        )
        
        if not created:
            ligne.quantite += quantite
            ligne.save()
        
        return ligne
    
    def enlever_produit(self, produit, quantite=1):
        """Enlève une quantité d'un produit"""
        try:
            ligne = LignePanier.objects.get(panier=self, produit=produit)
            
            if ligne.quantite <= quantite:
                ligne.delete()
            else:
                ligne.quantite -= quantite
                ligne.save()
        
        except LignePanier.DoesNotExist:
            pass
    
    def supprimer_produit(self, produit):
        """Supprime complètement un produit du panier"""
        LignePanier.objects.filter(panier=self, produit=produit).delete()
    
    def vider_panier(self):
        """Vide complètement le panier"""
        # ✅ Utilisation de LignePanier.objects au lieu de self.lignes
        LignePanier.objects.filter(panier=self).delete()
    
    # ===================================
    # CALCULS
    # ===================================
    
    def calculer_total(self):
        """Calcule le total HT du panier"""
        # ✅ Utilisation de LignePanier.objects
        total = 0
        for ligne in LignePanier.objects.filter(panier=self):
            total += ligne.sous_total
        return total
    
    def calculer_total_ttc(self):
        """Calcule le total TTC du panier"""
        total = 0
        for ligne in LignePanier.objects.filter(panier=self):
            total += ligne.sous_total_ttc()
        return total
    
    def calculer_poids_total(self):
        """Calcule le poids total du panier"""
        poids = 0
        for ligne in LignePanier.objects.filter(panier=self):
            poids += ligne.poids_total
        return poids
    
    def nombre_articles(self):
        """Retourne le nombre total d'articles"""
        total = 0
        for ligne in LignePanier.objects.filter(panier=self):
            total += ligne.quantite
        return total
    
    # ===================================
    # INFORMATIONS
    # ===================================
    
    def afficher_lignes(self):
        """Affiche les lignes avec nom, quantité et statut"""
        lignes = LignePanier.objects.filter(panier=self).select_related('produit')
        return [(l.produit.nom, l.quantite, l.statut) for l in lignes]
    
    def est_vide(self):
        """Vérifie si le panier est vide"""
        return not LignePanier.objects.filter(panier=self).exists()
    
    def get_lignes_par_fournisseur(self):
        """Regroupe les lignes par fournisseur"""
        lignes_par_fournisseur = {}
        
        lignes = LignePanier.objects.filter(panier=self).select_related('produit__fournisseur')
        
        for ligne in lignes:
            fournisseur = ligne.produit.fournisseur
            
            if fournisseur not in lignes_par_fournisseur:
                lignes_par_fournisseur[fournisseur] = []
            
            lignes_par_fournisseur[fournisseur].append(ligne)
        
        return lignes_par_fournisseur
    
    def get_lignes_par_statut(self):
        """Regroupe les lignes par statut"""
        from collections import defaultdict
        lignes_par_statut = defaultdict(list)
        
        for ligne in LignePanier.objects.filter(panier=self):
            lignes_par_statut[ligne.statut].append(ligne)
        
        return dict(lignes_par_statut)
    
    # ===================================
    # STATUT
    # ===================================
    
    def marquer_comme_termine(self):
        """Marque le panier comme terminé"""
        self.statut = 'termine'
        self.save()
    
    def archiver(self):
        """Archive le panier"""
        self.statut = 'archive'
        self.save()
    
    def reinitialiser_statuts_lignes(self):
        """Remet tous les statuts des lignes à EN_ATTENTE"""
        LignePanier.objects.filter(panier=self).update(statut=StatutProduit.EN_ATTENTE)
