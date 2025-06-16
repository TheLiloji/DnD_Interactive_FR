# Système de Dés 3D pour D&D

## Description

Ce projet intègre un système de dés 3D basé sur Three.js et Cannon.js dans l'application D&D existante. Les joueurs peuvent maintenant lancer des dés en 3D avec physique réaliste, sons et animations.

## Fonctionnalités

### Dés Supportés
- **D4** - Tétraèdre
- **D6** - Cube
- **D8** - Octaèdre  
- **D10** - Cône
- **D12** - Dodécaèdre
- **D20** - Icosaèdre
- **D100** - Sphère

### Options Avancées
- **Effets sonores** - 15 sons différents de collision
- **Ombres** - Rendu avec ombres réalistes
- **Physique** - 3 niveaux d'intensité (faible, normale, élevée)

### Interface
- **Bouton Mode 3D** - Bascule entre vue 2D et 3D
- **Bouton Effacer** - Nettoie la surface de jeu
- **Options** - Double-clic sur Mode 3D pour les options avancées

## Architecture Technique

### Fichiers Principaux
- `static/js/dice3d.js` - Classe principale des dés 3D
- `static/socket.js` - Intégration WebSocket modifiée
- `templates/game.html` - Interface utilisateur
- `static/game.css` - Styles pour les dés 3D
- `sockets.py` - Gestion serveur des dés 3D

### Librairies Utilisées
- **Three.js** - Rendu 3D
- **Cannon.js** - Moteur physique
- **Socket.IO** - Communication temps réel

### Système de Physique
- Gravité réaliste
- Collision entre dés
- Surfaces avec friction
- Murs invisibles pour contenir les dés

## Utilisation

1. **Activer le mode 3D** : Cliquer sur le bouton "Mode 3D" dans la sidebar
2. **Lancer des dés** : Utiliser le menu flottant (bouton 🎲) pour choisir type et nombre
3. **Options avancées** : Double-cliquer sur "Mode 3D" pour accéder aux paramètres
4. **Effacer** : Bouton "Effacer" pour nettoyer la surface

## Intégration Serveur

Les résultats des dés 3D sont calculés côté client avec validation serveur :
- Les résultats physiques sont envoyés au serveur
- Le serveur valide la cohérence (1 ≤ résultat ≤ max_faces)
- Si invalide, le serveur génère de nouveaux résultats
- Les lancers sont synchronisés entre tous les joueurs

## Performance

- Détection automatique des capacités WebGL
- Fallback vers dés 2D si les librairies 3D ne sont pas disponibles
- Rendu optimisé à 60 FPS
- Gestion mémoire avec nettoyage automatique

## Personnalisation

### Couleurs des Dés
Palette moderne prédéfinie avec 7 couleurs vives

### Sons
15 fichiers audio différents pour la variété

### Physique
Paramètres ajustables pour différents niveaux de détail

## Compatibilité

- **Navigateurs modernes** avec support WebGL
- **Mobiles** avec interface responsive
- **Desktop** avec contrôles souris optimisés 