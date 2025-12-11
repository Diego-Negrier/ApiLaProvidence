# 🌱 Système de Gestion des Fournisseurs - La Providence

## 📋 Vue d'ensemble

Ce système permet aux fournisseurs et aux administrateurs de gérer leurs produits et commandes via deux interfaces Django Admin séparées :

- **Admin Principal (`/admin/`)** : Pour les administrateurs
- **Espace Fournisseur (`/fournisseur-admin/`)** : Pour les fournisseurs

## 🔐 Séparation des Droits d'Accès

### Administrateurs
- ✅ Accès complet à l'admin principal (`/admin/`)
- ✅ Peuvent voir la liste complète de tous les fournisseurs
- ✅ Peuvent créer, modifier et supprimer des fournisseurs
- ✅ Peuvent gérer tous les produits de tous les fournisseurs
- ✅ Peuvent voir toutes les commandes
- ✅ Ont tous les droits sur le système

### Fournisseurs
- ✅ Accès uniquement à l'espace fournisseur (`/fournisseur-admin/`)
- ✅ Peuvent modifier leur propre profil
- ✅ Peuvent créer, modifier et supprimer leurs propres produits
- ✅ Peuvent consulter les commandes contenant leurs produits
- ❌ Ne peuvent PAS voir les autres fournisseurs
- ❌ Ne peuvent PAS voir les produits des autres fournisseurs
- ❌ Ne peuvent PAS modifier les commandes (lecture seule)

## 🚀 Installation et Configuration

### 1. Configuration Django

Le système est déjà configuré dans les fichiers suivants :

#### `back/back/settings.py`
```python
# Backend d'authentification personnalisé
AUTHENTICATION_BACKENDS = [
    'fournisseur.backends.FournisseurAuthBackend',  # Pour les fournisseurs
    'django.contrib.auth.backends.ModelBackend',     # Pour les admins
]
```

#### `back/back/urls.py`
```python
from fournisseur.admin_site import fournisseur_admin_site
import fournisseur.admin_fournisseur

urlpatterns = [
    path('admin/', admin.site.urls),                    # Admin principal
    path('fournisseur-admin/', fournisseur_admin_site.urls),  # Espace fournisseur
    # ... autres URLs
]
```

### 2. Créer un Compte Fournisseur

#### Méthode 1 : Via l'Admin Principal (Recommandé)

1. Connectez-vous à l'admin principal : `http://localhost:8007/admin/`
2. Allez dans **Fournisseurs** > **Fournisseurs**
3. Cliquez sur **Ajouter un fournisseur**
4. Remplissez tous les champs obligatoires :
   - Nom, Prénom
   - Email (sera utilisé pour la connexion)
   - Password (définissez un mot de passe temporaire)
   - Métier, Contact, Téléphone
   - Adresse complète
   - etc.
5. Sauvegardez

#### Méthode 2 : Via une Commande Django

