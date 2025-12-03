#!/bin/bash

set -euo pipefail

# ==========================================
# 🌐 CONFIGURATION PROJET
# ==========================================

PROJECT_NAME="ApiLaProvidence"
PROJECT_URL="https://api-laprovidence.data-worlds.com"
GIT_REMOTE="origin"
GIT_BRANCH="main"

# ==========================================
# 🐳 CONFIGURATION DOCKER
# ==========================================

IMAGE_NAME="apilaprovidence"
IMAGE_TAG="latest"
FULL_IMAGE="$IMAGE_NAME:$IMAGE_TAG"
CONTAINER_NAME="apilaprovidence"
SERVICE_NAME="apilaprovidence"

# ==========================================
# 📁 CHEMINS
# ==========================================

# Local (Mac)
LOCAL_SOURCE_PATH="back"
LOCAL_ENV_PATH="back/.env.production"
BUILD_CONTEXT="./$LOCAL_SOURCE_PATH"

# NAS
NAS_HOST="dataworlds"
NAS_PROJECT_PATH="/volume1/web/ProjetLaProvidence/ApiLaProvidence"
NAS_DOCKER_PATH="/usr/local/bin/docker"

# ==========================================
# 🎨 COLORS & LOGGING
# ==========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_step() {
    echo -e "\n${BLUE}🔷 $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_git() {
    echo -e "${MAGENTA}🔀 $1${NC}"
}

# ==========================================
# 📋 BANNER
# ==========================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}🚀 Deployment Script - $PROJECT_NAME${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Project:  ${GREEN}$PROJECT_NAME${NC}"
echo -e "  URL:      ${BLUE}$PROJECT_URL${NC}"
echo -e "  NAS Host: ${YELLOW}$NAS_HOST${NC}"
echo -e "  Image:    ${CYAN}$FULL_IMAGE${NC}"
echo -e "  Branch:   ${MAGENTA}$GIT_BRANCH${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ==========================================
# 🔀 SYNCHRONISATION GIT
# ==========================================

log_step "Git Synchronization"

if [ ! -d ".git" ]; then
    log_error "Not a git repository"
    exit 1
fi

log_git "Current status:"
git status --short

echo ""

if git diff-index --quiet HEAD -- 2>/dev/null; then
    log_info "No changes to commit"
else
    echo ""
    read -p "📝 Commit changes? (y/n): " -n 1 -r COMMIT_REPLY
    echo ""

    if [[ $COMMIT_REPLY =~ ^[Yy]$ ]]; then
        log_git "Adding all files..."
        git add .

        echo ""
        log_git "Files to be committed:"
        git status --short
        echo ""

        read -p "💬 Commit message: " COMMIT_MSG

        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="Update $(date +%Y-%m-%d\ %H:%M:%S)"
            log_info "Using default message: $COMMIT_MSG"
        fi

        if git commit -m "$COMMIT_MSG"; then
            log_success "Changes committed"
        else
            log_error "Commit failed"
            exit 1
        fi
    else
        log_warning "Skipping commit"
    fi
fi

UNPUSHED_COMMITS=$(git log "$GIT_REMOTE/$GIT_BRANCH..HEAD" --oneline 2>/dev/null | wc -l | tr -d ' ')

if [ "$UNPUSHED_COMMITS" -gt 0 ]; then
    echo ""
    log_git "Found $UNPUSHED_COMMITS unpushed commit(s)"

    echo ""
    git log "$GIT_REMOTE/$GIT_BRANCH..HEAD" --oneline --decorate -5
    echo ""

    read -p "📤 Push to $GIT_REMOTE/$GIT_BRANCH? (y/n): " -n 1 -r PUSH_REPLY
    echo ""

    if [[ $PUSH_REPLY =~ ^[Yy]$ ]]; then
        log_git "Pushing to $GIT_REMOTE/$GIT_BRANCH..."

        if git push "$GIT_REMOTE" "$GIT_BRANCH"; then
            log_success "Push successful"
        else
            log_error "Push failed"
            echo ""
            read -p "❓ Continue deployment anyway? (y/n): " -n 1 -r CONTINUE_REPLY
            echo ""

            if [[ ! $CONTINUE_REPLY =~ ^[Yy]$ ]]; then
                log_error "Deployment cancelled"
                exit 1
            fi
        fi
    else
        log_warning "Skipping push"
    fi
