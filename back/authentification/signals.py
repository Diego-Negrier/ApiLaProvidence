

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from produits.models import Fournisseur

@receiver(post_save, sender=User)
def create_fournisseur(sender, instance, created, **kwargs):
    # Si l'utilisateur vient d'être créé (pas une mise à jour)
    if created:
        # Créer un fournisseur associé à l'utilisateur
        Fournisseur.objects.create(user=instance)