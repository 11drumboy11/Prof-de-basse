#!/usr/bin/env python3
"""
📊 Générateur MEGA SEARCH INDEX v2.0
Fusionne tous les résultats du scan en un seul fichier de recherche unifié
FORMAT COMPATIBLE avec le site Prof-de-basse
"""

import json
from pathlib import Path
from datetime import datetime
import re

class MegaIndexGenerator:
    def __init__(self):
        self.root_dir = Path('.')
        self.scan_report_file = self.root_dir / 'scan-report.json'
        self.output_file = self.root_dir / 'mega-search-index.json'
        
    def generate(self):
        """Génère le mega-search-index.json"""
        print("📊 Génération du MEGA SEARCH INDEX v2.0...")
        
        # Charger le scan report
        if not self.scan_report_file.exists():
            print(f"❌ Fichier {self.scan_report_file} introuvable")
            return
        
        with open(self.scan_report_file, 'r', encoding='utf-8') as f:
            scan_data = json.load(f)
        
        # Construire l'index de recherche
        search_index = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '3.0.0',
                'total_resources': 0,
                'total_methods': scan_data['total_methods'],
                'total_songs': scan_data['total_songs'],
                'total_images': scan_data['total_images'],
                'total_mp3': scan_data['total_mp3'],
                'scan_date': scan_data['scan_date']
            },
            'all_resources': self.build_resources(scan_data),  # ← NOM CHANGÉ !
            'categories': self.build_categories(scan_data),
            'search_index': self.build_search_index(scan_data),
            'total_resources': 0,  # Sera calculé après
            'version': '3.0.0'
        }
        
        search_index['total_resources'] = len(search_index['all_resources'])
        search_index['metadata']['total_resources'] = len(search_index['all_resources'])
        
        # Sauvegarder
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(search_index, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {self.output_file} généré avec succès!")
        print(f"   📦 {search_index['total_resources']} ressources indexées")
        print(f"   📂 {len(search_index['categories'])} catégories")
        print(f"   🔍 Format compatible site: all_resources ✓")
    
    def build_categories(self, scan_data):
        """Construit la liste des catégories"""
        categories = {}
        
        for method_id, method_data in scan_data['methods'].items():
            category = method_data['category']
            
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'count': 0,
                    'methods': []
                }
            
            categories[category]['count'] += 1
            categories[category]['methods'].append({
                'id': method_id,
                'name': method_data['name'],
                'path': method_data['path'],
                'songs_count': len(method_data['songs']),
                'has_mp3': method_data['mp3_count'] > 0
            })
        
        return categories
    
    def build_resources(self, scan_data):
        """Construit la liste complète des ressources"""
        resources = []
        resource_id = 1
        
        for method_id, method_data in scan_data['methods'].items():
            method_name = method_data['name']
            category = method_data['category']
            base_path = method_data['path']
            
            # Ajouter chaque morceau comme ressource
            for song in method_data['songs']:
                # Construire les URLs
                page_url = self.build_url(base_path, song.get('page_url'))
                mp3_url = self.build_mp3_url(base_path, song.get('mp3_url'))
                
                resource = {
                    'id': resource_id,
                    'type': 'song',
                    'method_id': method_id,
                    'method_name': method_name,
                    'category': category,
                    'title': song.get('title', 'Sans titre'),
                    'page_number': song.get('page_number'),
                    'tonalite': song.get('tonalite'),
                    'track_number': song.get('track_number'),
                    'techniques': song.get('techniques', []),
                    'composer': song.get('composer'),
                    'page_url': page_url,
                    'mp3_url': mp3_url,
                    'index_url': f"https://11drumboy11.github.io/Prof-de-basse/{base_path}/index.html",
                    'searchable_text': self.build_searchable_text(song, method_name)
                }
                
                resources.append(resource)
                resource_id += 1
        
        return resources
    
    def build_search_index(self, scan_data):
        """Construit un index de recherche rapide"""
        index = {
            'by_title': {},
            'by_technique': {},
            'by_tonalite': {},
            'by_composer': {},
            'by_method': {},
            'by_category': {}
        }
        
        for method_id, method_data in scan_data['methods'].items():
            category = method_data['category']
            method_name = method_data['name']
            
            # Index par méthode
            if method_id not in index['by_method']:
                index['by_method'][method_id] = []
            
            # Index par catégorie
            if category not in index['by_category']:
                index['by_category'][category] = []
            
            for song in method_data['songs']:
                song_ref = {
                    'method_id': method_id,
                    'title': song.get('title'),
                    'page': song.get('page_number')
                }
                
                # Par titre
                title = song.get('title', '').lower()
                for word in self.tokenize(title):
                    if word not in index['by_title']:
                        index['by_title'][word] = []
                    index['by_title'][word].append(song_ref)
                
                # Par technique
                for technique in song.get('techniques', []):
                    tech_lower = technique.lower()
                    if tech_lower not in index['by_technique']:
                        index['by_technique'][tech_lower] = []
                    index['by_technique'][tech_lower].append(song_ref)
                
                # Par tonalité
                tonalite = song.get('tonalite')
                if tonalite:
                    ton_key = tonalite.lower()
                    if ton_key not in index['by_tonalite']:
                        index['by_tonalite'][ton_key] = []
                    index['by_tonalite'][ton_key].append(song_ref)
                
                # Par compositeur
                composer = song.get('composer')
                if composer:
                    comp_lower = composer.lower()
                    if comp_lower not in index['by_composer']:
                        index['by_composer'][comp_lower] = []
                    index['by_composer'][comp_lower].append(song_ref)
                
                # Ajouter aux index de méthode et catégorie
                index['by_method'][method_id].append(song_ref)
                index['by_category'][category].append(song_ref)
        
        return index
    
    def build_url(self, base_path, relative_url):
        """Construit une URL complète GitHub Pages"""
        if not relative_url:
            return None
        
        # Nettoyer le chemin relatif
        clean_path = relative_url.replace('./', '')
        
        # Construire l'URL GitHub Pages
        base_url = "https://11drumboy11.github.io/Prof-de-basse"
        full_url = f"{base_url}/{base_path}/{clean_path}"
        
        # Encoder les espaces
        full_url = full_url.replace(' ', '%20')
        
        return full_url
    
    def build_mp3_url(self, base_path, mp3_filename):
        """Construit une URL MP3 complète"""
        if not mp3_filename:
            return None
        
        base_url = "https://11drumboy11.github.io/Prof-de-basse"
        
        # Si c'est déjà un chemin complet, utiliser tel quel
        if mp3_filename.startswith('http'):
            return mp3_filename
        
        # Sinon, construire l'URL
        full_url = f"{base_url}/{base_path}/{mp3_filename}"
        full_url = full_url.replace(' ', '%20')
        
        return full_url
    
    def build_searchable_text(self, song, method_name):
        """Construit le texte complet pour la recherche"""
        parts = [
            song.get('title', ''),
            method_name,
            song.get('composer', ''),
            song.get('tonalite', ''),
            ' '.join(song.get('techniques', []))
        ]
        
        return ' '.join([p for p in parts if p]).lower()
    
    def tokenize(self, text):
        """Découpe un texte en mots"""
        if not text:
            return []
        
        # Enlever la ponctuation et découper
        words = re.findall(r'\w+', text.lower())
        
        # Enlever les mots trop courts
        words = [w for w in words if len(w) > 2]
        
        return words


if __name__ == '__main__':
    generator = MegaIndexGenerator()
    generator.generate()
