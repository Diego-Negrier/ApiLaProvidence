# produits/admin.py

from django.contrib import admin,messages
from django.utils.html import format_html
from django.db.models import Count, Sum, Q, QuerySet, F
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from typing import Optional, List, Tuple, Any
from decimal import Decimal
from django.db.models import QuerySet

from .models import (
    Produit,
    ImageProduit,
    DescripteurProduit,
    LogoLabel,
    StatutProduit,
    Categorie,
    SousCategorie,
    SousSousCategorie
)


# ===================================
# INLINE ADMINS
# ===================================

class ImageProduitInline(admin.TabularInline):
    """Inline pour les images additionnelles"""
    model = ImageProduit
    extra = 1
    fields = ('image', 'image_preview', 'ordre', 'legende', 'est_principale')
    readonly_fields = ('image_preview',)
    ordering = ('ordre',)
    
    def image_preview(self, obj: ImageProduit) -> str:
        """Aperçu de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; '
                'object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return '-'
    
    image_preview.short_description = 'Aperçu'  # type: ignore


class DescripteurProduitInline(admin.TabularInline):
    """Inline pour les descripteurs relationnels"""
    model = DescripteurProduit
    extra = 0
    fields = ('cle', 'valeur', 'ordre')
    ordering = ('ordre', 'cle')


class LogoLabelInline(admin.TabularInline):
    """Inline pour les logos/labels"""
    model = LogoLabel
    extra = 0
    fields = ('nom', 'image', 'image_preview', 'description', 'ordre')
    readonly_fields = ('image_preview',)
    ordering = ('ordre',)
    
    def image_preview(self, obj: LogoLabel) -> str:
        """Aperçu du logo"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 60px; max-height: 60px; '
                'object-fit: contain;" />',
                obj.image.url
            )
        return '-'
    
    image_preview.short_description = 'Aperçu'  # type: ignore


# ===================================
# FILTERS
# ===================================

class CategorieFilter(admin.SimpleListFilter):
    """Filtre par catégorie"""
    title = 'Catégorie'
    parameter_name = 'categorie'
    
    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        categories = Categorie.objects.filter(est_active=True).order_by('nom')
        return [(cat.id, cat.nom) for cat in categories]
    
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(categorie_id=self.value())
        return queryset


class StockFilter(admin.SimpleListFilter):
    """Filtre par niveau de stock"""
    title = 'Niveau de stock'
    parameter_name = 'stock'
    
    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        return [
            ('rupture', '❌ En rupture'),
            ('faible', '⚠️ Stock faible'),
            ('normal', '✅ Stock normal'),
        ]
    
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() == 'rupture':
            return queryset.filter(stock_actuel=0)
        elif self.value() == 'faible':
            return queryset.filter(
                stock_actuel__gt=0,
                stock_actuel__lte=F('stock_minimum')
            )
        elif self.value() == 'normal':
            return queryset.filter(stock_actuel__gt=F('stock_minimum'))
        return queryset


class PrixFilter(admin.SimpleListFilter):
    """Filtre par plage de prix"""
    title = 'Plage de prix'
    parameter_name = 'prix'
    
    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        return [
            ('0-10', 'Moins de 10€'),
            ('10-50', '10€ - 50€'),
            ('50-100', '50€ - 100€'),
            ('100+', 'Plus de 100€'),
        ]
    
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() == '0-10':
            return queryset.filter(prix_ht__lt=10)
        elif self.value() == '10-50':
            return queryset.filter(prix_ht__gte=10, prix_ht__lt=50)
        elif self.value() == '50-100':
            return queryset.filter(prix_ht__gte=50, prix_ht__lt=100)
        elif self.value() == '100+':
            return queryset.filter(prix_ht__gte=100)
        return queryset


class PromotionFilter(admin.SimpleListFilter):
    """Filtre par promotion"""
    title = 'Promotion'
    parameter_name = 'promotion'
    
    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        return [
            ('oui', '🏷️ En promotion'),
            ('non', 'Sans promotion'),
        ]
    
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() == 'oui':
            return queryset.filter(en_promotion=True)
        elif self.value() == 'non':
            return queryset.filter(en_promotion=False)
        return queryset


