from django.shortcuts import render
from clients.models import Client
from clients.utilis import client_login_required
from django.shortcuts import get_object_or_404,redirect
from paniers.models import Panier,LignePanier
from commandes.models import Commande,HistoriqueCommande,StatutCommande
from produits.models import Produit,Fournisseur,StatutProduit
from livraisons.models import Livreur
import json
from django.http import JsonResponse
import logging
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import StatutCommandeForm  # Supposons que vous avez un formulaire pour changer le statut
from produits.forms import StatutProduitForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import transaction

from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


def commande_view(request):
    # Vérification de l'authentification et des groupes
    is_authenticated = request.user.is_authenticated
    is_admin = request.user.groups.filter(name='Administrateurs').exists()
    is_fournisseur = request.user.groups.filter(name='Fournisseurs').exists()

    # Traitement du formulaire POST
    if request.method == 'POST':
        ligne_panier_id = request.POST.get('ligne_panier_id')
        statut = request.POST.get('statut')

        try:
            # Récupérer la ligne de panier spécifiée
            ligne_panier = LignePanier.objects.get(id=ligne_panier_id)
            ligne_panier.statut = statut
            ligne_panier.save()

            messages.success(request, f"Statut de la ligne '{ligne_panier.produit.nom}' mis à jour.")
        except LignePanier.DoesNotExist:
            messages.error(request, "Ligne de panier introuvable.")
        return redirect('commande_view')

    # Préparer les données des commandes
    try:
        if is_fournisseur:
            fournisseur = Fournisseur.objects.get(user=request.user)
            commandes = Commande.objects.filter(
                panier__lignes__produit__fournisseur=fournisseur
            ).distinct().prefetch_related(
                Prefetch('panier__lignes__produit__fournisseur')
            )
        elif is_admin:
            commandes = Commande.objects.all().prefetch_related(
                Prefetch('panier__lignes__produit__fournisseur')
            )
        else:
            commandes = Commande.objects.none()
    except Fournisseur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas associé à un fournisseur.")
        return redirect('une_autre_vue')  # Redirigez l'utilisateur si nécessaire.

    commande_data = []
    for commande in commandes:
        if not commande.panier:
            continue  # Ignorez les commandes sans panier associé

        produits_commande = []

        for ligne in commande.panier.lignes.all():
            if is_fournisseur and ligne.produit.fournisseur.user != request.user:
                continue

            produits_commande.append({
                'produit': ligne.produit.nom,
                'quantite': ligne.quantite,
                'prix': ligne.produit.prix,
                'total': ligne.produit.prix * ligne.quantite,
                'statut': ligne.statut,
                'ligne_panier_id': ligne.id,
                'image': ligne.produit.image.url if ligne.produit.image else None,
                'fournisseur': ligne.produit.fournisseur.nom if ligne.produit.fournisseur else 'Inconnu',
            })

        commande.mettre_a_jour_statut()
        commande.marquer_comme_terminee()
        commande.rouvrir_commande_historique()

        commande_data.append({
            'id': commande.id,
            'statut': commande.get_statut_display(),
            'avancement': commande.avancement,
            'total': commande.total,
            'date_commande': commande.date_commande,
            'produits': produits_commande,
            'panier': commande.panier,
            'client': commande.client,
        })

    return render(request, 'Commandes.html', {
        'commandes': commande_data,
        'is_admin': is_admin,
        'is_authenticated': is_authenticated,
        'is_fournisseur': is_fournisseur,
        'statut_choices': StatutProduit.choices,
    })
