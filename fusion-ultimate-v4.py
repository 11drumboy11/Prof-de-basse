#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FUSION ULTIMATE v4.0
====================
Script de fusion automatique de tous les index songs_index.json
avec enrichissement OCR pour les assets manquants.

Auteur: Prof de Basse System
Date: Novembre 2025
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

BASE_DIR = Path(__file__).parent
METHODES_DIR = BASE_DIR / "Methodes"
OUTPUT_FILE = BASE_DIR / "mega-search-index.json"
SEARCH_INDEX_OCR = BASE_DIR / "search_index_ocr.json"

# Patterns pour extraction
TONALITY_PATTERN = re.compile(r'\b([A-G][#b]?\s*(?:maj|min|M|m|Δ|°|ø)?)(?:\s|$)', re.IGNORECASE)
TRACK_PATTERN = re.compile(r'(?:Track|Piste|Exercise|Ex\.?)\s*(\d+)', re.IGNORECASE)
PAGE_PATTERN = re.compile(r'(?:Page|P\.?|Pg\.?)\s*(\d+)', re.IGNORECASE)

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def extract_tonality(text):
    """Extrait la tonalité d'un texte."""
    if not text:
        return None
    
    match = TONALITY_PATTERN.search(text)
    if match:
        tonality = match.group(1).strip()
        # Normalisation
        tonality = tonality.replace('maj', 'M').replace('min', 'm')
        return tonality
    return None

def extract_track_number(text):
    """Extrait le numéro de track."""
    if not text:
        return None
    
    match = TRACK_PATTERN.search(text)
    if match:
        return int(match.group(1))
    return None

def extract_page_number(text):
    """Extrait le numéro de page."""
    if not text:
        return None
    
    match = PAGE_PATTERN.search(text)
    if match:
        return int(match.group(1))
    return None

def extract_techniques(text):
    """Extrait les techniques mentionnées."""
    if not text:
        return []
    
    techniques = []
    keywords = {
        'arpège': 'Arpège',
        'arpeggio': 'Arpège',
        'slap': 'Slap',
        'ghost': 'Ghost Notes',
        'walking': 'Walking Bass',
        'hammer': 'Hammer-on',
        'pull': 'Pull-off',
        'slide': 'Slide',
        'bend': 'Bend',
        'tapping': 'Tapping',
        'harmonics': 'Harmoniques',
        'palm mute': 'Palm Mute',
        'fingerstyle': 'Fingerstyle',
        'pick': 'Médiator'
    }
    
    text_lower = text.lower()
    for keyword, technique in keywords.items():
        if keyword in text_lower:
            if technique not in techniques:
                techniques.append(technique)
    
    return techniques

def normalize_url(url, method_name):
    """Normalise une URL pour GitHub Pages."""
    if not url:
        return None
    
    # Si c'est déjà une URL complète
    if url.startswith('http'):
        return url
    
    # Si c'est un chemin relatif
    base_url = "https://11drumboy11.github.io/Prof-de-basse/"
    
    # Nettoyer le chemin
    url = url.replace('\\', '/')
    if url.startswith('./'):
        url = url[2:]
    if url.startswith('../'):
        url = url[3:]
    
    # Encoder les caractères spéciaux
    url = url.replace(' ', '%20')
    url = url.replace('&', '%26')
    
    return base_url + "Methodes/" + method_name + "/" + url

# ============================================
# SCAN DES DOSSIERS *_with_index
# ============================================

def find_with_index_folders():
    """Trouve tous les dossiers *_with_index dans Methodes/"""
    folders = []
    
    if not METHODES_DIR.exists():
        print(f"❌ Dossier {METHODES_DIR} introuvable")
        return folders
    
    for item in METHODES_DIR.iterdir():
        if item.is_dir() and item.name.endswith('_with_index'):
            folders.append(item)
            print(f"✅ Trouvé: {item.name}")
    
    return folders

# ============================================
# CHARGEMENT DES INDEX
# ============================================

def load_songs_index(folder):
    """Charge le songs_index.json d'un dossier."""
    index_file = folder / "songs_index.json"
    
    if not index_file.exists():
        print(f"⚠️  Pas de songs_index.json dans {folder.name}")
        return None
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📄 Chargé: {len(data.get('songs', []))} songs depuis {folder.name}")
            return data
    except Exception as e:
        print(f"❌ Erreur lecture {index_file}: {e}")
        return None

