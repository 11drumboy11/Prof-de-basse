#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎸 Prof de Basse - Musical Metadata Extractor
Extrait automatiquement tempo, tonalité, niveau, technique depuis les noms de fichiers
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class MusicalMetadataExtractor:
    """Extracteur intelligent de métadonnées musicales"""
    
    # Patterns de détection
    PATTERNS = {
        'track_number': r'(?:Track|track)\s*(\d{1,3})',
        'tempo': r'(\d{2,3})\s*(?:bpm|BPM)',
        'tonality': r'\b([A-G][#b]?(?:maj|min|m|M|7|maj7|m7|dim|aug)?)\b',
        'technique': r'\b(slap|fingerstyle|pick|ghost[-\s]?notes?|hammer[-\s]?on|pull[-\s]?off|tapping)\b',
        'level': r'\b(beginner|intermediate|advanced|débutant|intermédiaire|avancé)\b',
        'style': r'\b(funk|jazz|rock|blues|disco|motown|fusion|latin|afrobeat|reggae)\b',
    }
    
    # Mapping niveau FR→EN
    LEVEL_MAP = {
        'débutant': 'beginner',
        'intermédiaire': 'intermediate',
        'avancé': 'advanced'
    }
    
    # Tempos typiques par style (pour déduction)
    STYLE_TEMPOS = {
        'funk': (90, 115),
        'disco': (115, 130),
        'jazz': (120, 180),
        'blues': (60, 120),
        'rock': (110, 140),
        'latin': (100, 140),
        'reggae': (70, 100),
    }
    
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.metadata = {}
    
    def extract_from_filename(self, filename: str) -> Dict[str, any]:
        """Extrait toutes les métadonnées possibles d'un nom de fichier"""
        meta = {}
        
        # Track number
        if match := re.search(self.PATTERNS['track_number'], filename, re.IGNORECASE):
            meta['track_number'] = int(match.group(1))
        
        # Tempo
        if match := re.search(self.PATTERNS['tempo'], filename, re.IGNORECASE):
            meta['tempo'] = int(match.group(1))
        
        # Tonalité
        if match := re.search(self.PATTERNS['tonality'], filename):
            meta['tonality'] = match.group(1)
        
        # Technique
        techniques = re.findall(self.PATTERNS['technique'], filename, re.IGNORECASE)
        if techniques:
            meta['techniques'] = [t.lower().replace(' ', '-') for t in techniques]
        
        # Niveau
        if match := re.search(self.PATTERNS['level'], filename, re.IGNORECASE):
            level = match.group(1).lower()
            meta['level'] = self.LEVEL_MAP.get(level, level)
        
        # Style
        styles = re.findall(self.PATTERNS['style'], filename, re.IGNORECASE)
        if styles:
            meta['styles'] = [s.lower() for s in styles]
        
        return meta
    
    def deduce_level_from_track(self, track_num: int, method: str) -> Optional[str]:
        """Déduit le niveau depuis le numéro de track et la méthode"""
        if '70' in method.lower() and 'funk' in method.lower():
            if track_num <= 15:
                return 'beginner'
            elif track_num <= 40:
                return 'intermediate'
            else:
                return 'advanced'
        return None
    
    def deduce_tempo_from_style(self, style: str) -> Optional[Tuple[int, int]]:
        """Retourne un range de tempo typique pour un style"""
        return self.STYLE_TEMPOS.get(style.lower())
    
    def scan_mp3_files(self) -> Dict[str, Dict]:
        """Scanne tous les MP3 et extrait métadonnées"""
        mp3_data = {}
        
        for mp3_file in self.repo_root.rglob('*.mp3'):
            rel_path = mp3_file.relative_to(self.repo_root)
            filename = mp3_file.name
            parent_dir = mp3_file.parent.name
            
            # Extraction de base
            meta = self.extract_from_filename(filename)
            meta['filename'] = filename
            meta['path'] = str(rel_path)
            meta['method'] = parent_dir
            
            # Déductions intelligentes
            if 'track_number' in meta and 'level' not in meta:
                if deduced_level := self.deduce_level_from_track(meta['track_number'], parent_dir):
                    meta['level'] = deduced_level
                    meta['level_deduced'] = True
            
            if 'styles' in meta and 'tempo' not in meta:
                for style in meta['styles']:
                    if tempo_range := self.deduce_tempo_from_style(style):
                        meta['tempo_range'] = tempo_range
            
            # URL GitHub Pages
            meta['url'] = f"https://11drumboy11.github.io/Prof-de-basse/{rel_path.as_posix()}"
            
            mp3_data[str(rel_path)] = meta
        
        return mp3_data
    
    def scan_pdf_files(self) -> Dict[str, Dict]:
        """Scanne tous les PDF"""
        pdf_data = {}
        
        for pdf_file in self.repo_root.rglob('*.pdf'):
            rel_path = pdf_file.relative_to(self.repo_root)
            filename = pdf_file.name
            
            meta = self.extract_from_filename(filename)
            meta['filename'] = filename
            meta['path'] = str(rel_path)
            meta['size_mb'] = round(pdf_file.stat().st_size / (1024*1024), 2)
            
            pdf_data[str(rel_path)] = meta
        
        return pdf_data
    
    def load_ocr_json(self) -> Dict[str, any]:
        """Charge les JSON OCR existants (depuis ton convertisseur)"""
        ocr_data = {}
        
        for json_file in self.repo_root.rglob('*.json'):
            if 'ocr' in json_file.name.lower() or 'exercises' in json_file.name.lower():
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        ocr_data[str(json_file.relative_to(self.repo_root))] = data
                except Exception as e:
                    print(f"⚠️  Could not load {json_file}: {e}")
        
        return ocr_data
    
    def associate_mp3_pdf_png(self, mp3_data: Dict, pdf_data: Dict, ocr_data: Dict) -> List[Dict]:
        """Crée des associations intelligentes MP3↔PDF↔PNG"""
        associations = []
        
        for mp3_path, mp3_meta in mp3_data.items():
            # Pattern matching pour trouver PDF correspondant
            method = mp3_meta.get('method', '')
            track_num = mp3_meta.get('track_number')
            
            for pdf_path, pdf_meta in pdf_data.items():
                # Si même méthode dans le path
                if method.lower() in pdf_path.lower():
                    assoc = {
                        'mp3': mp3_path,
                        'mp3_meta': mp3_meta,
                        'pdf': pdf_path,
                        'pdf_meta': pdf_meta,
                        'confidence': 'high' if track_num else 'medium'
                    }
                    
                    # Chercher PNG correspondant dans OCR
                    for ocr_path, ocr_content in ocr_data.items():
                        if isinstance(ocr_content, dict) and 'exercises' in ocr_content:
                            for ex in ocr_content['exercises']:
                                if track_num and 'track' in ex.get('title', '').lower():
                                    if str(track_num) in ex['title']:
                                        assoc['png'] = ex.get('image_path')
                                        assoc['page'] = ex.get('page')
                                        assoc['exercise_title'] = ex.get('title')
                                        assoc['confidence'] = 'very_high'
                    
                    associations.append(assoc)
                    break  # Une seule association par MP3
        
        return associations
    
    def generate_stats(self, mp3_data: Dict, pdf_data: Dict, associations: List) -> Dict:
        """Génère des statistiques globales"""
        stats = {
            'total_mp3': len(mp3_data),
            'total_pdf': len(pdf_data),
            'total_associations': len(associations),
            'by_method': {},
            'by_level': {},
            'by_style': {},
            'tempo_distribution': {},
        }
        
        # Stats par méthode
        for meta in mp3_data.values():
            method = meta.get('method', 'unknown')
            stats['by_method'][method] = stats['by_method'].get(method, 0) + 1
            
            # Par niveau
            if level := meta.get('level'):
                stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
            
            # Par style
            for style in meta.get('styles', []):
                stats['by_style'][style] = stats['by_style'].get(style, 0) + 1
            
            # Distribution tempo
            if tempo := meta.get('tempo'):
                bucket = f"{(tempo//10)*10}-{(tempo//10)*10+9}"
                stats['tempo_distribution'][bucket] = stats['tempo_distribution'].get(bucket, 0) + 1
        
        return stats
    
    def export_to_json(self, output_dir: Path):
        """Exporte toutes les données en JSON"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("🔍 Scanning MP3 files...")
        mp3_data = self.scan_mp3_files()
        print(f"   ✅ Found {len(mp3_data)} MP3 files")
        
        print("📄 Scanning PDF files...")
        pdf_data = self.scan_pdf_files()
        print(f"   ✅ Found {len(pdf_data)} PDF files")
        
        print("🖼️  Loading OCR JSON...")
        ocr_data = self.load_ocr_json()
        print(f"   ✅ Loaded {len(ocr_data)} OCR files")
        
        print("🔗 Creating associations MP3↔PDF↔PNG...")
        associations = self.associate_mp3_pdf_png(mp3_data, pdf_data, ocr_data)
        print(f"   ✅ Created {len(associations)} associations")
        
        print("📊 Generating statistics...")
        stats = self.generate_stats(mp3_data, pdf_data, associations)
        
        # Export JSON complet
        complete_map = {
            'metadata': {
                'generated_at': str(Path.cwd()),
                'version': '1.0.0',
            },
            'mp3_index': mp3_data,
            'pdf_index': pdf_data,
            'ocr_index': ocr_data,
            'associations': associations,
            'stats': stats,
        }
        
        output_file = output_dir / 'complete-resource-map.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_map, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Complete map exported to: {output_file}")
        
        # Export stats séparément
        stats_file = output_dir / 'stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Stats exported to: {stats_file}")
        
        return complete_map


if __name__ == '__main__':
    repo_root = Path.cwd()  # GitHub Actions run from repo root
    output_dir = repo_root / 'resources'
    
    print("🎸 Prof de Basse - Musical Metadata Extractor")
    print(f"📁 Repository root: {repo_root}")
    print(f"📂 Output directory: {output_dir}\n")
    
    extractor = MusicalMetadataExtractor(repo_root)
    complete_map = extractor.export_to_json(output_dir)
    
    print("\n🎉 Extraction complete!")
    print(f"   📊 {complete_map['stats']['total_mp3']} MP3 indexed")
    print(f"   📄 {complete_map['stats']['total_pdf']} PDF indexed")
    print(f"   🔗 {complete_map['stats']['total_associations']} associations created")
