from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Client

@receiver(post_migrate)
def create_anonymous_user(sender, **kwargs):
    if not Client.objects.filter(username="anonymes").exists():
        Client.objects.create_user(
            pk=1000,  # ID spécifique
            username="anonymes",
            email="anonymes@example.com",  # Email générique
            password="",  # Mot de passe vide ou complexe
            is_active=True
        )
        print("Utilisateur par défaut 'anonymes' avec pk=1000 créé avec succès.")
    else:
        print("Utilisateur 'anonymes' existe déjà.")