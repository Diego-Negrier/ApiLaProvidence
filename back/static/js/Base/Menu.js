// Sélectionner les éléments nécessaires
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile_menu');

// Ajouter un événement au clic sur le bouton hamburger
hamburger.addEventListener('click', function () {
    // Basculer entre l'affichage et le masquage du menu mobile
    mobileMenu.classList.toggle('menu-show');
});

document.querySelector('.dropdown-toggle').addEventListener('click', function(e) {
    const menu = document.querySelector('.dropdown-menu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    e.stopPropagation(); // Empêche de fermer immédiatement
});

// Fermer le menu si on clique ailleurs
document.addEventListener('click', function() {
    const menu = document.querySelector('.dropdown-menu');
    if (menu) {
        menu.style.display = 'none';
    }
});