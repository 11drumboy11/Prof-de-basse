#!/usr/bin/env python3
"""
🔧 CORRECTEUR D'URLs - Prof de Basse
Corrige les URLs 404 dans mega-search-index.json
"""

import json
from pathlib import Path
import re

def fix_all_urls():
    """Corrige toutes les URLs du mega-search-index.json"""
    
    print("🔧 CORRECTEUR D'URLs")
    print("="*60)
    
    # Charger le fichier
    index_file = Path('mega-search-index.json')
    
    if not index_file.exists():
        print("❌ mega-search-index.json introuvable")
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    resources = data.get('all_resources', data.get('resources', []))
    
    print(f"📊 {len(resources)} ressources à vérifier\n")
    
    # Statistiques
    stats = {
        'total': len(resources),
        'page_urls_fixed': 0,
        'mp3_urls_fixed': 0,
        'page_urls_removed': 0,
        'mp3_urls_removed': 0
    }
    
    # Construire un mapping des fichiers existants
    file_mapping = build_file_mapping()
    
    print("🔍 Analyse de la structure locale...")
    print(f"   Fichiers indexés: {sum(len(files) for files in file_mapping.values())}")
    print()
    
    # Corriger chaque ressource
    for i, res in enumerate(resources):
        if (i + 1) % 100 == 0:
            print(f"   Traitement: {i+1}/{len(resources)}...")
        
        # Corriger page_url
        page_url = res.get('page_url')
        if page_url:
            fixed_page_url = fix_page_url(page_url, res, file_mapping)
            if fixed_page_url != page_url:
                if fixed_page_url:
                    res['page_url'] = fixed_page_url
                    stats['page_urls_fixed'] += 1
                else:
                    res['page_url'] = None
                    stats['page_urls_removed'] += 1
        
        # Corriger mp3_url
        mp3_url = res.get('mp3_url')
        if mp3_url:
            fixed_mp3_url = fix_mp3_url(mp3_url, res, file_mapping)
            if fixed_mp3_url != mp3_url:
                if fixed_mp3_url:
                    res['mp3_url'] = fixed_mp3_url
                    stats['mp3_urls_fixed'] += 1
                else:
                    res['mp3_url'] = None
                    stats['mp3_urls_removed'] += 1
    
    # Sauvegarder
    if 'all_resources' in data:
        data['all_resources'] = resources
    else:
        data['resources'] = resources
    
    with open('mega-search-index.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Afficher les résultats
    print("\n" + "="*60)
    print("✅ CORRECTION TERMINÉE")
    print("="*60)
    print(f"📊 Total ressources: {stats['total']}")
    print(f"📄 Page URLs corrigées: {stats['page_urls_fixed']}")
    print(f"🎵 MP3 URLs corrigées: {stats['mp3_urls_fixed']}")
    print(f"❌ Page URLs invalides supprimées: {stats['page_urls_removed']}")
    print(f"❌ MP3 URLs invalides supprimées: {stats['mp3_urls_removed']}")
    print()
    print("💾 Fichier mega-search-index.json mis à jour")
    print()
    print("🚀 Prochaine étape: git add + commit + push")

def build_file_mapping():
    """Construit un mapping de tous les fichiers disponibles"""
    mapping = {
        'images': {},  # path -> fichier
        'mp3': {}      # path -> fichier
    }
    
    # Scanner les dossiers principaux
    base_dirs = ['Methodes', 'Theorie']
    
    for base_dir in base_dirs:
        base_path = Path(base_dir)
        if not base_path.exists():
            continue
        
        for method_dir in base_path.iterdir():
            if not method_dir.is_dir() or method_dir.name.startswith('.'):
                continue
            
            # Scanner assets/pages/ pour les images
            assets_pages = method_dir / 'assets' / 'pages'
            if assets_pages.exists():
                for img_file in assets_pages.glob('*'):
                    if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                        key = f"{base_dir}/{method_dir.name}"
                        if key not in mapping['images']:
                            mapping['images'][key] = []
                        mapping['images'][key].append(img_file.name)
            
            # Scanner pour les MP3
            for mp3_file in method_dir.rglob('*.mp3'):
                key = f"{base_dir}/{method_dir.name}"
                if key not in mapping['mp3']:
                    mapping['mp3'][key] = []
                rel_path = mp3_file.relative_to(method_dir)
                mapping['mp3'][key].append(str(rel_path))
    
    return mapping

def fix_page_url(url, resource, file_mapping):
    """Corrige une URL de page"""
    if not url:
        return None
    
    # Extraire les composants
    try:
        # Format attendu: https://11drumboy11.github.io/Prof-de-basse/Category/Method/assets/pages/file.png
        parts = url.split('/')
        
        if len(parts) < 8:
            return None
        
        # Extraire catégorie et méthode
        category = parts[4]  # Methodes ou Theorie
        method = parts[5]    # Nom de la méthode
        filename = parts[-1] # Nom du fichier
        
        # Décoder l'URL
        filename = filename.replace('%20', ' ')
        method = method.replace('%20', ' ')
        
        # Vérifier si le fichier existe
        key = f"{category}/{method}"
        
        if key in file_mapping['images']:
            if filename in file_mapping['images'][key]:
                # Reconstruire l'URL correcte
                safe_method = method.replace(' ', '%20')
                safe_filename = filename.replace(' ', '%20')
                return f"https://11drumboy11.github.io/Prof-de-basse/{category}/{safe_method}/assets/pages/{safe_filename}"
        
        # Essayer de trouver un fichier similaire
        page_num = resource.get('page_number')
        if page_num and key in file_mapping['images']:
            # Chercher page_XXX.png ou page_XXX.jpg
            for img in file_mapping['images'][key]:
                if f"page_{page_num:03d}" in img.lower() or f"page_{page_num:02d}" in img.lower():
                    safe_method = method.replace(' ', '%20')
                    safe_img = img.replace(' ', '%20')
                    return f"https://11drumboy11.github.io/Prof-de-basse/{category}/{safe_method}/assets/pages/{safe_img}"
        
        return None
        
    except Exception as e:
        return None

def fix_mp3_url(url, resource, file_mapping):
    """Corrige une URL MP3"""
    if not url:
        return None
    
    try:
        # Format attendu: https://11drumboy11.github.io/Prof-de-basse/Category/Method/file.mp3
        parts = url.split('/')
        
        if len(parts) < 6:
            return None
        
        category = parts[4]
        method = parts[5]
        filename = '/'.join(parts[6:])  # Peut avoir des sous-dossiers
        
        # Décoder
        filename = filename.replace('%20', ' ')
        method = method.replace('%20', ' ')
        
        # Vérifier
        key = f"{category}/{method}"
        
        if key in file_mapping['mp3']:
            if filename in file_mapping['mp3'][key]:
                # Reconstruire
                safe_method = method.replace(' ', '%20')
                safe_filename = filename.replace(' ', '%20')
                return f"https://11drumboy11.github.io/Prof-de-basse/{category}/{safe_method}/{safe_filename}"
        
        # Essayer de trouver un fichier similaire avec le track_number
        track_num = resource.get('track_number')
        if track_num and key in file_mapping['mp3']:
            for mp3 in file_mapping['mp3'][key]:
                # Chercher "Track XX.mp3" ou "XX.mp3"
                if f"Track {track_num:02d}" in mp3 or f"{track_num:02d}.mp3" in mp3:
                    safe_method = method.replace(' ', '%20')
                    safe_mp3 = mp3.replace(' ', '%20')
                    return f"https://11drumboy11.github.io/Prof-de-basse/{category}/{safe_method}/{safe_mp3}"
        
        return None
        
    except Exception as e:
        return None

if __name__ == '__main__':
    fix_all_urls()