Si le fournisseur existe déjà (créé via l'admin), utilisez cette commande pour définir/réinitialiser son mot de passe :

```bash
python manage.py create_fournisseur_user
```

Ou en mode non-interactif :

```bash
python manage.py create_fournisseur_user --email "fournisseur@exemple.com" --password "MotDePasse123"
```

## 🔑 Connexion

### Pour les Administrateurs

1. Allez sur : `http://localhost:8007/admin/`
2. Connectez-vous avec votre compte superuser Django

### Pour les Fournisseurs

1. Allez sur : `http://localhost:8007/fournisseur-admin/`
2. Connectez-vous avec :
   - **Identifiant** : Votre email (ex: `jean.dupont@ferme.fr`)
   - **Mot de passe** : Votre mot de passe

## 📊 Fonctionnalités Fournisseur

### 1. Mon Profil

- Modifier mes informations personnelles
- Mettre à jour ma photo
- Gérer ma description et mes certifications
- Consulter mes statistiques (nombre de produits, commandes)
- Voir ma zone de couverture

**Champs modifiables :**
- Nom, Prénom, Email
- Métier, Contact, Téléphone
- Photo
- Description
- Type de production, Années d'expérience
- Certifications
- Produits principaux
- Calendrier de production

**Champs en lecture seule :**
- Date d'ajout / modification
- Statistiques
- Zone de couverture (géré par les admins)

### 2. Mes Produits

**Actions disponibles :**
- ✅ Créer un nouveau produit
- ✅ Modifier mes produits existants
- ✅ Supprimer mes produits
- ✅ Activer/Désactiver un produit
- ✅ Gérer le stock

**Champs modifiables :**
- Nom du produit
- Description (courte et complète)
- Prix HT, TVA
- Poids, Unité
- Stock
- Catégorie, Sous-catégorie
- Image principale
- Activation

**Filtres disponibles :**
- Par statut (actif/inactif)
- Par catégorie
- Par sous-catégorie
- Recherche par nom ou numéro unique

### 3. Mes Commandes

**Informations visibles :**
- Numéro de commande
- Client (nom, email)
- Date de commande
- Statut global
- Mes produits dans la commande
- Montant de mes produits (HT)

**Détails par commande :**
- Liste complète des produits du fournisseur
- Quantité commandée
- Prix unitaire HT
- Sous-total par ligne
- Statut de chaque produit

**Actions disponibles :**
- 🔍 Consulter les détails
- ❌ Pas de modification (lecture seule)

**Filtres disponibles :**
- Par statut de commande
- Par date
- Recherche par numéro de commande ou client

## 🛠️ Architecture Technique

### Fichiers Créés

```
fournisseur/
├── backends.py                      # Backend d'authentification personnalisé
├── admin_site.py                    # Site admin séparé pour les fournisseurs
├── admin_fournisseur.py             # Admins personnalisés (Profil, Produits, Commandes)
├── management/
│   └── commands/
│       └── create_fournisseur_user.py  # Commande de création de compte
└── README_FOURNISSEUR_ADMIN.md      # Cette documentation
```

### Flux d'Authentification

1. **Fournisseur se connecte sur `/fournisseur-admin/`**
2. `FournisseurAuthBackend` vérifie l'email/password dans la table `Fournisseur`
3. Si OK, crée/récupère un `User` Django avec username `fournisseur_{id}`
4. L'utilisateur est marqué comme `is_staff=True` pour accéder à l'admin
5. `FournisseurAdminSite` vérifie que le username commence par `fournisseur_`
6. Les requêtes sont filtrées automatiquement pour ne montrer que les données du fournisseur

### Sécurité

✅ **Séparation stricte des données**
- Chaque fournisseur ne voit QUE ses propres données
- Les queryset sont automatiquement filtrés dans `get_queryset()`
- Impossible de voir ou modifier les données d'un autre fournisseur

✅ **Permissions limitées**
- `has_add_permission()` : Contrôle qui peut créer
- `has_delete_permission()` : Contrôle qui peut supprimer
- `has_change_permission()` : Contrôle qui peut modifier

✅ **Mots de passe sécurisés**
- Les mots de passe sont hashés avec `make_password()`
- Vérification avec `check_password()`
- Pas de stockage en clair

## 📝 Exemples d'Utilisation

### Créer un Nouveau Produit (Fournisseur)

1. Connectez-vous sur `/fournisseur-admin/`
2. Cliquez sur **Produits**
3. Cliquez sur **Ajouter un produit**
4. Remplissez les champs :
   ```
   Nom: Tomates Bio du Potager
   Description: Tomates cultivées en permaculture
   Prix HT: 4.50
   TVA: 5.5
   Poids: 1
   Stock: 50
   Catégorie: Légumes
   ```
5. Uploadez une image
6. Cochez "Actif"
7. Sauvegardez

→ Le produit sera automatiquement associé à votre compte fournisseur

### Consulter les Commandes (Fournisseur)

1. Connectez-vous sur `/fournisseur-admin/`
2. Cliquez sur **Commandes**
3. Vous voyez toutes les commandes contenant vos produits
4. Cliquez sur une commande pour voir le détail
5. Section "Vos produits dans cette commande" :
   - Liste de vos produits
   - Quantités commandées
   - Montant total de vos produits

### Gérer Tous les Fournisseurs (Admin)

1. Connectez-vous sur `/admin/`
2. Cliquez sur **Fournisseurs** > **Fournisseurs**
3. Vous voyez la liste complète de tous les fournisseurs
4. Fonctionnalités :
   - Filtrer par zone de livraison, type de production, etc.
   - Exporter la liste
   - Voir les statistiques détaillées
   - Gérer les zones de livraison
   - Assigner des points de livraison

## 🔧 Maintenance

### Réinitialiser le Mot de Passe d'un Fournisseur

```bash
python manage.py create_fournisseur_user --email "fournisseur@exemple.com" --password "NouveauMotDePasse"
```

### Vérifier les Permissions

```python
# Dans le shell Django
python manage.py shell

from django.contrib.auth.models import User
from fournisseur.models import Fournisseur

# Récupérer un utilisateur fournisseur
user = User.objects.get(username='fournisseur_1')
print(f"Is staff: {user.is_staff}")  # Doit être True
print(f"Is superuser: {user.is_superuser}")  # Doit être False

# Récupérer le fournisseur associé
fournisseur_id = int(user.username.split('_')[1])
fournisseur = Fournisseur.objects.get(id=fournisseur_id)
print(f"Fournisseur: {fournisseur}")
```

### Déboguer les Problèmes de Connexion

1. **Fournisseur ne peut pas se connecter ?**
   - Vérifier que l'email est correct
   - Réinitialiser le mot de passe avec la commande
   - Vérifier que le fournisseur existe dans la BDD

2. **Fournisseur voit des données d'autres fournisseurs ?**
   - Vérifier `get_queryset()` dans les admins
   - Vérifier que `get_fournisseur_from_request()` fonctionne

3. **Erreur 403 Forbidden ?**
   - Vérifier `has_permission()` dans `FournisseurAdminSite`
   - Vérifier que `is_staff=True` sur l'utilisateur

## 📞 Support

Pour toute question ou problème :
- Vérifiez les logs Django : `python manage.py runserver`
- Consultez le fichier `admin_fournisseur.py` pour les configurations
- Testez avec le compte superuser pour vérifier que le problème vient bien des permissions

## 🎯 Roadmap Futures Améliorations

- [ ] Tableau de bord fournisseur avec graphiques
- [ ] Notifications par email lors de nouvelles commandes
- [ ] Export des commandes en PDF/CSV
- [ ] Gestion des factures
- [ ] Chat avec les clients
- [ ] Statistiques de ventes avancées

---

**Créé le** : 2025-12-11
**Version** : 1.0
**Dernière mise à jour** : 2025-12-11
