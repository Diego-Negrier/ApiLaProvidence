# commandes/models.py

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count, Q
from decimal import Decimal
from typing import TYPE_CHECKING

from clients.models import Client
from livraisons.models import Livreur, PointRelais
from paniers.models import Panier, LignePanier
from produits.models import Produit, StatutProduit


# ===================================
# STATUTS
# ===================================
class StatutCommande(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    EN_COURS = 'en_cours', 'En cours'
    EN_LIVRAISON = 'en_livraison', 'En livraison'
    TERMINEE = 'terminee', 'Terminée'
    ANNULEE = 'annulee', 'Annulée'


# ===================================
# HISTORIQUE LIGNE PANIER (DÉCLARÉ EN PREMIER)
# ===================================
class HistoriqueLignePanier(models.Model):
    """
    Archive d'une ligne de panier dans une commande terminée/annulée
    """
    
    # Relation avec l'historique de la commande
    historique_commande = models.ForeignKey(
        'HistoriqueCommande',
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    
    # Données du produit (snapshot au moment de la commande)
    produit = models.ForeignKey(
        Produit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Produit'
    )
    nom_produit = models.CharField(
        max_length=255,
        verbose_name='Nom du produit'
    )
    reference_produit = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Référence'
    )
    
    # Quantité et prix
    quantite = models.PositiveIntegerField(
        default=1,
        verbose_name='Quantité'
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire HT'
    )
    poids = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name='Poids (kg)'
    )
    
    # Statut au moment de l'archivage
    statut = models.CharField(
        max_length=50,
        choices=StatutProduit.choices,
        default=StatutProduit.EN_ATTENTE,
        verbose_name='Statut'
    )
    
    # Métadonnées
    date_archivage = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'archivage'
    )
    
    class Meta:
        verbose_name = 'Historique ligne panier'
        verbose_name_plural = 'Historiques lignes panier'
        ordering = ['id']
        indexes = [
            models.Index(fields=['historique_commande']),
        ]
    
    def __str__(self):
        return f"{self.nom_produit} x{self.quantite}"
    
    @property
    def sous_total(self):
        """Calcule le sous-total de la ligne"""
        return self.quantite * self.prix_unitaire
    
    @property
    def poids_total(self):
        """Calcule le poids total de la ligne"""
        return self.quantite * self.poids


