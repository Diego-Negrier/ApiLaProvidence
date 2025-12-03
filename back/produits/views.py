from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Produit
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from clients.utilis import client_login_required
import json
from .forms import ProduitForm
from .models import (Produit,
                    Categorie,
                    SousCategorie,
                    Fournisseur
                    )
# Create your views here.
from .models import Categorie, SousCategorie
import logging
from .models import Fournisseur
from .forms import FournisseurForm
from django.contrib import messages
# views.py



@csrf_exempt  # Ajoute la protection CSRF de manière appropriée pour ton cas




def save_image(request, produit_id):  
    if request.method == 'POST':
        # Utilisation de get_object_or_404 pour récupérer le produit
        produit = get_object_or_404(Produit, pk=produit_id)
        
        # Récupération de l'image de la requête
        image = request.FILES.get('image')

        if image:
            # Sauvegarder l'image
            produit.image = image
            produit.save()
            
            # Log succès
            logger.info(f"Image sauvegardée avec succès pour le produit ID {produit_id}.")
            
            return JsonResponse({'message': 'Image sauvegardée avec succès !'})
        else:
            # Log erreur si pas d'image
            logger.warning(f"Aucune image reçue pour le produit ID {produit_id}.")
            
            return JsonResponse({'error': 'Aucune image envoyée'}, status=400)

    # Log si méthode incorrecte
    logger.error(f"Requête avec une méthode non POST pour le produit ID {produit_id}.")
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


# Configurez le logger pour afficher des messages dans la console ou les logs
logger = logging.getLogger(__name__)



def catalogue_view(request):
    produits = Produit.objects.all()
    produits_data = []
    
    # Préparer les données pour la réponse JSON
    for produit in produits:
        produits_data.append({
            'pk': produit.id,
            'nom': produit.nom,
            'description': produit.description,
            'prix': str(produit.prix),
            'stock': produit.stock,
            'image': produit.image.url if produit.image else None,
            'grande_image': produit.grande_image.url if produit.grande_image else None,
            'categorie': produit.categorie if produit.categorie else None,
            'souscategorie': produit.souscategorie if produit.souscategorie else None,
            'qr_code': produit.qr_code.url if produit.qr_code else None,
            'numero_unique': produit.numero_unique,
            'adresse_produit': produit.adresse_produit,
            'lat': produit.lat,
            'long': produit.long,
            'poids': str(produit.poids) if produit.poids else None,
            'fournisseur': produit.fournisseur if produit.fournisseur else None
        })
    # Variables pour vérifier si l'utilisateur est admin ou fournisseur
    is_admin = False
    is_fournisseur = False
    is_authenticated = request.user.is_authenticated  # Vérifie si l'utilisateur est connecté

    if is_authenticated:
        if request.user.groups.filter(name='Administrateurs').exists():
            is_admin = True
        elif request.user.groups.filter(name='Fournisseurs').exists():
            is_fournisseur = True

        if is_fournisseur:
            try:
                fournisseur = Fournisseur.objects.get(user=request.user)
                produits = Produit.objects.filter(fournisseur=fournisseur)
            except Fournisseur.DoesNotExist:
                produits = Produit.objects.none()

    # Passer les informations nécessaires au template
    context = {
        'produits': produits_data,
        'is_admin': is_admin,
        'is_fournisseur': is_fournisseur,
        'is_authenticated': is_authenticated  # Passer l'état de la connexion
    }

    return render(request, 'Catalogue.html', context)


@login_required
def edit_fournisseur(request):
    try:
        fournisseur = Fournisseur.objects.get(user=request.user)
    except Fournisseur.DoesNotExist:
        messages.error(request, "Aucun profil fournisseur trouvé.")
        return redirect('home')  # Redirigez vers une page d'accueil ou autre.

    if request.method == 'POST':
        form = FournisseurForm(request.POST, request.FILES, instance=fournisseur)  # Ajoutez request.FILES ici
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect('edit_fournisseur')  # Recharge la page ou redirige selon votre logique.
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = FournisseurForm(instance=fournisseur)

    return render(request, 'Fournisseur.html', {'form': form, 'fournisseur': fournisseur})


