#!/bin/bash

# ============================================================
# SCRIPT DE GESTION LOCALE - InBoundPR Backend (Sans Docker)
# ============================================================

# Couleurs
G='\033[0;32m'
B='\033[0;34m'
Y='\033[1;33m'
R='\033[0;31m'
NC='\033[0m'

info() { echo -e "${B}ℹ️  $1${NC}"; }
ok() { echo -e "${G}✅ $1${NC}"; }
warn() { echo -e "${Y}⚠️  $1${NC}"; }
error() { echo -e "${R}❌ $1${NC}"; }

# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACK_DIR="$SCRIPT_DIR/back"
ENV_FILE="$BACK_DIR/.env.local"
MANAGE="$BACK_DIR/manage.py"
SETTINGS_FILE="$BACK_DIR/back/settings.py"

# Afficher les chemins pour debug
info "Chemins détectés:"
echo "   Script: $SCRIPT_DIR"
echo "   Back: $BACK_DIR"
echo "   Settings: $SETTINGS_FILE"
echo ""

# ============================================================
# VÉRIFICATIONS
# ============================================================

check_python() {
    if ! command -v python3 &> /dev/null; then
        error "Python 3 n'est pas installé"
        error "Installer avec: brew install python3 (macOS) ou apt install python3 (Linux)"
        exit 1
    fi
    info "Python: $(python3 --version)"
}

check_structure() {
    info "Vérification de la structure..."
    
    # Vérifier manage.py
    if [ ! -f "$MANAGE" ]; then
        error "manage.py introuvable dans $BACK_DIR"
        exit 1
    fi
    
    # Vérifier settings.py
    if [ ! -f "$SETTINGS_FILE" ]; then
        error "settings.py introuvable: $SETTINGS_FILE"
        exit 1
    fi
    
    ok "Structure OK"
}

check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        warn ".env.local introuvable"
        info "Création de .env.local..."
        create_env_local
    fi
    ok "Fichier .env.local OK"
}

# ============================================================
# CRÉATION .env.local
# ============================================================

create_env_local() {
    info "Création de .env.local..."
    
    cat > "$ENV_FILE" << 'EOF'
# ==============================================================================
# ENVIRONNEMENT LOCAL (Sans Docker)
# ==============================================================================

# Environnement
DJANGO_ENV=local
DOCKER_CONTAINER=false

# Sécurité
SECRET_KEY=django-insecure-local-dev-key-CHANGE-ME
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données - SQLite (par défaut pour développement local)
DB_ENGINE=django.db.backends.sqlite3

# OU MySQL (décommenter et configurer si vous utilisez MySQL)
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=ApiTcareDev
# DB_USER=root
# DB_PASSWORD=votre_mot_de_passe
# DB_HOST=localhost
# DB_PORT=3306

# URLs
BACKEND_DOMAIN=localhost:8007
FRONTEND_URL=http://localhost:3007
BACKEND_URL=http://localhost:8007

# Email (console pour développement)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=DEBUG
EOF
    
    chmod 600 "$ENV_FILE"
    ok ".env.local créé"
    warn "N'oubliez pas de configurer vos paramètres de base de données !"
}

# ============================================================
# CRÉATION STRUCTURE
# ============================================================

