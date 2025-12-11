"""
Admins personnalisés pour l'espace fournisseur
Chaque fournisseur ne voit que ses propres données
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import QuerySet, Sum, Count, Q
from django.http import HttpRequest
from django.urls import reverse
from typing import Any, Optional

from .models import Fournisseur, PointLivraison, ZoneLivraison
from produits.models import Produit, ImageProduit
from commandes.models import Commande
from paniers.models import LignePanier, Panier
from .admin_site import fournisseur_admin_site


# ===================================
# HELPERS
# ===================================

def get_fournisseur_from_request(request: HttpRequest) -> Optional[Fournisseur]:
    """
    Récupère le fournisseur associé à l'utilisateur connecté
    """
    if hasattr(request.user, 'fournisseur'):
        return request.user.fournisseur

    # Si pas d'attribut fournisseur, essayer de le récupérer depuis le username
    if request.user.username.startswith('fournisseur_'):
        try:
            fournisseur_id = int(request.user.username.split('_')[1])
            return Fournisseur.objects.get(id=fournisseur_id)
        except (Fournisseur.DoesNotExist, ValueError, IndexError):
            pass

    return None


# ===================================
# ADMIN: PROFIL FOURNISSEUR
# ===================================

@admin.register(Fournisseur, site=fournisseur_admin_site)
class ProfilFournisseurAdmin(admin.ModelAdmin):
    """
    Admin pour que le fournisseur gère son propre profil
    """

    # Affichage de base
    list_display = ['display_nom', 'metier', 'ville', 'email', 'tel']

    # Champs en lecture seule (le fournisseur ne peut pas tout modifier)
    readonly_fields = [
        'date_ajoutee', 'date_modifiee', 'display_stats',
        'display_zone_couverture', 'client'
    ]

    # Champs modifiables par le fournisseur
    fields = (
        ('nom', 'prenom'),
        'email',
        'password',
        'metier',
        ('contact', 'tel'),
        'photo',
        'description',
        ('type_production', 'experience_annees'),
        'certifications',
        'produits_principaux',
        'calendrier_production',
        'saisonnalite_respectee',
        'display_stats',
        'display_zone_couverture',
        ('date_ajoutee', 'date_modifiee'),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Les fournisseurs ne peuvent pas créer de nouveaux profils"""
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        """Les fournisseurs ne peuvent pas supprimer leur profil"""
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Le fournisseur ne voit que son propre profil"""
        qs = super().get_queryset(request)
        fournisseur = get_fournisseur_from_request(request)

        if fournisseur:
            return qs.filter(id=fournisseur.id)

        return qs.none()

    def display_nom(self, obj: Fournisseur) -> str:
        """Affiche le nom complet"""
        return format_html(
            '<strong>{} {}</strong>',
            obj.nom, obj.prenom
        )
    display_nom.short_description = 'Nom complet'

    def display_stats(self, obj: Fournisseur) -> str:
        """Affiche les statistiques du fournisseur"""
        # Nombre de produits
        nb_produits = Produit.objects.filter(fournisseur=obj).count()

        # Nombre de commandes
        commandes_ids = LignePanier.objects.filter(
            produit__fournisseur=obj
        ).values_list('panier__commande__id', flat=True).distinct()
        nb_commandes = len([c for c in commandes_ids if c is not None])

        html = '<div style="background: #e3f2fd; padding: 15px; border-radius: 5px;">'
        html += '<strong>📊 Vos statistiques :</strong><br><br>'
        html += f'<p>📦 <strong>{nb_produits}</strong> produit(s)</p>'
        html += f'<p>📝 <strong>{nb_commandes}</strong> commande(s)</p>'
        html += '</div>'

        return format_html(html)
    display_stats.short_description = 'Statistiques'

    def display_zone_couverture(self, obj: Fournisseur) -> str:
        """Affiche la zone de couverture"""
        html = '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">'
        html += '<strong>🚚 Zone de livraison :</strong><br><br>'

        zone_labels = {
            'rayon': f'Rayon de {obj.rayon_livraison_km} km',
            'departements': 'Par départements',
            'villes': 'Villes spécifiques',
            'national': 'National'
        }

        html += f'<p>{zone_labels.get(obj.zone_livraison_type, obj.zone_livraison_type)}</p>'
        html += f'<p>💰 Frais de base : <strong>{obj.frais_livraison_base} €</strong></p>'

        if obj.livraison_gratuite_montant:
            html += f'<p>🎁 Gratuit dès : <strong>{obj.livraison_gratuite_montant} €</strong></p>'

        html += '</div>'
        return format_html(html)
    display_zone_couverture.short_description = 'Zone de livraison'


# ===================================
# ADMIN: PRODUITS DU FOURNISSEUR
# ===================================

@admin.register(Produit, site=fournisseur_admin_site)
class ProduitFournisseurAdmin(admin.ModelAdmin):
    """
    Gestion des produits par le fournisseur
    """

    list_display = [
        'display_image', 'nom', 'numero_unique',
        'prix_ht', 'statut', 'est_actif', 'date_creation'
    ]

    list_filter = ['est_actif', 'categorie', 'souscategorie', 'statut']

    search_fields = ['nom', 'numero_unique', 'description_longue', 'description_courte']

    readonly_fields = [
        'numero_unique', 'date_creation', 'date_modification',
        'fournisseur', 'display_image_principale', 'slug'
    ]

    fields = (
        'fournisseur',
        'nom',
        'numero_unique',
        'slug',
        'description_longue',
        'description_courte',
        ('prix_ht', 'tva'),
        ('poids', 'unite_mesure'),
        'statut',
        ('categorie', 'souscategorie', 'soussouscategorie'),
        'image_principale',
        'display_image_principale',
        'est_actif',
        ('date_creation', 'date_modification'),
    )

    list_editable = ['est_actif']

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Les fournisseurs peuvent ajouter des produits"""
        return True

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        """Les fournisseurs peuvent supprimer leurs produits"""
        return True

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Le fournisseur ne voit que ses propres produits"""
        qs = super().get_queryset(request)
        fournisseur = get_fournisseur_from_request(request)

        if fournisseur:
            return qs.filter(fournisseur=fournisseur)

        return qs.none()

    def save_model(self, request: HttpRequest, obj: Produit, form, change: bool) -> None:
        """Associe automatiquement le produit au fournisseur connecté"""
        if not change:  # Nouveau produit
            fournisseur = get_fournisseur_from_request(request)
            if fournisseur:
                obj.fournisseur = fournisseur

        super().save_model(request, obj, form, change)

    def display_image(self, obj: Produit) -> str:
        """Affiche l'image du produit"""
        if obj.image_principale:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image_principale.url
            )
        return '—'
    display_image.short_description = 'Image'

    def display_image_principale(self, obj: Produit) -> str:
        """Aperçu de l'image principale"""
        if obj.image_principale:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: contain;" />',
                obj.image_principale.url
            )
        return 'Aucune image'
    display_image_principale.short_description = 'Aperçu image'