@login_required
def ajouter_produit(request, pk=None):
    # Si un 'pk' est passé, on récupère le produit existant, sinon on crée un produit vide
    if pk:
        produit = get_object_or_404(Produit, pk=pk)
        # Vérification si l'utilisateur est administrateur ou s'il est le fournisseur du produit
        if not request.user.groups.filter(name='Administrateurs').exists() and produit.fournisseur != Fournisseur.objects.get(user=request.user):
            return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour modifier ce produit.")
        action = 'modifier'
    else:
        # Si c'est un nouveau produit, vérifier si l'utilisateur est un fournisseur ou administrateur
        if not request.user.groups.filter(name='Administrateurs').exists() and not request.user.groups.filter(name='Fournisseurs').exists():
            return HttpResponseForbidden("Vous devez être un administrateur ou un fournisseur pour ajouter un produit.")
        produit = Produit(fournisseur=Fournisseur.objects.get(user=request.user))  # Associe le fournisseur à son produit
        action = 'ajouter'

    # Traitement du formulaire
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('catalogue')  # Rediriger vers le catalogue après enregistrement

    else:
        form = ProduitForm(instance=produit)  # Si c'est un GET, on pré-remplit le formulaire avec les données existantes

    return render(request, 'FormulaireProduit.html', {'form': form, 'action': action})

@login_required
def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)

    # Vérifier si l'utilisateur est un administrateur ou le fournisseur du produit
    if not request.user.groups.filter(name='Administrateurs').exists() and produit.fournisseur != Fournisseur.objects.get(user=request.user):
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour supprimer ce produit.")

    # Vérifie si la requête est POST
    if request.method == 'POST':
        logger.debug(f"Suppression du produit {produit.nom} avec ID {pk}")
        produit.delete()  # Supprime le produit
        return redirect('catalogue')  # Redirige vers la page catalogue

    logger.debug(f"Requête non-POST reçue pour le produit {produit.nom} avec ID {pk}")
    return redirect('catalogue')  # Redirige dans tous les cas vers la page catalogue








@csrf_exempt
def produit_view(request):
    if request.method == 'GET':
        # Récupérer tous les produits
        produits = Produit.objects.all()
        produits_data = []
        
        # Préparer les données pour la réponse JSON
        for produit in produits:
            produits_data.append({
                'id': produit.id,
                'nom': produit.nom,
                'description': produit.description,
                'prix': str(produit.prix),
                'stock': produit.stock,
                'image': produit.image.url if produit.image else None,
                'grande_image': produit.grande_image.url if produit.grande_image else None,
                'categorie': produit.categorie.nom if produit.categorie else None,
                'souscategorie': produit.souscategorie.nom if produit.souscategorie else None,
                'qr_code': produit.qr_code.url if produit.qr_code else None,
                'numero_unique': produit.numero_unique,
                'adresse_produit': produit.adresse_produit,
                'lat': produit.lat,
                'long': produit.long,
                'poids': str(produit.poids) if produit.poids else None,
                'fournisseur': produit.fournisseur.nom if produit.fournisseur else None
            })
        # Retourner la liste des produits en JSON
        
        return JsonResponse(produits_data, safe=False)
    elif request.method == 'POST':
        try:
            # Récupérer les données envoyées dans le corps de la requête
            data = json.loads(request.body)

            # Récupérer les objets liés
            categorie = get_object_or_404(Categorie, id=data.get('categorie_id'))
            souscategorie = get_object_or_404(SousCategorie, id=data.get('souscategorie_id'))

            fournisseur = get_object_or_404(Fournisseur, id=data.get('fournisseur_id')) if data.get('fournisseur_id') else None

            # Créer le nouveau produit
            produit = Produit.objects.create(
                nom=data.get('nom'),
                description=data.get('description'),
                description_longue=data.get('description_longue'),
                prix=data.get('prix'),
                stock=data.get('stock'),
                image=None,  # L'image sera gérée différemment si envoyée
                grande_image=None,
                categorie=categorie,
                souscategorie=souscategorie,
                qr_code=None,
                numero_unique=data.get('numero_unique'),
                adresse_produit=data.get('adresse_produit'),
                lat=data.get('lat'),
                long=data.get('long'),
                poids=data.get('poids'),
                fournisseur=fournisseur
            )

            # Retourner les détails du produit nouvellement créé
            return JsonResponse({
                'message': 'Produit créé avec succès',
                'id': produit.id,
                'nom': produit.nom,
                'description': produit.description,
                'prix': str(produit.prix),
                'stock': produit.stock,
                'souscategorie':produit.souscategorie.nom,
                'categorie': produit.categorie.nom,
                'numero_unique': produit.numero_unique
            }, status=201)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Erreur lors de la création du produit'}, status=400)

    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@csrf_exempt
