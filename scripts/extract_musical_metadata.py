#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎸 Prof de Basse - Ultimate Musical Metadata Extractor
Version FINALE avec support Real Books JSON
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
    styles = ['funk', 'jazz', 'rock', 'blues', 'disco', 'motown', 'fusion', 'latin', 'reggae', 'soul']
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
                meta['path'] = str(rel_path).replace('\\', '/')
                
                # Détecter la méthode depuis le chemin
                path_parts = rel_path.parts
                if len(path_parts) > 1:
                    meta['method'] = path_parts[1] if path_parts[0] == 'Methodes' else path_parts[0]
                
                # URL GitHub Pages
                url_path = str(rel_path).replace('\\', '/')
                # Encoder les espaces
                url_path_encoded = url_path.replace(' ', '%20').replace('&', '%26')
                meta['url'] = f"https://11drumboy11.github.io/Prof-de-basse/{url_path_encoded}"
                
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
                meta['path'] = str(rel_path).replace('\\', '/')
                
                try:
                    size_mb = round(file_path.stat().st_size / (1024*1024), 2)
                    meta['size_mb'] = size_mb
                except:
                    meta['size_mb'] = 0
                
                pdf_data[str(rel_path)] = meta
    
    print(f"   ✅ Found {pdf_count} PDF files")
    return pdf_data

def load_realbook_json_files(repo_root):
    """Charge tous les JSON de Real Books (songs_index.json, exercises.json)"""
    realbook_data = {}
    json_count = 0
    
    print("📋 Loading Real Book JSON files...")
    
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            # Chercher spécifiquement les JSON de Real Books
            if file in ['songs_index.json', 'exercises.json', 'index.json']:
                try:
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(repo_root)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Détecter le nom du Real Book depuis le chemin
                        realbook_name = "Unknown"
                        path_parts = rel_path.parts
                        if 'Realbook' in path_parts or 'Reabook' in path_parts:
                            for i, part in enumerate(path_parts):
                                if 'Realbook' in part or 'Reabook' in part:
                                    realbook_name = path_parts[i+1] if i+1 < len(path_parts) else part
                                    break
                        
                        # Extraire les morceaux
                        songs = []
                        for song_id, song_data in data.items():
                            if isinstance(song_data, dict) and 'title' in song_data:
                                song_info = {
                                    'id': song_id,
                                    'title': song_data.get('title', ''),
                                    'composer': song_data.get('composer'),
                                    'page': song_data.get('page'),
                                    'file': song_data.get('file', ''),
                                    'format': song_data.get('format', ''),
                                    'realbook': realbook_name,
                                }
                                
                                # Construire URL vers PNG
                                if song_info['file']:
                                    parent_dir = str(rel_path.parent).replace('\\', '/')
                                    assets_path = f"{parent_dir}/assets/{song_info['file']}"
                                    assets_path_encoded = assets_path.replace(' ', '%20')
                                    song_info['png_url'] = f"https://11drumboy11.github.io/Prof-de-basse/{assets_path_encoded}"
                                
                                songs.append(song_info)
                        
                        realbook_data[str(rel_path)] = {
                            'path': str(rel_path).replace('\\', '/'),
                            'realbook_name': realbook_name,
                            'total_songs': len(songs),
                            'songs': songs,
                        }
                        
                        json_count += 1
                        print(f"   ✅ Loaded {realbook_name}: {len(songs)} songs")
                        
                except Exception as e:
                    print(f"   ⚠️  Could not load {file}: {e}")
    
    print(f"   ✅ Total: {json_count} Real Book JSON files loaded")
    return realbook_data

def generate_stats(mp3_data, pdf_data, realbook_data):
    """Génère statistiques globales"""
    stats = {
        'total_mp3': len(mp3_data),
        'total_pdf': len(pdf_data),
        'total_realbooks': len(realbook_data),
        'total_songs': sum(rb['total_songs'] for rb in realbook_data.values()),
        'by_method': {},
        'by_level': {},
        'by_style': {},
        'realbooks': {},
    }
    
    # Stats MP3
    for meta in mp3_data.values():
        method = meta.get('method', 'unknown')
        stats['by_method'][method] = stats['by_method'].get(method, 0) + 1
        
        level = meta.get('level', 'unknown')
        stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
        
        style = meta.get('style', 'unknown')
        stats['by_style'][style] = stats['by_style'].get(style, 0) + 1
    
    # Stats Real Books
    for rb_path, rb_data in realbook_data.items():
        rb_name = rb_data['realbook_name']
        stats['realbooks'][rb_name] = {
            'total_songs': rb_data['total_songs'],
            'path': rb_data['path'],
        }
    
    return stats

def create_quick_reference(mp3_data, realbook_data):
    """Crée une référence rapide pour le GPT"""
    quick_ref = {
        'funk_beginner': [],
        'funk_intermediate': [],
        'jazz_standards': [],
    }
    
    # MP3 Funk
    for path, meta in mp3_data.items():
        if meta.get('style') == 'funk':
            if meta.get('level') == 'beginner':
                quick_ref['funk_beginner'].append({
                    'track': meta.get('track_number'),
                    'url': meta.get('url'),
                    'tempo': meta.get('tempo'),
                })
            elif meta.get('level') == 'intermediate':
                quick_ref['funk_intermediate'].append({
                    'track': meta.get('track_number'),
                    'url': meta.get('url'),
                    'tempo': meta.get('tempo'),
                })
    
    # Real Book Jazz (top 20 standards)
    for rb_path, rb_data in realbook_data.items():
        for song in rb_data['songs'][:20]:  # Top 20
            if song['title'] and song['page']:
                quick_ref['jazz_standards'].append({
                    'title': song['title'],
                    'composer': song['composer'],
                    'page': song['page'],
                    'png_url': song.get('png_url'),
                })
    
    return quick_ref

def main():
    """Fonction principale"""
    print("🎸 Prof de Basse - Ultimate Musical Metadata Extractor")
    print("=" * 70)
    
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
    realbook_data = load_realbook_json_files(repo_root)
    
    # Générer stats
    print("\n📊 Generating statistics...")
    stats = generate_stats(mp3_data, pdf_data, realbook_data)
    print(f"   ✅ Stats generated")
    
    # Générer référence rapide
    print("⚡ Generating quick reference...")
    quick_ref = create_quick_reference(mp3_data, realbook_data)
    print(f"   ✅ Quick reference generated")
    
    # Créer le mapping complet
    complete_map = {
        'metadata': {
            'version': '2.0.0',
            'generated_at': str(repo_root),
        },
        'mp3_index': mp3_data,
        'pdf_index': pdf_data,
        'realbook_index': realbook_data,
        'stats': stats,
        'quick_reference': quick_ref,
    }
    
    # Exporter JSON complet
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
    print("\n" + "=" * 70)
    print("🎉 Extraction complete!")
    print(f"   📊 {stats['total_mp3']} MP3 indexed")
    print(f"   📄 {stats['total_pdf']} PDF indexed")
    print(f"   📚 {stats['total_realbooks']} Real Books loaded")
    print(f"   🎵 {stats['total_songs']} jazz standards indexed")
    
    if stats['realbooks']:
        print("\n   📖 Real Books:")
        for rb_name, rb_stats in stats['realbooks'].items():
            print(f"      • {rb_name}: {rb_stats['total_songs']} songs")
    
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    exit(main())