# ===================================
# ADMIN: COMMANDES DU FOURNISSEUR
# ===================================

@admin.register(Commande, site=fournisseur_admin_site)
class CommandeFournisseurAdmin(admin.ModelAdmin):
    """
    Vue des commandes contenant des produits du fournisseur
    """

    list_display = [
        'numero_commande', 'display_client', 'date_commande',
        'statut', 'display_mes_produits', 'display_montant_fournisseur'
    ]

    list_filter = ['statut', 'date_commande']

    search_fields = ['numero_commande', 'client__username', 'client__email']

    readonly_fields = [
        'numero_commande', 'date_commande', 'client',
        'panier', 'livreur', 'point_relais', 'total',
        'display_lignes_fournisseur'
    ]

    fields = (
        'numero_commande',
        'client',
        'date_commande',
        'statut',
        'display_lignes_fournisseur',
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Les fournisseurs ne peuvent pas créer de commandes"""
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        """Les fournisseurs ne peuvent pas supprimer de commandes"""
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Le fournisseur ne voit que les commandes contenant ses produits"""
        qs = super().get_queryset(request)
        fournisseur = get_fournisseur_from_request(request)

        if fournisseur:
            # Récupérer les IDs des commandes contenant des produits du fournisseur
            commandes_ids = LignePanier.objects.filter(
                produit__fournisseur=fournisseur
            ).values_list('panier__commande__id', flat=True).distinct()

            return qs.filter(id__in=[c for c in commandes_ids if c is not None])

        return qs.none()

    def display_client(self, obj: Commande) -> str:
        """Affiche le client"""
        if obj.client:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.client.username,
                obj.client.email if hasattr(obj.client, 'email') else ''
            )
        return '—'
    display_client.short_description = 'Client'

    def display_mes_produits(self, obj: Commande) -> str:
        """Affiche le nombre de produits du fournisseur dans cette commande"""
        if not obj.panier:
            return '0'

        fournisseur = get_fournisseur_from_request(self.request)  # type: ignore
        if not fournisseur:
            return '0'

        nb = LignePanier.objects.filter(
            panier=obj.panier,
            produit__fournisseur=fournisseur
        ).count()

        return format_html('<strong>{}</strong>', nb)
    display_mes_produits.short_description = 'Mes produits'

    def display_montant_fournisseur(self, obj: Commande) -> str:
        """Affiche le montant total des produits du fournisseur"""
        if not obj.panier:
            return '0.00 €'

        fournisseur = get_fournisseur_from_request(self.request)  # type: ignore
        if not fournisseur:
            return '0.00 €'

        lignes = LignePanier.objects.filter(
            panier=obj.panier,
            produit__fournisseur=fournisseur
        ).select_related('produit')

        total = sum(ligne.quantite * ligne.produit.prix_ht for ligne in lignes)

        return format_html('<strong style="color: #4caf50;">{:.2f} €</strong>', total)
    display_montant_fournisseur.short_description = 'Montant (mes produits)'

    def display_lignes_fournisseur(self, obj: Commande) -> str:
        """Affiche uniquement les lignes concernant le fournisseur"""
        if not obj.panier:
            return 'Aucune ligne'

        fournisseur = get_fournisseur_from_request(self.request)  # type: ignore
        if not fournisseur:
            return 'Aucune ligne'

        lignes = LignePanier.objects.filter(
            panier=obj.panier,
            produit__fournisseur=fournisseur
        ).select_related('produit')

        if not lignes:
            return 'Aucune ligne'

        html = '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">'
        html += '<strong>📦 Vos produits dans cette commande :</strong><br><br>'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #e0e0e0;"><th style="padding: 8px; text-align: left;">Produit</th><th style="padding: 8px;">Qté</th><th style="padding: 8px;">Prix HT</th><th style="padding: 8px;">Sous-total</th><th style="padding: 8px;">Statut</th></tr>'

        for ligne in lignes:
            sous_total = ligne.quantite * ligne.produit.prix_ht
            html += f'<tr style="border-bottom: 1px solid #ddd;">'
            html += f'<td style="padding: 8px;">{ligne.produit.nom}</td>'
            html += f'<td style="padding: 8px; text-align: center;">{ligne.quantite}</td>'
            html += f'<td style="padding: 8px; text-align: right;">{ligne.produit.prix_ht} €</td>'
            html += f'<td style="padding: 8px; text-align: right;"><strong>{sous_total:.2f} €</strong></td>'
            html += f'<td style="padding: 8px; text-align: center;"><span style="background: #4caf50; color: white; padding: 2px 8px; border-radius: 3px;">{ligne.statut}</span></td>'
            html += f'</tr>'

        html += '</table></div>'
        return format_html(html)
    display_lignes_fournisseur.short_description = 'Détail de vos produits'

    def changelist_view(self, request, extra_context=None):
        """Ajoute le request pour l'utiliser dans les méthodes display"""
        self.request = request
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Ajoute le request pour l'utiliser dans les méthodes display"""
        self.request = request
        return super().changeform_view(request, object_id, form_url, extra_context)
