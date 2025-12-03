from django.apps import AppConfig

class AuthentificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentification'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(self.create_groups, sender=self)

    @staticmethod
    def create_groups(sender, **kwargs):
        from django.contrib.auth.models import Group
        try:
            admin_group, created = Group.objects.get_or_create(name='Administrateurs')
            if created:
                print("✅ Groupe Administrateurs créé")
        except Exception as e:
            print(f"⚠️ Erreur création groupe: {e}")
