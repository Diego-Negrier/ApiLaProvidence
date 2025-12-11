from django.contrib import admin
<<<<<<< HEAD
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
=======
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import QuerySet, Count
from django.http import HttpRequest
from typing import Any

from .models import (
    Client, AdresseFacturation, AdresseLivraison, 
    NavigationLog
)


# ===================================
# INLINES
# ===================================

class AdresseFacturationInline(admin.TabularInline):
    """Inline pour les adresses de facturation"""
    model = AdresseFacturation
    extra = 0
    fields = ['adresse', 'code_postal', 'ville', 'pays', 'est_principale']
    readonly_fields = ['date_ajoutee']


class AdresseLivraisonInline(admin.TabularInline):
    """Inline pour les adresses de livraison"""
    model = AdresseLivraison
    extra = 0
    fields = ['adresse', 'code_postal', 'ville', 'pays', 'est_principale']
    readonly_fields = ['date_ajoutee']


# ===================================
# ADMIN CLIENT
# ===================================

@admin.register(Client)
class ClientAdmin(UserAdmin):
    """Administration des clients"""
    
    list_display = [
        'display_avatar', 'email', 'get_nom_complet',
        'username', 'display_statut', 'display_commandes',
        'date_inscription', 'date_derniere_connexion'
    ]
    
    list_filter = [
        'is_active', 'is_verified', 'is_staff',
        'newsletter', 'langue', 'date_inscription'
    ]
    
    search_fields = [
        'email', 'username', 'nom', 'prenom',
        'telephone'
    ]
    
    readonly_fields = [
        'date_inscription', 'date_derniere_connexion',
        'date_modification', 'session_token',
        'token_expiration', 'display_avatar_large',
        'display_stats'
    ]
    
    inlines = [AdresseFacturationInline, AdresseLivraisonInline]
    
    list_per_page = 50
    
    date_hierarchy = 'date_inscription'
    
    actions = [
        'activer_clients', 'desactiver_clients',
        'verifier_emails', 'activer_newsletter'
    ]
    
    fieldsets = (
        ('👤 Informations personnelles', {
            'fields': (
                'username', 'email', 'nom', 'prenom',
                'telephone', 'image', 'display_avatar_large'
            )
        }),
        ('🔐 Authentification', {
            'fields': (
                'password', 'session_token', 'token_expiration'
            )
        }),
        ('✅ Statuts', {
            'fields': (
                'is_active', 'is_verified', 'is_staff', 'is_superuser'
            )
        }),
        ('📧 Préférences', {
            'fields': (
                'newsletter', 'notifications_commande', 'langue'
            )
        }),
        ('📊 Statistiques', {
            'fields': ('display_stats',),
            'classes': ('collapse',)
        }),
        ('📅 Dates', {
            'fields': (
                'date_inscription', 'date_derniere_connexion',
                'date_modification'
            ),
            'classes': ('collapse',)
        }),
        ('🔑 Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('👤 Créer un client', {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'nom', 'prenom',
                'password1', 'password2', 'is_active'
            ),
        }),
    )
    
    # ===================================
    # AFFICHAGES PERSONNALISÉS
    # ===================================
    
    def display_avatar(self, obj: Client) -> str:
        """Affiche l'avatar miniature"""
        if obj.image:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="border-radius: 50%; object-fit: cover;" />',
                obj.image.url
            )
        initiales = obj.get_initiales()
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; '
            'background: #1976d2; color: white; display: flex; '
            'align-items: center; justify-content: center; font-weight: bold;">'
            '{}</div>',
            initiales
        )
    display_avatar.short_description = '👤'
    
    def display_avatar_large(self, obj: Client) -> str:
        """Affiche l'avatar en grande taille"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; border-radius: 10px;" />',
                obj.image.url
            )
        return '❌ Aucune photo'
    display_avatar_large.short_description = '🖼️ Photo de profil'
    
    def display_statut(self, obj: Client) -> str:
        """Affiche le statut du client"""
        if not obj.is_active:
            return format_html('<span style="color: red;">❌ Inactif</span>')
        if not obj.is_verified:
            return format_html('<span style="color: orange;">⚠️ Non vérifié</span>')
        if obj.is_staff:
            return format_html('<span style="color: blue;">👑 Staff</span>')
        return format_html('<span style="color: green;">✅ Actif</span>')
    display_statut.short_description = '📊 Statut'
    
    def display_commandes(self, obj: Client) -> str:
        """Affiche le nombre de commandes"""
        count = obj.nombre_commandes()
        if count == 0:
            return format_html('<span style="color: gray;">➖ Aucune</span>')
        if count < 5:
            return format_html('<span style="color: orange;">📦 {}</span>', count)
        return format_html('<span style="color: green;">🎯 {}</span>', count)
    display_commandes.short_description = '🛒 Commandes'
    
    def display_stats(self, obj: Client) -> str:
        """Affiche les statistiques du client"""
        nb_commandes = obj.nombre_commandes()
        nb_adresses_fact = obj.adresse_facturation.count()
        nb_adresses_livr = obj.adresse_livraison.count()
        
        return format_html(
            '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">'
            '<strong>📊 Statistiques :</strong><br><br>'
            '🛒 Commandes : <strong>{}</strong><br>'
            '📧 Adresses facturation : <strong>{}</strong><br>'
            '🚚 Adresses livraison : <strong>{}</strong><br>'
            '📅 Inscrit depuis : <strong>{} jours</strong><br>'
            '</div>',
            nb_commandes, nb_adresses_fact, nb_adresses_livr,
            (obj.date_inscription.date() - obj.date_inscription.date()).days
            if obj.date_inscription else 0
        )
    display_stats.short_description = '📊 Statistiques'
    
    # ===================================
    # ACTIONS ADMIN
    # ===================================
    
    @admin.action(description='✅ Activer les clients sélectionnés')
    def activer_clients(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.update(is_active=True)
        self.message_user(request, f'✅ {count} client(s) activé(s)')
    
    @admin.action(description='❌ Désactiver les clients sélectionnés')
    def desactiver_clients(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.update(is_active=False)
        self.message_user(request, f'❌ {count} client(s) désactivé(s)')
    
    @admin.action(description='✉️ Vérifier les emails')
    def verifier_emails(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.update(is_verified=True)
        self.message_user(request, f'✉️ {count} email(s) vérifié(s)')
    
    @admin.action(description='📧 Activer la newsletter')
    def activer_newsletter(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.update(newsletter=True)
        self.message_user(request, f'📧 {count} client(s) abonné(s)')


# ===================================
# ADMIN NAVIGATION LOG
# ===================================

@admin.register(NavigationLog)
class NavigationLogAdmin(admin.ModelAdmin):
    """Administration des logs de navigation"""
    
    list_display = [
        'display_client', 'path', 'produit',
        'device_type', 'ip_address', 'timestamp'
    ]
    
    list_filter = [
        'device_type', 'timestamp', 'produit__categorie'
    ]
    
    search_fields = [
        'client__email', 'path', 'ip_address',
        'produit__nom'
    ]
    
    readonly_fields = [
        'client', 'produit', 'path', 'user_agent',
        'referrer', 'ip_address', 'os_info',
        'device_type', 'timestamp', 'session_duration',
        'fingerprint'
    ]
    
    date_hierarchy = 'timestamp'
    
    list_per_page = 100
    
    def display_client(self, obj: NavigationLog) -> str:
        """Affiche le client"""
        if obj.client:
            return format_html(
                '<a href="/admin/clients/client/{}/change/">{}</a>',
                obj.client.pk, obj.client.email
            )
        return '👤 Anonyme'
    display_client.short_description = '👤 Client'
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        """Désactive l'ajout manuel"""
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Lecture seule"""
        return False
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
