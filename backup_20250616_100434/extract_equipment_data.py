#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json

def extract_armors():
    """Extraire les armures depuis le fichier markdown"""
    armor_path = 'data/docs/armures/README.md'
    if not os.path.exists(armor_path):
        return []
    
    with open(armor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    armors = []
    
    # Pattern pour extraire les lignes du tableau d'armures
    # Chercher entre |**Armures légères**| et |**Bouclier**|
    table_pattern = r'\|Armure\|Prix\|Classe d\'armure.*?\|\*\*Bouclier\*\*\|\|\|\|\|\|\|Bouclier\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|'
    
    # Pattern plus simple pour chaque ligne d'armure
    armor_lines = re.findall(r'\|([^|*]+)\|([^|]+)\|([^|]+)\|([^|]*)\|([^|]*)\|([^|]+)\|', content)
    
    for line in armor_lines:
        name = line[0].strip()
        price = line[1].strip()
        ca = line[2].strip()
        force = line[3].strip()
        stealth = line[4].strip()
        weight = line[5].strip()
        
        # Ignorer les en-têtes et lignes vides
        if (name and name not in ['Armure', ':-', '**Armures légères**', '**Armures intermédiaires**', '**Armures lourdes**', '**Bouclier**'] 
            and not name.startswith('**') and price != ':-'):
            
            # Déterminer le type d'armure
            armor_type = "légère"
            if "intermédiaire" in content[content.find(name)-200:content.find(name)]:
                armor_type = "intermédiaire"
            elif "lourde" in content[content.find(name)-200:content.find(name)]:
                armor_type = "lourde"
            elif name == "Bouclier":
                armor_type = "bouclier"
            
            armors.append({
                'name': name,
                'type': armor_type,
                'price': price,
                'ca': ca,
                'force_req': force if force and force != '-' else None,
                'stealth_disadvantage': stealth == 'Désavantage',
                'weight': weight
            })
    
    return armors

def extract_weapons():
    """Extraire les armes depuis le fichier markdown"""
    weapon_path = 'data/docs/armes/README.md'
    if not os.path.exists(weapon_path):
        return []
    
    with open(weapon_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    weapons = []
    
    # Pattern pour extraire les lignes du tableau d'armes
    weapon_lines = re.findall(r'\|([^|*]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]*)\|', content)
    
    current_category = ""
    
    for line in weapon_lines:
        name = line[0].strip()
        price = line[1].strip()
        damage = line[2].strip()
        weight = line[3].strip()
        properties = line[4].strip()
        
        # Détecter les catégories
        if name.startswith('**') and name.endswith('**'):
            current_category = name.replace('**', '')
            continue
        
        # Ignorer les en-têtes et lignes vides
        if (name and name not in ['Nom', ':-', ''] and price != ':-' and not name.startswith('**')):
            
            # Déterminer si c'est une arme de guerre ou courante
            weapon_type = "courante" if "courante" in current_category else "guerre"
            
            # Déterminer si c'est corps-à-corps ou à distance
            weapon_range = "corps-à-corps" if "corps-à-corps" in current_category else "distance"
            
            weapons.append({
                'name': name,
                'category': current_category,
                'type': weapon_type,
                'range': weapon_range,
                'price': price,
                'damage': damage,
                'weight': weight,
                'properties': properties
            })
    
    return weapons

def extract_equipment():
    """Extraire l'équipement d'aventurier"""
    equipment_path = 'data/docs/equipement-d-aventurier/README.md'
    if not os.path.exists(equipment_path):
        return []
    
    with open(equipment_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    equipment = []
    
    # Pattern pour extraire les lignes des tableaux d'équipement
    equipment_lines = re.findall(r'\|([^|*]+)\|([^|]+)\|([^|]*)\|', content)
    
    for line in equipment_lines:
        name = line[0].strip()
        price = line[1].strip()
        weight = line[2].strip()
        
        # Ignorer les en-têtes et lignes vides
        if (name and name not in ['Objet', ':-', ''] and price != ':-' and not name.startswith('**')):
            # Nettoyer le nom (supprimer le markdown)
            clean_name = re.sub(r'\*\*([^*]+)\*\*', r'\1', name)
            
            equipment.append({
                'name': clean_name,
                'price': price,
                'weight': weight if weight and weight != '-' else '0'
            })
    
    return equipment

def extract_class_proficiencies():
    """Extraire les maîtrises par classe"""
    classes = ['barbare', 'barde', 'clerc', 'druide', 'ensorceleur', 'guerrier', 
               'magicien', 'moine', 'paladin', 'rodeur', 'roublard', 'sorcier']
    
    proficiencies = {}
    
    for character_class in classes:
        class_path = f'data/docs/classes/{character_class}/README.md'
        if os.path.exists(class_path):
            with open(class_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chercher les maîtrises dans la section des aptitudes de classe
            armor_match = re.search(r'\*\*Armures\*\*\s*:\s*([^\n]+)', content, re.IGNORECASE)
            weapon_match = re.search(r'\*\*Armes\*\*\s*:\s*([^\n]+)', content, re.IGNORECASE)
            
            proficiencies[character_class] = {
                'armors': armor_match.group(1).strip() if armor_match else "aucune",
                'weapons': weapon_match.group(1).strip() if weapon_match else "aucune"
            }
    
    return proficiencies

def save_equipment_data():
    """Sauvegarder toutes les données d'équipement"""
    print("🔍 EXTRACTION DES DONNÉES D'ÉQUIPEMENT")
    print("=" * 60)
    
    # Extraire toutes les données
    armors = extract_armors()
    weapons = extract_weapons()
    equipment = extract_equipment()
    proficiencies = extract_class_proficiencies()
    
    # Créer la structure de données complète
    equipment_data = {
        'armors': armors,
        'weapons': weapons,
        'equipment': equipment,
        'proficiencies': proficiencies
    }
    
    # Sauvegarder en JSON
    with open('equipment_data.json', 'w', encoding='utf-8') as f:
        json.dump(equipment_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(armors)} armures extraites")
    print(f"✅ {len(weapons)} armes extraites")
    print(f"✅ {len(equipment)} objets d'équipement extraits")
    print(f"✅ {len(proficiencies)} classes avec maîtrises")
    
    # Afficher quelques exemples
    print(f"\n📋 EXEMPLES D'ARMURES:")
    for armor in armors[:5]:
        print(f"   - {armor['name']} ({armor['type']}) - CA: {armor['ca']} - Prix: {armor['price']}")
    
    print(f"\n⚔️ EXEMPLES D'ARMES:")
    for weapon in weapons[:5]:
        print(f"   - {weapon['name']} ({weapon['type']}, {weapon['range']}) - Dégâts: {weapon['damage']}")
    
    print(f"\n🎒 EXEMPLES D'ÉQUIPEMENT:")
    for item in equipment[:5]:
        print(f"   - {item['name']} - Prix: {item['price']} - Poids: {item['weight']}")
    
    return equipment_data

if __name__ == "__main__":
    data = save_equipment_data()
    print(f"\n✅ Données sauvegardées dans equipment_data.json") 