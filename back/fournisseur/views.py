from django.shortcuts import render

# Create your views here.
# fournisseurs/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .models import Fournisseur


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_fournisseur(request):
    """
    Vue de connexion pour les fournisseurs
    SÉPARÉE de l'admin Django
    """
    # Si déjà connecté, rediriger vers le dashboard
    if request.session.get('fournisseur_id'):
        return redirect('fournisseurs:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            fournisseur = Fournisseur.objects.get(email=email, actif=True)
            
            if fournisseur.check_password(password):
                # Créer la session fournisseur
                request.session['fournisseur_id'] = fournisseur.pk
                request.session['fournisseur_nom'] = fournisseur.nom
                
                # Enregistrer la connexion
                fournisseur.enregistrer_connexion()
                
                messages.success(request, f'Bienvenue {fournisseur.nom} !')
                return redirect('fournisseurs:dashboard')
            else:
                messages.error(request, 'Email ou mot de passe incorrect')
                
        except Fournisseur.DoesNotExist:
            messages.error(request, 'Email ou mot de passe incorrect')

    context = {
        'titre': 'Connexion Fournisseur'
    }
    return render(request, 'fournisseurs/login.html', context)


def logout_fournisseur(request):
    """
    Vue de déconnexion pour les fournisseurs
    """
    if 'fournisseur_id' in request.session:
        del request.session['fournisseur_id']
    if 'fournisseur_nom' in request.session:
        del request.session['fournisseur_nom']
    
    messages.success(request, 'Vous êtes déconnecté')
    return redirect('fournisseurs:login')


# fournisseur/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from decimal import Decimal
from .models import Fournisseur
from django.views.generic import DetailView


def liste_fournisseurs(request):
    """
    Affiche la liste des fournisseurs avec filtres et recherche
    """
    # Récupération de tous les fournisseurs
    fournisseurs = Fournisseur.objects.all()

    # ===================================
    # FILTRES
    # ===================================
    
    # Recherche par nom, prénom, métier ou ville
    search = request.GET.get('search', '')
    if search:
        fournisseurs = fournisseurs.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(metier__icontains=search) |
            Q(ville__icontains=search) |
            Q(produits_principaux__icontains=search)
        )

    # Filtre par métier
    metier = request.GET.get('metier', '')
    if metier:
        fournisseurs = fournisseurs.filter(metier__icontains=metier)

    # Filtre par ville
    ville = request.GET.get('ville', '')
    if ville:
        fournisseurs = fournisseurs.filter(ville__icontains=ville)

    # Filtre par type de production
    type_production = request.GET.get('type_production', '')
    if type_production:
        fournisseurs = fournisseurs.filter(type_production=type_production)

    # Filtre par zone de livraison
    zone_livraison = request.GET.get('zone_livraison', '')
    if zone_livraison:
        fournisseurs = fournisseurs.filter(zone_livraison_type=zone_livraison)

    # Tri
    sort = request.GET.get('sort', 'nom')
    if sort == 'ville':
        fournisseurs = fournisseurs.order_by('ville', 'nom')
    elif sort == 'metier':
        fournisseurs = fournisseurs.order_by('metier', 'nom')
    elif sort == 'experience':
        fournisseurs = fournisseurs.order_by('-experience_annees', 'nom')
    else:
        fournisseurs = fournisseurs.order_by('nom', 'prenom')

    # ===================================
    # STATISTIQUES
    # ===================================
    stats = {
        'total': fournisseurs.count(),
        'villes': fournisseurs.values('ville').distinct().count(),
        'metiers': fournisseurs.values('metier').distinct().count(),
        'bio': fournisseurs.filter(type_production='biologique').count(),
        'permaculture': fournisseurs.filter(type_production='permaculture').count(),
    }

    # ===================================
    # PAGINATION
    # ===================================
    paginator = Paginator(fournisseurs, 12)  # 12 fournisseurs par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ===================================
    # CONTEXTE
    # ===================================
    context = {
        'fournisseurs': page_obj,
        'page_obj': page_obj,
        'stats': stats,
        'search': search,
        'metier': metier,
        'ville': ville,
        'type_production': type_production,
        'zone_livraison': zone_livraison,
        'sort': sort,
        # Listes pour les filtres
        'metiers_list': Fournisseur.objects.values_list('metier', flat=True).distinct().order_by('metier'),
        'villes_list': Fournisseur.objects.values_list('ville', flat=True).distinct().order_by('ville'),
        'types_production': [
            ('permaculture', 'Permaculture'),
            ('biologique', 'Biologique'),
            ('raisonnee', 'Agriculture Raisonnée'),
            ('autre', 'Autre')
        ],
        'zones_livraison': [
            ('rayon', 'Rayon kilométrique'),
            ('departements', 'Départements'),
            ('villes', 'Villes spécifiques'),
            ('national', 'National'),
        ],
    }

    return render(request, 'FournisseurList.html', context)


class FournisseurDetailView(DetailView):
    model = Fournisseur
    template_name = 'FournisseurDetail.html'
    context_object_name = 'fournisseur'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fournisseur = self.get_object()
        
        # Fournisseurs similaires (même ville ou même métier)
        context['fournisseurs_similaires'] = Fournisseur.objects.filter(
            ville=fournisseur.ville
        ).exclude(pk=fournisseur.pk)[:3]
        
        if context['fournisseurs_similaires'].count() < 3:
            context['fournisseurs_similaires'] = Fournisseur.objects.filter(
                metier=fournisseur.metier
            ).exclude(pk=fournisseur.pk)[:3]
        
        return context