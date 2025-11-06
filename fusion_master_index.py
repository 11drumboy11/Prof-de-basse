#!/usr/bin/env python3
"""
SCRIPT FINAL : Fusion de tous les songs_index.json en unified_index.json
Compatible avec la structure automatique OCR déjà en place
"""

import json
import os
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

def find_all_songs_indexes(base_path='.'):
    """Trouve tous les songs_index.json dans le repo"""
    indexes = []
    base_path = Path(base_path).resolve()
    
    print("🔍 Recherche de tous les songs_index.json...")
    
    for root, dirs, files in os.walk(base_path):
        # Ignorer les dossiers cachés et .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        if 'songs_index.json' in files:
            index_path = Path(root) / 'songs_index.json'
            
            # Calculer le path relatif depuis la racine du repo
            try:
                relative_dir = Path(root).relative_to(base_path)
            except ValueError:
                continue
            
            # Extraire le nom de la méthode/livre
            parts = relative_dir.parts
            method_name = "Unknown"
            
            if len(parts) > 0:
                # Dernier dossier = nom de la méthode
                method_name = parts[-1].replace('_with_index', '')
            
            print(f"  ✅ {relative_dir}")
            
            indexes.append({
                'path': index_path,
                'relative_dir': str(relative_dir).replace('\\', '/'),
                'method_name': method_name
            })
    
    print(f"\n📊 Total: {len(indexes)} fichiers songs_index.json trouvés\n")
    return indexes


def normalize_url(file_path, base_dir):
    """
    Construit l'URL complète depuis la racine du site
    
    Input: 
        file_path = "page_0123.jpg"
        base_dir = "Methodes/Reabook/Realbook Bass F_with_index"
    
    Output:
        "Methodes/Reabook/Realbook Bass F_with_index/assets/page_0123.jpg"
    """
    # Le fichier est TOUJOURS dans assets/
    if not file_path.startswith('assets/'):
        file_path = f"assets/{file_path}"
    
    # Construire le path complet
    full_path = f"{base_dir}/{file_path}"
    
    # Normaliser les slashes
    full_path = full_path.replace('\\', '/')
    
    return full_path


def load_and_merge_index(index_info):
    """Charge un songs_index.json et transforme en format unifié"""
    index_path = index_info['path']
    relative_dir = index_info['relative_dir']
    method_name = index_info['method_name']
    
    # Charger le JSON
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ⚠️  Erreur lecture {index_path}: {e}")
        return []
    
    resources = []
    
    # data est un dict avec des clés uniques
    for key, item in data.items():
        # Extraire les informations
        title = item.get('title', 'Unknown')
        composer = item.get('composer')
        page = item.get('page')
        file_name = item.get('file', '')
        file_format = item.get('format', 'jpg')
        
        # Données OCR optionnelles
        confidence = item.get('confidence')
        ocr_raw = item.get('ocr_raw')
        
        # Construire l'URL complète
        url = normalize_url(file_name, relative_dir)
        
        # Créer la ressource unifiée
        resource = {
            "type": "image",
            "title": title,
            "url": url,
            "metadata": {
                "method": method_name,
                "page": page,
                "filename": file_name,
                "format": file_format
            }
        }
        
        # Ajouter compositeur si présent
        if composer:
            resource["metadata"]["composer"] = composer
        
        # Ajouter données OCR si présentes
        if confidence is not None:
            resource["metadata"]["ocr_confidence"] = confidence
        if ocr_raw:
            resource["metadata"]["ocr_text"] = ocr_raw.strip()
        
        resources.append(resource)
    
    print(f"    📦 {len(resources)} ressources extraites")
    return resources


def generate_unified_index(output_file='unified_index.json'):
    """
    Génère l'index unifié final
    """
    print("=" * 70)
    print("🎸 FUSION MASTER INDEX - Prof de Basse")
    print("=" * 70)
    print()
    
    # 1. Trouver tous les songs_index.json
    all_indexes = find_all_songs_indexes()
    
    if not all_indexes:
        print("❌ Aucun songs_index.json trouvé!")
        return
    
    # 2. Fusionner tous les indexes
    print("🔄 Fusion en cours...\n")
    all_resources = []
    
    for index_info in all_indexes:
        print(f"📖 {index_info['method_name']}")
        resources = load_and_merge_index(index_info)
        all_resources.extend(resources)
        print()
    
    # 3. Trier par méthode puis par page
    all_resources.sort(key=lambda x: (
        x['metadata'].get('method', ''),
        x['metadata'].get('page', 0)
    ))
    
    # 4. Créer l'index final
    unified_index = {
        "generated_at": datetime.now().isoformat(),
        "total_resources": len(all_resources),
        "total_methods": len(all_indexes),
        "resources": all_resources
    }
    
    # 5. Sauvegarder
    print("=" * 70)
    print(f"💾 Sauvegarde de {len(all_resources)} ressources...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unified_index, f, indent=2, ensure_ascii=False)
    
    # 6. Statistiques finales
    print()
    print("✅ TERMINÉ!")
    print("=" * 70)
    print()
    print("📊 STATISTIQUES:")
    print(f"   • Total ressources: {len(all_resources)}")
    print(f"   • Total méthodes: {len(all_indexes)}")
    
    # Stats par méthode
    methods_count = {}
    for r in all_resources:
        m = r['metadata'].get('method', 'Unknown')
        methods_count[m] = methods_count.get(m, 0) + 1
    
    print()
    print("📚 Par méthode:")
    for method, count in sorted(methods_count.items()):
        print(f"   • {method}: {count} pages")
    
    print()
    print(f"📁 Fichier généré: {output_file}")
    print()
    print("=" * 70)
    
    return unified_index


if __name__ == '__main__':
    # Générer l'index unifié
    generate_unified_index()
    
    print()
    print("🎯 PROCHAINES ÉTAPES:")
    print("1. Vérifie le fichier unified_index.json")
    print("2. Teste une URL:")
    print("   https://11drumboy11.github.io/Prof-de-basse/[URL du JSON]")
    print("3. Commit + Push vers GitHub")
    print("4. Attends 2-3 min le déploiement")
    print("5. Teste advanced-search.html")
