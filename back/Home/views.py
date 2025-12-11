from django.shortcuts import render
<<<<<<< HEAD

# Create your views here.
def Home(request):
    return render(request, 'OcciDelice.html')
=======
from produits.models import Categorie, SousCategorie, SousSousCategorie, Produit
from fournisseur.models import Fournisseur
from commandes.models import Commande
from paniers.models import LignePanier
from django.db.models import Count, Q

# Create your views here.
def Home(request):
    # Récupérer les catégories actives avec leurs sous-catégories
    categories = Categorie.objects.filter(est_active=True).prefetch_related(
        'souscategories__soussouscategories'
    ).annotate(
        nb_produits=Count('produits', filter=Q(produits__est_actif=True))
    ).order_by('ordre')[:6]  # Top 6 catégories

    # Récupérer les fournisseurs avec leurs coordonnées pour la carte
    fournisseurs = Fournisseur.objects.all().select_related().order_by('-date_ajoutee')[:12]  # Top 12 fournisseurs

    # Produits nouveautés et promotions
    produits_nouveautes = Produit.objects.filter(
        est_actif=True,
        est_nouveaute=True
    ).select_related('categorie').order_by('-date_creation')[:6]

    produits_promos = Produit.objects.filter(
        est_actif=True,
        en_promotion=True
    ).select_related('categorie').order_by('-date_creation')[:6]

    # Statistiques de base pour tout le monde
    stats = {
        'total_produits': Produit.objects.filter(est_actif=True).count(),
        'total_fournisseurs': Fournisseur.objects.all().count(),
        'total_categories': Categorie.objects.filter(est_active=True).count(),
    }

    context = {
        'categories': categories,
        'fournisseurs': fournisseurs,
        'produits_nouveautes': produits_nouveautes,
        'produits_promos': produits_promos,
        'stats': stats,
    }

    # Statistiques spécifiques pour les utilisateurs connectés
    if request.user.is_authenticated:
        # ADMINISTRATEUR
        if request.user.is_superuser:
            context['nb_commandes_total'] = Commande.objects.count()

        # FOURNISSEUR
        elif request.user.username.startswith('fournisseur_') and hasattr(request.user, 'fournisseur'):
            fournisseur = request.user.fournisseur

            # Nombre de produits du fournisseur
            nb_produits = Produit.objects.filter(fournisseur=fournisseur).count()
            context['nb_produits'] = nb_produits

            # Nombre de produits actifs
            nb_produits_actifs = Produit.objects.filter(
                fournisseur=fournisseur,
                est_actif=True
            ).count()
            context['nb_produits_actifs'] = nb_produits_actifs

            # Nombre de commandes contenant ses produits
            commandes_ids = LignePanier.objects.filter(
                produit__fournisseur=fournisseur
            ).values_list('panier__commande__id', flat=True).distinct()
            nb_commandes = len([c for c in commandes_ids if c is not None])
            context['nb_commandes'] = nb_commandes

            # Note moyenne (placeholder - à implémenter si système de notation existe)
            context['note_moyenne'] = "N/A"

    return render(request, 'Home.html', context)
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
