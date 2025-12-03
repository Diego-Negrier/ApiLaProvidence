"""
URL configuration for back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from authentification.views import *
from Home.views import Home
from clients.views import *
from produits.views import *
from paniers.views import *
from livraisons.views import * 
from commandes.views import * 


urlpatterns = [
    path('admin/', admin.site.urls),


    ############ BACK #####################

    # Home

    path('',Home,name='home'),


    # Login
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # Ajout de la route pour la déconnexion


    # Fournisseur
    path('fournisseur/', edit_fournisseur, name='edit_fournisseur'),

    
    # Produits
    path('save_image/<int:produit_id>/', save_image, name='save_image'),

    path('catalogue',catalogue_view,name='catalogue'),
    path('produits/ajouter/pk', ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:pk>/', ajouter_produit, name='modifier_produit'),  # Modifier un produit existant
    path('produits/supprimer/<int:pk>/', supprimer_produit, name='supprimer_produit'),  # Supprimer un produit existant

    # Commande

    path('commandes', commande_view, name='commande_view'),
 
    ############ FRONT #####################

    # Connexion
    path('client/inscription/', inscription, name='client-create'),
    path('client/login/', login, name='login_client'),
    path('client/logout/', logout, name='logout_client'),


    # Clients
    path('client/<int:pk>/',view_client, name='view_client'),
    path('client/update/<int:pk>/', update_client, name='update_client'),  # Route pour mettre à jour un client
    path('client/update_client_info/<int:pk>/', update_client_info, name='update_client_info'),  # Route pour mettre à jour un client
    path('client/update/password/<int:pk>/', update_client_password, name='update_client_password'),  # Route pour mettre à jour un client

    path('client/<int:pk>/delete_address_facturation/<int:address_pk>/', view_delete_adresse, name='delete_address_facturation'),
    path('client/<int:pk>/delete_address_livraison/<int:address_pk>/', view_delete_adresse, name='delete_address_livraison'),
    
    path('client/<int:pk>/adresses/', view_get_adresses, name='view_get_adresses'),
        # --- Tracking ---
    path('api/navigation/log/', log_navigation, name='log_navigation'),
    # URL pour la mise à jour de l'adresse de facturation du client
    path('client/update/<int:pk>/adresse_facturation/',update_adresse_facturation, name='update_adresse_facturation'),
    
    # URL pour la mise à jour de l'adresse de livraison du client
    path('client/update/<int:pk>/adresse_livraison/', update_adresse_livraison, name='update_adresse_livraison'),


    # Produits
    path('produits/', produit_view , name='produit-list-create'),
    path('produits/<str:numero_unique>/', produit_detail, name='produit-detail'),
    path('ajouter-produit/<str:numero_unique>/', ajouter_produit_via_qr_code, name='ajouter-produit'),
    path('produits/<str:numero_unique>/update_quantity/', update_product_quantity, name='update_product_quantity'),
    
    # Gestion du panier
    path('panier/', view_cart, name='view_cart'),
    path('panier/ajouter/<str:numero_unique>/', add_to_cart, name='add_to_cart'),
    path('panier/soustraire/<str:numero_unique>/', subtract_to_cart, name='subtract_to_cart'),
    path('panier/supprimer/<str:numero_unique>/', supprimer_produit_panier, name='supprimer_produit_panier'),
    path('panier/vider/', clear_cart, name='clear_cart'),

    # Livraison
    path('livreur/', view_livreurs, name='view_livreurs'),
    path('point-relais/', point_relais_list, name='point_relais_list'),
    path('points-relais/proches/<int:client_id>/', points_relais_proches, name='points_relais_proches'),


    # Commande
    path('creation-commande/', creation_commande, name='creation_commande'),
    path('commande/<int:commande_id>/terminer/', marquer_commande_comme_terminee, name='marquer_commande_comme_terminee'),
    path('client/<int:client_id>/commandes/', commandes_par_client, name='commandes_par_client'),


]
# Ajouter cette ligne pour servir les fichiers statiques en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]