"""
Backend d'authentification personnalisé pour les fournisseurs
Permet aux fournisseurs de se connecter à l'admin avec leur email
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from clients.models import Client
from fournisseur.models import Fournisseur


class FournisseurAuthBackend(BaseBackend):
    """
    Backend d'authentification pour les fournisseurs
    Permet de se connecter avec email/password depuis le modèle Fournisseur
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un fournisseur

        Args:
            username: Email du fournisseur
            password: Mot de passe du fournisseur

        Returns:
            User Django associé au fournisseur ou None
        """
        try:
            # Chercher le fournisseur par email
            fournisseur = Fournisseur.objects.get(email=username)

            # Vérifier le mot de passe
            if fournisseur.check_password(password):
                # Récupérer ou créer un utilisateur Django associé
                user, created = User.objects.get_or_create(
                    username=f"fournisseur_{fournisseur.id}",
                    defaults={
                        'email': fournisseur.email,
                        'first_name': fournisseur.prenom,
                        'last_name': fournisseur.nom,
                        'is_staff': True,  # Permet l'accès à l'admin
                        'is_active': True,
                    }
                )

                # Si l'utilisateur existait déjà, mettre à jour ses infos
                if not created:
                    user.email = fournisseur.email
                    user.first_name = fournisseur.prenom
                    user.last_name = fournisseur.nom
                    user.is_staff = True
                    user.save()

                # Ajouter le fournisseur comme attribut pour y accéder plus tard
                user.fournisseur = fournisseur

                # Enregistrer la connexion
                # fournisseur.enregistrer_connexion()  # Désactivé: champ derniere_connexion n'existe pas

                return user

        except Fournisseur.DoesNotExist:
            return None

        return None

    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID
        """
        try:
            user = User.objects.get(pk=user_id)
            # Attacher le fournisseur si c'est un compte fournisseur
            if user.username.startswith('fournisseur_'):
                fournisseur_id = int(user.username.split('_')[1])
                user.fournisseur = Fournisseur.objects.get(id=fournisseur_id)
            return user
        except (User.DoesNotExist, Fournisseur.DoesNotExist, ValueError, IndexError):
            return None
