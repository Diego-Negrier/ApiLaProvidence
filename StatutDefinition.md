Statuts de la commande (StatutCommande) :

	1.	EN_ATTENTE (En attente) :
	•	La commande a été créée, mais elle n’a pas encore commencé à être traitée. Cela peut signifier que la commande est en attente de validation, de paiement, ou d’une autre action avant de commencer son traitement.
	2.	EN_PREPARATION (En préparation) :
	•	La commande est en cours de traitement. Les articles sont préparés, emballés, ou mis à disposition pour la livraison. Ce statut signifie que la commande est active et que des actions sont entreprises pour la finaliser.
	3.	EN_COURS (En cours) :
	•	La commande est en train d’être traitée mais n’est pas encore terminée. Cela peut inclure des étapes intermédiaires de la préparation, de l’emballage, ou de la coordination avec le livreur. Ce statut est souvent utilisé pour signaler que la commande est toujours en transit ou en traitement.
	4.	TERMINEE (Terminée) :
	•	La commande a été complétée avec succès. Tous les produits ont été préparés, expédiés et livrés. La commande est désormais considérée comme fermée et le client a reçu ce qu’il a commandé.
	5.	ANNULEE (Annulée) :
	•	La commande a été annulée avant ou pendant le processus de traitement. Cela peut se produire si un client annule sa commande ou si un problème survient (par exemple, un produit est en rupture de stock ou il y a une erreur dans la commande).

Statuts du produit dans une commande (StatutProduit) :

	1.	EN_ATTENTE (En attente) :
	•	Le produit est en attente d’une action spécifique, comme l’approvisionnement ou la validation. Cela signifie que le produit n’a pas encore commencé à être préparé ou expédié. Cela pourrait également indiquer que le produit est en attente de stock.
	2.	EN_PREPARATION (En préparation) :
	•	Le produit est en cours de préparation. Il est peut-être emballé, étiqueté, ou prêt à être expédié. Ce statut signifie que l’article est actif et en train d’être préparé pour l’expédition.
	3.	EN_LIVRAISON (En livraison) :
	•	Le produit a été expédié et est en route vers le client. Il est en phase de livraison, soit par un transporteur ou via un autre mode de livraison. Le produit est hors de l’entrepôt et dans le processus de transport.
	4.	TERMINE (Terminé) :
	•	Le produit a été livré et la transaction est considérée comme achevée. Le produit est en possession du client et toutes les actions associées à la commande du produit ont été complètes.
	5.	EN_STOCK (En stock) :
	•	Le produit est disponible dans l’entrepôt ou le magasin et peut être ajouté à une commande. Ce statut signifie que le produit est actuellement disponible pour être vendu et expédié.
	6.	RUPTURE_STOCK (Rupture de stock) :
	•	Le produit n’est plus disponible en stock. Cela indique que le produit est temporairement ou définitivement épuisé et ne peut pas être ajouté à une commande tant qu’il n’est pas réapprovisionné.

Résumé des définitions :

	•	Commande :
	•	En attente : Non traitée, en attente d’action.
	•	En préparation : Traitée, produits en préparation.
	•	En cours : En traitement actif, produits non encore expédiés.
	•	Terminée : Traitée et livrée.
	•	Annulée : Non finalisée, annulée avant ou pendant le traitement.
	•	Produit :
	•	En attente : En attente d’approvisionnement ou de validation.
	•	En préparation : Prêt à être expédié.
	•	En livraison : En cours de transport vers le client.
	•	Terminé : Livraison effectuée et réception confirmée.
	•	En stock : Disponible dans l’entrepôt pour la vente.
	•	Rupture de stock : Pas disponible à la vente, stock épuisé.