#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORRECTEUR songs_index.json v1.0
=================================
Convertit un songs_index.json mal formaté en format compatible avec le mega moteur.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = "songs_index.json"  # Fichier à corriger
OUTPUT_FILE = "songs_index_corrected.json"  # Fichier corrigé
METHOD_NAME = "'70s Funk & Disco Bass"

# ============================================
# PATTERNS
# ============================================

TRACK_PATTERN = re.compile(r'(?:Track|Pattern)\s*(\d+)', re.IGNORECASE)
PAGE_PATTERN = re.compile(r'(?:Page|P\.?|Pg\.?)\s*(\d+)', re.IGNORECASE)
TONALITY_PATTERN = re.compile(r'\b([A-G][#b]?\s*(?:maj|min|M|m|Δ|°|ø)?)\b', re.IGNORECASE)

# ============================================
# FONCTIONS
# ============================================

def extract_track_number(text):
    """Extrait le numéro de track/pattern."""
    if not text:
        return None
    match = TRACK_PATTERN.search(text)
    if match:
        return int(match.group(1))
    return None

def extract_page_number(text, fallback_page=None):
    """Extrait le numéro de page."""
    if not text:
        return fallback_page
    match = PAGE_PATTERN.search(text)
    if match:
        return int(match.group(1))
    return fallback_page

def extract_tonality(text):
    """Extrait la tonalité."""
    if not text:
        return None
    match = TONALITY_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return None

def extract_techniques(text):
    """Détecte les techniques mentionnées."""
    if not text:
        return []
    
    techniques = []
    text_lower = text.lower()
    
    keywords = {
        'funk': 'Funk',
        'disco': 'Disco',
        'slap': 'Slap',
        'pattern': 'Pattern',
        'ghost': 'Ghost Notes',
        'hammer': 'Hammer-on',
        'pull': 'Pull-off'
    }
    
    for keyword, technique in keywords.items():
        if keyword in text_lower and technique not in techniques:
            techniques.append(technique)
    
    return techniques

def convert_to_proper_format(old_data):
    """Convertit le format incorrect en format correct."""
    
    songs = []
    song_id = 1
    
    for key, item in old_data.items():
        # Skip si pas assez de données
        if not isinstance(item, dict):
            continue
        
        title = item.get('title', f'Page {item.get("page", "?")}')
        page_num = item.get('page')
        file_name = item.get('file', '')
        
        # Extraction des métadonnées
        track_num = extract_track_number(title)
        tonalite = extract_tonality(title)
        techniques = extract_techniques(title)
        
        # Construction de l'URL de la page
        if file_name:
            page_url = f"assets/pages/{file_name}"
        else:
            page_url = None
        
        # URL MP3 (basée sur le numéro de track si détecté)
        mp3_url = None
        if track_num:
            # Format: Track 01.mp3 à Track 99.mp3
            mp3_url = f"Track {track_num:02d}.mp3"
        
        # Créer l'objet song
        song = {
            "id": song_id,
            "title": title.strip(),
            "tonalite": tonalite,
            "track_number": track_num,
            "page_number": page_num,
            "page_url": page_url,
            "mp3_url": mp3_url,
            "techniques": techniques,
            "composer": item.get('composer'),
            "confidence": item.get('confidence'),
            "ocr_raw": item.get('ocr_raw', ''),
            "format": item.get('format', 'jpg')
        }
        
        songs.append(song)
        song_id += 1
    
    # Trier par page
    songs.sort(key=lambda x: x['page_number'] if x['page_number'] else 999)
    
    return songs

def create_proper_index(songs):
    """Crée un index au format correct."""
    
    # Compter les MP3 disponibles
    mp3_count = sum(1 for s in songs if s['mp3_url'])
    
    return {
        "metadata": {
            "method_name": METHOD_NAME,
            "total_songs": len(songs),
            "has_mp3": mp3_count > 0,
            "mp3_count": mp3_count,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        "songs": songs
    }

# ============================================
# MAIN
# ============================================

def main():
    print("\n" + "="*60)
    print("🔧 CORRECTEUR songs_index.json v1.0")
    print("="*60 + "\n")
    
    # 1. Charger l'ancien fichier
    print(f"📖 Lecture de {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        print(f"✅ Chargé: {len(old_data)} entrées\n")
    except FileNotFoundError:
        print(f"❌ Fichier {INPUT_FILE} introuvable")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON: {e}")
        return
    
    # 2. Convertir au bon format
    print("🔄 Conversion au format correct...")
    songs = convert_to_proper_format(old_data)
    print(f"✅ {len(songs)} songs converties\n")
    
    # 3. Créer l'index final
    print("📦 Création de l'index final...")
    final_index = create_proper_index(songs)
    
    # 4. Statistiques
    print("\n📊 STATISTIQUES:")
    print(f"   - Total songs: {final_index['metadata']['total_songs']}")
    print(f"   - Songs avec MP3: {final_index['metadata']['mp3_count']}")
    print(f"   - Songs avec tonalité: {sum(1 for s in songs if s['tonalite'])}")
    print(f"   - Songs avec techniques: {sum(1 for s in songs if s['techniques'])}")
    
    # 5. Sauvegarder
    print(f"\n💾 Sauvegarde dans {OUTPUT_FILE}...")
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_index, f, ensure_ascii=False, indent=2)
        print(f"✅ SUCCÈS ! Fichier créé: {OUTPUT_FILE}\n")
        
        # 6. Instructions
        print("📋 PROCHAINES ÉTAPES:")
        print(f"   1. Vérifie {OUTPUT_FILE}")
        print(f"   2. Si OK, remplace l'ancien: mv {OUTPUT_FILE} {INPUT_FILE}")
        print(f"   3. Relance fusion-ultimate-v4.py\n")
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

if __name__ == "__main__":
    main()
