from flask import jsonify, request
from flask_login import current_user, login_required
from flask_app import app
from flask_app.models.user import User

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400

        new_pseudo = data.get('pseudo')
        new_avatar = data.get('avatar')

        # Vérifier si le pseudo est déjà utilisé
        if new_pseudo and new_pseudo != current_user.pseudo:
            users = User.load_all()
            for email, user_data in users.items():
                if email != current_user.email and user_data.get('pseudo') == new_pseudo:
                    return jsonify({'error': 'Ce pseudo est déjà utilisé'}), 400

        # Mettre à jour le profil
        current_user.update_profile(new_pseudo=new_pseudo, new_avatar=new_avatar)

        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': {
                'email': current_user.email,
                'pseudo': current_user.pseudo,
                'avatar': current_user.avatar
            }
        }), 200

    except Exception as e:
        print(f"Erreur lors de la mise à jour du profil : {str(e)}")  # Log l'erreur
        return jsonify({'error': 'Une erreur est survenue lors de la mise à jour'}), 500 