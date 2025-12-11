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
