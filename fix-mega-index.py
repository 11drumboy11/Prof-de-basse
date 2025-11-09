#!/usr/bin/env python3
"""
🔧 CORRECTEUR DE FORMAT mega-search-index.json
Adapte le format généré au format attendu par le site
"""

import json
from pathlib import Path

def fix_mega_index():
    """Corrige le format du mega-search-index.json"""
    
    print("🔧 Correction du format mega-search-index.json...")
    
    # Charger le fichier actuel
    index_file = Path('mega-search-index.json')
    
    if not index_file.exists():
        print("❌ Fichier mega-search-index.json introuvable")
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Format actuel détecté:")
    print(f"   - Clés principales: {list(data.keys())}")
    
    # Vérifier si déjà au bon format
    if 'all_resources' in data:
        print("✅ Le fichier est déjà au bon format !")
        return
    
    # Créer le nouveau format
    print("\n🔄 Conversion vers le format attendu par le site...")
    
    fixed_data = {
        "metadata": data.get("metadata", {}),
        "all_resources": data.get("resources", []),
        "categories": data.get("categories", {}),
        "search_index": data.get("search_index", {})
    }
    
    # Ajouter des champs compatibles
    fixed_data["total_resources"] = len(fixed_data["all_resources"])
    fixed_data["version"] = "3.0.0"
    
    # Sauvegarder
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Fichier corrigé !")
    print(f"   - Total ressources: {fixed_data['total_resources']}")
    print(f"   - Catégories: {len(fixed_data['categories'])}")
    print(f"   - Format: all_resources (compatible site)")
    
    # Afficher aperçu
    if fixed_data['all_resources']:
        first = fixed_data['all_resources'][0]
        print(f"\n📄 Aperçu première ressource:")
        print(f"   - Titre: {first.get('title', 'N/A')}")
        print(f"   - Méthode: {first.get('method_name', 'N/A')}")
        print(f"   - Catégorie: {first.get('category', 'N/A')}")

if __name__ == '__main__':
    fix_mega_index()
