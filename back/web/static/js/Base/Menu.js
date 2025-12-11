<<<<<<< HEAD
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
=======
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile_menu');
    const menuOverlay = document.getElementById('menu-overlay');
    const nav = document.querySelector('.glass-nav');
    
    // Toggle menu mobile
    function toggleMenu() {
        hamburger?.classList.toggle('active');
        mobileMenu?.classList.toggle('active');
        mobileMenu?.classList.toggle('menu-hidden');
        menuOverlay?.classList.toggle('active');
        document.body.style.overflow = mobileMenu?.classList.contains('active') ? 'hidden' : '';
    }
    
    // Événements
    hamburger?.addEventListener('click', toggleMenu);
    menuOverlay?.addEventListener('click', toggleMenu);
    
    // Fermer le menu lors du clic sur un lien
    document.querySelectorAll('.mobile-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 850) {
                toggleMenu();
            }
        });
    });
    
    // Effet scroll sur navbar
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            nav?.classList.add('scrolled');
        } else {
            nav?.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
});
>>>>>>> e097b66e17a2ea974af903e357531f5ddcf8880b