# ===================================
# ADMIN CATÉGORIES
# ===================================

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    """Administration des catégories"""

    def get_queryset(self, request):
        """Optimisation avec préchargement des relations"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('souscategories', 'produits')

    list_display = (
        'icone_display',
        'nom',
        'nombre_souscategories_display',
        'nombre_produits_display',
        'ordre',
        'est_active'
    )
    list_filter = ('est_active',)
    search_fields = ('nom', 'description')
    list_editable = ('ordre', 'est_active')
    
    readonly_fields = (
        'date_creation',
        'date_modification',
        'nombre_souscategories_display',
        'nombre_produits_display',
        'image_preview'
    )
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom',  'description', 'icone', 'ordre', 'est_active')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Statistiques', {
            'fields': ('nombre_souscategories_display', 'nombre_produits_display'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='', ordering='nom')
    def icone_display(self, obj: Categorie) -> str:
        """Affichage de l'icône"""
        if obj.icone:
            return format_html(
                '<span style="font-size: 24px;">{}</span>',
                obj.icone
            )
        return '📁'
    
    @admin.display(description='Sous-catégories')
    def nombre_souscategories_display(self, obj: Categorie) -> str:
        """Nombre de sous-catégories"""
        count = obj.get_nombre_souscategories()
        return format_html(
            '<strong style="color: #17a2b8;">{}</strong>',
            count
        )
    
    @admin.display(description='Produits')
    def nombre_produits_display(self, obj: Categorie) -> str:
        """Nombre de produits"""
        count = obj.get_nombre_produits()
        return format_html(
            '<strong style="color: #28a745;">{}</strong>',
            count
        )
    
    @admin.display(description='Aperçu image')
    def image_preview(self, obj: Categorie) -> str:
        """Aperçu de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; '
                'object-fit: contain; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'


@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    """Administration des sous-catégories"""
    list_display = (
        'icone_display',
        'nom',
        'categorie',
        'nombre_sousssouscategories_display',
        'nombre_produits_display',
        'ordre',
        'est_active'
    )
    list_filter = ('categorie', 'est_active')
    search_fields = ('nom', 'description', 'categorie__nom')
    list_editable = ('ordre', 'est_active')
    
    readonly_fields = (
        
        'date_creation',
        'date_modification',
        'arborescence_display',
        'nombre_sousssouscategories_display',
        'nombre_produits_display',
        'image_preview'
    )
    
    fieldsets = (
        ('Hiérarchie', {
            'fields': ('categorie', 'arborescence_display')
        }),
        ('Informations principales', {
            'fields': ('nom',  'description', 'icone', 'ordre', 'est_active')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Descripteurs spécifiques', {
            'fields': ('descripteurs',),
            'classes': ('collapse',),
            'description': 'Descripteurs additionnels propres à cette sous-catégorie'
        }),
        ('Statistiques', {
            'fields': ('nombre_sousssouscategories_display', 'nombre_produits_display'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='', ordering='nom')
    def icone_display(self, obj: SousCategorie) -> str:
        """Affichage de l'icône"""
        if obj.icone:
            return format_html(
                '<span style="font-size: 20px;">{}</span>',
                obj.icone
            )
        return '📂'
    
    @admin.display(description='Arborescence')
    def arborescence_display(self, obj: SousCategorie) -> str:
        """Arborescence complète"""
        return format_html(
            '<span style="color: #666; font-size: 11px;">{}</span>',
            obj.get_arborescence()
        )
    
    @admin.display(description='Sous-sous-catégories')
    def nombre_sousssouscategories_display(self, obj: SousCategorie) -> str:
        """Nombre de sous-sous-catégories"""
        count = obj.get_nombre_sousssouscategories()
        return format_html(
            '<strong style="color: #17a2b8;">{}</strong>',
            count
        )
    
    @admin.display(description='Produits')
    def nombre_produits_display(self, obj: SousCategorie) -> str:
        """Nombre de produits"""
        count = obj.get_nombre_produits()
        return format_html(
            '<strong style="color: #28a745;">{}</strong>',
            count
        )
    
    @admin.display(description='Aperçu image')
    def image_preview(self, obj: SousCategorie) -> str:
        """Aperçu de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; '
                'object-fit: contain; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'


@admin.register(SousSousCategorie)
class SousSousCategorieAdmin(admin.ModelAdmin):
    """Administration des sous-sous-catégories"""
    list_display = (
        'icone_display',
        'nom',
        'souscategorie',
        'categorie_principale',
        'nombre_produits_display',
        'ordre',
        'est_active'
    )
    list_filter = ('souscategorie__categorie', 'souscategorie', 'est_active')
    search_fields = (
        'nom',
        'description',
        'souscategorie__nom',
        'souscategorie__categorie__nom'
    )
    list_editable = ('ordre', 'est_active')
    
    readonly_fields = (
        
        'date_creation',
        'date_modification',
        'arborescence_display',
        'nombre_produits_display',
        'image_preview'
    )
    
    fieldsets = (
        ('Hiérarchie', {
            'fields': ('souscategorie', 'arborescence_display')
        }),
        ('Informations principales', {
            'fields': ('nom',  'description', 'icone', 'ordre', 'est_active')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Descripteurs spécifiques', {
            'fields': ('descripteurs',),
            'classes': ('collapse',),
            'description': 'Descripteurs qui s\'ajoutent ou remplacent ceux des niveaux supérieurs'
        }),
        ('Statistiques', {
            'fields': ('nombre_produits_display',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='', ordering='nom')
    def icone_display(self, obj: SousSousCategorie) -> str:
        """Affichage de l'icône"""
        if obj.icone:
            return format_html(
                '<span style="font-size: 18px;">{}</span>',
                obj.icone
            )
        return '📄'
    
    @admin.display(description='Catégorie principale', ordering='souscategorie__categorie__nom')
    def categorie_principale(self, obj: SousSousCategorie) -> str:
        """Catégorie principale"""
        return obj.get_categorie().nom
    
    @admin.display(description='Arborescence')
    def arborescence_display(self, obj: SousSousCategorie) -> str:
        """Arborescence complète"""
        return format_html(
            '<span style="color: #666; font-size: 11px;">{}</span>',
            obj.get_arborescence()
        )
    
    @admin.display(description='Produits')
    def nombre_produits_display(self, obj: SousSousCategorie) -> str:
        """Nombre de produits"""
        count = obj.get_nombre_produits()
        return format_html(
            '<strong style="color: #28a745;">{}</strong>',
            count
        )
    
    @admin.display(description='Aperçu image')
    def image_preview(self, obj: SousSousCategorie) -> str:
        """Aperçu de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; '
                'object-fit: contain; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'


# ===================================
# ADMIN PRODUIT
# ===================================

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    """Administration des produits"""

    def get_queryset(self, request):
        """Optimisation des requêtes avec select_related et prefetch_related"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'fournisseur',
            'categorie',
            'souscategorie',
            'soussouscategorie'
        ).prefetch_related(
            'images',
            'descripteurs',
            'logos'
        )

    list_display = (
        'image_thumbnail',
        'nom',
        'numero_unique',
        'categorie_badge',
        'prix_display',
        'stock_display',
        'statut_badge',
        'badges_display',
        'est_actif'
    )

    list_filter = (
        CategorieFilter,
        'souscategorie',
        'statut',
        StockFilter,
        PrixFilter,
        PromotionFilter,
        'est_actif',
        'est_bio',
        'est_local',
        'est_nouveaute',
        'fournisseur',
    )

    search_fields = (
        'nom',
        'numero_unique',
        'code_barre',
        'reference_interne',
        'description_courte',
        'description_longue',
        'origine'
    )

    list_editable = ('est_actif',)

    readonly_fields = (
        'numero_unique',
        
        'date_creation',
        'date_modification',
        'image_principale_preview',
        'qr_code_preview',
        'prix_calcules_display',
        'stock_stats_display',
        'arborescence_display'
    )

    inlines = [
        ImageProduitInline,
        DescripteurProduitInline,
        LogoLabelInline
    ]

    fieldsets = (
        ('Identifiants', {
            'fields': (
                'numero_unique',
                'code_barre',
                'reference_interne',
            )
        }),
        ('Informations de base', {
            'fields': (
                'nom',
                'description_courte',
                'description_longue',
                'origine'
            )
        }),
        ('Categorisation', {
            'fields': (
                'categorie',
                'souscategorie',
                'soussouscategorie',
                'arborescence_display'
            )
        }),
        ('Images', {
            'fields': (
                'image_principale',
                'image_principale_preview',
                'qr_code',
                'qr_code_preview'
            )
        }),
        ('Prix et TVA', {
            'fields': (
                'prix_ht',
                'tva',
                'prix_calcules_display'
            )
        }),
        ('Promotion', {
            'fields': (
                'en_promotion',
                'pourcentage_promotion'
            ),
            'classes': ('collapse',)
        }),
        ('Stock', {
            'fields': (
                'stock_actuel',
                'stock_minimum',
                'stock_stats_display',
                'date_ajout_stock'
            )
        }),
        ('Statut et visibilite', {
            'fields': (
                'statut',
                'est_actif',
                'est_nouveaute',
                'est_bio',
                'est_local'
            )
        }),
        ('Poids et mesures', {
            'fields': (
                'poids',
                'unite_mesure'
            ),
            'classes': ('collapse',)
        }),
        ('Fournisseur', {
            'fields': ('fournisseur',),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description'
            ),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': (
                'date_creation',
                'date_modification',
            ),
            'classes': ('collapse',)
        })
    )

    actions = [
        'activer_produits',
        'desactiver_produits',
        'mettre_en_promotion',
        'retirer_promotion',
        'marquer_rupture',
        'regenerer_qr_codes'
    ]

    list_per_page = 25

    # ===================================
    # ACTIONS ADMIN
    # ===================================

    @admin.action(description='Activer les produits selectionnes')
    def activer_produits(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Active les produits sélectionnés"""
        updated = queryset.update(est_actif=True)
        self.message_user(
            request,
            f"{updated} produit(s) active(s) avec succes.",
            messages.SUCCESS
        )

    @admin.action(description='Desactiver les produits selectionnes')
    def desactiver_produits(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Désactive les produits sélectionnés"""
        updated = queryset.update(est_actif=False)
        self.message_user(
            request,
            f"{updated} produit(s) desactive(s) avec succes.",
            messages.WARNING
        )

    @admin.action(description='Mettre en promotion 10 pourcent')
    def mettre_en_promotion(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Met les produits en promotion à 10%"""
        count = 0
        for produit in queryset:
            if not produit.en_promotion:
                produit.en_promotion = True
                produit.pourcentage_promotion = Decimal('10.00')
                produit.save()
                count += 1
        
        self.message_user(
            request,
            f"{count} produit(s) mis en promotion a 10 pourcent.",
            messages.SUCCESS
        )

    @admin.action(description='Retirer la promotion')
    def retirer_promotion(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Retire la promotion des produits"""
        updated = queryset.update(
            en_promotion=False,
            pourcentage_promotion=Decimal('0.00')
        )
        self.message_user(
            request,
            f"{updated} produit(s) retire(s) de la promotion.",
            messages.INFO
        )

    @admin.action(description='Marquer en rupture de stock')
    def marquer_rupture(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Marque les produits en rupture de stock"""
        updated = queryset.update(stock_actuel=0)
        self.message_user(
            request,
            f"{updated} produit(s) marque(s) en rupture de stock.",
            messages.WARNING
        )

    @admin.action(description='Regenerer les QR codes')
    def regenerer_qr_codes(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Régénère les QR codes des produits"""
        count = 0
        for produit in queryset:
            produit.save()  # Le signal se charge de régénérer le QR code
            count += 1
        
        self.message_user(
            request,
            f"{count} QR code(s) regenere(s) avec succes.",
            messages.SUCCESS
        )

    # ===================================
    # AFFICHAGES PERSONNALISÉS
    # ===================================

    @admin.display(description='', ordering='nom')
    def image_thumbnail(self, obj: Produit) -> str:
        """Miniature de l'image avec fallback icône"""
        if obj.image_principale:
            try:
                # Vérifier que l'image existe physiquement
                if hasattr(obj.image_principale, 'path'):
                    import os
                    if not os.path.exists(obj.image_principale.path):
                        return format_html(
                            '<span style="font-size: 32px;" title="Image non trouvée">📦</span>'
                        )

                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; '
                    'object-fit: cover; border-radius: 8px;" '
                    'onerror="this.style.display=\'none\'; this.parentElement.innerHTML=\'<span style=\\\'font-size: 32px;\\\' title=\\\'Image corrompue\\\'>📦</span>\';"/>',
                    obj.image_principale.url
                )
            except (ValueError, AttributeError, OSError):
                return format_html('<span style="font-size: 32px;" title="Erreur image">📦</span>')
        return format_html('<span style="font-size: 32px;" title="Pas d\'image">📷</span>')

    @admin.display(description='Categorie')
    def categorie_badge(self, obj: Produit) -> str:
        """Badge de la catégorie"""
        if obj.soussouscategorie:
            cat = obj.soussouscategorie
            icone = cat.icone or '📄'
            nom = cat.nom
        elif obj.souscategorie:
            cat = obj.souscategorie
            icone = cat.icone or '📂'
            nom = cat.nom
        elif obj.categorie:
            cat = obj.categorie
            icone = cat.icone or '📁'
            nom = cat.nom
        else:
            return format_html(
                '<span style="color: #999;">Non categorise</span>'
            )

        return format_html(
            '<span style="background: #f0f0f0; padding: 4px 8px; '
            'border-radius: 12px; font-size: 12px;">'
            '{} {}'
            '</span>',
            icone,
            nom
        )

    @admin.display(description='Prix', ordering='prix_ht')
    def prix_display(self, obj: Produit) -> str:
        """Affichage du prix"""
        prix_ttc = obj.prix_ttc
        
        if obj.en_promotion and obj.prix_promo_ttc:
            return format_html(
                '<div style="text-align: right;">'
                '<span style="text-decoration: line-through; color: #999; font-size: 11px;">'
                '</span><br>'
                '<strong style="color: #28a745; font-size: 14px;">'
                '</strong>'
                '<span style="background: #ff4444; color: white; padding: 2px 4px; '
                'border-radius: 3px; font-size: 10px; margin-left: 4px;">'
                ''
                '</span>'
                '</div>',
                prix_ttc,
                obj.prix_promo_ttc,
                int(obj.pourcentage_promotion)
            )
        
        return format_html(
            '<strong style="font-size: 14px;">€</strong>',
            prix_ttc
        )

    @admin.display(description='Stock', ordering='stock_actuel')
    def stock_display(self, obj: Produit) -> str:
        """Affichage du stock avec indicateur coloré"""
        stock = obj.stock_actuel
        
        if stock == 0:
            color = '#dc3545'
            icon = '⚠️'
            text = 'RUPTURE'
        elif stock <= obj.stock_minimum:
            color = '#ffc107'
            icon = '⚡'
            text = f'{stock} unités'
        else:
            color = '#28a745'
            icon = '✓'
            text = f'{stock} unités'
        
        return format_html(
            '<div style="color: {}; font-weight: bold; text-align: center;">'
            '{} {}'
            '</div>',
            color, icon, text
        )

    @admin.display(description='Statut')
    def statut_badge(self, obj: Produit) -> str:
        """Badge de statut du produit"""
        if not obj.statut:
            return format_html(
                '<span style="background: #6c757d; color: white; padding: 4px 8px; '
                'border-radius: 12px; font-size: 11px;">Non défini</span>'
            )

        # Mapping des couleurs pour les statuts
        colors = {
            'disponible': '#28a745',
            'rupture_stock': '#dc3545',
            'en_commande': '#ffc107',
            'archive': '#6c757d',
            'indisponible': '#dc3545'
        }

        # obj.statut est la valeur du choix (ex: 'disponible')
        color = colors.get(obj.statut, '#6c757d')
        # get_statut_display() retourne le label lisible
        label = obj.get_statut_display() if hasattr(obj, 'get_statut_display') else obj.statut

        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, label
        )

    @admin.display(description='Labels')
    def badges_display(self, obj: Produit) -> str:
        """Affichage des badges spéciaux"""
        badges = []

        if obj.est_nouveaute:
            badges.append('🆕')
        if obj.est_bio:
            badges.append('🌱')
        if obj.est_local:
            badges.append('📍')
        if obj.en_promotion:
            badges.append('🏷️')

        if badges:
            return format_html(' '.join(badges))
        return format_html('<span style="color: #999;">-</span>')

    @admin.display(description='Aperçu image principale')
    def image_principale_preview(self, obj: Produit) -> str:
        """Aperçu grande taille de l'image principale"""
        if obj.image_principale:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; '
                'border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image_principale.url
            )
        return "Aucune image"

    @admin.display(description='QR Code')
    def qr_code_preview(self, obj: Produit) -> str:
        """Aperçu du QR code"""
        if obj.qr_code:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-width: 200px; border: 2px solid #ddd; '
                'border-radius: 4px; padding: 10px; background: white;" />'
                '<p style="margin-top: 8px; font-size: 12px; color: #666;">{}</p>'
                '</div>',
                obj.qr_code.url,
                obj.numero_unique
            )
        return "Pas de QR code"

    @admin.display(description='Prix calcules')
    def prix_calcules_display(self, obj: Produit) -> str:
        """Affichage détaillé des prix calculés"""
        # Protection pour les nouveaux objets
        if not obj.pk or obj.prix_ht is None:
            return format_html('<em style="color: #999;">Enregistrez pour voir les prix calculés</em>')
        
        try:
            html = f'''
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 4px;"><strong>Prix HT:</strong></td>
                    <td style="padding: 4px; text-align: right;">{obj.prix_ht:.2f}€</td>
                </tr>
                <tr>
                    <td style="padding: 4px;"><strong>TVA ({obj.tva}%):</strong></td>
                    <td style="padding: 4px; text-align: right;">{obj.montant_tva:.2f}€</td>
                </tr>
                <tr style="border-top: 2px solid #ddd;">
                    <td style="padding: 4px;"><strong>Prix TTC:</strong></td>
                    <td style="padding: 4px; text-align: right;"><strong>{obj.prix_ttc:.2f}€</strong></td>
                </tr>
            '''
            
            if obj.en_promotion and obj.prix_promo_ttc:
                html += f'''
                <tr style="border-top: 1px solid #eee; background: #f0fff0;">
                    <td style="padding: 4px;"><strong>Prix promo TTC:</strong></td>
                    <td style="padding: 4px; text-align: right; color: #28a745;">
                        <strong>{obj.prix_promo_ttc:.2f}€</strong>
                    </td>
                </tr>
                <tr style="background: #f0fff0;">
                    <td style="padding: 4px;"><strong>Economie:</strong></td>
                    <td style="padding: 4px; text-align: right; color: #28a745;">
                        <strong>-{obj.prix_ttc - obj.prix_promo_ttc:.2f}€</strong>
                    </td>
                </tr>
                '''
            
            html += '</table>'
            return format_html(html)
        except (AttributeError, TypeError):
            return format_html('<em style="color: #999;">Données incomplètes</em>')



    @admin.display(description='Statistiques stock')
    def stock_stats_display(self, obj: Produit) -> str:
        """Affichage des statistiques de stock"""
        # Protection pour les nouveaux objets
        if not obj.pk or obj.stock_actuel is None:
            return format_html('<em style="color: #999;">Enregistrez pour voir les statistiques</em>')
        
        try:
            stock_min = obj.stock_minimum if obj.stock_minimum else 1
            pourcentage = (obj.stock_actuel / max(stock_min, 1)) * 100
            
            if pourcentage == 0:
                color = '#dc3545'
                status = 'RUPTURE'
            elif pourcentage <= 100:
                color = '#ffc107'
                status = 'ALERTE'
            else:
                color = '#28a745'
                status = 'OK'
            
            return format_html(
                '<div style="padding: 10px; border: 2px solid {}; border-radius: 8px; '
                'background: {}22;">'
                '<div style="margin-bottom: 8px;"><strong>Status:</strong> '
                '<span style="color: {}; font-weight: bold;">{}</span></div>'
                '<div><strong>Stock actuel:</strong> {} unites</div>'
                '<div><strong>Stock minimum:</strong> {} unites</div>'
                '<div style="margin-top: 8px;">'
                '<div style="background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden;">'
                '<div style="background: {}; height: 100%; width: {}%;"></div>'
                '</div>'
                '</div>'
                '</div>',
                color, color, color, status,
                obj.stock_actuel,
                stock_min,
                color,
                min(pourcentage, 100)
            )
        except (AttributeError, TypeError, ZeroDivisionError):
            return format_html('<em style="color: #999;">Données incomplètes</em>')

    @admin.display(description='Arborescence')
    def arborescence_display(self, obj: Produit) -> str:
        """Affichage de l'arborescence complète"""
        if not obj.pk:
            return format_html('<em style="color: #999;">Enregistrez pour voir l\'arborescence</em>')
        
        parts = []
        
        if obj.categorie:
            parts.append(f'📁 {obj.categorie.nom}')
        if obj.souscategorie:
            parts.append(f'📂 {obj.souscategorie.nom}')
        if obj.soussouscategorie:
            parts.append(f'📄 {obj.soussouscategorie.nom}')
        
        if parts:
            return format_html(
                '<div style="font-size: 12px; line-height: 1.6;">{}</div>',
                '<br>'.join(parts)
            )
        return format_html('<span style="color: #999;">Non categorise</span>')


    @admin.display(description='Aperçu image principale')
    def image_principale_preview(self, obj: Produit) -> str:
        """Aperçu grande taille de l'image principale avec fallback"""
        if not obj.pk or not obj.image_principale:
            return format_html(
                '<div style="display: flex; align-items: center; justify-content: center; '
                'width: 300px; height: 300px; background: #f5f5f5; border-radius: 8px;">'
                '<span style="font-size: 120px;">📦</span>'
                '</div>'
            )

        try:
            # Vérifier que l'image existe physiquement
            if hasattr(obj.image_principale, 'path'):
                import os
                if not os.path.exists(obj.image_principale.path):
                    return format_html(
                        '<div style="display: flex; flex-direction: column; align-items: center; '
                        'justify-content: center; width: 300px; height: 300px; background: #fff3cd; '
                        'border-radius: 8px; border: 2px dashed #ffc107;">'
                        '<span style="font-size: 100px;">📦</span>'
                        '<p style="color: #856404; margin-top: 10px;">Image non trouvée</p>'
                        '<p style="color: #856404; font-size: 11px;">{}</p>'
                        '</div>',
                        obj.image_principale.name
                    )

            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; '
                'border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" '
                'onerror="this.style.display=\'none\'; this.parentElement.innerHTML=\'<div style=\\\'display: flex; flex-direction: column; align-items: center; justify-content: center; width: 300px; height: 300px; background: #f8d7da; border-radius: 8px; border: 2px dashed #dc3545;\\\'><span style=\\\'font-size: 100px;\\\'>📦</span><p style=\\\'color: #721c24; margin-top: 10px;\\\'>Image corrompue</p></div>\';"/>',
                obj.image_principale.url
            )
        except (ValueError, AttributeError, OSError) as e:
            return format_html(
                '<div style="display: flex; flex-direction: column; align-items: center; '
                'justify-content: center; width: 300px; height: 300px; background: #f8d7da; '
                'border-radius: 8px; border: 2px dashed #dc3545;">'
                '<span style="font-size: 100px;">📦</span>'
                '<p style="color: #721c24; margin-top: 10px;">Erreur</p>'
                '<p style="color: #721c24; font-size: 11px;">{}</p>'
                '</div>',
                str(e)
            )


    @admin.display(description='QR Code')
    def qr_code_preview(self, obj: Produit) -> str:
        """Aperçu du QR code"""
        if not obj.pk or not obj.qr_code:
            return format_html('<em style="color: #999;">Le QR code sera genere automatiquement</em>')
        
        return format_html(
            '<div style="text-align: center;">'
            '<img src="{}" style="max-width: 200px; border: 2px solid #ddd; '
            'border-radius: 4px; padding: 10px; background: white;" />'
            '<p style="margin-top: 8px; font-size: 12px; color: #666;">{}</p>'
            '</div>',
            obj.qr_code.url,
            obj.numero_unique
        )

