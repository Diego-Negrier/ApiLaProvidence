from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist  # Assurez-vous d'importer cette exception

from .models import (
    Produit,
    Categorie,
    Fournisseur,
    SousCategorie,
    Logo

    )
@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ('nom', 'image')  # Affiche le nom et l'image dans la liste des logos
    search_fields = ('nom',)  # Permet de rechercher par nom

class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'numero_unique', 'stock', 'qr_code_tag')  # Affichage des produits dans la liste
    filter_horizontal = ('logos',)  # Ajoute un filtre horizontal pour associer des logos
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        
        if request.user.groups.filter(name='Administrateurs').exists():
            # Si l'utilisateur est un administrateur, afficher tous les produits
            return queryset
        elif request.user.groups.filter(name='Fournisseurs').exists():
            # Si l'utilisateur est un fournisseur, n'afficher que ses produits
            try:
                fournisseur = Fournisseur.objects.get(user=request.user)
                queryset = queryset.filter(fournisseur=fournisseur)
            except Fournisseur.DoesNotExist:
                queryset = queryset.none()  # Aucun produit si aucun fournisseur n'est associé
        return queryset

    def get_readonly_fields(self, request, obj=None):
        # Pour les administrateurs, permettre l'édition de tous les champs
        if request.user.groups.filter(name='Administrateurs').exists():
            return self.readonly_fields
        # Pour les fournisseurs, rendre tous les champs en lecture seule
        if request.user.groups.filter(name='Fournisseurs').exists():
            return self.list_display  # Rendre tous les champs en lecture seule
        return self.readonly_fields

admin.site.register(Produit, ProduitAdmin)


admin.site.register(Categorie)
admin.site.register(SousCategorie)

class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'metier', 'pays', 'ville', 'type_production', 'experience_annees', 'certifications', 'impact_local')
    search_fields = ('nom', 'prenom', 'metier', 'pays', 'ville')

    # Optionnel : afficher l'image du fournisseur dans la liste
    def get_image(self, obj):
        return obj.photo.url if obj.photo else 'No image'

    get_image.short_description = 'Photo'

    # Afficher la photo dans la liste
    list_display_links = ('nom', 'prenom')

admin.site.register(Fournisseur, FournisseurAdmin)
