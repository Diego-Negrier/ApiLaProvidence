from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from produits.models import Produit
from paniers.models import Panier, LignePanier

class Command(BaseCommand):
    help = 'Configure les groupes et permissions pour LaProvidence'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌾 Configuration des groupes et permissions...')

        # Création des groupes
        admin_group, created = Group.objects.get_or_create(name='Administrateurs')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Groupe Administrateurs créé'))
        
        fournisseur_group, created = Group.objects.get_or_create(name='Fournisseurs')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Groupe Fournisseurs créé'))

        # === PERMISSIONS PANIER ===
        panier_ct = ContentType.objects.get_for_model(Panier)
        
        view_panier, _ = Permission.objects.get_or_create(
            codename='view_panier',
            content_type=panier_ct,
            defaults={'name': 'Can view panier'}
        )
        
        change_panier, _ = Permission.objects.get_or_create(
            codename='change_panier',
            content_type=panier_ct,
            defaults={'name': 'Can change panier'}
        )

        # === PERMISSIONS LIGNE PANIER ===
        ligne_panier_ct = ContentType.objects.get_for_model(LignePanier)
        
        view_ligne_panier, _ = Permission.objects.get_or_create(
            codename='view_lignepanier',
            content_type=ligne_panier_ct,
            defaults={'name': 'Can view ligne de panier'}
        )
        
        change_ligne_panier, _ = Permission.objects.get_or_create(
            codename='change_lignepanier',
            content_type=ligne_panier_ct,
            defaults={'name': 'Can change ligne de panier'}
        )

        # === PERMISSIONS PRODUIT ===
        produit_ct = ContentType.objects.get_for_model(Produit)
        
        view_produit, _ = Permission.objects.get_or_create(
            codename='view_produit',
            content_type=produit_ct,
            defaults={'name': 'Can view produit'}
        )
        
        add_produit, _ = Permission.objects.get_or_create(
            codename='add_produit',
            content_type=produit_ct,
            defaults={'name': 'Can add produit'}
        )
        
        change_produit, _ = Permission.objects.get_or_create(
            codename='change_produit',
            content_type=produit_ct,
            defaults={'name': 'Can change produit'}
        )
        
        delete_produit, _ = Permission.objects.get_or_create(
            codename='delete_produit',
            content_type=produit_ct,
            defaults={'name': 'Can delete produit'}
        )

        # === ASSIGNER PERMISSIONS ADMINISTRATEURS ===
        admin_group.permissions.add(
            view_produit, add_produit, change_produit, delete_produit,
            view_panier, change_panier,
            view_ligne_panier, change_ligne_panier
        )
        self.stdout.write(self.style.SUCCESS('✅ Permissions Administrateurs configurées'))

        # === ASSIGNER PERMISSIONS FOURNISSEURS ===
        fournisseur_group.permissions.add(
            view_produit, add_produit, change_produit,
            view_panier, view_ligne_panier
        )
        self.stdout.write(self.style.SUCCESS('✅ Permissions Fournisseurs configurées'))

        self.stdout.write(self.style.SUCCESS('🎉 Configuration terminée avec succès !'))
