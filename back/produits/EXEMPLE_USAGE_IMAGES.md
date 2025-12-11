# Exemple d'utilisation des images de produits

## Dans les vues Django

### Récupérer toutes les images d'un produit

```python
from produits.models import Produit

# Récupérer un produit
produit = Produit.objects.get(slug='mon-produit')

# Méthode 1: Récupérer uniquement les URLs
toutes_les_urls = produit.get_toutes_images()
# Retourne: ['url/image1.jpg', 'url/image2.jpg', ...]

# Méthode 2: Récupérer les objets ImageProduit complets
images_additionnelles = produit.get_images_additionnelles()
# Retourne un QuerySet d'objets ImageProduit

# Méthode 3: Compter le nombre total d'images
nombre_images = produit.get_nombre_images()
# Retourne: 5 (par exemple)

# Méthode 4: Récupérer l'image principale (si marquée dans ImageProduit)
image_principale_obj = produit.get_image_principale_obj()
```

## Dans les templates Django

### Exemple 1: Afficher l'image principale

```html
<!-- ProduitDetail.html -->
{% if produit.image_principale %}
    <img src="{{ produit.image_principale.url }}"
         alt="{{ produit.nom }}"
         class="img-fluid">
{% else %}
    <img src="{% static 'images/no-image.jpg' %}"
         alt="Pas d'image"
         class="img-fluid">
{% endif %}
```

### Exemple 2: Galerie d'images additionnelles

```html
<!-- ProduitDetail.html -->
<div class="gallery">
    <h3>Photos du produit ({{ nombre_images }} images)</h3>

    <!-- Image principale -->
    {% if produit.image_principale %}
    <div class="gallery-item">
        <img src="{{ produit.image_principale.url }}"
             alt="{{ produit.nom }}"
             class="img-thumbnail">
        <p class="text-muted">Image principale</p>
    </div>
    {% endif %}

    <!-- Images additionnelles -->
    {% for image in images_additionnelles %}
    <div class="gallery-item">
        <img src="{{ image.image.url }}"
             alt="{{ image.legende|default:produit.nom }}"
             class="img-thumbnail">
        {% if image.legende %}
        <p class="text-muted">{{ image.legende }}</p>
        {% endif %}
        {% if image.est_principale %}
        <span class="badge badge-primary">Principale</span>
        {% endif %}
    </div>
    {% endfor %}
</div>
```

### Exemple 3: Carrousel Bootstrap

```html
<!-- ProduitDetail.html - Carrousel avec toutes les images -->
<div id="carouselProduit" class="carousel slide" data-ride="carousel">
    <div class="carousel-inner">
        <!-- Image principale -->
        {% if produit.image_principale %}
        <div class="carousel-item active">
            <img src="{{ produit.image_principale.url }}"
                 class="d-block w-100"
                 alt="{{ produit.nom }}">
        </div>
        {% endif %}

        <!-- Images additionnelles -->
        {% for image in images_additionnelles %}
        <div class="carousel-item {% if not produit.image_principale and forloop.first %}active{% endif %}">
            <img src="{{ image.image.url }}"
                 class="d-block w-100"
                 alt="{{ image.legende|default:produit.nom }}">
            {% if image.legende %}
            <div class="carousel-caption d-none d-md-block">
                <p>{{ image.legende }}</p>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <!-- Contrôles -->
    <a class="carousel-control-prev" href="#carouselProduit" role="button" data-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="sr-only">Précédent</span>
    </a>
    <a class="carousel-control-next" href="#carouselProduit" role="button" data-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="sr-only">Suivant</span>
    </a>
</div>
```

### Exemple 4: Utiliser simplement les URLs

```html
<!-- ProduitDetail.html - Liste simple d'URLs -->
{% for url in toutes_images_urls %}
    <img src="{{ url }}" alt="{{ produit.nom }}" class="img-thumbnail m-2" style="max-width: 150px;">
{% endfor %}
```

## Dans l'API (Django REST Framework)

### Créer un serializer

```python
# produits/serializers.py
from rest_framework import serializers
from .models import Produit, ImageProduit

class ImageProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduit
        fields = ['id', 'image', 'legende', 'ordre', 'est_principale']

class ProduitSerializer(serializers.ModelSerializer):
    images_additionnelles = ImageProduitSerializer(source='images', many=True, read_only=True)
    toutes_images = serializers.SerializerMethodField()
    nombre_images = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'slug', 'image_principale',
            'images_additionnelles', 'toutes_images', 'nombre_images',
            # ... autres champs
        ]

    def get_toutes_images(self, obj):
        return obj.get_toutes_images()

    def get_nombre_images(self, obj):
        return obj.get_nombre_images()
```

### Exemple de réponse API JSON

```json
{
    "id": 1,
    "nom": "Pommes bio #1",
    "slug": "pommes-bio-1",
    "image_principale": "/media/produits/pommes-bio/2024-1209-A7B3/image.jpg",
    "nombre_images": 4,
    "toutes_images": [
        "/media/produits/pommes-bio/2024-1209-A7B3/image.jpg",
        "/media/produits/pommes-bio/2024-1209-A7B3/produit_1_add_0_1234.jpg",
        "/media/produits/pommes-bio/2024-1209-A7B3/produit_1_add_1_5678.jpg",
        "/media/produits/pommes-bio/2024-1209-A7B3/produit_1_add_2_9012.jpg"
    ],
    "images_additionnelles": [
        {
            "id": 1,
            "image": "/media/produits/pommes-bio/2024-1209-A7B3/produit_1_add_0_1234.jpg",
            "legende": "Vue détaillée du produit",
            "ordre": 1,
            "est_principale": false
        },
        {
            "id": 2,
            "image": "/media/produits/pommes-bio/2024-1209-A7B3/produit_1_add_1_5678.jpg",
            "legende": "Présentation du produit",
            "ordre": 2,
            "est_principale": false
        }
    ]
}
```

## Shell Django - Exemples pratiques

```python
# Démarrer le shell
python manage.py shell

# Importer les modèles
from produits.models import Produit, ImageProduit

# Récupérer un produit
produit = Produit.objects.first()

# Afficher toutes les URLs d'images
print(produit.get_toutes_images())

# Compter les images
print(f"Ce produit a {produit.get_nombre_images()} images")

# Parcourir les images additionnelles
for img in produit.get_images_additionnelles():
    print(f"- {img.legende}: {img.image.url}")

# Ajouter une image manuellement
nouvelle_image = ImageProduit.objects.create(
    produit=produit,
    legende="Vue arrière",
    ordre=10,
    est_principale=False
)
# Puis attacher un fichier à nouvelle_image.image
```

## Tests unitaires

```python
# produits/tests.py
from django.test import TestCase
from .models import Produit, ImageProduit

class ProduitImagesTestCase(TestCase):
    def setUp(self):
        self.produit = Produit.objects.create(
            nom="Produit Test",
            prix_ht=10.00,
            # ... autres champs requis
        )

    def test_get_nombre_images_sans_image(self):
        """Test sans aucune image"""
        self.assertEqual(self.produit.get_nombre_images(), 0)

    def test_get_nombre_images_avec_images(self):
        """Test avec image principale et additionnelles"""
        # Simuler une image principale
        # self.produit.image_principale = ...

        # Créer 3 images additionnelles
        for i in range(3):
            ImageProduit.objects.create(
                produit=self.produit,
                legende=f"Image {i}",
                ordre=i
            )

        # Devrait retourner 3 (ou 4 si image principale)
        self.assertEqual(self.produit.get_nombre_images(), 3)
```
