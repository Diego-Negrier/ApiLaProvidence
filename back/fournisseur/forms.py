"""
Formulaires pour l'espace fournisseur
"""

from django import forms
from produits.models import Produit
from fournisseur.models import Fournisseur


class ProduitForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier un produit"""

    class Meta:
        model = Produit
        fields = [
            'nom',
            'description_courte',
            'description_longue',
            'prix_ht',
            'tva',
            'poids',
            'categorie',
            'souscategorie',
            'image_principale',
            'est_actif',
            'statut',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }),
            'description_courte': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description courte'
            }),
            'description_longue': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Description détaillée'
            }),
            'prix_ht': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'tva': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '20.00'
            }),
            'poids': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '0.000'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control'
            }),
            'souscategorie': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image_principale': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'est_actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nom': 'Nom du produit',
            'description_courte': 'Description courte',
            'description_longue': 'Description détaillée',
            'prix_ht': 'Prix HT (€)',
            'tva': 'TVA (%)',
            'poids': 'Poids (kg)',
            'categorie': 'Catégorie',
            'souscategorie': 'Sous-catégorie',
            'image_principale': 'Image du produit',
            'est_actif': 'Produit actif',
            'statut': 'Statut',
        }


class FournisseurProfilForm(forms.ModelForm):
    """Formulaire pour modifier le profil fournisseur"""

    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe actuel'
        }),
        label='Mot de passe actuel'
    )
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        }),
        label='Nouveau mot de passe'
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        }),
        label='Confirmer le mot de passe'
    )

    class Meta:
        model = Fournisseur
        fields = [
            'nom',
            'prenom',
            'email',
            'tel',
            'metier',
            'contact',
            'adresse',
            'code_postal',
            'ville',
            'pays',
            'description',
            'photo',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tel': forms.TextInput(attrs={'class': 'form-control'}),
            'metier': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Si un nouveau mot de passe est fourni
        if new_password or confirm_password:
            # Le mot de passe actuel est obligatoire
            if not current_password:
                raise forms.ValidationError("Vous devez fournir votre mot de passe actuel pour en définir un nouveau")

            # Les deux nouveaux mots de passe doivent correspondre
            if new_password != confirm_password:
                raise forms.ValidationError("Les nouveaux mots de passe ne correspondent pas")

        return cleaned_data
