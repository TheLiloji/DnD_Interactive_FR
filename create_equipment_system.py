#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def create_equipment_data():
    """Créer les données d'équipement manuellement pour être sûr de la qualité"""
    
    # Armures extraites manuellement du fichier
    armors = [
        # Armures légères
        {"name": "Matelassée", "type": "légère", "ca": "11 + Dex", "price": "5 po", "weight": "4 kg", "stealth_disadvantage": True},
        {"name": "Cuir", "type": "légère", "ca": "11 + Dex", "price": "10 po", "weight": "5 kg", "stealth_disadvantage": False},
        {"name": "Cuir clouté", "type": "légère", "ca": "12 + Dex", "price": "45 po", "weight": "6,5 kg", "stealth_disadvantage": False},
        
        # Armures intermédiaires
        {"name": "Peau", "type": "intermédiaire", "ca": "12 + Dex (max 2)", "price": "10 po", "weight": "6 kg", "stealth_disadvantage": False},
        {"name": "Chemise de mailles", "type": "intermédiaire", "ca": "13 + Dex (max 2)", "price": "50 po", "weight": "10 kg", "stealth_disadvantage": False},
        {"name": "Écailles", "type": "intermédiaire", "ca": "14 + Dex (max 2)", "price": "50 po", "weight": "22,5 kg", "stealth_disadvantage": True},
        {"name": "Cuirasse", "type": "intermédiaire", "ca": "14 + Dex (max 2)", "price": "400 po", "weight": "10 kg", "stealth_disadvantage": False},
        {"name": "Demi-plate", "type": "intermédiaire", "ca": "15 + Dex (max 2)", "price": "750 po", "weight": "20 kg", "stealth_disadvantage": True},
        
        # Armures lourdes
        {"name": "Broigne", "type": "lourde", "ca": "14", "price": "30 po", "weight": "20 kg", "stealth_disadvantage": True, "force_req": None},
        {"name": "Cotte de mailles", "type": "lourde", "ca": "16", "price": "75 po", "weight": "27,5 kg", "stealth_disadvantage": True, "force_req": "For 13"},
        {"name": "Clibanion", "type": "lourde", "ca": "17", "price": "200 po", "weight": "30 kg", "stealth_disadvantage": True, "force_req": "For 15"},
        {"name": "Harnois", "type": "lourde", "ca": "18", "price": "1500 po", "weight": "32,5 kg", "stealth_disadvantage": True, "force_req": "For 15"},
        
        # Bouclier
        {"name": "Bouclier", "type": "bouclier", "ca": "+2", "price": "10 po", "weight": "3 kg", "stealth_disadvantage": False}
    ]
    
    # Armes extraites manuellement
    weapons = [
        # Armes de corps-à-corps courantes
        {"name": "Bâton", "type": "courante", "range": "corps-à-corps", "damage": "1d6 contondant", "price": "2 pa", "weight": "2 kg", "properties": "Polyvalente (1d8)"},
        {"name": "Dague", "type": "courante", "range": "corps-à-corps", "damage": "1d4 perforant", "price": "2 po", "weight": "0,5 kg", "properties": "Finesse, légère, lancer (portée 6/18)"},
        {"name": "Gourdin", "type": "courante", "range": "corps-à-corps", "damage": "1d4 contondant", "price": "1 pa", "weight": "1 kg", "properties": "Légère"},
        {"name": "Hachette", "type": "courante", "range": "corps-à-corps", "damage": "1d6 tranchant", "price": "5 po", "weight": "1 kg", "properties": "Légère, lancer (portée 6/18)"},
        {"name": "Javeline", "type": "courante", "range": "corps-à-corps", "damage": "1d6 perforant", "price": "5 pa", "weight": "1 kg", "properties": "Lancer (portée 9/36)"},
        {"name": "Lance", "type": "courante", "range": "corps-à-corps", "damage": "1d6 perforant", "price": "1 po", "weight": "1,5 kg", "properties": "Lancer (portée 6/18), polyvalente (1d8)"},
        {"name": "Marteau léger", "type": "courante", "range": "corps-à-corps", "damage": "1d4 contondant", "price": "2 po", "weight": "1 kg", "properties": "Légère, lancer (portée 6/18)"},
        {"name": "Masse d'armes", "type": "courante", "range": "corps-à-corps", "damage": "1d6 contondant", "price": "5 po", "weight": "2 kg", "properties": "-"},
        {"name": "Massue", "type": "courante", "range": "corps-à-corps", "damage": "1d8 contondant", "price": "2 pa", "weight": "5 kg", "properties": "À deux mains"},
        {"name": "Serpe", "type": "courante", "range": "corps-à-corps", "damage": "1d4 tranchant", "price": "1 po", "weight": "1 kg", "properties": "Légère"},
        
        # Armes à distance courantes
        {"name": "Arbalète légère", "type": "courante", "range": "distance", "damage": "1d8 perforant", "price": "25 po", "weight": "2,5 kg", "properties": "Munitions (portée 24/96), chargement, à deux mains"},
        {"name": "Arc court", "type": "courante", "range": "distance", "damage": "1d6 perforant", "price": "25 po", "weight": "1 kg", "properties": "Munitions (portée 24/96), à deux mains"},
        {"name": "Fléchettes", "type": "courante", "range": "distance", "damage": "1d4 perforant", "price": "5 pc", "weight": "0,1 kg", "properties": "Finesse, lancer (portée 6/18)"},
        {"name": "Fronde", "type": "courante", "range": "distance", "damage": "1d4 contondant", "price": "1 pa", "weight": "-", "properties": "Munitions (portée 9/36)"},
        
        # Armes de corps-à-corps de guerre
        {"name": "Cimeterre", "type": "guerre", "range": "corps-à-corps", "damage": "1d6 tranchant", "price": "25 po", "weight": "1,5 kg", "properties": "Finesse, légère"},
        {"name": "Coutille", "type": "guerre", "range": "corps-à-corps", "damage": "1d10 tranchant", "price": "20 po", "weight": "3 kg", "properties": "Lourde, allonge, à deux mains"},
        {"name": "Épée à deux mains", "type": "guerre", "range": "corps-à-corps", "damage": "2d6 tranchant", "price": "50 po", "weight": "3 kg", "properties": "Lourde, à deux mains"},
        {"name": "Épée courte", "type": "guerre", "range": "corps-à-corps", "damage": "1d6 perforant", "price": "10 po", "weight": "1 kg", "properties": "Finesse, légère"},
        {"name": "Épée longue", "type": "guerre", "range": "corps-à-corps", "damage": "1d8 tranchant", "price": "15 po", "weight": "1,5 kg", "properties": "Polyvalente (1d10)"},
        {"name": "Fléau", "type": "guerre", "range": "corps-à-corps", "damage": "1d8 contondant", "price": "10 po", "weight": "1 kg", "properties": "-"},
        {"name": "Fouet", "type": "guerre", "range": "corps-à-corps", "damage": "1d4 tranchant", "price": "2 po", "weight": "1,5 kg", "properties": "Finesse, allonge"},
        {"name": "Hache à deux mains", "type": "guerre", "range": "corps-à-corps", "damage": "1d12 tranchant", "price": "30 po", "weight": "3,5 kg", "properties": "Lourde, à deux mains"},
        {"name": "Hache d'armes", "type": "guerre", "range": "corps-à-corps", "damage": "1d8 tranchant", "price": "10 po", "weight": "2 kg", "properties": "Polyvalente (1d10)"},
        {"name": "Hallebarde", "type": "guerre", "range": "corps-à-corps", "damage": "1d10 tranchant", "price": "20 po", "weight": "3 kg", "properties": "Lourde, allonge, à deux mains"},
        {"name": "Lance d'arçon", "type": "guerre", "range": "corps-à-corps", "damage": "1d12 perforant", "price": "10 po", "weight": "3 kg", "properties": "Allonge, spéciale"},
        {"name": "Marteau de guerre", "type": "guerre", "range": "corps-à-corps", "damage": "1d8 contondant", "price": "15 po", "weight": "1 kg", "properties": "Polyvalente (1d10)"},
        {"name": "Merlin", "type": "guerre", "range": "corps-à-corps", "damage": "2d6 contondant", "price": "10 po", "weight": "5 kg", "properties": "Lourde, à deux mains"},
        {"name": "Morgenstern", "type": "guerre", "range": "corps-à-corps", "damage": "1d8 perforant", "price": "15 po", "weight": "2 kg", "properties": "-"},
        {"name": "Pic de guerre", "type": "guerre", "range": "corps-à-corps", "damage": "1d8 perforant", "price": "5 po", "weight": "1 kg", "properties": "-"},
        {"name": "Pique", "type": "guerre", "range": "corps-à-corps", "damage": "1d10 perforant", "price": "5 po", "weight": "9 kg", "properties": "Lourde, allonge, à deux mains"},
        {"name": "Rapière", "type": "guerre", "range": "corps-à-corps", "damage": "1d8 perforant", "price": "25 po", "weight": "1 kg", "properties": "Finesse"},
        {"name": "Trident", "type": "guerre", "range": "corps-à-corps", "damage": "1d6 perforant", "price": "5 po", "weight": "2 kg", "properties": "Lancer (portée 6/18), polyvalente (1d8)"},
        
        # Armes à distance de guerre
        {"name": "Arbalète de poing", "type": "guerre", "range": "distance", "damage": "1d6 perforant", "price": "75 po", "weight": "1,5 kg", "properties": "Munitions (portée 9/36), légère, chargement"},
        {"name": "Arbalète lourde", "type": "guerre", "range": "distance", "damage": "1d10 perforant", "price": "50 po", "weight": "9 kg", "properties": "Munitions (portée 30/120), lourde, chargement, à deux mains"},
        {"name": "Arc long", "type": "guerre", "range": "distance", "damage": "1d8 perforant", "price": "50 po", "weight": "1 kg", "properties": "Munitions (portée 45/180), lourde, à deux mains"},
        {"name": "Filet", "type": "guerre", "range": "distance", "damage": "-", "price": "1 po", "weight": "1,5 kg", "properties": "Spéciale, lancer (portée 1,5/4,5)"},
        {"name": "Sarbacane", "type": "guerre", "range": "distance", "damage": "1 perforant", "price": "10 po", "weight": "0,5 kg", "properties": "Munitions (portée 7,5/30), chargement"}
    ]
    
    # Équipement d'aventurier sélectionné
    equipment = [
        {"name": "Acide (fiole)", "price": "25 po", "weight": "0,5 kg", "category": "Outils"},
        {"name": "Antitoxine (fiole)", "price": "50 po", "weight": "-", "category": "Potions"},
        {"name": "Balance de marchand", "price": "5 po", "weight": "1,5 kg", "category": "Outils"},
        {"name": "Bélier portatif", "price": "4 po", "weight": "17,5 kg", "category": "Outils"},
        {"name": "Billes (sac de 1000)", "price": "1 po", "weight": "1 kg", "category": "Outils"},
        {"name": "Boîte à amadou", "price": "5 pa", "weight": "0,5 kg", "category": "Outils"},
        {"name": "Bougie", "price": "1 pc", "weight": "0,5 kg", "category": "Éclairage"},
        {"name": "Cadenas", "price": "10 po", "weight": "0,5 kg", "category": "Outils"},
        {"name": "Carquois", "price": "1 po", "weight": "0,5 kg", "category": "Munitions"},
        {"name": "Chaîne (3 mètres)", "price": "5 po", "weight": "5 kg", "category": "Outils"},
        {"name": "Chausse-trappes (sac de 20)", "price": "1 po", "weight": "1 kg", "category": "Outils"},
        {"name": "Corde de chanvre (15 mètres)", "price": "2 po", "weight": "5 kg", "category": "Outils"},
        {"name": "Corde de soie (15 mètres)", "price": "10 po", "weight": "2,5 kg", "category": "Outils"},
        {"name": "Eau bénite (flasque)", "price": "25 po", "weight": "0,5 kg", "category": "Potions"},
        {"name": "Étui à cartes", "price": "1 po", "weight": "0,5 kg", "category": "Contenants"},
        {"name": "Étui pour carreaux", "price": "1 po", "weight": "0,5 kg", "category": "Munitions"},
        {"name": "Feu grégeois (flasque)", "price": "50 po", "weight": "0,5 kg", "category": "Outils"},
        {"name": "Focaliseur arcanique", "price": "20 po", "weight": "1,5 kg", "category": "Focaliseurs"},
        {"name": "Focaliseur druidique", "price": "10 po", "weight": "2 kg", "category": "Focaliseurs"},
        {"name": "Gamelle", "price": "2 po", "weight": "0,5 kg", "category": "Ustensiles"},
        {"name": "Grimoire", "price": "50 po", "weight": "1,5 kg", "category": "Livres"},
        {"name": "Huile (flasque)", "price": "1 pa", "weight": "0,5 kg", "category": "Outils"},
        {"name": "Lampe", "price": "5 pa", "weight": "0,5 kg", "category": "Éclairage"},
        {"name": "Lanterne à capote", "price": "5 po", "weight": "1 kg", "category": "Éclairage"},
        {"name": "Lanterne sourde", "price": "10 po", "weight": "1 kg", "category": "Éclairage"},
        {"name": "Livre", "price": "25 po", "weight": "2,5 kg", "category": "Livres"},
        {"name": "Longue-vue", "price": "1000 po", "weight": "0,5 kg", "category": "Outils"},
        {"name": "Loupe", "price": "100 po", "weight": "-", "category": "Outils"},
        {"name": "Matériel de pêche", "price": "1 po", "weight": "2 kg", "category": "Outils"},
        {"name": "Matériel d'escalade", "price": "25 po", "weight": "6 kg", "category": "Outils"},
        {"name": "Menottes", "price": "2 po", "weight": "3 kg", "category": "Outils"},
        {"name": "Palan", "price": "20 po", "weight": "2,5 kg", "category": "Outils"},
        {"name": "Pied-de-biche", "price": "2 po", "weight": "2,5 kg", "category": "Outils"},
        {"name": "Piège à mâchoires", "price": "5 po", "weight": "12,5 kg", "category": "Outils"},
        {"name": "Poison (fiole)", "price": "100 po", "weight": "-", "category": "Potions"},
        {"name": "Potion de soins", "price": "50 po", "weight": "0,25 kg", "category": "Potions"},
        {"name": "Rations (1 jour)", "price": "2 po", "weight": "1 kg", "category": "Nourriture"},
        {"name": "Sacoche", "price": "5 pa", "weight": "0,5 kg", "category": "Contenants"},
        {"name": "Sacoche à composantes", "price": "25 po", "weight": "1 kg", "category": "Focaliseurs"},
        {"name": "Sac à dos", "price": "2 po", "weight": "2,5 kg", "category": "Contenants"},
        {"name": "Sac de couchage", "price": "1 po", "weight": "3,5 kg", "category": "Camping"},
        {"name": "Symbole sacré", "price": "5 po", "weight": "-", "category": "Focaliseurs"},
        {"name": "Tente (2 personnes)", "price": "2 po", "weight": "10 kg", "category": "Camping"},
        {"name": "Torche", "price": "1 pc", "weight": "0,5 kg", "category": "Éclairage"},
        {"name": "Trousse de soins", "price": "5 po", "weight": "1,5 kg", "category": "Médical"}
    ]
    
    # Maîtrises par classe (extraites manuellement)
    proficiencies = {
        "barbare": {
            "armors": "armures légères, armures intermédiaires, boucliers",
            "weapons": "armes courantes, armes de guerre"
        },
        "barde": {
            "armors": "armures légères",
            "weapons": "armes courantes, arbalètes de poing, épées longues, rapières, épées courtes"
        },
        "clerc": {
            "armors": "armures légères, armures intermédiaires, boucliers",
            "weapons": "armes courantes"
        },
        "druide": {
            "armors": "armures légères, armures intermédiaires, boucliers (non métalliques)",
            "weapons": "gourdins, dagues, fléchettes, javelines, masses d'armes, bâtons, cimeterres, serpes, frondes, lances"
        },
        "ensorceleur": {
            "armors": "aucune",
            "weapons": "dagues, fléchettes, frondes, bâtons, arbalètes légères"
        },
        "guerrier": {
            "armors": "toutes les armures, boucliers",
            "weapons": "armes courantes, armes de guerre"
        },
        "magicien": {
            "armors": "aucune",
            "weapons": "dagues, fléchettes, frondes, bâtons, arbalètes légères"
        },
        "moine": {
            "armors": "aucune",
            "weapons": "armes courantes, épées courtes"
        },
        "paladin": {
            "armors": "toutes les armures, boucliers",
            "weapons": "armes courantes, armes de guerre"
        },
        "rodeur": {
            "armors": "armures légères, armures intermédiaires, boucliers",
            "weapons": "armes courantes, armes de guerre"
        },
        "roublard": {
            "armors": "armures légères",
            "weapons": "armes courantes, arbalètes de poing, épées longues, rapières, épées courtes"
        },
        "sorcier": {
            "armors": "armures légères",
            "weapons": "armes courantes"
        }
    }
    
    return {
        "armors": armors,
        "weapons": weapons,
        "equipment": equipment,
        "proficiencies": proficiencies
    }

