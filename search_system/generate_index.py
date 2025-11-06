#!/usr/bin/env python3
"""
Générateur automatique de search_index.json pour Prof de Basse
Scanne le repo GitHub et créée un index complet de toutes les ressources
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Configuration
REPO_BASE = "https://11drumboy11.github.io/Prof-de-basse/"
OUTPUT_FILE = "search_system/data/search_index.json"

class ResourceIndexer:
    def __init__(self):
        self.resources = []
        
    def add_resource(self, resource: Dict[str, Any]):
        """Ajoute une ressource à l'index"""
        self.resources.append(resource)
    
    def generate_funk_disco_resources(self):
        """Génère les entrées pour 70s Funk & Disco (99 tracks)"""
        print("Génération des ressources Funk & Disco...")
        
        for i in range(1, 100):
            track_num = str(i).zfill(2)
            
            # Déterminer niveau et style selon le track
            if i <= 15:
                level = "beginner"
                style = "funk"
                technique = "fingerstyle"
            elif i <= 30:
                level = "intermediate"
                style = "funk"
                technique = "ghostnotes"
            elif i <= 60:
                level = "intermediate"
                style = "funk"
                technique = "slap"
            elif i <= 80:
                level = "advanced"
                style = "disco"
                technique = "fingerstyle"
            else:
                level = "advanced"
                style = "slap"
                technique = "slap"
            
            resource = {
                "id": f"funk-disco-{track_num}",
                "title": f"Track {track_num}",
                "type": "mp3",
                "source": "70s Funk & Disco Bass",
                "url": f"{REPO_BASE}Methodes/70%20Funk%20&%20Disco%20bass%20MP3/Track%20{track_num}.mp3",
                "style": style,
                "level": level,
                "technique": technique,
                "tempo": 90 + i,
                "description": f"Exercice de {style} niveau {level}",
                "tags": [style, level, technique],
                "searchable_text": f"track {track_num} funk disco {style} {level} {technique}"
            }
            
            self.add_resource(resource)
    
    def generate_liebman_resources(self):
        """Génère les entrées pour John Liebman Funk Fusion"""
        print("Génération des ressources John Liebman...")
        
        for i in range(1, 51):
            track_num = str(i).zfill(2)
            
            level = "beginner" if i <= 15 else "intermediate" if i <= 35 else "advanced"
            
            resource = {
                "id": f"liebman-{track_num}",
                "title": f"Track {i}",
                "type": "mp3",
                "source": "John Liebman Funk Fusion",
                "url": f"{REPO_BASE}Methodes/John%20Liebman%20Funk%20Fusion%20Mp3/{track_num}%20-%20Track%20{i}.mp3",
                "style": "funk",
                "level": level,
                "technique": "fingerstyle",
                "description": f"Exercice funk fusion niveau {level}",
                "tags": ["funk", "fusion", level],
                "searchable_text": f"liebman track {i} funk fusion {level}"
            }
            
            self.add_resource(resource)
    
    def generate_jazz_standards(self):
        """Génère les entrées pour les Real Books Jazz"""
        print("Génération des standards jazz...")
        
        standards = [
            {
                "title": "All The Things You Are",
                "composer": "Jerome Kern",
                "key": "Ab",
                "tempo": 120,
                "level": "intermediate",
                "description": "Standard jazz en Ab majeur avec walking bass"
            },
            {
                "title": "Autumn Leaves",
                "composer": "Joseph Kosma",
                "key": "Gm",
                "tempo": 140,
                "level": "beginner",
                "description": "Standard jazz parfait pour débuter le walking"
            },
            {
                "title": "Blue Bossa",
                "composer": "Kenny Dorham",
                "key": "Cm",
                "tempo": 130,
                "level": "intermediate",
                "description": "Bossa nova classique en Cm"
            },
            {
                "title": "So What",
                "composer": "Miles Davis",
                "key": "Dm",
                "tempo": 136,
                "level": "intermediate",
                "description": "Modal jazz iconique, ligne de Paul Chambers"
            },
            {
                "title": "Summertime",
                "composer": "George Gershwin",
                "key": "Am",
                "tempo": 100,
                "level": "beginner",
                "description": "Ballade jazz parfaite pour travailler le phrasé"
            },
            {
                "title": "Take Five",
                "composer": "Paul Desmond",
                "key": "Ebm",
                "tempo": 176,
                "level": "intermediate",
                "description": "Standard en 5/4 avec ligne de walking iconique"
            },
            {
                "title": "Girl from Ipanema",
                "composer": "Antonio Carlos Jobim",
                "key": "F",
                "tempo": 140,
                "level": "beginner",
                "description": "Bossa nova facile et populaire"
            }
        ]
        
        for std in standards:
            resource = {
                "id": f"jazz-{std['title'].lower().replace(' ', '-')}",
                "title": std['title'],
                "type": "realbook",
                "source": "Real Book Jazz",
                "composer": std['composer'],
                "style": "jazz",
                "level": std['level'],
                "technique": "walking",
                "key": std['key'],
                "tempo": std['tempo'],
                "description": std['description'],
                "tags": ["jazz", "standard", std['level'], "walking"],
                "searchable_text": f"{std['title']} {std['composer']} jazz standard {std['level']} {std['key']}"
            }
            
            self.add_resource(resource)
    
    def generate_exercises(self):
        """Génère les exercices techniques"""
        print("Génération des exercices techniques...")
        
        exercises = [
            {
                "title": "Chromatic Warm-up",
                "technique": "fingerstyle",
                "level": "beginner",
                "description": "Échauffement chromatique sur 4 cordes"
            },
            {
                "title": "Gammes majeures",
                "technique": "scales",
                "level": "beginner",
                "description": "Gammes majeures sur 2 octaves"
            },
            {
                "title": "Arpèges 7e",
                "technique": "arpeggio",
                "level": "intermediate",
                "description": "Arpèges d'accords de 7e"
            },
            {
                "title": "Ghost Notes Funk",
                "technique": "ghostnotes",
                "level": "intermediate",
                "description": "Travail des ghost notes en funk"
            },
            {
                "title": "Slap Introduction",
                "technique": "slap",
                "level": "intermediate",
                "description": "Bases du slap : thumb et pop"
            },
            {
                "title": "Walking Bass II-V-I",
                "technique": "walking",
                "level": "intermediate",
                "description": "Walking bass sur progression II-V-I"
            }
        ]
        
        for ex in exercises:
            resource = {
                "id": f"exercise-{ex['title'].lower().replace(' ', '-')}",
                "title": ex['title'],
                "type": "exercise",
                "source": "Prof de Basse",
                "style": "technique",
                "level": ex['level'],
                "technique": ex['technique'],
                "description": ex['description'],
                "tags": ["exercise", "technique", ex['level'], ex['technique']],
                "searchable_text": f"{ex['title']} exercise technique {ex['level']} {ex['technique']}"
            }
            
            self.add_resource(resource)
    
    def generate_index(self):
        """Génère l'index complet"""
        print("\n=== Génération de l'index complet ===\n")
        
        self.generate_funk_disco_resources()
        self.generate_liebman_resources()
        self.generate_jazz_standards()
        self.generate_exercises()
        
        print(f"\nTotal : {len(self.resources)} ressources générées")
        
        return self.resources
    
    def save_to_json(self):
        """Sauvegarde l'index en JSON"""
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Structure finale
        index_data = {
            "version": "1.0.0",
            "generated_at": "2025-11-06",
            "total_resources": len(self.resources),
            "resources": self.resources,
            "statistics": {
                "mp3": len([r for r in self.resources if r['type'] == 'mp3']),
                "realbook": len([r for r in self.resources if r['type'] == 'realbook']),
                "exercise": len([r for r in self.resources if r['type'] == 'exercise']),
                "beginner": len([r for r in self.resources if r['level'] == 'beginner']),
                "intermediate": len([r for r in self.resources if r['level'] == 'intermediate']),
                "advanced": len([r for r in self.resources if r['level'] == 'advanced'])
            }
        }
        
        # Sauvegarder
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Index sauvegardé dans {OUTPUT_FILE}")
        print(f"   - {index_data['statistics']['mp3']} fichiers MP3")
        print(f"   - {index_data['statistics']['realbook']} Real Book standards")
        print(f"   - {index_data['statistics']['exercise']} exercices")
        print(f"\nRépartition par niveau :")
        print(f"   - Débutant : {index_data['statistics']['beginner']}")
        print(f"   - Intermédiaire : {index_data['statistics']['intermediate']}")
        print(f"   - Avancé : {index_data['statistics']['advanced']}")

def main():
    print("🎸 Prof de Basse - Générateur d'Index de Recherche\n")
    
    indexer = ResourceIndexer()
    indexer.generate_index()
    indexer.save_to_json()
    
    print("\n✨ Index généré avec succès !")

if __name__ == "__main__":
    main()
