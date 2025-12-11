# 🚀 Installation et Configuration - Système Fournisseur

## ✅ Fichiers Créés

### Backend
- ✅ `fournisseur/backends.py` - Backend d'authentification personnalisé
- ✅ `fournisseur/admin_site.py` - Site admin séparé pour les fournisseurs
- ✅ `fournisseur/admin_fournisseur.py` - Admins personnalisés (Profil, Produits, Commandes)
- ✅ `fournisseur/management/commands/create_fournisseur_user.py` - Commande de création de compte

### Templates
- ✅ `fournisseur/templates/admin/fournisseur/base_site.html` - Template de base
- ✅ `fournisseur/templates/admin/fournisseur/index.html` - Page d'accueil
- ✅ `fournisseur/templates/admin/fournisseur/login.html` - Page de connexion

### Styles
- ✅ `fournisseur/static/fournisseur/css/fournisseur_admin.css` - CSS personnalisé

### Configuration
- ✅ `back/settings.py` - Backend d'authentification configuré
- ✅ `back/urls.py` - URLs séparées configurées

### Documentation
- ✅ `fournisseur/README_FOURNISSEUR_ADMIN.md` - Documentation complète
- ✅ `fournisseur/INSTALLATION.md` - Ce fichier

## 📦 Installation

### 1. Vérifier que tous les fichiers sont présents

```bash
cd ApiLaProvidence/back/fournisseur

# Vérifier la structure
ls -la backends.py admin_site.py admin_fournisseur.py
ls -la templates/admin/fournisseur/
ls -la static/fournisseur/css/
ls -la management/commands/
```

### 2. Appliquer les migrations (si nécessaire)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

## 👤 Créer un Compte Fournisseur

### Option 1 : Via l'Admin Principal (Recommandé)

1. Connectez-vous à `/admin/` avec un compte superuser
2. Allez dans **Fournisseurs** > **Ajouter un fournisseur**
3. Remplissez tous les champs obligatoires
4. **Important** : Définissez un mot de passe dans le champ `password`
5. Sauvegardez

### Option 2 : Via la Commande Django

Si le fournisseur existe déjà :

```bash
python manage.py create_fournisseur_user
# Puis suivez les instructions
```

Ou en mode non-interactif :

```bash
python manage.py create_fournisseur_user \
    --email "jean.dupont@ferme.fr" \
    --password "MonMotDePasse123"
```

## 🔑 Se Connecter

### Fournisseurs
- URL : `http://localhost:8007/fournisseur-admin/`
- Identifiant : Votre email
- Mot de passe : Votre mot de passe

### Administrateurs
- URL : `http://localhost:8007/admin/`
- Identifiant : Username superuser
- Mot de passe : Mot de passe superuser

## 🧪 Tester le Système

### 1. Tester la Connexion Fournisseur

```bash
# Démarrer le serveur
python manage.py runserver

# Ouvrir dans le navigateur
# http://localhost:8007/fournisseur-admin/
```

### 2. Vérifier les Permissions

Une fois connecté en tant que fournisseur :

- ✅ Vous devez voir uniquement 3 sections :
  - Fournisseurs (votre profil uniquement)
  - Produits (vos produits uniquement)
  - Commandes (commandes avec vos produits uniquement)

- ❌ Vous ne devez PAS voir :
  - Les autres fournisseurs
  - Les produits des autres fournisseurs
  - Les clients
  - Les paniers
  - etc.

### 3. Tester les Fonctionnalités

#### Modifier son Profil
1. Cliquez sur **Fournisseurs**
2. Cliquez sur votre nom
3. Modifiez vos informations
4. Sauvegardez
5. Vérifiez que les modifications sont enregistrées

#### Créer un Produit
1. Cliquez sur **Produits**
2. Cliquez sur **Ajouter un produit**
3. Remplissez les champs :
   - Nom
   - Description
   - Prix HT
   - TVA
   - Poids
   - Catégorie
4. Uploadez une image
5. Cochez "Actif"
6. Sauvegardez
7. Le produit doit être automatiquement associé à votre compte