def load_search_index_ocr():
    """Charge le search_index_ocr.json si disponible."""
    if not SEARCH_INDEX_OCR.exists():
        print("⚠️  search_index_ocr.json introuvable - pas d'enrichissement OCR")
        return {}
    
    try:
        with open(SEARCH_INDEX_OCR, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📄 Chargé: {len(data)} ressources OCR depuis search_index_ocr.json")
            return data
    except Exception as e:
        print(f"❌ Erreur lecture search_index_ocr.json: {e}")
        return {}

# ============================================
# ENRICHISSEMENT AVEC OCR
# ============================================

def enrich_with_ocr(song, method_name, ocr_data):
    """Enrichit une song avec les données OCR."""
    # Chercher dans les données OCR
    for resource in ocr_data.get('resources', []):
        # Match par URL de page
        if song.get('page_url') and resource.get('page_url'):
            if song['page_url'] in resource['page_url'] or resource['page_url'] in song['page_url']:
                # Enrichir les métadonnées
                if not song.get('tonalite') and resource.get('tonalite'):
                    song['tonalite'] = resource['tonalite']
                
                if not song.get('track_number') and resource.get('track_number'):
                    song['track_number'] = resource['track_number']
                
                if not song.get('page_number') and resource.get('page_number'):
                    song['page_number'] = resource['page_number']
                
                if not song.get('techniques') and resource.get('techniques'):
                    song['techniques'] = resource['techniques']
                
                # Ajouter le texte OCR
                if resource.get('text'):
                    song['ocr_text'] = resource['text']
                
                print(f"  ✨ Enrichi avec OCR: {song.get('title', 'Sans titre')}")
                break
    
    return song

# ============================================
# FUSION DES INDEX
# ============================================

def merge_indexes():
    """Fusionne tous les index en un seul mega-search-index.json"""
    
    print("\n" + "="*60)
    print("🔍 FUSION ULTIMATE v4.0 - DÉMARRAGE")
    print("="*60 + "\n")
    
    # 1. Trouver tous les dossiers
    folders = find_with_index_folders()
    if not folders:
        print("❌ Aucun dossier *_with_index trouvé")
        return
    
    print(f"\n📂 {len(folders)} dossiers trouvés\n")
    
    # 2. Charger les données OCR
    ocr_data = load_search_index_ocr()
    
    # 3. Fusionner
    merged_data = {
        "metadata": {
            "version": "4.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_methods": 0,
            "total_resources": 0,
            "sources": []
        },
        "methods": [],
        "all_resources": []
    }
    
    resource_id = 1
    
    for folder in folders:
        # Charger l'index
        index_data = load_songs_index(folder)
        if not index_data:
            continue
        
        method_name = folder.name.replace('_with_index', '')
        
        # Créer l'entrée méthode
        method_entry = {
            "name": method_name,
            "folder": folder.name,
            "total_songs": len(index_data.get('songs', [])),
            "has_mp3": index_data.get('metadata', {}).get('has_mp3', False),
            "resources": []
        }
        
        # Traiter chaque song
        for song in index_data.get('songs', []):
            # Enrichir avec OCR
            song = enrich_with_ocr(song, method_name, ocr_data)
            
            # Créer la ressource
            resource = {
                "id": resource_id,
                "method": method_name,
                "title": song.get('title', 'Sans titre'),
                "tonalite": song.get('tonalite') or extract_tonality(song.get('title', '')),
                "track_number": song.get('track_number') or extract_track_number(song.get('title', '')),
                "page_number": song.get('page_number') or extract_page_number(song.get('title', '')),
                "techniques": song.get('techniques', []),
                "page_url": normalize_url(song.get('page_url'), method_name),
                "mp3_url": normalize_url(song.get('mp3_url'), method_name) if song.get('mp3_url') else None,
                "type": "song",
                "searchable_text": f"{song.get('title', '')} {song.get('tonalite', '')} {' '.join(song.get('techniques', []))} {song.get('ocr_text', '')}"
            }
            
            # Ajouter aux listes
            method_entry['resources'].append(resource)
            merged_data['all_resources'].append(resource)
            
            resource_id += 1
        
        # Ajouter la méthode
        merged_data['methods'].append(method_entry)
        merged_data['metadata']['sources'].append({
            "method": method_name,
            "resources": len(method_entry['resources'])
        })
    
    # Mise à jour des métadonnées
    merged_data['metadata']['total_methods'] = len(merged_data['methods'])
    merged_data['metadata']['total_resources'] = len(merged_data['all_resources'])
    
    # 4. Sauvegarder
    print(f"\n💾 Sauvegarde de {merged_data['metadata']['total_resources']} ressources...")
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ SUCCÈS ! Fichier créé: {OUTPUT_FILE}")
        print(f"\n📊 STATISTIQUES:")
        print(f"   - Méthodes: {merged_data['metadata']['total_methods']}")
        print(f"   - Ressources: {merged_data['metadata']['total_resources']}")
        print(f"\n🎸 Le mega-search-index.json est prêt !")
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    merge_indexes()
