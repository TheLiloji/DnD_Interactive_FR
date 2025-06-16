from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
import re
import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sockets import GameNamespace
from oauthlib.oauth2 import WebApplicationClient
import requests
from models.user import User  # Import de notre nouvelle classe User

# Pour le développement uniquement
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configuration OAuth Google
GOOGLE_CLIENT_ID = "788777892892-k7fso5fkemnm5dcs9n9m52sfg9udd2e0.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Configuration de l'application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clé_secrète_ici'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Client OAuth 2.0
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Configuration du login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialisation des WebSockets
game_namespace = GameNamespace(socketio)
game_namespace.init_app()

# Gestion des données
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Routes principales
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    games = load_json('games.json')
    # Charger les personnages de l'utilisateur
    characters = load_json('characters.json')
    user_characters = characters.get(current_user.email, [])
    return render_template('dashboard.html', games=games, characters=user_characters)

@app.route('/game/<game_id>')
@login_required
def game(game_id):
    """Page de jeu en temps réel"""
    games = load_json('games.json')
    if game_id not in games:
        flash('Cette partie n\'existe pas', 'error')
        return redirect(url_for('dashboard'))
    
    game = games[game_id]
    user_email = current_user.email
    
    # Vérifier l'accès
    if user_email != game['dm_email'] and user_email not in game.get('players', []):
        flash('Vous n\'avez pas accès à cette partie', 'error')
        return redirect(url_for('dashboard'))
    
    # Récupérer les informations du MJ
    dm = User.get_by_email(game['dm_email'])
    if not dm:
        dm = User(email=game['dm_email'], pseudo=game['dm_email'])
    
    # Récupérer les informations des joueurs
    players = []
    for player_email in game.get('players', []):
        player = User.get_by_email(player_email)
        if not player:
            player = User(email=player_email, pseudo=player_email)
        players.append(player)
    
    # Configuration des dés pour le template
    dice_types = {
        'd4': { 'color': '#FF6B6B' },
        'd6': { 'color': '#4ECDC4' },
        'd8': { 'color': '#45B7D1' },
        'd10': { 'color': '#96CEB4' },
        'd12': { 'color': '#FFEEAD' },
        'd20': { 'color': '#D4A373' },
        'd100': { 'color': '#9B5DE5' }
    }
    
    return render_template('game.html', 
                         game=game, 
                         game_id=game_id, 
                         is_dm=(user_email == game['dm_email']),
                         dm=dm,
                         players=players,
                         DICE_TYPES=dice_types)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.get_by_email(email)
        if user and user.password and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Email ou mot de passe incorrect')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        needs_tutorial = request.form.get('needs_tutorial') == 'on'
        
        # Vérifier si l'utilisateur existe déjà
        if User.get_by_email(email):
            flash('Cet email est déjà utilisé', 'error')
            return render_template('register.html')
        
        # Créer un nouvel utilisateur
        user = User(
            email=email,
            password=generate_password_hash(password),
            needs_tutorial=needs_tutorial,
            characters=[],
            pseudo=email  # Utiliser l'email comme pseudo par défaut
        )
        user.save()
        
        login_user(user)
        flash('Compte créé avec succès !', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def generate_game_code():
    """Génère un code unique de 6 caractères pour une partie."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        games = load_json('games.json')
        if code not in games:
            return code

@app.route('/create_game')
@login_required
def create_game_page():
    """Page de création de partie"""
    return render_template('create_game.html')

@app.route('/character_creation')
@login_required
def character_creation():
    """Page de création de personnage"""
    return render_template('character_creation.html')

@app.route('/create_character', methods=['POST'])
@login_required
def create_character():
    """Traiter la création d'un personnage"""
    try:
        # Données de base
        character_data = {
            'name': request.form.get('character_name'),
            'level': int(request.form.get('character_level', 1)),
            'class': request.form.get('selected_class'),
            'race': request.form.get('selected_race'),
            'background': request.form.get('selected_background'),
            'abilities': {
                'force': int(request.form.get('force', 10)),
                'dexterite': int(request.form.get('dexterite', 10)),
                'constitution': int(request.form.get('constitution', 10)),
                'intelligence': int(request.form.get('intelligence', 10)),
                'sagesse': int(request.form.get('sagesse', 10)),
                'charisme': int(request.form.get('charisme', 10))
            },
            'skills': request.form.getlist('skills'),
            'owner': current_user.email,
            'created_at': datetime.now().isoformat()
        }
        
        # Données de progression (sous-classe, multiclassing)
        progression_data = {
            'subclass': request.form.get('selected_subclass', ''),
            'multiclass': request.form.get('selected_multiclass', ''),
            'progression_choice': request.form.get('progression_choice', 'single')
        }
        
        # Ajouter les données de progression si elles existent
        if progression_data['subclass']:
            character_data['subclass'] = progression_data['subclass']
        if progression_data['multiclass']:
            character_data['multiclass'] = progression_data['multiclass']
        character_data['progression_choice'] = progression_data['progression_choice']
        
        # Sorts sélectionnés
        selected_spells_json = request.form.get('selected_spells', '[]')
        try:
            selected_spells = json.loads(selected_spells_json)
            character_data['selected_spells'] = selected_spells
        except json.JSONDecodeError:
            character_data['selected_spells'] = []
        
        # Choix raciaux et de classe
        try:
            racial_choices_json = request.form.get('racial_choices', '{}')
            character_data['racial_choices'] = json.loads(racial_choices_json)
        except json.JSONDecodeError:
            character_data['racial_choices'] = {}
            
        try:
            class_skills_json = request.form.get('class_skills', '[]')
            character_data['class_skills'] = json.loads(class_skills_json)
        except json.JSONDecodeError:
            character_data['class_skills'] = []
        
        # Données d'équipement
        equipment_data = {
            'custom_equipment': request.form.get('custom_equipment', ''),
            'selected_armor': request.form.get('selected_armor', ''),
            'selected_shield': request.form.get('selected_shield', ''),
            'selected_main_weapon': request.form.get('selected_main_weapon', ''),
            'selected_secondary_weapon': request.form.get('selected_secondary_weapon', ''),
            'selected_backup_weapon': request.form.get('selected_backup_weapon', ''),
            'selected_inventory': request.form.getlist('selected_inventory')
        }
        
        # Ajouter les données d'équipement au personnage
        character_data['equipment'] = equipment_data
        
        # Données de finalisation
        finalization_data = {
            'sex': request.form.get('character_sex', ''),
            'alignment': request.form.get('character_alignment', ''),
            'age': request.form.get('character_age', ''),
            'height': request.form.get('character_height', ''),
            'weight': request.form.get('character_weight', ''),
            'image_url': request.form.get('character_image_url', ''),
            'eyes': request.form.get('character_eyes', ''),
            'skin': request.form.get('character_skin', ''),
            'hair': request.form.get('character_hair', ''),
            'appearance': request.form.get('character_appearance', ''),
            'history': request.form.get('character_history', '')
        }
        
        # Ajouter les données de finalisation au personnage
        character_data['finalization'] = finalization_data
        
        # Charger les personnages existants
        characters = load_json('characters.json')
        if current_user.email not in characters:
            characters[current_user.email] = []
        
        # Ajouter le nouveau personnage
        characters[current_user.email].append(character_data)
        save_json(characters, 'characters.json')
        
        # Message de succès avec détails de progression et équipement
        success_msg = f'Personnage "{character_data["name"]}" créé avec succès !'
        if character_data.get('subclass'):
            success_msg += f' Sous-classe: {character_data["subclass"]}'
        if character_data.get('multiclass'):
            success_msg += f' Multiclassing: {character_data["multiclass"]}'
        if character_data.get('selected_spells'):
            success_msg += f' avec {len(character_data["selected_spells"])} sorts'
        
        # Ajouter les informations d'équipement au message
        equipment = character_data.get('equipment', {})
        equipment_parts = []
        if equipment.get('selected_armor'):
            equipment_parts.append(f"Armure: {equipment['selected_armor']}")
        if equipment.get('selected_shield'):
            equipment_parts.append(f"Bouclier: {equipment['selected_shield']}")
        if equipment.get('selected_main_weapon'):
            equipment_parts.append(f"Arme principale: {equipment['selected_main_weapon']}")
        if equipment.get('selected_inventory'):
            equipment_parts.append(f"{len(equipment['selected_inventory'])} objets d'inventaire")
        
        if equipment_parts:
            success_msg += f' - Équipement: {", ".join(equipment_parts)}'
        
        # Ajouter les informations de finalisation au message
        finalization = character_data.get('finalization', {})
        finalization_parts = []
        if finalization.get('sex'):
            finalization_parts.append(f"Sexe: {finalization['sex']}")
        if finalization.get('alignment'):
            finalization_parts.append(f"Alignement: {finalization['alignment']}")
        if finalization.get('age'):
            finalization_parts.append(f"Âge: {finalization['age']} ans")
        
        if finalization_parts:
            success_msg += f' - Détails: {", ".join(finalization_parts)}'
        
        # Calculer l'index du nouveau personnage (le dernier ajouté)
        character_index = len(characters[current_user.email]) - 1
        
        flash(success_msg, 'success')
        return redirect(url_for('character_sheet', character_index=character_index))
        
    except Exception as e:
        flash(f'Erreur lors de la création du personnage : {str(e)}', 'error')
        return redirect(url_for('character_creation'))

@app.route('/character/<int:character_index>')
@login_required
def character_sheet(character_index):
    """Afficher la fiche d'un personnage spécifique"""
    characters = load_json('characters.json')
    user_characters = characters.get(current_user.email, [])
    
    if character_index < 0 or character_index >= len(user_characters):
        flash('Personnage introuvable', 'error')
        return redirect(url_for('dashboard'))
    
    character = user_characters[character_index]
    
    # Fonctions utilitaires pour les calculs
    def calculate_hit_points(char):
        hit_dice = {
            'barbare': 12, 'guerrier': 10, 'paladin': 10, 'rôdeur': 10,
            'barde': 8, 'clerc': 8, 'druide': 8, 'moine': 8, 'roublard': 8, 'sorcier': 8,
            'ensorceleur': 6, 'magicien': 6
        }
        hit_die = hit_dice.get(char['class'].lower(), 8)
        con_bonus = char.get('racial_choices', {}).get('constitution', 0)
        con_modifier = ((char['abilities']['constitution'] + con_bonus - 10) // 2)
        return hit_die + con_modifier + ((char['level'] - 1) * (hit_die // 2 + 1 + con_modifier))
    
    def calculate_armor_class(char):
        base_ac = 10
        dex_bonus = char.get('racial_choices', {}).get('dexterite', 0)
        dex_modifier = ((char['abilities']['dexterite'] + dex_bonus - 10) // 2)
        
        equipment = char.get('equipment', {})
        if equipment.get('selected_armor'):
            # Simplification : CA de base + mod dex pour armure légère
            base_ac = 11 + dex_modifier  # Armure de cuir par défaut
        else:
            base_ac = 10 + dex_modifier
            
        if equipment.get('selected_shield'):
            base_ac += 2
            
        return base_ac
    
    def get_hit_die(class_name):
        hit_dice = {
            'barbare': 12, 'guerrier': 10, 'paladin': 10, 'rôdeur': 10,
            'barde': 8, 'clerc': 8, 'druide': 8, 'moine': 8, 'roublard': 8, 'sorcier': 8,
            'ensorceleur': 6, 'magicien': 6
        }
        return hit_dice.get(class_name.lower(), 8)
    
    return render_template('character_sheet.html', 
                         character=character, 
                         character_index=character_index,
                         calculate_hit_points=calculate_hit_points,
                         calculate_armor_class=calculate_armor_class)

@app.route('/characters')
@login_required  
def characters_list():
    """Liste de tous les personnages de l'utilisateur"""
    characters = load_json('characters.json')
    user_characters = characters.get(current_user.email, [])
    
    # Fonctions utilitaires pour les calculs
    def get_hit_die(class_name):
        hit_dice = {
            'barbare': 12, 'guerrier': 10, 'paladin': 10, 'rôdeur': 10,
            'barde': 8, 'clerc': 8, 'druide': 8, 'moine': 8, 'roublard': 8, 'sorcier': 8,
            'ensorceleur': 6, 'magicien': 6
        }
        return hit_dice.get(class_name.lower(), 8)
    
    return render_template('characters_list.html', characters=user_characters, get_hit_die=get_hit_die)

@app.route('/delete_character/<int:character_index>', methods=['POST'])
@login_required
def delete_character(character_index):
    """Supprimer un personnage"""
    try:
        characters = load_json('characters.json')
        user_characters = characters.get(current_user.email, [])
        
        if character_index < 0 or character_index >= len(user_characters):
            return jsonify({'success': False, 'error': 'Personnage introuvable'})
        
        # Supprimer le personnage
        deleted_character = user_characters.pop(character_index)
        characters[current_user.email] = user_characters
        save_json(characters, 'characters.json')
        
        return jsonify({
            'success': True, 
            'message': f'Personnage "{deleted_character["name"]}" supprimé avec succès'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/join_game', methods=['POST'])
@login_required
def join_game():
    game_code = request.form.get('game_code', '').upper()
    if not game_code:
        flash('Le code de la partie est requis', 'error')
        return redirect(url_for('dashboard'))
    
    games = load_json('games.json')
    if game_code not in games:
        flash('Code de partie invalide', 'error')
        return redirect(url_for('dashboard'))
    
    game = games[game_code]
    user_email = current_user.email

    # Si l'utilisateur est le MJ, rediriger directement
    if user_email == game['dm_email']:
        return redirect(url_for('game', game_id=game_code))
    
    # Si l'utilisateur est déjà dans la partie
    if user_email in game.get('players', []):
        return redirect(url_for('game', game_id=game_code))
    
    # Ajouter le joueur à la partie
    if 'players' not in game:
        game['players'] = []
    game['players'].append(user_email)
    save_json(games, 'games.json')
    
    flash('Vous avez rejoint la partie avec succès !', 'success')
    return redirect(url_for('game', game_id=game_code))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/google_login")
def google_login():
    # Trouver l'URL de découverte des endpoints d'authentification Google
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Construire la requête pour Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for('google_authorized', _external=True),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/google/authorized")
def google_authorized():
    # Récupérer le code d'autorisation que Google a envoyé
    code = request.args.get("code")
    
    # Trouver l'URL pour échanger le code contre les tokens
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Préparer et envoyer la requête pour obtenir les tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=url_for('google_authorized', _external=True),
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Analyser les tokens
    client.parse_request_body_response(token_response.text)

    # Récupérer les informations de profil de l'utilisateur
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers)

    if userinfo_response.json().get("email_verified"):
        email = userinfo_response.json()["email"]
        
        # Créer ou mettre à jour l'utilisateur
        user = User.get_by_email(email)
        if not user:
            user = User(
                email=email,
                needs_tutorial=True,
                pseudo=email
            )
            user.save()
        
        # Connecter l'utilisateur
        login_user(user)
        return redirect(url_for('dashboard'))
    else:
        flash("L'authentification Google a échoué", "error")
        return redirect(url_for('login'))

@login_manager.user_loader
def load_user(email):
    return User.get_by_email(email)

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    
    if not data or 'pseudo' not in data:
        return jsonify({'error': 'Données invalides'}), 400
    
    pseudo = data.get('pseudo').strip()
    avatar = data.get('avatar', '').strip() or None
    
    if not pseudo:
        return jsonify({'error': 'Le pseudo ne peut pas être vide'}), 400
        
    try:
        current_user.update_profile(new_pseudo=pseudo, new_avatar=avatar)
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': {
                'email': current_user.email,
                'pseudo': current_user.pseudo,
                'avatar': current_user.avatar
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_game', methods=['POST'])
@login_required
def api_create_game():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Données invalides'}), 400
    
    game_code = generate_game_code()
    games = load_json('games.json')
    
    games[game_code] = {
        'name': data['name'],
        'description': data.get('description', ''),
        'dm_email': current_user.email,
        'players': [],
        'max_players': data.get('max_players', 5),
        'password': generate_password_hash(data['password']) if data.get('password') else None,
        'game_type': data.get('game_type', 'standard'),
        'options': data.get('options', {
            'allow_spectators': False,
            'auto_level': False,
            'voice_chat': False,
            'dice_validation': False
        }),
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    save_json(games, 'games.json')
    
    return jsonify({
        'message': 'Partie créée avec succès',
        'game_id': game_code
    })

@app.route('/api/update_game_settings/<game_id>', methods=['POST'])
@login_required
def update_game_settings(game_id):
    """Mettre à jour les paramètres d'une partie"""
    games = load_json('games.json')
    if game_id not in games:
        return jsonify({'error': 'Cette partie n\'existe pas'}), 404
    
    game = games[game_id]
    if current_user.email != game['dm_email']:
        return jsonify({'error': 'Seul le MJ peut modifier les paramètres'}), 403
    
    data = request.get_json()
    
    # Mettre à jour les paramètres
    game['name'] = data['name']
    game['description'] = data['description']
    game['max_players'] = data['max_players']
    game['game_type'] = data['game_type']
    game['options'] = data['options']
    
    save_json(games, 'games.json')
    
    return jsonify({'message': 'Paramètres mis à jour avec succès'})

@app.route('/api/backgrounds')
def get_backgrounds():
    """API pour récupérer tous les historiques depuis les fichiers README"""
    
    backgrounds_dir = 'data/docs/personnalite-et-historique'
    backgrounds = {}
    
    try:
        # Lister tous les dossiers d'historiques
        for item in os.listdir(backgrounds_dir):
            item_path = os.path.join(backgrounds_dir, item)
            if os.path.isdir(item_path) and item != '__pycache__':
                readme_path = os.path.join(item_path, 'README.md')
                if os.path.exists(readme_path):
                    background_data = parse_background_readme(readme_path, item)
                    if background_data:
                        backgrounds[item] = background_data
        
        return jsonify(backgrounds)
    except Exception as e:
        print(f"Erreur lors de la lecture des historiques: {e}")
        return jsonify({})

def parse_background_readme(file_path, background_id):
    """Parse un fichier README d'historique"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraction du titre
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else background_id.title()
        
        # Extraction des compétences (avec gestion des choix)
        skills_match = re.search(r'\*\*Compétences\*\*\s*:\s*(.+?)\.', content)
        skills = []
        skill_choices = []
        if skills_match:
            skills_text = skills_match.group(1)
            skill_parts = [part.strip() for part in skills_text.split(',')]
            
            for part in skill_parts:
                if ' ou ' in part:
                    # Compétence avec choix (ex: "Investigation ou Persuasion")
                    choice_options = [opt.strip() for opt in part.split(' ou ')]
                    skill_choices.append({
                        'description': part,
                        'options': choice_options
                    })
                else:
                    # Compétence fixe
                    skills.append(part)
        
        # Extraction des outils maîtrisés
        tools_match = re.search(r'\*\*Outils maîtrisés\*\*\s*:\s*(.+?)\.', content)
        tools = []
        if tools_match:
            tools_text = tools_match.group(1)
            tools = [tool.strip() for tool in tools_text.split(',')]
        
        # Extraction des langues (si présentes)
        languages_match = re.search(r'\*\*Langues maîtrisées\*\*\s*:\s*(.+?)\.', content)
        languages = []
        if languages_match:
            languages_text = languages_match.group(1)
            languages = [lang.strip() for lang in languages_text.split(',')]
        
        # Extraction de l'équipement
        equipment_match = re.search(r'\*\*Équipement\*\*\s*:\s*(.+?)\.', content)
        equipment = []
        if equipment_match:
            equipment_text = equipment_match.group(1)
            equipment = [item.strip() for item in equipment_text.split(',')]
        
        # Extraction de l'aptitude principale
        ability = extract_main_ability(content)
        
        # Extraction des sections spéciales (comme milieu naturel)
        special_sections = extract_special_sections(content)
        
        # Extraction des sections de choix interactives (comme Unité)
        choice_sections = extract_choice_sections(content)
        
        # Extraction des traits de personnalité (avec fonction améliorée)
        personality_section = extract_personality_data(content, 'Trait de personnalité')
        ideals_section = extract_personality_data(content, 'Idéal')
        bonds_section = extract_personality_data(content, 'Lien')
        flaws_section = extract_personality_data(content, 'Défaut')
        
        # Extraction des variantes (mais pas affichées par défaut)
        variants = extract_variants(content)
        
        return {
            'id': background_id,
            'title': title,
            'skills': skills,
            'skill_choices': skill_choices,
            'tools': tools,
            'languages': languages,
            'equipment': equipment,
            'ability': ability,
            'special_sections': special_sections,
            'choice_sections': choice_sections,
            'personality_traits': personality_section,
            'ideals': ideals_section,
            'bonds': bonds_section,
            'flaws': flaws_section,
            'variants': variants
        }
        
    except Exception as e:
        print(f"Erreur lors du parsing de {file_path}: {e}")
        return None

def extract_personality_data(content, table_name):
    """Extrait les données des tables de personnalité avec format **1** """
    try:
        # Pattern pour capturer une table avec le nom donné
        pattern = rf'\|\s*D\d+\s*\|\s*{re.escape(table_name)}\s*\|(.*?)(?=\n\n|\|\s*D\d+\s*\||\#\#|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return []
        
        table_content = match.group(1)
        rows = []
        
        for line in table_content.split('\n'):
            if line.strip() and '|' in line:
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 3:
                    roll_part = parts[1].strip()
                    # Gérer les formats **1** ou 1
                    if roll_part.startswith('**') and roll_part.endswith('**'):
                        roll_num = roll_part.replace('**', '')
                        if roll_num.isdigit():
                            rows.append({
                                'roll': roll_num,
                                'text': parts[2].strip()
                            })
                    elif roll_part.isdigit():
                        rows.append({
                            'roll': roll_part,
                            'text': parts[2].strip()
                        })
        
        return rows
    except Exception:
        return []

def extract_table_data(content, table_name):
    """Extrait les données d'une table spécifique"""
    try:
        # Pattern pour capturer une table avec le nom donné
        pattern = rf'\|\s*D\d+\s*\|\s*{re.escape(table_name)}\s*\|(.*?)(?=\n\n|\|\s*D\d+\s*\||\#\#|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return []
        
        table_content = match.group(1)
        rows = []
        
        for line in table_content.split('\n'):
            if line.strip() and '|' in line:
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 3 and parts[1].strip().isdigit():
                    # Format: | D | Contenu |
                    rows.append({
                        'roll': parts[1].strip(),
                        'text': parts[2].strip()
                    })
        
        return rows
    except Exception:
        return []

def extract_variants(content):
    """Extrait les variantes d'un historique"""
    variants = {}
    
    # Pattern pour les variantes
    variant_pattern = r'## Variante : (.+?)\n(.*?)(?=## Variante|$)'
    matches = re.findall(variant_pattern, content, re.DOTALL)
    
    for variant_name, variant_content in matches:
        variant_data = {
            'name': variant_name.strip(),
            'skills': [],
            'skill_choices': [],
            'tools': [],
            'languages': [],
            'equipment': [],
            'ability': None
        }
        
        # Extraction de l'aptitude spécifique à la variante (si elle existe)
        # Pattern robuste pour les aptitudes de variantes
        ability_match = re.search(r'### Aptitude : (.+?)\n([\s\S]*?)(?=\n## |\n### |\n\*\*|\n$)', variant_content)
        if ability_match:
            variant_data['ability'] = {
                'name': ability_match.group(1).strip(),
                'description': ability_match.group(2).strip()
            }
        
        # Extraction des compétences de la variante (avec gestion des choix)
        skills_match = re.search(r'\*\*Compétences\*\*\s*:\s*(.+?)\.', variant_content)
        if skills_match:
            skills_text = skills_match.group(1)
            skill_parts = [part.strip() for part in skills_text.split(',')]
            variant_skills = []
            variant_skill_choices = []
            
            for part in skill_parts:
                if ' ou ' in part:
                    # Compétence avec choix
                    choice_options = [opt.strip() for opt in part.split(' ou ')]
                    variant_skill_choices.append({
                        'description': part,
                        'options': choice_options
                    })
                else:
                    # Compétence fixe
                    variant_skills.append(part)
            
            variant_data['skills'] = variant_skills
            variant_data['skill_choices'] = variant_skill_choices
        
        # Extraction des outils de la variante
        tools_match = re.search(r'\*\*Outils maîtrisés\*\*\s*:\s*(.+?)\.', variant_content)
        if tools_match:
            variant_data['tools'] = [tool.strip() for tool in tools_match.group(1).split(',')]
        
        # Extraction des langues de la variante
        languages_match = re.search(r'\*\*Langues maîtrisées\*\*\s*:\s*(.+?)\.', variant_content)
        if languages_match:
            variant_data['languages'] = [lang.strip() for lang in languages_match.group(1).split(',')]
        
        # Extraction de l'équipement de la variante
        equipment_match = re.search(r'\*\*Équipement\*\*\s*:\s*(.+?)\.', variant_content)
        if equipment_match:
            variant_data['equipment'] = [item.strip() for item in equipment_match.group(1).split(',')]
        
        variants[variant_name.lower().replace(' ', '-')] = variant_data
    
    return variants

def extract_main_ability(content):
    """Extrait l'aptitude principale de l'historique"""
    try:
        # Pattern robuste pour capturer une aptitude principale
        pattern = r'## Aptitude : (.+?)\n([\s\S]*?)(?=\n## |\n### |\n$)'
        match = re.search(pattern, content)
        
        if match:
            ability_name = match.group(1).strip()
            ability_description = match.group(2).strip()
            return {
                'name': ability_name,
                'description': ability_description
            }
            
        return None
    except Exception:
        return None

def extract_choice_sections(content):
    """Extrait les sections de choix interactives avec tables D6/D8"""
    choice_sections = []
    try:
        # Pattern pour les sections avec des tables de choix
        pattern = r'## (.+?)\n(.*?)(?=## |\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        choice_section_names = [
            'Unité',
            'Spécialité', 
            'Milieu naturel de prédilection',
            'Domaine d\'études',
            'Origine sociale de l\'employeur'
        ]
        
        for section_title, section_content in matches:
            if any(choice_name in section_title.strip() for choice_name in choice_section_names):
                # Extraire la description et la table de choix
                description_text = ""
                choice_options = []
                
                # Séparer la description du texte avant la table
                lines = section_content.split('\n')
                table_started = False
                
                for line in lines:
                    if '| D' in line and '|' in line:
                        table_started = True
                        continue
                    elif '|:-' in line or '|-' in line:
                        continue
                    elif table_started and '|' in line and line.strip():
                        # Ligne de table avec choix
                        parts = [part.strip() for part in line.split('|')]
                        if len(parts) >= 3 and parts[1].strip().startswith('**') and parts[1].strip().endswith('**'):
                            roll_num = parts[1].strip().replace('**', '')
                            choice_text = parts[2].strip()
                            choice_options.append({
                                'roll': roll_num,
                                'text': choice_text
                            })
                    elif not table_started:
                        if line.strip():
                            description_text += line + "\n"
                
                if choice_options:
                    choice_sections.append({
                        'title': section_title.strip(),
                        'description': description_text.strip(),
                        'options': choice_options
                    })
                    
    except Exception as e:
        print(f"Erreur extraction sections de choix: {e}")
    
    return choice_sections

def extract_special_sections(content):
    """Extrait les sections spéciales comme 'Milieu naturel de prédilection'"""
    sections = []
    try:
        # Pattern pour les sections avec des tables (comme milieu naturel)
        pattern = r'## (.+?)\n(.*?)(?=### Aptitude|## Personnalités|## Variante|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for section_title, section_content in matches:
            # Ignorer toutes les sections standards pour éviter les parasites
            ignored_sections = [
                'Personnalités suggérées', 
                'Variante',
                'Statut social',
                'Milieu d\'origine',
                'Aptitude',
                'Unité',
                'Spécialité',
                'Milieu naturel de prédilection',
                'Domaine d\'études',
                'Origine sociale de l\'employeur'
            ]
            
            if any(ignored in section_title.strip() for ignored in ignored_sections):
                continue
            
            # Extraire les tables de cette section si elles existent
            tables = extract_section_tables(section_content)
            
            sections.append({
                'title': section_title.strip(),
                'content': section_content.strip(),
                'tables': tables
            })
    except Exception:
        pass
    
    return sections

def extract_section_tables(content):
    """Extrait les tables d'une section"""
    tables = []
    try:
        # Pattern pour les tables avec D et description
        pattern = r'\|\s*D\d+\s*\|\s*([^|]+)\s*\|(.*?)(?=\n\n|\n\||\n#|$)'
        table_match = re.search(pattern, content, re.DOTALL)
        
        if table_match:
            table_content = table_match.group(0)
            rows = []
            
            for line in table_content.split('\n'):
                if line.strip() and '|' in line:
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 3 and parts[1].strip().isdigit():
                        rows.append({
                            'roll': parts[1].strip(),
                            'text': parts[2].strip()
                        })
            
            if rows:
                tables.append({
                    'title': table_match.group(1).strip(),
                    'rows': rows
                })
    except Exception:
        pass
    
    return tables

@app.route('/api/character-spells-data', methods=['POST'])
@login_required
def get_character_spells_data():
    """Récupérer les sorts et compétences disponibles pour une classe et race données"""
    try:
        data = request.get_json()
        character_class = data.get('class', data.get('character_class', '')).lower()
        character_race = data.get('race', '').lower()
        character_level = int(data.get('level', 1))
        
        # Extraire les données avec regex
        spells_data = extract_available_spells(character_class, character_level)
        abilities = extract_class_abilities(character_class)
        racial_traits = extract_relevant_racial_traits(character_race)
        
        return jsonify({
            'spells': spells_data['spells'],
            'spell_limitations': spells_data['limitations'],
            'incantation_rules': spells_data['incantation_rules'],
            'abilities': abilities,
            'racial_traits': racial_traits,
            'success': True
        })
        
    except Exception as e:
        print(f"Erreur dans get_character_spells_data: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

def extract_available_spells(character_class, level=1):
    """Extraire les sorts disponibles pour une classe donnée en utilisant regex"""
    spells = []
    grimoire_path = 'data/docs/grimoire'
    
    if not os.path.exists(grimoire_path):
        return spells
    
    # Mapper les noms de classes
    class_mapping = {
        'ensorceleur': 'Ensorceleur/Sorcelame',
        'magicien': 'Magicien',
        'clerc': 'Clerc',
        'barde': 'Barde',
        'druide': 'Druide',
        'paladin': 'Paladin',
        'rodeur': 'Rôdeur',
        'sorcier': 'Ensorceleur/Sorcelame'  # Mapping temporaire
    }
    
    class_name = class_mapping.get(character_class, character_class.capitalize())
    
    # Extraire les limitations de sorts pour cette classe
    spell_limitations = extract_spell_limitations(character_class, level)
    
    # Parcourir tous les dossiers de sorts
    for spell_dir in os.listdir(grimoire_path):
        spell_path = os.path.join(grimoire_path, spell_dir, 'README.md')
        
        if os.path.exists(spell_path):
            try:
                with open(spell_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraire les métadonnées YAML du front matter
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    # Extraire le titre
                    title_match = re.search(r'title:\s*["\']?(.*?)["\']?$', yaml_content, re.MULTILINE)
                    title = title_match.group(1) if title_match else spell_dir.replace('-', ' ').title()
                    
                    # Extraire les classes compatibles
                    classes_section = re.search(r'classes:\s*\n((?:\s*-\s*.*\n?)*)', yaml_content, re.MULTILINE)
                    if classes_section:
                        classes_text = classes_section.group(1)
                        # Vérifier si la classe est dans la liste
                        if class_name in classes_text or character_class.capitalize() in classes_text:
                            # Extraire les autres métadonnées
                            level_match = re.search(r'level:\s*(\d+)', yaml_content)
                            level = int(level_match.group(1)) if level_match else 0
                            
                            school_match = re.search(r'school:\s*["\']?(.*?)["\']?$', yaml_content, re.MULTILINE)
                            school = school_match.group(1) if school_match else 'Inconnue'
                            
                            range_match = re.search(r'range:\s*["\']?(.*?)["\']?$', yaml_content, re.MULTILINE)
                            spell_range = range_match.group(1) if range_match else 'N/A'
                            
                            duration_match = re.search(r'duration:\s*["\']?(.*?)["\']?$', yaml_content, re.MULTILINE)
                            duration = duration_match.group(1) if duration_match else 'N/A'
                            
                            casting_time_match = re.search(r'casting_time:\s*["\']?(.*?)["\']?$', yaml_content, re.MULTILINE)
                            casting_time = casting_time_match.group(1) if casting_time_match else 'N/A'
                            
                            # Extraire la description (après le front matter)
                            description_match = re.search(r'---\s*\n(.*)', content, re.DOTALL)
                            if description_match:
                                desc_content = description_match.group(1).strip()
                                
                                # Nettoyer le contenu et extraire la description
                                # Supprimer les titres, liens, et autres éléments markdown
                                clean_content = re.sub(r'^#+\s+.*$', '', desc_content, flags=re.MULTILINE)  # Supprimer les titres
                                clean_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_content)  # Convertir les liens en texte
                                clean_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_content)  # Supprimer le gras
                                clean_content = re.sub(r'\*([^*]+)\*', r'\1', clean_content)  # Supprimer l'italique
                                clean_content = re.sub(r'`([^`]+)`', r'\1', clean_content)  # Supprimer le code inline
                                
                                # Prendre les premiers paragraphes significatifs
                                paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
                                description_parts = []
                                
                                for paragraph in paragraphs[:3]:  # Prendre jusqu'à 3 paragraphes
                                    if paragraph and len(paragraph) > 10:  # Ignorer les paragraphes trop courts
                                        description_parts.append(paragraph)
                                        if len(' '.join(description_parts)) > 300:  # Limiter la longueur
                                            break
                                
                                description = ' '.join(description_parts)[:400] if description_parts else 'Aucune description'
                                
                                # Si la description est trop courte, essayer de prendre plus de contenu
                                if len(description) < 50:
                                    lines = [line.strip() for line in clean_content.split('\n') if line.strip()]
                                    description = ' '.join(lines[:5])[:400] if lines else 'Aucune description'
                                    
                            else:
                                description = 'Aucune description'
                            
                            # Vérifier si ce sort est accessible au niveau 1
                            if is_spell_accessible(level, spell_limitations):
                                spells.append({
                                    'title': title,
                                    'level': level,
                                    'school': school,
                                    'range': spell_range,
                                    'duration': duration,
                                    'casting_time': casting_time,
                                    'description': description,
                                    'accessible': True
                                })
                            
            except Exception as e:
                print(f"Erreur lors de l'extraction du sort {spell_dir}: {e}")
    
    # Trier par niveau puis par nom
    spells.sort(key=lambda x: (x['level'], x['title']))
    
    # Ajouter les informations de limitation
    result = {
        'spells': spells,
        'limitations': spell_limitations,
        'incantation_rules': extract_incantation_rules(character_class)
    }
    
    return result

def extract_class_abilities(character_class):
    """Extraire les aptitudes de combat par niveau pour une classe donnée"""
    abilities = []
    class_path = f'data/docs/classes/{character_class}/README.md'
    
    if not os.path.exists(class_path):
        return abilities
    
    try:
        with open(class_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher le tableau d'évolution - pattern plus flexible
        table_patterns = [
            r'§§§\s*\.table-container\s*\n(\|Niveau\|.*?\n(?:\|.*?\n)*?)§§§',  # Pattern avec container
            r'(\|Niveau\|.*?\n(?:\|.*?\n)*)',  # Pattern standard
        ]
        
        table_content = None
        for pattern in table_patterns:
            table_match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if table_match:
                table_content = table_match.group(1)
                break
        
        if table_content:
            lines = table_content.split('\n')
            
            # Analyser l'en-tête pour trouver la colonne "Aptitudes"
            header_lines = []
            data_lines = []
            separator_found = False
            
            for line in lines:
                if line.startswith('|:-'):
                    separator_found = True
                    continue
                elif line.startswith('|') and line.strip():
                    if separator_found:
                        data_lines.append(line)
                    else:
                        header_lines.append(line)
            
            # Reconstruire l'en-tête complet
            aptitudes_index = 2  # Valeur par défaut
            if header_lines:
                combined_header = []
                if len(header_lines) >= 2:
                    # Première ligne d'en-tête
                    first_header = [cell.strip() for cell in header_lines[0].split('|')[1:-1]]
                    # Deuxième ligne d'en-tête (avec ^^)
                    second_header = [cell.strip() for cell in header_lines[1].split('|')[1:-1]]
                    
                    # Fusionner les en-têtes - utiliser la deuxième ligne sauf pour les ^^
                    for i in range(max(len(first_header), len(second_header))):
                        if i < len(second_header) and second_header[i] != '^^':
                            combined_header.append(second_header[i])
                        elif i < len(first_header):
                            combined_header.append(first_header[i])
                        else:
                            combined_header.append('')
                else:
                    combined_header = [cell.strip() for cell in header_lines[0].split('|')[1:-1]]
                
                # Chercher la colonne "Aptitudes"
                for i, cell in enumerate(combined_header):
                    if 'Aptitudes' in cell or 'aptitudes' in cell.lower():
                        aptitudes_index = i
                        break
            
            # Extraire chaque ligne du tableau
            for line in data_lines:
                    
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Ignorer les | du début et de la fin
                    
                    if len(cells) > aptitudes_index and cells[0]:
                        # Extraire le niveau - gérer **1** ou 1
                        level_text = cells[0].replace('*', '').strip()
                        if level_text.isdigit():
                            level = int(level_text)
                            aptitudes_cell = cells[aptitudes_index] if len(cells) > aptitudes_index else ''
                            
                            # Extraire les aptitudes de cette cellule
                            if aptitudes_cell and aptitudes_cell != '-' and aptitudes_cell.strip():
                                level_abilities = []
                                
                                # Rechercher les liens vers les aptitudes [Nom](#ancre)
                                ability_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', aptitudes_cell)
                                for ability_name, anchor in ability_links:
                                    # Nettoyer le nom de l'aptitude
                                    clean_name = re.sub(r'\s*\([^)]*\)', '', ability_name).strip()
                                    # Rechercher la description de cette aptitude dans le contenu
                                    description = extract_ability_description(content, anchor, clean_name)
                                    level_abilities.append({
                                        'name': clean_name,
                                        'description': description
                                    })
                                
                                # Si pas de liens, traiter le texte brut
                                if not ability_links and aptitudes_cell.strip():
                                    # Séparer par des virgules
                                    raw_abilities = [apt.strip() for apt in aptitudes_cell.split(',')]
                                    for raw_ability in raw_abilities:
                                        if raw_ability and raw_ability != '-':
                                            # Nettoyer le nom
                                            clean_name = re.sub(r'\s*\([^)]*\)', '', raw_ability).strip()
                                            level_abilities.append({
                                                'name': clean_name,
                                                'description': 'Voir le manuel de règles pour plus de détails.'
                                            })
                                
                                if level_abilities:
                                    abilities.append({
                                        'level': level,
                                        'abilities': level_abilities
                                    })
        
        # Trier par niveau
        abilities.sort(key=lambda x: x['level'])
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des aptitudes de {character_class}: {e}")
    
    return abilities[:10]  # Limiter aux 10 premiers niveaux

def extract_ability_description(content, anchor, ability_name):
    """Extraire la description d'une aptitude à partir de son ancre"""
    # Rechercher la section correspondant à l'ancre
    anchor_pattern = rf'###?\s*{re.escape(ability_name)}|###?\s*.*?{re.escape(anchor.replace("-", "[ -]"))}'
    section_match = re.search(anchor_pattern, content, re.IGNORECASE)
    
    if section_match:
        # Extraire le texte après le titre jusqu'à la prochaine section
        start_pos = section_match.end()
        next_section = re.search(r'\n###?\s+', content[start_pos:])
        
        if next_section:
            description_text = content[start_pos:start_pos + next_section.start()]
        else:
            description_text = content[start_pos:start_pos + 500]  # Limiter à 500 caractères
        
        # Nettoyer le texte
        description_text = re.sub(r'\n+', ' ', description_text.strip())
        description_text = re.sub(r'\s+', ' ', description_text)
        
        return description_text[:300] if description_text else 'Voir le manuel de règles pour plus de détails.'
    
    return 'Voir le manuel de règles pour plus de détails.'

def extract_relevant_racial_traits(character_race):
    """Extraire les traits raciaux pertinents pour la magie et le combat"""
    traits = []
    race_path = f'data/docs/races/{character_race}/README.md'
    
    if not os.path.exists(race_path):
        return traits
    
    try:
        with open(race_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher les sections de traits
        trait_patterns = [
            r'\*\*([^*]+)\*\*\.\s*([^*\n]+(?:\n(?!\*\*)[^*\n]*)*)',  # **Nom**. Description
            r'###\s*([^\n]+)\n([^#]+?)(?=###|\Z)',  # ### Titre \n Description
        ]
        
        combat_keywords = [
            'sort', 'magie', 'incantation', 'combat', 'attaque', 'dégâts', 'résistance',
            'armure', 'arme', 'compétence', 'avantage', 'bonus', 'modificateur',
            'tour de magie', 'caractéristique'
        ]
        
        for pattern in trait_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for name, description in matches:
                name = name.strip()
                description = re.sub(r'\s+', ' ', description.strip())
                
                # Vérifier si le trait est pertinent pour la magie/combat
                is_relevant = any(keyword in description.lower() or keyword in name.lower() 
                                for keyword in combat_keywords)
                
                if is_relevant and len(description) > 20:  # Filtrer les descriptions trop courtes
                    # Analyser l'impact
                    impact = analyze_trait_impact(description)
                    
                    traits.append({
                        'name': name,
                        'description': description[:400],  # Limiter la longueur
                        'impact': impact
                    })
        
        # Supprimer les doublons
        seen_names = set()
        unique_traits = []
        for trait in traits:
            if trait['name'] not in seen_names:
                seen_names.add(trait['name'])
                unique_traits.append(trait)
        
        return unique_traits[:8]  # Limiter à 8 traits
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des traits raciaux de {character_race}: {e}")
    
    return traits

def analyze_trait_impact(description):
    """Analyser l'impact d'un trait racial sur la magie/combat"""
    description_lower = description.lower()
    
    impacts = []
    
    if 'sort' in description_lower or 'magie' in description_lower or 'incantation' in description_lower:
        impacts.append('Accès à des sorts supplémentaires')
    
    if 'résistance' in description_lower or 'résistant' in description_lower:
        impacts.append('Résistance aux dégâts')
    
    if 'avantage' in description_lower:
        impacts.append('Avantage sur certains jets')
    
    if 'compétence' in description_lower or 'maîtrise' in description_lower:
        impacts.append('Compétences supplémentaires')
    
    if 'bonus' in description_lower or '+' in description:
        impacts.append('Bonus aux caractéristiques ou jets')
    
    if 'arme' in description_lower or 'armure' in description_lower:
        impacts.append('Maîtrises d\'équipement')
    
    return ' | '.join(impacts) if impacts else 'Avantage situationnel'

def extract_spell_limitations(character_class, level=1):
    """Extraire les limitations de sorts depuis le tableau d'évolution de la classe"""
    limitations = {
        'cantrips_known': 0,
        'spells_known': 0,
        'spell_slots': {},
        'max_spell_level': 0,
        'prepares_spells': False,  # Indique si la classe prépare ses sorts
        'spells_preparable': 0     # Nombre de sorts préparables
    }
    
    class_path = f'data/docs/classes/{character_class}/README.md'
    
    if not os.path.exists(class_path):
        return limitations
    
    try:
        with open(class_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher le tableau d'évolution pour extraire les limitations
        table_patterns = [
            r'§§§\s*\.table-container\s*\n(\|Niveau\|.*?\n(?:\|.*?\n)*?)§§§',  # Pattern avec container
            r'(\|Niveau\|.*?\n(?:\|.*?\n)*)',  # Pattern standard
        ]
        
        table_content = None
        for pattern in table_patterns:
            table_match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if table_match:
                table_content = table_match.group(1)
                break
        
        if table_content:
            lines = table_content.split('\n')
            
            # Analyser l'en-tête pour comprendre la structure
            header_lines = []
            data_lines = []
            separator_found = False
            
            for line in lines:
                if line.startswith('|:-'):
                    separator_found = True
                    continue
                elif line.startswith('|') and line.strip():
                    if separator_found:
                        data_lines.append(line)
                    else:
                        header_lines.append(line)
            
            # Reconstruire l'en-tête complet pour les tableaux avec colonnes fusionnées
            if header_lines:
                # Combiner les lignes d'en-tête
                combined_header = []
                if len(header_lines) >= 2:
                    # Première ligne d'en-tête
                    first_header = [cell.strip() for cell in header_lines[0].split('|')[1:-1]]
                    # Deuxième ligne d'en-tête (avec ^^)
                    second_header = [cell.strip() for cell in header_lines[1].split('|')[1:-1]]
                    
                    # Fusionner les en-têtes - utiliser la deuxième ligne sauf pour les ^^
                    for i in range(max(len(first_header), len(second_header))):
                        if i < len(second_header) and second_header[i] != '^^':
                            combined_header.append(second_header[i])
                        elif i < len(first_header):
                            combined_header.append(first_header[i])
                        else:
                            combined_header.append('')
                else:
                    combined_header = [cell.strip() for cell in header_lines[0].split('|')[1:-1]]
                
                # Trouver les indices des colonnes importantes
                cantrips_index = -1
                spells_index = -1
                slots_start_index = -1
                
                for i, header in enumerate(combined_header):
                    header_lower = header.lower()
                    if 'tour' in header_lower and 'magie' in header_lower:
                        cantrips_index = i
                    elif 'sorts' in header_lower and 'connu' in header_lower:
                        spells_index = i
                    elif ('1' in header and 'sup' in header) or header.strip() == '1':
                        if slots_start_index == -1:
                            slots_start_index = i
            
            # Rechercher la ligne du niveau demandé
            for line in data_lines:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                
                if len(cells) > 0 and cells[0]:
                    level_text = cells[0].replace('*', '').strip()
                    if level_text == str(level):
                        try:
                            # Extraire tours de magie connus
                            if cantrips_index >= 0 and cantrips_index < len(cells):
                                if cells[cantrips_index].isdigit():
                                    limitations['cantrips_known'] = int(cells[cantrips_index])
                            
                            # Extraire sorts connus (pour les classes comme barde/ensorceleur)
                            if spells_index >= 0 and spells_index < len(cells):
                                if cells[spells_index].isdigit():
                                    limitations['spells_known'] = int(cells[spells_index])
                            
                            # Extraire les emplacements de sorts
                            if slots_start_index >= 0:
                                spell_level = 1
                                for i in range(slots_start_index, len(cells)):
                                    cell_value = cells[i]
                                    if cell_value and cell_value != '-':
                                        try:
                                            slots = int(cell_value)
                                            if slots > 0:
                                                limitations['spell_slots'][spell_level] = slots
                                                limitations['max_spell_level'] = spell_level
                                        except ValueError:
                                            pass
                                    spell_level += 1
                            
                            # Si pas d'emplacements trouvés, chercher seulement si la classe est magique
                            if not limitations['spell_slots'] and character_class.lower() in ['barde', 'clerc', 'druide', 'ensorceleur', 'magicien', 'paladin', 'rodeur', 'sorcier']:
                                spell_level = 1
                                for i, cell in enumerate(cells[3:], 3):  # Commencer après niveau, bonus, aptitudes
                                    if cell and cell != '-':
                                        try:
                                            slots = int(cell)
                                            if slots > 0:
                                                limitations['spell_slots'][spell_level] = slots
                                                limitations['max_spell_level'] = spell_level
                                            spell_level += 1
                                        except ValueError:
                                            continue
                                        
                        except (ValueError, IndexError) as e:
                            print(f"Erreur lors de l'extraction des limitations pour {character_class}: {e}")
                        break
        
        # Déterminer si la classe prépare ses sorts et calculer le nombre préparable
        if character_class.lower() in ['clerc', 'druide', 'paladin', 'rodeur']:
            limitations['prepares_spells'] = True
            # Pour ces classes, le nombre de sorts préparables = modificateur de caractéristique + niveau
            # On estime un modificateur de +3 (caractéristique 16)
            limitations['spells_preparable'] = 3 + level  # Modificateur + niveau
        elif character_class.lower() == 'magicien':
            limitations['prepares_spells'] = True
            # Le magicien prépare un nombre de sorts = modificateur d'Intelligence + niveau de magicien
            limitations['spells_preparable'] = 3 + level  # Modificateur + niveau
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des limitations de {character_class}: {e}")
    
    return limitations

def is_spell_accessible(spell_level, limitations):
    """Vérifier si un sort est accessible selon les limitations de classe"""
    if spell_level == 0:  # Tours de magie
        return limitations['cantrips_known'] > 0
    else:
        return spell_level <= limitations['max_spell_level']

def extract_available_subclasses(character_class):
    """Extraire les sous-classes disponibles pour une classe donnée"""
    subclasses = []
    class_path = f'data/docs/classes/{character_class}/README.md'
    
    if not os.path.exists(class_path):
        return subclasses
    
    try:
        with open(class_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns améliorés pour différents types de sous-classes
        subclass_patterns = {
            'barbare': r'### (Voie [^#\n]+)',
            'barde': r'### (Collège [^#\n]+)',
            'clerc': r'### (Domaine [^#\n]+)',
            'druide': r'### (Cercle [^#\n]+)',
            'ensorceleur': r'### (Origine [^#\n]+|Lignée [^#\n]+)',
            'guerrier': r'### (Archétype [^#\n]+)',
            'magicien': r'### (École [^#\n]+|Tradition [^#\n]+)',
            'moine': r'### (Voie [^#\n]+)',
            'paladin': r'### (Serment [^#\n]+)',
            'rodeur': r'### (Archétype [^#\n]+)',
            'roublard': r'### (Archétype [^#\n]+)',
            'sorcier': r'### (Pacte [^#\n]+|Protecteur [^#\n]+)',
        }
        
        # Utiliser le pattern spécifique à la classe
        if character_class in subclass_patterns:
            pattern = subclass_patterns[character_class]
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for match in matches:
                subclass_name = match.strip()
                
                # Extraire une description courte
                description_pattern = rf'### {re.escape(subclass_name)}\s*\n(.*?)(?=\n###|\n##|\Z)'
                desc_match = re.search(description_pattern, content, re.DOTALL)
                
                description = ""
                if desc_match:
                    desc_content = desc_match.group(1).strip()
                    
                    # Nettoyer le contenu : supprimer les tableaux, liens, etc.
                    desc_content = re.sub(r'\|[^|\n]*\|', '', desc_content)  # Supprimer les tableaux
                    desc_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc_content)  # Convertir les liens
                    desc_content = re.sub(r'#{1,6}\s*', '', desc_content)  # Supprimer les titres markdown
                    desc_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc_content)  # Supprimer le gras
                    desc_content = re.sub(r'\*([^*]+)\*', r'\1', desc_content)  # Supprimer l'italique
                    desc_content = re.sub(r'^\s*[-*+]\s+', '', desc_content, flags=re.MULTILINE)  # Supprimer les listes
                    desc_content = re.sub(r'§§§.*?§§§', '', desc_content, flags=re.DOTALL)  # Supprimer les blocs source
                    desc_content = re.sub(r'\n+', ' ', desc_content)  # Remplacer les sauts de ligne
                    desc_content = re.sub(r'\s+', ' ', desc_content)  # Normaliser les espaces
                    
                    # Prendre le premier paragraphe significatif
                    paragraphs = [p.strip() for p in desc_content.split('.') if p.strip() and len(p.strip()) > 20]
                    if paragraphs:
                        first_sentence = paragraphs[0] + '.'
                        description = first_sentence[:150] + "..." if len(first_sentence) > 150 else first_sentence
                
                # Extraire les aptitudes de la sous-classe
                abilities = extract_subclass_abilities(content, subclass_name)
                
                subclasses.append({
                    'name': subclass_name,
                    'description': description,
                    'class': character_class,
                    'abilities': abilities
                })
        
        # Pattern générique de fallback avec recherche plus large
        if not subclasses:
            # Essayer des patterns plus génériques
            generic_patterns = [
                r'### (Voie [^#\n]+)',
                r'### (Tradition [^#\n]+)',
                r'### (Archétype [^#\n]+)',
                r'### (Collège [^#\n]+)',
                r'### (Domaine [^#\n]+)',
                r'### (Cercle [^#\n]+)',
                r'### (Serment [^#\n]+)',
                r'### (École [^#\n]+)',
                r'### (Origine [^#\n]+)',
                r'### (Lignée [^#\n]+)',
                r'### (Pacte [^#\n]+)',
                r'### (Protecteur [^#\n]+)',
            ]
            
            for pattern in generic_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if not any(sub['name'] == match.strip() for sub in subclasses):
                        abilities = extract_subclass_abilities(content, match.strip())
                        subclasses.append({
                            'name': match.strip(),
                            'description': "Spécialisation de cette classe avec des capacités uniques.",
                            'class': character_class,
                            'abilities': abilities
                        })
    
    except Exception as e:
        print(f"Erreur lors de l'extraction des sous-classes de {character_class}: {e}")
    
    return subclasses

def extract_subclass_abilities(content, subclass_name):
    """Extraire les aptitudes d'une sous-classe spécifique"""
    abilities = []
    
    try:
        # Chercher la section de la sous-classe
        subclass_pattern = rf'### {re.escape(subclass_name)}\s*\n(.*?)(?=\n###|\n##|\Z)'
        subclass_match = re.search(subclass_pattern, content, re.DOTALL)
        
        if not subclass_match:
            return abilities
        
        subclass_content = subclass_match.group(1)
        
        # Chercher les aptitudes (titres de niveau 4)
        ability_pattern = r'#### ([^#\n]+)\s*\n(.*?)(?=\n####|\n###|\n##|\Z)'
        ability_matches = re.findall(ability_pattern, subclass_content, re.DOTALL)
        
        for ability_name, ability_desc in ability_matches:
            ability_name = ability_name.strip()
            
            # Nettoyer la description
            ability_desc = ability_desc.strip()
            ability_desc = re.sub(r'\|[^|\n]*\|', '', ability_desc)  # Supprimer les tableaux
            ability_desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', ability_desc)  # Convertir les liens
            ability_desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', ability_desc)  # Supprimer le gras
            ability_desc = re.sub(r'\*([^*]+)\*', r'\1', ability_desc)  # Supprimer l'italique
            ability_desc = re.sub(r'§§§.*?§§§', '', ability_desc, flags=re.DOTALL)  # Supprimer les blocs source
            ability_desc = re.sub(r'\n+', ' ', ability_desc)  # Remplacer les sauts de ligne
            ability_desc = re.sub(r'\s+', ' ', ability_desc)  # Normaliser les espaces
            
            # Limiter la longueur
            if len(ability_desc) > 300:
                ability_desc = ability_desc[:300] + "..."
            
            # Extraire le niveau si mentionné
            level_match = re.search(r'niveau (\d+)', ability_desc, re.IGNORECASE)
            level = int(level_match.group(1)) if level_match else None
            
            abilities.append({
                'name': ability_name,
                'description': ability_desc,
                'level': level
            })
    
    except Exception as e:
        print(f"Erreur lors de l'extraction des aptitudes de {subclass_name}: {e}")
    
    return abilities

def get_subclass_unlock_level(character_class):
    """Déterminer à quel niveau se débloquent les sous-classes"""
    unlock_levels = {
        'clerc': 1,      # Domaine divin dès le niveau 1
        'druide': 2,     # Cercle druidique au niveau 2
        'magicien': 2,   # Tradition arcanique au niveau 2
        'barde': 3,      # Collège bardique au niveau 3
        'guerrier': 3,   # Archétype martial au niveau 3
        'moine': 3,      # Tradition monacale au niveau 3
        'paladin': 3,    # Serment sacré au niveau 3
        'rodeur': 3,     # Archétype de rôdeur au niveau 3
        'roublard': 3,   # Archétype de roublard au niveau 3
        'sorcier': 1,    # Protecteur dès le niveau 1
    }
    
    return unlock_levels.get(character_class.lower(), None)

def get_multiclass_options():
    """Retourner les options de multiclassing disponibles"""
    return {
        'classes': ['barbare', 'barde', 'clerc', 'druide', 'ensorceleur', 'guerrier', 'magicien', 'moine', 'paladin', 'rodeur', 'roublard', 'sorcier'],
        'prerequisites': {
            'Force': ['guerrier', 'paladin', 'rodeur'],
            'Dextérité': ['moine', 'rodeur', 'roublard'],
            'Intelligence': ['guerrier', 'magicien', 'roublard'],
            'Sagesse': ['clerc', 'druide', 'moine', 'rodeur'],
            'Charisme': ['barde', 'paladin', 'sorcier']
        },
        'spell_progression': {
            'full_casters': ['barde', 'clerc', 'druide', 'ensorceleur', 'magicien', 'sorcier'],
            'half_casters': ['paladin', 'rodeur'],
            'non_casters': ['barbare', 'guerrier', 'moine', 'roublard']
        }
    }

def extract_incantation_rules(character_class):
    """Extraire les règles d'incantation depuis le fichier de classe"""
    rules = {
        'casting_ability': 'Charisme',
        'ritual_casting': False,
        'spellcasting_focus': '',
        'description': ''
    }
    
    class_path = f'data/docs/classes/{character_class}/README.md'
    
    if not os.path.exists(class_path):
        return rules
    
    try:
        with open(class_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire la caractéristique d'incantation
        ability_match = re.search(r'caractéristique d\'incantation.*?est (?:le |la )?(\w+)', content, re.IGNORECASE)
        if ability_match:
            rules['casting_ability'] = ability_match.group(1).capitalize()
        
        # Vérifier l'incantation rituelle
        if 'rituel' in content.lower() or 'ritual' in content.lower():
            rules['ritual_casting'] = True
        
        # Extraire le focaliseur d'incantation
        focus_match = re.search(r'focaliseur d\'incantation.*?([^.]+)', content, re.IGNORECASE)
        if focus_match:
            rules['spellcasting_focus'] = focus_match.group(1).strip()
        
        # Extraire la description des incantations
        incantation_match = re.search(r'### Incantations?\s*\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if incantation_match:
            description = incantation_match.group(1).strip()
            # Nettoyer la description
            description = re.sub(r'\n+', ' ', description)
            description = re.sub(r'\s+', ' ', description)
            rules['description'] = description[:500]  # Limiter la longueur
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des règles d'incantation de {character_class}: {e}")
    
    return rules

@app.route('/api/subclasses/<character_class>')
def get_subclasses_for_class(character_class):
    """API pour récupérer les sous-classes disponibles"""
    subclasses = extract_available_subclasses(character_class)
    unlock_level = get_subclass_unlock_level(character_class)
    
    return jsonify({
        'subclasses': subclasses,
        'unlock_level': unlock_level,
        'has_subclasses': len(subclasses) > 0
    })

@app.route('/api/multiclass-options')
def get_multiclass_options_api():
    """API pour récupérer les options de multiclassing"""
    return jsonify(get_multiclass_options())

@app.route('/api/character-options')
def get_character_options():
    """API pour déterminer les options disponibles selon la classe et le niveau"""
    character_class = request.args.get('class', '')
    level = request.args.get('level', 1, type=int)
    
    options = {
        'can_multiclass': level >= 2,
        'can_choose_subclass': False,
        'subclass_unlock_level': None,
        'available_subclasses': []
    }
    
    if character_class:
        unlock_level = get_subclass_unlock_level(character_class)
        if unlock_level and level >= unlock_level:
            options['can_choose_subclass'] = True
            options['subclass_unlock_level'] = unlock_level
            options['available_subclasses'] = extract_available_subclasses(character_class)
    
    return jsonify(options)

@app.route('/api/equipment')
def get_equipment():
    """API pour récupérer tout l'équipement"""
    try:
        import json
        with open('equipment_data.json', 'r', encoding='utf-8') as f:
            equipment_data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': equipment_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/equipment/proficiencies/<character_class>')
def get_class_proficiencies(character_class):
    """API pour récupérer les maîtrises d'une classe"""
    try:
        import json
        with open('equipment_data.json', 'r', encoding='utf-8') as f:
            equipment_data = json.load(f)
        
        proficiencies = equipment_data.get('proficiencies', {}).get(character_class, {})
        
        return jsonify({
            'success': True,
            'proficiencies': proficiencies
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def check_proficiency(character_class, item_name, item_type):
    """Vérifier si un personnage maîtrise un équipement"""
    try:
        import json
        with open('equipment_data.json', 'r', encoding='utf-8') as f:
            equipment_data = json.load(f)
        
        proficiencies = equipment_data.get('proficiencies', {}).get(character_class, {})
        
        if item_type == 'armor':
            armor_prof = proficiencies.get('armors', '').lower()
            item_lower = item_name.lower()
            
            # Vérifications spécifiques
            if 'toutes les armures' in armor_prof:
                return True
            elif 'armures légères' in armor_prof and any(x in item_lower for x in ['matelassée', 'cuir']):
                return True
            elif 'armures intermédiaires' in armor_prof and any(x in item_lower for x in ['peau', 'chemise', 'écailles', 'cuirasse', 'demi-plate']):
                return True
            elif 'armures lourdes' in armor_prof and any(x in item_lower for x in ['broigne', 'cotte', 'clibanion', 'harnois']):
                return True
            elif 'boucliers' in armor_prof and 'bouclier' in item_lower:
                return True
                
        elif item_type == 'weapon':
            weapon_prof = proficiencies.get('weapons', '').lower()
            item_lower = item_name.lower()
            
            # Vérifications spécifiques
            if 'armes de guerre' in weapon_prof or 'armes courantes' in weapon_prof:
                return True
            elif item_lower in weapon_prof:
                return True
        
        return False
        
    except Exception as e:
        print(f"Erreur lors de la vérification de maîtrise: {e}")
        return False

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000) 