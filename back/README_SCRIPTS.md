# 🚀 Scripts de Génération de Données - La Providence

Ce guide explique comment utiliser les scripts Django pour générer automatiquement toutes les données de La Providence (catégories, fournisseurs, produits avec images).

## 📋 Table des matières

- [Scripts disponibles](#scripts-disponibles)
- [Usage rapide](#usage-rapide)
- [Guide détaillé](#guide-détaillé)
- [Options avancées](#options-avancées)

---

## Scripts disponibles

### 1. 🎯 `generate_all_data.py` - Script tout-en-un (RECOMMANDÉ)

Génère automatiquement **tout** : catégories, fournisseurs ET produits avec images.

```bash
# Génération complète avec valeurs par défaut
python manage.py generate_all_data --clean

# Personnalisé
python manage.py generate_all_data --clean --nombre-fournisseurs=50 --nombre-produits=200
```

### 2. 📂 `setup_initial_data.py` - Catégories + Fournisseurs

Génère les catégories et les fournisseurs (sans les produits).

```bash
# Tout créer
python manage.py setup_initial_data --clean

# Uniquement catégories
python manage.py setup_initial_data --categories-only --clean

# Uniquement fournisseurs
python manage.py setup_initial_data --fournisseurs-only --nombre-fournisseurs=30
```

### 3. 📦 `generer_produits.py` - Produits avec images

Génère uniquement les produits (nécessite des catégories et fournisseurs existants).

```bash
# Générer 100 produits avec images
python manage.py generer_produits --nombre=100

# Sans télécharger les images (plus rapide)
python manage.py generer_produits --nombre=100 --skip-images
```

### 4. 🗑️ `clear_data.py` - Nettoyage

Supprime les données de manière sécurisée.

```bash
# Supprimer tout
python manage.py clear_data --all --confirm

# Supprimer uniquement les produits
python manage.py clear_data --produits --confirm

# Supprimer uniquement les fournisseurs
python manage.py clear_data --fournisseurs --confirm
```

---

## Usage rapide

### 🎬 Démarrage rapide - Première utilisation

Pour initialiser complètement votre base de données :

```bash
# 1. Nettoyer et créer TOUT (catégories, fournisseurs, produits avec images)
python manage.py generate_all_data --clean --nombre-fournisseurs=30 --nombre-produits=100
```

✅ **C'est tout !** Votre base est prête avec :
- 9 catégories principales
- ~80 sous-catégories
- ~200 sous-sous-catégories
- 30 fournisseurs
- 100 produits avec images Unsplash

### ⚡ Mode rapide (sans images)

Pour les tests rapides sans télécharger les images :

```bash
python manage.py generate_all_data --clean --nombre-produits=50 --skip-images
```

---

## Guide détaillé

### Étape 1: Créer les catégories

Les catégories La Providence sont organisées en 3 niveaux :

```
🏡 Habitat Autonome Premium (Catégorie)
  └─ 🏠 Maisons Passives (Sous-catégorie)
      └─ Maison passive sur-mesure (Sous-sous-catégorie)
      └─ Kit maison passive
      └─ Extension passive
```

**Commande:**

```bash
python manage.py setup_initial_data --categories-only --clean
```

**Résultat:**
- 9 catégories principales (Habitat, Matériaux, Énergie, Eau, etc.)
- ~80 sous-catégories
- ~200 sous-sous-catégories

### Étape 2: Créer les fournisseurs

Génère des fournisseurs cohérents avec les catégories créées.

**Commande:**

```bash
python manage.py setup_initial_data --fournisseurs-only --nombre-fournisseurs=30
```

**Résultat:**
- Fournisseurs avec métiers alignés aux catégories
- Coordonnées GPS réalistes (villes françaises)
- Informations de livraison (zones, frais, délais)
- Certifications et engagements écologiques

### Étape 3: Créer les produits

Génère des produits avec images téléchargées depuis Unsplash.

**Commande:**

```bash
python manage.py generer_produits --nombre=100
```

**Résultat:**
- Produits assignés aux sous-sous-catégories existantes
- Fournisseurs assignés aléatoirement
- Images de qualité depuis Unsplash
- Prix, stocks, promotions
- Attributs (bio, local, nouveauté)

---

## Options avancées

### 🎛️ Options du script `generate_all_data`

| Option | Description | Défaut |
|--------|-------------|--------|
| `--clean` | Supprimer toutes les données avant génération | False |
| `--nombre-fournisseurs` | Nombre de fournisseurs à créer | 30 |
| `--nombre-produits` | Nombre de produits à créer | 100 |
| `--skip-images` | Ne pas télécharger les images (plus rapide) | False |

**Exemples:**

```bash
# Production : beaucoup de données
python manage.py generate_all_data --clean \
  --nombre-fournisseurs=100 \
  --nombre-produits=500

# Développement : données minimales sans images
python manage.py generate_all_data --clean \
  --nombre-fournisseurs=10 \
  --nombre-produits=30 \
  --skip-images

# Test : données moyennes
python manage.py generate_all_data --clean \
  --nombre-fournisseurs=20 \
  --nombre-produits=80
```

### 🎛️ Options du script `clear_data`

| Option | Description |
|--------|-------------|
| `--all` | Supprimer tout |
| `--categories` | Supprimer uniquement les catégories |
| `--produits` | Supprimer uniquement les produits |
| `--fournisseurs` | Supprimer uniquement les fournisseurs |
| `--confirm` | Ne pas demander de confirmation |

**Exemples:**

```bash
# Supprimer uniquement les produits (garde catégories et fournisseurs)
python manage.py clear_data --produits --confirm

# Supprimer tout avec confirmation
python manage.py clear_data --all

# Supprimer fournisseurs et produits
python manage.py clear_data --fournisseurs --confirm
python manage.py clear_data --produits --confirm
```

---

## 📊 Résumé des données générées

### Catégories (9 principales)

1. 🏡 **Habitat Autonome Premium** - Maisons passives, tiny houses, rénovation
2. 🌳 **Matériaux Nobles et Locaux** - Bois, chanvre, pierre
3. ⚡ **Énergie Autonome** - Solaire, batteries, éolien, chauffage bois
4. 💧 **Eau et Traitement Local** - Filtration, phytoépuration, récupération
5. 🌱 **Autonomie Alimentaire** - Potager, verger, apiculture, serres
6. 🌿 **Plantes & Végétaux** - Semences, arbres, arbustes
7. 🎨 **Artisanat Local Premium** - Mobilier, céramique, vannerie
8. 🍷 **Gastronomie du Terroir** - Vins, fromages, miel
9. 🌍 **Expérience & Proximité** - Formations, services

### Fournisseurs

**Métiers cohérents:**
- Constructeur de maisons passives
- Installateur solaire certifié RGE
- Maraîcher bio & permaculture
- Viticulteur biodynamique
- etc.

**Données incluses:**
- Coordonnées complètes
- Zones de livraison (rayon, départements, villes, national)
- Frais de livraison (base + km)
- Certifications (AB, RGE, Demeter, etc.)
- Engagements écologiques

### Produits

**Caractéristiques:**
- Images haute qualité (Unsplash)
- Prix HT + TVA
- Stock aléatoire
- ~20% Bio
- ~30% Local
- ~15% Nouveauté
- ~10% En promotion

---

## 🔧 Dépannage

### Problème: "Aucune catégorie trouvée"

**Solution:** Créer d'abord les catégories

```bash
python manage.py setup_initial_data --categories-only
```

### Problème: "Aucun fournisseur trouvé"

**Solution:** Créer d'abord les fournisseurs

```bash
python manage.py setup_initial_data --fournisseurs-only --nombre-fournisseurs=30
```

### Problème: Images Unsplash ne se téléchargent pas

**Solutions:**
1. Vérifier la connexion internet
2. Utiliser `--skip-images` pour ignorer les images
3. Télécharger les images manuellement plus tard

### Problème: "Decimal field overflow"

**Solution:** Les montants sont limités à 9999.99€. Le script gère automatiquement cette limite.

---

## 💡 Bonnes pratiques

### 1. Développement

```bash
# Données minimales sans images pour tester rapidement
python manage.py generate_all_data --clean \
  --nombre-fournisseurs=5 \
  --nombre-produits=20 \
  --skip-images
```

### 2. Staging / Pré-production

```bash
# Données réalistes avec images
python manage.py generate_all_data --clean \
  --nombre-fournisseurs=30 \
  --nombre-produits=100
```

### 3. Production

```bash
# Ne JAMAIS utiliser --clean en production !
# Ajouter des données supplémentaires uniquement
python manage.py generer_produits --nombre=50
```

### 4. Reset complet

```bash
# Méthode sûre avec confirmation
python manage.py clear_data --all
python manage.py generate_all_data --nombre-fournisseurs=30 --nombre-produits=100
```

---

## 🎯 Workflow recommandé

### Initialisation du projet

```bash
# 1. Migrations
python manage.py migrate

# 2. Génération complète
python manage.py generate_all_data --clean \
  --nombre-fournisseurs=30 \
  --nombre-produits=100

# 3. Créer un superuser
python manage.py createsuperuser

# 4. Lancer le serveur
python manage.py runserver
```

### Ajout de données

```bash
# Ajouter 20 nouveaux produits
python manage.py generer_produits --nombre=20

# Ajouter 10 nouveaux fournisseurs
python manage.py setup_initial_data --fournisseurs-only --nombre-fournisseurs=10
```

### Réinitialisation

```bash
# Tout supprimer et recréer
python manage.py clear_data --all --confirm
python manage.py generate_all_data --clean \
  --nombre-fournisseurs=30 \
  --nombre-produits=100
```

---

## 📝 Notes importantes

- ⚠️ **ATTENTION:** `--clean` supprime TOUTES les données existantes
- 📸 Le téléchargement d'images peut prendre du temps (1-2 secondes par produit)
- 🔄 Les scripts sont idempotents avec `get_or_create` (sauf avec `--clean`)
- 💾 Utilisez toujours `transaction.atomic()` pour garantir l'intégrité des données
- 🎲 Les données sont générées aléatoirement mais de façon cohérente

---

## 🆘 Support

En cas de problème, vérifier :
1. Les migrations sont à jour : `python manage.py migrate`
2. Les modèles sont corrects dans `produits/models.py` et `fournisseur/models.py`
3. Les dépendances sont installées : `pip install -r requirements.txt`

---

**Bonne génération de données ! 🎉**
