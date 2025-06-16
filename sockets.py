from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from datetime import datetime
import random
import json
import os
from models.user import User  # Ajout de l'import

def load_json(filename):
    filepath = os.path.join('data', filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(data, filename):
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class GameNamespace:
    """Gestion des WebSockets pour les parties de jeu"""

    def __init__(self, socketio):
        self.socketio = socketio
        # Structure : game_id -> {players: {email: {is_dm: bool, pseudo: str, avatar: str}}}
        self.active_games = {}

    def init_app(self):
        """Initialise les événements Socket.IO"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Vérifie l'authentification à la connexion"""
            if not current_user.is_authenticated:
                return False
            print(f"Client connecté: {current_user.email}")
            return True

        @self.socketio.on('join_game')
        def handle_join_game(data):
            """Gère l'arrivée d'un joueur dans une partie"""
            game_id = data['game_id']
            room = f"game_{game_id}"
            user_email = current_user.email
            
            # Charger les données de la partie
            games = load_json('games.json')
            if game_id not in games:
                emit('error', {'message': 'Partie introuvable'})
                return
            
            game = games[game_id]
            is_dm = user_email == game['dm_email']
            
            # Récupérer les informations de l'utilisateur
            user = User.get_by_email(user_email)
            if not user:
                user = User(email=user_email, pseudo=user_email)
            
            # Rejoindre la room Socket.IO
            join_room(room)
            
            # Initialiser la room si nécessaire
            if room not in self.active_games:
                self.active_games[room] = {
                    'players': {},
                    'dm_email': game['dm_email']
                }
            
            # Ajouter le joueur à la liste active
            self.active_games[room]['players'][user_email] = {
                'is_dm': is_dm,
                'pseudo': user.pseudo,
                'avatar': user.avatar,
                'joined_at': datetime.now().isoformat()
            }

            # Envoyer la notification à tous les clients AVANT d'envoyer la liste complète
            emit('player_joined', {
                'player': {
                    'email': user_email,
                    'is_dm': is_dm,
                    'pseudo': user.pseudo,
                    'avatar': user.avatar,
                    'is_self': False
                },
                'timestamp': datetime.now().isoformat()
            }, broadcast=True, room=room)

            # Envoyer la liste complète à TOUS les clients
            player_list = {
                'players': [
                    {
                        'email': email,
                        'is_dm': data['is_dm'],
                        'pseudo': data['pseudo'],
                        'avatar': data['avatar'],
                        'is_self': False  # Le client déterminera lui-même si c'est lui
                    }
                    for email, data in self.active_games[room]['players'].items()
                ],
                'dm_email': game['dm_email']
            }
            emit('current_players', player_list, broadcast=True, room=room)

            # Si c'est un nouveau joueur (pas le MJ et pas déjà dans la partie)
            if not is_dm and user_email not in game.get('players', []):
                if 'players' not in game:
                    game['players'] = []
                game['players'].append(user_email)
                save_json(games, 'games.json')
                
                # Notifier les autres joueurs
                emit('player_joined', {
                    'player': {
                        'email': user_email,
                        'is_dm': is_dm,
                        'pseudo': user.pseudo,
                        'avatar': user.avatar,
                        'is_self': False
                    },
                    'timestamp': datetime.now().isoformat()
                }, room=room, broadcast=True)  # Broadcast à tous les clients dans la room

        @self.socketio.on('leave_game')
        def handle_leave_game(data):
            """Gère le départ d'un joueur"""
            game_id = data['game_id']
            room = f"game_{game_id}"
            user_email = current_user.email
            
            leave_room(room)
            
            if room in self.active_games:
                # Retirer le joueur de la liste active
                if user_email in self.active_games[room]['players']:
                    del self.active_games[room]['players'][user_email]
                
                # Notifier les autres joueurs
                emit('player_left', {
                    'player_email': user_email,
                    'timestamp': datetime.now().isoformat()
                }, room=room)
                
                # Si la room est vide, la nettoyer
                if not self.active_games[room]['players']:
                    del self.active_games[room]

        @self.socketio.on('roll_dice')
        def handle_roll_dice(data):
            """Gère les lancers de dés (2D et 3D)"""
            try:
                game_id = data['game_id']
                room = f"game_{game_id}"
                dice_type = data['type']  # 'd4', 'd6', 'composite', etc.
                count = int(data.get('count', 1))
                is_public = data['is_public']
                is_3d = data.get('is_3d', False)
                pre_calculated_results = data.get('results', None)
                modifier = data.get('modifier', 0)
                formula = data.get('formula', '')
                breakdown = data.get('breakdown', [])
                advantage = data.get('advantage', False)
                action_type = data.get('action_type', None)
                
                # Récupérer les informations de l'utilisateur
                user = User.get_by_email(current_user.email)
                if not user:
                    user = User(email=current_user.email, pseudo=current_user.email)
                
                # Gestion des lancers composés
                if dice_type == 'composite':
                    if not formula:
                        emit('error', {'message': 'Formule manquante pour le lancer composé'})
                        return
                    
                    # Pour les lancers composés, on utilise les résultats du client
                    total = data.get('total', 0)
                    results = pre_calculated_results or []
                    
                    response = {
                        'type': 'composite',
                        'formula': formula,
                        'results': results,
                        'total': total,
                        'breakdown': breakdown,
                        'player': user.pseudo,
                        'is_public': is_public,
                        'is_3d': False,
                        'action_type': action_type,
                        'timestamp': datetime.now().isoformat()
                    }
                
                else:
                    # Validation pour les dés simples
                    if count < 1 or count > 100:
                        count = 1
                    dice_max = int(dice_type[1:]) if dice_type.startswith('d') else 20
                    if dice_max not in [4, 6, 8, 10, 12, 20, 100]:
                        emit('error', {'message': 'Type de dé invalide'})
                        return
                
                    # Gestion de l'avantage pour D20
                    if advantage and dice_type == 'd20':
                        if is_3d and pre_calculated_results and len(pre_calculated_results) >= 2:
                            # Prendre le meilleur résultat des dés 3D
                            results = [max(pre_calculated_results[:2])]
                            advantage_results = pre_calculated_results[:2]
                        else:
                            # Lancer 2 dés et prendre le meilleur
                            advantage_results = [random.randint(1, dice_max), random.randint(1, dice_max)]
                            results = [max(advantage_results)]
                        
                        # Appliquer le modificateur
                        if modifier != 0:
                            final_result = max(1, results[0] + modifier)
                            results = [final_result]
                        
                        response = {
                            'type': dice_type,
                            'count': 1,
                            'results': results,
                            'total': results[0],
                            'advantage_rolls': advantage_results,
                            'modifier': modifier,
                            'player': user.pseudo,
                            'is_public': is_public,
                            'is_3d': is_3d,
                            'advantage': True,
                            'action_type': action_type,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        # Lancer normal
                        if is_3d and pre_calculated_results and len(pre_calculated_results) == count:
                            # Vérifier que les résultats sont valides
                            valid_results = all(1 <= result <= dice_max for result in pre_calculated_results)
                            if valid_results:
                                results = pre_calculated_results[:]
                            else:
                                results = [random.randint(1, dice_max) for _ in range(count)]
                                is_3d = False
                        else:
                            results = [random.randint(1, dice_max) for _ in range(count)]
                            is_3d = False
                        
                        # Appliquer le modificateur à chaque dé ou au total selon le contexte
                        if modifier != 0:
                            # Pour les dés uniques, modifier directement
                            if count == 1:
                                results = [max(1, results[0] + modifier)]
                            # Pour les dés multiples, on ajoute le modificateur au total
                        
                        total = sum(results) + (modifier if count > 1 else 0)
                        
                        response = {
                            'type': dice_type,
                            'count': count,
                            'results': results,
                            'total': total,
                            'modifier': modifier,
                            'player': user.pseudo,
                            'is_public': is_public,
                            'is_3d': is_3d,
                            'action_type': action_type,
                            'timestamp': datetime.now().isoformat()
                        }

                # Si le lancer est public, l'envoyer à toute la room
                if is_public:
                    emit('dice_rolled', response, room=room)
                else:
                    # Si privé, envoyer uniquement au lanceur
                    emit('dice_rolled', response)
                    
                    # Et toujours au MJ
                    games = load_json('games.json')
                    if game_id in games:
                        dm_email = games[game_id]['dm_email']
                        # Ne pas renvoyer au MJ s'il est le lanceur
                        if dm_email != current_user.email:
                            response_for_dm = response.copy()
                            response_for_dm['for_dm'] = True
                            # Émettre spécifiquement au MJ
                            emit('dice_rolled', response_for_dm, room=room)
                
            except Exception as e:
                print(f"Erreur lors du lancer de dés: {e}")
                emit('error', {'message': 'Erreur lors du lancer de dés'})

        @self.socketio.on('update_player')
        def handle_player_update(data):
            """Gère la mise à jour des informations d'un joueur"""
            game_id = data['game_id']
            room = f"game_{game_id}"
            user_email = current_user.email
            
            if room in self.active_games:
                if user_email in self.active_games[room]['players']:
                    # Mettre à jour les informations du joueur
                    self.active_games[room]['players'][user_email].update({
                        'pseudo': data['pseudo'],
                        'avatar': data['avatar']
                    })
                    
                    # Notifier tous les clients dans la room
                    emit('player_updated', {
                        'email': user_email,
                        'pseudo': data['pseudo'],
                        'avatar': data['avatar']
                    }, room=room) 