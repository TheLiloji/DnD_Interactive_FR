document.addEventListener('DOMContentLoaded', function() {
    const leftSidebar = document.querySelector('.sidebar.left');
    const rightSidebar = document.querySelector('.sidebar.right');
    const leftToggle = document.querySelector('.sidebar-toggle:not(.right)');
    const rightToggle = document.querySelector('.sidebar-toggle.right');

    // État des sidebars
    let leftIsOpen = false;
    let rightIsOpen = false;

    // Fonction pour gérer le toggle de la sidebar gauche
    function toggleLeftSidebar() {
        leftIsOpen = !leftIsOpen;
        leftSidebar.classList.toggle('active');
        leftToggle.style.left = leftIsOpen ? '280px' : '0';
    }

    // Fonction pour gérer le toggle de la sidebar droite
    function toggleRightSidebar() {
        rightIsOpen = !rightIsOpen;
        rightSidebar.classList.toggle('active');
        rightToggle.style.right = rightIsOpen ? '280px' : '0';
    }

    // Ajout des event listeners
    leftToggle.addEventListener('click', toggleLeftSidebar);
    rightToggle.addEventListener('click', toggleRightSidebar);
}); 