from django.shortcuts import render
from clients.utilis import client_login_required
from .models import Panier,Produit,LignePanier
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404

# Create your views here.
##################################################################
##################### PANIER #####################################
##################################################################


def get_or_create_panier_actif(client):
    """Récupère ou crée un panier actif pour le client."""
    return Panier.objects.get_or_create(client=client, statut='actif')

@csrf_exempt
@client_login_required
def view_cart(request):
    client = request.client

    # Récupérer ou créer un panier actif
    panier, _ = get_or_create_panier_actif(client)

    if request.method == 'GET':
        lignes_panier = panier.lignes.all()
        total_quantite = sum(ligne.quantite for ligne in lignes_panier if ligne.produit is not None)

        response_data = {
            'pk': panier.pk,
            'lignes': [
                {
                    'produit': ligne.produit.nom,
                    'prix': str(ligne.produit.prix.quantize(Decimal('0.01'))),
                    'quantite': ligne.quantite,
                    'image': ligne.produit.image.url if ligne.produit.image else None,
                    'numero_unique': ligne.produit.numero_unique,
                    'poids': ligne.produit.poids,
                    'tva': ligne.produit.taux_tva,
                    'ttc': ligne.produit.prix_ttc() ,
                    'stock': ligne.produit.stock,
                } for ligne in lignes_panier if ligne.produit is not None
            ],
            'session_token': client.session_token,
            'total_quantite': total_quantite
        }

        return JsonResponse(response_data)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            produit_id = data.get('produit')
            quantite = data.get('quantite', 1)

            if not produit_id:
                return JsonResponse({'error': 'Produit non spécifié.'}, status=400)

            produit = get_object_or_404(Produit, id=produit_id)

            if quantite <= 0:
                return JsonResponse({'error': 'Quantité invalide. Elle doit être supérieure à zéro.'}, status=400)

            if quantite > produit.stock:
                return JsonResponse({'error': f'Stock insuffisant. Il reste seulement {produit.stock} articles.'}, status=400)

            ligne_panier, created = LignePanier.objects.get_or_create(
                panier=panier,
                produit=produit,
                defaults={'quantite': quantite}
            )

            if not created:
                ligne_panier.quantite += quantite
                ligne_panier.save()

            return JsonResponse({
                'message': 'Produit ajouté au panier.',
                'produit': produit.nom,
                'quantite': ligne_panier.quantite,
                'total': str(panier.calculer_total())
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données invalides.'}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)

@csrf_exempt
@client_login_required
def add_to_cart(request, numero_unique):
    client = request.client
    produit = get_object_or_404(Produit, numero_unique=numero_unique)

    panier, _ = get_or_create_panier_actif(client)

    panier.ajouter_produit(produit)
    return JsonResponse({'message': 'Produit ajouté au panier.'}, status=200)

@csrf_exempt
@client_login_required
def subtract_to_cart(request, numero_unique):
    client = request.client
    produit = get_object_or_404(Produit, numero_unique=numero_unique)

    panier, _ = get_or_create_panier_actif(client)

    panier.enlever_produit(produit, quantite=1)
    return JsonResponse({'message': 'Quantité réduite pour ce produit.'}, status=200)

@csrf_exempt
@client_login_required
def supprimer_produit_panier(request, numero_unique):
    client = request.client
    produit = get_object_or_404(Produit, numero_unique=numero_unique)

    panier, _ = get_or_create_panier_actif(client)

    panier.supprimer_produit(produit)
    return JsonResponse({'message': 'Produit supprimé du panier.'}, status=200)

@csrf_exempt
@client_login_required
def clear_cart(request):
    client = request.client

    panier, _ = get_or_create_panier_actif(client)

    panier.vider_panier()
    return JsonResponse({'message': 'Panier vidé.'}, status=200)