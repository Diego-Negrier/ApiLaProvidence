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
from Home.views import Home
from clients.views import *
from produits.views import *
from paniers.views import *
from livraisons.views import *
from commandes.views import *
from api.views import *
from django.contrib.auth.views import LogoutView

# Import du site admin fournisseur
from fournisseur.admin_site import fournisseur_admin_site
# Import des admins fournisseur pour les enregistrer
import fournisseur.admin_fournisseur  # noqa

# Import du login unifié
from fournisseur.views_espace import unified_login


urlpatterns = [
    # Admin principal (pour les administrateurs)
    path('admin/', admin.site.urls),

    # Espace fournisseur (pour les fournisseurs connectés)
    path('fournisseur-admin/', fournisseur_admin_site.urls),

    # Logout général
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # Login général (admin ou fournisseur)
    path('login/', unified_login, name='login'),

    ############ BACK #####################

    # Home

    path('',Home,name='home'),

    path('fournisseurs/', include('fournisseur.urls')),  # ✅ Ajouter ceci
    path('magasin/', include('produits.urls', namespace='produits')),



# ==========================================
# API
# ==========================================

    path('api/',include('api.urls'))





]
# ==========================================
# STATIC & MEDIA FILES
# ==========================================

# Whitenoise gère automatiquement les fichiers statiques en production
# En mode DEBUG, servir aussi les fichiers statiques et media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]

# Toujours servir les fichiers media (même en production)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)