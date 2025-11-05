#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎸 Prof de Basse - Simple Musical Metadata Extractor
Version simplifiée pour GitHub Actions - Sans dépendances externes
"""

import re
import json
import os
from pathlib import Path

def extract_metadata_from_filename(filename):
    """Extrait métadonnées depuis nom de fichier"""
    meta = {}
    
    # Track number
    track_match = re.search(r'(?:Track|track)\s*(\d{1,3})', filename, re.IGNORECASE)
    if track_match:
        meta['track_number'] = int(track_match.group(1))
    
    # Tempo
    tempo_match = re.search(r'(\d{2,3})\s*(?:bpm|BPM)', filename, re.IGNORECASE)
    if tempo_match:
        meta['tempo'] = int(tempo_match.group(1))
    
    # Style
    styles = ['funk', 'jazz', 'rock', 'blues', 'disco', 'motown', 'fusion', 'latin', 'reggae']
    for style in styles:
        if style in filename.lower():
            meta['style'] = style
            break
    
    # Niveau (déduction basique)
    if 'track_number' in meta:
        track_num = meta['track_number']
        if track_num <= 15:
            meta['level'] = 'beginner'
        elif track_num <= 40:
            meta['level'] = 'intermediate'
        else:
            meta['level'] = 'advanced'
    
    return meta

def scan_mp3_files(repo_root):
    """Scanne tous les MP3"""
    mp3_data = {}
    mp3_count = 0
    
    print("🔍 Scanning MP3 files...")
    
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            if file.endswith('.mp3'):
                mp3_count += 1
                file_path = Path(root) / file
                rel_path = file_path.relative_to(repo_root)
                
                meta = extract_metadata_from_filename(file)
                meta['filename'] = file
                meta['path'] = str(rel_path)
                
                # URL GitHub Pages
                url_path = str(rel_path).replace('\\', '/')
                meta['url'] = f"https://11drumboy11.github.io/Prof-de-basse/{url_path}"
                
                mp3_data[str(rel_path)] = meta
    
    print(f"   ✅ Found {mp3_count} MP3 files")
    return mp3_data

def scan_pdf_files(repo_root):
    """Scanne tous les PDF"""
    pdf_data = {}
    pdf_count = 0
    
    print("📄 Scanning PDF files...")
    
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            if file.endswith('.pdf'):
                pdf_count += 1
                file_path = Path(root) / file
                rel_path = file_path.relative_to(repo_root)
                
                meta = extract_metadata_from_filename(file)
                meta['filename'] = file
                meta['path'] = str(rel_path)
                
                try:
                    size_mb = round(file_path.stat().st_size / (1024*1024), 2)
                    meta['size_mb'] = size_mb
                except:
                    meta['size_mb'] = 0
                
                pdf_data[str(rel_path)] = meta
    
    print(f"   ✅ Found {pdf_count} PDF files")
    return pdf_data

def load_json_files(repo_root):
    """Charge tous les JSON (OCR, etc.)"""
    json_data = {}
    json_count = 0
    
    print("📋 Loading JSON files...")
    
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            if file.endswith('.json') and file != 'package.json':
                try:
                    file_path = Path(root) / file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        json_data[str(file_path.relative_to(repo_root))] = data
                        json_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not load {file}: {e}")
    
    print(f"   ✅ Loaded {json_count} JSON files")
    return json_data

def generate_stats(mp3_data, pdf_data):
    """Génère statistiques globales"""
    stats = {
        'total_mp3': len(mp3_data),
        'total_pdf': len(pdf_data),
        'by_level': {},
        'by_style': {},
    }
    
    for meta in mp3_data.values():
        level = meta.get('level', 'unknown')
        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
        
        style = meta.get('style', 'unknown')
        stats['by_style'][style] = stats['by_style'].get(style, 0) + 1
    
    return stats

def main():
    """Fonction principale"""
    print("🎸 Prof de Basse - Musical Metadata Extractor")
    print("=" * 60)
    
    # Déterminer le root du repo
    repo_root = Path.cwd()
    print(f"📁 Repository root: {repo_root}")
    
    # Créer dossier output
    output_dir = repo_root / 'resources'
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📂 Output directory: {output_dir}\n")
    
    # Scanner les fichiers
    mp3_data = scan_mp3_files(repo_root)
    pdf_data = scan_pdf_files(repo_root)
    json_data = load_json_files(repo_root)
    
    # Générer stats
    print("📊 Generating statistics...")
    stats = generate_stats(mp3_data, pdf_data)
    print(f"   ✅ Stats generated")
    
    # Créer le mapping complet
    complete_map = {
        'metadata': {
            'version': '1.0.0',
            'generated_at': str(repo_root),
        },
        'mp3_index': mp3_data,
        'pdf_index': pdf_data,
        'json_index': json_data,
        'stats': stats,
    }
    
    # Exporter JSON
    output_file = output_dir / 'complete-resource-map.json'
    print(f"\n💾 Exporting to {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_map, f, indent=2, ensure_ascii=False)
        print("   ✅ Export successful!")
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        return 1
    
    # Exporter stats séparément
    stats_file = output_dir / 'stats.json'
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Stats exported to {stats_file}")
    except Exception as e:
        print(f"   ⚠️  Stats export failed: {e}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("🎉 Extraction complete!")
    print(f"   📊 {stats['total_mp3']} MP3 indexed")
    print(f"   📄 {stats['total_pdf']} PDF indexed")
    print(f"   📋 {len(json_data)} JSON loaded")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    exit(main())
