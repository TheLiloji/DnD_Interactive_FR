#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def analyze_armors():
    """Analyser les armures disponibles"""
    print("🛡️ ANALYSE DES ARMURES")
    print("=" * 60)
    
    armor_path = 'data/docs/armures/README.md'
    if not os.path.exists(armor_path):
        print("❌ Fichier armures introuvable")
        return []
    
    with open(armor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher les tableaux d'armures
    armor_patterns = [
        r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|',  # Tableau complet
        r'### ([^#\n]+armure[^#\n]*)',  # Titres d'armures
    ]
    
    armors = []
    
    # Extraire depuis les tableaux
    table_matches = re.findall(armor_patterns[0], content)
    for match in table_matches:
        if 'Nom' not in match[0] and match[0].strip():  # Ignorer les en-têtes
            armor_name = match[0].strip()
            armor_type = match[1].strip() if len(match) > 1 else ""
            ca = match[2].strip() if len(match) > 2 else ""
            
            if armor_name and armor_name not in ['---', ':-']:
                armors.append({
                    'name': armor_name,
                    'type': armor_type,
                    'ca': ca,
                    'raw_data': match
                })
    
    print(f"✅ {len(armors)} armures trouvées dans les tableaux")
    for armor in armors[:5]:  # Afficher les 5 premières
        print(f"   - {armor['name']} ({armor['type']}) - CA: {armor['ca']}")
    
    return armors

def analyze_weapons():
    """Analyser les armes disponibles"""
    print("\n⚔️ ANALYSE DES ARMES")
    print("=" * 60)
    
    weapon_path = 'data/docs/armes/README.md'
    if not os.path.exists(weapon_path):
        print("❌ Fichier armes introuvable")
        return []
    
    with open(weapon_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher les tableaux d'armes
    weapon_patterns = [
        r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|',  # Tableau armes
    ]
    
    weapons = []
    
    # Extraire depuis les tableaux
    table_matches = re.findall(weapon_patterns[0], content)
    for match in table_matches:
        if 'Nom' not in match[0] and match[0].strip():  # Ignorer les en-têtes
            weapon_name = match[0].strip()
            damage = match[1].strip() if len(match) > 1 else ""
            properties = match[2].strip() if len(match) > 2 else ""
            
            if weapon_name and weapon_name not in ['---', ':-']:
                weapons.append({
                    'name': weapon_name,
                    'damage': damage,
                    'properties': properties,
                    'raw_data': match
                })
    
    print(f"✅ {len(weapons)} armes trouvées dans les tableaux")
    for weapon in weapons[:5]:  # Afficher les 5 premières
        print(f"   - {weapon['name']} - Dégâts: {weapon['damage']} - Propriétés: {weapon['properties'][:30]}...")
    
    return weapons

def analyze_equipment():
    """Analyser l'équipement d'aventurier"""
    print("\n🎒 ANALYSE DE L'ÉQUIPEMENT D'AVENTURIER")
    print("=" * 60)
    
    equipment_path = 'data/docs/equipement-d-aventurier/README.md'
    if not os.path.exists(equipment_path):
        print("❌ Fichier équipement introuvable")
        return []
    
    with open(equipment_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher les tableaux d'équipement
    equipment_patterns = [
        r'\|([^|]+)\|([^|]+)\|([^|]+)\|',  # Tableau équipement
        r'### ([^#\n]+)',  # Catégories d'équipement
    ]
    
    equipment = []
    categories = []
    
    # Extraire les catégories
    category_matches = re.findall(equipment_patterns[1], content)
    for match in category_matches:
        if match.strip() and len(match.strip()) > 3:
            categories.append(match.strip())
    
    # Extraire depuis les tableaux
    table_matches = re.findall(equipment_patterns[0], content)
    for match in table_matches:
        if 'Objet' not in match[0] and match[0].strip():  # Ignorer les en-têtes
            item_name = match[0].strip()
            cost = match[1].strip() if len(match) > 1 else ""
            weight = match[2].strip() if len(match) > 2 else ""
            
            if item_name and item_name not in ['---', ':-']:
                equipment.append({
                    'name': item_name,
                    'cost': cost,
                    'weight': weight,
                    'raw_data': match
                })
    
    print(f"✅ {len(categories)} catégories trouvées:")
    for cat in categories[:8]:
        print(f"   - {cat}")
    
    print(f"✅ {len(equipment)} objets d'équipement trouvés")
    for item in equipment[:5]:  # Afficher les 5 premiers
        print(f"   - {item['name']} - Coût: {item['cost']} - Poids: {item['weight']}")
    
    return equipment, categories

def analyze_class_proficiencies():
    """Analyser les maîtrises d'armures et d'armes par classe"""
    print("\n🎯 ANALYSE DES MAÎTRISES PAR CLASSE")
    print("=" * 60)
    
    classes = ['barbare', 'barde', 'clerc', 'druide', 'ensorceleur', 'guerrier', 
               'magicien', 'moine', 'paladin', 'rodeur', 'roublard', 'sorcier']
    
    proficiencies = {}
    
    for character_class in classes:
        class_path = f'data/docs/classes/{character_class}/README.md'
        if os.path.exists(class_path):
            with open(class_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chercher les maîtrises
            armor_prof = re.search(r'Armures?\s*:\s*([^\n]+)', content, re.IGNORECASE)
            weapon_prof = re.search(r'Armes?\s*:\s*([^\n]+)', content, re.IGNORECASE)
            
            proficiencies[character_class] = {
                'armors': armor_prof.group(1).strip() if armor_prof else "Aucune",
                'weapons': weapon_prof.group(1).strip() if weapon_prof else "Aucune"
            }
            
            print(f"   {character_class.upper()}:")
            print(f"      Armures: {proficiencies[character_class]['armors']}")
            print(f"      Armes: {proficiencies[character_class]['weapons'][:50]}...")
    
    return proficiencies

if __name__ == "__main__":
    print("🔍 ANALYSE COMPLÈTE DE L'ÉQUIPEMENT D&D")
    print("=" * 80)
    
    armors = analyze_armors()
    weapons = analyze_weapons()
    equipment, categories = analyze_equipment()
    proficiencies = analyze_class_proficiencies()
    
    print(f"\n📊 RÉSUMÉ")
    print("=" * 80)
    print(f"✅ Armures: {len(armors)}")
    print(f"✅ Armes: {len(weapons)}")
    print(f"✅ Équipement: {len(equipment)}")
    print(f"✅ Catégories: {len(categories)}")
    print(f"✅ Classes analysées: {len(proficiencies)}") 