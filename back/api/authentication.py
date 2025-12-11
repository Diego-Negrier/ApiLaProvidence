# authentication.py (dans votre app)
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from clients.models import Client
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class ClientTokenAuthentication(TokenAuthentication):
    """Authentication backend personnalisé utilisant session_token"""
    keyword = 'Token'  # Le mot-clé dans le header Authorization

    def authenticate_credentials(self, key):
        """Authentifier avec session_token du modèle Client"""
        logger.info(f"🔐 Tentative d'authentication avec token: {key[:8]}...")

        try:
            # Chercher le client par session_token
            client = Client.objects.get(session_token=key)
            logger.info(f"✅ Client trouvé: {client.email} (pk={client.pk})")
        except Client.DoesNotExist:
            logger.error(f"❌ Token invalide: {key[:8]}...")
            raise exceptions.AuthenticationFailed('Token invalide.')

        # Vérifier que le token n'a pas expiré
        if not client.is_token_valid():
            logger.error(f"❌ Token expiré pour {client.email}")
            raise exceptions.AuthenticationFailed('Token expiré.')

        logger.info(f"✅ Authentication réussie pour {client.email}")
        # Retourner le client comme utilisateur
        return (client, None)
