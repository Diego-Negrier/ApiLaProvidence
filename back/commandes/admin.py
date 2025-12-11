<<<<<<< HEAD
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
=======
# commandes/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Commande, 
    HistoriqueCommande, 
    HistoriqueLignePanier,
    StatutCommande
)


# ===================================
# INLINES
# ===================================

class HistoriqueLignePanierInline(admin.TabularInline):
    """Affiche les lignes d'historique dans l'admin HistoriqueCommande"""
    model = HistoriqueLignePanier
    extra = 0
    can_delete = False
    
    readonly_fields = [
        'produit', 'nom_produit', 'reference_produit',
        'quantite', 'prix_unitaire', 'poids', 'statut',
        'sous_total_display', 'date_archivage'
    ]
    
    fields = [
        'nom_produit', 'reference_produit', 'quantite',
        'prix_unitaire', 'sous_total_display', 'poids', 'statut'
    ]

    def sous_total_display(self, obj):
        return format_html("{:.2f} €", obj.sous_total)
    sous_total_display.short_description = "Sous-total"

    def has_add_permission(self, request, obj=None):
        return False


# ===================================
# ADMIN COMMANDE
# ===================================

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        'numero_commande',
        'client_nom',
        'statut_badge',
        'avancement_bar',
        'total_format',
        'nombre_produits_display',
        'date_commande'
    ]
    
    list_filter = [
        'statut',
        'date_commande',
        'livreur',
        'point_relais'
    ]
    
    search_fields = [
        'numero_commande',
        'client__username',
        'client__email',
        'client__telephone'
    ]
    
    readonly_fields = [
        'numero_commande',
        'date_commande',
        'date_modification',
        'avancement',
        'total',
        'nombre_produits_display',
        'lien_panier'
    ]
    
    fieldsets = (
        ('📋 Informations générales', {
            'fields': (
                'numero_commande',
                'client',
                'statut',
                'avancement'
            )
        }),
        ('🚚 Livraison', {
            'fields': ('livreur', 'point_relais'),
            'classes': ('collapse',)
        }),
        ('🛒 Panier', {
            'fields': ('panier', 'lien_panier'),
            'classes': ('collapse',)
        }),
        ('💰 Financier', {
            'fields': ('total', 'nombre_produits_display')
        }),
        ('📅 Dates', {
            'fields': ('date_commande', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['terminer_commandes', 'annuler_commandes', 'recalculer_totaux']
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related(
            'client', 'livreur', 'panier', 'point_relais'
        )
    
    # ===================================
    # MÉTHODES D'AFFICHAGE
    # ===================================
    
    def client_nom(self, obj):
        if obj.client:
            return obj.client.username
        return "Client supprimé"
    client_nom.short_description = "Client"
    client_nom.admin_order_field = "client__username"
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ffc107',
            'en_cours': '#17a2b8',
            'en_livraison': '#007bff',
            'terminee': '#28a745',
            'annulee': '#dc3545'
        }
        color = colors.get(obj.statut, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:5px 10px; '
            'border-radius:3px; font-weight:bold;">{}</span>',
            color,
            obj.get_statut_display()
        )
    statut_badge.short_description = "Statut"
    statut_badge.admin_order_field = "statut"
    
    def avancement_bar(self, obj):
        avancement = obj.avancement if obj.avancement is not None else 0
        color = '#28a745' if avancement == 100 else '#007bff'
        return format_html(
            '<div style="width:100px; background:#e9ecef; border-radius:3px;">'
            '<div style="width:{}%; background:{}; color:white; text-align:center; '
            'padding:2px; border-radius:3px; font-size:11px;">{}%</div></div>',
            avancement,
            color,
            int(avancement)
        )
    avancement_bar.short_description = "Avancement"
    avancement_bar.admin_order_field = "avancement"
    
    def total_format(self, obj):
        return format_html("{} €", obj.total)
    total_format.short_description = "Total HT"
    total_format.admin_order_field = "total"
    
    def nombre_produits_display(self, obj):
        return obj.nombre_produits
    nombre_produits_display.short_description = "Nb produits"
    
    def lien_panier(self, obj):
        if obj.panier:
            url = reverse('admin:paniers_panier_change', args=[obj.panier.pk])
            return format_html(
                '<a href="{}" target="_blank">📦 Voir le panier</a>',
                url
            )
        return "Aucun panier"
    lien_panier.short_description = "Panier"
    
    # ===================================
    # ACTIONS PERSONNALISÉES
    # ===================================
    
    @admin.action(description="✅ Terminer les commandes sélectionnées")
    def terminer_commandes(self, request, queryset):
        count = 0
        errors = []
        
        for commande in queryset:
            try:
                commande.marquer_comme_terminee()
                count += 1
            except Exception as e:
                errors.append(f"{commande.numero_commande}: {str(e)}")
        
        if count:
            self.message_user(request, f"{count} commande(s) terminée(s)")
        
        if errors:
            self.message_user(
                request, 
                "Erreurs: " + ", ".join(errors),
                level='error'
            )
    
    @admin.action(description="❌ Annuler les commandes sélectionnées")
    def annuler_commandes(self, request, queryset):
        count = 0
        errors = []
        
        for commande in queryset:
            try:
                commande.annuler_commande()
                count += 1
            except Exception as e:
                errors.append(f"{commande.numero_commande}: {str(e)}")
        
        if count:
            self.message_user(request, f"{count} commande(s) annulée(s)")
        
        if errors:
            self.message_user(
                request,
                "Erreurs: " + ", ".join(errors),
                level='error'
            )
    
    @admin.action(description="🔄 Recalculer les totaux")
    def recalculer_totaux(self, request, queryset):
        count = 0
        for commande in queryset:
            commande.calculer_total()
            count += 1
        
        self.message_user(request, f"{count} total(aux) recalculé(s)")


# ===================================
# ADMIN HISTORIQUE COMMANDE
# ===================================

@admin.register(HistoriqueCommande)
class HistoriqueCommandeAdmin(admin.ModelAdmin):
    list_display = [
        'numero_commande',
        'client_nom',
        'statut_badge',
        'action_badge',
        'total_format',
        'nombre_produits_display',
        'date_commande',
        'date_archivage'
    ]
    
    list_filter = [
        'statut_final',
        'action',
        'date_archivage',
        'date_commande'
    ]
    
    search_fields = [
        'numero_commande',
        'client_nom',
        'client_email'
    ]
    
    readonly_fields = [
        'commande', 'client', 'client_nom', 'client_email',
        'client_telephone', 'livreur', 'livreur_nom',
        'point_relais', 'point_relais_nom', 'numero_commande',
        'date_commande', 'date_archivage', 'statut_final',
        'action', 'total', 'id_panier', 'nombre_lignes',
        'nombre_produits_display', 'poids_total_display'
    ]
    
    fieldsets = (
        ('📋 Informations commande', {
            'fields': (
                'numero_commande',
                'statut_final',
                'action',
                'date_commande',
                'date_archivage'
            )
        }),
        ('👤 Client', {
            'fields': (
                'client',
                'client_nom',
                'client_email',
                'client_telephone'
            ),
            'classes': ('collapse',)
        }),
        ('🚚 Livraison', {
            'fields': (
                'livreur',
                'livreur_nom',
                'point_relais',
                'point_relais_nom'
            ),
            'classes': ('collapse',)
        }),
        ('💰 Résumé', {
            'fields': (
                'total',
                'nombre_lignes',
                'nombre_produits_display',
                'poids_total_display',
                'id_panier'
            )
        })
    )
    
    inlines = [HistoriqueLignePanierInline]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    # ===================================
    # MÉTHODES D'AFFICHAGE
    # ===================================
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ffc107',
            'en_cours': '#17a2b8',
            'en_livraison': '#007bff',
            'terminee': '#28a745',
            'annulee': '#dc3545'
        }
        color = colors.get(obj.statut_final, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:5px 10px; '
            'border-radius:3px; font-weight:bold;">{}</span>',
            color,
            obj.get_statut_final_display()
        )
    statut_badge.short_description = "Statut"
    
    def action_badge(self, obj):
        colors = {
            'terminer': '#28a745',
            'annuler': '#dc3545',
            'reouvrir': '#17a2b8'
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:3px; font-size:11px;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = "Action"
    
    def total_format(self, obj):
        return format_html("{:.2f} €", obj.total)
    total_format.short_description = "Total"
    total_format.admin_order_field = "total"
    
    def nombre_produits_display(self, obj):
        return obj.nombre_produits
    nombre_produits_display.short_description = "Nb produits"
    
    def poids_total_display(self, obj):
        return format_html("{:.3f} kg", obj.poids_total)
    poids_total_display.short_description = "Poids total"


# ===================================
# ADMIN HISTORIQUE LIGNE PANIER
# ===================================

@admin.register(HistoriqueLignePanier)
class HistoriqueLignePanierAdmin(admin.ModelAdmin):
    list_display = [
        'nom_produit',
        'reference_produit',
        'historique_numero',
        'quantite',
        'prix_unitaire_format',
        'sous_total_format',
        'statut',
        'date_archivage'
    ]
    
    list_filter = [
        'statut',
        'date_archivage'
    ]
    
    search_fields = [
        'nom_produit',
        'reference_produit',
        'historique_commande__numero_commande'
    ]
    
    readonly_fields = [
        'historique_commande', 'produit', 'nom_produit',
        'reference_produit', 'quantite', 'prix_unitaire',
        'poids', 'statut', 'date_archivage',
        'sous_total_display', 'poids_total_display'
    ]
    
    fieldsets = (
        ('📦 Produit', {
            'fields': (
                'produit',
                'nom_produit',
                'reference_produit'
            )
        }),
        ('📊 Quantités & Prix', {
            'fields': (
                'quantite',
                'prix_unitaire',
                'sous_total_display',
                'poids',
                'poids_total_display'
            )
        }),
        ('📋 Informations', {
            'fields': (
                'historique_commande',
                'statut',
                'date_archivage'
            )
        })
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # ===================================
    # MÉTHODES D'AFFICHAGE
    # ===================================
    
    def historique_numero(self, obj):
        return obj.historique_commande.numero_commande
    historique_numero.short_description = "N° Commande"
    historique_numero.admin_order_field = "historique_commande__numero_commande"
    
    def prix_unitaire_format(self, obj):
        return format_html("{:.2f} €", obj.prix_unitaire)
    prix_unitaire_format.short_description = "Prix unitaire"
    prix_unitaire_format.admin_order_field = "prix_unitaire"

    def sous_total_format(self, obj):
        return format_html("{:.2f} €", obj.sous_total)
    sous_total_format.short_description = "Sous-total"

    def sous_total_display(self, obj):
        return format_html("{:.2f} €", obj.sous_total)
    sous_total_display.short_description = "Sous-total"

    def poids_total_display(self, obj):
        return format_html("{:.3f} kg", obj.poids_total)
    poids_total_display.short_description = "Poids total"
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
