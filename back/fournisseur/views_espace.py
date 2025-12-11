"""
Vues pour l'espace fournisseur personnalisé
Pages web sur mesure (pas Django admin)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Fournisseur
from .forms import ProduitForm, FournisseurProfilForm
from produits.models import Produit, Categorie, SousCategorie
from commandes.models import Commande
from paniers.models import LignePanier
from django.contrib.auth.hashers import make_password


def fournisseur_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est un fournisseur"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Vous devez être connecté")
            return redirect('fournisseur_login')

        if not request.user.username.startswith('fournisseur_'):
            messages.error(request, "Accès réservé aux fournisseurs")
            return redirect('home')

        if not hasattr(request.user, 'fournisseur'):
            messages.error(request, "Profil fournisseur introuvable")
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return wrapper


def unified_login(request):
    """
    Page de connexion unifiée pour:
    - Admins Django (superuser)
    - Fournisseurs
    """
    # Si déjà connecté, rediriger vers le bon espace
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.username.startswith('fournisseur_'):
            return redirect('fournisseur:dashboard')
        else:
            return redirect('home')

    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')

        from django.contrib.auth import authenticate, login
        from django.contrib.auth.models import User

        user = None

        # 1. Essayer d'abord avec le username direct (pour les admins)
        user = authenticate(request, username=email_or_username, password=password)

        # 2. Si échec, chercher un utilisateur par email et essayer avec son username
        if not user:
            try:
                django_user = User.objects.get(email=email_or_username)
                user = authenticate(request, username=django_user.username, password=password)
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # Si plusieurs utilisateurs avec le même email, prendre le premier
                django_user = User.objects.filter(email=email_or_username).first()
                if django_user:
                    user = authenticate(request, username=django_user.username, password=password)

        # 3. Si toujours échec, essayer l'authentification fournisseur (par email)
        if not user:
            try:
                from fournisseur.backends import FournisseurAuthBackend
                backend = FournisseurAuthBackend()
                user = backend.authenticate(request, username=email_or_username, password=password)
            except:
                pass

        if user:
            login(request, user)

            # Redirection selon le type d'utilisateur
            if user.is_superuser:
                messages.success(request, f'Bienvenue Admin {user.username}!')
                return redirect('/admin/')
            elif user.username.startswith('fournisseur_'):
                messages.success(request, f'Bienvenue {user.fournisseur.prenom} {user.fournisseur.nom}!')
                return redirect('fournisseur:dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect')

    return render(request, 'fournisseur_login.html')


def fournisseur_login(request):
    """Redirection vers le login unifié"""
    return unified_login(request)


@fournisseur_required
def fournisseur_dashboard(request):
    """Dashboard du fournisseur"""
    fournisseur = request.user.fournisseur

    # Statistiques
    nb_produits = Produit.objects.filter(fournisseur=fournisseur).count()
    nb_produits_actifs = Produit.objects.filter(fournisseur=fournisseur, est_actif=True).count()

    # Commandes contenant ses produits
    commandes_ids = LignePanier.objects.filter(
        produit__fournisseur=fournisseur
    ).values_list('panier__commande__id', flat=True).distinct()
    nb_commandes = len([c for c in commandes_ids if c is not None])

    # Produits récents
    produits_recents = Produit.objects.filter(
        fournisseur=fournisseur
    ).order_by('-date_creation')[:5]

    context = {
        'fournisseur': fournisseur,
        'nb_produits': nb_produits,
        'nb_produits_actifs': nb_produits_actifs,
        'nb_commandes': nb_commandes,
        'produits_recents': produits_recents,
    }

    return render(request, 'fournisseur_dashboard.html', context)


@fournisseur_required
def fournisseur_produits(request):
    """Liste des produits du fournisseur"""
    fournisseur = request.user.fournisseur

    produits = Produit.objects.filter(fournisseur=fournisseur).order_by('-date_creation')

    # Filtres
    search = request.GET.get('search', '')
    if search:
        produits = produits.filter(Q(nom__icontains=search) | Q(numero_unique__icontains=search))

    statut = request.GET.get('statut', '')
    if statut == 'actif':
        produits = produits.filter(est_actif=True)
    elif statut == 'inactif':
        produits = produits.filter(est_actif=False)

    context = {
        'fournisseur': fournisseur,
        'produits': produits,
        'search': search,
        'statut': statut,
    }

    return render(request, 'fournisseur_produits_liste.html', context)


@fournisseur_required
def fournisseur_produit_ajouter(request):
    """Ajouter un nouveau produit"""
    fournisseur = request.user.fournisseur

    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.fournisseur = fournisseur
            produit.save()
            messages.success(request, f'Produit "{produit.nom}" ajouté avec succès !')
            return redirect('fournisseur:produits')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez vérifier les champs.')
    else:
        form = ProduitForm()

    context = {
        'fournisseur': fournisseur,
        'form': form,
    }

    return render(request, 'fournisseur_produit_form.html', context)


@fournisseur_required
def fournisseur_produit_modifier(request, pk):
    """Modifier un produit existant"""
    fournisseur = request.user.fournisseur
    produit = get_object_or_404(Produit, pk=pk, fournisseur=fournisseur)

    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produit "{produit.nom}" modifié avec succès !')
            return redirect('fournisseur:produits')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez vérifier les champs.')
    else:
        form = ProduitForm(instance=produit)

    context = {
        'fournisseur': fournisseur,
        'produit': produit,
        'form': form,
        'mode': 'modifier',
    }

    return render(request, 'fournisseur_produit_form.html', context)


@fournisseur_required
def fournisseur_produit_supprimer(request, pk):
    """Supprimer un produit"""
    fournisseur = request.user.fournisseur
    produit = get_object_or_404(Produit, pk=pk, fournisseur=fournisseur)

    if request.method == 'POST':
        nom = produit.nom
        produit.delete()
        messages.success(request, f'Produit "{nom}" supprimé avec succès !')
        return redirect('fournisseur:produits')

    context = {
        'fournisseur': fournisseur,
        'produit': produit,
    }

    return render(request, 'fournisseur_produit_supprimer.html', context)


@fournisseur_required
def fournisseur_profil(request):
    """Paramétrage du profil fournisseur"""
    fournisseur = request.user.fournisseur

    if request.method == 'POST':
        # Gérer le changement de mot de passe
        if request.POST.get('action') == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if current_password and new_password and confirm_password:
                # Vérifier le mot de passe actuel
                if not fournisseur.check_password(current_password):
                    messages.error(request, 'Mot de passe actuel incorrect')
                elif new_password != confirm_password:
                    messages.error(request, 'Les nouveaux mots de passe ne correspondent pas')
                else:
                    fournisseur.set_password(new_password)
                    fournisseur.save()
                    messages.success(request, 'Mot de passe modifié avec succès !')
                    return redirect('fournisseur:profil')
            else:
                messages.error(request, 'Tous les champs sont obligatoires pour changer le mot de passe')

    context = {
        'fournisseur': fournisseur,
    }

    return render(request, 'fournisseur_profil.html', context)


@fournisseur_required
def fournisseur_commandes(request):
    """Liste des commandes contenant les produits du fournisseur"""
    fournisseur = request.user.fournisseur

    # Récupérer les commandes contenant ses produits
    commandes_ids = LignePanier.objects.filter(
        produit__fournisseur=fournisseur
    ).values_list('panier__commande__id', flat=True).distinct()

    commandes = Commande.objects.filter(id__in=commandes_ids).select_related('client', 'livreur', 'point_relais').order_by('-date_commande')

    # Filtrer par statut si demandé
    statut = request.GET.get('statut', '')
    if statut:
        commandes = commandes.filter(statut=statut)

    # Statistiques
    total_commandes = commandes.count()
    commandes_en_attente = commandes.filter(statut='en_attente').count()
    commandes_livrees = commandes.filter(statut='terminee').count()

    # Pour chaque commande, récupérer uniquement les lignes du fournisseur
    for commande in commandes:
        commande.mes_lignes = LignePanier.objects.filter(
            panier__commande=commande,
            produit__fournisseur=fournisseur
        ).select_related('produit')

    context = {
        'fournisseur': fournisseur,
        'commandes': commandes,
        'total_commandes': total_commandes,
        'commandes_en_attente': commandes_en_attente,
        'commandes_livrees': commandes_livrees,
    }

    return render(request, 'fournisseur_commandes.html', context)
