# fournisseur/urls.py

from django.urls import path
from .views import FournisseurDetailView, liste_fournisseurs
from .views_espace import (
    fournisseur_login,
    fournisseur_dashboard,
    fournisseur_produits,
    fournisseur_produit_ajouter,
    fournisseur_produit_modifier,
    fournisseur_produit_supprimer,
    fournisseur_profil,
    fournisseur_commandes,
)

app_name = 'fournisseur'

urlpatterns = [
    # Pages publiques
    path('liste/', liste_fournisseurs, name='liste'),
    path('detail/<int:pk>/', FournisseurDetailView.as_view(), name='detail'),

    # Espace fournisseur
    path('login/', fournisseur_login, name='login'),
    path('dashboard/', fournisseur_dashboard, name='dashboard'),
    path('produits/', fournisseur_produits, name='produits'),
    path('produits/ajouter/', fournisseur_produit_ajouter, name='produit_ajouter'),
    path('produits/modifier/<int:pk>/', fournisseur_produit_modifier, name='produit_modifier'),
    path('produits/supprimer/<int:pk>/', fournisseur_produit_supprimer, name='produit_supprimer'),
    path('profil/', fournisseur_profil, name='profil'),
    path('commandes/', fournisseur_commandes, name='commandes'),
]
