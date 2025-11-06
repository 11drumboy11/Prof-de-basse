#!/usr/bin/env python3
"""
Fusion Script - Prof de Basse
Fusionne TOUS les index JSON en un MEGA index pour recherche ultra-rapide
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class MegaIndexFusion:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.mega_index = {
            "version": "3.0.0-MEGA",
            "generated_at": datetime.now().isoformat(),
            "total_resources": 0,
            "sources": [],
            "resources": []
        }
        
    def find_all_json_files(self) -> List[Path]:
        """Trouve TOUS les fichiers JSON pertinents"""
        json_files = []
        
        # Patterns de recherche
        patterns = [
            "**/search_index*.json",
            "**/resources_index.json",
            "**/complete-resource-map.json",
            "**/songs_index.json",
            "**/master_index.json",
            "**/search_index_ocr.json",
            "**/test_ocr_results.json"
        ]
        
        for pattern in patterns:
            found = list(self.repo_path.glob(pattern))
            json_files.extend(found)
            print(f"   ✓ Pattern '{pattern}': {len(found)} fichiers")
        
        # Dédupliquer
        json_files = list(set(json_files))
        print(f"\n📊 Total JSON trouvés: {len(json_files)}")
        return json_files
    
    def load_json_safe(self, filepath: Path) -> Dict:
        """Charge un JSON en sécurité"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"   ✓ {filepath.name}")
                return data
        except Exception as e:
            print(f"   ✗ {filepath.name}: {e}")
            return {}
    
    def normalize_resource(self, resource: Dict, source: str) -> Dict:
        """Normalise une ressource au format standard"""
        
        # Format standard
        normalized = {
            "id": resource.get("id", resource.get("file", "")),
            "title": resource.get("title", resource.get("name", "Sans titre")),
            "type": self.detect_type(resource),
            "url": self.build_url(resource),
            "source": source,
            "metadata": {}
        }
        
        # Ajouter métadonnées
        metadata_fields = [
            "techniques", "styles", "level", "tempo", "key", "composer",
            "page", "track", "pattern", "duration", "tags", "description",
            "ocr_text", "excerpt", "content", "path", "size"
        ]
        
        for field in metadata_fields:
            if field in resource and resource[field]:
                normalized["metadata"][field] = resource[field]
        
        # Texte de recherche (pour full-text)
        search_text_parts = [
            normalized["title"],
            normalized.get("metadata", {}).get("composer", ""),
            normalized.get("metadata", {}).get("ocr_text", ""),
            normalized.get("metadata", {}).get("content", ""),
            normalized.get("metadata", {}).get("description", ""),
        ]
        
        normalized["search_text"] = " ".join(
            str(part) for part in search_text_parts if part
        ).lower()
        
        return normalized
    
    def detect_type(self, resource: Dict) -> str:
        """Détecte le type de ressource"""
        file = resource.get("file", resource.get("path", ""))
        
        if ".mp3" in file.lower():
            return "mp3"
        elif ".pdf" in file.lower():
            return "pdf"
        elif ".png" in file.lower() or ".jpg" in file.lower():
            return "image"
        elif ".html" in file.lower():
            return "html"
        elif ".json" in file.lower():
            return "data"
        else:
            return "other"
    
    def build_url(self, resource: Dict) -> str:
        """Construit l'URL complète GitHub Pages"""
        base_url = "https://11drumboy11.github.io/Prof-de-basse/"
        
        # Chercher le chemin
        path = resource.get("file", resource.get("path", resource.get("url", "")))
        
        if path.startswith("http"):
            return path
        
        # Nettoyer le chemin
        path = path.lstrip("/").lstrip("./")
        
        # Encoder les espaces et caractères spéciaux
        path = path.replace(" ", "%20").replace("&", "%26")
        
        return base_url + path
    
    def merge_resources(self, json_files: List[Path]) -> List[Dict]:
        """Fusionne toutes les ressources"""
        all_resources = []
        seen_ids = set()
        
        for json_file in json_files:
            data = self.load_json_safe(json_file)
            
            if not data:
                continue
            
            source_name = json_file.name
            self.mega_index["sources"].append(str(json_file))
            
            # Extraire les ressources selon le format
            resources = []
            
            if "resources" in data:
                resources = data["resources"]
            elif isinstance(data, list):
                resources = data
            elif isinstance(data, dict):
                # Peut-être un songs_index
                for key, value in data.items():
                    if isinstance(value, dict):
                        value["id"] = key
                        resources.append(value)
            
            # Normaliser chaque ressource
            for resource in resources:
                if isinstance(resource, dict):
                    normalized = self.normalize_resource(resource, source_name)
                    
                    # Éviter doublons
                    resource_id = normalized["id"]
                    if resource_id not in seen_ids:
                        all_resources.append(normalized)
                        seen_ids.add(resource_id)
        
        return all_resources
    
    def create_mega_index(self) -> Dict:
        """Crée le MEGA index complet"""
        print("\n🔍 RECHERCHE DES INDEX JSON...")
        json_files = self.find_all_json_files()
        
        if not json_files:
            print("❌ Aucun fichier JSON trouvé!")
            return self.mega_index
        
        print("\n📥 FUSION DES RESSOURCES...")
        resources = self.merge_resources(json_files)
        
        self.mega_index["resources"] = resources
        self.mega_index["total_resources"] = len(resources)
        
        # Statistiques
        types_count = {}
        for r in resources:
            t = r["type"]
            types_count[t] = types_count.get(t, 0) + 1
        
        self.mega_index["statistics"] = {
            "by_type": types_count,
            "sources_merged": len(self.mega_index["sources"])
        }
        
        return self.mega_index
    
    def save_mega_index(self, output_path: str = "mega-search-index.json"):
        """Sauvegarde le MEGA index"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(self.mega_index, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ MEGA INDEX CRÉÉ: {output}")
        print(f"   📊 Total: {self.mega_index['total_resources']} ressources")
        print(f"   📚 Sources: {self.mega_index['statistics']['sources_merged']} fichiers")
        print(f"\n📈 Par type:")
        for type_name, count in self.mega_index["statistics"]["by_type"].items():
            print(f"   {type_name}: {count}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fusion MEGA Index')
    parser.add_argument('--repo', default='.', help='Chemin du repo')
    parser.add_argument('--output', default='mega-search-index.json', help='Fichier de sortie')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 MEGA INDEX FUSION - Prof de Basse v3.0")
    print("=" * 60)
    
    fusion = MegaIndexFusion(args.repo)
    fusion.create_mega_index()
    fusion.save_mega_index(args.output)
    
    print("\n✅ FUSION TERMINÉE!")

if __name__ == "__main__":
    main()
