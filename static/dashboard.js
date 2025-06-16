document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const mainContainer = document.querySelector('.main-container');
    const leftSidebar = document.querySelector('.sidebar.left');
    const rightSidebar = document.querySelector('.sidebar.right');
    const leftToggle = document.querySelector('.sidebar-toggle.left');
    const rightToggle = document.querySelector('.sidebar-toggle.right');

    // Fonction pour gérer l'ouverture/fermeture des sidebars
    function toggleSidebar(sidebar, isRight = false) {
        const isActive = sidebar.classList.toggle('active');
        mainContainer.classList.toggle('sidebar-open');
        
        // Ajuster la position du bouton toggle
        const toggle = isRight ? rightToggle : leftToggle;
        if (isActive) {
            toggle.style.transform = `translateX(${isRight ? '-' : ''}${window.innerWidth <= 768 ? '320' : '280'}px) translateY(-50%)`;
        } else {
            toggle.style.transform = 'translateY(-50%)';
        }
    }

    // Event listeners pour les boutons toggle
    leftToggle.addEventListener('click', () => toggleSidebar(leftSidebar));
    rightToggle.addEventListener('click', () => toggleSidebar(rightSidebar, true));

    // Fermer les sidebars en cliquant en dehors
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.sidebar') && !e.target.closest('.sidebar-toggle')) {
            if (leftSidebar.classList.contains('active')) {
                toggleSidebar(leftSidebar);
            }
            if (rightSidebar.classList.contains('active')) {
                toggleSidebar(rightSidebar, true);
            }
        }
    });

    // Gérer les clics sur les tiles
    document.querySelectorAll('.tile').forEach(tile => {
        tile.addEventListener('click', function() {
            const action = this.dataset.action;
            switch(action) {
                case 'create':
                    window.location.href = '/create_game';
                    break;
                case 'join':
                    // Ouvrir une modale pour rejoindre une partie
                    document.querySelector('#joinGameModal').classList.add('active');
                    break;
                case 'character':
                    window.location.href = '/character_creation';
                    break;
                case 'tutorial':
                    // Rediriger vers le tutoriel
                    window.location.href = '/tutorial';
                    break;
            }
        });
    });

    // Animation initiale des tiles
    document.querySelectorAll('.tile').forEach((tile, index) => {
        setTimeout(() => {
            tile.style.opacity = '1';
            tile.style.transform = 'translateY(0)';
        }, index * 200);
    });
}); 