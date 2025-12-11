"""
Commande Django pour générer automatiquement des mots de passe pour tous les fournisseurs
Usage: python manage.py generer_passwords_fournisseurs
"""

from django.core.management.base import BaseCommand
from fournisseur.models import Fournisseur


class Command(BaseCommand):
    help = 'Génère automatiquement le mot de passe "123" pour tous les fournisseurs (développement)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tous',
            action='store_true',
            help='Régénérer les mots de passe même pour ceux qui en ont déjà un',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email d\'un fournisseur spécifique (optionnel)',
        )

    def handle(self, *args, **options):
        regenerer_tous = options['tous']
        email_specifique = options.get('email')

        # Mot de passe de développement
        password_dev = "123"

        self.stdout.write(
            self.style.WARNING('🔐 Génération de mots de passe pour les fournisseurs...\n')
        )

        # Filtrer les fournisseurs
        if email_specifique:
            try:
                fournisseurs = [Fournisseur.objects.get(email=email_specifique)]
            except Fournisseur.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Aucun fournisseur trouvé avec l\'email: {email_specifique}')
                )
                return
        else:
            fournisseurs = Fournisseur.objects.all()

        resultats = []
        compteur = 0

        for fournisseur in fournisseurs:
            # Vérifier si le fournisseur a déjà un mot de passe
            a_deja_password = bool(fournisseur.password)

            if a_deja_password and not regenerer_tous:
                self.stdout.write(
                    self.style.WARNING(
                        f'⏭️  {fournisseur.prenom} {fournisseur.nom} ({fournisseur.email}) - '
                        f'A déjà un mot de passe (utilisez --tous pour régénérer)'
                    )
                )
                continue

            # Définir le mot de passe
            fournisseur.set_password(password_dev)
            fournisseur.save()

            compteur += 1

            # Stocker les résultats
            resultats.append({
                'nom': f'{fournisseur.prenom} {fournisseur.nom}',
                'email': fournisseur.email,
                'username': f'fournisseur_{fournisseur.pk}',
                'regenere': a_deja_password
            })

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {fournisseur.prenom} {fournisseur.nom} ({fournisseur.email})'
                )
            )

        # Afficher le récapitulatif
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 {compteur} mot(s) de passe généré(s) avec succès!\n')
        )
        self.stdout.write('=' * 80 + '\n')

        if resultats:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  MODE DÉVELOPPEMENT: Mot de passe = "123" pour tous les fournisseurs\n'
                )
            )
            self.stdout.write('📋 RÉCAPITULATIF:\n')
            self.stdout.write('-' * 80 + '\n')

            for r in resultats:
                statut = '(RÉGÉNÉRÉ)' if r['regenere'] else '(NOUVEAU)'
                self.stdout.write(
                    f"👤 {r['nom']:<30} {statut}\n"
                    f"   📧 Email:    {r['email']}\n"
                    f"   👤 Username: {r['username']}\n"
                    f"   🔒 Password: 123\n"
                    f"   🌐 Connexion: http://localhost:8007/login/\n"
                    f"{'-' * 80}\n"
                )

            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  ATTENTION: En production, utilisez des mots de passe sécurisés!\n'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Aucun mot de passe n\'a été généré. '
                    'Utilisez --tous pour régénérer les mots de passe existants.\n'
                )
            )
