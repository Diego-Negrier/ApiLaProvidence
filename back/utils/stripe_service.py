"""
Service Stripe pour gérer les paiements
"""
import stripe
from django.conf import settings
from decimal import Decimal
from typing import Dict, Any, Optional

# Configurer la clé API Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service pour gérer les paiements Stripe"""

    @staticmethod
    def creer_payment_intent(
        montant: Decimal,
        devise: str = 'eur',
        metadata: Optional[Dict[str, Any]] = None,
        client_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crée un PaymentIntent Stripe

        Args:
            montant: Montant en euros (sera converti en centimes)
            devise: Devise (par défaut 'eur')
            metadata: Métadonnées additionnelles
            client_email: Email du client

        Returns:
            Dict contenant le PaymentIntent et le client_secret
        """
        try:
            # Convertir le montant en centimes (Stripe utilise les plus petites unités)
            montant_centimes = int(montant * 100)

            # Préparer les paramètres
            params = {
                'amount': montant_centimes,
                'currency': devise,
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }

            # Ajouter les métadonnées si fournies
            if metadata:
                params['metadata'] = metadata

            # Ajouter l'email du client si fourni
            if client_email:
                params['receipt_email'] = client_email

            # Créer le PaymentIntent
            payment_intent = stripe.PaymentIntent.create(**params)

            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': montant,
                'currency': devise,
                'status': payment_intent.status
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    @staticmethod
    def recuperer_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Récupère un PaymentIntent existant

        Args:
            payment_intent_id: ID du PaymentIntent

        Returns:
            Dict contenant les informations du PaymentIntent
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'amount': payment_intent.amount / 100,  # Reconvertir en euros
                'currency': payment_intent.currency,
                'status': payment_intent.status,
                'metadata': payment_intent.metadata
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    @staticmethod
    def confirmer_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirme un PaymentIntent

        Args:
            payment_intent_id: ID du PaymentIntent

        Returns:
            Dict contenant le résultat de la confirmation
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)

            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'status': payment_intent.status
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    @staticmethod
    def annuler_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Annule un PaymentIntent

        Args:
            payment_intent_id: ID du PaymentIntent

        Returns:
            Dict contenant le résultat de l'annulation
        """
        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)

            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'status': payment_intent.status
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    @staticmethod
    def verifier_webhook_signature(payload: bytes, sig_header: str) -> Optional[Any]:
        """
        Vérifie la signature d'un webhook Stripe

        Args:
            payload: Corps de la requête (bytes)
            sig_header: En-tête Stripe-Signature

        Returns:
            Event Stripe si la signature est valide, None sinon
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError:
            # Payload invalide
            return None
        except stripe.error.SignatureVerificationError:
            # Signature invalide
            return None

    @staticmethod
    def creer_remboursement(
        payment_intent_id: str,
        montant: Optional[Decimal] = None,
        raison: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crée un remboursement pour un PaymentIntent

        Args:
            payment_intent_id: ID du PaymentIntent
            montant: Montant à rembourser (None = remboursement total)
            raison: Raison du remboursement

        Returns:
            Dict contenant les informations du remboursement
        """
        try:
            params = {
                'payment_intent': payment_intent_id
            }

            if montant is not None:
                params['amount'] = int(montant * 100)

            if raison:
                params['reason'] = raison

            refund = stripe.Refund.create(**params)

            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