# ===================================
# HISTORIQUE COMMANDE
# ===================================
class HistoriqueCommande(models.Model):
    """
    Archive complète d'une commande terminée/annulée
    """
    if TYPE_CHECKING:
        lignes: models.Manager[HistoriqueLignePanier]
    class Action(models.TextChoices):
        TERMINER = 'terminer', 'Terminée'
        ANNULER = 'annuler', 'Annulée'
        REOUVRIR = 'reouvrir', 'Réouverture'
    
    # Relations
    commande = models.OneToOneField(
        'Commande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historique'
    )
    
    # Données archivées CLIENT
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historique_commandes'
    )
    client_nom = models.CharField(max_length=255)
    client_email = models.EmailField(blank=True, null=True)
    client_telephone = models.CharField(max_length=20, blank=True, null=True)
    
    # Données archivées LIVREUR
    livreur = models.ForeignKey(
        Livreur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    livreur_nom = models.CharField(max_length=255, blank=True, null=True)
    
    # Données archivées POINT RELAIS
    point_relais = models.ForeignKey(
        PointRelais,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    point_relais_nom = models.CharField(max_length=255, blank=True, null=True)
    
    # Données commande
    numero_commande = models.CharField(
        max_length=255, 
        unique=True,
        db_index=True
    )
    date_commande = models.DateTimeField()
    date_archivage = models.DateTimeField(auto_now_add=True)
    
    statut_final = models.CharField(
        max_length=50,
        choices=StatutCommande.choices
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        default=Action.TERMINER
    )
    
    # Financier
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Panier archivé
    id_panier = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Historique commande'
        verbose_name_plural = 'Historiques commandes'
        ordering = ['-date_archivage']
        indexes = [
            models.Index(fields=['numero_commande']),
            models.Index(fields=['-date_archivage']),
        ]
    
    def __str__(self):
        return f"Historique {self.numero_commande}"
    
    @property
    def nombre_lignes(self):
        """Retourne le nombre de lignes dans l'historique"""
        return self.lignes.count()
    
    @property
    def nombre_produits(self):
        """Retourne le nombre total de produits"""
        result = self.lignes.aggregate(total=Sum('quantite'))
        return result['total'] or 0
    
    @property
    def poids_total(self):
        """Calcule le poids total de toutes les lignes"""
        return sum(ligne.poids_total for ligne in self.lignes.all())


# ===================================
# MODÈLE COMMANDE
# ===================================
class Commande(models.Model):
    """
    Modèle représentant une commande client
    """
    # Relations
    client = models.ForeignKey(
        Client, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='commandes'
    )

    livreur = models.ForeignKey(
        Livreur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='commandes'
    )

    panier = models.OneToOneField(
        Panier, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='commande'
    )

    point_relais = models.ForeignKey(
        PointRelais, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='commandes'
    )

    # Informations de base
    numero_commande = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True,
        verbose_name='Numéro de commande'
    )

    date_commande = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    statut = models.CharField(
        max_length=20,
        choices=StatutCommande.choices,
        default=StatutCommande.EN_ATTENTE
    )

    avancement = models.FloatField(
        default=0.0,
        verbose_name='Avancement (%)',
        help_text='Pourcentage d\'avancement de la commande'
    )

    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total HT'
    )
    
    # Type hints pour Pylance
    if TYPE_CHECKING:
        historique: HistoriqueCommande

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']
        indexes = [
            models.Index(fields=['numero_commande']),
            models.Index(fields=['statut']),
            models.Index(fields=['-date_commande']),
        ]

    def __str__(self):
        client_nom = self.client.username if self.client else "Client supprimé"
        return f"{self.numero_commande} - {client_nom}"

    # ===================================
    # GÉNÉRATION DU NUMÉRO
    # ===================================
    def generer_numero_commande(self):
        """Génère un numéro de commande unique au format CMD-YYYYMMDD-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        prefix = f'CMD-{date_str}'

        derniere_commande = Commande.objects.filter(
            numero_commande__startswith=prefix
        ).order_by('-numero_commande').first()

        if derniere_commande:
            try:
                dernier_numero = int(derniere_commande.numero_commande.split('-')[-1])
                nouveau_numero = dernier_numero + 1
            except (ValueError, IndexError):
                nouveau_numero = 1
        else:
            nouveau_numero = 1

        return f'{prefix}-{nouveau_numero:04d}'

    # ===================================
    # CRÉATION DE COMMANDE
    # ===================================
    @classmethod
    def creer_depuis_panier(cls, client, livreur=None, point_relais=None):
        """
        Crée une commande à partir du panier actif du client
        et génère un nouveau panier vide

        Returns:
            tuple: (commande, nouveau_panier)
        """
        # Récupérer le panier actif
        panier_actuel = Panier.objects.filter(
            client=client, 
            statut='actif'
        ).first()

        if not panier_actuel:
            raise ValidationError("Aucun panier actif trouvé pour ce client.")

        # Vérifier que le panier contient des produits
        lignes = LignePanier.objects.filter(panier=panier_actuel).select_related('produit')
        if not lignes.exists():
            raise ValidationError("Le panier est vide. Ajoutez des produits avant de créer une commande.")

        # Calculer le total avec Decimal
        total = sum(
            Decimal(str(ligne.quantite)) * ligne.produit.prix_ttc
            for ligne in lignes
        )

        # Marquer le panier comme terminé
        panier_actuel.statut = 'termine'
        panier_actuel.save()

        # Créer la commande
        commande = cls.objects.create(
            client=client,
            livreur=livreur,
            panier=panier_actuel,
            point_relais=point_relais,
            total=total,
            statut=StatutCommande.EN_ATTENTE
        )

        # Créer un nouveau panier vide pour le client
        nouveau_panier = Panier.objects.create(
            client=client,
            statut='actif'
        )

        return commande, nouveau_panier

    # ===================================
    # MISE À JOUR DU STATUT
    # ===================================
    from django.db.models import Count, Q

    def mettre_a_jour_statut(self):
        """
        Met à jour le statut de la commande en fonction des lignes du panier
        """
        if not self.panier:
            return

        # Récupérer toutes les lignes
        lignes = LignePanier.objects.filter(panier=self.panier)
        total_lignes = lignes.count()

        if not lignes.exists():
            self.avancement = 0
            return

        # ✅ Poids par statut
        poids_statuts = {
            'en_attente': 0,
            'en_preparation': 33,
            'en_livraison': 66,
            'termine': 100,
        }

        # ✅ Calcul de l'avancement
        total_avancement = sum(
            poids_statuts.get(ligne.statut, 0)
            for ligne in lignes
        )

        self.avancement = round((total_avancement / total_lignes), 2) if total_lignes > 0 else 0

        # ✅ Compter les statuts EN UNE SEULE REQUÊTE
        statuts_count = lignes.aggregate(
            en_attente=Count('id', filter=Q(statut='en_attente')),
            en_preparation=Count('id', filter=Q(statut='en_preparation')),
            en_livraison=Count('id', filter=Q(statut='en_livraison')),
            termine=Count('id', filter=Q(statut='termine')),
        )

        # ✅ Déterminer le statut global
        if statuts_count['termine'] == total_lignes:
            self.statut = StatutCommande.TERMINEE
        elif statuts_count['en_livraison'] > 0:
            self.statut = StatutCommande.EN_LIVRAISON
        elif statuts_count['en_preparation'] > 0:
            self.statut = StatutCommande.EN_COURS
        else:
            self.statut = StatutCommande.EN_ATTENTE

        self.save()


    # ===================================
    # CALCUL DU TOTAL
    # ===================================
    def calculer_total(self):
        """Recalculer le total à partir des lignes du panier"""
        if self.panier:
            lignes = LignePanier.objects.filter(panier=self.panier).select_related('produit')
            self.total = sum(
                Decimal(str(ligne.quantite)) * ligne.produit.prix 
                for ligne in lignes
            )
            self.save()
        return self.total

    # ===================================
    # ARCHIVAGE (MÉTHODE PRIVÉE)
    # ===================================
    def _archiver(self, action):
        """
        Archive la commande et ses lignes dans l'historique
        """
        if not self.panier:
            raise ValidationError("Aucun panier associé à cette commande")
        
        # Vérifier si l'historique existe déjà
        if getattr(self, 'historique', None):
            print(f"⚠️ Historique déjà existant pour {self.numero_commande}")
            return self.historique
        
        # Créer l'historique de la commande
        historique = HistoriqueCommande.objects.create(
            commande=self,
            client=self.client,
            client_nom=self.client.username if self.client else "Client supprimé",
            client_email=getattr(self.client, 'email', None),
            client_telephone=getattr(self.client, 'telephone', None),
            livreur=self.livreur,
            livreur_nom=self.livreur.nom if self.livreur else None,
            point_relais=self.point_relais,
            point_relais_nom=self.point_relais.nom if self.point_relais else None,
            numero_commande=self.numero_commande,
            date_commande=self.date_commande,
            statut_final=self.statut,
            action=action,
            total=self.total,
            id_panier=self.panier.pk
        )
        
        # Archiver toutes les lignes du panier
        lignes = LignePanier.objects.filter(panier=self.panier).select_related('produit')
        
        lignes_historique = [
            HistoriqueLignePanier(
                historique_commande=historique,
                produit=ligne.produit,
                nom_produit=ligne.produit.nom,
                reference_produit=getattr(ligne.produit, 'reference', ''),
                quantite=ligne.quantite,
                prix_unitaire=ligne.produit.prix,
                poids=ligne.produit.poids if ligne.produit.poids else Decimal('0.000'),
                statut=ligne.statut
            )
            for ligne in lignes
        ]
        
        HistoriqueLignePanier.objects.bulk_create(lignes_historique)
        
        print(f"✅ Historique créé pour {self.numero_commande} avec {len(lignes_historique)} lignes")
        return historique

    # ===================================
    # TERMINER LA COMMANDE
    # ===================================
    def marquer_comme_terminee(self):
        """Marque la commande comme terminée et sauvegarde dans l'historique"""
        if not self.panier:
            raise ValidationError("Aucun panier associé à cette commande")

        lignes = LignePanier.objects.filter(panier=self.panier)
        total_lignes = lignes.count()
        lignes_terminees = lignes.filter(statut=StatutProduit.ARRIVEE).count()

        # Vérifier que toutes les lignes sont terminées
        if lignes_terminees != total_lignes:
            raise ValidationError(
                f"Toutes les lignes doivent être terminées. "
                f"({lignes_terminees}/{total_lignes} terminées)"
            )

        self.statut = StatutCommande.TERMINEE
        self.avancement = 100
        self.save()

        # Archiver
        self._archiver(HistoriqueCommande.Action.TERMINER)

    # ===================================
    # ANNULER LA COMMANDE
    # ===================================
    def annuler_commande(self):
        """Annule la commande et sauvegarde dans l'historique"""
        if self.statut == StatutCommande.TERMINEE:
            raise ValidationError("Impossible d'annuler une commande terminée")

        self.statut = StatutCommande.ANNULEE
        self.save()

        # Archiver
        self._archiver(HistoriqueCommande.Action.ANNULER)

    # ===================================
    # RÉOUVRIR UNE COMMANDE
    # ===================================
    def rouvrir_commande(self):
        """Réouvre une commande terminée ou annulée"""
        if self.statut not in [StatutCommande.TERMINEE, StatutCommande.ANNULEE]:
            raise ValidationError("Seules les commandes terminées ou annulées peuvent être réouvertes")

        # Réinitialiser le statut
        self.statut = StatutCommande.EN_ATTENTE
        self.avancement = 0
        self.save()

        # Remettre toutes les lignes en attente
        if self.panier:
            LignePanier.objects.filter(panier=self.panier).update(
                statut=StatutProduit.EN_ATTENTE
            )

        # Enregistrer dans l'historique
        HistoriqueCommande.objects.create(
            commande=self,
            client=self.client,
            client_nom=self.client.username if self.client else "Client supprimé",
            livreur=self.livreur,
            livreur_nom=self.livreur.nom if self.livreur else None,
            point_relais=self.point_relais,
            point_relais_nom=self.point_relais.nom if self.point_relais else None,
            numero_commande=self.numero_commande,
            date_commande=self.date_commande,
            statut_final=self.statut,
            action=HistoriqueCommande.Action.REOUVRIR,
            total=self.total,
            id_panier=self.panier.pk if self.panier else None
        )

    # ===================================
    # PROPRIÉTÉS UTILES
    # ===================================
    @property
    def nombre_produits(self):
        """Retourne le nombre total de produits dans la commande"""
        if self.panier:
            result = LignePanier.objects.filter(panier=self.panier).aggregate(
                total=Sum('quantite')
            )
            return result['total'] or 0
        return 0

    @property
    def peut_etre_modifiee(self):
        """Vérifie si la commande peut être modifiée"""
        return self.statut in [StatutCommande.EN_ATTENTE, StatutCommande.EN_COURS]

    # ===================================
    # SAVE OVERRIDE
    # ===================================
    def save(self, *args, **kwargs):
        # Générer le numéro de commande si nouveau
        if not self.pk and not self.numero_commande:
            self.numero_commande = self.generer_numero_commande()

        super().save(*args, **kwargs)
