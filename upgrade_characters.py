#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à niveau tous les personnages existants vers la nouvelle structure
"""
import json
import os
from datetime import datetime

def load_json(filename):
    """Charger un fichier JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(data, filename):
    """Sauvegarder un fichier JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_all_racial_traits():
    """Retourner tous les traits raciaux"""
    return {
        "nain": {
            "ability_bonuses": {"constitution": 2},
            "speed": 25,
            "languages": ["Commun", "Nain"],
            "traits": [
                {
                    "name": "Vision dans le noir",
                    "description": "Vous pouvez voir dans la pénombre à 18 mètres comme si c'était une lumière vive, et dans l'obscurité comme si c'était une pénombre."
                },
                {
                    "name": "Résistance naine", 
                    "description": "Vous avez l'avantage aux jets de sauvegarde contre le poison et vous avez la résistance aux dégâts de poison."
                },
                {
                    "name": "Formation aux armes naines",
                    "description": "Vous maîtrisez la hachette, la hache d'armes, le marteau léger et le marteau de guerre."
                },
                {
                    "name": "Maîtrise des outils",
                    "description": "Vous maîtrisez les outils d'artisan de votre choix parmi : outils de forgeron, matériel de brasseur ou outils de maçon."
                },
                {
                    "name": "Connaissance de la pierre",
                    "description": "Chaque fois que vous effectuez un test d'Intelligence (Histoire) lié à l'origine d'un travail de maçonnerie, vous êtes considéré comme maîtrisant la compétence Histoire et vous ajoutez le double de votre bonus de maîtrise au test."
                }
            ]
        },
        "humain": {
            "ability_bonuses": {"force": 1, "dexterite": 1, "constitution": 1, "intelligence": 1, "sagesse": 1, "charisme": 1},
            "speed": 30,
            "languages": ["Commun"],
            "traits": [
                {
                    "name": "Compétence supplémentaire",
                    "description": "Vous maîtrisez une compétence de votre choix."
                },
                {
                    "name": "Don supplémentaire", 
                    "description": "Vous obtenez un don de votre choix."
                }
            ]
        },
        "elfe": {
            "ability_bonuses": {"dexterite": 2},
            "speed": 30,
            "languages": ["Commun", "Elfique"],
            "traits": [
                {
                    "name": "Vision dans le noir",
                    "description": "Vous pouvez voir dans la pénombre à 18 mètres comme si c'était une lumière vive, et dans l'obscurité comme si c'était une pénombre."
                },
                {
                    "name": "Sens aiguisés",
                    "description": "Vous maîtrisez la compétence Perception."
                },
                {
                    "name": "Ascendance féérique",
                    "description": "Vous avez l'avantage aux jets de sauvegarde contre les charmes et la magie ne peut pas vous endormir."
                },
                {
                    "name": "Transe",
                    "description": "Les elfes n'ont pas besoin de dormir. Ils méditent profondément 4 heures par jour."
                }
            ]
        },
        "halfelin": {
            "ability_bonuses": {"dexterite": 2},
            "speed": 25,
            "languages": ["Commun", "Halfelin"],
            "traits": [
                {
                    "name": "Chanceux",
                    "description": "Quand vous obtenez un 1 naturel sur un d20 pour un jet d'attaque, un test de caractéristique ou un jet de sauvegarde, vous pouvez relancer le dé et devez utiliser le nouveau résultat."
                },
                {
                    "name": "Brave",
                    "description": "Vous avez l'avantage aux jets de sauvegarde contre la peur."
                },
                {
                    "name": "Agilité halfeline",
                    "description": "Vous pouvez vous déplacer à travers l'espace de toute créature d'une taille supérieure à la vôtre."
                }
            ]
        },
        "demi-elfe": {
            "ability_bonuses": {"charisme": 2},
            "speed": 30,
            "languages": ["Commun", "Elfique"],
            "traits": [
                {
                    "name": "Vision dans le noir",
                    "description": "Vous pouvez voir dans la pénombre à 18 mètres comme si c'était une lumière vive, et dans l'obscurité comme si c'était une pénombre."
                },
                {
                    "name": "Ascendance féérique",
                    "description": "Vous avez l'avantage aux jets de sauvegarde contre les charmes et la magie ne peut pas vous endormir."
                },
                {
                    "name": "Polyvalence de compétence",
                    "description": "Vous gagnez la maîtrise de deux compétences de votre choix."
                }
            ]
        },
        "demi-orc": {
            "ability_bonuses": {"force": 2, "constitution": 1},
            "speed": 30,
            "languages": ["Commun", "Orc"],
            "traits": [
                {
                    "name": "Vision dans le noir",
                    "description": "Vous pouvez voir dans la pénombre à 18 mètres comme si c'était une lumière vive, et dans l'obscurité comme si c'était une pénombre."
                },
                {
                    "name": "Acharnement",
                    "description": "Quand vous tombez à 0 point de vie mais n'êtes pas tué sur le coup, vous pouvez passer à 1 point de vie à la place. Vous ne pouvez pas réutiliser cette capacité tant que vous n'avez pas terminé un repos long."
                },
                {
                    "name": "Attaques sauvages",
                    "description": "Quand vous réussissez un coup critique avec une attaque d'arme de corps à corps, vous pouvez lancer un des dés de dégâts de l'arme une fois de plus et l'ajouter aux dégâts supplémentaires du coup critique."
                }
            ]
        }
    }

def get_all_class_features():
    """Retourner toutes les capacités de classe"""
    return {
        "guerrier": {
            "proficiencies": {
                "armor": ["Toutes les armures", "Boucliers"],
                "weapons": ["Armes simples", "Armes de guerre"],
                "tools": [],
                "saving_throws": ["Force", "Constitution"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Style de combat",
                    "description": "Vous adoptez un style de combat particulier comme spécialité."
                },
                {
                    "level": 1,
                    "name": "Second souffle",
                    "description": "Vous récupérez 1d10 + niveau de guerrier points de vie."
                }
            ]
        },
        "magicien": {
            "proficiencies": {
                "armor": [],
                "weapons": ["Dague", "Dard", "Fronde", "Bâton", "Arbalète légère"],
                "tools": [],
                "saving_throws": ["Intelligence", "Sagesse"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Incantation",
                    "description": "Vous pouvez lancer des sorts de magicien."
                },
                {
                    "level": 1,
                    "name": "Récupération arcanique",
                    "description": "Une fois par jour lors d'un repos court, vous récupérez des emplacements de sorts."
                }
            ]
        },
        "roublard": {
            "proficiencies": {
                "armor": ["Armures légères"],
                "weapons": ["Armes simples", "Arbalète de poing", "Épée courte", "Épée longue", "Rapière"],
                "tools": ["Outils de voleur"],
                "saving_throws": ["Dextérité", "Intelligence"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Expertise",
                    "description": "Choisissez deux de vos maîtrises de compétence ou une maîtrise de compétence et une maîtrise d'outils de voleur. Votre bonus de maîtrise est doublé pour tout test de caractéristique qui utilise l'une des maîtrises choisies."
                },
                {
                    "level": 1,
                    "name": "Attaque sournoise",
                    "description": "Une fois par tour, vous pouvez infliger 1d6 dégâts supplémentaires à une créature que vous touchez avec une attaque si vous avez l'avantage au jet d'attaque."
                }
            ]
        },
        "clerc": {
            "proficiencies": {
                "armor": ["Armures légères", "Armures intermédiaires", "Boucliers"],
                "weapons": ["Armes simples"],
                "tools": [],
                "saving_throws": ["Sagesse", "Charisme"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Incantation",
                    "description": "Vous pouvez lancer des sorts de clerc."
                },
                {
                    "level": 1,
                    "name": "Domaine divin",
                    "description": "Choisissez un domaine lié à votre divinité."
                }
            ]
        },
        "barde": {
            "proficiencies": {
                "armor": ["Armures légères"],
                "weapons": ["Armes simples", "Arbalète de poing", "Épée courte", "Épée longue", "Rapière"],
                "tools": ["Trois instruments de musique de votre choix"],
                "saving_throws": ["Dextérité", "Charisme"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Incantation",
                    "description": "Vous pouvez lancer des sorts de barde."
                },
                {
                    "level": 1,
                    "name": "Inspiration bardique",
                    "description": "Vous pouvez inspirer les autres en parlant ou en chantant."
                }
            ]
        },
        "druide": {
            "proficiencies": {
                "armor": ["Armures légères", "Armures intermédiaires", "Boucliers (non métalliques)"],
                "weapons": ["Massue", "Dague", "Fléchette", "Javeline", "Masse d'armes", "Bâton", "Cimeterre", "Fronde", "Lance"],
                "tools": ["Kit d'herboriste"],
                "saving_throws": ["Intelligence", "Sagesse"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Druidique",
                    "description": "Vous connaissez le druidique, la langue secrète des druides."
                },
                {
                    "level": 1,
                    "name": "Incantation",
                    "description": "Vous pouvez lancer des sorts de druide."
                }
            ]
        },
        "moine": {
            "proficiencies": {
                "armor": [],
                "weapons": ["Armes simples", "Épée courte"],
                "tools": ["Un type d'outils d'artisan ou un instrument de musique"],
                "saving_throws": ["Force", "Dextérité"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Défense sans armure",
                    "description": "Tant que vous ne portez pas d'armure ni de bouclier, votre CA égale 10 + votre modificateur de Dextérité + votre modificateur de Sagesse."
                },
                {
                    "level": 1,
                    "name": "Arts martiaux",
                    "description": "Votre pratique des arts martiaux vous donne la maîtrise des styles de combat qui utilisent les attaques à mains nues et les armes de moine."
                }
            ]
        },
        "rodeur": {
            "proficiencies": {
                "armor": ["Armures légères", "Armures intermédiaires", "Boucliers"],
                "weapons": ["Armes simples", "Armes de guerre"],
                "tools": [],
                "saving_throws": ["Force", "Dextérité"]
            },
            "class_features": [
                {
                    "level": 1,
                    "name": "Ennemi juré",
                    "description": "Choisissez un type de créature comme ennemi juré."
                },
                {
                    "level": 1,
                    "name": "Explorateur-né",
                    "description": "Choisissez un terrain de prédilection."
                }
            ]
        }
    }

def get_all_backgrounds():
    """Retourner tous les historiques"""
    return {
        "crapule": {
            "name": "Crapule",
            "skills": ["Tromperie", "Discrétion"],
            "personality_traits": [
                "Je mens toujours quand c'est plus simple que de dire la vérité.",
                "J'ai toujours un plan pour ce qui peut mal tourner."
            ],
            "ideals": [
                "Liberté. Les chaînes sont faites pour être brisées, comme celles qui lient les opprimés. (Chaotique)"
            ],
            "bonds": [
                "Je suis traqué pour un crime que je n'ai pas commis."
            ],
            "flaws": [
                "Quand je vois quelque chose de précieux, je ne peux pas penser à autre chose qu'à comment le voler."
            ]
        },
        "homme-de-loi": {
            "name": "Homme de loi",
            "skills": ["Investigation", "Persuasion"],
            "personality_traits": [
                "J'ai toujours le bon document ou la bonne référence légale à portée de main.",
                "Je suis très précis dans mes mots et mes actions."
            ],
            "ideals": [
                "Justice. La loi doit être respectée et appliquée équitablement. (Loyal)"
            ],
            "bonds": [
                "Je ferai tout pour préserver l'institution que je sers."
            ],
            "flaws": [
                "Je respecte la loi même quand elle pourrait causer un préjudice."
            ]
        },
        "militaire": {
            "name": "Militaire",
            "skills": ["Athlétisme", "Intimidation"],
            "personality_traits": [
                "Je peux regarder fixement un chien de l'enfer sans ciller.",
                "J'apprécie les plaisirs simples dans la vie : boire, manger, chanter."
            ],
            "ideals": [
                "Plus grand bien. Nos lots sont liés à ceux de tous les autres, et nous devons tous échouer ou réussir ensemble. (Bon)"
            ],
            "bonds": [
                "J'aimerais que mon ancien groupe militaire soit fier de moi."
            ],
            "flaws": [
                "L'ennemi tyrannique que j'ai affronté dans la bataille me hante encore."
            ]
        },
        "habitant-de-la-foret": {
            "name": "Habitant de la forêt",
            "skills": ["Dressage", "Survie"],
            "personality_traits": [
                "Je me sens bien plus à l'aise avec les animaux qu'avec les gens.",
                "J'étais, en fait, élevé par des loups."
            ],
            "ideals": [
                "Changement. La vie c'est comme les saisons, en constant changement, et nous devons changer avec elle. (Chaotique)"
            ],
            "bonds": [
                "Mon isolement m'a rendu grand mais mon raisonnement et mes manières sont quelque peu incultes."
            ],
            "flaws": [
                "Je suis trop attaché à un endroit naturel et je vais le défendre à tout prix."
            ]
        },
        "membre-de-guilde": {
            "name": "Membre de guilde",
            "skills": ["Intuition", "Persuasion"],
            "personality_traits": [
                "Je crois que tout vaut la peine d'être fait s'il vaut la peine d'être bien fait.",
                "Je suis un snob qui regarde de haut ceux qui ne peuvent pas apprécier l'art fin et l'artisanat."
            ],
            "ideals": [
                "Communauté. Il est du devoir de tous les gens civilisés de renforcer les liens de communauté et la sécurité de la civilisation. (Loyal)"
            ],
            "bonds": [
                "L'atelier où j'ai appris mon métier est l'endroit le plus sacré au monde pour moi."
            ],
            "flaws": [
                "Je ne peux pas garder un secret pour sauver ma vie, ou la vie de quelqu'un d'autre."
            ]
        }
    }

def upgrade_all_characters():
    """Mettre à niveau tous les personnages"""
    print("=== MISE À NIVEAU DES PERSONNAGES ===\n")
    
    # Charger les données de référence
    racial_traits = get_all_racial_traits()
    class_features = get_all_class_features()
    backgrounds = get_all_backgrounds()
    
    # Charger les personnages existants
    characters = load_json('data/characters.json')
    
    if not characters:
        print("Aucun personnage trouvé.")
        return
    
    upgraded_count = 0
    total_count = 0
    
    # Traiter chaque utilisateur
    for user_email, user_characters in characters.items():
        print(f"Utilisateur: {user_email}")
        
        for i, character in enumerate(user_characters):
            total_count += 1
            char_name = character.get('name', f'Personnage {i+1}')
            print(f"  Mise à niveau: {char_name}")
            
            # Ajouter les champs manquants
            upgraded = False
            
            # Sous-classe et sous-race
            if 'subclass' not in character:
                character['subclass'] = ""
                upgraded = True
                
            if 'subrace' not in character:
                character['subrace'] = ""
                upgraded = True
                
            # Points d'expérience
            if 'experience_points' not in character:
                character['experience_points'] = (character.get('level', 1) - 1) * 300
                upgraded = True
            
            # Traits raciaux
            race = character.get('race', '').lower()
            if race in racial_traits:
                if 'racial_bonuses' not in character:
                    character['racial_bonuses'] = racial_traits[race].get('ability_bonuses', {})
                    upgraded = True
                    
                if 'speed' not in character:
                    character['speed'] = racial_traits[race].get('speed', 30)
                    upgraded = True
                    
                if 'languages' not in character:
                    character['languages'] = racial_traits[race].get('languages', ["Commun"])
                    upgraded = True
                    
                if 'racial_traits' not in character:
                    character['racial_traits'] = racial_traits[race].get('traits', [])
                    upgraded = True
            
            # Capacités de classe
            char_class = character.get('class', '').lower()
            if char_class in class_features:
                if 'class_features' not in character:
                    character['class_features'] = class_features[char_class].get('class_features', [])
                    upgraded = True
                    
                if 'proficiencies' not in character:
                    character['proficiencies'] = class_features[char_class].get('proficiencies', {})
                    upgraded = True
                    
                if 'saving_throw_proficiencies' not in character:
                    character['saving_throw_proficiencies'] = class_features[char_class]['proficiencies'].get('saving_throws', [])
                    upgraded = True
            
            # Détails physiques
            if 'physical_details' not in character:
                finalization = character.get('finalization', {})
                character['physical_details'] = {
                    "age": finalization.get('age', ''),
                    "height": finalization.get('height', ''),
                    "weight": finalization.get('weight', ''),
                    "hair": finalization.get('hair', ''),
                    "eyes": finalization.get('eyes', ''),
                    "skin": finalization.get('skin', ''),
                    "gender": finalization.get('sex', ''),
                    "appearance": finalization.get('appearance', ''),
                    "backstory": finalization.get('history', '')
                }
                upgraded = True
            
            # Alignement
            if 'alignment' not in character:
                character['alignment'] = character.get('finalization', {}).get('alignment', '')
                upgraded = True
            
            # Personnalité de l'historique
            if 'personality' not in character:
                background_name = character.get('background', '').lower().replace('-', '')
                if background_name in backgrounds:
                    bg = backgrounds[background_name]
                    character['personality'] = {
                        "traits": bg.get('personality_traits', [])[:1],
                        "ideals": bg.get('ideals', [])[:1], 
                        "bonds": bg.get('bonds', [])[:1],
                        "flaws": bg.get('flaws', [])[:1]
                    }
                else:
                    character['personality'] = {
                        "traits": [],
                        "ideals": [],
                        "bonds": [],
                        "flaws": []
                    }
                upgraded = True
            
            # Détails d'historique
            if 'background_details' not in character:
                background_name = character.get('background', '').lower().replace('-', '')
                if background_name in backgrounds:
                    character['background_details'] = backgrounds[background_name]
                else:
                    character['background_details'] = {}
                upgraded = True
            
            # Améliorer l'équipement
            if 'equipment' in character and isinstance(character['equipment'], dict):
                equipment = character['equipment']
                
                # Structure moderne de l'équipement
                if not isinstance(equipment.get('armor'), dict):
                    new_equipment = {
                        "armor": {},
                        "shield": {},
                        "weapons": [],
                        "inventory": [],
                        "currency": {"pp": 0, "po": 0, "pe": 0, "pa": 0, "pc": 0}
                    }
                    
                    # Convertir l'ancienne structure
                    if equipment.get('selected_armor'):
                        new_equipment['armor'] = {
                            "name": equipment['selected_armor'],
                            "ac": 12,
                            "type": "Armure légère"
                        }
                    
                    if equipment.get('selected_shield'):
                        new_equipment['shield'] = {
                            "name": equipment['selected_shield'],
                            "ac_bonus": 2
                        }
                    
                    # Convertir les armes
                    weapons = []
                    for weapon_key in ['selected_main_weapon', 'selected_secondary_weapon', 'selected_backup_weapon']:
                        if equipment.get(weapon_key):
                            weapons.append({
                                "name": equipment[weapon_key],
                                "damage": "1d8",
                                "damage_type": "tranchant"
                            })
                    new_equipment['weapons'] = weapons
                    
                    # Convertir l'inventaire
                    if equipment.get('selected_inventory'):
                        inventory_items = equipment['selected_inventory']
                        if isinstance(inventory_items, list):
                            new_equipment['inventory'] = inventory_items
                    
                    character['equipment'] = new_equipment
                    upgraded = True
            
            # Nettoyer les anciens champs
            if 'finalization' in character:
                del character['finalization']
                upgraded = True
            
            # Marquer la version
            character['version'] = "2.0"
            
            if upgraded:
                upgraded_count += 1
                print(f"    ✓ Mis à niveau avec succès")
            else:
                print(f"    - Déjà à jour")
    
    # Sauvegarder les modifications
    save_json(characters, 'data/characters.json')
    
    print(f"\n=== RÉSUMÉ ===")
    print(f"Personnages traités: {total_count}")
    print(f"Personnages mis à niveau: {upgraded_count}")
    print(f"Fichier sauvegardé: data/characters.json")

if __name__ == "__main__":
    upgrade_all_characters()