else
    log_success "Already up to date with $GIT_REMOTE/$GIT_BRANCH"
fi

echo ""
log_git "Latest commit:"
git log -1 --oneline --decorate
echo ""

# ==========================================
# ✅ VERIFICATION DOCKER
# ==========================================

log_step "Checking Docker..."

if ! docker version &>/dev/null; then
    log_error "Docker not found or not running"
    exit 1
fi

log_success "Docker ready"

# ==========================================
# ✅ VERIFICATION DOCKERFILE
# ==========================================

log_step "Locating Dockerfile..."

if [ ! -f "$BUILD_CONTEXT/Dockerfile" ]; then
    log_error "Dockerfile not found at: $BUILD_CONTEXT/Dockerfile"
    log_info "Current directory: $(pwd)"
    exit 1
fi

log_success "Found Dockerfile at $BUILD_CONTEXT/Dockerfile"

# ==========================================
# ✅ SYNCHRONISATION FICHIERS DE CONFIG
# ==========================================

log_step "Syncing configuration files to NAS..."

ssh "$NAS_HOST" "mkdir -p $NAS_PROJECT_PATH" || {
    log_error "Failed to create directory on NAS"
    exit 1
}

# 1. Sync .env.production
if [ -f "$LOCAL_ENV_PATH" ]; then
    log_info "Syncing .env.production..."

    # Créer le répertoire back/ sur le NAS
    ssh "$NAS_HOST" "mkdir -p $NAS_PROJECT_PATH/back" || {
        log_error "Failed to create back/ directory on NAS"
        exit 1
    }

    if cat "$LOCAL_ENV_PATH" | ssh "$NAS_HOST" "cat > $NAS_PROJECT_PATH/back/.env.production"; then
        REMOTE_SIZE=$(ssh "$NAS_HOST" "wc -c < $NAS_PROJECT_PATH/back/.env.production" 2>/dev/null || echo "0")
        LOCAL_SIZE=$(wc -c < "$LOCAL_ENV_PATH")

        if [ "$REMOTE_SIZE" -eq "$LOCAL_SIZE" ]; then
            log_success ".env.production synced to back/.env.production ($REMOTE_SIZE bytes)"
        else
            log_warning "Size mismatch: local=$LOCAL_SIZE, remote=$REMOTE_SIZE"
        fi
    else
        log_error "Failed to sync .env.production"
        exit 1
    fi
else
    log_error ".env.production NOT FOUND at $LOCAL_ENV_PATH"
    exit 1
fi

# 2. Sync docker-compose.yml (PRODUCTION VERSION)
COMPOSE_LOCAL_PATH="docker-compose.yml"
if [ -f "$COMPOSE_LOCAL_PATH" ]; then
    log_info "Syncing docker-compose.yml to NAS..."
    log_info "This will OVERWRITE the docker-compose.yml on NAS"

    if cat "$COMPOSE_LOCAL_PATH" | ssh "$NAS_HOST" "cat > $NAS_PROJECT_PATH/docker-compose.yml"; then
        log_success "docker-compose.yml synced to NAS"
        log_info "✓ Using pre-built image (no build: section)"
        log_info "✓ Using correct env file (./back/.env.production)"
    else
        log_error "Failed to sync docker-compose.yml"
        exit 1
    fi

    # Vérifier que le fichier sur NAS n'a pas de section 'build:'
    if ssh "$NAS_HOST" "grep -q 'build:' $NAS_PROJECT_PATH/docker-compose.yml"; then
        log_error "ERROR: docker-compose.yml on NAS still contains 'build:' section!"
        log_error "This will cause deployment to fail. Check the sync process."
        exit 1
    else
        log_success "Verified: No 'build:' section in docker-compose.yml on NAS"
    fi
