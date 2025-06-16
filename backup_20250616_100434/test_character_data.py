#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour enrichir et analyser les données de personnage D&D 5e
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

def get_racial_traits():
    """Retourner les traits raciaux complets"""
    return {
        "nain": {
            "name": "Nain",
            "ability_bonuses": {"constitution": 2},
            "speed": 25,
            "size": "Moyen",
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
            "name": "Humain",  
            "ability_bonuses": {"force": 1, "dexterite": 1, "constitution": 1, "intelligence": 1, "sagesse": 1, "charisme": 1},
            "speed": 30,
            "size": "Moyen",
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
            "name": "Elfe",
            "ability_bonuses": {"dexterite": 2},
            "speed": 30,
            "size": "Moyen",
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
        }
    }

def get_class_features():
    """Retourner les capacités de classe complètes"""
    return {
        "guerrier": {
            "name": "Guerrier",
            "hit_die": 10,
            "primary_ability": ["Force", "Dextérité"],
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
        "mage": {
            "name": "Magicien",
            "hit_die": 6,
            "primary_ability": ["Intelligence"],
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
        }
    }

def get_backgrounds():
    """Retourner les historiques complets"""
    return {
        "crapule": {
            "name": "Crapule",
            "skills": ["Tromperie", "Discrétion"],
            "languages": [],
            "tools": ["Outils de voleur", "Un type de jeu"],
            "equipment": [
                "Un pied-de-biche",
                "Des vêtements sombres avec une capuche",
                "Une bourse contenant 15 po"
            ],
            "feature": {
                "name": "Contacts criminels",
                "description": "Vous avez un contact fiable et digne de confiance qui agit comme votre agent de liaison avec un réseau d'autres criminels."
            },
            "personality_traits": [
                "Je mens toujours quand c'est plus simple que de dire la vérité.",
                "J'ai toujours un plan pour ce qui peut mal tourner."
            ],
            "ideals": [
                "Honneur. Je ne vole pas mes autres membres du gang ou mes clients. (Loyal)",
                "Liberté. Les chaînes sont faites pour être brisées, comme celles qui lient les opprimés. (Chaotique)"
            ],
            "bonds": [
                "Je suis traqué pour un crime que je n'ai pas commis.",
                "J'ai une dette qui ne peut être remboursée à une personne malveillante."
            ],
            "flaws": [
                "Quand je vois quelque chose de précieux, je ne peux pas penser à autre chose qu'à comment le voler.",
                "Quand je suis face au choix entre l'argent et mes amis, je choisis généralement l'argent."
            ]
        }
    }

def create_complete_test_character():
    """Créer un personnage de test avec TOUTES les données"""
    racial_traits = get_racial_traits()
    class_features = get_class_features()
    backgrounds = get_backgrounds()
    
    character = {
        "name": "Test Complet",
        "level": 3,
        "class": "guerrier",
        "subclass": "Champion",
        "race": "nain",
        "subrace": "Nain des montagnes",
        "background": "crapule",
        "experience_points": 900,
        
        # Caractéristiques avec bonus raciaux appliqués
        "abilities": {
            "force": 16,      # 15 + 1 (racial)
            "dexterite": 14,  # 14 de base
            "constitution": 17, # 15 + 2 (racial nain)
            "intelligence": 12, # 12 de base
            "sagesse": 13,    # 13 de base
            "charisme": 10    # 10 de base
        },
        
        # Bonus raciaux séparés pour clarté
        "racial_bonuses": racial_traits["nain"]["ability_bonuses"],
        
        # Compétences avec maîtrises
        "skills": ["Athlétisme", "Intimidation", "Tromperie", "Discrétion"],
        
        # Jets de sauvegarde avec maîtrises
        "saving_throw_proficiencies": ["Force", "Constitution"],
        
        # Vitesse (modifiée par la race)
        "speed": racial_traits["nain"]["speed"],
        
        # Langues
        "languages": racial_traits["nain"]["languages"] + ["Voleur"],
        
        # Traits raciaux complets
        "racial_traits": racial_traits["nain"]["traits"],
        
        # Capacités de classe complètes
        "class_features": class_features["guerrier"]["class_features"],
        
        # Maîtrises d'armes et armures
        "proficiencies": {
            "armor": class_features["guerrier"]["proficiencies"]["armor"],
            "weapons": class_features["guerrier"]["proficiencies"]["weapons"] + ["Hachette", "Hache d'armes", "Marteau léger", "Marteau de guerre"],
            "tools": ["Outils de forgeron", "Outils de voleur", "Un type de jeu"],
            "saving_throws": class_features["guerrier"]["proficiencies"]["saving_throws"]
        },
        
        # Historique complet
        "background_details": backgrounds["crapule"],
        
        # Équipement détaillé
        "equipment": {
            "armor": {
                "name": "Cotte de mailles",
                "ac": 16,
                "type": "Armure intermédiaire",
                "stealth_disadvantage": True
            },
            "shield": {
                "name": "Bouclier",
                "ac_bonus": 2
            },
            "weapons": [
                {
                    "name": "Épée longue",
                    "damage": "1d8",
                    "damage_type": "tranchant",
                    "properties": ["Polyvalente (1d10)"]
                },
                {
                    "name": "Hache d'armes",
                    "damage": "1d8",
                    "damage_type": "tranchant",
                    "properties": ["Polyvalente (1d10)"]
                },
                {
                    "name": "Arc court",
                    "damage": "1d6",
                    "damage_type": "perforant",
                    "range": "24/96",
                    "properties": ["Munitions", "Légère", "À deux mains"]
                }
            ],
            "inventory": [
                "Pied-de-biche",
                "Vêtements sombres avec capuche",
                "Outils de voleur",
                "Carquois avec 20 flèches",
                "Sac d'exploration",
                "Corde de chanvre (15 mètres)",
                "10 torches",
                "Rations (10 jours)",
                "Kit de guérison"
            ],
            "currency": {
                "pp": 2,
                "po": 47,
                "pe": 3,
                "pa": 15,
                "pc": 28
            }
        },
        
        # Détails physiques complets
        "physical_details": {
            "age": 45,
            "height": "1m35",
            "weight": "75 kg",
            "hair": "Brun avec des mèches grises",
            "eyes": "Noisette",
            "skin": "Basanée et rugueuse",
            "gender": "Homme",
            "appearance": "Un nain robuste avec une barbe tressée et des mains calleuses d'artisan. Porte souvent un tablier de forgeron même en dehors de son atelier.",
            "backstory": "Ancien forgeron devenu mercenaire après que sa forge ait été détruite par des bandits. Cherche maintenant à reconstruire sa vie tout en luttant contre ses tendances criminelles."
        },
        
        # Alignement
        "alignment": "Chaotique Neutre",
        
        # Personnalité de l'historique
        "personality": {
            "traits": ["Je mens toujours quand c'est plus simple que de dire la vérité."],
            "ideals": ["Liberté. Les chaînes sont faites pour être brisées, comme celles qui lient les opprimés. (Chaotique)"],
            "bonds": ["Je suis traqué pour un crime que je n'ai pas commis."],
            "flaws": ["Quand je vois quelque chose de précieux, je ne peux pas penser à autre chose qu'à comment le voler."]
        },
        
        # Sorts (aucun pour un guerrier)
        "spells": [],
        
        # Notes diverses
        "notes": "Personnage de test complet avec toutes les données nécessaires pour une fiche de personnage D&D 5e complète.",
        
        # Métadonnées
        "owner": "test@example.com",
        "created_at": datetime.now().isoformat(),
        "version": "2.0"
    }
    
    return character

def analyze_current_character(character_data):
    """Analyser un personnage existant et identifier les données manquantes"""
    missing_data = []
    
    # Vérifier les champs essentiels
    essential_fields = [
        'subclass', 'subrace', 'experience_points', 'racial_bonuses',
        'saving_throw_proficiencies', 'speed', 'languages', 'racial_traits',
        'class_features', 'proficiencies', 'background_details', 'physical_details',
        'alignment', 'personality'
    ]
    
    for field in essential_fields:
        if field not in character_data:
            missing_data.append(f"Champ manquant: {field}")
    
    # Vérifier la structure de l'équipement
    if 'equipment' in character_data:
        equipment = character_data['equipment']
        if not isinstance(equipment.get('armor'), dict):
            missing_data.append("Équipement: structure d'armure incomplète")
        if not isinstance(equipment.get('weapons'), list):
            missing_data.append("Équipement: liste des armes manquante")
        if 'currency' not in equipment:
            missing_data.append("Équipement: monnaie manquante")
    else:
        missing_data.append("Équipement: section complètement manquante")
    
    return missing_data

def upgrade_character_structure(old_character):
    """Mettre à niveau un ancien personnage vers la nouvelle structure"""
    racial_traits = get_racial_traits()
    class_features = get_class_features()
    backgrounds = get_backgrounds()
    
    # Créer une copie mise à niveau
    upgraded = old_character.copy()
    
    # Ajouter les champs manquants avec valeurs par défaut
    if 'subclass' not in upgraded:
        upgraded['subclass'] = ""
    
    if 'subrace' not in upgraded:
        upgraded['subrace'] = ""
    
    if 'experience_points' not in upgraded:
        upgraded['experience_points'] = (upgraded.get('level', 1) - 1) * 300
    
    # Ajouter les bonus raciaux
    race = upgraded.get('race', '').lower()
    if race in racial_traits and 'racial_bonuses' not in upgraded:
        upgraded['racial_bonuses'] = racial_traits[race].get('ability_bonuses', {})
    
    # Ajouter la vitesse raciale
    if 'speed' not in upgraded:
        if race in racial_traits:
            upgraded['speed'] = racial_traits[race].get('speed', 30)
        else:
            upgraded['speed'] = 30
    
    # Ajouter les langues
    if 'languages' not in upgraded:
        if race in racial_traits:
            upgraded['languages'] = racial_traits[race].get('languages', ["Commun"])
        else:
            upgraded['languages'] = ["Commun"]
    
    # Ajouter les traits raciaux
    if 'racial_traits' not in upgraded:
        if race in racial_traits:
            upgraded['racial_traits'] = racial_traits[race].get('traits', [])
        else:
            upgraded['racial_traits'] = []
    
    # Ajouter les capacités de classe
    char_class = upgraded.get('class', '').lower()
    if 'class_features' not in upgraded:
        if char_class in class_features:
            upgraded['class_features'] = class_features[char_class].get('class_features', [])
        else:
            upgraded['class_features'] = []
    
    # Mettre à niveau l'équipement
    if 'equipment' in upgraded and isinstance(upgraded['equipment'], dict):
        equipment = upgraded['equipment']
        
        # Convertir l'équipement simple en structure détaillée
        new_equipment = {
            "armor": {},
            "shield": {},
            "weapons": [],
            "inventory": [],
            "currency": {"pp": 0, "po": 0, "pe": 0, "pa": 0, "pc": 0}
        }
        
        if equipment.get('selected_armor'):
            new_equipment['armor'] = {
                "name": equipment['selected_armor'],
                "ac": 12,  # Valeur par défaut
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
        
        upgraded['equipment'] = new_equipment
    
    # Ajouter les détails physiques
    if 'physical_details' not in upgraded:
        finalization = upgraded.get('finalization', {})
        upgraded['physical_details'] = {
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
    
    # Ajouter l'alignement
    if 'alignment' not in upgraded:
        upgraded['alignment'] = upgraded.get('finalization', {}).get('alignment', '')
    
    # Ajouter la personnalité
    if 'personality' not in upgraded:
        background_name = upgraded.get('background', '').lower().replace('-', '')
        if background_name in backgrounds:
            bg = backgrounds[background_name]
            upgraded['personality'] = {
                "traits": bg.get('personality_traits', [])[:1],
                "ideals": bg.get('ideals', [])[:1],
                "bonds": bg.get('bonds', [])[:1],
                "flaws": bg.get('flaws', [])[:1]
            }
        else:
            upgraded['personality'] = {
                "traits": [],
                "ideals": [],
                "bonds": [],
                "flaws": []
            }
    
    # Ajouter les maîtrises
    if 'proficiencies' not in upgraded:
        upgraded['proficiencies'] = {
            "armor": [],
            "weapons": [],
            "tools": [],
            "saving_throws": []
        }
    
    # Ajouter les détails d'historique
    if 'background_details' not in upgraded:
        background_name = upgraded.get('background', '').lower().replace('-', '')
        if background_name in backgrounds:
            upgraded['background_details'] = backgrounds[background_name]
        else:
            upgraded['background_details'] = {}
    
    # Nettoyer les anciens champs
    if 'finalization' in upgraded:
        del upgraded['finalization']
    
    upgraded['version'] = "2.0"
    
    return upgraded

if __name__ == "__main__":
    print("=== TEST DES DONNÉES DE PERSONNAGE D&D 5E ===\n")
    
    # Charger les personnages existants
    print("1. Chargement des personnages existants...")
    characters = load_json('data/characters.json')
    
    # Analyser le premier personnage
    if characters:
        first_user = list(characters.keys())[0]
        if characters[first_user]:
            first_char = characters[first_user][0]
            print(f"   Personnage analysé: {first_char.get('name', 'Sans nom')}")
            missing = analyze_current_character(first_char)
            print(f"   Données manquantes: {len(missing)}")
            for item in missing[:5]:  # Afficher les 5 premiers
                print(f"   - {item}")
    
    # Créer un personnage de test complet
    print("\n2. Création d'un personnage de test complet...")
    test_character = create_complete_test_character()
    print(f"   Personnage créé: {test_character['name']}")
    print(f"   Niveau: {test_character['level']}")
    print(f"   Classe: {test_character['class']} ({test_character['subclass']})")
    print(f"   Race: {test_character['race']} ({test_character['subrace']})")
    print(f"   Nombre de traits raciaux: {len(test_character['racial_traits'])}")
    print(f"   Nombre de capacités de classe: {len(test_character['class_features'])}")
    print(f"   Nombre d'armes: {len(test_character['equipment']['weapons'])}")
    
    # Sauvegarder le personnage de test
    test_characters = {"test@example.com": [test_character]}
    save_json(test_characters, 'test_complete_character.json')
    print("   Personnage de test sauvegardé dans 'test_complete_character.json'")
    
    # Mettre à niveau un personnage existant
    if characters and characters[first_user]:
        print("\n3. Mise à niveau d'un personnage existant...")
        old_char = characters[first_user][0]
        upgraded_char = upgrade_character_structure(old_char)
        print(f"   Personnage mis à niveau: {upgraded_char['name']}")
        print(f"   Version: {upgraded_char.get('version', '1.0')}")
        
        # Sauvegarder le personnage mis à niveau
        upgraded_characters = {first_user: [upgraded_char]}
        save_json(upgraded_characters, 'upgraded_character.json')
        print("   Personnage mis à niveau sauvegardé dans 'upgraded_character.json'")
    
    print("\n=== FIN DES TESTS ===")