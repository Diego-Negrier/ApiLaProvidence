from django.contrib import admin
from django.utils.html import format_html
from django.db.models import QuerySet, Count, Sum, Avg, Q
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from typing import Any, Optional
from decimal import Decimal

from .models import Fournisseur, PointLivraison, ZoneLivraison, Logo


# ===================================
# FILTRES PERSONNALISÉS
# ===================================

class ZoneLivraisonFilter(admin.SimpleListFilter):
    """Filtre par type de zone de livraison"""
    title = 'Zone de livraison'
    parameter_name = 'zone_type'

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[str, str]]:
        return [
            ('rayon', '📍 Rayon kilométrique'),
            ('departements', '🗺️ Départements'),
            ('villes', '🏙️ Villes'),
            ('national', '🌍 National'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> Optional[QuerySet]:
        if self.value():
            return queryset.filter(zone_livraison_type=self.value())
        return queryset


class TypeProductionFilter(admin.SimpleListFilter):
    """Filtre par type de production"""
    title = 'Type de production'
    parameter_name = 'type_prod'

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[str, str]]:
        # Récupère les valeurs uniques depuis la DB
        types = Fournisseur.objects.values_list('type_production', flat=True).distinct()
        return [(t, t) for t in types if t]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> Optional[QuerySet]:
        if self.value():
            return queryset.filter(type_production=self.value())
        return queryset


class ExperienceFilter(admin.SimpleListFilter):
    """Filtre par années d'expérience"""
    title = "Années d'expérience"
    parameter_name = 'experience'

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[str, str]]:
        return [
            ('debutant', '🆕 Débutant (0-2 ans)'),
            ('intermediaire', '📊 Intermédiaire (3-5 ans)'),
            ('experimente', '🏆 Expérimenté (6-10 ans)'),
            ('expert', '👑 Expert (>10 ans)'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> Optional[QuerySet]:
        if self.value() == 'debutant':
            return queryset.filter(experience_annees__lte=2)
        if self.value() == 'intermediaire':
            return queryset.filter(experience_annees__gte=3, experience_annees__lte=5)
        if self.value() == 'experimente':
            return queryset.filter(experience_annees__gte=6, experience_annees__lte=10)
        if self.value() == 'expert':
            return queryset.filter(experience_annees__gt=10)
        return queryset


class FraisLivraisonFilter(admin.SimpleListFilter):
    """Filtre par frais de livraison"""
    title = 'Frais de livraison'
    parameter_name = 'frais'

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[str, str]]:
        return [
            ('gratuit', '🎁 Gratuit (avec minimum)'),
            ('economique', '💰 Économique (< 5€)'),
            ('standard', '💵 Standard (5-15€)'),
            ('premium', '💎 Premium (> 15€)'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> Optional[QuerySet]:
        if self.value() == 'gratuit':
            return queryset.filter(livraison_gratuite_montant__isnull=False)
        if self.value() == 'economique':
            return queryset.filter(frais_livraison_base__lt=5)
        if self.value() == 'standard':
            return queryset.filter(frais_livraison_base__gte=5, frais_livraison_base__lte=15)
        if self.value() == 'premium':
            return queryset.filter(frais_livraison_base__gt=15)
        return queryset


# ===================================
# INLINES
# ===================================

class ZoneLivraisonInline(admin.TabularInline):
    """Inline pour les zones de livraison"""
    model = ZoneLivraison
    extra = 1
    fields = ['nom', 'frais_livraison', 'delai_livraison_jours', 'montant_minimum', 'actif']
    classes = ['collapse']


# ===================================
# ADMIN LOGO
# ===================================

@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    """Administration des logos/certifications"""
    
    list_display = ['display_logo', 'nom']
    search_fields = ['nom']
    
    def display_logo(self, obj: Logo) -> str:
        """Affiche le logo"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain;" />',
                obj.image.url
            )
        return '—'
    display_logo.short_description = 'Logo'


# ===================================
# ADMIN POINT LIVRAISON
# ===================================

@admin.register(PointLivraison)
class PointLivraisonAdmin(admin.ModelAdmin):
    """Administration des points de livraison"""
    
    list_display = [
        'display_nom', 'type_point', 'ville', 'code_postal',
        'display_coordonnees', 'display_jours', 'actif'
    ]
    
    list_filter = ['actif', 'type_point', 'ville']
    
    search_fields = ['nom', 'ville', 'code_postal', 'adresse']
    
    readonly_fields = ['display_carte', 'date_ajout', 'date_modification']
    
    list_editable = ['actif']
    
    fieldsets = (
        ('📍 Informations', {
            'fields': ('nom', 'type_point', 'adresse', 'code_postal', 'ville')
        }),
        ('🗺️ Coordonnées GPS', {
            'fields': ('latitude', 'longitude', 'display_carte'),
            'classes': ('collapse',)
        }),
        ('⏰ Disponibilité', {
            'fields': ('horaires', 'jours_disponibles', 'instructions')
        }),
        ('⚙️ Paramètres', {
            'fields': ('actif',)
        }),
        ('📅 Dates', {
            'fields': ('date_ajout', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def display_nom(self, obj: PointLivraison) -> str:
        """Affiche le nom avec icône"""
        icons = {
            'marche': '🏪',
            'depot': '📦',
            'magasin': '🏬',
            'autre': '📍'
        }
        icon = icons.get(obj.type_point, '📍')
        return format_html('<strong>{} {}</strong>', icon, obj.nom)
    display_nom.short_description = 'Point de livraison'
    
    def display_coordonnees(self, obj: PointLivraison) -> str:
        """Affiche les coordonnées GPS"""
        if obj.latitude and obj.longitude:
            return format_html(
                '<span title="{}, {}">🌍 GPS</span>',
                obj.latitude, obj.longitude
            )
        return format_html('<span style="color: #999;">❌ Non défini</span>')
    display_coordonnees.short_description = 'GPS'
    
    def display_jours(self, obj: PointLivraison) -> str:
        """Affiche les jours disponibles"""
        jours = obj.get_jours_list()
        if not jours:
            return '—'
        
        if len(jours) > 3:
            return format_html(
                '<span title="{}">📅 {} jours</span>',
                ', '.join(jours), len(jours)
            )
        return format_html('📅 {}', ', '.join(jours[:3]))
    display_jours.short_description = 'Jours'
    
    def display_carte(self, obj: PointLivraison) -> str:
        """Affiche une carte Google Maps"""
        if obj.latitude and obj.longitude:
            return format_html(
                '<iframe width="100%" height="300" frameborder="0" style="border:0" '
                'src="https://www.google.com/maps?q={},{}&output=embed&z=15"></iframe>',
                obj.latitude, obj.longitude
            )
        return '❌ Coordonnées GPS non définies'
    display_carte.short_description = '🗺️ Carte'


# ===================================
# ADMIN ZONE LIVRAISON
# ===================================

@admin.register(ZoneLivraison)
class ZoneLivraisonAdmin(admin.ModelAdmin):
    """Administration des zones de livraison"""
    
    list_display = [
        'display_fournisseur', 'nom', 'display_frais',
        'delai_livraison_jours', 'display_minimum', 'actif'
    ]
    
    list_filter = ['actif', 'fournisseur']
    
    search_fields = ['nom', 'fournisseur__nom', 'departements', 'villes']
    
    
    list_editable = ['actif']
    
    readonly_fields = ['display_couverture']
    
    fieldsets = (
        ('🏢 Fournisseur', {
            'fields': ('fournisseur', 'nom')
        }),
        ('🗺️ Couverture', {
            'fields': ('departements', 'villes', 'display_couverture')
        }),
        ('💰 Tarification', {
            'fields': ('frais_livraison', 'montant_minimum', 'delai_livraison_jours')
        }),
        ('⚙️ Paramètres', {
            'fields': ('actif',)
        }),
    )
    
    def display_fournisseur(self, obj: ZoneLivraison) -> str:
        """Affiche le fournisseur avec lien"""
        url = reverse('admin:fournisseur_fournisseur_change', args=[obj.fournisseur.pk])
        return format_html(
            '<a href="{}"><strong>{}</strong></a>',
            url, obj.fournisseur
        )
    display_fournisseur.short_description = 'Fournisseur'
    
    def display_frais(self, obj: ZoneLivraison) -> str:
        """Affiche les frais de livraison"""
        return format_html(
            '<strong style="color: #1976d2;">{} €</strong>',
            obj.frais_livraison
        )
    display_frais.short_description = '💰 Frais'
    
    def display_minimum(self, obj: ZoneLivraison) -> str:
        """Affiche le montant minimum"""
        if obj.montant_minimum > 0:
            return format_html('{} €', obj.montant_minimum)
        return format_html('<span style="color: #999;">—</span>')
    display_minimum.short_description = 'Minimum'
    
    def display_couverture(self, obj: ZoneLivraison) -> str:
        """Affiche la couverture géographique"""
        html = '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">'
        
        if obj.departements:
            depts = obj.get_departements_list()
            html += f'<strong>📍 Départements ({len(depts)}) :</strong><br>'
            html += ', '.join(depts) + '<br><br>'
        
        if obj.villes:
            villes = obj.get_villes_list()
            html += f'<strong>🏙️ Villes ({len(villes)}) :</strong><br>'
            html += ', '.join(villes)
        
        html += '</div>'
        return format_html(html)
    display_couverture.short_description = '🗺️ Couverture'


# ===================================
# ADMIN FOURNISSEUR (PRINCIPAL)
# ===================================

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    """Administration complète des fournisseurs"""
    
    list_display = [
        'display_photo', 'display_nom_complet', 'metier',
        'display_localisation', 'display_zone_livraison',
        'display_production', 'display_experience', 'display_certifications'
    ]
    
    list_filter = [
        ZoneLivraisonFilter, TypeProductionFilter, ExperienceFilter,
        FraisLivraisonFilter, 'saisonnalite_respectee', 'ville', 'pays'
    ]
    
    search_fields = [
        'nom', 'prenom', 'metier', 'ville', 'code_postal',
        'produits_principaux', 'certifications'
    ]
    
    readonly_fields = [
        'display_resume', 'display_carte_zone', 'display_stats_livraison',
        'display_calendrier', 'date_ajoutee', 'date_modifiee'
    ]
    
    
    filter_horizontal = ['points_livraison']
    
    date_hierarchy = 'date_ajoutee'
    
    list_per_page = 25
    
    inlines = [ZoneLivraisonInline]
    
    actions = [
        'exporter_fournisseurs',
        'activer_saisonnalite',
        'desactiver_saisonnalite'
    ]
    
    fieldsets = (
        ('👤 Informations personnelles', {
            'fields': (
                ('nom', 'prenom'),
                'metier',
                ('contact', 'tel'),
                'photo',
                'client'
            )
        }),
        ('📍 Adresse principale', {
            'fields': (
                'adresse',
                ('code_postal', 'ville'),
                'pays',
                ('latitude', 'longitude'),
                'display_carte_zone'
            )
        }),
        ('🚚 Zones de livraison', {
            'fields': (
                'zone_livraison_type',
                'rayon_livraison_km',
                'departements_livraison',
                'villes_livraison',
                'points_livraison',
                'display_stats_livraison'
            ),
            'classes': ('wide',)
        }),
        ('💰 Frais de livraison', {
            'fields': (
                ('frais_livraison_base', 'frais_livraison_par_km'),
                'livraison_gratuite_montant',
                ('jours_livraison', 'delai_livraison_jours')
            )
        }),
        ('🌱 Production', {
            'fields': (
                'description',
                'type_production',
                'experience_annees',
                'certifications'
            )
        }),
        ('🎯 Engagements', {
            'fields': (
                'engagement_ecologique',
                'conditions_travail',
                'objectifs_durables'
            ),
            'classes': ('collapse',)
        }),
        ('📦 Produits et saisonnalité', {
            'fields': (
                'produits_principaux',
                'calendrier_production',
                'saisonnalite_respectee',
                'display_calendrier'
            )
        }),
        ('💬 Relations et impact', {
            'fields': (
                'temoignages_clients',
                'impact_local'
            ),
            'classes': ('collapse',)
        }),
        ('📊 Résumé', {
            'fields': ('display_resume',),
            'classes': ('collapse',)
        }),
        ('📅 Dates', {
            'fields': ('date_ajoutee', 'date_modifiee'),
            'classes': ('collapse',)
        }),
    )
    
    # ===================================
    # AFFICHAGES PERSONNALISÉS
    # ===================================
    
    def display_photo(self, obj: Fournisseur) -> str:
        """Affiche la photo du fournisseur"""
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 50%; border: 2px solid #ddd;" />',
                obj.photo.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'border-radius: 50%; display: flex; align-items: center; justify-content: center; '
            'color: white; font-weight: bold; font-size: 18px;">{}</div>',
            obj.nom[0].upper() if obj.nom else '?'
        )
    display_photo.short_description = '📷'
    
    def display_nom_complet(self, obj: Fournisseur) -> str:
        """Affiche le nom complet avec lien"""
        url = reverse('admin:fournisseur_fournisseur_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="font-weight: bold; font-size: 13px;">{} {}</a><br>'
            '<small style="color: #666;">📞 {}</small>',
            url, obj.nom, obj.prenom, obj.tel
        )
    display_nom_complet.short_description = 'Fournisseur'
    
    def display_localisation(self, obj: Fournisseur) -> str:
        """Affiche la localisation"""
        return format_html(
            '<strong>📍 {}</strong><br><small style="color: #666;">{}</small>',
            obj.ville, obj.code_postal or '—'
        )
    display_localisation.short_description = 'Localisation'
    
    def display_zone_livraison(self, obj: Fournisseur) -> str:
        """Affiche la zone de livraison"""
        icons = {
            'rayon': '📍',
            'departements': '🗺️',
            'villes': '🏙️',
            'national': '🌍'
        }
        
        labels = {
            'rayon': f'{obj.rayon_livraison_km or "?"} km',
            'departements': f'{len(obj.get_departements_list())} dép.',
            'villes': f'{len(obj.get_villes_list())} villes',
            'national': 'France'
        }
        
        icon = icons.get(obj.zone_livraison_type, '📍')
        label = labels.get(obj.zone_livraison_type, '—')
        
        return format_html(
            '<span style="background: #e3f2fd; padding: 4px 8px; border-radius: 4px;">'
            '{} {}</span>',
            icon, label
        )
    display_zone_livraison.short_description = '🚚 Zone'
    
    def display_production(self, obj: Fournisseur) -> str:
        """Affiche le type de production"""
        if not obj.type_production:
            return '—'
        
        # Mapping des types avec icônes
        icons = {
            'permaculture': '🌱',
            'biologique': '🌿',
            'bio': '🌿',
            'raisonnee': '🌾',
            'raisonnée': '🌾',
            'conventionnel': '🌾',
            'autre': '📦'
        }
        
        type_lower = obj.type_production.lower()
        icon = '🌱'  # Icône par défaut
        
        for key, ico in icons.items():
            if key in type_lower:
                icon = ico
                break
        
        return format_html(
            '<span style="background: #e8f5e9; padding: 4px 8px; border-radius: 4px;">'
            '{} {}</span>',
            icon, obj.type_production
        )
    display_production.short_description = '🌱 Production'
    
    def display_experience(self, obj: Fournisseur) -> str:
        """Affiche l'expérience"""
        if not obj.experience_annees:
            return '—'
        
        if obj.experience_annees < 3:
            color = '#ff9800'
            icon = '🆕'
        elif obj.experience_annees < 6:
            color = '#2196f3'
            icon = '📊'
        elif obj.experience_annees < 10:
            color = '#4caf50'
            icon = '🏆'
        else:
            color = '#9c27b0'
            icon = '👑'
        
        return format_html(
            '<span style="color: {};">{} {} ans</span>',
            color, icon, obj.experience_annees
        )
    display_experience.short_description = '⏱️ Exp.'
    
    def display_certifications(self, obj: Fournisseur) -> str:
        """Affiche les certifications"""
        if not obj.certifications:
            return '—'
        
        certifs = [c.strip() for c in obj.certifications.split(',')]
        if len(certifs) > 2:
            return format_html(
                '<span title="{}">🏅 {} certif.</span>',
                ', '.join(certifs), len(certifs)
            )
        return format_html('🏅 {}', ', '.join(certifs[:2]))
    display_certifications.short_description = '🏅 Certif.'
    
    def display_carte_zone(self, obj: Fournisseur) -> str:
        """Affiche une carte de la zone de livraison"""
        if not (obj.latitude and obj.longitude):
            return '❌ Coordonnées GPS non définies'
        
        html = '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">'
        html += '<strong>🗺️ Zone de livraison :</strong><br><br>'
        
        # Carte Google Maps
        html += format_html(
            '<iframe width="100%" height="300" frameborder="0" style="border:0" '
            'src="https://www.google.com/maps?q={},{}&output=embed&z=12"></iframe>',
            obj.latitude, obj.longitude
        )
        
        html += '</div>'
        return format_html(html)
    display_carte_zone.short_description = '🗺️ Carte'
    
    def display_stats_livraison(self, obj: Fournisseur) -> str:
        """Affiche les statistiques de livraison"""
        html = '<div style="background: #e3f2fd; padding: 15px; border-radius: 5px;">'
        html += '<strong>📊 Statistiques livraison :</strong><br><br>'
        
        html += '<table style="width: 100%;">'
        html += f'<tr><td>💰 Frais de base :</td><td style="text-align: right;"><strong>{obj.frais_livraison_base} €</strong></td></tr>'
        
        if obj.frais_livraison_par_km > 0:
            html += f'<tr><td>🚗 Par km :</td><td style="text-align: right;">{obj.frais_livraison_par_km} €/km</td></tr>'
        
        if obj.livraison_gratuite_montant:
            html += f'<tr><td>🎁 Gratuit dès :</td><td style="text-align: right;"><strong>{obj.livraison_gratuite_montant} €</strong></td></tr>'
        
        html += f'<tr><td>📅 Délai :</td><td style="text-align: right;">{obj.delai_livraison_jours} jour(s)</td></tr>'
        
        if obj.jours_livraison:
            html += f'<tr><td>🗓️ Jours :</td><td style="text-align: right;">{obj.jours_livraison}</td></tr>'
        
        html += '</table></div>'
        return format_html(html)
    display_stats_livraison.short_description = '📊 Stats livraison'
    
    def display_calendrier(self, obj: Fournisseur) -> str:
        """Affiche le calendrier de production"""
        html = '<div style="background: #e8f5e9; padding: 15px; border-radius: 5px;">'
        html += '<strong>🗓️ Calendrier de production :</strong><br><br>'
        
        if obj.calendrier_production:
            html += f'<p>{obj.calendrier_production}</p>'
        else:
            html += '<p style="color: #999;">Non renseigné</p>'
        
        if obj.produits_principaux:
            html += '<br><strong>📦 Produits principaux :</strong><br>'
            produits = [p.strip() for p in obj.produits_principaux.split(',')]
            html += '<ul style="margin: 5px 0; padding-left: 20px;">'
            for produit in produits[:5]:
                html += f'<li>{produit}</li>'
            html += '</ul>'
        
        if obj.saisonnalite_respectee:
            html += '<br><span style="color: #4caf50; font-weight: bold;">✅ Saisonnalité respectée</span>'
        else:
            html += '<br><span style="color: #f44336;">❌ Saisonnalité non respectée</span>'
        
        html += '</div>'
        return format_html(html)
    display_calendrier.short_description = '🗓️ Calendrier'
    
    def display_resume(self, obj: Fournisseur) -> str:
        """Affiche un résumé complet"""
        html = '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">'
        html += f'<h2 style="margin: 0 0 15px 0;">{obj.nom} {obj.prenom}</h2>'
        html += f'<p style="font-size: 16px; margin: 0 0 20px 0;">{obj.metier}</p>'
        
        html += '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">'
        
        # Colonne 1
        html += '<div>'
        html += f'<div style="margin-bottom: 10px;">📍 <strong>{obj.ville}</strong></div>'
        
        if obj.type_production:
            html += f'<div style="margin-bottom: 10px;">🌱 <strong>{obj.type_production}</strong></div>'
        
        if obj.experience_annees:
            html += f'<div style="margin-bottom: 10px;">⏱️ <strong>{obj.experience_annees} ans d\'exp.</strong></div>'
        html += '</div>'
        
        # Colonne 2
        html += '<div>'
        
        # Labels pour zone_livraison_type
        zone_labels = {
            'rayon': 'Rayon kilométrique',
            'departements': 'Départements',
            'villes': 'Villes',
            'national': 'National'
        }
        zone_label = zone_labels.get(obj.zone_livraison_type, obj.zone_livraison_type)
        html += f'<div style="margin-bottom: 10px;">🚚 <strong>{zone_label}</strong></div>'
        
        html += f'<div style="margin-bottom: 10px;">💰 <strong>{obj.frais_livraison_base} € (base)</strong></div>'
        
        if obj.livraison_gratuite_montant:
            html += f'<div style="margin-bottom: 10px;">🎁 <strong>Gratuit dès {obj.livraison_gratuite_montant} €</strong></div>'
        html += '</div>'
        
        html += '</div></div>'
        return format_html(html)
    display_resume.short_description = '📋 Résumé'
    
    # ===================================
    # ACTIONS ADMIN
    # ===================================
    
    @admin.action(description='📥 Exporter les fournisseurs')
    def exporter_fournisseurs(self, request: HttpRequest, queryset: QuerySet) -> None:
        # TODO: Implémenter l'export CSV/Excel
        self.message_user(request, f'📥 Export de {queryset.count()} fournisseur(s) (à implémenter)')
    
    @admin.action(description='✅ Activer saisonnalité')
    def activer_saisonnalite(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.update(saisonnalite_respectee=True)
        self.message_user(request, f'✅ Saisonnalité activée pour {count} fournisseur(s)')
    
    @admin.action(description='❌ Désactiver saisonnalité')
    def desactiver_saisonnalite(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.update(saisonnalite_respectee=False)
        self.message_user(request, f'❌ Saisonnalité désactivée pour {count} fournisseur(s)')
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('client').prefetch_related('points_livraison')