# ===================================
# ADMIN DESCRIPTEUR PRODUIT
# ===================================

@admin.register(DescripteurProduit)
class DescripteurProduitAdmin(admin.ModelAdmin):
    """Administration des descripteurs"""
    list_display = (
        'produit',
        'type_descripteur_display',
        'valeur',
        'ordre'
    )
    search_fields = ('produit__nom', 'valeur')
    list_editable = ('ordre',)
    
    @admin.display(description='Clé', ordering='cle')
    def type_descripteur_display(self, obj: DescripteurProduit) -> str:
        """Affichage du type de descripteur"""
        return format_html(
            '<span style="background: #e9ecef; padding: 4px 8px; '
            'border-radius: 8px; font-size: 12px;">{}</span>',
            obj.cle
        )


# ===================================
# ADMIN IMAGE PRODUIT
# ===================================

@admin.register(ImageProduit)
class ImageProduitAdmin(admin.ModelAdmin):
    """Administration des images de produits"""
    list_display = (
        'image_thumbnail',
        'produit',
        'legende',
        'ordre',
        'est_principale',
    )
    search_fields = ('produit__nom', 'legende')
    list_editable = ('ordre', 'est_principale')

    readonly_fields = ('image_preview', 'date_ajout', 'date_modification')

    fieldsets = (
        ('Image', {
            'fields': ('produit', 'image', 'image_preview')
        }),
        ('Informations', {
            'fields': ('legende', 'ordre', 'est_principale')
        }),
        ('Dates', {
            'fields': ('date_ajout', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    @admin.display(description='Miniature')
    def image_thumbnail(self, obj: ImageProduit) -> str:
        """Miniature de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; '
                'object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return '📷'
    
    @admin.display(description='Aperçu')
    def image_preview(self, obj: ImageProduit) -> str:
        """Aperçu de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; '
                'object-fit: contain; border-radius: 12px;" />',
                obj.image.url
            )
        return '-'


# ===================================
# ADMIN LOGO LABEL
# ===================================

@admin.register(LogoLabel)
class LogoLabelAdmin(admin.ModelAdmin):
    """Administration des logos et labels"""
    list_display = (
        'logo_thumbnail',
        'produit',
        'nom',
        'type_label_display',
        'ordre',
    )
    search_fields = ('produit__nom', 'nom', 'description')
    
    readonly_fields = ('logo_preview',)
    
    fieldsets = (
        ('Logo', {
            'fields': ('produit', 'image', 'logo_preview')
        }),
        ('Informations', {
            'fields': ('nom', 'description', 'ordre')
        })
    )

    @admin.display(description='Logo')
    def logo_thumbnail(self, obj: LogoLabel) -> str:
        """Miniature du logo"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; '
                'object-fit: contain; border-radius: 4px; background: #f8f9fa; padding: 4px;" />',
                obj.image.url
            )
        return '🏷️'

    @admin.display(description='Type')
    def type_label_display(self, obj: LogoLabel) -> str:
        """Affichage du type de label"""
        return format_html(
            '<span style="background: #007bff; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            obj.nom
        )

    @admin.display(description='Aperçu')
    def logo_preview(self, obj: LogoLabel) -> str:
        """Aperçu du logo"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; '
                'object-fit: contain; border-radius: 8px; background: #f8f9fa; padding: 12px;" />',
                obj.image.url
            )
        return '-'
       
