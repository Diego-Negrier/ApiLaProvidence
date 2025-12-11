from rest_framework import status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from .authentication import ClientTokenAuthentication

from clients.models import Client, ClientToken
from livraisons.models import Livreur, Tarif, PointRelais
from .models import *
from .serializers import *


# ============= AUTH VIEWS =============



@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ Permettre l'accès sans authentification
def api_inscription(request):
    """Inscription d'un nouveau client"""
    serializer = InscriptionSerializer(data=request.data)
    
    if serializer.is_valid():
        client = serializer.save()
        
        return Response({
            'message': 'Inscription réussie',
            'user': {
                'id': client.id,
                'username': client.username,
                'email': client.email,
                'prenom': client.prenom,
                'nom': client.nom,
                'telephone': client.telephone,
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from .serializers import LoginSerializer
from clients.models import Client

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Connexion d'un client"""
    print("=== DEBUG LOGIN ===")
    print(f"Request data: {request.data}")
    
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        username_or_email = serializer.validated_data['username_or_email']
        password = serializer.validated_data['password']
        
        print(f"Username/Email: {username_or_email}")

        try:
            # Rechercher par username OU email
            client = Client.objects.get(
                Q(username=username_or_email) | Q(email=username_or_email)
            )
            print(f"Client trouvé: {client.username}")
            
            # Vérifier le mot de passe
            if check_password(password, client.password):
                print("✅ Connexion réussie")

                # Générer un nouveau session_token
                token = client.generate_session_token()
                print(f"🔑 Nouveau session_token généré: {token[:10]}...")

                return Response({
                    'message': 'Connexion réussie',
                    'token': token,
                    'client_id': client.pk,
                    'username': client.username,
                    'email': client.email,
                    'token_expiration': client.token_expiration.isoformat() if client.token_expiration else None,
                    'pk': client.pk,
                }, status=status.HTTP_200_OK)
            else:
                print("❌ Mot de passe incorrect")
                return Response({
                    'error': 'Nom d\'utilisateur ou mot de passe incorrect'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Client.DoesNotExist:
            print(f"❌ Client '{username_or_email}' n'existe pas")
            return Response({
                'error': 'Nom d\'utilisateur ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
    else:
        print(f"❌ Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([ClientTokenAuthentication])  # ✅ Utilisez votre backend
@permission_classes([IsAuthenticated])
def get_client_detail(request, pk):
    """Récupère les détails d'un client"""
    print("=== DEBUG GET CLIENT ===")
    print(f"Request user: {request.user}")
    print(f"Request user pk: {request.user.pk if hasattr(request.user, 'pk') else 'N/A'}")
    print(f"Requested pk: {pk}")
    print(f"Auth header: {request.META.get('HTTP_AUTHORIZATION', 'None')}")
    
    try:
        # Vérifier que l'utilisateur connecté accède à ses propres données
        if request.user.pk != int(pk):
            print(f"❌ Accès refusé: user {request.user.pk} tente d'accéder à {pk}")
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        client = Client.objects.get(pk=pk)
        print(f"✅ Client trouvé: {client.username}")

        return Response({
            'pk': client.pk,
            'username': client.username,
            'email': client.email,
            'prenom': client.prenom,
            'nom': client.nom,
            'telephone': client.telephone,
        }, status=status.HTTP_200_OK)

    except Client.DoesNotExist:
        print(f"❌ Client {pk} non trouvé")
        return Response({
            'error': 'Client non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_logout(request):
    """Déconnexion d'un client"""
    return Response({
        'message': 'Déconnexion réussie'
    }, status=status.HTTP_200_OK)
# ============= CLIENT VIEWS =============


# ============================================
# PARAMÈTRES GÉNÉRAUX DU CLIENT
# ============================================

@api_view(['GET', 'PUT'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def client_parametre(request, pk_client):
    """
    GET/PUT /api/<pk_client>/parametre/
    Récupérer ou mettre à jour les informations générales du client
    """
    client = get_object_or_404(Client, pk=pk_client)

    # Vérifier que l'utilisateur accède à son propre profil
    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ClientParametreSerializer(client)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ClientParametreSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# ADRESSES DE FACTURATION
# ============================================

@api_view(['GET', 'POST'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def adresse_facturation_list(request, pk_client):
    """
    GET/POST /client/update/<pk_client>/adresse_facturation/
    Liste toutes les adresses de facturation ou en ajoute une nouvelle
    """
    client = get_object_or_404(Client, pk=pk_client)

    # Vérifier que l'utilisateur accède à son propre profil
    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        adresses = AdresseFacturation.objects.filter(client=client)
        serializer = AdresseFacturationSerializer(adresses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Extraire les données de l'adresse
        adresse_data = request.data.get('adresse_facturation', request.data)
        
        serializer = AdresseFacturationSerializer(data=adresse_data)
        if serializer.is_valid():
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def adresse_facturation_detail(request, pk_client, pk_adresse):
    """
    PUT/DELETE /client/update/<pk_client>/adresse_facturation/<pk_adresse>/
    Modifier ou supprimer une adresse de facturation spécifique
    """
    client = get_object_or_404(Client, pk=pk_client)

    # Vérifier que l'utilisateur accède à son propre profil
    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    adresse = get_object_or_404(AdresseFacturation, pk=pk_adresse, client=client)

    if request.method == 'PUT':
        # Extraire les données de l'adresse
        adresse_data = request.data.get('adresse_facturation', request.data)
        
        serializer = AdresseFacturationSerializer(adresse, data=adresse_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        adresse.delete()
        return Response(
            {'message': 'Adresse de facturation supprimée avec succès'},
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================
# ADRESSES DE LIVRAISON
# ============================================

@api_view(['GET', 'POST'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def adresse_livraison_list(request, pk_client):
    """
    GET/POST /client/update/<pk_client>/adresse_livraison/
    Liste toutes les adresses de livraison ou en ajoute une nouvelle
    """
    client = get_object_or_404(Client, pk=pk_client)

    # Vérifier que l'utilisateur accède à son propre profil
    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        adresses = AdresseLivraison.objects.filter(client=client)
        serializer = AdresseLivraisonSerializer(adresses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Extraire les données de l'adresse
        adresse_data = request.data.get('adresse_livraison', request.data)
        
        serializer = AdresseLivraisonSerializer(data=adresse_data)
        if serializer.is_valid():
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def adresse_livraison_detail(request, pk_client, pk_adresse):
    """
    PUT/DELETE /client/update/<pk_client>/adresse_livraison/<pk_adresse>/
    Modifier ou supprimer une adresse de livraison spécifique
    """
    client = get_object_or_404(Client, pk=pk_client)

    # Vérifier que l'utilisateur accède à son propre profil
    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    adresse = get_object_or_404(AdresseLivraison, pk=pk_adresse, client=client)

    if request.method == 'PUT':
        # Extraire les données de l'adresse
        adresse_data = request.data.get('adresse_livraison', request.data)
        
        serializer = AdresseLivraisonSerializer(adresse, data=adresse_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        adresse.delete()
        return Response(
            {'message': 'Adresse de livraison supprimée avec succès'},
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================
# CHANGEMENT DE MOT DE PASSE
# ============================================

@api_view(['PUT'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request, pk_client):
    """
    PUT /client/update/<pk_client>/password/
    Changer le mot de passe du client
    """
    client = get_object_or_404(Client, pk=pk_client)

    # Vérifier que l'utilisateur accède à son propre profil
    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    serializer = PasswordChangeSerializer(data=request.data)
    
    if serializer.is_valid():
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # Vérifier l'ancien mot de passe
        if not client.check_password(old_password):
            return Response(
                {'error': 'Ancien mot de passe incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Définir le nouveau mot de passe
        client.set_password(new_password)
        client.save()

        return Response(
            {'message': 'Mot de passe modifié avec succès'},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)















# ============= PANIER VIEWS =============
@api_view(['GET', 'POST'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def panier_view(request, pk_client):
    """GET/POST /api/<pk-client>/panier"""
    client = get_object_or_404(Client, pk=pk_client)

    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    panier, created = Panier.objects.get_or_create(client=client, commande__isnull=True)

    if request.method == 'GET':
        # Optimisation : précharger les relations
        panier = Panier.objects.prefetch_related(
            'lignes__produit__fournisseur',
            'lignes__produit__categorie',
            'lignes__produit__souscategorie'
        ).get(pk=panier.pk)
        serializers = PanierSerializer(panier)
        return Response(serializers.data)

    elif request.method == 'POST':
        # Ajout d'un produit au panier
        produit_id = request.data.get('produit_id')
        quantite = request.data.get('quantite', 1)

        produit = get_object_or_404(Produit, pk=produit_id)

        ligne, created = LignePanier.objects.get_or_create(
            panier=panier,
            produit=produit,
            defaults={'quantite': quantite}
        )

        if not created:
            ligne.quantite += int(quantite)
            ligne.save()

        # Optimisation : précharger les relations
        panier = Panier.objects.prefetch_related(
            'lignes__produit__fournisseur',
            'lignes__produit__categorie',
            'lignes__produit__souscategorie'
        ).get(pk=panier.pk)
        serializers = PanierSerializer(panier)
        return Response(serializers.data)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def ligne_panier_view(request, pk_client, pk_ligne):
    """GET/PUT/DELETE /api/<pk-client>/panier/<pk-ligne>"""
    client = get_object_or_404(Client, pk=pk_client)

    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    # Optimisation : précharger les relations
    ligne = get_object_or_404(
        LignePanier.objects.select_related(
            'produit__fournisseur',
            'produit__categorie',
            'produit__souscategorie',
            'panier'
        ),
        pk=pk_ligne,
        panier__client=client
    )

    if request.method == 'GET':
        serializers = LignePanierSerializer(ligne)
        return Response(serializers.data)

    elif request.method == 'PUT':
        serializers = LignePanierSerializer(ligne, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            # Recharger avec les relations
            ligne = LignePanier.objects.select_related(
                'produit__fournisseur',
                'produit__categorie',
                'produit__souscategorie'
            ).get(pk=ligne.pk)
            serializers = LignePanierSerializer(ligne)
            return Response(serializers.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        ligne.delete()
        return Response({'message': 'Ligne supprimée'}, status=status.HTTP_204_NO_CONTENT)


# ============= COMMANDE VIEWS =============
@api_view(['GET', 'POST'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def commandes_view(request, pk_client):
    """GET/POST /api/<pk-client>/commandes"""
    client = get_object_or_404(Client, pk=pk_client)

    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        commandes = Commande.objects.filter(client=client).order_by('-date_commande')

        # Séparer les commandes en cours et l'historique
        statuts_en_cours = ['en_attente', 'en_cours', 'en_livraison']
        statuts_termines = ['terminee', 'annulee']

        commandes_en_cours = commandes.filter(statut__in=statuts_en_cours)
        historique_commandes = commandes.filter(statut__in=statuts_termines)

        # Sérialiser les deux listes
        serializer_en_cours = CommandeSerializer(commandes_en_cours, many=True)
        serializer_historique = CommandeSerializer(historique_commandes, many=True)

        # Retourner la structure attendue par le frontend
        return Response({
            'commandes_en_cours': serializer_en_cours.data,
            'historique_commandes': serializer_historique.data,
            'commandes_statut_liste': [
                {'key': 'en_attente', 'label': 'En attente'},
                {'key': 'en_cours', 'label': 'En cours'},
                {'key': 'en_livraison', 'label': 'En livraison'},
                {'key': 'terminee', 'label': 'Terminée'},
                {'key': 'annulee', 'label': 'Annulée'},
            ]
        })
    
    elif request.method == 'POST':
        # Transformer le panier en commande
        panier = get_object_or_404(Panier, client=client, commande__isnull=True)
        
        if not LignePanier:
            return Response({'error': 'Le panier est vide'}, status=status.HTTP_400_BAD_REQUEST)
        
        commande = Commande.objects.create(
            client=client,
            total=sum(l.quantite * l.prix_unitaire for l in LignePanier.all()),
            statut='EN_ATTENTE'
        )
        
        # Associer le panier à la commande
        panier.commande = commande
        panier.save()
        
        serializers = CommandeDetailSerializer(commande)
        return Response(serializers.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def commande_detail_view(request, pk_client, pk_commande):
    """GET /api/<pk-client>/commandes/<pk-commande>"""
    client = get_object_or_404(Client, pk=pk_client)

    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    commande = get_object_or_404(Commande, pk=pk_commande, client=client)
    serializers = CommandeDetailSerializer(commande)
    return Response(serializers.data)


# ============= FOURNISSEURS DU CLIENT =============
@api_view(['GET'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def client_fournisseurs_view(request, pk_client):
    """GET /api/<pk-client>/fournisseurs"""
    client = get_object_or_404(Client, pk=pk_client)

    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les fournisseurs des produits commandés par le client
    fournisseurs = Fournisseur.objects.filter(
        produit__lignepanier__panier__client=client
    ).distinct()
    
    serializers = FournisseurSerializer(fournisseurs, many=True)
    return Response(serializers.data)


# ============= MAGASIN (vue client) =============
@api_view(['GET'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def magasin_client_view(request, pk_client):
    """GET /api/<pk-client>/magasin"""
    client = get_object_or_404(Client, pk=pk_client)

    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)

    produits = Produit.objects.filter(est_actif=True)
    serializers = ProduitSerializer(produits, many=True)
    return Response(serializers.data)


@api_view(['GET'])
@authentication_classes([ClientTokenAuthentication])
@permission_classes([IsAuthenticated])
def magasin_produit_client_view(request, pk_client, pk_produit):
    """GET /api/<pk-client>/magasin/<pk-produit>"""
    client = get_object_or_404(Client, pk=pk_client)

    if client.username != request.user.username:
        return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    produit = get_object_or_404(Produit, pk=pk_produit)
    serializers = ProduitDetailSerializer(produit)
    return Response(serializers.data)


# ============= FOURNISSEURS (ADMIN) =============
class FournisseurViewSet(viewsets.ModelViewSet):
    """GET /api/fournisseurs et GET/PUT /api/fournisseurs/<pk>"""
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get', 'post'])
    def reglementation(self, request, pk=None):
        """GET/POST /api/fournisseurs/<pk>/reglementation"""
        fournisseur = self.get_object()
        
        if request.method == 'GET':
            reglementations = Reglementation.objects.filter(fournisseur=fournisseur)
            serializers = ReglementationSerializer(reglementations, many=True)
            return Response(serializers.data)
        
        elif request.method == 'POST':
            serializers = ReglementationSerializer(data=request.data)
            if serializers.is_valid():
                serializers.save(fournisseur=fournisseur)
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post'])
    def certification(self, request, pk=None):
        """GET/POST /api/fournisseurs/<pk>/certification"""
        fournisseur = self.get_object()
        
        if request.method == 'GET':
            certifications = Certification.objects.filter(fournisseur=fournisseur)
            serializers = CertificationSerializer(certifications, many=True)
            return Response(serializers.data)
        
        elif request.method == 'POST':
            serializers = CertificationSerializer(data=request.data)
            if serializers.is_valid():
                serializers.save(fournisseur=fournisseur)
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


# ============= ROUTES GLOBALES =============
@api_view(['GET'])
@permission_classes([AllowAny])
def magasin_view(request):
    """GET /api/magasin"""
    # Optimisation: select_related pour les relations ForeignKey
    produits = Produit.objects.filter(
        est_actif=True
    ).select_related(
        'fournisseur',
        'categorie',
        'souscategorie',
        'soussouscategorie'
    )
    serializers = ProduitSerializer(produits, many=True)
    return Response(serializers.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def magasin_produit_view(request, pk_produit):
    """GET /api/magasin/<pk-produit>"""
    produit = get_object_or_404(Produit, pk=pk_produit)
    serializers = ProduitDetailSerializer(produit)
    return Response(serializers.data)


# ============= CATEGORIES =============
@api_view(['GET'])
@permission_classes([AllowAny])
def categories_view(request):
    """GET /api/categories"""
    categories = Categorie.objects.filter(
        est_active=True
    ).prefetch_related(
        'souscategories__soussouscategories'
    ).order_by('ordre')
    from .serializers import CategorieSerializer
    serializers = CategorieSerializer(categories, many=True)
    return Response(serializers.data)


# ============= FOURNISSEURS PUBLICS =============
@api_view(['GET'])
@permission_classes([AllowAny])
def fournisseurs_view(request):
    """GET /api/fournisseurs"""
    fournisseurs = Fournisseur.objects.all().order_by('-date_ajoutee')
    from .serializers import FournisseurSerializer
    serializers = FournisseurSerializer(fournisseurs, many=True)
    return Response(serializers.data)


# ============= LIVREURS =============
@api_view(['GET'])
@permission_classes([AllowAny])
def livreurs_view(request):
    """
    GET /api/livreur/
    Récupère la liste de tous les livreurs actifs
    """
    livreurs = Livreur.objects.filter(est_actif=True).prefetch_related('tarifs').order_by('nom')
    from .serializers import LivreurSerializer
    serializer = LivreurSerializer(livreurs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def livreur_detail_view(request, pk_livreur):
    """
    GET /api/livreur/<pk>/
    Récupère les détails d'un livreur spécifique
    """
    livreur = get_object_or_404(Livreur.objects.prefetch_related('tarifs'), pk=pk_livreur)
    from .serializers import LivreurSerializer
    serializer = LivreurSerializer(livreur)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def livreur_tarifs_view(request, pk_livreur):
    """
    GET /api/livreur/<pk>/tarifs/
    Récupère les tarifs d'un livreur
    """
    livreur = get_object_or_404(Livreur, pk=pk_livreur)
    tarifs = livreur.tarifs.all().order_by('poids_min')
    from .serializers import TarifSerializer
    serializer = TarifSerializer(tarifs, many=True)
    return Response(serializer.data)


