import json
from flask_login import UserMixin
from pathlib import Path

class User(UserMixin):
    def __init__(self, email, password=None, is_dm=False, needs_tutorial=True, characters=None, pseudo=None):
        self.email = email
        self.password = password
        self.is_dm = is_dm
        self.needs_tutorial = needs_tutorial
        self.characters = characters or []
        self.pseudo = pseudo or email  # Par défaut, le pseudo est l'email
        self.avatar = None

    @property
    def id(self):
        return self.email

    def to_dict(self):
        return {
            "password": self.password,
            "is_dm": self.is_dm,
            "needs_tutorial": self.needs_tutorial,
            "characters": self.characters,
            "pseudo": self.pseudo,
            "avatar": self.avatar
        }

    @staticmethod
    def get_users_file():
        return Path("data/users.json")

    @classmethod
    def load_all(cls):
        try:
            with open(cls.get_users_file(), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @classmethod
    def save_all(cls, users_data):
        with open(cls.get_users_file(), "w") as f:
            json.dump(users_data, f, indent=4)

    @classmethod
    def get_by_email(cls, email):
        users = cls.load_all()
        if email not in users:
            return None
        
        user_data = users[email]
        user = cls(
            email=email,
            password=user_data.get("password"),
            is_dm=user_data.get("is_dm", False),
            needs_tutorial=user_data.get("needs_tutorial", True),
            characters=user_data.get("characters", []),
            pseudo=user_data.get("pseudo", email)
        )
        user.avatar = user_data.get("avatar")
        return user

    def save(self):
        users = self.load_all()
        users[self.email] = self.to_dict()
        self.save_all(users)

    def update_profile(self, new_pseudo=None, new_avatar=None):
        if new_pseudo:
            self.pseudo = new_pseudo
        if new_avatar is not None:  # Permettre de mettre une chaîne vide
            self.avatar = new_avatar
        self.save() 