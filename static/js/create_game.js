document.addEventListener('DOMContentLoaded', function() {
    // Gestion du slider pour le nombre de joueurs
    const playerSlider = document.getElementById('max_players');
    const playerCount = document.getElementById('playerCount');
    
    playerSlider.addEventListener('input', function() {
        playerCount.textContent = this.value;
    });

    // Gestion du formulaire
    const form = document.getElementById('createGameForm');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            name: formData.get('game_name'),
            description: formData.get('description'),
            password: formData.get('password'),
            max_players: parseInt(formData.get('max_players')),
            game_type: formData.get('game_type'),
            options: {
                allow_spectators: formData.get('allow_spectators') === '1',
                auto_level: formData.get('auto_level') === '1',
                voice_chat: formData.get('voice_chat') === '1',
                dice_validation: formData.get('dice_validation') === '1'
            }
        };

        try {
            const response = await fetch('/api/create_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // Redirection vers la nouvelle partie
                window.location.href = `/game/${result.game_id}`;
            } else {
                // Affichage de l'erreur
                showNotification(result.error || 'Une erreur est survenue', 'error');
            }
        } catch (error) {
            showNotification('Une erreur est survenue lors de la création de la partie', 'error');
            console.error('Error:', error);
        }
    });

    // Fonction pour afficher les notifications
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '1000';
        container.appendChild(notification);

        document.body.appendChild(container);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => container.remove(), 300);
        }, 3000);
    }
}); 