// Configuration des dés
const DICE_TYPES = {
    'd4': { faces: 4, color: '#FF6B6B' },
    'd6': { faces: 6, color: '#4ECDC4' },
    'd8': { faces: 8, color: '#45B7D1' },
    'd10': { faces: 10, color: '#96CEB4' },
    'd12': { faces: 12, color: '#FFEEAD' },
    'd20': { faces: 20, color: '#D4A373' },
    'd100': { faces: 100, color: '#9B5DE5' }
};

class GameClient {
    constructor() {
        this.socket = io();
        this.gameId = window.gameId || document.querySelector('.game-code').textContent.split(': ')[1];
        this.players = new Map();  // email -> playerData
        this.dice3D = null;
        this.is3DMode = false;
        this.setupSocketListeners();
        this.setupDiceMenu();
        this.setup3DDice();
        this.joinGame();
        this.setupProfileSync();
    }

    setupSocketListeners() {
        // Connexion/Déconnexion
        this.socket.on('connect', () => this.handleConnect());
        this.socket.on('disconnect', () => this.handleDisconnect());
        
        // Événements de jeu
        this.socket.on('current_players', (data) => this.handleCurrentPlayers(data));
        this.socket.on('player_joined', (data) => this.handlePlayerJoined(data));
        this.socket.on('player_left', (data) => this.handlePlayerLeft(data));
        this.socket.on('dice_rolled', (data) => this.handleDiceRolled(data));
        this.socket.on('error', (data) => this.handleError(data));
        this.socket.on('player_updated', (data) => this.handlePlayerUpdated(data));
    }

    setup3DDice() {
        // Initialiser les dés 3D seulement si on a les librairies
        if (typeof THREE !== 'undefined' && typeof CANNON !== 'undefined') {
            try {
                this.dice3D = new Dice3D();
                console.log('Système de dés 3D initialisé');
            } catch (error) {
                console.error('Erreur lors de l\'initialisation des dés 3D:', error);
            }
        }

        // Gestionnaire pour le bouton de basculement 3D (sidebar)
        const toggle3DBtn = document.getElementById('toggle3D');
        if (toggle3DBtn) {
            toggle3DBtn.addEventListener('click', () => {
                this.toggle3DMode();
            });
            
            // Double-clic pour afficher/masquer les options avancées
            let clickCount = 0;
            toggle3DBtn.addEventListener('click', () => {
                clickCount++;
                setTimeout(() => {
                    if (clickCount === 2) {
                        this.toggle3DOptions();
                    }
                    clickCount = 0;
                }, 300);
            });
        }

        // Gestionnaire pour le bouton 3D mini (dans le menu)
        const toggle3DMini = document.getElementById('toggle3DMini');
        if (toggle3DMini) {
            toggle3DMini.addEventListener('click', () => {
                this.toggle3DMode();
            });
        }

        // Gestionnaire pour effacer les dés (sidebar)
        const clearDiceBtn = document.getElementById('clearDice');
        if (clearDiceBtn) {
            clearDiceBtn.addEventListener('click', () => {
                if (this.dice3D) {
                    this.dice3D.clearDice();
                    this.dice3D.hide();
                }
            });
        }

        // Gestionnaire pour effacer les dés mini (dans le menu)
        const clearDiceMini = document.getElementById('clearDiceMini');
        if (clearDiceMini) {
            clearDiceMini.addEventListener('click', () => {
                if (this.dice3D) {
                    this.dice3D.clearDice();
                    this.dice3D.hide();
                }
            });
        }

        // Gestionnaires pour les options avancées
        this.setup3DOptions();
    }

    setup3DOptions() {
        // Option sons
        const soundCheckbox = document.getElementById('diceSound');
        if (soundCheckbox) {
            soundCheckbox.addEventListener('change', (e) => {
                if (this.dice3D) {
                    this.dice3D.sounds = e.target.checked;
                    this.showNotification(`Sons ${e.target.checked ? 'activés' : 'désactivés'}`, 'info');
                }
            });
        }

        // Option ombres
        const shadowsCheckbox = document.getElementById('diceShadows');
        if (shadowsCheckbox) {
            shadowsCheckbox.addEventListener('change', (e) => {
                if (this.dice3D) {
                    if (e.target.checked) {
                        this.dice3D.enableShadows();
                    } else {
                        this.dice3D.disableShadows();
                    }
                    this.showNotification(`Ombres ${e.target.checked ? 'activées' : 'désactivées'}`, 'info');
                }
            });
        }
    }

