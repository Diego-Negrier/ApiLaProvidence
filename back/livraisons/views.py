from django.shortcuts import render
from clients.utilis import client_login_required
from django.views.decorators.csrf import csrf_exempt
from paniers.models import  Panier
from clients.models import Client
from .models import Livreur, PointRelais
from geopy.distance import geodesic
from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404

# Create your views here.

##################################################################
##################### LIVRAISON #####################################
##################################################################



def calculer_poids_total(panier):
    """
    Calculer le poids total des produits dans le panier.
    panier : un objet Panier qui a des lignes avec des produits et des quantités.
    """
    poids_total = sum(ligne.produit.poids * ligne.quantite for ligne in panier.lignes.all())
    return poids_total
@csrf_exempt  # Vous pouvez vouloir gérer la sécurité CSRF d'une autre manière
@client_login_required
def view_livreurs(request):
    client = request.client

    # Récupérer le dernier panier actif du client (non associé à une commande)
    panier = Panier.objects.filter(client=client, commande__isnull=True).first()

    # Vérifier si un panier actif existe
    if not panier:
        return JsonResponse({'error': 'Aucun panier actif trouvé.'}, status=400)

    if request.method == 'GET':
        # Calculer le poids total du panier
        poids_total = panier.calculer_poids_total()        
        print(poids_total)

        livreurs = Livreur.objects.all()
        response_data = []

        for livreur in livreurs:
            # Calculer le prix de livraison en utilisant le poids total
            prix_livraison = livreur.calculer_prix_livraison(poids_total)  # Utiliser le poids total
            print(prix_livraison)
            response_data.append({
                'id': livreur.pk,
                'nom_entreprise': livreur.nom,
                'telephone': livreur.telephone,
                'prix_livraison': prix_livraison,  # Appeler la méthode pour obtenir le prix
                'type_service': livreur.type_service,
                'email': livreur.email,
                'adresse': livreur.adresse,
            })
        
        return JsonResponse(response_data, safe=False)

    else:
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt  # Vous pouvez vouloir gérer la sécurité CSRF d'une autre manière
@client_login_required
def points_relais_proches(request, client_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({"error": "Données invalides."}, status=400)

        # Vérifiez que les coordonnées sont fournies
        if latitude is None or longitude is None:
            return JsonResponse({"error": "Les coordonnées sont requises."}, status=400)

        # Récupérer le client
        client = get_object_or_404(Client, id=client_id)

        # Récupérer tous les points relais
        point_relais = PointRelais.objects.all()
        points_proches = []

        for point in point_relais:
            point_coords = (point.latitude, point.longitude)
            distance = geodesic((latitude, longitude), point_coords).km  # Calcule la distance en km

            if distance <= 10:  # Vérifier si la distance est inférieure ou égale à 10 km
                points_proches.append({
                    "id": point.pk,
                    "nom": point.nom,
                    "adresse": point.adresse,
                    "code_postal": point.code_postal,
                    "ville": point.ville,
                    "pays": point.pays,
                    "distance": distance  # Vous pouvez également inclure la distance
                })

        return JsonResponse(points_proches, safe=False)

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)

@csrf_exempt
@client_login_required
def point_relais_list(request):
    # Récupérer tous les points relais
    points_relais = PointRelais.objects.all().values('id', 'nom', 'adresse', 'code_postal', 'ville', 'pays')
    return JsonResponse(list(points_relais), safe=False)

