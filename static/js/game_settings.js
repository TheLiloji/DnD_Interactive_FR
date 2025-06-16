document.addEventListener('DOMContentLoaded', function() {
    if (!isDm) return; // Seul le MJ peut modifier les paramètres

    const settingsModal = document.getElementById('settingsModal');
    const editSettingsBtn = document.getElementById('editSettingsBtn');
    const cancelSettingsBtn = document.getElementById('cancelSettings');
    const gameSettingsForm = document.getElementById('gameSettingsForm');
    const maxPlayersInput = document.getElementById('maxPlayers');
    const maxPlayersValue = document.getElementById('maxPlayersValue');

    // Afficher la valeur du slider
    maxPlayersInput.addEventListener('input', function() {
        maxPlayersValue.textContent = this.value;
    });

    // Ouvrir la modal
    editSettingsBtn.addEventListener('click', function() {
        settingsModal.classList.add('active');
    });

    // Fermer la modal
    cancelSettingsBtn.addEventListener('click', function() {
        settingsModal.classList.remove('active');
    });

    // Fermer la modal en cliquant en dehors
    settingsModal.addEventListener('click', function(e) {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('active');
        }
    });

    // Gérer la soumission du formulaire
    gameSettingsForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = {
            name: document.getElementById('gameName').value,
            description: document.getElementById('gameDescription').value,
            max_players: parseInt(document.getElementById('maxPlayers').value),
            game_type: document.getElementById('gameType').value,
            options: {
                allow_spectators: document.getElementById('allowSpectators').checked,
                auto_level: document.getElementById('autoLevel').checked,
                dice_validation: document.getElementById('diceValidation').checked
            }
        };

        try {
            const response = await fetch(`/api/update_game_settings/${gameId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Fermer la modal et afficher un message de succès
                settingsModal.classList.remove('active');
                showNotification('Paramètres mis à jour avec succès', 'success');
                
                // Mettre à jour l'interface
                updateGameInterface(formData);
            } else {
                showNotification(data.error || 'Une erreur est survenue', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Une erreur est survenue', 'error');
        }
    });

    function updateGameInterface(settings) {
        // Mettre à jour le nom et la description
        document.querySelector('.game-header h2').textContent = settings.name;
        const descElement = document.querySelector('.game-description');
        if (descElement) {
            descElement.textContent = settings.description;
        }

        // Mettre à jour les informations de la partie
        document.querySelector('.info-item span').textContent = 
            `${document.querySelectorAll('.player-item').length}/${settings.max_players} joueurs`;
        
        // Mettre à jour le type de partie
        document.querySelector('.info-item:nth-child(2) span').textContent = 
            settings.game_type === 'standard' ? 'Standard' : 'Simplifiée';
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        const container = document.getElementById('notifications');
        container.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}); 