    toggle3DMode() {
        if (!this.dice3D) {
            this.showNotification('Les dés 3D ne sont pas disponibles', 'error');
            return;
        }

        this.is3DMode = !this.is3DMode;
        const toggle3DBtn = document.getElementById('toggle3D');
        const toggle3DMini = document.getElementById('toggle3DMini');

        if (this.is3DMode) {
            if (toggle3DBtn) {
                toggle3DBtn.innerHTML = '<i class="material-icons">view_list</i> Mode 2D';
                toggle3DBtn.classList.add('active');
            }
            if (toggle3DMini) {
                toggle3DMini.classList.add('active');
            }
            this.showNotification('Mode 3D activé - Les dés apparaîtront en superposition', 'success');
        } else {
            if (toggle3DBtn) {
                toggle3DBtn.innerHTML = '<i class="material-icons">3d_rotation</i> Mode 3D';
                toggle3DBtn.classList.remove('active');
            }
            if (toggle3DMini) {
                toggle3DMini.classList.remove('active');
            }
            this.dice3D.hide(); // Cacher les dés 3D
            this.showNotification('Mode 2D activé', 'success');
        }
    }

    toggle3DOptions() {
        const optionsDiv = document.getElementById('dice3dOptions');
        const toggle3DBtn = document.getElementById('toggle3D');
        
        if (optionsDiv) {
            const isVisible = optionsDiv.style.display !== 'none';
            optionsDiv.style.display = isVisible ? 'none' : 'block';
            optionsDiv.classList.toggle('active', !isVisible);
            
            if (toggle3DBtn) {
                toggle3DBtn.classList.toggle('options-visible', !isVisible);
            }
        }
    }

