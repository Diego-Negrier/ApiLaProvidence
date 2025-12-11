# Guide complet - Gestion des images de produits

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Méthodes disponibles](#méthodes-disponibles)
3. [Utilisation dans les vues](#utilisation-dans-les-vues)
4. [Utilisation dans les templates](#utilisation-dans-les-templates)
5. [API REST](#api-rest)
6. [Tests](#tests)
7. [Génération automatique](#génération-automatique)

---

## 🎯 Vue d'ensemble

Le système de gestion des images de produits permet de :
- Avoir **une image principale** par produit (`image_principale`)
- Ajouter **plusieurs images additionnelles** via le modèle `ImageProduit`
- Récupérer facilement toutes les images d'un produit
- Marquer une image comme principale dans les images additionnelles

### Structure des modèles

```
Produit
├── image_principale (ImageField) - Image principale du produit
└── images (relation ManyToMany via ImageProduit)
    ├── image (ImageField)
    ├── legende (CharField)
    ├── ordre (IntegerField)
    └── est_principale (BooleanField)
```

---

## 🔧 Méthodes disponibles

### Dans le modèle `Produit`

#### 1. `get_images_additionnelles()`
Retourne toutes les images additionnelles triées par ordre.

```python
images = produit.get_images_additionnelles()
# Retourne: QuerySet[ImageProduit]
```

#### 2. `get_toutes_images()`
Retourne les URLs de toutes les images (principale + additionnelles).

```python
urls = produit.get_toutes_images()
# Retourne: List[str]
# Exemple: ['/media/produits/.../image1.jpg', '/media/produits/.../image2.jpg']
```

#### 3. `get_nombre_images()`
Retourne le nombre total d'images.

```python
count = produit.get_nombre_images()
# Retourne: int
# Exemple: 5
```

#### 4. `get_image_principale_obj()`
Retourne l'objet ImageProduit marqué comme principal (si existe).

```python
img = produit.get_image_principale_obj()
# Retourne: Optional[ImageProduit]
```

---

## 💻 Utilisation dans les vues

### Vue basique (Function-Based View)

```python
from django.shortcuts import render, get_object_or_404
from .models import Produit

def produit_detail(request, slug):
    produit = get_object_or_404(Produit, slug=slug)

    context = {
        'produit': produit,
        'images_additionnelles': produit.get_images_additionnelles(),
        'toutes_images': produit.get_toutes_images(),
        'nombre_images': produit.get_nombre_images(),
    }

    return render(request, 'produit_detail.html', context)
```

### Vue Class-Based (DetailView)

```python
from django.views.generic import DetailView
from .models import Produit

class ProduitDetailView(DetailView):
    model = Produit
    template_name = 'produit_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        produit = ctx['produit']

        # Ajouter les images au contexte
        ctx['images_additionnelles'] = produit.get_images_additionnelles()
        ctx['toutes_images_urls'] = produit.get_toutes_images()
        ctx['nombre_images'] = produit.get_nombre_images()

        return ctx
```

---

## 🎨 Utilisation dans les templates

### 1. Affichage simple de l'image principale

```html
{% if produit.image_principale %}
    <img src="{{ produit.image_principale.url }}"
         alt="{{ produit.nom }}"
         class="img-fluid">
{% else %}
    <img src="{% static 'images/placeholder.jpg' %}"
         alt="Pas d'image">
{% endif %}
```

### 2. Galerie d'images Bootstrap

```html
<div class="row">
    <!-- Image principale -->
    {% if produit.image_principale %}
    <div class="col-md-3 mb-3">
        <img src="{{ produit.image_principale.url }}"
             alt="{{ produit.nom }}"
             class="img-thumbnail">
        <small class="text-muted">Image principale</small>
    </div>
    {% endif %}

    <!-- Images additionnelles -->
    {% for image in images_additionnelles %}
    <div class="col-md-3 mb-3">
        <img src="{{ image.image.url }}"
             alt="{{ image.legende|default:produit.nom }}"
             class="img-thumbnail">
        {% if image.legende %}
            <small class="text-muted">{{ image.legende }}</small>
        {% endif %}
    </div>
    {% endfor %}
</div>
```

### 3. Carrousel Bootstrap complet

```html
<div id="productCarousel" class="carousel slide" data-ride="carousel">
    <!-- Indicateurs -->
    <ol class="carousel-indicators">
        {% if produit.image_principale %}
        <li data-target="#productCarousel" data-slide-to="0" class="active"></li>
        {% endif %}
        {% for image in images_additionnelles %}
        <li data-target="#productCarousel"
            data-slide-to="{{ forloop.counter }}"
            {% if not produit.image_principale and forloop.first %}class="active"{% endif %}>
        </li>
        {% endfor %}
    </ol>

    <!-- Slides -->
    <div class="carousel-inner">
        {% if produit.image_principale %}
        <div class="carousel-item active">
            <img src="{{ produit.image_principale.url }}"
                 class="d-block w-100"
                 alt="{{ produit.nom }}">
        </div>
        {% endif %}

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
    <a class="carousel-control-prev" href="#productCarousel" role="button" data-slide="prev">
        <span class="carousel-control-prev-icon"></span>
    </a>
    <a class="carousel-control-next" href="#productCarousel" role="button" data-slide="next">
        <span class="carousel-control-next-icon"></span>
    </a>
</div>
```

### 4. Lightbox moderne

```html
<!-- Nécessite une librairie comme GLightbox ou Fancybox -->
<div class="gallery">
    {% for url in toutes_images_urls %}
    <a href="{{ url }}" class="glightbox">
        <img src="{{ url }}"
             alt="{{ produit.nom }}"
             class="img-thumbnail m-1"
             style="max-width: 150px;">
    </a>
    {% endfor %}
</div>

<script>
    const lightbox = GLightbox({
        selector: '.glightbox'
    });
</script>
```

---

## 🌐 API REST

### Créer un serializer (Django REST Framework)

```python
# produits/serializers.py
from rest_framework import serializers
from .models import Produit, ImageProduit

class ImageProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produits"""
    class Meta:
        model = ImageProduit
        fields = ['id', 'image', 'legende', 'ordre', 'est_principale']


class ProduitDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un produit avec images"""

    # Images via relation
    images_additionnelles = ImageProduitSerializer(
        source='images',
        many=True,
        read_only=True
    )

    # Méthodes personnalisées
    toutes_images = serializers.SerializerMethodField()
    nombre_images = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'slug',
            'image_principale',
            'images_additionnelles',
            'toutes_images',
            'nombre_images',
            # ... autres champs
        ]

    def get_toutes_images(self, obj):
        """Retourne toutes les URLs d'images"""
        return obj.get_toutes_images()

    def get_nombre_images(self, obj):
        """Retourne le nombre total d'images"""
        return obj.get_nombre_images()
```

### Vue API

```python
# produits/views.py
from rest_framework import viewsets
from .models import Produit
from .serializers import ProduitDetailSerializer

class ProduitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitDetailSerializer
    lookup_field = 'slug'
```

### Exemple de réponse JSON

```json
GET /api/produits/pommes-bio-1/

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

---

## 🧪 Tests

### Exécuter le script de test

```bash
cd ApiLaProvidence/back
python3 test_images_produit.py
```

### Tests unitaires Django

```python
# produits/tests.py
from django.test import TestCase
from .models import Produit, ImageProduit
from decimal import Decimal

class ProduitImagesTest(TestCase):

    def setUp(self):
        """Créer un produit de test"""
        self.produit = Produit.objects.create(
            nom="Produit Test",
            prix_ht=Decimal('10.00'),
            tva=Decimal('20.00'),
            stock_actuel=100,
            statut='en_stock'
        )

    def test_get_nombre_images_vide(self):
        """Test sans aucune image"""
        self.assertEqual(self.produit.get_nombre_images(), 0)

    def test_get_images_additionnelles(self):
        """Test des images additionnelles"""
        # Créer 3 images
        for i in range(3):
            ImageProduit.objects.create(
                produit=self.produit,
                legende=f"Image {i}",
                ordre=i
            )

        images = self.produit.get_images_additionnelles()
        self.assertEqual(images.count(), 3)

    def test_get_toutes_images_avec_principale(self):
        """Test avec image principale"""
        # Simuler une image principale
        # self.produit.image_principale = 'test.jpg'
        # self.produit.save()

        # Créer 2 images additionnelles
        for i in range(2):
            ImageProduit.objects.create(
                produit=self.produit,
                legende=f"Image {i}",
                ordre=i
            )

        urls = self.produit.get_toutes_images()
        # Devrait avoir 2 URLs (ou 3 si image principale)
        self.assertEqual(len(urls), 2)

    def test_ordre_images(self):
        """Test du tri par ordre"""
        # Créer dans le désordre
        ImageProduit.objects.create(produit=self.produit, ordre=3)
        ImageProduit.objects.create(produit=self.produit, ordre=1)
        ImageProduit.objects.create(produit=self.produit, ordre=2)

        images = self.produit.get_images_additionnelles()
        ordres = [img.ordre for img in images]

        self.assertEqual(ordres, [1, 2, 3])
```

### Lancer les tests

```bash
python manage.py test produits.tests.ProduitImagesTest
```

---

## 🤖 Génération automatique

### Commande de génération

```bash
# Générer 20 produits avec images
python manage.py generer_produits --nombre=20

# Supprimer les produits existants et en générer 50
python manage.py generer_produits --nombre=50 --clean
```

### Ce qui est généré

Pour chaque produit :
- ✅ 1 image principale (téléchargée depuis Unsplash)
- ✅ 2 à 4 images additionnelles (aléatoire)
- ✅ Légendes aléatoires parmi 6 options
- ✅ Ordre d'affichage automatique
- ✅ Flag `est_principale=False` pour les additionnelles

### Légendes générées

Les images additionnelles reçoivent une légende aléatoire parmi :
- "Vue détaillée du produit"
- "Présentation du produit"
- "Vue d'ensemble"
- "Gros plan"
- "Packaging du produit"
- "Produit en situation"

---

## 📝 Exemples pratiques

### Shell Django

```bash
python manage.py shell
```

```python
from produits.models import Produit

# Récupérer un produit
produit = Produit.objects.first()

# Afficher les images
print(f"Nombre d'images: {produit.get_nombre_images()}")
print(f"URLs: {produit.get_toutes_images()}")

# Parcourir les images
for img in produit.get_images_additionnelles():
    print(f"- {img.legende}: {img.image.url}")
```

### Ajouter une image manuellement

```python
from produits.models import Produit, ImageProduit
from django.core.files import File

produit = Produit.objects.get(slug='mon-produit')

# Créer l'objet image
nouvelle_image = ImageProduit.objects.create(
    produit=produit,
    legende="Vue de côté",
    ordre=10,
    est_principale=False
)

# Attacher le fichier
with open('chemin/vers/image.jpg', 'rb') as f:
    nouvelle_image.image.save('image.jpg', File(f), save=True)
```

---

## 🔍 Dépannage

### Problème : Les images ne s'affichent pas

1. Vérifier que `MEDIA_URL` et `MEDIA_ROOT` sont configurés dans `settings.py`
2. Vérifier que les URLs de media sont dans `urls.py` :

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... vos urls
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Problème : AttributeError sur get_toutes_images()

Assurez-vous d'avoir la dernière version du modèle `Produit` avec les méthodes ajoutées.

### Problème : Images dupliquées lors de la génération

L'API Unsplash peut retourner la même image. C'est normal en développement.

---

## 📚 Ressources

- [Documentation Django ImageField](https://docs.djangoproject.com/en/stable/ref/models/fields/#imagefield)
- [Bootstrap Carousel](https://getbootstrap.com/docs/4.6/components/carousel/)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

## 🎉 Conclusion

Vous disposez maintenant d'un système complet pour gérer les images de produits :
- ✅ Modèles configurés
- ✅ Méthodes de récupération
- ✅ Intégration dans les vues
- ✅ Exemples de templates
- ✅ API REST
- ✅ Génération automatique
- ✅ Tests

Pour toute question, consultez le fichier `EXEMPLE_USAGE_IMAGES.md`.
