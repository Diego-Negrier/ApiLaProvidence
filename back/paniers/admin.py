from django.contrib import admin
from .models import LignePanier,Panier
from produits.models import Fournisseur
# Register your models here.

class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 0  # Pas d'entrées vides supplémentaires

class PanierAdmin(admin.ModelAdmin):
    inlines = [LignePanierInline]
    list_display = ('pk', 'client', 'date_creation', 'total_produits')

    def total_produits(self, obj):
        """Retourne le nombre total de produits dans le panier."""
        return obj.lignes.count()
    total_produits.short_description = 'Total Produits'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Fournisseurs').exists():
            try:
                fournisseur = Fournisseur.objects.get(user=request.user)
                # Filtrer les paniers contenant des produits fournis par ce fournisseur
                queryset = queryset.filter(lignes__produit__fournisseur=fournisseur).distinct()
            except Fournisseur.DoesNotExist:
                queryset = queryset.none()  # Aucun accès si le fournisseur n'existe pas
        return queryset

admin.site.register(Panier, PanierAdmin)

