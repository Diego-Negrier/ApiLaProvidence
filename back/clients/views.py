
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import logging
import json

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password,make_password
from django.utils import timezone

from .utilis import client_login_required
from .models import (
                    Client,
                    AdresseFacturation,
                    AdresseLivraison,
                    NavigationLog)



logger = logging.getLogger(__name__)



##################################################################
##################### CONNEXION ####################################
##################################################################

@csrf_exempt
def inscription(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            # Vérifiez si l'email est déjà utilisé
            if Client.objects.filter(email=email).exists():
                return JsonResponse({"message": "Cet email est déjà utilisé."}, status=400)

            # Hacher le mot de passe avant de le sauvegarder
            client = Client(username=username, email=email, password=make_password(password))
            client.save()

            return JsonResponse({"message": "Inscription réussie."}, status=201)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=400)

    return JsonResponse({"message": "Méthode non autorisée."}, status=405)


@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            # Charger les données de la requête
            data = json.loads(request.body)
            username_or_email = data.get('username_or_email')  # Peut être un email ou un nom d'utilisateur
            password = data.get('password')

            # Log des données reçues pour le débogage (à éviter en production)
            logger.debug(f'Requête de connexion reçue: username_or_email={username_or_email}')

            # Chercher l'utilisateur par email ou nom d'utilisateur
            client = None
            if '@' in username_or_email:
                # Recherche par email
                client = get_object_or_404(Client, email=username_or_email)
            else:
                # Recherche par nom d'utilisateur
                client = get_object_or_404(Client, username=username_or_email)

            # Log pour vérifier le mot de passe en base (évidemment à ne pas faire en production)
            logger.debug(f'Mot de passe de l\'utilisateur en base: {client.password}')

            # Vérifier le mot de passe avec la méthode check_password
            if check_password(password, client.password):
                # Mettre à jour la date de dernier login et générer un nouveau token de session
                client.last_login = timezone.now()
                client.generate_session_token()  # Assurez-vous que cette méthode existe dans votre modèle
                client.save()

                logger.info(f'Session token généré pour {username_or_email}')

                # Retourner la réponse avec le token de session et l'expiration
                return JsonResponse({
                    'message': 'Connexion réussie',
                    'token': client.session_token,
                    'username': client.username,
                    'token_expiration': client.token_expiration.isoformat(),
                    'pk': client.pk,
                    'email': client.email,
                }, status=200)
            else:
                logger.warning(f'Erreur de connexion pour {username_or_email} - Mot de passe incorrect')
                return JsonResponse({'message': 'Identifiants incorrects'}, status=401)
        except Exception as e:
            # Log de l'erreur
            logger.error(f'Erreur lors de la tentative de connexion: {e}')
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def logout(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Récupérer les données envoyées dans la requête
            token = data.get('token')

            # Récupérer le client via le token de session
            client = get_object_or_404(Client, session_token=token)

            # Réinitialiser le token de session et l'expiration
            client.session_token = None
            client.token_expiration = None
            client.save()

            return JsonResponse({"detail": "Déconnexion réussie"}, status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


##################################################################
##################### CLIENTS ####################################
##################################################################

@csrf_exempt
@client_login_required
def view_client(request, pk):
    if request.method == 'GET':
        client = get_object_or_404(Client, pk=pk)

        # Récupération des informations du client
        data = {
            'pk': client.pk,
            'username': client.username,

            'prenom': client.prenom,
            'nom': client.nom,
            'email': client.email,
            'adresse_facturation': [],
            'adresse_livraison': [],
        }

        # Récupérer toutes les adresses de facturation si elles existent
        adresse_facturation_list = client.adresse_facturation.all()  # Utilisez .all() pour obtenir une liste
        for adresse_facturation in adresse_facturation_list:
            data['adresse_facturation'].append({
                'pk': adresse_facturation.pk,
                'adresse': adresse_facturation.adresse,
                'code_postal': adresse_facturation.code_postal,
                'ville': adresse_facturation.ville,
                'pays': adresse_facturation.pays,
            })

        # Récupérer toutes les adresses de livraison si elles existent
        adresse_livraison_list = client.adresse_livraison.all()  # Utilisez .all() pour obtenir une liste
        for adresse_livraison in adresse_livraison_list:
            data['adresse_livraison'].append({
                'pk': adresse_livraison.pk,
                'adresse': adresse_livraison.adresse,
                'code_postal': adresse_livraison.code_postal,
                'ville': adresse_livraison.ville,
                'pays': adresse_livraison.pays,
            })

        return JsonResponse(data, safe=False)

    return JsonResponse({'message': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
@client_login_required
def view_get_adresses(request, pk):
    if request.method == 'GET':
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return JsonResponse({"error": "Client non trouvé."}, status=404)

        # Récupérer les adresses de livraison
        adresse_livraison = list(client.adresse_livraison.values('pk', 'adresse', 'code_postal', 'ville', 'pays'))
        # Récupérer les adresses de facturation
        adresse_facturation = list(client.adresse_facturation.values('pk', 'adresse', 'code_postal', 'ville', 'pays'))

        # Si aucune adresse n'est trouvée
        if not adresse_livraison and not adresse_facturation:
            return JsonResponse({"message": "Aucune adresse trouvée pour ce client."}, status=404)

        return JsonResponse({
            "adresse_livraison": adresse_livraison if adresse_livraison else None,
            "adresse_facturation": adresse_facturation if adresse_facturation else None
        }, status=200, safe=False)

    return JsonResponse({"message": "Méthode non autorisée."}, status=405)


@csrf_exempt
@client_login_required
def view_delete_adresse(request, pk, address_pk):
    if request.method == 'DELETE':
        try:
            # Récupérer le client
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return JsonResponse({"error": "Client not found."}, status=404)

        # Tentative de suppression de l'adresse de facturation
        try:
            adresse_facturation = client.adresse_facturation.get(pk=address_pk)
            adresse_facturation.delete()
            print("Adresse de facturation supprimée:", adresse_facturation)  # Débogage
            return JsonResponse({"message": "Adresse de facturation supprimée avec succès."}, status=200)
        except AdresseFacturation.DoesNotExist:
            pass  # Si non trouvée, on passe à l'adresse de livraison

        # Tentative de suppression de l'adresse de livraison
        try:
            adresse_livraison = client.adresse_livraison.get(pk=address_pk)
            adresse_livraison.delete()
            print("Adresse de livraison supprimée:", adresse_livraison)  # Débogage
            return JsonResponse({"message": "Adresse de livraison supprimée avec succès."}, status=200)
        except AdresseLivraison.DoesNotExist:
            return JsonResponse({"error": "Adresse de facturation et de livraison non trouvée."}, status=404)

        return JsonResponse({"error": "Adresse non trouvée."}, status=404)

    return JsonResponse({"message": "Méthode non autorisée."}, status=405)

@csrf_exempt
@client_login_required
def update_client_info(request, pk):
    if request.method == 'PUT':
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return JsonResponse({"error": "Client not found."}, status=404)

        data = json.loads(request.body)

        # Mettre à jour uniquement les informations personnelles
        client.prenom = data.get('prenom', client.prenom)
        client.nom = data.get('nom', client.nom)
        client.email = data.get('email', client.email)

        client.save()

        return JsonResponse({"message": "Informations mises à jour avec succès."}, status=200)
    
    return JsonResponse({"message": "Méthode non autorisée."}, status=405)



@csrf_exempt
@client_login_required
def update_client_password(request, pk):
    if request.method == 'PUT':
        try:
            # Log pour vérifier les données reçues
            data = json.loads(request.body)
            ancienMotDePasse = data.get('ancienMotDePasse')
            nouveauMotDePasse = data.get('password')
            print(f'Ancien mot de passe: {ancienMotDePasse}, Nouveau mot de passe: {nouveauMotDePasse}')
            
            client = get_object_or_404(Client, pk=pk)

            # Vérification du mot de passe actuel
            if not check_password(ancienMotDePasse, client.password):
                return JsonResponse({'message': 'Ancien mot de passe incorrect'}, status=400)

            # Si les mots de passe sont valides, mettre à jour
            client.password = make_password(nouveauMotDePasse)  # Hacher le nouveau mot de passe
            client.save()



            return JsonResponse({'message': 'Mot de passe mis à jour avec succès.'}, status=200)

        except Exception as e:
            print(f'Erreur lors de la mise à jour du mot de passe: {e}')  # Log de l'erreur
            return JsonResponse({'message': 'Erreur lors de la mise à jour du mot de passe.'}, status=500)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


@csrf_exempt
@client_login_required
def update_client(request, pk):
    if request.method == 'PUT':
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return JsonResponse({"error": "Client not found."}, status=404)

        data = json.loads(request.body)

        # Mettre à jour les attributs du client
        for field, value in data.items():
            if hasattr(client, field) and field not in ['adresse_facturation', 'adresse_livraison']:
                setattr(client, field, value)

        client.save()

        # Mettre à jour ou créer l'adresse de facturation
        adresse_facturation_data = data.get('adresse_facturation', {})
        adresse_facturation, created_facturation = AdresseFacturation.objects.update_or_create(
            client=client,
            defaults={
                'adresse': adresse_facturation_data.get('adresse', ''),
                'code_postal': adresse_facturation_data.get('code_postal', ''),
                'ville': adresse_facturation_data.get('ville', ''),
                'pays': adresse_facturation_data.get('pays', ''),
            }
        )

        # Mettre à jour ou créer l'adresse de livraison
        adresse_livraison_data = data.get('adresse_livraison', {})
        adresse_livraison, created_livraison = AdresseLivraison.objects.update_or_create(
            client=client,
            defaults={
                'adresse': adresse_livraison_data.get('adresse', ''),
                'code_postal': adresse_livraison_data.get('code_postal', ''),
                'ville': adresse_livraison_data.get('ville', ''),
                'pays': adresse_livraison_data.get('pays', ''),
            }
        )

        # Optionnel : afficher si les adresses ont été créées ou mises à jour
        if created_facturation:
            print("Adresse de facturation créée:", adresse_facturation)
        else:
            print("Adresse de facturation mise à jour:", adresse_facturation)

        if created_livraison:
            print("Adresse de livraison créée:", adresse_livraison)
        else:
            print("Adresse de livraison mise à jour:", adresse_livraison)

        return JsonResponse({"message": "Client updated successfully."}, status=200)
    
    return JsonResponse({"message": "Méthode non autorisée."}, status=405)


@csrf_exempt
@client_login_required
def update_adresse_facturation(request, pk):
    if request.method == 'PUT':
        logger.debug(f"Received request body: {request.body}")

        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return JsonResponse({"error": "Client not found."}, status=404)

        try:
            data = json.loads(request.body)
            logger.debug(f"Parsed JSON data: {data}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        adresse = data.get('adresse_facturation')

        if not adresse or not adresse.get('adresse') or not adresse.get('code_postal') or not adresse.get('ville') or not adresse.get('pays'):
            return JsonResponse({"error": "Tous les champs doivent être fournis."}, status=400)

        # Créer une nouvelle adresse de facturation sans écraser les anciennes
        adresse_facturation = AdresseFacturation.objects.create(
            client=client,
            adresse=adresse.get('adresse'),
            code_postal=adresse.get('code_postal'),
            ville=adresse.get('ville'),
            pays=adresse.get('pays'),
        )

        # Retourner la nouvelle adresse de facturation ajoutée
        return JsonResponse({"message": "Adresse de facturation ajoutée avec succès.", "adresse_facturation": adresse_facturation.to_dict()}, status=200)

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)

@csrf_exempt
@client_login_required
def update_adresse_livraison(request, pk):
    if request.method == 'PUT':
        logger.debug(f"Received request body: {request.body}")

        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return JsonResponse({"error": "Client not found."}, status=404)

        try:
            data = json.loads(request.body)
            logger.debug(f"Parsed JSON data: {data}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        adresse = data.get('adresse_livraison')

        if not adresse or not adresse.get('adresse') or not adresse.get('code_postal') or not adresse.get('ville') or not adresse.get('pays'):
            return JsonResponse({"error": "Tous les champs doivent être fournis."}, status=400)

        # Créer une nouvelle adresse de livraison sans écraser les anciennes
        adresse_livraison = AdresseLivraison.objects.create(
            client=client,
            adresse=adresse.get('adresse'),
            code_postal=adresse.get('code_postal'),
            ville=adresse.get('ville'),
            pays=adresse.get('pays'),
        )

        # Retourner la nouvelle adresse ajoutée
        return JsonResponse({"message": "Adresse de livraison ajoutée avec succès.", "adresse_livraison": adresse_livraison.to_dict()}, status=200)

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)
import re
from produits.models import Produit
from clients.models import Client


@csrf_exempt
def log_navigation(request):
    """Vue pour enregistrer les journaux de navigation."""
    if request.method == 'POST':
        try:
            # Récupérer les données envoyées dans le corps de la requête
            data = json.loads(request.body)
            print("Données reçues:", data)  # Afficher les données reçues pour déboguer

            # Extraire l'ID de l'article si présent dans l'URL
            current_url = data.get('currentURL', '')
            produit_id = None  # Valeur par défaut si aucun ID n'est trouvé

            # Vérifier si l'URL contient "/article/{id}"
            match = re.search(r'/produits/(\d+)', current_url)
            print("URL actuelle:", current_url)
            if match:
                produit_id = match.group(1)  # Extraire l'ID de l'article

            # Si un ID d'article est trouvé, essayer de récupérer l'objet Article
            produit = None
            if produit_id:
                try:
                    produit = Produit.objects.get(pk=produit_id)
                    print(f"Produit trouvé: {produit.pk}")
                except Produit.DoesNotExist:
                    print(f"Produir avec l'ID {produit_id} non trouvé.")

            # Récupérer le journaliste (en supposant que 'journalistId' correspond à l'ID du journaliste)
            client = None
            ClientId = data.get('ClientId')
            if ClientId:
                try:
                    client = Client.objects.get(id=ClientId)
                    print(f"Client trouvé: {client.username}")
                except Client.DoesNotExist:
                    print(f"Client avec l'ID {ClientId} non trouvé.")

            # Récupérer et convertir sessionStartTime et sessionEndTime
            duration_session_start_time = data.get('sessionStartTime')
            duration_session_end_time = data.get('sessionEndTime')

            # Afficher la valeur de sessionStartTime pour le débogage
            print(f"sessionStartTime: {duration_session_start_time}")
            print(f"sessionEndTime: {duration_session_end_time}")

            session_duration = duration_session_end_time -duration_session_start_time
            # Créer un nouvel enregistrement dans NavigationLog
            print("Création de l'objet NavigationLog...")
            navigation_log = NavigationLog(
            client=client,
            produit=produit,
            path=current_url,
            user_agent=data.get('userAgent', ''),
            fingerprint=data.get('fingerprint',''),
            referrer=data.get('referrer', ''),
            ip_address=data.get('ip', ''),
            os_info=data.get('os_info', ''),
            device_type=data.get('deviceType', 'desktop'),
            session_duration=session_duration  # Ajouter la durée de la session ici

                        )

            navigation_log.save()
            print("Navigation enregistrée avec succès.")

            # Réponse réussie
            return JsonResponse({"message": "Navigation enregistrée avec succès."}, status=200)

        except Exception as e:
            print("Erreur lors de l'enregistrement de la navigation:", e)
            return JsonResponse({"message": "Erreur lors de l'enregistrement de la navigation."}, status=500)
    