    setupDiceMenu() {
        const menuBtn = document.getElementById('diceMenuBtn');
        const menu = document.getElementById('diceMenu');
        const diceCount = document.getElementById('diceCount');
        const diceVisibility = document.getElementById('diceVisibility');
        
        // Variable pour le modificateur actuel
        this.currentModifier = 0;
        this.hasAdvantage = false;
        
        // Gérer l'ouverture/fermeture du menu
        menuBtn.addEventListener('click', () => {
            menu.classList.toggle('active');
        });

        // Fermer le menu si on clique en dehors
        document.addEventListener('click', (e) => {
            if (!menu.contains(e.target) && !menuBtn.contains(e.target)) {
                menu.classList.remove('active');
            }
        });

        // Gestionnaires pour les lancers composés
        const compositeInput = document.getElementById('compositeRoll');
        const compositeBtn = document.getElementById('rollComposite');
        const exampleBtns = menu.querySelectorAll('.example-btn');

        // Remplir l'input avec les exemples
        exampleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                compositeInput.value = btn.dataset.formula;
                compositeInput.focus();
            });
        });

        // Lancer composé
        if (compositeBtn) {
            compositeBtn.addEventListener('click', () => {
                this.rollComposite(compositeInput.value);
            });
        }

        // Lancer sur Entrée
        if (compositeInput) {
            compositeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.rollComposite(compositeInput.value);
                }
            });
        }

        // Gestionnaires pour les modificateurs
        const modifierButtons = menu.querySelectorAll('.modifier-btn');
        modifierButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const mod = btn.dataset.mod;
                if (mod === 'ADV') {
                    // Gérer l'avantage
                    this.hasAdvantage = !this.hasAdvantage;
                    btn.classList.toggle('active', this.hasAdvantage);
                    btn.classList.toggle('advantage', this.hasAdvantage);
                    console.log('Avantage:', this.hasAdvantage ? 'activé' : 'désactivé');
                } else {
                    // Retirer l'active de tous les modificateurs numériques
                    modifierButtons.forEach(b => {
                        if (b.dataset.mod !== 'ADV') {
                            b.classList.remove('active');
                        }
                    });
                    
                    // Activer le bouton cliqué
                    btn.classList.add('active');
                    this.currentModifier = parseInt(mod) || 0;
                    document.getElementById('currentMod').textContent = mod;
                }
            });
        });

        // Gérer les clics sur les boutons de dés
        const diceButtons = menu.querySelectorAll('.dice-btn');
        diceButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const diceType = btn.dataset.dice;
                const count = parseInt(diceCount.value) || 1;
                const isPublic = diceVisibility.checked;
                
                await this.rollSingleDice(diceType, count, isPublic);
            });
        });

        // Actions rapides
        const attackBtn = menu.querySelector('.attack-btn');
        const damageBtn = menu.querySelector('.damage-btn');
        const saveBtn = menu.querySelector('.save-btn');

        if (attackBtn) {
            attackBtn.addEventListener('click', () => {
                this.quickAction('attack');
            });
        }

        if (damageBtn) {
            damageBtn.addEventListener('click', () => {
                this.quickAction('damage');
            });
        }

        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.quickAction('save');
            });
        }

        // Limiter le nombre de dés
        diceCount.addEventListener('input', () => {
            let value = parseInt(diceCount.value);
            if (value < 1) diceCount.value = 1;
            if (value > 20) diceCount.value = 20;
        });
    }

    // Nouvelle méthode pour les actions rapides
    async quickAction(action) {
        const isPublic = document.getElementById('diceVisibility').checked;
        
        switch (action) {
            case 'attack':
                // Jet d'attaque : 1d20 + modificateur avec possibilité d'avantage
                await this.rollSingleDice('d20', 1, isPublic, 'Jet d\'attaque');
                break;
                
            case 'damage':
                // Ouvrir un menu rapide pour choisir le type de dégâts
                this.showDamageMenu();
                break;
                
            case 'save':
                // Jet de sauvegarde : 1d20 + modificateur
                await this.rollSingleDice('d20', 1, isPublic, 'Jet de sauvegarde');
                break;
        }
    }

    // Menu pour les dégâts
    showDamageMenu() {
        // Créer un menu contextuel pour choisir les dégâts
        const existingMenu = document.getElementById('damageQuickMenu');
        if (existingMenu) existingMenu.remove();

        const damageMenu = document.createElement('div');
        damageMenu.id = 'damageQuickMenu';
        damageMenu.className = 'damage-quick-menu';
        damageMenu.innerHTML = `
            <div class="damage-menu-content">
                <h4>Dégâts Rapides</h4>
                <div class="damage-options">
                    <button class="damage-option" data-formula="1d6">1d6 (Dague)</button>
                    <button class="damage-option" data-formula="1d8">1d8 (Épée longue)</button>
                    <button class="damage-option" data-formula="1d10">1d10 (Rapière)</button>
                    <button class="damage-option" data-formula="1d12">1d12 (Hache à 2 mains)</button>
                    <button class="damage-option" data-formula="2d6">2d6 (Épée à 2 mains)</button>
                    <button class="damage-option" data-formula="1d4+1">1d4+1 (Projectile magique)</button>
                </div>
                <button class="close-damage-menu">Fermer</button>
            </div>
        `;

        // Positionner près du bouton dégâts
        const damageBtn = document.querySelector('.damage-btn');
        const rect = damageBtn.getBoundingClientRect();
        damageMenu.style.position = 'fixed';
        damageMenu.style.left = (rect.left - 150) + 'px';
        damageMenu.style.top = (rect.top - 200) + 'px';
        damageMenu.style.zIndex = '1001';

        document.body.appendChild(damageMenu);

        // Gestionnaires d'événements
        damageMenu.querySelectorAll('.damage-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const formula = btn.dataset.formula;
                this.rollComposite(formula);
                damageMenu.remove();
        });
        });

        damageMenu.querySelector('.close-damage-menu').addEventListener('click', () => {
            damageMenu.remove();
        });

        // Fermer si on clique en dehors
        setTimeout(() => {
            document.addEventListener('click', function closeMenu(e) {
                if (!damageMenu.contains(e.target)) {
                    damageMenu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        }, 100);
    }

    // Méthode améliorée pour lancer un dé simple
    async rollSingleDice(diceType, count, isPublic, actionType = null) {
        try {
            // Si on est en mode 3D et que les dés 3D sont disponibles
            if (this.is3DMode && this.dice3D) {
                // Pour l'avantage, on lance 2 dés si c'est un d20
                const rollCount = (this.hasAdvantage && diceType === 'd20') ? 2 : count;
                
                const results = await this.dice3D.rollDice(rollCount, diceType);
                
                // Émettre l'événement avec les résultats des dés 3D
                this.socket.emit('roll_dice', {
                    game_id: this.gameId,
                    type: diceType,
                    count: count,
                    is_public: isPublic,
                    results: results,
                    modifier: this.currentModifier,
                    advantage: this.hasAdvantage && diceType === 'd20',
                    action_type: actionType,
                    is_3d: true
                });
            } else {
                // Lancer de dés 2D classique
                this.socket.emit('roll_dice', {
                    game_id: this.gameId,
                    type: diceType,
                    count: count,
                    is_public: isPublic,
                    modifier: this.currentModifier,
                    advantage: this.hasAdvantage && diceType === 'd20',
                    action_type: actionType,
                    is_3d: false
                });
            }

        } catch (error) {
            console.error('Erreur lors du lancer de dés:', error);
            this.showNotification('Erreur lors du lancer de dés', 'error');
        }
    }

    // Nouvelle méthode pour les lancers composés
    rollComposite(formula) {
        if (!formula || formula.trim() === '') {
            this.showNotification('Veuillez entrer une formule de dés', 'error');
            return;
        }

        try {
            // Parser la formule (ex: "2d10+3d6+5")
            const results = this.parseAndRollFormula(formula.trim());
            const isPublic = document.getElementById('diceVisibility').checked;

            // Émettre le résultat
            this.socket.emit('roll_dice', {
                game_id: this.gameId,
                type: 'composite',
                formula: formula,
                is_public: isPublic,
                results: results.rolls,
                total: results.total,
                breakdown: results.breakdown,
                is_3d: false
            });

        } catch (error) {
            this.showNotification('Formule invalide: ' + error.message, 'error');
        }
    }

    // Parser et calculer une formule de dés
    parseAndRollFormula(formula) {
        // Nettoyer la formule
        const cleanFormula = formula.toLowerCase().replace(/\s/g, '');
        
        // Séparer en termes (ex: ["2d10", "+3d6", "+5"])
        const terms = cleanFormula.match(/[+-]?[^+-]+/g) || [];
        
        let total = 0;
        const breakdown = [];
        const rolls = [];

        for (let term of terms) {
            const isNegative = term.startsWith('-');
            const cleanTerm = term.replace(/^[+-]/, '');

            if (cleanTerm.includes('d')) {
                // C'est un dé (ex: "2d10")
                const [countStr, sidesStr] = cleanTerm.split('d');
                const count = parseInt(countStr) || 1;
                const sides = parseInt(sidesStr);

                if (!sides || sides < 2 || count > 20) {
                    throw new Error(`Terme invalide: ${term}`);
                }

                const diceResults = [];
                for (let i = 0; i < count; i++) {
                    const roll = Math.floor(Math.random() * sides) + 1;
                    diceResults.push(roll);
                    rolls.push(roll);
                }

                const sum = diceResults.reduce((a, b) => a + b, 0);
                const finalSum = isNegative ? -sum : sum;
                total += finalSum;
                
                breakdown.push({
                    type: 'dice',
                    formula: `${count}d${sides}`,
                    results: diceResults,
                    sum: finalSum,
                    negative: isNegative
                });

            } else {
                // C'est un modificateur (ex: "5")
                const modifier = parseInt(cleanTerm);
                if (isNaN(modifier)) {
                    throw new Error(`Modificateur invalide: ${term}`);
                }

                const finalModifier = isNegative ? -modifier : modifier;
                total += finalModifier;
                
                breakdown.push({
                    type: 'modifier',
                    value: finalModifier
                });
            }
        }

        return {
            total: total,
            rolls: rolls,
            breakdown: breakdown
        };
    }

    joinGame() {
        this.socket.emit('join_game', { game_id: this.gameId });
    }

    // Gestionnaires d'événements Socket.IO
    handleConnect() {
        console.log('Connecté au serveur');
        this.showNotification('Connexion établie', 'success');
    }

    handleDisconnect() {
        console.log('Déconnecté du serveur');
        this.showNotification('Connexion perdue', 'error');
    }

    handleCurrentPlayers(data) {
        console.log('Liste des joueurs reçue:', data);
        
        // Réinitialiser la Map des joueurs
        this.players.clear();
        
        // Ajouter tous les joueurs
        data.players.forEach(player => {
            this.players.set(player.email, {
                ...player,
                pseudo: player.pseudo || player.email,
                avatar: player.avatar || null,
                is_dm: player.email === data.dm_email,
                is_self: player.email === window.playerEmail
            });
        });
        
        // Mettre à jour l'affichage
        this.updatePlayersList();
    }

    handlePlayerJoined(data) {
        console.log('Joueur rejoint:', data);
        
        const player = {
            email: data.player.email,
            pseudo: data.player.pseudo || data.player.email,
            avatar: data.player.avatar || null,
            is_dm: data.player.email === this.players.get(data.dm_email)?.email,
            is_self: data.player.email === window.playerEmail
        };
        
        // Mettre à jour la Map des joueurs
        this.players.set(player.email, player);
        
        // Forcer la mise à jour de l'affichage
        requestAnimationFrame(() => {
            this.updatePlayersList();
            this.showNotification(`${player.pseudo} a rejoint la partie`, 'info');
        });
    }

    handlePlayerLeft(data) {
        console.log('Joueur parti:', data);
        
        if (this.players.has(data.player_email)) {
            const playerPseudo = this.players.get(data.player_email).pseudo;
            this.players.delete(data.player_email);
            
            requestAnimationFrame(() => {
                this.updatePlayersList();
                this.showNotification(`${playerPseudo} a quitté la partie`, 'info');
            });
        }
    }

    handleDiceRolled(data) {
        // Afficher si :
        // - Le lancer est public
        // - On est le lanceur
        // - On est le MJ
        if (!data.is_public && data.player !== window.playerEmail && !window.isDm) return;

        // Si c'est un lancer 3D des autres joueurs, on peut l'afficher différemment
        if (data.is_3d && data.player !== window.playerEmail) {
            this.showNotification(`${data.player} a lancé des dés 3D`, 'info');
        }

        const resultsContainer = document.getElementById('dice-results');
        const rollElement = document.createElement('div');
        rollElement.className = 'dice-roll-result';
        
        // Ajouter des classes CSS selon le type de lancer
        if (data.advantage) rollElement.classList.add('advantage');
        if (data.type === 'composite') rollElement.classList.add('composite');
        if (data.action_type === 'Jet d\'attaque') rollElement.classList.add('attack');
        if (data.action_type === 'Jet de sauvegarde') rollElement.classList.add('save');
        if (data.formula && (data.formula.includes('d6') || data.formula.includes('d8') || data.formula.includes('d10') || data.formula.includes('d12'))) {
            rollElement.classList.add('damage');
        }
        
        rollElement.style.borderLeftColor = this.getDiceColor(data);

        const visibility = data.is_public ? 'public' : 'privé';
        const formattedResults = this.formatDiceResults(data);
        
        // Ajouter une indication spéciale pour les lancers privés vus par le MJ
        const visibilityText = window.isDm && !data.is_public && data.for_dm 
            ? `(${visibility} - visible car MJ)` 
            : `(${visibility})`;

        const modeText = data.is_3d ? ' 🎲3D' : '';
        const actionText = data.action_type ? ` - ${data.action_type}` : '';

        rollElement.innerHTML = `
            <div class="roll-header">
                <span class="roll-type">${formattedResults}${modeText}${actionText}</span>
                <span class="roll-player">Par ${data.player}</span>
                <span class="roll-visibility">${visibilityText}</span>
            </div>
            ${this.generateRollDetails(data)}
        `;

        // Animation d'apparition
        rollElement.style.opacity = '0';
        resultsContainer.insertBefore(rollElement, resultsContainer.firstChild);
        requestAnimationFrame(() => {
            rollElement.style.opacity = '1';
            rollElement.style.transform = 'translateY(0)';
        });

        // Limiter le nombre de résultats affichés
        while (resultsContainer.children.length > 10) {
            resultsContainer.removeChild(resultsContainer.lastChild);
        }
    }

    // Nouvelle méthode pour générer les détails du lancer
    generateRollDetails(data) {
        let details = '';
        
        // Pour les lancers avec avantage
        if (data.advantage && data.advantage_rolls) {
            details += '<div class="roll-breakdown">';
            details += '<strong>Détail:</strong><br>';
            details += `<span style="color: #27ae60">Avantage: [${data.advantage_rolls.join(', ')}] → meilleur: ${Math.max(...data.advantage_rolls)}</span><br>`;
            
            if (data.modifier && data.modifier !== 0) {
                const modifierText = data.modifier > 0 ? `+${data.modifier}` : `${data.modifier}`;
                details += `<span class="modifier-display">${modifierText}</span><br>`;
            }
            
            details += `<span class="roll-total">Total: ${data.total}</span>`;
            details += '</div>';
        }
        
        // Pour les lancers composés
        else if (data.type === 'composite' && data.breakdown) {
            details += '<div class="roll-breakdown">';
            details += '<strong>Détail:</strong><br>';
            data.breakdown.forEach(item => {
                if (item.type === 'dice') {
                    const sign = item.negative ? '-' : '+';
                    const color = item.negative ? '#e74c3c' : '#27ae60';
                    details += `<span style="color: ${color}">${sign}${item.formula}: [${item.results.join(', ')}] = ${Math.abs(item.sum)}</span><br>`;
                } else if (item.type === 'modifier') {
                    const sign = item.value >= 0 ? '+' : '';
                    details += `<span class="modifier-display">${sign}${item.value}</span><br>`;
                }
            });
            details += `<span class="roll-total">Total: ${data.total}</span>`;
            details += '</div>';
        }
        
        // Pour les lancers normaux avec modificateur
        else if (data.modifier && data.modifier !== 0) {
            details += '<div class="roll-breakdown">';
            details += '<strong>Détail:</strong><br>';
            
            // Afficher le résultat des dés
            if (data.count === 1) {
                const diceResult = data.results[0] - (data.modifier || 0);
                details += `<span style="color: #27ae60">${data.type.toUpperCase()}: [${diceResult}]</span><br>`;
            } else {
                const diceTotal = data.total - (data.modifier || 0);
                details += `<span style="color: #27ae60">${data.count}${data.type.toUpperCase()}: [${data.results.join(', ')}] = ${diceTotal}</span><br>`;
            }
            
            // Afficher le modificateur
            const modifierText = data.modifier > 0 ? `+${data.modifier}` : `${data.modifier}`;
            details += `<span class="modifier-display">${modifierText}</span><br>`;
            details += `<span class="roll-total">Total: ${data.total}</span>`;
            details += '</div>';
        }
        
        return details;
    }

    // Nouvelle méthode pour obtenir la couleur selon le type
    getDiceColor(data) {
        if (data.advantage) return '#27ae60';
        if (data.type === 'composite') return '#9b59b6';
        if (data.action_type === 'Jet d\'attaque') return '#e74c3c';
        if (data.action_type === 'Jet de sauvegarde') return '#3498db';
        return DICE_TYPES[data.type]?.color || '#3498db';
    }

    handleError(data) {
        console.error('Erreur:', data);
        this.showNotification(data.message, 'error');
    }

    handlePlayerUpdated(data) {
        if (this.players.has(data.email)) {
            const player = this.players.get(data.email);
            player.pseudo = data.pseudo;
            player.avatar = data.avatar;
            this.players.set(data.email, player);
            this.updatePlayersList();
        }
    }

    // Gestion des joueurs
    updatePlayersList() {
        const playersList = document.querySelector('.players-list');
        if (!playersList) return;

        // Garder le MJ en place
        const dmItem = playersList.querySelector('.player-item:first-child');
        
        // Nettoyer la liste des joueurs (sauf le MJ)
        Array.from(playersList.children).forEach(child => {
            if (child !== dmItem) {
                child.remove();
            }
        });

        // Ajouter les joueurs
        this.players.forEach(player => {
            if (!player.is_dm) {  // Ne pas recréer le MJ car il est déjà dans le template
                const playerItem = document.createElement('li');
                playerItem.className = 'player-item';
                
                const avatar = document.createElement('div');
                avatar.className = 'player-avatar';
                if (player.avatar) {
                    const img = document.createElement('img');
                    img.src = player.avatar;
                    img.alt = player.pseudo || player.email;
                    avatar.appendChild(img);
                } else {
                    avatar.textContent = (player.pseudo || player.email)[0].toUpperCase();
                }
                
                const info = document.createElement('div');
                info.className = 'player-info';
                
                const name = document.createElement('span');
                name.className = 'player-name';
                name.textContent = player.pseudo || player.email;
                
                info.appendChild(name);
                
                if (player.is_self) {
                    const badges = document.createElement('div');
                    badges.className = 'player-badges';
                    const selfBadge = document.createElement('span');
                    selfBadge.className = 'self-badge';
                    selfBadge.textContent = 'Vous';
                    badges.appendChild(selfBadge);
                    info.appendChild(badges);
                }
                
                playerItem.appendChild(avatar);
                playerItem.appendChild(info);
                playersList.appendChild(playerItem);
            }
        });

        // Afficher le message "Aucun joueur" si nécessaire
        const noPlayersMessage = playersList.querySelector('.no-players');
        const hasPlayers = Array.from(this.players.values()).some(p => !p.is_dm);
        
        if (!hasPlayers) {
            if (!noPlayersMessage) {
                const message = document.createElement('p');
                message.className = 'no-players';
                message.textContent = 'Aucun joueur n\'a encore rejoint la partie';
                playersList.appendChild(message);
            }
        } else if (noPlayersMessage) {
            noPlayersMessage.remove();
        }
    }

    // Gestion des dés
    rollDice(diceType) {
        const count = document.getElementById(`${diceType}-count`).value;
        const isPublic = document.getElementById(`${diceType}-visibility`).checked;

        this.socket.emit('roll_dice', {
            game_id: this.gameId,
            type: diceType,
            count: parseInt(count),
            is_public: isPublic
        });
    }

    formatDiceResults(data) {
        // Pour les lancers composés
        if (data.type === 'composite') {
            return `[${data.formula} = ${data.total}]`;
        }
        
        // Pour les lancers avec avantage
        if (data.advantage) {
            return `[${data.type.toUpperCase()} Avantage = ${data.total}]`;
        }
        
        // Pour les lancers normaux
        if (data.modifier && data.modifier !== 0) {
            const modText = data.modifier > 0 ? `+${data.modifier}` : `${data.modifier}`;
            if (data.count === 1) {
                return `[${data.type.toUpperCase()}${modText} = ${data.total}]`;
            } else {
                return `[${data.count}${data.type.toUpperCase()}${modText} = ${data.total}]`;
            }
        } else {
            // Sans modificateur
            if (data.count === 1) {
                return `[${data.type.toUpperCase()} = ${data.total}]`;
            } else {
                return `[${data.count}${data.type.toUpperCase()} = ${data.total}]`;
            }
        }
    }

    // Utilitaires
    showNotification(message, type = 'info') {
        const notifContainer = document.getElementById('notifications');
        if (!notifContainer) return;

        const notif = document.createElement('div');
        notif.className = `notification ${type}`;
        notif.textContent = message;

        notifContainer.appendChild(notif);
        setTimeout(() => {
            notif.style.opacity = '0';
            setTimeout(() => notif.remove(), 300);
        }, 5000);
    }

    setupProfileSync() {
        // Écouter les changements de profil
        document.addEventListener('userProfileUpdated', (event) => {
            const { pseudo, avatar } = event.detail;
            this.socket.emit('update_player', {
                game_id: this.gameId,
                pseudo: pseudo,
                avatar: avatar
            });
        });
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    window.gameClient = new GameClient();
});

// Gestionnaires d'événements
function handleDiceRoll(diceType) {
    window.gameClient.rollDice(diceType);
}

function updateButtonText(diceType) {
    const countInput = document.getElementById(`${diceType}-count`);
    const button = document.getElementById(`${diceType}-button`);
    const count = parseInt(countInput.value) || 1;
    button.textContent = `Lancer ${count}${diceType.toUpperCase()}`;
}

// Gestion de la déconnexion
window.addEventListener('beforeunload', () => {
    if (window.gameClient) {
        window.gameClient.socket.emit('leave_game', { 
            game_id: window.gameClient.gameId 
        });
    }
}); 