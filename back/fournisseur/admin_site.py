"""
Site d'administration personnalisé pour les fournisseurs
Séparé de l'admin principal pour des permissions différentes
"""

from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class FournisseurAdminSite(AdminSite):
    """
    Site d'administration personnalisé pour les fournisseurs
    """

    # Configuration du site
    site_header = "🌱 Espace Fournisseur - La Providence"
    site_title = "Espace Fournisseur"
    index_title = "Bienvenue dans votre espace fournisseur"

    # URL du site fournisseur
    name = 'fournisseur_admin'

    # Templates personnalisés
    index_template = 'admin/fournisseur/index.html'
    login_template = 'admin/fournisseur/login.html'

    def has_permission(self, request):
        """
        Vérifie si l'utilisateur connecté a les permissions pour accéder

        Un fournisseur peut accéder s'il est:
        - is_staff = True
        - ET son username commence par 'fournisseur_'
        """
        if not request.user.is_active:
            return False

        # Vérifier si c'est un compte fournisseur
        if request.user.is_staff and request.user.username.startswith('fournisseur_'):
            return True

        return False

    def index(self, request, extra_context=None):
        """
        Page d'accueil personnalisée pour les fournisseurs
        """
        extra_context = extra_context or {}

        # Récupérer le fournisseur associé
        if hasattr(request.user, 'fournisseur'):
            fournisseur = request.user.fournisseur
            extra_context['fournisseur'] = fournisseur

            # Statistiques rapides
            from produits.models import Produit
            from commandes.models import Commande
            from paniers.models import LignePanier

            # Nombre de produits du fournisseur
            nb_produits = Produit.objects.filter(fournisseur=fournisseur).count()
            extra_context['nb_produits'] = nb_produits

            # Nombre de commandes contenant des produits du fournisseur
            commandes_ids = LignePanier.objects.filter(
                produit__fournisseur=fournisseur
            ).values_list('panier__commande__id', flat=True).distinct()
            nb_commandes = len([c for c in commandes_ids if c is not None])
            extra_context['nb_commandes'] = nb_commandes

        return super().index(request, extra_context)


# Instance du site fournisseur
fournisseur_admin_site = FournisseurAdminSite(name='fournisseur_admin')
