from rest_framework import serializers
from clients.models import Client
from fournisseur.models import Fournisseur
from produits.models import Produit,Categorie,SousCategorie,SousSousCategorie
from paniers.models import Panier, LignePanier
from commandes.models import Commande
from livraisons.models import Livreur,Tarif


# ============= AUTH SERIALIZERS =============
class ClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['pk', 'username', 'email']
        read_only_fields = ['id']


class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    prenom = serializers.CharField(required=False, allow_blank=True)
    nom = serializers.CharField(required=False, allow_blank=True)
    telephone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Client
        fields = ['username', 'email', 'password', 'password_confirm', 'prenom', 'nom', 'telephone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        # Retirer password_confirm car ce n'est pas un champ du modèle
        validated_data.pop('password_confirm')

        # Créer le client avec create_user pour bien hasher le mot de passe
        client = Client.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            prenom=validated_data.get('prenom', ''),
            nom=validated_data.get('nom', ''),
            telephone=validated_data.get('telephone', '')
        )
        return client


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=255)  # ✅ Changé
    password = serializers.CharField(write_only=True)


# ============= CLIENT SERIALIZERS =============
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


# serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from clients.models import Client, AdresseFacturation, AdresseLivraison


class AdresseFacturationSerializer(serializers.ModelSerializer):
    """Serializer pour les adresses de facturation"""
    
    class Meta:
        model = AdresseFacturation
        fields = ['pk', 'adresse', 'code_postal', 'ville', 'pays']
        read_only_fields = ['pk']

    def validate_code_postal(self, value):
        """Validation du code postal"""
        if not value.isdigit() or len(value) != 5:
            raise serializers.ValidationError("Le code postal doit contenir 5 chiffres.")
        return value


class AdresseLivraisonSerializer(serializers.ModelSerializer):
    """Serializer pour les adresses de livraison"""
    
    class Meta:
        model = AdresseLivraison
        fields = ['pk', 'adresse', 'code_postal', 'ville', 'pays']
        read_only_fields = ['pk']

    def validate_code_postal(self, value):
        """Validation du code postal"""
        if not value.isdigit() or len(value) != 5:
            raise serializers.ValidationError("Le code postal doit contenir 5 chiffres.")
        return value


class ClientParametreSerializer(serializers.ModelSerializer):
    """Serializer pour les paramètres généraux du client"""
    
    adresse_facturation = AdresseFacturationSerializer(many=True, read_only=True)
    adresse_livraison = AdresseLivraisonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'pk',
            'username',
            'email',
            'prenom',
            'nom',
            'telephone',
            'adresse_facturation',
            'adresse_livraison',
        ]
        read_only_fields = ['pk', 'username', 'adresse_facturation', 'adresse_livraison']

    def validate_email(self, value):
        """Validation de l'email"""
        if Client.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """Vérifier que les nouveaux mots de passe correspondent"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Les mots de passe ne correspondent pas.'
            })
        return data


# ============= PRODUIT SERIALIZERS =============
class ProduitSerializer(serializers.ModelSerializer):
    fournisseur_nom = serializers.CharField(source='fournisseur.nom', read_only=True)
    image_principale = serializers.SerializerMethodField()
    icone_produit = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = '__all__'

    def get_image_principale(self, obj):
        """Retourne l'URL complète de l'image principale ou None si pas d'image"""
        from django.conf import settings
        if obj.image_principale:
            # Construire l'URL complète avec MEDIA_BASE_URL
            image_path = str(obj.image_principale)
            return f"{settings.MEDIA_BASE_URL}{image_path}"
        return None

    def get_icone_produit(self, obj):
        """Retourne l'icône intelligente du produit basée sur son nom"""
        from produits.utils import get_smart_product_icon
        return get_smart_product_icon(obj.nom, obj.description_courte or "")


class ProduitDetailSerializer(serializers.ModelSerializer):
    fournisseur = serializers.StringRelatedField()
    image_principale = serializers.SerializerMethodField()
    icone_produit = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = '__all__'

    def get_image_principale(self, obj):
        """Retourne l'URL complète de l'image principale ou None si pas d'image"""
        from django.conf import settings
        if obj.image_principale:
            # Construire l'URL complète avec MEDIA_BASE_URL
            image_path = str(obj.image_principale)
            return f"{settings.MEDIA_BASE_URL}{image_path}"
        return None

    def get_icone_produit(self, obj):
        """Retourne l'icône intelligente du produit basée sur son nom"""
        from produits.utils import get_smart_product_icon
        return get_smart_product_icon(obj.nom, obj.description_courte or "")


