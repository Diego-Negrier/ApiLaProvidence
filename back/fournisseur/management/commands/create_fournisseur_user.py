"""
Commande Django pour créer un compte fournisseur
Usage: python manage.py create_fournisseur_user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from fournisseur.models import Fournisseur


class Command(BaseCommand):
    help = 'Crée un compte utilisateur pour un fournisseur existant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email du fournisseur',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Mot de passe pour le fournisseur',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')

        # Mode interactif si pas d'arguments
        if not email:
            email = input('📧 Email du fournisseur: ')

        if not password:
            password = input('🔒 Mot de passe: ')

        try:
            # Chercher le fournisseur
            fournisseur = Fournisseur.objects.get(email=email)

            # Définir le mot de passe
            fournisseur.set_password(password)
            fournisseur.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Compte fournisseur créé avec succès pour {fournisseur.nom} {fournisseur.prenom}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'🌐 Le fournisseur peut maintenant se connecter sur: /fournisseur-admin/'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'   Email: {email}'
                )
            )

        except Fournisseur.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Aucun fournisseur trouvé avec l\'email: {email}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Créez d\'abord le fournisseur dans l\'admin principal.'
                )
            )
