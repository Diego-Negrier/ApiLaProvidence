from django.contrib import admin
<<<<<<< HEAD
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

=======
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import QuerySet, Sum, F
from django.http import HttpRequest
from typing import Any, Optional
from decimal import Decimal

from .models import Panier, LignePanier

# ===================================
# ADMIN PANIER
# ===================================

class LignePanierInline(admin.TabularInline):
    """Inline pour afficher les articles du panier"""
    model = LignePanier
    extra = 0
    readonly_fields = ['produit', 'quantite', 'display_sous_total', 'date_ajoutee', 'statut']
    can_delete = True

    fields = ['produit', 'quantite', 'statut', 'display_sous_total', 'date_ajoutee']

    def display_sous_total(self, obj):
        """Affiche le sous-total de la ligne"""
        if obj.pk:
            return format_html('<strong>{} €</strong>', f'{float(obj.sous_total):.2f}')
        return '—'
    display_sous_total.short_description = 'Sous-total'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    """Administration des paniers"""

    list_display = [
        'id', 'display_client', 'display_statut', 'display_nb_articles',
        'display_total', 'date_creation', 'date_modification'
    ]

    list_filter = ['statut', 'date_creation', 'date_modification']

    search_fields = ['client__username', 'client__email', 'client__nom', 'client__prenom']

    readonly_fields = [
        'date_creation', 'date_modification',
        'display_details', 'display_resume'
    ]

    inlines = [LignePanierInline]

    date_hierarchy = 'date_creation'

    list_per_page = 25

    actions = ['vider_paniers', 'marquer_termine', 'archiver_paniers']

    fieldsets = (
        ('👤 Client', {
            'fields': ('client',)
        }),
        ('📊 Statut', {
            'fields': ('statut',)
        }),
        ('📈 Résumé', {
            'fields': ('display_resume',)
        }),
        ('📋 Détails', {
            'fields': ('display_details',),
            'classes': ('collapse',)
        }),
        ('📅 Dates', {
            'fields': ('date_creation', 'date_modification')
        }),
    )

    def display_client(self, obj):
        """Affiche le client"""
        return format_html(
            '<strong>👤 {}</strong><br><small>{}</small>',
            obj.client.username,
            obj.client.email
        )
    display_client.short_description = 'Client'

    def display_statut(self, obj):
        """Affiche le statut avec couleur"""
        couleurs = {
            'actif': '#4caf50',
            'termine': '#2196f3',
            'archive': '#9e9e9e'
        }
        icones = {
            'actif': '🛒',
            'termine': '✅',
            'archive': '📦'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            couleurs.get(obj.statut, '#000'),
            icones.get(obj.statut, ''),
            obj.get_statut_display()
        )
    display_statut.short_description = 'Statut'

    def display_nb_articles(self, obj):
        """Affiche le nombre d'articles"""
        nb = obj.nombre_articles()
        if nb == 0:
            return format_html('<span style="color: #999;">0</span>')
        return format_html(
            '<strong style="color: #2196f3;">📦 {}</strong>',
            nb
        )
    display_nb_articles.short_description = 'Articles'

    def display_total(self, obj):
        """Affiche le total du panier"""
        total = obj.calculer_total()
        if total == 0:
            return format_html('<span style="color: #999;">0 €</span>')
        return format_html(
            '<strong style="color: #4caf50; font-size: 14px;">💰 {} €</strong>',
            f'{float(total):.2f}'
        )
    display_total.short_description = 'Total HT'

    def display_resume(self, obj):
        """Affiche un résumé du panier"""
        total_ht = obj.calculer_total()
        total_ttc = obj.calculer_total_ttc()
        poids = obj.calculer_poids_total()
        
        html = '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">'
        html += '<h3 style="margin: 0 0 15px 0;">🛒 Résumé du panier</h3>'
        html += '<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">'

        # Nombre d'articles
        html += '<div style="text-align: center;">'
        html += f'<div style="font-size: 32px; font-weight: bold;">{obj.nombre_articles()}</div>'
        html += '<div style="opacity: 0.9;">📦 Articles</div>'
        html += '</div>'

        # Total HT
        html += '<div style="text-align: center;">'
        html += f'<div style="font-size: 32px; font-weight: bold;">{float(total_ht):.2f} €</div>'
        html += '<div style="opacity: 0.9;">💰 Total HT</div>'
        html += '</div>'

        # Total TTC
        html += '<div style="text-align: center;">'
        html += f'<div style="font-size: 32px; font-weight: bold;">{float(total_ttc):.2f} €</div>'
        html += '<div style="opacity: 0.9;">💵 Total TTC</div>'
        html += '</div>'

        # Poids
        html += '<div style="text-align: center;">'
        html += f'<div style="font-size: 32px; font-weight: bold;">{float(poids):.2f}</div>'
        html += '<div style="opacity: 0.9;">⚖️ Kg</div>'
        html += '</div>'

        html += '</div></div>'
        return mark_safe(html)
    display_resume.short_description = 'Résumé'

    def display_details(self, obj):
        """Affiche les détails complets des articles"""
        lignes = LignePanier.objects.filter(panier=obj).select_related('produit')

        if not lignes.exists():
            return format_html('<p style="color: #999;">🛒 Panier vide</p>')

        html = '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead><tr style="background: #ddd;">'
        html += '<th style="padding: 10px; text-align: left;">Produit</th>'
        html += '<th style="padding: 10px; text-align: center;">Qté</th>'
        html += '<th style="padding: 10px; text-align: center;">Statut</th>'
        html += '<th style="padding: 10px; text-align: right;">Prix unit.</th>'
        html += '<th style="padding: 10px; text-align: right;">Sous-total</th>'
        html += '</tr></thead><tbody>'

        for ligne in lignes:
            statut_color = {
                'en_attente': '#ff9800',
                'en_preparation': '#2196f3',
                'pret': '#4caf50',
                'livre': '#9c27b0'
            }.get(ligne.statut, '#999')

            html += '<tr style="border-bottom: 1px solid #ddd;">'
            html += f'<td style="padding: 10px;"><strong>{ligne.produit.nom}</strong></td>'
            html += f'<td style="padding: 10px; text-align: center;">{ligne.quantite}</td>'
            html += f'<td style="padding: 10px; text-align: center;"><span style="color: {statut_color}; font-weight: bold;">{ligne.get_statut_display()}</span></td>'
            html += f'<td style="padding: 10px; text-align: right;">{float(ligne.produit.prix_ht):.2f} €</td>'
            html += f'<td style="padding: 10px; text-align: right;"><strong>{float(ligne.sous_total):.2f} €</strong></td>'
            html += '</tr>'

        html += '</tbody><tfoot><tr style="background: #e8f5e9;">'
        html += '<td colspan="4" style="padding: 10px; text-align: right;"><strong>TOTAL HT :</strong></td>'
        html += f'<td style="padding: 10px; text-align: right;"><strong style="font-size: 16px; color: #4caf50;">{float(obj.calculer_total()):.2f} €</strong></td>'
        html += '</tr></tfoot></table></div>'

        return mark_safe(html)
    display_details.short_description = 'Détails des articles'

    @admin.action(description='🗑️ Vider les paniers sélectionnés')
    def vider_paniers(self, request, queryset):
        """Vide les paniers sélectionnés"""
        total_items = 0
        for panier in queryset:
            total_items += panier.nombre_articles()
            panier.vider_panier()

        self.message_user(
            request,
            f'🗑️ {queryset.count()} panier(s) vidé(s) ({total_items} articles supprimés)'
        )

    @admin.action(description='✅ Marquer comme terminé')
    def marquer_termine(self, request, queryset):
        """Marque les paniers comme terminés"""
        count = 0
        for panier in queryset:
            panier.marquer_comme_termine()
            count += 1

        self.message_user(
            request,
            f'✅ {count} panier(s) marqué(s) comme terminé(s)'
        )

    @admin.action(description='📦 Archiver les paniers')
    def archiver_paniers(self, request, queryset):
        """Archive les paniers sélectionnés"""
        count = 0
        for panier in queryset:
            panier.archiver()
            count += 1

        self.message_user(
            request,
            f'📦 {count} panier(s) archivé(s)'
        )

    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related(
            'client'
        ).prefetch_related('lignes__produit')