create_structure() {
    info "Création de la structure locale..."
    
    mkdir -p "$BACK_DIR"/{static,staticfiles,media,logs,templates}
    mkdir -p "$BACK_DIR/static"/{css,js,images,fonts}
    
    # CSS de base
    if [ ! -f "$BACK_DIR/static/css/base.css" ]; then
        cat > "$BACK_DIR/static/css/base.css" << 'EOF'
:root {
    --primary: #2563eb;
    --secondary: #64748b;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}
EOF
    fi

    # JavaScript de base
    if [ ! -f "$BACK_DIR/static/js/main.js" ]; then
        cat > "$BACK_DIR/static/js/main.js" << 'EOF'
console.log('🚀 InBoundPR Backend loaded');
EOF
    fi

    # .gitkeep files
    touch "$BACK_DIR/logs/.gitkeep"
    touch "$BACK_DIR/media/.gitkeep"
    touch "$BACK_DIR/staticfiles/.gitkeep"
    
    ok "Structure créée"
}

# ============================================================
# INSTALLATION DÉPENDANCES
# ============================================================

install_deps() {
    info "Installation des dépendances..."
    
    # Chercher requirements.txt
    REQUIREMENTS=""
    
    if [ -f "$BACK_DIR/requirements.txt" ]; then
        REQUIREMENTS="$BACK_DIR/requirements.txt"
    elif [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        REQUIREMENTS="$SCRIPT_DIR/requirements.txt"
    else
        warn "requirements.txt introuvable"
        info "Création d'un requirements.txt minimal..."
        create_requirements
        REQUIREMENTS="$BACK_DIR/requirements.txt"
    fi
    
    info "Utilisation de: $REQUIREMENTS"
    
    python3 -m pip install --upgrade pip
    pip3 install -r "$REQUIREMENTS"
    
    ok "Dépendances installées"
}

create_requirements() {
    cat > "$BACK_DIR/requirements.txt" << 'EOF'
# Django
Django>=4.2,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0

# Base de données
pymysql>=1.1.0
mysqlclient>=2.2.0

# Utilitaires
python-dotenv>=1.0.0
Pillow>=10.0.0

# TinyMCE
django-tinymce>=3.6.1

# Production
gunicorn>=21.2.0
EOF
    
    ok "requirements.txt créé"
}

# ============================================================
# MIGRATIONS
# ============================================================

migrate() {
    info "Migrations de la base de données..."
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false
    
    cd "$BACK_DIR" || exit 1
    
    # Créer les migrations
    python3 manage.py makemigrations
    
    # Appliquer les migrations
    python3 manage.py migrate
    
    ok "Migrations effectuées"
}

# ============================================================
# COLLECTE FICHIERS STATIQUES
# ============================================================

collectstatic() {
    info "Collecte des fichiers statiques..."
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false
    
    cd "$BACK_DIR" || exit 1
    python3 manage.py collectstatic --noinput
    
    ok "Fichiers statiques collectés"
}

# ============================================================
# UTILISATEUR ADMIN
# ============================================================

create_superuser() {
    info "Création du superutilisateur..."
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false
    
    cd "$BACK_DIR" || exit 1
    python3 manage.py createsuperuser
    
    ok "Superutilisateur créé"
}

# ============================================================
# DÉMARRAGE SERVEUR
# ============================================================

start_server() {
    info "🚀 Démarrage du serveur Django..."
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false
    
    # Port
    PORT="${1:-8007}"
    
    # Afficher les infos
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   🐍 Django Development Server             ║"
    echo "╠════════════════════════════════════════════╣"
    echo "║   Environment: local (sans Docker)         ║"
    echo "║   Port: $PORT                                 ║"
    echo "║   Admin: http://localhost:$PORT/admin        ║"
    echo "║   API: http://localhost:$PORT/api            ║"
    echo "╠════════════════════════════════════════════╣"
    echo "║   Arrêt: Ctrl+C                            ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    
    # Lancer le serveur
    cd "$BACK_DIR" || exit 1
    python3 manage.py runserver "0.0.0.0:$PORT"
}

# ============================================================
# SHELL DJANGO
# ============================================================

shell() {
    info "🐚 Ouverture du shell Django..."
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false
    
    cd "$BACK_DIR" || exit 1
    python3 manage.py shell
}

# ============================================================
# TESTS
# ============================================================

run_tests() {
    info "🧪 Exécution des tests..."
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false
    
    cd "$BACK_DIR" || exit 1
    
    if [ -n "$1" ]; then
        # Test spécifique
        python3 manage.py test "$1"
    else
        # Tous les tests
        python3 manage.py test
    fi
}

# ============================================================
# NETTOYAGE
# ============================================================

clean() {
    warn "Nettoyage des fichiers temporaires..."
    
    # Fichiers Python
    find "$BACK_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find "$BACK_DIR" -type f -name "*.pyc" -delete 2>/dev/null
    find "$BACK_DIR" -type f -name "*.pyo" -delete 2>/dev/null
    
    # Logs
    if [ -d "$BACK_DIR/logs" ]; then
        rm -f "$BACK_DIR/logs"/*.log
        touch "$BACK_DIR/logs/.gitkeep"
    fi
    
    # Staticfiles
    if [ -d "$BACK_DIR/staticfiles" ]; then
        rm -rf "$BACK_DIR/staticfiles"/*
        touch "$BACK_DIR/staticfiles/.gitkeep"
    fi
    
    ok "Nettoyage effectué"
}

# ============================================================
# RESET COMPLET
# ============================================================

reset() {
    error "⚠️  ATTENTION: Ceci va supprimer TOUTES les données !"
    read -p "Êtes-vous sûr ? (tapez 'oui' pour confirmer): " confirm
    
    if [ "$confirm" != "oui" ]; then
        info "Annulé"
        return
    fi
    
    warn "Reset en cours..."
    
    # Supprimer la base SQLite
    if [ -f "$BACK_DIR/db.sqlite3" ]; then
        rm -f "$BACK_DIR/db.sqlite3"
        ok "Base SQLite supprimée"
    fi
    
    # Supprimer les migrations
    find "$BACK_DIR" -path "*/migrations/*.py" -not -name "__init__.py" -delete 2>/dev/null
    find "$BACK_DIR" -path "*/migrations/*.pyc" -delete 2>/dev/null
    ok "Migrations supprimées"
    
    # Nettoyer
    clean
    
    # Recréer
    info "Recréation de la base..."
    migrate
    
    ok "Reset terminé"
}

# ============================================================
# LOGS
# ============================================================

logs() {
    if [ ! -f "$BACK_DIR/logs/django.log" ]; then
        warn "Aucun log disponible"
        return
    fi
    
    info "📋 Logs Django:"
    echo ""
    
    if [ -n "$1" ]; then
        tail -n "$1" "$BACK_DIR/logs/django.log"
    else
        tail -n 50 "$BACK_DIR/logs/django.log"
    fi
}

# ============================================================
# VÉRIFIER LES DÉPENDANCES
# ============================================================

check_deps() {
    info "Vérification des dépendances..."
    
    cd "$BACK_DIR" || exit 1
    
    # Vérifier Django
    if ! python3 -c "import django" 2>/dev/null; then
        error "Django n'est pas installé"
        info "Exécutez: ./start_local.sh setup"
        exit 1
    fi
    
    # Vérifier les autres packages
    python3 << 'PYEOF'
import sys

packages = {
    'django': 'Django',
    'rest_framework': 'djangorestframework',
    'corsheaders': 'django-cors-headers',
    'dotenv': 'python-dotenv',
    'PIL': 'Pillow',
    'tinymce': 'django-tinymce',
}

missing = []
for module, package in packages.items():
    try:
        __import__(module)
    except ImportError:
        missing.append(package)

if missing:
    print(f"❌ Packages manquants: {', '.join(missing)}")
    print("Exécutez: pip3 install -r requirements.txt")
    sys.exit(1)
else:
    print("✅ Toutes les dépendances sont installées")
PYEOF
    
    ok "Dépendances OK"
}

# ============================================================
# INFORMATIONS
# ============================================================

show_info() {
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   📦 InBoundPR Backend - Info              ║"
    echo "║   Mode: Sans Docker                        ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    
    info "Structure:"
    echo "   Back: $BACK_DIR"
    echo "   Settings: $SETTINGS_FILE"
    echo "   .env.local: $ENV_FILE"
    echo ""
    
    if [ -f "$ENV_FILE" ]; then
        info "Configuration actuelle:"
        echo "   DJANGO_ENV: $(grep '^DJANGO_ENV=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)"
        echo "   DEBUG: $(grep '^DEBUG=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)"
        echo "   DB_ENGINE: $(grep '^DB_ENGINE=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)"
        echo ""
    fi
    
    info "Commandes disponibles:"
    cat << 'EOF'
   ./start_local.sh setup          - Configuration initiale complète
   ./start_local.sh start [port]   - Démarrer le serveur (défaut: 8007)
   ./start_local.sh migrate        - Migrations DB
   ./start_local.sh collect        - Collecter les fichiers statiques
   ./start_local.sh superuser      - Créer un superutilisateur
   ./start_local.sh shell          - Ouvrir le shell Django
   ./start_local.sh test [app]     - Exécuter les tests
   ./start_local.sh logs [n]       - Afficher les logs (défaut: 50 lignes)
   ./start_local.sh clean          - Nettoyer les fichiers temporaires
   ./start_local.sh reset          - Reset complet (⚠️ DANGER)
   ./start_local.sh check          - Vérifier les dépendances
   ./start_local.sh info           - Afficher ces informations
EOF
    echo ""
    
    info "Exemples d'utilisation:"
    cat << 'EOF'
   # Configuration initiale
   ./start_local.sh setup

   # Démarrer le serveur sur le port par défaut (8007)
   ./start_local.sh start

   # Démarrer sur un autre port
   ./start_local.sh start 8007

   # Créer un admin
   ./start_local.sh superuser

   # Ouvrir le shell Django
   ./start_local.sh shell
EOF
    echo ""
}

# ============================================================
# SETUP COMPLET
# ============================================================

setup() {
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   🚀 Setup InBoundPR Backend               ║"
    echo "║   Mode: Sans Docker                        ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    
    check_python
    check_structure
    create_env_local
    check_env
    create_structure
    install_deps
    check_deps
    migrate
    collectstatic
    
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   ✅ Setup terminé avec succès !           ║"
    echo "╠════════════════════════════════════════════╣"
    echo "║   Prochaines étapes:                       ║"
    echo "║   1. Créer un superutilisateur:            ║"
    echo "║      ./start_local.sh superuser            ║"
    echo "║                                            ║"
    echo "║   2. Démarrer le serveur:                  ║"
    echo "║      ./start_local.sh start                ║"
    echo "║                                            ║"
    echo "║   3. Accéder à l'admin:                    ║"
    echo "║      http://localhost:8007/admin           ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
}

# ============================================================
# MENU PRINCIPAL
# ============================================================

case "${1:-}" in
    setup) setup ;;
    start|run|serve) check_env; start_server "${2:-8007}" ;;
    migrate|mig) check_env; migrate ;;
    collect|collectstatic|static) check_env; collectstatic ;;
    superuser|createsuperuser|admin) check_env; create_superuser ;;
    shell|sh) check_env; shell ;;
    test|tests) check_env; run_tests "$2" ;;
    logs|log) logs "$2" ;;
    clean|clear) clean ;;
    reset) reset ;;
    check|deps) check_deps ;;
    info|help|--help|-h) show_info ;;
    *)
        error "Commande inconnue: ${1:-}"
        show_info
        exit 1
        ;;
esac