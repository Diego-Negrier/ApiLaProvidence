// Fonction pour filtrer la table
function filterTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('productsTable');
    const rows = table.getElementsByTagName('tr');
    const produitsListe = document.getElementById('productsListe');
    const produitCards = produitsListe.getElementsByClassName('produit-card');

    for (let i = 1; i < rows.length; i++) {  // Commence à 1 pour ignorer l'en-tête
        let cells = rows[i].getElementsByTagName('td');
        let match = false;
        for (let j = 0; j < cells.length; j++) {
            if (cells[j]) {
                if (cells[j].innerText.toLowerCase().includes(filter)) {
                    match = true;
                    break;
                }
            }
        }
        rows[i].style.display = match ? '' : 'none';
    }

    for (let i = 0; i < produitCards.length; i++) {
        const card = produitCards[i];
        const productName = card.getAttribute('data-produit-name'); // Attribut contenant le nom du produit en minuscule

        // Vérifiez si le nom du produit correspond au texte de la recherche
        if (productName.includes(filter)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    }
}
function sortTable(n) {
    const table = document.getElementById("productsTable");
    const rows = table.rows;
    let switching = true;
    let dir = "asc";  // Initialisation de la direction de tri à 'asc'
    let switchCount = 0;

    // Répéter tant qu'il y a des échanges à effectuer
    while (switching) {
        switching = false;
        let rowsArray = Array.from(rows);  // Convertir les lignes en tableau

        // Parcourir toutes les lignes, sauf la première (en-tête)
        for (let i = 1; i < rowsArray.length - 1; i++) {
            let x = rowsArray[i].getElementsByTagName("TD")[n];
            let y = rowsArray[i + 1].getElementsByTagName("TD")[n];
            let shouldSwitch = compareRows(x, y, dir, n); // Appel à la fonction compareRows

            // Si un échange est nécessaire
            if (shouldSwitch) {
                rowsArray[i].parentNode.insertBefore(rowsArray[i + 1], rowsArray[i]);
                switching = true;  // Il y a eu un échange, donc on continue
                switchCount++; // Incrémenter le nombre d'échanges
                break; // Quitter la boucle de comparaison
            }
        }

        // Si aucun échange n'a eu lieu, on inverse la direction
        if (switchCount === 0 && dir === "asc") {
            dir = "desc";
            switching = true; // Redémarre le processus
        }
    }
}

// Fonction qui détermine si une ligne doit être échangée
function compareRows(x, y, dir, columnIndex) {
    let shouldSwitch = false;
    
    // Si c'est la colonne des ID, faire une comparaison numérique
    if (columnIndex === 0) {
        let xValue = parseFloat(x.innerHTML);
        let yValue = parseFloat(y.innerHTML);

        // Comparaison numérique
        if (dir === "asc" && xValue > yValue) {
            shouldSwitch = true;
        } else if (dir === "desc" && xValue < yValue) {
            shouldSwitch = true;
        }
    } else {
        // Comparaison pour les autres colonnes (par défaut en texte)
        let xText = x.innerHTML.toLowerCase();
        let yText = y.innerHTML.toLowerCase();

        if (dir === "asc" && xText > yText) {
            shouldSwitch = true;
        } else if (dir === "desc" && xText < yText) {
            shouldSwitch = true;
        }
    }

    return shouldSwitch;
}

