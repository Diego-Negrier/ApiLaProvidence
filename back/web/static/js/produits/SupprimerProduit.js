function confirmerSuppression(event, produitId) {
    // Empêcher le comportement par défaut du lien
    event.preventDefault();

    // Affiche une popup de confirmation
    const confirmation = confirm("Êtes-vous sûr de vouloir supprimer ce produit ?");

    if (confirmation) {
        // Vérifier que le formulaire existe avant de le soumettre
        const form = document.getElementById('delete-form-' + produitId);
        if (form) {
            console.log("Soumission du formulaire pour supprimer le produit avec ID", produitId);
            form.submit();  // Soumettre le formulaire avec méthode POST
        } else {
            console.error('Formulaire non trouvé pour le produit avec ID:', produitId);
        }
    }

    // Retourner false empêche toute autre action si l'utilisateur annule
    return false;
}