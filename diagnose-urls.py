#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC URLs 404
Analyse le mega-search-index.json et corrige les URLs
"""

import json
from pathlib import Path
import re

def diagnose_urls():
    """Diagnostique les URLs dans mega-search-index.json"""
    
    print("🔍 DIAGNOSTIC DES URLs...")
    print("="*60)
    
    # Charger le fichier
    index_file = Path('mega-search-index.json')
    
    if not index_file.exists():
        print("❌ mega-search-index.json introuvable")
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    resources = data.get('all_resources', data.get('resources', []))
    
    if not resources:
        print("❌ Aucune ressource trouvée")
        return
    
    print(f"📊 {len(resources)} ressources trouvées\n")
    
    # Analyser les 10 premières URLs
    print("🔗 EXEMPLES D'URLs GÉNÉRÉES:")
    print("-"*60)
    
    for i, res in enumerate(resources[:10]):
        print(f"\n{i+1}. {res.get('title', 'Sans titre')}")
        print(f"   Méthode: {res.get('method_name')}")
        print(f"   Catégorie: {res.get('category')}")
        
        page_url = res.get('page_url')
        mp3_url = res.get('mp3_url')
        
        if page_url:
            print(f"   📄 Page: {page_url}")
        if mp3_url:
            print(f"   🎵 MP3:  {mp3_url}")
    
    # Analyser la structure des URLs
    print("\n" + "="*60)
    print("📊 ANALYSE DE LA STRUCTURE")
    print("="*60)
    
    url_patterns = {}
    
    for res in resources:
        page_url = res.get('page_url', '')
        if page_url:
            # Extraire le pattern
            parts = page_url.split('/')
            if len(parts) > 5:
                pattern = '/'.join(parts[3:6])  # Prendre Methodes/Nom/assets
                if pattern not in url_patterns:
                    url_patterns[pattern] = 0
                url_patterns[pattern] += 1
    
    print("\n🗂️  Patterns d'URLs détectés:")
    for pattern, count in sorted(url_patterns.items(), key=lambda x: -x[1]):
        print(f"   {count:4d}x  {pattern}")
    
    # Suggestions de correction
    print("\n" + "="*60)
    print("💡 SUGGESTIONS DE CORRECTION")
    print("="*60)
    
    # Vérifier si les chemins existent localement
    print("\n🔍 Vérification de la structure locale:")
    
    base_dirs = ['Methodes', 'Theorie', 'Pratique', 'Arpeges', 'Harmonie']
    
    for base_dir in base_dirs:
        path = Path(base_dir)
        if path.exists():
            subdirs = [d for d in path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            print(f"\n📂 {base_dir}/ ({len(subdirs)} sous-dossiers)")
            
            for subdir in subdirs[:5]:  # Montrer les 5 premiers
                assets = subdir / 'assets' / 'pages'
                has_assets = assets.exists()
                
                # Compter les images
                img_count = 0
                if has_assets:
                    img_count = len(list(assets.glob('*.png'))) + len(list(assets.glob('*.jpg')))
                
                status = "✅" if has_assets else "❌"
                print(f"   {status} {subdir.name}")
                if has_assets:
                    print(f"      → {img_count} images dans assets/pages/")
    
    # Proposer une correction
    print("\n" + "="*60)
    print("🔧 CORRECTION AUTOMATIQUE")
    print("="*60)
    
    correction_needed = input("\nVoulez-vous corriger les URLs automatiquement? (y/N) ")
    
    if correction_needed.lower() == 'y':
        fix_urls(data, resources)

def fix_urls(data, resources):
    """Corrige les URLs"""
    
    print("\n🔧 Correction des URLs en cours...")
    
    fixed_count = 0
    
    for res in resources:
        page_url = res.get('page_url', '')
        
        if page_url:
            # Corriger les doubles slashes
            page_url = re.sub(r'/+', '/', page_url)
            page_url = page_url.replace('https:/', 'https://')
            
            # Corriger les espaces mal encodés
            page_url = page_url.replace('%20', ' ').replace(' ', '%20')
            
            if page_url != res.get('page_url'):
                res['page_url'] = page_url
                fixed_count += 1
        
        mp3_url = res.get('mp3_url')
        if mp3_url:
            # Corriger les doubles slashes
            mp3_url = re.sub(r'/+', '/', mp3_url)
            mp3_url = mp3_url.replace('https:/', 'https://')
            
            # Corriger les espaces mal encodés
            mp3_url = mp3_url.replace('%20', ' ').replace(' ', '%20')
            
            if mp3_url != res.get('mp3_url'):
                res['mp3_url'] = mp3_url
                fixed_count += 1
    
    # Sauvegarder
    if 'all_resources' in data:
        data['all_resources'] = resources
    else:
        data['resources'] = resources
    
    with open('mega-search-index.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {fixed_count} URLs corrigées")
    print(f"💾 mega-search-index.json mis à jour")

if __name__ == '__main__':
    diagnose_urls()
