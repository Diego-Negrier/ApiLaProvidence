from .models import (
                    Client)
import logging
from functools import wraps
from django.http import JsonResponse

logger = logging.getLogger(__name__)

##################################################################
##################### TOKEN CLIENT AUTORISED ###################################
##################################################################
def is_token_valid(token):
    try:
        # Assurez-vous de retirer "Bearer " du token s'il est présent
        token = token.split()[1] if token.startswith('Bearer ') else token
        client = Client.objects.get(session_token=token)

        # Vérifiez si le token est encore valide
        return client.is_token_valid()  # Implémentez cette méthode pour vérifier la validité
    except Client.DoesNotExist:
        return False

def get_client_from_token(token):
    try:
        # Retirez "Bearer " si nécessaire
        token = token.split()[1] if token.startswith('Bearer ') else token
        client = Client.objects.get(session_token=token)
        return client
    except Client.DoesNotExist:
        return None
    
def client_login_required(view_func):
    @wraps(view_func)  # Utiliser wraps pour conserver le nom et les docstrings de la fonction originale
    def _wrapped_view(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        
        if not token or not is_token_valid(token):
            return JsonResponse({'detail': 'Unauthorized'}, status=401)
        
        # Assurez-vous que `get_client_from_token` renvoie un client valide
        request.client = get_client_from_token(token)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view