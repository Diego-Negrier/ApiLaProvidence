
from .models import Produit
from django.shortcuts import get_object_or_404

from clients.utilis import client_login_required
import json
from .models import (Produit,
                    Categorie,
                    SousCategorie,
                    Fournisseur
                    )
# Create your views here.
from .models import Categorie, SousCategorie
import logging
from .models import Fournisseur
from django.contrib import messages
# views.py



from django.views.generic import ListView, DetailView
from .models import Produit

class ProduitListView(ListView):
    model = Produit
    template_name = "ProduitList.html"
    context_object_name = "produits"
    paginate_by = 24

    def get_queryset(self):
        # Exemple : ne retourner que les produits actifs
        return Produit.objects.filter(est_actif=True).order_by('-date_creation')

class ProduitDetailView(DetailView):
    model = Produit
    template_name = "ProduitDetail.html"
    context_object_name = "produit"

    def get_object(self):
        # On récupère via slug (ou pk si vous préférez)
        slug = self.kwargs.get('slug')
        return get_object_or_404(Produit, slug=slug, est_actif=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        produit = ctx['produit']
        # Descripteurs organisés en dict (clé -> valeur)
        ctx['descripteurs'] = produit.get_descripteurs()
        ctx['descripteurs_dict'] = produit.get_descripteurs_dict()

        # Images
        ctx['images_additionnelles'] = produit.get_images_additionnelles()
        ctx['toutes_images_urls'] = produit.get_toutes_images()
        ctx['nombre_images'] = produit.get_nombre_images()

        # Labels
        ctx['labels'] = produit.logos.all().order_by('ordre')

        # Prix calculés
        ctx['prix_ht'] = produit.prix_ht
        ctx['prix_ttc'] = produit.prix_ttc
        ctx['prix_promo_ht'] = produit.prix_promo_ht
        ctx['prix_promo_ttc'] = produit.prix_promo_ttc
        ctx['economie'] = produit.economie
        return ctx
