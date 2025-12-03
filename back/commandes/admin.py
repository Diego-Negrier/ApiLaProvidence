from django.contrib import admin
from .models import * 

class HistoriqueLignePanierInline(admin.TabularInline):
    model = HistoriqueLignePanier
    readonly_fields = ('produit','poids', 'quantite', 'prix')


class HistoriqueCommandeAdmin(admin.ModelAdmin):
    inlines = [HistoriqueLignePanierInline]

    list_display = ('pk','statut','action','client', 'commande',  'total')



# Enregistrer le modèle HistoriquePanier dans l'admin
admin.site.register(HistoriqueCommande,HistoriqueCommandeAdmin)



# Admin pour Commande

class CommandeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'client', 'livreur', 'date_commande', 'statut', 'total')
    readonly_fields = ('date_commande', 'total')  # Rendre certains champs en lecture seule

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        
        if request.user.groups.filter(name='Administrateurs').exists():
            # Les administrateurs voient toutes les commandes
            return queryset
        elif request.user.groups.filter(name='Fournisseurs').exists():
            # Les fournisseurs voient uniquement les commandes contenant leurs produits
            try:
                fournisseur = Fournisseur.objects.get(user=request.user)
                # Filtrer les commandes qui contiennent les produits du fournisseur
                queryset = queryset.filter(panier__lignes__produit__fournisseur=fournisseur).distinct()
            except Fournisseur.DoesNotExist:
                queryset = queryset.none()  # Aucun résultat si aucun fournisseur associé
        else:
            # Autres utilisateurs n'ont pas accès
            queryset = queryset.none()
        return queryset

    def get_readonly_fields(self, request, obj=None):
        # Si l'utilisateur est un administrateur, permettre l'édition
        if request.user.groups.filter(name='Administrateurs').exists():
            return self.readonly_fields
        # Si l'utilisateur est un fournisseur, rendre tous les champs en lecture seule
        if request.user.groups.filter(name='Fournisseurs').exists():
            return self.list_display  # Champs en lecture seule
        return self.readonly_fields

# Enregistrement dans l'admin
admin.site.register(Commande, CommandeAdmin)