else
    log_error "docker-compose.yml NOT FOUND at $COMPOSE_LOCAL_PATH"
    exit 1
fi

log_success "All configuration files synchronized"

# ==========================================
# 🧹 NETTOYAGE DES ANCIENNES IMAGES LOCALES
# ==========================================

log_step "Cleaning up old local images..."

# Compter et afficher les images existantes
EXISTING_IMAGES=$(docker images "$IMAGE_NAME" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | wc -l | tr -d ' ')
if [ "$EXISTING_IMAGES" -gt 0 ]; then
    log_info "Found $EXISTING_IMAGES existing $IMAGE_NAME image(s):"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
    echo ""
fi

# Supprimer TOUTES les images localement
log_info "Removing all existing $IMAGE_NAME images..."
docker images "$IMAGE_NAME" -q | xargs -r docker rmi -f 2>/dev/null || true

# Supprimer les images dangling
log_info "Removing dangling images..."
docker images -f "dangling=true" -q | xargs -r docker rmi -f 2>/dev/null || true

log_success "Local cleanup complete"

# ==========================================
# 🏗️  BUILD DE L'IMAGE DOCKER
# ==========================================

log_step "Building Docker image..."
log_info "Image name: $FULL_IMAGE"
log_info "Platform:   linux/amd64"
log_info "Context:    $BUILD_CONTEXT"

BUILD_START=$(date +%s)

if docker buildx build \
    --platform linux/amd64 \
    --tag "$FULL_IMAGE" \
    --load \
    "$BUILD_CONTEXT"; then

    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))

    log_success "Image built successfully in ${BUILD_TIME}s"
else
    log_error "Docker build failed"
    exit 1
fi

# ==========================================
# 📊 INFORMATIONS SUR L'IMAGE
# ==========================================

log_step "Inspecting image..."

IMAGE_COUNT=$(docker images "$FULL_IMAGE" --format "{{.ID}}" | wc -l | tr -d ' ')

if [ "$IMAGE_COUNT" -eq 0 ]; then
    log_error "No image found after build!"
    exit 1
elif [ "$IMAGE_COUNT" -gt 1 ]; then
    log_warning "Multiple images found with tag $FULL_IMAGE!"
    docker images "$FULL_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
    log_error "This should not happen. Aborting."
    exit 1
fi

IMAGE_ID=$(docker images "$FULL_IMAGE" --format "{{.ID}}")
IMAGE_SIZE=$(docker images "$FULL_IMAGE" --format "{{.Size}}")

log_info "Image ID:   $IMAGE_ID"
log_info "Image Size: $IMAGE_SIZE"
log_success "Exactly 1 image found (no duplicates)"

# ==========================================
# 💾 SAUVEGARDE DE L'IMAGE (COMPRESSÉE)
# ==========================================

log_step "Saving and compressing Docker image..."

TAR_FILE="/tmp/${IMAGE_NAME}_${IMAGE_TAG}.tar.gz"
rm -f "$TAR_FILE"

# Utiliser pigz (gzip parallèle) si disponible
if command -v pigz &> /dev/null; then
    log_info "Saving image with parallel compression (pigz)..."
    COMPRESS_CMD="pigz -1"
else
    log_info "Saving image with standard compression (gzip)..."
    COMPRESS_CMD="gzip -1"
fi

if docker save "$FULL_IMAGE" | $COMPRESS_CMD > "$TAR_FILE"; then
    TAR_SIZE=$(du -h "$TAR_FILE" | cut -f1)
    log_success "Image saved and compressed: $TAR_FILE ($TAR_SIZE)"
else
    log_error "Failed to save image"
    exit 1
fi

# ==========================================
# 📤 TRANSFERT VERS LE NAS
# ==========================================

