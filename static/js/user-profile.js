document.addEventListener('DOMContentLoaded', function() {
    const userProfile = document.querySelector('.user-profile');
    const userMenu = document.querySelector('.user-menu');
    const saveButton = document.querySelector('.user-menu-button');
    const pseudoInput = document.querySelector('#user-pseudo');
    const avatarInput = document.querySelector('#user-avatar');

    // Gestion de l'ouverture/fermeture du menu
    userProfile.addEventListener('click', function(e) {
        e.stopPropagation();
        userProfile.classList.toggle('active');
        userMenu.classList.toggle('active');
    });

    // Fermer le menu en cliquant ailleurs
    document.addEventListener('click', function(e) {
        if (!userMenu.contains(e.target) && !userProfile.contains(e.target)) {
            userProfile.classList.remove('active');
            userMenu.classList.remove('active');
        }
    });

    // Empêcher la fermeture en cliquant dans le menu
    userMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Fonction pour afficher un message d'erreur
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'user-menu-error';
        errorDiv.textContent = message;
        
        // Supprimer l'ancien message d'erreur s'il existe
        const oldError = userMenu.querySelector('.user-menu-error');
        if (oldError) oldError.remove();
        
        // Insérer avant le bouton
        saveButton.parentNode.insertBefore(errorDiv, saveButton);
        
        // Supprimer après 3 secondes
        setTimeout(() => errorDiv.remove(), 3000);
    }

    // Fonction pour afficher un message de succès
    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'user-menu-success';
        successDiv.textContent = message;
        
        // Supprimer l'ancien message de succès s'il existe
        const oldSuccess = userMenu.querySelector('.user-menu-success');
        if (oldSuccess) oldSuccess.remove();
        
        // Insérer avant le bouton
        saveButton.parentNode.insertBefore(successDiv, saveButton);
        
        // Supprimer après 3 secondes
        setTimeout(() => successDiv.remove(), 3000);
    }

    // Gestion de la sauvegarde
    saveButton.addEventListener('click', async function() {
        const pseudo = pseudoInput.value.trim();
        const avatar = avatarInput.value.trim();

        if (!pseudo) {
            showError('Le pseudo ne peut pas être vide');
            return;
        }

        // Désactiver le bouton pendant la sauvegarde
        saveButton.disabled = true;
        saveButton.textContent = 'Enregistrement...';

        try {
            const response = await fetch('/api/update-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pseudo,
                    avatar
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Mise à jour de l'interface
                document.querySelector('.user-profile-name').textContent = data.user.pseudo;
                if (data.user.avatar) {
                    const avatarElement = document.querySelector('.user-avatar');
                    if (avatarElement.tagName === 'IMG') {
                        avatarElement.src = data.user.avatar;
                    } else {
                        // Si c'était une initiale, on crée une image
                        const img = document.createElement('img');
                        img.src = data.user.avatar;
                        img.alt = data.user.pseudo;
                        img.className = 'user-avatar';
                        avatarElement.replaceWith(img);
                    }
                }

                showSuccess('Profil mis à jour avec succès');

                // Émettre un événement personnalisé pour la synchronisation
                const event = new CustomEvent('userProfileUpdated', {
                    detail: {
                        pseudo: data.user.pseudo,
                        avatar: data.user.avatar
                    }
                });
                document.dispatchEvent(event);

                // Fermer le menu après un court délai
                setTimeout(() => {
                    userProfile.classList.remove('active');
                    userMenu.classList.remove('active');
                }, 1500);
            } else {
                showError(data.error || 'Erreur lors de la mise à jour');
            }
        } catch (error) {
            showError('Une erreur est survenue lors de la mise à jour du profil');
            console.error(error);
        } finally {
            // Réactiver le bouton
            saveButton.disabled = false;
            saveButton.textContent = 'Enregistrer';
        }
    });

    // Prévisualisation de l'avatar
    avatarInput.addEventListener('input', function() {
        const avatar = avatarInput.value.trim();
        if (avatar) {
            const img = new Image();
            img.onload = function() {
                const avatarElement = document.querySelector('.user-avatar');
                if (avatarElement.tagName === 'IMG') {
                    avatarElement.src = avatar;
                } else {
                    avatarElement.style.backgroundImage = `url(${avatar})`;
                }
            };
            img.onerror = function() {
                showError('URL d\'image invalide');
                avatarInput.value = '';
            };
            img.src = avatar;
        }
    });
}); 