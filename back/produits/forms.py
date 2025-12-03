from django import forms
from .models import Produit,StatutProduit,Fournisseur,Logo



class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = [
            'nom', 'prenom', 'metier', 'contact', 'tel', 
            'adresse', 'description', 'pays', 'ville', 
            'latitude', 'longitude', 'type_production', 'experience_annees',
            'certifications', 'engagement_ecologique', 'conditions_travail',
            'objectifs_durables', 'produits_principaux', 'calendrier_production',
            'saisonnalite_respectee', 'temoignages_clients', 'impact_local', 'photo'
        ]

class ProduitForm(forms.ModelForm):
    # Ajout des champs image et grande_image avec widget personnalisé
    logos = forms.ModelMultipleChoiceField(
        queryset=Logo.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False  # Rendre le choix facultatif
    )

    image = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input'}))
    grande_image = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input'}))

    class Meta:
        model = Produit
        fields = ['nom','numero_unique','cycle_fabrication','description_longue','preparation','origine', 'date_recolte','description','souscategorie', 'prix', 'stock'
                  , 'image', 'grande_image', 'categorie', 'adresse_produit'
                  , 'lat', 'long', 'poids', 'fournisseur','logos']  # Champs à afficher
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'custom-file-input', 'placeholder': 'Image principale'}),
            'grande_image': forms.ClearableFileInput(attrs={'class': 'custom-file-input', 'placeholder': 'Grande Image'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProduitForm, self).__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Nom du produit'})
        self.fields['description'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Description'})
        self.fields['prix'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Prix'})
        self.fields['stock'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Stock'})
        self.fields['image'].widget.attrs.update({'class': 'custom-file-input', 'placeholder': 'Image principale'})
        self.fields['grande_image'].widget.attrs.update({'class': 'custom-file-input', 'placeholder': 'Grande Image'})
        self.fields['categorie'].widget.attrs.update({'class': 'form-input'})
        self.fields['souscategorie'].widget.attrs.update({'class': 'form-input'})

        self.fields['adresse_produit'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Adresse du produit'})
        self.fields['lat'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Latitude'})
        self.fields['long'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Longitude'})
        self.fields['poids'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Poids'})
        self.fields['fournisseur'].widget.attrs.update({'class': 'form-input'})
        self.fields['logos'].widget.attrs.update({'class': 'form-input'})  # Ajout de la classe pour le champ logos
        self.fields['cycle_fabrication'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Cycle de fabrication'}) 
        self.fields['preparation'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Préparation'})  # Ajout de la classe pour le champ logos
        self.fields['origine'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Origin'})  # Ajout de la classe pour le champ logos
        self.fields['date_recolte'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Date Recolte'})  # Ajout de la classe pour le champ logos
        self.fields['description_longue'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Desctiption Longue'})  # Ajout de la classe pour le champ logos
        self.fields['numero_unique'].widget.attrs['disabled'] = True


    




class StatutProduitForm(forms.Form):
    produit_id = forms.IntegerField(widget=forms.HiddenInput())  # Champ caché pour l'ID du produit
    statut = forms.ChoiceField(
        choices=StatutProduit.choices,  # Utilisation correcte des choix définis dans StatutProduit
        widget=forms.Select,
    )