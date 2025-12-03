from django.db import models
from clients.models import Client
from livraisons.models import Livreur
from paniers.models import Panier
from livraisons.models import PointRelais
from produits.models import Produit,Fournisseur,StatutProduit
from django.utils import timezone

class StatutCommande(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    EN_COURS = 'en_cours', 'En cours'
    EN_LIVRAISON = 'en_livraison', 'En livraison'

    TERMINEE = 'terminee', 'Terminée'
    ANNULEE = 'annulee', 'Annulée'


# Create your models here.
class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    livreur = models.ForeignKey(Livreur, on_delete=models.SET_NULL, null=True, blank=True)  # Clé étrangère vers Livreur
    panier = models.OneToOneField(Panier, on_delete=models.SET_NULL, null=True, blank=True, related_name='commande')

    date_commande = models.DateTimeField(auto_now_add=True)
    point_relais = models.ForeignKey(PointRelais, on_delete=models.SET_NULL, null=True, blank=True)
    avancement = models.FloatField(default=0.0)  # Champ pour enregistrer le pourcentage d'avancement

    statut = models.CharField(
        max_length=20,
        choices=StatutCommande.choices,
        default=StatutCommande.EN_ATTENTE
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajoutee = models.DateTimeField(auto_now_add=True)


    @classmethod
    def creer_commande_et_nouveau_panier(cls, client, livreur, total, point_relais=None):
        """
        Crée une commande associée à un panier existant ou un nouveau, 
        puis génère un nouveau panier vide pour le client.
        """
        # Récupérer ou créer un panier actif pour le client
        panier_actuel = Panier.objects.filter(client=client, statut='actif').first()

        if not panier_actuel:
            panier_actuel = Panier.objects.create(client=client)

        # Vérifier si le panier est valide pour une commande
        if panier_actuel.lignes.count() == 0:
            raise ValueError("Le panier est vide. Ajoutez des produits avant de créer une commande.")

        # Marquer le panier comme terminé, il n'est plus actif
        panier_actuel.statut = 'termine'
        panier_actuel.save()

        # Créer la commande associée
        commande = cls.objects.create(
            client=client,
            livreur=livreur,
            panier=panier_actuel,
            total=total,
        )

        # Créer un nouveau panier vide pour le client
        nouveau_panier = Panier.objects.create(client=client)

        return commande, nouveau_panier
    def mettre_a_jour_statut(self):
        if self.panier:  # Vérifie si le panier existe
            lignes_en_attente = self.panier.lignes.filter(statut=StatutProduit.EN_ATTENTE)
            # Le reste de votre logique ici
        else:
            # Gérer le cas où il n'y a pas de panier
            raise ValueError("Le panier n'est pas défini pour cette commande")
            # Filtrage des lignes de panier selon leur statut
        lignes_en_attente = self.panier.lignes.filter(statut=StatutProduit.EN_ATTENTE)
        lignes_en_preparation = self.panier.lignes.filter(statut=StatutProduit.EN_PREPARATION)
        lignes_en_livraison = self.panier.lignes.filter(statut=StatutProduit.EN_LIVRAISON)
        lignes_terminees = self.panier.lignes.filter(statut=StatutProduit.TERMINE)
        
        total_lignes = self.panier.lignes.count()
        
        # Calcul de l'avancement : on attribue un pourcentage pour chaque statut
        total_avancement = 0
        if total_lignes > 0:
            for ligne in self.panier.lignes.all():
                if ligne.statut == StatutProduit.TERMINE:
                    total_avancement += 100  # Produit terminé
                elif ligne.statut == StatutProduit.EN_LIVRAISON:
                    total_avancement += 66  # Produit en livraison
                elif ligne.statut == StatutProduit.EN_PREPARATION:
                    total_avancement += 50  # Produit en préparation
                elif ligne.statut == StatutProduit.EN_ATTENTE:
                    total_avancement += 0   # Produit en attente
                else:
                    total_avancement += 0   # Statut inconnu ou par défaut

            # Calcul du pourcentage moyen de l'avancement
            self.avancement = total_avancement / total_lignes
        else:
            self.avancement = 0  # Aucun produit dans le panier, avancement à 0

        # Mise à jour du statut de la commande en fonction des lignes de produit
        if lignes_terminees.count() == total_lignes:
            self.statut = StatutCommande.TERMINEE
        elif lignes_en_livraison.exists():
            self.statut = StatutCommande.EN_LIVRAISON
        elif lignes_en_preparation.exists():
            self.statut = StatutCommande.EN_COURS
        elif lignes_en_attente.exists():
            self.statut = StatutCommande.EN_ATTENTE
        else:
            self.statut = StatutCommande.EN_COURS  # Si rien d'autre, on considère la commande comme en cours


    def calculer_total(self):
        """Calculer le total à partir des lignes du panier"""
        self.total = sum(ligne.produit.prix * ligne.quantite for ligne in self.panier.lignes.all())
        self.save()

    def marquer_comme_terminee(self):
        """Marquer la commande comme terminée et sauvegarder l'historique"""
                # Mise à jour du statut de la commande en fonction des lignes de produit
        lignes_terminees = self.panier.lignes.filter(statut=StatutProduit.TERMINE)
        total_lignes = self.panier.lignes.count()
        if self.statut == StatutCommande.ANNULEE:
            self.sauvegarder_panier_dans_historique()
            self.save()

        if lignes_terminees.count() == total_lignes:
            self.statut = StatutCommande.TERMINEE 
        
        if self.statut == StatutCommande.TERMINEE:
            self.sauvegarder_panier_dans_historique()
            self.save()

    def rouvrir_commande_historique(self):
        """Réouvrir une commande, mettre à jour le statut et enregistrer cette action dans l'historique."""
        if self.statut == StatutCommande.TERMINEE or self.statut == StatutCommande.ANNULEE:
            # Changer le statut de la commande à "en attente"
            self.statut = StatutCommande.EN_ATTENTE
            
            # Mettre toutes les lignes de la commande en "en attente"
            for ligne in self.panier.lignes.all():
                ligne.statut = StatutProduit.EN_ATTENTE
                ligne.save()

            # Sauvegarder les modifications de la commande
            self.save()

            # Sauvegarder l'historique de la commande pour la réouverture
            HistoriqueCommande.objects.create(
                commande=self,
                statut=StatutCommande.EN_ATTENTE,
                action=HistoriqueCommande.Action.REOUVRIR  # Enregistrer l'action comme "réouverture"
            )
     
       
    def sauvegarder_panier_dans_historique(self):
        """Sauvegarder les lignes du panier dans un modèle HistoriqueLignePanier pour éviter les doublons"""
        print(f"Sauvegarde de l'historique pour la commande {self.id}")  # Debug

        if not HistoriqueCommande.objects.filter(commande=self).exists():
            historique_commande, created = HistoriqueCommande.objects.get_or_create(
                commande=self,  # Remplacez par l'objet `Commande` concerné
                defaults={
                    "numero_commande": f"C-{self.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    "client": self.client,
                    "livreur_nom": self.livreur.nom if self.livreur else None,
                    "date_commande": self.date_commande,
                    "statut": self.statut,
                    "total": self.total,
                    "id_panier": self.panier.id if self.panier else None,
                }
            )
            print(f"HistoriqueCommande créé : {historique_commande.numero_commande}")  # Debug
            for ligne in self.panier.lignes.all():
                HistoriqueLignePanier.objects.create(
                    historique_panier=historique_commande,
                    produit=ligne.produit,
                    quantite=ligne.quantite,
                    prix=ligne.produit.prix,
                    poids=ligne.produit.poids
                )
                print(f"Ligne ajoutée à l'historique : {ligne.produit.nom}")  # Debug
    def save(self, *args, **kwargs):
        # Si la commande est terminée et que l'historique n'existe pas déjà, on sauvegarde l'historique
        if not self.pk:  # Vérifie si l'objet est nouveau
                self.statut = StatutCommande.EN_ATTENTE
        super().save(*args, **kwargs)  # Appeler la méthode save originale pour persister la comman



class HistoriqueCommande(models.Model):
    commande = models.OneToOneField(
        Commande,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # Supprimez la virgule ici
    numero_commande = models.CharField(max_length=255, null=True, blank=True, unique=True)  # Nouveau champ pour le numéro de commande sauvegardé
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    livreur_nom = models.CharField(max_length=255, null=True, blank=True)  # Nom du livreur copié
    date_commande = models.DateTimeField(null=True, blank=True)  # Date de la commande
    statut = models.CharField(
        max_length=20,
        choices=StatutCommande.choices,
        default=StatutCommande.EN_ATTENTE
    )
        # Définir les choix pour l'action
    class Action(models.TextChoices):
        TERMINER = 'terminer', 'Terminer'
        REOUVRIR = 'reouvir', 'Réouverture'

    action = models.CharField(
        max_length=20,
        choices=Action.choices,  # Utilisation des choix définis
        null=True,
        blank=True
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    id_panier = models.PositiveIntegerField(null=True, blank=True)  # ID du panier sauvegardé

    def __str__(self):
        return f"Historique - Commande pour {self.client} - {self.statut}"

class HistoriqueLignePanier(models.Model):
    historique_panier = models.ForeignKey(HistoriqueCommande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    poids = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.produit.nom} - Quantité : {self.quantite}"