@csrf_exempt
@client_login_required
def creation_commande(request):
    try:
        data = json.loads(request.body)
        
        client_id = data.get('client_id')
        livreur_id = data.get('livreur_id')
        total_commande = data.get('total')
        panier_data = data.get('panier_id')  # Récupérer l'objet panier complet
        
        if not client_id or not livreur_id or not total_commande or not panier_data:
            return JsonResponse({'error': 'Les champs client_id, livreur_id, total et panier sont requis.'}, status=400)

        # Récupérer l'ID du panier et ses lignes
        panier_id = panier_data.get('pk')
        lignes_panier = panier_data.get('lignes', [])

        # Récupérer les objets nécessaires
        client = Client.objects.get(pk=client_id)
        livreur = Livreur.objects.get(pk=livreur_id)
        panier = Panier.objects.get(pk=panier_id)

        # Vérification du stock pour chaque ligne de panier
        message_stock = []
        for ligne in lignes_panier:
            produit_unique = ligne.get('numero_unique')
            quantite_commandee = ligne.get('quantite')
            
            produit = Produit.objects.get(numero_unique=produit_unique)
            
            if produit.stock < quantite_commandee:
                message_stock.append({
                    'produit': produit.nom,
                    'quantite_commandee': quantite_commandee,
                    'stock_disponible': produit.stock
                })
                continue

            # Réduction du stock
            produit.stock -= quantite_commandee
            produit.save()

        if message_stock:
            print(message_stock)

            return JsonResponse({
                'error': 'Certains produits ont un stock insuffisant',
                'details': message_stock,
            }, status=400)
        # Utilisation d'une transaction pour garantir la cohérence des données
        with transaction.atomic():
            # Création de la commande et d'un nouveau panier
            commande, nouveau_panier = Commande.creer_commande_et_nouveau_panier(
                client=client,
                livreur=livreur,
                total=float(total_commande),
            )

        return JsonResponse({
            'message': 'Commande créée avec succès.',
            'commande_id': commande.pk,
            'nouveau_panier_id': nouveau_panier.pk,
            'total_commande': commande.total,
            'statut': commande.statut,
        }, status=201)

    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client non trouvé.'}, status=404)
    except Livreur.DoesNotExist:
        return JsonResponse({'error': 'Livreur non trouvé.'}, status=404)
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Un produit de la commande n\'existe pas.'}, status=404)
    except Exception as e:
        logger.error(f"Erreur lors de la création de la commande : {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Erreur: {str(e)}'}, status=500)

@csrf_exempt
@client_login_required
def commandes_par_client(request, client_id):
    """
    Récupère les commandes en cours et l'historique des commandes pour un client spécifique.
    """
    client = get_object_or_404(Client, pk=client_id)

    # Précharger les lignes de panier pour chaque commande
    panier_lignes = Prefetch('panier__lignes', queryset=LignePanier.objects.all())

    # Récupérer les commandes en cours (statut différent de "terminée") avec les lignes de panier préchargées
    commandes_en_cours = Commande.objects.filter(client=client).exclude(statut='terminée').prefetch_related(panier_lignes)
    produits_statut_liste = list(StatutProduit.choices)
    commandes_statut_liste = list(StatutCommande.choices)
    commandes_data = []
    
    # Initialisation de l'historique des commandes (vide par défaut)
    historique_commandes = []

    for commande in commandes_en_cours:
        commande.mettre_a_jour_statut()

        produits = []
        if commande.panier and commande.panier.lignes.exists():  # Vérifie si le panier existe et contient des lignes
            for ligne in commande.panier.lignes.all():
                produits.append({
                    'produit': ligne.produit.nom,
                    'quantite': ligne.quantite,
                    'prix': ligne.produit.prix,
                    'total': ligne.produit.prix * ligne.quantite,
                    'image': ligne.produit.image.url if ligne.produit.image else None,
                    'statut': ligne.statut,
                })
        else:
            produits.append({
                'message': 'Aucun produit dans le panier'
            })

        commandes_data.append({
            'id': commande.id,
            'statut': commande.statut,
            'total': commande.total,
            'date_commande': commande.date_commande,
            'livreur_nom': commande.livreur.nom if commande.livreur else None,
            'produits': produits
        })
        for historique in HistoriqueCommande.objects.filter(client=client, statut="terminée"):
            produits = []
            if historique.lignes.exists():  # Vérifie si des lignes existent pour cet historique
                produits = [
                    {
                        'produit': ligne.produit.nom,
                        'quantite': ligne.quantite,
                        'prix': ligne.prix,
                        'poids': ligne.poids,
                        'total': ligne.prix * ligne.quantite,
                        'image': ligne.produit.image.url if ligne.produit.image else None,
                    }
                    for ligne in historique.lignes.all()  # Utilise related_name="lignes"
                ]
            else:
                produits.append({
                    'message': 'Aucun produit dans l\'historique'
                })

            historique_commandes.append({
                'id': historique.id,
                'statut': historique.statut,
                'total': historique.total,
                'date_commande': historique.date_commande.isoformat() if historique.date_commande else None,
                'numero_commande': historique.numero_commande,
                'livreur_nom': historique.livreur_nom,
                'produits': produits,
            })

    # Retourner les données sous forme de réponse JSON
    return JsonResponse({
        'commandes_en_cours': commandes_data,
        'historique_commandes': historique_commandes,
        'produits_statut_liste': produits_statut_liste,
        'commandes_statut_liste': commandes_statut_liste
    })



def marquer_commande_comme_terminee(request, commande_id):
    try:
        commande = Commande.objects.get(pk=commande_id)
        commande.marquer_comme_terminee()  # Mettre à jour le statut de la commande

        return JsonResponse({'message': 'Commande marquée comme terminée avec succès.'}, status=200)
    
    except Commande.DoesNotExist:
        return JsonResponse({'error': 'Commande non trouvée.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"Erreur lors de la mise à jour de la commande: {str(e)}"}, status=500)
    