<<<<<<< HEAD
from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Tarif)

admin.site.register(PointRelais)

admin.site.register(Livreur)
=======
# livraison/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg, Q
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.contrib import messages
from typing import Any, Optional
from decimal import Decimal
import csv

from .models import Livreur, Tarif, PointRelais

# ===================================
# FILTRES PERSONNALISÉS
# ===================================

class TypeServiceFilter(admin.SimpleListFilter):
    """Filtre pour le type de service"""
    title = 'Type de service'
    parameter_name = 'type_service'

    def lookups(self, request, model_admin):
        return [
            ('standard', '📦 Standard'),
            ('express', '⚡ Express'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type_service=self.value())
        return queryset


class PoidsFilter(admin.SimpleListFilter):
    """Filtre pour les tranches de poids"""
    title = 'Tranche de poids'
    parameter_name = 'tranche_poids'

    def lookups(self, request, model_admin):
        return [
            ('leger', '📦 Léger (0-2kg)'),
            ('moyen', '📦 Moyen (2-10kg)'),
            ('lourd', '📦 Lourd (10-30kg)'),
            ('tres_lourd', '📦 Très lourd (>30kg)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'leger':
            return queryset.filter(poids_max__lte=2)
        if self.value() == 'moyen':
            return queryset.filter(poids_min__gte=2, poids_max__lte=10)
        if self.value() == 'lourd':
            return queryset.filter(poids_min__gte=10, poids_max__lte=30)
        if self.value() == 'tres_lourd':
            return queryset.filter(poids_min__gte=30)
        return queryset


# ===================================
# INLINE POUR TARIFS
# ===================================

class TarifInline(admin.TabularInline):
    """Inline pour les tarifs d'un livreur"""
    model = Tarif
    extra = 1

    fields = [
        'poids_min', 'poids_max', 'prix_ht', 
        'taux_tva', 'prix_ttc', 'display_marge'
    ]

    readonly_fields = ['display_marge']

    def display_marge(self, obj):
        """Affiche la marge par kg"""
        if obj.pk and obj.poids_max > obj.poids_min:
            marge_kg = float(obj.prix_ttc) / (float(obj.poids_max) - float(obj.poids_min))
            return format_html(
                '<span style="color: #4caf50; font-weight: bold;">{:.2f} €/kg</span>',
                marge_kg
            )
        return '—'
    display_marge.short_description = 'Prix/kg'


# ===================================
# ADMIN LIVREUR
# ===================================

@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    """Administration des livreurs"""

    list_display = [
        'display_nom', 'display_contact', 'display_type_service',
        'display_nb_tarifs', 'display_statut', 'date_ajoutee'
    ]

    list_filter = [
        'est_actif', 
        TypeServiceFilter,
        'date_ajoutee'
    ]

    search_fields = [
        'nom', 'email', 'telephone', 'cle_api'
    ]

    readonly_fields = [
        'date_ajoutee', 'date_modifiee',
        'display_statistiques', 'display_grille_tarifaire'
    ]

    inlines = [TarifInline]

    date_hierarchy = 'date_ajoutee'

    list_per_page = 25

    actions = [
        'activer_livreurs', 'desactiver_livreurs',
        'dupliquer_tarifs', 'passer_en_express'
    ]

    fieldsets = (
        ('👤 Informations générales', {
            'fields': ('nom', 'email', 'telephone', 'adresse')
        }),
        ('🔐 API', {
            'fields': ('cle_api',),
            'classes': ('collapse',)
        }),
        ('⚙️ Configuration', {
            'fields': ('type_service', 'est_actif')
        }),
        ('📊 Statistiques', {
            'fields': ('display_statistiques', 'display_grille_tarifaire'),
            'classes': ('collapse',)
        }),
        ('📅 Dates', {
            'fields': ('date_ajoutee', 'date_modifiee'),
            'classes': ('collapse',)
        }),
    )

    # ===================================
    # MÉTHODES D'AFFICHAGE
    # ===================================

    def display_nom(self, obj):
        """Affiche le nom avec icône selon le statut"""
        icone = '✅' if obj.est_actif else '❌'
        return format_html(
            '{} <strong>{}</strong>',
            icone,
            obj.nom
        )
    display_nom.short_description = 'Livreur'
    display_nom.admin_order_field = 'nom'

    def display_contact(self, obj):
        """Affiche les informations de contact"""
        return format_html(
            '📧 <a href="mailto:{}">{}</a><br>'
            '📞 {}',
            obj.email,
            obj.email,
            obj.telephone or '—'
        )
    display_contact.short_description = 'Contact'

    def display_type_service(self, obj):
        """Affiche le type de service avec style"""
        if obj.type_service == 'express':
            return format_html(
                '<span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;">'
                '⚡ EXPRESS'
                '</span>'
            )
        return format_html(
            '<span style="background: #e3f2fd; color: #1976d2; '
            'padding: 5px 15px; border-radius: 20px; font-weight: bold;">'
            '📦 STANDARD'
            '</span>'
        )
    display_type_service.short_description = 'Service'
    display_type_service.admin_order_field = 'type_service'

    def display_nb_tarifs(self, obj):
        """Affiche le nombre de tarifs"""
        nb = obj.tarifs.count()
        if nb == 0:
            return format_html('<span style="color: #f44336;">⚠️ 0</span>')
        return format_html(
            '<strong style="color: #4caf50;">💰 {}</strong>',
            nb
        )
    display_nb_tarifs.short_description = 'Tarifs'

    def display_statut(self, obj):
        """Affiche le statut"""
        if obj.est_actif:
            return format_html(
                '<span style="color: #4caf50; font-weight: bold;">✅ Actif</span>'
            )
        return format_html(
            '<span style="color: #f44336; font-weight: bold;">❌ Inactif</span>'
        )
    display_statut.short_description = 'Statut'
    display_statut.admin_order_field = 'est_actif'

    def display_statistiques(self, obj):
        """Affiche les statistiques du livreur"""
        tarifs = obj.tarifs.all()

        if not tarifs.exists():
            return format_html(
                '<div style="padding: 20px; background: #fff3cd; border-radius: 5px;">'
                '⚠️ Aucun tarif configuré'
                '</div>'
            )

        prix_min = tarifs.order_by('prix_ttc').first()
        prix_max = tarifs.order_by('-prix_ttc').first()
        poids_max = tarifs.order_by('-poids_max').first()

        html = '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
        html += 'color: white; padding: 20px; border-radius: 10px;">'
        html += '<h3 style="margin: 0 0 15px 0;">📊 Statistiques</h3>'
        html += '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">'

        # Nombre de tarifs
        html += '<div style="text-align: center;">'
        html += '<div style="font-size: 32px; font-weight: bold;">{}</div>'.format(tarifs.count())
        html += '<div style="opacity: 0.9;">💰 Tarifs</div>'
        html += '</div>'

        # Prix minimum
        html += '<div style="text-align: center;">'
        html += '<div style="font-size: 32px; font-weight: bold;">{:.2f} €</div>'.format(float(prix_min.prix_ttc))
        html += '<div style="opacity: 0.9;">🔽 Prix min</div>'
        html += '</div>'

        # Prix maximum
        html += '<div style="text-align: center;">'
        html += '<div style="font-size: 32px; font-weight: bold;">{:.2f} €</div>'.format(float(prix_max.prix_ttc))
        html += '<div style="opacity: 0.9;">🔼 Prix max</div>'
        html += '</div>'

        html += '</div>'

        # Poids maximum supporté
        html += '<div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.3);">'
        html += '<div style="text-align: center;">'
        html += '<strong>⚖️ Poids max supporté :</strong> {} kg'.format(float(poids_max.poids_max))
        html += '</div></div>'

        html += '</div>'
        return format_html(html)
    display_statistiques.short_description = 'Statistiques'

# CORRECTION 1 : Ligne ~227
    def display_grille_tarifaire(self, obj):
        """Affiche la grille tarifaire complète"""
        tarifs = obj.tarifs.all().order_by('poids_min')

        if not tarifs.exists():
            return format_html('<p style="color: #999;">Aucun tarif</p>')

        html = '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead><tr style="background: #ddd;">'
        html += '<th style="padding: 10px; text-align: left;">Tranche de poids</th>'
        html += '<th style="padding: 10px; text-align: right;">Prix HT</th>'
        html += '<th style="padding: 10px; text-align: right;">TVA</th>'
        html += '<th style="padding: 10px; text-align: right;">Prix TTC</th>'
        html += '</tr></thead><tbody>'

        for tarif in tarifs:
            html += '<tr style="border-bottom: 1px solid #ddd;">'
            html += '<td style="padding: 10px;"><strong>{} - {} kg</strong></td>'.format(
                float(tarif.poids_min), 
                float(tarif.poids_max)
            )
            html += '<td style="padding: 10px; text-align: right;">{:.2f} €</td>'.format(float(tarif.prix_ht))
            html += '<td style="padding: 10px; text-align: right;">{:.2f}%</td>'.format(float(tarif.taux_tva))  # ✅ CORRIGÉ
            html += '<td style="padding: 10px; text-align: right;"><strong>{:.2f} €</strong></td>'.format(float(tarif.prix_ttc))
            html += '</tr>'

        html += '</tbody></table></div>'
        return format_html(html)

    # ===================================
    # ACTIONS
    # ===================================

    @admin.action(description='✅ Activer les livreurs sélectionnés')
    def activer_livreurs(self, request, queryset):
        count = queryset.update(est_actif=True)
        self.message_user(
            request,
            '{} livreur(s) activé(s)'.format(count),
            messages.SUCCESS
        )

    @admin.action(description='❌ Désactiver les livreurs sélectionnés')
    def desactiver_livreurs(self, request, queryset):
        count = queryset.update(est_actif=False)
        self.message_user(
            request,
            '{} livreur(s) désactivé(s)'.format(count),
            messages.WARNING
        )

    @admin.action(description='⚡ Passer en mode Express')
    def passer_en_express(self, request, queryset):
        count = queryset.update(type_service='express')
        self.message_user(
            request,
            '{} livreur(s) passé(s) en Express'.format(count),
            messages.SUCCESS
        )

    @admin.action(description='📋 Dupliquer les tarifs')
    def dupliquer_tarifs(self, request, queryset):
        """Duplique les tarifs d'un livreur vers un autre"""
        if queryset.count() != 2:
            self.message_user(
                request,
                '⚠️ Sélectionnez exactement 2 livreurs (source et destination)',
                messages.WARNING
            )
            return

        livreurs = list(queryset)
        source = livreurs[0]
        destination = livreurs[1]

        tarifs_copies = 0
        for tarif in source.tarifs.all():
            Tarif.objects.create(
                livreur=destination,
                poids_min=tarif.poids_min,
                poids_max=tarif.poids_max,
                prix_ht=tarif.prix_ht,
                prix_ttc=tarif.prix_ttc,
                taux_tva=tarif.taux_tva
            )
            tarifs_copies += 1

        self.message_user(
            request,
            '{} tarif(s) copié(s) de {} vers {}'.format(
                tarifs_copies, source.nom, destination.nom
            ),
            messages.SUCCESS
        )

    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).prefetch_related('tarifs')


# ===================================
# ADMIN TARIF
# ===================================

# livraisons/admin.py

# livraisons/admin.py

# livraisons/admin.py

@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    """Administration des tarifs"""

    list_display = [
        'display_livreur', 
        'display_tranche', 
        'display_prix_ht',
        'display_tva', 
        'display_prix_ttc', 
        'display_prix_kg'
    ]

    list_filter = [
        'livreur',
        PoidsFilter,
        'taux_tva'
    ]

    search_fields = [
        'livreur__nom',
    ]

    readonly_fields = ['display_prix_kg', 'display_formule']

    list_per_page = 50

    actions = ['augmenter_prix', 'diminuer_prix', 'recalculer_ttc']

    fieldsets = (
        ('🚚 Livreur', {
            'fields': ('livreur',)
        }),
        ('⚖️ Poids', {
            'fields': ('poids_min', 'poids_max')
        }),
        ('💰 Tarification', {
            'fields': ('prix_ht', 'taux_tva', 'prix_ttc')
        }),
        ('📊 Calculs', {
            'fields': ('display_prix_kg', 'display_formule'),
            'classes': ('collapse',)
        }),
    )

    # ===================================
    # MÉTHODES D'AFFICHAGE
    # ===================================

    @admin.display(description='Livreur', ordering='livreur__nom')
    def display_livreur(self, obj):
        """Affiche le livreur avec type de service"""
        if not obj or not obj.livreur:
            return '—'
        
        icone = '⚡' if obj.livreur.type_service == 'express' else '📦'
        return format_html(
            '<span>{} <strong>{}</strong></span>',
            icone,
            obj.livreur.nom
        )

    @admin.display(description='Tranche de poids')
    def display_tranche(self, obj):
        """Affiche la tranche de poids"""
        if not obj or not obj.pk:
            return '—'
        
        if obj.poids_min is None or obj.poids_max is None:
            return format_html('<em style="color: #999;">Non définie</em>')
        
        return format_html(
            '<span><strong>{}</strong> → <strong>{}</strong> kg</span>',
            float(obj.poids_min),
            float(obj.poids_max)
        )

    @admin.display(description='Prix HT')
    def display_prix_ht(self, obj):
        """Affiche le prix HT"""
        if not obj or not obj.pk or obj.prix_ht is None:
            return '—'
        
        return format_html(
            '<span style="color: #2196f3; font-weight: bold;">{:.2f} €</span>',
            float(obj.prix_ht)
        )

    @admin.display(description='TVA')
    def display_tva(self, obj):
        """Affiche le taux de TVA"""
        if not obj or not obj.pk or obj.taux_tva is None:
            return '—'
        
        return format_html(
            '<span style="color: #ff9800;">{:.1f}%</span>',
            float(obj.taux_tva)
        )

    @admin.display(description='Prix TTC')
    def display_prix_ttc(self, obj):
        """Affiche le prix TTC"""
        if not obj or not obj.pk or obj.prix_ttc is None:
            return '—'
        
        return format_html(
            '<span style="color: #4caf50; font-weight: bold; font-size: 14px;">{:.2f} €</span>',
            float(obj.prix_ttc)
        )

    @admin.display(description='Prix/kg')
    def display_prix_kg(self, obj):
        """Affiche le prix au kg"""
        if not obj or not obj.pk:
            return format_html('<em style="color: #999;">Enregistrez d\'abord</em>')
        
        if obj.poids_min is None or obj.poids_max is None or obj.prix_ttc is None:
            return format_html('<em style="color: #999;">Données incomplètes</em>')
        
        try:
            ecart_poids = float(obj.poids_max) - float(obj.poids_min)
            
            if ecart_poids <= 0:
                return format_html('<em style="color: #f44336;">⚠️ Poids max doit être &gt; poids min</em>')
            
            prix_kg = float(obj.prix_ttc) / ecart_poids
            
            return format_html(
                '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; padding: 8px 12px; border-radius: 5px; display: inline-block;">'
                '<strong>{:.2f} €/kg</strong>'
                '</div>',
                prix_kg
            )
        except Exception as e:
            return format_html('<em style="color: #f44336;">Erreur de calcul</em>')

    @admin.display(description='Formule de calcul')
    def display_formule(self, obj):
        """Affiche la formule de calcul"""
        if not obj or not obj.pk:
            return '—'
        
        if obj.poids_min is None or obj.poids_max is None or obj.prix_ttc is None:
            return '—'
        
        try:
            ecart = float(obj.poids_max) - float(obj.poids_min)
            if ecart <= 0:
                return '—'
            
            return format_html(
                '<code style="background: #f5f5f5; padding: 5px; border-radius: 3px;">'
                '{:.2f} € ÷ ({} kg - {} kg) = {:.2f} €/kg'
                '</code>',
                float(obj.prix_ttc),
                float(obj.poids_max),
                float(obj.poids_min),
                float(obj.prix_ttc) / ecart
            )
        except Exception:
            return '—'

    # ===================================
    # ACTIONS
    # ===================================

    @admin.action(description='Augmenter les prix de 10%%')  # ✅ Double %% pour échapper
    def augmenter_prix(self, request, queryset):
        """Augmente les prix de 10%"""
        count = 0
        for tarif in queryset:
            try:
                if tarif.prix_ht and tarif.prix_ttc:
                    tarif.prix_ht *= Decimal('1.10')
                    tarif.prix_ttc *= Decimal('1.10')
                    tarif.save()
                    count += 1
            except Exception:
                continue

        self.message_user(
            request,
            'Prix augmentés de 10% pour {} tarif(s)'.format(count),
            messages.SUCCESS
        )

    @admin.action(description='Diminuer les prix de 10%%')  # ✅ Double %% pour échapper
    def diminuer_prix(self, request, queryset):
        """Diminue les prix de 10%"""
        count = 0
        for tarif in queryset:
            try:
                if tarif.prix_ht and tarif.prix_ttc:
                    tarif.prix_ht *= Decimal('0.90')
                    tarif.prix_ttc *= Decimal('0.90')
                    tarif.save()
                    count += 1
            except Exception:
                continue

        self.message_user(
            request,
            'Prix diminués de 10% pour {} tarif(s)'.format(count),
            messages.SUCCESS
        )

    @admin.action(description='Recalculer les prix TTC')
    def recalculer_ttc(self, request, queryset):
        """Recalcule les prix TTC"""
        count = 0
        for tarif in queryset:
            try:
                if tarif.prix_ht and tarif.taux_tva:
                    tarif.prix_ttc = tarif.prix_ht * (1 + tarif.taux_tva / 100)
                    tarif.save()
                    count += 1
            except Exception:
                continue

        self.message_user(
            request,
            'Prix TTC recalculés pour {} tarif(s)'.format(count),
            messages.SUCCESS
        )

    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('livreur')

# ===================================
# ADMIN POINT RELAIS
# ===================================

@admin.register(PointRelais)
class PointRelaisAdmin(admin.ModelAdmin):
    """Administration des points relais"""

    list_display = [
        'display_nom', 'display_adresse', 'display_capacite',
        'display_statut', 'display_coordonnees'
    ]

    list_filter = [
        'est_actif',
        'ville',
        'code_postal',
        'pays'
    ]

    search_fields = [
        'nom', 'adresse', 'ville',
        'code_postal', 'telephone'
    ]

    readonly_fields = [
        'display_carte', 'display_infos_complete'
    ]

    list_per_page = 25

    actions = [
        'activer_points', 'desactiver_points',
        'exporter_coordonnees'
    ]

    fieldsets = (
        ('📍 Identification', {
            'fields': ('nom', 'telephone')
        }),
        ('🏠 Adresse', {
            'fields': ('adresse', 'code_postal', 'ville', 'pays')
        }),
        ('🗺️ Géolocalisation', {
            'fields': ('latitude', 'longitude', 'display_carte')
        }),
        ('⏰ Horaires', {
            'fields': ('horaires_ouverture',)
        }),
        ('📦 Capacité', {
            'fields': ('capacite_max', 'est_actif')
        }),
        ('ℹ️ Informations complètes', {
            'fields': ('display_infos_complete',),
            'classes': ('collapse',)
        }),
    )

    # ===================================
    # MÉTHODES D'AFFICHAGE
    # ===================================

    def display_nom(self, obj):
        """Affiche le nom avec statut"""
        icone = '✅' if obj.est_actif else '❌'
        return format_html(
            '{} <strong>{}</strong>',
            icone,
            obj.nom
        )
    display_nom.short_description = 'Point relais'
    display_nom.admin_order_field = 'nom'

    def display_adresse(self, obj):
        """Affiche l'adresse complète"""
        return format_html(
            '{}<br><small>{} {}</small>',
            obj.adresse,
            obj.code_postal,
            obj.ville
        )
    display_adresse.short_description = 'Adresse'
    # CORRECTION 2 : Ligne ~530
    def display_capacite(self, obj):
        """Affiche la capacité"""
        pourcentage = 70  # À calculer en fonction des colis réels
        couleur = '#4caf50' if pourcentage < 80 else '#ff9800'

        return format_html(
            '<div style="background: #f5f5f5; border-radius: 5px; padding: 5px;">'
            '<div style="background: {}; height: 20px; width: {}%; border-radius: 3px;"></div>'  # ✅ CORRIGÉ
            '<small>{} / {} colis</small>'
            '</div>',
            couleur,
            pourcentage,
            int(obj.capacite_max * pourcentage / 100),
            obj.capacite_max
        )

    display_capacite.short_description = 'Capacité'

    def display_statut(self, obj):
        """Affiche le statut"""
        if obj.est_actif:
            return format_html(
                '<span style="color: #4caf50; font-weight: bold;">✅ Actif</span>'
            )
        return format_html(
            '<span style="color: #f44336; font-weight: bold;">❌ Inactif</span>'
        )
    display_statut.short_description = 'Statut'

    def display_coordonnees(self, obj):
        """Affiche les coordonnées GPS"""
        return format_html(
            '<small>📍 {}, {}</small>',
            obj.latitude,
            obj.longitude
        )
    display_coordonnees.short_description = 'GPS'

    # CORRECTION 3 : Ligne ~575
    def display_carte(self, obj):
        """Affiche une carte Google Maps"""
        if not obj.latitude or not obj.longitude:
            return format_html('<p style="color: #999;">Coordonnées manquantes</p>')

        url = 'https://www.google.com/maps?q={},{}'.format(obj.latitude, obj.longitude)

        html = '<div style="text-align: center;">'
        html += '<iframe width="100%" height="300" frameborder="0" style="border:0; border-radius: 10px;" '  # ✅ CORRIGÉ
        html += 'src="https://www.google.com/maps/embed/v1/place?key=VOTRE_CLE_API&q={},{}" '.format(obj.latitude, obj.longitude)
        html += 'allowfullscreen></iframe>'
        html += '<br><a href="{}" target="_blank" style="display: inline-block; margin-top: 10px; '.format(url)
        html += 'background: #4285f4; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">'
        html += '🗺️ Ouvrir dans Google Maps</a>'
        html += '</div>'

        return format_html(html)

    display_carte.short_description = 'Carte'

    def display_infos_complete(self, obj):
        """Affiche toutes les informations"""
        html = '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
        html += 'color: white; padding: 20px; border-radius: 10px;">'
        html += '<h3 style="margin: 0 0 15px 0;">📍 Informations complètes</h3>'

        html += '<div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; margin-bottom: 15px;">'
        html += '<strong>📍 Nom :</strong> {}<br>'.format(obj.nom)
        html += '<strong>🏠 Adresse :</strong> {}<br>'.format(obj.adresse_complete())
        html += '<strong>📞 Téléphone :</strong> {}<br>'.format(obj.telephone or "Non renseigné")
        html += '<strong>🗺️ GPS :</strong> {}, {}'.format(obj.latitude, obj.longitude)
        html += '</div>'

        if obj.horaires_ouverture:
            html += '<div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; margin-bottom: 15px;">'
            html += '<strong>⏰ Horaires :</strong><br>{}'.format(obj.horaires_ouverture.replace('\n', '<br>'))
            html += '</div>'

        html += '<div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px;">'
        html += '<strong>📦 Capacité max :</strong> {} colis<br>'.format(obj.capacite_max)
        html += '<strong>✅ Statut :</strong> {}'.format("Actif" if obj.est_actif else "Inactif")
        html += '</div>'

        html += '</div>'
        return format_html(html)
    display_infos_complete.short_description = 'Informations'

    # ===================================
    # ACTIONS
    # ===================================

    @admin.action(description='✅ Activer les points relais sélectionnés')
    def activer_points(self, request, queryset):
        count = queryset.update(est_actif=True)
        self.message_user(
            request,
            '{} point(s) relais activé(s)'.format(count),
            messages.SUCCESS
        )

    @admin.action(description='❌ Désactiver les points relais sélectionnés')
    def desactiver_points(self, request, queryset):
        count = queryset.update(est_actif=False)
        self.message_user(
            request,
            '{} point(s) relais désactivé(s)'.format(count),
            messages.WARNING
        )

    @admin.action(description='📄 Exporter les coordonnées GPS')
    def exporter_coordonnees(self, request, queryset):
        """Exporte les coordonnées GPS au format CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="points_relais.csv"'

        writer = csv.writer(response)
        writer.writerow(['Nom', 'Adresse', 'Ville', 'Code Postal', 'Latitude', 'Longitude'])

        for point in queryset:
            writer.writerow([
                point.nom,
                point.adresse,
                point.ville,
                point.code_postal,
                point.latitude,
                point.longitude
            ])

        return response
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
