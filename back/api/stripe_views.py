"""
Vues API pour gérer les paiements Stripe
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db import transaction
import json

from utils.stripe_service import StripeService
from paniers.models import Panier
from commandes.models import Commande
from clients.models import Client


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_payment_intent(request, pk_client):
    """
    Crée un PaymentIntent Stripe pour le panier du client
    POST /api/<pk_client>/paiement/creer-intent/

    Body (optionnel):
    {
        "montant": 150.00,  // Optionnel, si absent utilise le total du panier
        "devise": "eur"     // Optionnel, par défaut EUR
    }
    """
    try:
        # Vérifier que le client existe et correspond à l'utilisateur authentifié
        client = Client.objects.get(pk=pk_client)

        if request.user.pk != client.pk:
            return Response(
                {'error': 'Vous ne pouvez pas créer un paiement pour un autre client'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Récupérer le panier actif du client
        panier = Panier.objects.filter(client=client, statut='actif').first()

        if not panier:
            return Response(
                {'error': 'Aucun panier actif trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier que le panier n'est pas vide
        if panier.nombre_articles() == 0:
            return Response(
                {'error': 'Le panier est vide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer le montant (utiliser celui fourni ou calculer depuis le panier)
        montant = request.data.get('montant')
        if montant is None:
            montant = panier.calculer_total_ttc()  # Utiliser le TTC pour le paiement

        devise = request.data.get('devise', 'eur')

        # Créer le PaymentIntent via le service Stripe
        result = StripeService.creer_payment_intent(
            montant=montant,
            devise=devise,
            metadata={
                'client_id': str(client.pk),
                'client_email': client.email,
                'panier_id': str(panier.pk),
                'nombre_articles': panier.nombre_articles()
            },
            client_email=client.email
        )

        if not result.get('success'):
            return Response(
                {
                    'error': 'Erreur lors de la création du paiement',
                    'details': result.get('error')
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Retourner le client_secret pour le frontend
        return Response({
            'success': True,
            'client_secret': result['client_secret'],
            'payment_intent_id': result['payment_intent_id'],
            'montant': float(result['amount']),
            'devise': result['currency']
        }, status=status.HTTP_201_CREATED)

    except Client.DoesNotExist:
        return Response(
            {'error': 'Client non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirmer_paiement(request, pk_client):
    """
    Confirme le paiement et crée la commande
    POST /api/<pk_client>/paiement/confirmer/

    Body:
    {
        "payment_intent_id": "pi_xxxxx",
        "livreur_id": 1,  // Optionnel
        "point_relais_id": 1  // Optionnel
    }
    """
    try:
        # Vérifier que le client existe et correspond à l'utilisateur authentifié
        client = Client.objects.get(pk=pk_client)

        if request.user.pk != client.pk:
            return Response(
                {'error': 'Accès non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )

        payment_intent_id = request.data.get('payment_intent_id')

        if not payment_intent_id:
            return Response(
                {'error': 'payment_intent_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier le statut du paiement auprès de Stripe
        result = StripeService.recuperer_payment_intent(payment_intent_id)

        if not result.get('success'):
            return Response(
                {
                    'error': 'Erreur lors de la vérification du paiement',
                    'details': result.get('error')
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Vérifier que le paiement a réussi
        if result['status'] != 'succeeded':
            return Response(
                {
                    'error': 'Le paiement n\'a pas été complété',
                    'status': result['status']
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Créer la commande à partir du panier
        with transaction.atomic():
            livreur_id = request.data.get('livreur_id')
            point_relais_id = request.data.get('point_relais_id')

            # Import ici pour éviter les imports circulaires
            from livraisons.models import Livreur, PointRelais

            livreur = None
            point_relais = None

            if livreur_id:
                livreur = Livreur.objects.get(pk=livreur_id)

            if point_relais_id:
                point_relais = PointRelais.objects.get(pk=point_relais_id)

            # Créer la commande depuis le panier
            commande, nouveau_panier = Commande.creer_depuis_panier(
                client=client,
                livreur=livreur,
                point_relais=point_relais
            )

            # Stocker l'ID du payment intent dans les métadonnées de la commande
            # (Vous pourriez ajouter un champ payment_intent_id au modèle Commande si nécessaire)

            return Response({
                'success': True,
                'commande_id': commande.pk,
                'numero_commande': commande.numero_commande,
                'montant': float(commande.total),
                'payment_status': result['status']
            }, status=status.HTTP_201_CREATED)

    except Client.DoesNotExist:
        return Response(
            {'error': 'Client non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def recuperer_cle_publique(request):
    """
    Retourne la clé publique Stripe
    GET /api/paiement/cle-publique/
    Note: Pas d'authentification requise car c'est une clé publique
    """
    return Response({
        'publishable_key': settings.STRIPE_PUBLIC_KEY
    })


@csrf_exempt
def stripe_webhook(request):
    """
    Gère les webhooks Stripe
    POST /api/paiement/webhook/

    Ce endpoint reçoit les événements de Stripe (paiement réussi, échoué, etc.)
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        return HttpResponse(status=400)

    # Vérifier la signature du webhook
    event = StripeService.verifier_webhook_signature(payload, sig_header)

    if event is None:
        return HttpResponse(status=400)

    # Traiter l'événement
    event_type = event['type']

    try:
        if event_type == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Traiter le paiement réussi
            print(f"✅ Paiement réussi : {payment_intent['id']}")

            # Vous pouvez ajouter ici une logique pour mettre à jour la commande
            # Par exemple, marquer la commande comme payée

        elif event_type == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Traiter l'échec du paiement
            print(f"❌ Paiement échoué : {payment_intent['id']}")

        elif event_type == 'charge.refunded':
            charge = event['data']['object']
            # Traiter le remboursement
            print(f"💰 Remboursement effectué : {charge['id']}")

        return HttpResponse(status=200)

    except Exception as e:
        print(f"Erreur webhook Stripe : {str(e)}")
        return HttpResponse(status=500)