def produit_detail(request, numero_unique):
    produit = get_object_or_404(Produit, numero_unique=numero_unique)

    if request.method == 'GET':
        # Retourner les détails du produit
        data = {
             'id': produit.id,
                'nom': produit.nom,
                'description': produit.description,
                'prix': str(produit.prix),
                'stock': produit.stock,
                'image': produit.image.url if produit.image else None,
                'grande_image': produit.grande_image.url if produit.grande_image else None,
                'categorie': produit.categorie.nom if produit.categorie else None,
                'souscategorie': produit.souscategorie.nom if produit.souscategorie else None,
                'qr_code': produit.qr_code.url if produit.qr_code else None,
                'numero_unique': produit.numero_unique,
                'adresse_produit': produit.adresse_produit,
                'lat': produit.lat,
                'long': produit.long,
                'poids': str(produit.poids) if produit.poids else None,
                'fournisseur': produit.fournisseur.nom if produit.fournisseur else None
        }
        return JsonResponse(data)

    elif request.method == 'PATCH':
        # Mettre à jour le produit
        try:
            data = json.loads(request.body)
            updated_fields = []  # Pour garder une trace des champs mis à jour

            if 'prix' in data:
                produit.prix = data['prix']
                updated_fields.append('prix')
            if 'stock' in data:
                produit.stock = data['stock']
                updated_fields.append('stock')

            produit.save()

            return JsonResponse({'message': 'Produit mis à jour avec succès.', 'updated_fields': updated_fields})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide.'}, status=400)

    elif request.method == 'DELETE':
        # Supprimer le produit
        produit.delete()
        return JsonResponse({'message': 'Produit supprimé avec succès.'})

    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
def ajouter_produit_via_qr_code(request, numero_unique):
    # Récupérer le produit basé sur le numero_unique
    produit = get_object_or_404(Produit, numero_unique=numero_unique)

    # Vérifier si l'utilisateur est authentifié
    if request.user.is_anonymous:
        return JsonResponse({'detail': 'Veuillez vous connecter.'}, status=403)  # 403 Forbidden

 # Vérifier si l'utilisateur est le fournisseur associé au produit
    if produit.fournisseur.user != request.user:
        return JsonResponse({'detail': 'Permission refusée.'}, status=403)  # 403 Forbidden

    # Ajouter le produit au stock
    produit.stock += 1
    produit.save()

    # Retourner la réponse JSON
    return JsonResponse({
        'detail': f"Produit '{produit.nom}' ajouté avec succès.",
        'stock': produit.stock
    }, status=200)  # 200 OK



@csrf_exempt
@client_login_required
def update_product_quantity(request, numero_unique):
    try:
        produit = get_object_or_404(Produit, numero_unique=numero_unique)
        data = json.loads(request.body)
        quantite_a_retirer = data.get('quantite')

        if quantite_a_retirer is None:
            return JsonResponse({'error': 'Quantité non spécifiée.'}, status=400)

        if produit.stock < quantite_a_retirer:
            return JsonResponse({'error': 'Stock insuffisant.'}, status=400)

        # Mise à jour du stock
        produit.stock -= quantite_a_retirer
        produit.save()

        return JsonResponse({'message': 'Quantité mise à jour avec succès.'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Format JSON invalide.'}, status=400)
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erreur lors de la mise à jour du produit: {e}'}, status=500)