@admin.register(LignePanier)
class LignePanierAdmin(admin.ModelAdmin):
    """Administration des lignes de panier"""

    list_display = [
        'display_produit', 'display_panier', 'quantite',
        'display_statut', 'display_sous_total', 'date_ajoutee'
    ]

    list_filter = ['statut', 'date_ajoutee']

    search_fields = ['produit__nom', 'panier__client__username']

    readonly_fields = ['date_ajoutee', 'display_sous_total', 'display_sous_total_ttc']

    date_hierarchy = 'date_ajoutee'

    fieldsets = (
        ('📦 Produit', {
            'fields': ('panier', 'produit', 'quantite')
        }),
        ('📊 Statut', {
            'fields': ('statut',)
        }),
        ('💰 Montants', {
            'fields': ('display_sous_total', 'display_sous_total_ttc')
        }),
        ('📅 Date', {
            'fields': ('date_ajoutee',)
        }),
    )

    def display_produit(self, obj):
        """Affiche le produit avec image"""
        if obj.produit.image:
            return format_html(
                '<img src="{}" width="40" style="border-radius: 5px; margin-right: 10px; vertical-align: middle;">'
                '<strong>{}</strong>',
                obj.produit.image.url,
                obj.produit.nom
            )
        return format_html('<strong>📦 {}</strong>', obj.produit.nom)
    display_produit.short_description = 'Produit'

    def display_panier(self, obj):
        """Affiche le panier"""
        return format_html(
            '🛒 Panier #{} - {}',
            obj.panier.id,
            obj.panier.client.username
        )
    display_panier.short_description = 'Panier'

    def display_statut(self, obj):
        """Affiche le statut avec couleur"""
        couleurs = {
            'en_attente': '#ff9800',
            'en_preparation': '#2196f3',
            'pret': '#4caf50',
            'livre': '#9c27b0'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            couleurs.get(obj.statut, '#999'),
            obj.get_statut_display()
        )
    display_statut.short_description = 'Statut'

    def display_sous_total(self, obj):
        """Affiche le sous-total HT"""
        return format_html('<strong>{} €</strong>', f'{float(obj.sous_total):.2f}')
    display_sous_total.short_description = 'Sous-total HT'

    def display_sous_total_ttc(self, obj):
        """Affiche le sous-total TTC"""
        return format_html('<strong>{} €</strong>', f'{float(obj.sous_total_ttc()):.2f}')
    display_sous_total_ttc.short_description = 'Sous-total TTC'

    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related(
            'panier__client', 'produit'
        )
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
