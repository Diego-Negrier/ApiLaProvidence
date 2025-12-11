#!/bin/bash

# ============================================================
# SCRIPT DE GESTION LOCALE - InBoundPR Backend (Sans Docker)
# Version MariaDB
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
VENV_DIR="$HOME/EnvironnementPython/LaProvidence"

# Afficher les chemins pour debug
info "Chemins détectés:"
echo "   Script: $SCRIPT_DIR"
echo "   Back: $BACK_DIR"
echo "   Settings: $SETTINGS_FILE"
echo "   Venv: $VENV_DIR"
echo ""






# ============================================================
# DJANGO
# ============================================================

run_migrations() {
    info "Exécution des migrations..."
    
    cd "$BACK_DIR"
    activate_venv
    
    export $(grep -v '^#' "$ENV_FILE" | xargs 2>/dev/null)
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false

    python manage.py makemigrations
    python manage.py migrate

    if [ $? -eq 0 ]; then
        ok "Migrations appliquées"
    else
        error "Échec des migrations"
        exit 1
    fi
}

collect_static() {
    info "Collecte des fichiers statiques..."
    
    cd "$BACK_DIR"
    activate_venv
    
    export $(grep -v '^#' "$ENV_FILE" | xargs 2>/dev/null)
    export DJANGO_ENV=local

    python manage.py collectstatic --noinput

    if [ $? -eq 0 ]; then
        ok "Fichiers statiques collectés"
    else
        warn "Échec de collecte des statiques (non critique)"
    fi
}

create_superuser() {
    info "Création d'un superutilisateur..."
    
    cd "$BACK_DIR"
    activate_venv
    
    export $(grep -v '^#' "$ENV_FILE" | xargs 2>/dev/null)
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false

    python manage.py createsuperuser
}

start_server() {
    info "Démarrage du serveur Django..."
    
    cd "$BACK_DIR"
    activate_venv
    
    export $(grep -v '^#' "$ENV_FILE" | xargs 2>/dev/null)
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false

    PORT="${PORT:-8000}"
    
    ok "Serveur démarré sur http://127.0.0.1:$PORT"
    ok "Admin disponible sur http://127.0.0.1:$PORT/admin"
    
    python manage.py runserver "0.0.0.0:$PORT"
}

django_shell() {
    info "Ouverture du shell Django..."
    
    cd "$BACK_DIR"
    activate_venv
    
    export $(grep -v '^#' "$ENV_FILE" | xargs 2>/dev/null)
    export DJANGO_ENV=local
    export DOCKER_CONTAINER=false

    python manage.py shell
}


# ============================================================
# SETUP COMPLET
# ============================================================

full_setup() {
    echo ""
    info "========================================="
    info "  SETUP COMPLET - InBoundPR Backend"
    info "========================================="
    echo ""

    check_python
    check_mariadb
    check_structure
    check_env
    check_venv
    activate_venv
    
    create_structure
    install_deps
    

    test_django_db
    run_migrations
    collect_static

    echo ""
    ok "========================================="
    ok "  SETUP TERMINÉ AVEC SUCCÈS !"
    ok "========================================="
    echo ""
    info "Prochaines étapes:"
    echo "   1. Créer un superuser: ./start_local.sh superuser"
    echo "   2. Démarrer le serveur: ./start_local.sh start"
    echo ""
}



show_help() {
    cat << EOF

${B}InBoundPR Backend - Gestion Locale (MariaDB)${NC}

${G}Usage:${NC}
    ./start_local.sh [commande]

${G}Commandes principales:${NC}
    ${Y}setup${NC}          Configuration complète du projet
    ${Y}start${NC}          Démarrer le serveur Django
    ${Y}stop${NC}           Arrêter le serveur (Ctrl+C)

${G}Base de données:${NC}
    ${Y}checkdb${NC}        Vérifier la connexion MariaDB
    ${Y}testdb${NC}         Tester Django -> MariaDB
    ${Y}migrate${NC}        Exécuter les migrations
    ${Y}makemigrations${NC} Créer de nouvelles migrations

${G}Gestion:${NC}
    ${Y}superuser${NC}      Créer un superutilisateur
    ${Y}shell${NC}          Ouvrir le shell Django
    ${Y}static${NC}         Collecter les fichiers statiques

${G}Utilitaires:${NC}
    ${Y}status${NC}         Afficher le statut du système
    ${Y}logs${NC}           Afficher les logs
    ${Y}deps${NC}           Installer les dépendances
    ${Y}help${NC}           Afficher cette aide

${G}Exemples:${NC}
    ./start_local.sh setup          # Première installation
    ./start_local.sh checkdb        # Vérifier MariaDB
    ./start_local.sh migrate        # Appliquer les migrations
    ./start_local.sh superuser      # Créer admin
    ./start_local.sh start          # Démarrer le serveur

${B}Documentation:${NC}
    Backend: http://127.0.0.1:8000
    Admin: http://127.0.0.1:8000/admin

EOF
}

# ============================================================
# COMMANDES
# ============================================================

case "${1:-}" in
    setup)
        full_setup
        ;;
    start|run)
        check_python
        check_mariadb
        check_env
        check_venv
        start_server
        ;;
    checkdb|testdb)
        check_mariadb
        check_env
        check_db_connection
        ;;
    dbtest|django-db)
        test_django_db
        ;;
    migrate)
        check_env
        check_venv
        run_migrations
        ;;
    makemigrations)
        cd "$BACK_DIR"
        activate_venv
        export $(grep -v '^#' "$ENV_FILE" | xargs 2>/dev/null)
        export DJANGO_ENV=local
        python manage.py makemigrations
        ;;
    superuser|createsuperuser)
        check_env
        check_venv
        create_superuser
        ;;
    shell)
        check_env
        check_venv
        django_shell
        ;;
    static|collectstatic)
        check_env
        check_venv
        collect_static
        ;;
    deps|install)
        check_venv
        install_deps
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Commande inconnue: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
