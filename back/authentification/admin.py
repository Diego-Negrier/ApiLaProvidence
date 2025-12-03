from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from produits.models import Fournisseur

class UserAdminCustom(UserAdmin):
    def save_model(self, request, obj, form, change):
        # Sauvegarder l'utilisateur
        super().save_model(request, obj, form, change)

        # Si un utilisateur est créé, créer automatiquement un fournisseur
        if not change:  # C'est un nouvel utilisateur
            Fournisseur.objects.get_or_create(user=obj)

# Enregistrer la personnalisation du UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
