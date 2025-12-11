<<<<<<< HEAD
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
=======
# clients/signals.py

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from .models import Client

@receiver(post_migrate)
def create_anonymous_client(sender, **kwargs):
    """
    Crée automatiquement un client anonyme après les migrations
    """
    if sender.name == 'clients':
        
        # Vérifier si le client anonyme existe déjà
        if not Client.objects.filter(username='anonymeClient').exists():
            try:
                # ✅ Créer avec un mot de passe inutilisable
                Client.objects.create(
                    username='anonymeClient',
                    email='anonyme@laprovidence.com',
                    password=make_password(None),  # ✅ Mot de passe inutilisable
                    nom='Anonyme',
                    prenom='Visiteur',
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                )
                print("✅ Client anonyme créé avec succès")
            except Exception as e:
                print(f"❌ Erreur : {e}")
                import traceback
                traceback.print_exc()
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
