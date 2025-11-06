#!/usr/bin/env python3
"""
Fusion Script V2 - Prof de Basse (Version robuste)
Fusionne TOUS les index JSON avec gestion complète des erreurs
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import sys

class MegaIndexFusionV2:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.mega_index = {
            "version": "3.0.0-MEGA-V2",
            "generated_at": datetime.now().isoformat(),
            "total_resources": 0,
            "sources": [],
            "resources": []
        }
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log avec couleurs"""
        colors = {
            "INFO": "\033[94m",    # Bleu
            "SUCCESS": "\033[92m", # Vert
            "WARNING": "\033[93m", # Jaune
            "ERROR": "\033[91m",   # Rouge
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["RESET"])
        reset = colors["RESET"]
        print(f"{color}{message}{reset}")
        
    def find_all_json_files(self) -> List[Path]:
        """Trouve TOUS les fichiers JSON pertinents"""
        self.log("\n🔍 RECHERCHE DES INDEX JSON...", "INFO")
        
        json_files = []
        
        # Patterns de recherche
        patterns = [
            "**/search_index*.json",
            "**/resources_index.json",
            "**/complete-resource-map.json",
            "**/songs_index.json",
            "**/master_index.json"
        ]
        
        for pattern in patterns:
            try:
                found = list(self.repo_path.glob(pattern))
                if found:
                    self.log(f"   ✓ Pattern '{pattern}': {len(found)} fichiers", "SUCCESS")
                    json_files.extend(found)
                else:
                    self.log(f"   ○ Pattern '{pattern}': 0 fichiers", "WARNING")
            except Exception as e:
                self.log(f"   ✗ Erreur pattern '{pattern}': {e}", "ERROR")
        
        # Dédupliquer
        json_files = list(set(json_files))
        
        if json_files:
            self.log(f"\n📊 Total JSON trouvés: {len(json_files)}", "SUCCESS")
        else:
            self.log(f"\n⚠️  AUCUN fichier JSON trouvé!", "WARNING")
            self.log(f"   Cherché dans: {self.repo_path.absolute()}", "INFO")
            
        return json_files
    
    def load_json_safe(self, filepath: Path) -> Dict:
        """Charge un JSON en sécurité avec gestion d'erreurs"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.log(f"   ✓ {filepath.name}", "SUCCESS")
                return data
        except json.JSONDecodeError as e:
            error_msg = f"JSON invalide dans {filepath.name}: {e}"
            self.log(f"   ✗ {error_msg}", "ERROR")
            self.errors.append(error_msg)
            return {}
        except Exception as e:
            error_msg = f"Erreur lecture {filepath.name}: {e}"
            self.log(f"   ✗ {error_msg}", "ERROR")
            self.errors.append(error_msg)
            return {}
    
    def normalize_resource(self, resource: Dict, source: str, source_path: Path = None) -> Dict:
        """Normalise une ressource au format standard"""
        
        # Extraire l'ID
        resource_id = resource.get("id", resource.get("file", resource.get("path", "")))
        
        if not resource_id:
            # Générer un ID temporaire
            resource_id = f"unknown_{hash(str(resource))}"
        
        # Format standard
        normalized = {
            "id": str(resource_id),
            "title": str(resource.get("title", resource.get("name", "Sans titre"))),
            "type": self.detect_type(resource),
            "url": self.build_url(resource, source_path),
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
        
        # Texte de recherche
        search_parts = [
            normalized["title"],
            normalized.get("metadata", {}).get("composer", ""),
            normalized.get("metadata", {}).get("ocr_text", ""),
            normalized.get("metadata", {}).get("content", ""),
            normalized.get("metadata", {}).get("description", ""),
        ]
        
        # Ajouter styles et techniques
        if normalized.get("metadata", {}).get("styles"):
            search_parts.extend(normalized["metadata"]["styles"])
        if normalized.get("metadata", {}).get("techniques"):
            search_parts.extend(normalized["metadata"]["techniques"])
        
        normalized["search_text"] = " ".join(
            str(part).lower() for part in search_parts if part
        )
        
        return normalized
    
    def detect_type(self, resource: Dict) -> str:
        """Détecte le type de ressource"""
        file = str(resource.get("file", resource.get("path", "")))
        
        if ".mp3" in file.lower():
            return "mp3"
        elif ".pdf" in file.lower():
            return "pdf"
        elif ".png" in file.lower() or ".jpg" in file.lower() or ".jpeg" in file.lower():
            return "image"
        elif ".html" in file.lower():
            return "html"
        elif ".json" in file.lower():
            return "data"
        else:
            return "other"
    
    def build_url(self, resource: Dict, source_path: Path = None) -> str:
        """Construit l'URL complète GitHub Pages"""
        base_url = "https://11drumboy11.github.io/Prof-de-basse/"
        
        # Chercher le chemin - essayer plusieurs clés
        path = resource.get("url", "")
        if not path:
            path = resource.get("file", "")
        if not path:
            path = resource.get("path", "")
        if not path:
            path = resource.get("id", "")
        
        if not path:
            return base_url
        
        # Si déjà une URL complète, la retourner
        if str(path).startswith("http"):
            return str(path)
        
        # Nettoyer le chemin
        path = str(path)
        
        # Enlever les préfixes relatifs
        path = path.lstrip("/").lstrip("./")
        
        # CORRECTION INTELLIGENTE : Si le chemin semble incomplet (juste un nom de fichier)
        # et qu'on a le contexte du fichier source, reconstruire le chemin complet
        if source_path and "/" not in path:
            # C'est juste un nom de fichier (ex: "page_0374.jpg")
            # Reconstruire le chemin depuis le fichier source
            
            # Ex: source_path = "Real_Books/Real_book_jazz/songs_index.json"
            # On veut: "Real_Books/Real_book_jazz/assets/page_0374.jpg"
            
            source_dir = source_path.parent  # Real_Books/Real_book_jazz/
            
            # Chercher un dossier "assets" ou utiliser le dossier parent
            if (source_dir / "assets").exists():
                full_path = source_dir / "assets" / path
            else:
                full_path = source_dir / path
            
            # Convertir en chemin relatif depuis la racine du repo
            try:
                rel_path = full_path.relative_to(self.repo_path)
                path = str(rel_path)
            except ValueError:
                # Si on ne peut pas calculer le chemin relatif, garder tel quel
                pass
        
        # Encoder les espaces et caractères spéciaux pour URL
        # ATTENTION : Ne pas encoder les "/" qui sont des séparateurs de chemin
        parts = path.split("/")
        encoded_parts = []
        for part in parts:
            # Encoder chaque partie séparément
            encoded_part = part.replace(" ", "%20").replace("&", "%26")
            encoded_parts.append(encoded_part)
        
        path = "/".join(encoded_parts)
        
        return base_url + path
    
    def merge_resources(self, json_files: List[Path]) -> List[Dict]:
        """Fusionne toutes les ressources"""
        self.log("\n📥 FUSION DES RESSOURCES...", "INFO")
        
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
                try:
                    if isinstance(resource, dict):
                        # IMPORTANT : Passer le chemin du fichier source pour reconstruire les URLs
                        normalized = self.normalize_resource(resource, source_name, json_file)
                        
                        # Éviter doublons
                        resource_id = normalized["id"]
                        if resource_id not in seen_ids:
                            all_resources.append(normalized)
                            seen_ids.add(resource_id)
                except Exception as e:
                    error_msg = f"Erreur normalisation ressource dans {source_name}: {e}"
                    self.log(f"   ⚠ {error_msg}", "WARNING")
                    self.errors.append(error_msg)
        
        return all_resources
    
    def create_mega_index(self) -> Dict:
        """Crée le MEGA index complet"""
        self.log("\n" + "="*60, "INFO")
        self.log("🚀 MEGA INDEX FUSION V2 - Prof de Basse", "INFO")
        self.log("="*60, "INFO")
        
        json_files = self.find_all_json_files()
        
        if not json_files:
            self.log("\n❌ ERREUR: Aucun fichier JSON trouvé!", "ERROR")
            self.log("\n💡 SOLUTIONS:", "INFO")
            self.log("   1. Vérifie que tu es dans le bon dossier", "INFO")
            self.log("   2. Lance 'pwd' pour voir où tu es", "INFO")
            self.log("   3. Les fichiers JSON doivent être dans:", "INFO")
            self.log("      - Prof-de-basse-OCR/", "INFO")
            self.log("      - resources/", "INFO")
            self.log("      - Real_Books/", "INFO")
            return self.mega_index
        
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
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(self.mega_index, f, ensure_ascii=False, indent=2)
            
            self.log(f"\n✅ MEGA INDEX CRÉÉ: {output}", "SUCCESS")
            self.log(f"   📊 Total: {self.mega_index['total_resources']} ressources", "INFO")
            self.log(f"   📚 Sources: {self.mega_index['statistics']['sources_merged']} fichiers", "INFO")
            
            if self.mega_index["statistics"]["by_type"]:
                self.log(f"\n📈 Par type:", "INFO")
                for type_name, count in self.mega_index["statistics"]["by_type"].items():
                    self.log(f"   {type_name}: {count}", "INFO")
            
            # Afficher les erreurs si présentes
            if self.errors:
                self.log(f"\n⚠️  {len(self.errors)} avertissements:", "WARNING")
                for error in self.errors[:5]:  # Max 5 erreurs
                    self.log(f"   - {error}", "WARNING")
                if len(self.errors) > 5:
                    self.log(f"   ... et {len(self.errors) - 5} autres", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"\n❌ ERREUR SAUVEGARDE: {e}", "ERROR")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fusion MEGA Index V2')
    parser.add_argument('--repo', default='.', help='Chemin du repo')
    parser.add_argument('--output', default='mega-search-index.json', help='Fichier de sortie')
    args = parser.parse_args()
    
    fusion = MegaIndexFusionV2(args.repo)
    fusion.create_mega_index()
    success = fusion.save_mega_index(args.output)
    
    if success:
        fusion.log("\n✅ FUSION TERMINÉE!", "SUCCESS")
        sys.exit(0)
    else:
        fusion.log("\n❌ FUSION ÉCHOUÉE!", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