log_step "Transferring image to NAS..."
log_info "Destination: $NAS_HOST:$NAS_PROJECT_PATH"
log_info "This may take several minutes depending on image size..."

TRANSFER_START=$(date +%s)

ssh "$NAS_HOST" "mkdir -p $NAS_PROJECT_PATH"

# Utiliser pv si disponible pour afficher la progression
if command -v pv &> /dev/null; then
    log_info "Transferring with progress indicator..."
    if pv "$TAR_FILE" | ssh "$NAS_HOST" "cat > $NAS_PROJECT_PATH/${IMAGE_NAME}_${IMAGE_TAG}.tar.gz"; then
        TRANSFER_END=$(date +%s)
        TRANSFER_TIME=$((TRANSFER_END - TRANSFER_START))
        log_success "Transfer completed in ${TRANSFER_TIME}s"
    else
        log_error "Transfer failed"
        rm -f "$TAR_FILE"
        exit 1
    fi
else
    log_info "Transferring (install 'pv' for progress indicator)..."
    if cat "$TAR_FILE" | ssh "$NAS_HOST" "cat > $NAS_PROJECT_PATH/${IMAGE_NAME}_${IMAGE_TAG}.tar.gz"; then
        TRANSFER_END=$(date +%s)
        TRANSFER_TIME=$((TRANSFER_END - TRANSFER_START))
        log_success "Transfer completed in ${TRANSFER_TIME}s"
    else
        log_error "Transfer failed"
        rm -f "$TAR_FILE"
        exit 1
    fi
fi

# ==========================================
# 🔄 CHARGEMENT DE L'IMAGE SUR LE NAS
# ==========================================

log_step "Loading image on NAS..."

log_info "Removing ALL existing $IMAGE_NAME images on NAS..."
ssh "$NAS_HOST" "$NAS_DOCKER_PATH images | grep '$IMAGE_NAME' | awk '{print \$3}' | xargs -r $NAS_DOCKER_PATH rmi -f" 2>/dev/null || true

log_info "Decompressing and loading new image..."
log_warning "This step can take 2-5 minutes - please wait..."
echo ""

LOAD_START=$(date +%s)

DECOMPRESS_CMD="gunzip -c"
if ssh "$NAS_HOST" "command -v pigz" &>/dev/null; then
    log_info "Using pigz for parallel decompression on NAS"
    DECOMPRESS_CMD="pigz -dc"
fi

if ssh "$NAS_HOST" "$DECOMPRESS_CMD $NAS_PROJECT_PATH/${IMAGE_NAME}_${IMAGE_TAG}.tar.gz | $NAS_DOCKER_PATH load"; then
    LOAD_END=$(date +%s)
    LOAD_TIME=$((LOAD_END - LOAD_START))

    log_success "Image loaded on NAS in ${LOAD_TIME}s"

    NAS_IMAGE_COUNT=$(ssh "$NAS_HOST" "$NAS_DOCKER_PATH images '$FULL_IMAGE' --format '{{.ID}}'" | wc -l | tr -d ' ')

    if [ "$NAS_IMAGE_COUNT" -eq 1 ]; then
        NAS_IMAGE_ID=$(ssh "$NAS_HOST" "$NAS_DOCKER_PATH images '$FULL_IMAGE' --format '{{.ID}}'")
        log_success "Exactly 1 image on NAS (no duplicates)"
        log_info "NAS Image ID: $NAS_IMAGE_ID"
    else
        log_warning "Found $NAS_IMAGE_COUNT images on NAS (expected 1)"
        ssh "$NAS_HOST" "$NAS_DOCKER_PATH images '$IMAGE_NAME' --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'"
    fi
else
    log_error "Failed to load image on NAS"
    rm -f "$TAR_FILE"
    exit 1
fi

# ==========================================
# 🧹 NETTOYAGE NAS
# ==========================================

log_step "Cleaning up on NAS..."

ssh "$NAS_HOST" "$NAS_DOCKER_PATH images -f 'dangling=true' -q | xargs -r $NAS_DOCKER_PATH rmi -f" 2>/dev/null || true