# ============= PANIER SERIALIZERS =============
class LignePanierSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        source='produit',
        write_only=True
    )
    sous_total = serializers.SerializerMethodField()
    prix_unitaire = serializers.SerializerMethodField()
    prix_unitaire_ttc = serializers.SerializerMethodField()
    sous_total_ttc = serializers.SerializerMethodField()
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_image = serializers.SerializerMethodField()

    class Meta:
        model = LignePanier
        fields = ['id', 'produit', 'produit_id', 'quantite', 'prix_unitaire', 'sous_total', 'prix_unitaire_ttc', 'sous_total_ttc', 'produit_nom', 'produit_image']
        read_only_fields = ['id', 'prix_unitaire', 'prix_unitaire_ttc', 'sous_total_ttc']

    def get_prix_unitaire(self, obj):
        """Retourne le prix unitaire HT du produit"""
        return float(obj.produit.prix_ht)

    def get_sous_total(self, obj):
        """Retourne le sous-total HT de la ligne"""
        return float(obj.sous_total)

    def get_prix_unitaire_ttc(self, obj):
        """Retourne le prix unitaire TTC du produit"""
        prix_ht = float(obj.produit.prix_ht)
        tva_rate = float(obj.produit.tva) / 100
        prix_ttc = prix_ht * (1 + tva_rate)
        return float(prix_ttc)

    def get_sous_total_ttc(self, obj):
        """Retourne le sous-total TTC de la ligne"""
        prix_unitaire_ttc = self.get_prix_unitaire_ttc(obj)
        return float(prix_unitaire_ttc * obj.quantite)

    def get_produit_image(self, obj):
        """Retourne l'URL complète de l'image du produit ou None si pas d'image"""
        from django.conf import settings
        if obj.produit.image_principale:
            image_path = str(obj.produit.image_principale)
            return f"{settings.MEDIA_BASE_URL}{image_path}"
        return None


class PanierSerializer(serializers.ModelSerializer):
    lignes = LignePanierSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    total_ht = serializers.SerializerMethodField()
    total_tva = serializers.SerializerMethodField()
    total_ttc = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ['id', 'client', 'date_creation', 'lignes', 'total', 'total_ht', 'total_tva', 'total_ttc']
        read_only_fields = ['id', 'client', 'date_creation']

    def get_total(self, obj):
        """Retourne le total HT du panier"""
        return float(obj.calculer_total())

    def get_total_ht(self, obj):
        """Retourne le total HT du panier"""
        return float(obj.calculer_total())

    def get_total_tva(self, obj):
        """Calcule le montant total de la TVA"""
        total_ht = obj.calculer_total()
        total_tva = 0
        for ligne in obj.lignes.all():
            prix_ht = float(ligne.produit.prix_ht)
            tva_rate = float(ligne.produit.tva) / 100
            tva_ligne = prix_ht * tva_rate * ligne.quantite
            total_tva += tva_ligne
        return float(total_tva)

    def get_total_ttc(self, obj):
        """Retourne le total TTC du panier (HT + TVA)"""
        total_ht = self.get_total_ht(obj)
        total_tva = self.get_total_tva(obj)
        return float(total_ht + total_tva)


# ============= COMMANDE SERIALIZERS =============
class CommandeSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.get_full_name', read_only=True)
    lignes = serializers.SerializerMethodField()
    montant_total_ttc = serializers.SerializerMethodField()
    montant_total_ht = serializers.SerializerMethodField()
    montant_total_tva = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = '__all__'
        read_only_fields = ['id', 'numero_commande', 'date_commande', 'client']

    def get_lignes(self, obj):
        """Récupère les lignes du panier associé à la commande"""
        if obj.panier:
            lignes = obj.panier.lignes.all()
            return LignePanierSerializer(lignes, many=True).data
        return []

    def get_montant_total_ht(self, obj):
        """Calcule le montant total HT à partir des lignes du panier"""
        if obj.panier:
            from decimal import Decimal
            total_ht = Decimal('0.00')
            for ligne in obj.panier.lignes.all():
                # Calcul HT = quantité × prix_unitaire (qui est supposé être HT)
                prix_ht = ligne.produit.prix_ht if hasattr(ligne.produit, 'prix_ht') else ligne.prix_unitaire
                total_ht += ligne.quantite * prix_ht
            return str(total_ht)
        return "0.00"

    def get_montant_total_tva(self, obj):
        """Calcule le montant total de TVA"""
        if obj.panier:
            from decimal import Decimal
            total_tva = Decimal('0.00')
            for ligne in obj.panier.lignes.all():
                # Calcul TVA = quantité × prix_unitaire × (taux_tva / 100)
                prix_ht = ligne.produit.prix_ht if hasattr(ligne.produit, 'prix_ht') else ligne.prix_unitaire
                taux_tva = ligne.produit.tva if hasattr(ligne.produit, 'tva') else Decimal('20.00')
                total_tva += ligne.quantite * prix_ht * (taux_tva / 100)
            return str(total_tva)
        return "0.00"

    def get_montant_total_ttc(self, obj):
        """Calcule le montant total TTC"""
        # Le champ 'total' contient déjà le montant TTC après le calcul dans creer_depuis_panier
        return str(obj.total)


class CommandeDetailSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    lignes = serializers.SerializerMethodField()
    montant_total_ttc = serializers.SerializerMethodField()
    montant_total_ht = serializers.SerializerMethodField()
    montant_total_tva = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = '__all__'

    def get_lignes(self, obj):
        """Récupère les lignes du panier associé à la commande"""
        if obj.panier:
            lignes = obj.panier.lignes.all()
            return LignePanierSerializer(lignes, many=True).data
        return []

    def get_montant_total_ht(self, obj):
        """Calcule le montant total HT à partir des lignes du panier"""
        if obj.panier:
            from decimal import Decimal
            total_ht = Decimal('0.00')
            for ligne in obj.panier.lignes.all():
                # Calcul HT = quantité × prix_unitaire (qui est supposé être HT)
                prix_ht = ligne.produit.prix_ht if hasattr(ligne.produit, 'prix_ht') else ligne.prix_unitaire
                total_ht += ligne.quantite * prix_ht
            return str(total_ht)
        return "0.00"

    def get_montant_total_tva(self, obj):
        """Calcule le montant total de TVA"""
        if obj.panier:
            from decimal import Decimal
            total_tva = Decimal('0.00')
            for ligne in obj.panier.lignes.all():
                # Calcul TVA = quantité × prix_unitaire × (taux_tva / 100)
                prix_ht = ligne.produit.prix_ht if hasattr(ligne.produit, 'prix_ht') else ligne.prix_unitaire
                taux_tva = ligne.produit.tva if hasattr(ligne.produit, 'tva') else Decimal('20.00')
                total_tva += ligne.quantite * prix_ht * (taux_tva / 100)
            return str(total_tva)
        return "0.00"

    def get_montant_total_ttc(self, obj):
        """Calcule le montant total TTC"""
        return str(obj.total)
    


# ============= CATEGORIE SERIALIZERS =============
class SousSousCategorieSerializer(serializers.ModelSerializer):
    nb_produits = serializers.SerializerMethodField()

    class Meta:
        model = SousSousCategorie
        fields = ['pk', 'nom', 'slug', 'description', 'icone', 'est_active', 'ordre', 'nb_produits']

    def get_nb_produits(self, obj):
        return obj.produits.filter(est_actif=True).count()


class SousCategorieSerializer(serializers.ModelSerializer):
    soussouscategories = SousSousCategorieSerializer(many=True, read_only=True)
    nb_produits = serializers.SerializerMethodField()

    class Meta:
        model = SousCategorie
        fields = ['pk', 'nom', 'slug', 'description', 'icone', 'est_active', 'ordre', 'soussouscategories', 'nb_produits']

    def get_nb_produits(self, obj):
        return obj.produits.filter(est_actif=True).count()


class CategorieSerializer(serializers.ModelSerializer):
    souscategories = SousCategorieSerializer(many=True, read_only=True)
    nb_produits = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = ['pk', 'nom', 'slug', 'description', 'image', 'icone', 'est_active', 'ordre', 'souscategories', 'nb_produits']

    def get_nb_produits(self, obj):
        return obj.produits.filter(est_actif=True).count()


# ============= FOURNISSEUR SERIALIZERS =============
class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'


# ============= LIVRAISON SERIALIZERS =============
class TarifSerializer(serializers.ModelSerializer):
    """Serializer pour les tarifs de livraison"""

    class Meta:
        model = Tarif
        fields = ['pk', 'poids_min', 'poids_max', 'prix_ht', 'prix_ttc', 'taux_tva']
        read_only_fields = ['pk']


class LivreurSerializer(serializers.ModelSerializer):
    """Serializer pour les livreurs"""

    tarifs = TarifSerializer(many=True, read_only=True)
    prix_livraison = serializers.SerializerMethodField()
    nom_entreprise = serializers.CharField(source='nom')
    delai_livraison = serializers.SerializerMethodField()

    class Meta:
        model = Livreur
        fields = [
            'pk',
            'nom',
            'nom_entreprise',
            'telephone',
            'email',
            'type_service',
            'delai_livraison',
            'est_actif',
            'tarifs',
            'prix_livraison'
        ]
        read_only_fields = ['pk']

    def get_prix_livraison(self, obj):
        """Retourne le prix de base (premier tarif) ou None"""
        premier_tarif = obj.tarifs.first()
        return float(premier_tarif.prix_ttc) if premier_tarif else None

    def get_delai_livraison(self, obj):
        """Retourne le délai de livraison en fonction du type de service"""
        if obj.type_service == 'express':
            return "24h"
        return "3-5 jours"


