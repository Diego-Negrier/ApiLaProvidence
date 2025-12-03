from django.contrib import admin
from .models import (

    Client,
    AdresseLivraison,
    AdresseFacturation,NavigationLog
    )
# Admin pour le modèle Client
# Inline pour les adresses de livraison et de facturation
class AdresseLivraisonInline(admin.TabularInline):
    model = AdresseLivraison
    extra = 1
    fields = ['adresse', 'code_postal', 'ville', 'pays']

class AdresseFacturationInline(admin.TabularInline):
    model = AdresseFacturation
    extra = 1
    fields = ['adresse', 'code_postal', 'ville', 'pays']
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('username', 'nom', 'prenom', 'email', 'is_active', 'is_staff', 'last_login')
    list_filter = ('is_active', 'is_staff', 'date_inscription')
    search_fields = ('username', 'email', 'nom', 'prenom')
    readonly_fields = ('date_inscription', 'last_login', 'session_token', 'token_expiration')
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('username', 'nom', 'prenom', 'email')
        }),
        ('Authentification', {
            'fields': ('password', 'session_token', 'token_expiration')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {
            'fields': ('date_inscription', 'last_login')
        }),
    )


admin.site.register(AdresseFacturation)
admin.site.register(AdresseLivraison)
# Enregistrer le modèle avec son administration personnalisée

class NavigationLogAdmin(admin.ModelAdmin):
    # Liste des champs à afficher dans la liste des objets
    list_display = ('client', 'produit','fingerprint','path', 'user_agent', 'ip_address', 'device_type', 'session_duration','timestamp')
    
    # Ajouter un champ de recherche pour 'journalist' et 'article'
    search_fields = ('client__username', 'article__title', 'path')
    
    # Ajouter un filtre dans la colonne de l'admin
    list_filter = ('device_type', 'client')
    
    # Personnaliser les champs de formulaire dans l'admin
    fields = ('client', 'produit','fingerprint', 'path', 'user_agent', 'referrer', 'ip_address', 'os_info', 'device_type', 'session_duration')
    
    # Utiliser session_start_time pour date_hierarchy
    date_hierarchy = 'timestamp'  # Affichage hiérarchique des dates en fonction de session_start_time

    def get_readonly_fields(self, request, obj=None):
        # Vous pouvez définir certains champs comme "readonly" si nécessaire
        return ['session_duration']

admin.site.register(NavigationLog, NavigationLogAdmin)
