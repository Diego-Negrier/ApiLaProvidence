# 🏛️ Page d'accueil Luxe - La Providence

## 📋 Vue d'ensemble

J'ai créé une nouvelle page d'accueil moderne et luxueuse qui met en valeur :
- ✅ **Les catégories hiérarchiques** (Catégorie > Sous-catégorie > Sous-sous-catégorie)
- ✅ **Les fournisseurs locaux** avec une carte interactive
- ✅ **Les produits nouveautés** et **promotions**
- ✅ **Un design premium** inspiré du luxe et du terroir local

---

## 🎨 Caractéristiques principales

### 1. Hero Section avec Statistiques
- Vidéo de fond (réutilise votre vidéo `HomeLaProvidence.mp4`)
- Titre majestueux avec effets lumineux
- **Statistiques en temps réel** :
  - Nombre total de produits
  - Nombre de producteurs
  - Nombre de catégories

### 2. Section Catégories Hiérarchiques
- **Grille responsive** adaptable (1 à 3 colonnes selon l'écran)
- **Cartes élégantes** avec :
  - Image ou icône de la catégorie
  - Nom et nombre de produits
  - Liste des sous-catégories (4 premières + compteur)
  - Bouton "Explorer" avec animation
- **Effet hover** : Élévation 3D et bordure dorée

### 3. Carte Interactive des Fournisseurs
- **Carte Leaflet** affichant les fournisseurs français
- **Marqueurs personnalisés** avec icône tracteur
- **Liste latérale** des fournisseurs avec :
  - Avatar ou initiales
  - Nom, métier, ville
  - Bouton pour voir le profil
- **Interaction** : Clic sur un marqueur ouvre une popup avec infos

### 4. Carrousels de Produits
- **Nouveautés** : 6 derniers produits ajoutés
- **Promotions** : 6 produits en promo avec badge réduction
- **Design** : Cartes produits avec image, prix, catégorie

### 5. Call to Action Final
- Design impactant sur fond sombre
- 2 boutons principaux :
  - "Découvrir les produits"
  - "Rencontrer les producteurs"

---

## 🚀 Installation et activation

### Étape 1 : Vérifier les dépendances

Assurez-vous que le modèle `Fournisseur` a les champs suivants :
```python
class Fournisseur(models.Model):
    # ...
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # ...
```

Si ce n'est pas le cas, ajoutez-les et faites une migration :
```bash
python manage.py makemigrations
python manage.py migrate
```

### Étape 2 : Activer la nouvelle page

**Option A : Remplacer l'ancienne page**

Renommez les fichiers :
```bash
cd web/templates
mv Home.html HomeOld.html
mv HomeNew.html Home.html
```

**Option B : Tester en parallèle**

Modifiez `urls.py` pour avoir deux pages :
```python
urlpatterns = [
    path('', home_view, name='home'),  # Ancienne
    path('new/', home_new_view, name='home_new'),  # Nouvelle
]
```

### Étape 3 : Vérifier les assets

Assurez-vous que la vidéo de fond existe :
```
static/image/HomeLaProvidence.mp4
```

---

## 🎨 Personnalisation

### Couleurs

Les couleurs sont définies en CSS avec des variables :
```css
:root {
    --color-gold: #c9a961;           /* Or */
    --color-dark-gold: #a68840;      /* Or foncé */
    --color-deep-blue: #1e3a5f;     /* Bleu profond */
    --color-cream: #f8f6f0;          /* Crème */
    --color-light-cream: #faf8f2;   /* Crème clair */
    --color-brown: #2c2416;          /* Marron */
}
```

Pour changer la palette, modifiez ces valeurs.

### Nombre d'éléments affichés

Dans `Home/views.py`, modifiez les limites :
```python
categories = Categorie.objects.filter(...)[:6]  # ← Changer 6
fournisseurs = Fournisseur.objects.filter(...)[:12]  # ← Changer 12
produits_nouveautes = Produit.objects.filter(...)[:6]  # ← Changer 6
```

### Style de la carte

Pour changer le style de la carte Leaflet, modifiez l'URL de la tuile :
```javascript
// Style actuel : Voyager (élégant)
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', ...)

// Alternatives :
// Style vintage
'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png'

// Style sombre (luxe)
'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'

// Style clair
'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
```

---

## 🗺️ Configuration de la carte

### Ajouter les coordonnées des fournisseurs

Pour que les fournisseurs apparaissent à leur vraie position :

1. **Via l'admin Django** :
   - Aller sur `/admin/fournisseur/fournisseur/`
   - Éditer un fournisseur
   - Remplir `latitude` et `longitude`

2. **Automatiquement via géocodage** :
   Créez un script de géocodage :
   ```python
   # fournisseur/management/commands/geocode_fournisseurs.py
   from django.core.management.base import BaseCommand
   from fournisseur.models import Fournisseur
   import requests

   class Command(BaseCommand):
       def handle(self, *args, **options):
           for f in Fournisseur.objects.filter(latitude__isnull=True):
               adresse = f"{f.adresse}, {f.ville}, {f.code_postal}, France"
               response = requests.get(
                   'https://nominatim.openstreetmap.org/search',
                   params={'q': adresse, 'format': 'json'}
               )
               if response.json():
                   data = response.json()[0]
                   f.latitude = float(data['lat'])
                   f.longitude = float(data['lon'])
                   f.save()
                   print(f"✓ {f.nom} géocodé")
   ```

   Puis exécuter :
   ```bash
   python manage.py geocode_fournisseurs
   ```

### Carte sans coordonnées

Si les fournisseurs n'ont pas de coordonnées, ils sont placés **aléatoirement en France** pour démonstration. C'est géré automatiquement dans le code JavaScript.

---

## 📱 Responsive Design

La page est entièrement responsive :

- **Desktop (>1024px)** : Grille 3 colonnes, carte à côté de la liste
- **Tablet (768-1024px)** : Grille 2 colonnes, carte empilée
- **Mobile (<768px)** : Grille 1 colonne, navigation verticale

---

## 🔧 Dépannage

### Problème : La carte ne s'affiche pas

1. Vérifiez que Leaflet est chargé :
   ```html
   <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
   <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
   ```

2. Vérifiez la console du navigateur (F12) pour les erreurs JavaScript

3. Assurez-vous que `#fournisseurs-map` existe dans le DOM

### Problème : Les catégories ne s'affichent pas

1. Vérifiez qu'il y a des catégories actives :
   ```python
   python manage.py shell
   >>> from produits.models import Categorie
   >>> Categorie.objects.filter(est_active=True).count()
   ```

2. Si 0, créez des catégories via l'admin ou générez-les :
   ```bash
   python manage.py generer_produits --nombre=10
   ```

### Problème : La vidéo ne se charge pas

1. Vérifiez que le fichier existe :
   ```
   static/image/HomeLaProvidence.mp4
   ```

2. Si absent, la page fonctionnera quand même (fond noir)

3. Remplacez par une image de fond :
   ```css
   .video-background {
       background: url('/static/image/hero-background.jpg') center/cover;
   }
   ```

---

## 🎯 Prochaines améliorations possibles

### Fonctionnalités avancées

1. **Recherche en temps réel** dans les catégories
2. **Filtres** par région, label bio, prix
3. **Animation** d'entrée au scroll (AOS.js)
4. **Carrousel automatique** des produits (Swiper.js)
5. **Mode sombre** pour l'interface

### Intégration API

1. **Météo locale** pour chaque fournisseur
2. **Événements** locaux (marchés, foires)
3. **Actualités** du blog

### SEO

1. Ajouter des balises meta dynamiques
2. Schema.org pour les produits
3. Sitemap XML

---

## 📚 Bibliothèques utilisées

- **Leaflet 1.9.4** : Carte interactive
  - Documentation : https://leafletjs.com/
- **Font Awesome** : Icônes
  - Déjà inclus dans Base.html
- **CSS Grid & Flexbox** : Layout responsive

---

## 🎨 Palette de couleurs

| Couleur | Hex | Usage |
|---------|-----|-------|
| Or | `#c9a961` | Accents, boutons, badges |
| Or foncé | `#a68840` | Hover, bordures |
| Bleu profond | `#1e3a5f` | Titres, fonds sombres |
| Crème | `#f8f6f0` | Fonds clairs, cartes |
| Crème clair | `#faf8f2` | Backgrounds alternatifs |
| Marron | `#2c2416` | Textes foncés, overlay |

---

## ✨ Captures d'écran

### Hero Section
![Hero](docs/screenshots/hero.png)

### Catégories
![Categories](docs/screenshots/categories.png)

### Carte Fournisseurs
![Map](docs/screenshots/map.png)

---

## 📞 Support

Pour toute question ou personnalisation :
1. Consultez ce README
2. Vérifiez les commentaires dans le code
3. Testez les exemples fournis

---

## 🎉 Résumé

Vous disposez maintenant d'une page d'accueil :
- ✅ Moderne et luxueuse
- ✅ Affichant les catégories hiérarchiques
- ✅ Avec carte interactive des fournisseurs
- ✅ Incluant nouveautés et promotions
- ✅ Responsive et performante
- ✅ Facile à personnaliser

La page utilise le même fond vidéo que l'ancienne mais avec une structure complètement repensée pour mettre en valeur vos produits et vos producteurs locaux !
