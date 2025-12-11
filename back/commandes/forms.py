from django import forms
from .models import Commande, StatutCommande


class StatutCommandeForm(forms.Form):
    commande_id = forms.IntegerField(widget=forms.HiddenInput())  # Champ caché pour l'ID de la commande

    statut = forms.ChoiceField(
        choices=StatutCommande.choices,  # Utilisation correcte de StatutProduit.choices
        widget=forms.Select,
    )