#### Consulter les Commandes
1. Cliquez sur **Commandes**
2. Vous voyez toutes les commandes contenant vos produits
3. Cliquez sur une commande
4. Vous voyez uniquement vos produits dans cette commande

## 🐛 Débogage

### Problème : Impossible de se connecter

**Solution :**
```bash
# Vérifier que le fournisseur existe
python manage.py shell
>>> from fournisseur.models import Fournisseur
>>> f = Fournisseur.objects.get(email="votre@email.com")
>>> print(f)

# Réinitialiser le mot de passe
>>> f.set_password("NouveauMotDePasse")
>>> f.save()
>>> exit()
```

### Problème : Templates non trouvés

**Solution :**
```bash
# Vérifier que les templates existent
ls -la fournisseur/templates/admin/fournisseur/

# Collecter les statiques
python manage.py collectstatic --noinput
```

### Problème : CSS ne se charge pas

**Solution :**
```bash
# Vérifier DEBUG dans settings.py
DEBUG = True

# Vérifier STATIC_URL
STATIC_URL = '/static/'

# Collecter les statiques
python manage.py collectstatic --noinput

# Redémarrer le serveur
python manage.py runserver
```

### Problème : Erreur 403 Forbidden

**Solution :**
```python
# Vérifier que l'utilisateur est is_staff
python manage.py shell
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(username='fournisseur_1')
>>> u.is_staff = True
>>> u.save()
>>> exit()
```

## 📊 Structure de la Base de Données

### Tables Concernées

- `fournisseur_fournisseur` - Table des fournisseurs
- `auth_user` - Utilisateurs Django (créés automatiquement pour les fournisseurs)
- `produits_produit` - Produits (avec FK vers fournisseur)
- `commandes_commande` - Commandes
- `paniers_lignepanier` - Lignes de panier (avec FK vers produit)

### Relation Fournisseur ↔ User

Quand un fournisseur se connecte :
1. Le backend cherche le fournisseur par email
2. Vérifie le mot de passe
3. Crée/récupère un User Django avec username = `fournisseur_{id}`
4. Marque l'utilisateur comme `is_staff=True`
5. Attache le fournisseur à l'objet user : `user.fournisseur`

## 🔐 Sécurité

### Mots de Passe

- ✅ Les mots de passe sont hashés avec `make_password()`
- ✅ Vérification avec `check_password()`
- ✅ Pas de stockage en clair

### Permissions

- ✅ Fournisseurs ne voient que leurs données
- ✅ Filtrage automatique dans `get_queryset()`
- ✅ Vérification des permissions dans `has_permission()`
- ✅ Pas d'accès à l'admin principal

### Séparation des Sites

- ✅ Admin principal : `/admin/`
- ✅ Espace fournisseur : `/fournisseur-admin/`
- ✅ Authentification séparée
- ✅ Permissions différentes

## 📈 Performance

### Optimisations Appliquées

- `select_related()` pour les FK
- `prefetch_related()` pour les M2M
- Index sur les champs clés
- Filtrage au niveau de la requête

## 🚀 Prochaines Étapes

### Fonctionnalités à Ajouter (Optionnel)

- [ ] Dashboard avec graphiques
- [ ] Notifications par email
- [ ] Export PDF/CSV des commandes
- [ ] Gestion des factures
- [ ] Chat avec les clients
- [ ] Statistiques avancées
- [ ] Upload multiple d'images produits

### Améliorations Suggérées

- [ ] Tests automatisés
- [ ] Documentation API
- [ ] Logs détaillés
- [ ] Monitoring des performances
- [ ] Backup automatique

## 📞 Support

Pour toute question :
1. Consultez `README_FOURNISSEUR_ADMIN.md`
2. Vérifiez les logs : `python manage.py runserver`
3. Testez avec le compte superuser
4. Vérifiez les permissions en base de données

---

**Version** : 1.0
**Date** : 2025-12-11
**Auteur** : Système La Providence