log_info "Removing compressed archive from NAS..."
ssh "$NAS_HOST" "rm -f $NAS_PROJECT_PATH/${IMAGE_NAME}_${IMAGE_TAG}.tar.gz" || true

log_success "NAS cleanup complete"

# ==========================================
# 🚀 DEPLOIEMENT SUR NAS
# ==========================================

log_step "Deploying $PROJECT_NAME on NAS..."
log_info "Service:  $SERVICE_NAME"
log_info "Location: $NAS_PROJECT_PATH"

log_info "Stopping existing container..."
ssh "$NAS_HOST" "cd $NAS_PROJECT_PATH && $NAS_DOCKER_PATH compose down $SERVICE_NAME" 2>/dev/null || true

log_info "Starting new container (using pre-built image)..."
log_warning "Using --no-build flag to prevent rebuilding..."

if ssh "$NAS_HOST" "cd $NAS_PROJECT_PATH && $NAS_DOCKER_PATH compose up -d --no-build $SERVICE_NAME"; then
    log_success "Container started successfully"
else
    log_error "Failed to start container"
    exit 1
fi

log_info "Waiting for container to be ready..."
sleep 5

# ==========================================
# ✅ VERIFICATION DU DEPLOIEMENT
# ==========================================

log_step "Verifying deployment..."

CONTAINER_STATUS=$(ssh "$NAS_HOST" "$NAS_DOCKER_PATH ps --filter name=$CONTAINER_NAME --format '{{.Status}}'" || echo "not found")

if [[ "$CONTAINER_STATUS" == *"Up"* ]]; then
    log_success "Container is running"
    log_info "Status: $CONTAINER_STATUS"
else
    log_error "Container is not running properly"
    log_info "Status: $CONTAINER_STATUS"

    log_info "Container logs:"
    ssh "$NAS_HOST" "$NAS_DOCKER_PATH logs --tail 50 $CONTAINER_NAME" || true
    exit 1
fi

log_info "Recent logs:"
ssh "$NAS_HOST" "$NAS_DOCKER_PATH logs --tail 20 $CONTAINER_NAME" || true

# ==========================================
# 📦 COLLECTSTATIC
# ==========================================

log_step "Running collectstatic..."

ssh "$NAS_HOST" "$NAS_DOCKER_PATH exec $CONTAINER_NAME python manage.py collectstatic --noinput --clear" || {
    log_warning "Collectstatic failed (non-critical)"
}

log_success "Static files collected"

# ==========================================
# 🧹 NETTOYAGE LOCAL
# ==========================================

log_step "Cleaning up local files..."
rm -f "$TAR_FILE"
log_success "Local cleanup complete"

# ==========================================
# 🎉 RÉSUMÉ
# ==========================================

TOTAL_TIME=$(($(date +%s) - BUILD_START))
LAST_COMMIT=$(git log -1 --oneline --decorate)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Deployment Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Project:       ${CYAN}$PROJECT_NAME${NC}"
echo -e "  URL:           ${BLUE}$PROJECT_URL${NC}"
echo -e "  Git Commit:    ${MAGENTA}$LAST_COMMIT${NC}"
echo -e "  Image:         ${CYAN}$FULL_IMAGE${NC}"
echo -e "  Image ID:      ${CYAN}$IMAGE_ID${NC}"
echo -e "  Image Size:    ${CYAN}$IMAGE_SIZE${NC}"
echo -e "  Container:     ${GREEN}$CONTAINER_STATUS${NC}"
echo -e "  Build Time:    ${YELLOW}${BUILD_TIME}s${NC}"
echo -e "  Transfer Time: ${YELLOW}${TRANSFER_TIME}s${NC}"
echo -e "  Load Time:     ${YELLOW}${LOAD_TIME}s${NC}"
echo -e "  Total Time:    ${YELLOW}${TOTAL_TIME}s${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}🌐 Visit: $PROJECT_URL${NC}"
echo ""

exit 0