if __name__ == "__main__":
    print("🔧 CRÉATION DU SYSTÈME D'ÉQUIPEMENT")
    print("=" * 60)
    
    data = create_equipment_data()
    
    # Sauvegarder les données
    with open('equipment_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(data['armors'])} armures créées")
    print(f"✅ {len(data['weapons'])} armes créées")
    print(f"✅ {len(data['equipment'])} objets d'équipement créés")
    print(f"✅ {len(data['proficiencies'])} classes avec maîtrises")
    
    print(f"\n📋 EXEMPLES D'ARMURES:")
    for armor in data['armors'][:5]:
        print(f"   - {armor['name']} ({armor['type']}) - CA: {armor['ca']} - Prix: {armor['price']}")
    
    print(f"\n⚔️ EXEMPLES D'ARMES:")
    for weapon in data['weapons'][:5]:
        print(f"   - {weapon['name']} ({weapon['type']}, {weapon['range']}) - Dégâts: {weapon['damage']}")
    
    print(f"\n🎒 EXEMPLES D'ÉQUIPEMENT:")
    for item in data['equipment'][:5]:
        print(f"   - {item['name']} - Prix: {item['price']} - Poids: {item['weight']}")
    
    print(f"\n✅ Données sauvegardées dans equipment_data.json") 