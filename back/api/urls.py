from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .stripe_views import (
    creer_payment_intent,
    confirmer_paiement,
    recuperer_cle_publique,
    stripe_webhook
)

# app_name = 'api'  # Désactivé temporairement pour debug
# URLs mise à jour avec slashes finaux

urlpatterns = [
    # ============= AUTH =============
    path('login/', api_login, name='api-login'),
    path('logout/', api_logout, name='api-logout'),
    path('inscription/', api_inscription, name='api-inscription'),

    # ============= CLIENT ROUTES =============
    path('<int:pk_client>/parametre/', client_parametre, name='client-parametre'),
    path('clients/<int:pk>/', get_client_detail, name='client_detail'),  # ✅ Nouvelle route
   path('client/update/<int:pk_client>/adresse_facturation/', 
         adresse_facturation_list, 
         name='adresse-facturation-list'),
    path('client/update/<int:pk_client>/adresse_facturation/<int:pk_adresse>/', 
         adresse_facturation_detail, 
         name='adresse-facturation-detail'),
    
    # Adresses de livraison
    path('client/update/<int:pk_client>/adresse_livraison/', 
         adresse_livraison_list, 
         name='adresse-livraison-list'),
    path('client/update/<int:pk_client>/adresse_livraison/<int:pk_adresse>/', 
         adresse_livraison_detail, 
         name='adresse-livraison-detail'),
    
    # Changement de mot de passe
    path('client/update/<int:pk_client>/password/', 
         change_password, 
         name='change-password'),
    
    
    # Panier
    path('<int:pk_client>/panier/', panier_view, name='client-panier'),
    path('<int:pk_client>/panier/<int:pk_ligne>/', ligne_panier_view, name='ligne-panier'),

    # Commandes
    path('<int:pk_client>/commandes/', commandes_view, name='client-commandes'),
    path('<int:pk_client>/commandes/<int:pk_commande>/', commande_detail_view, name='commande-detail'),

    # Fournisseurs du client
    path('<int:pk_client>/fournisseurs/', client_fournisseurs_view, name='client-fournisseurs'),

    # Magasin (vue client)
    path('<int:pk_client>/magasin/', magasin_client_view, name='magasin-client'),
    path('<int:pk_client>/magasin/<int:pk_produit>/', magasin_produit_client_view, name='magasin-produit-client'),

    # ============= FOURNISSEURS (admin) =============

    # ============= ROUTES GLOBALES =============
    path('magasin/', magasin_view, name='magasin'),
    path('magasin/<int:pk_produit>/', magasin_produit_view, name='magasin-produit'),

    # Categories et Fournisseurs publics
    path('categories/', categories_view, name='categories'),
    path('fournisseurs/', fournisseurs_view, name='fournisseurs'),

    # ============= PAIEMENT STRIPE =============
    path('paiement/cle-publique/', recuperer_cle_publique, name='stripe-public-key'),
    path('paiement/webhook/', stripe_webhook, name='stripe-webhook'),
    path('<int:pk_client>/paiement/creer-intent/', creer_payment_intent, name='creer-payment-intent'),
    path('<int:pk_client>/paiement/confirmer/', confirmer_paiement, name='confirmer-paiement'),

    # ============= LIVREURS =============
    path('livreur/', livreurs_view, name='livreurs'),
    path('livreur/<int:pk_livreur>/', livreur_detail_view, name='livreur-detail'),
    path('livreur/<int:pk_livreur>/tarifs/', livreur_tarifs_view, name='livreur-tarifs'),

]
