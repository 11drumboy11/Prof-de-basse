#!/usr/bin/env python3
"""
Prof de Basse - Générateur Automatique d'Index Complets
========================================================

Ce script scanne TOUT le site GitHub et génère :
1. index.html à la racine (page d'accueil complète)
2. index.html dans chaque dossier
3. Système de recherche par nom, contenu et tags

Auteur: Prof de Basse GPT
Version: 1.0.0 FINAL
Date: 2025-11-03
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from bs4 import BeautifulSoup
import mimetypes
import re

# ============================================================================
# CONFIGURATION
# ============================================================================

# Dossiers et fichiers à ignorer
IGNORE_DIRS = {'.git', '.github', 'node_modules', '__pycache__', '.DS_Store'}
IGNORE_FILES = {'.gitignore', 'README.md', '.gitattributes', 'CNAME'}

# Extensions de fichiers par catégorie
FILE_CATEGORIES = {
    'audio': {'.mp3', '.wav', '.ogg', '.m4a', '.flac'},
    'image': {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'},
    'document': {'.pdf', '.doc', '.docx'},
    'sheet_music': {'.mxl', '.musicxml', '.gpx', '.gp5'},
    'web': {'.html', '.htm', '.css', '.js'},
    'data': {'.json', '.xml', '.csv', '.txt'}
}

# Tags musicaux (pour extraction automatique)
MUSIC_TAGS = {
    # Styles
    'funk', 'jazz', 'rock', 'blues', 'reggae', 'latin', 'afrobeat', 
    'disco', 'motown', 'soul', 'r&b', 'fusion',
    
    # Techniques
    'slap', 'fingerstyle', 'picking', 'tapping', 'harmonics',
    'ghost notes', 'walking', 'double thumb',
    
    # Niveaux
    'débutant', 'intermédiaire', 'avancé', 'expert',
    'beginner', 'intermediate', 'advanced',
    
    # Concepts
    'groove', 'timing', 'theory', 'improvisation', 'scales',
    'arpeggios', 'chords', 'rhythm', 'technique'
}

# ============================================================================
# CLASSES PRINCIPALES
# ============================================================================

class FileInfo:
    """Représente un fichier avec ses métadonnées"""
    
    def __init__(self, path: Path, root_dir: Path):
        self.path = path
        self.name = path.name
        self.relative_path = path.relative_to(root_dir)
        self.extension = path.suffix.lower()
        self.size = path.stat().st_size if path.exists() else 0
        self.modified = datetime.fromtimestamp(path.stat().st_mtime)
        self.category = self._get_category()
        self.tags = set()
        self.content_preview = ""
        
        # Extraire tags et contenu
        if self.extension == '.html':
            self._extract_html_info()
    
    def _get_category(self) -> str:
        """Détermine la catégorie du fichier"""
        for category, extensions in FILE_CATEGORIES.items():
            if self.extension in extensions:
                return category
        return 'other'
    
    def _extract_html_info(self):
        """Extrait les infos d'un fichier HTML"""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                
                # Extraire le titre
                title = soup.find('title')
                if title:
                    self.content_preview = title.get_text().strip()
                
                # Extraire les meta tags
                for meta in soup.find_all('meta'):
                    if meta.get('name') == 'keywords':
                        keywords = meta.get('content', '').lower()
                        self.tags.update(
                            tag.strip() for tag in keywords.split(',')
                            if tag.strip() in MUSIC_TAGS
                        )
                
                # Extraire tags du contenu
                text = soup.get_text().lower()
                self.tags.update(tag for tag in MUSIC_TAGS if tag in text)
                
        except Exception as e:
            print(f"⚠️ Erreur lecture HTML {self.path}: {e}")
    
    def get_url(self, base_url: str = "") -> str:
        """Retourne l'URL GitHub Pages du fichier"""
        return f"{base_url}/{self.relative_path.as_posix()}"
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour JSON"""
        return {
            'name': self.name,
            'path': str(self.relative_path),
            'extension': self.extension,
            'category': self.category,
            'size': self.size,
            'size_human': self._human_size(),
            'modified': self.modified.isoformat(),
            'tags': list(self.tags),
            'preview': self.content_preview
        }
    
    def _human_size(self) -> str:
        """Taille en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} TB"

class DirectoryScanner:
    """Scanne un répertoire et ses sous-répertoires"""
    
    def __init__(self, root_path: Path):
        self.root = root_path
        self.files: List[FileInfo] = []
        self.directories: Set[Path] = set()
    
    def scan(self):
        """Scanne récursivement le répertoire"""
        print(f"🔍 Scan de {self.root}...")
        
        for item in self.root.rglob('*'):
            # Ignorer certains dossiers
            if any(ignored in item.parts for ignored in IGNORE_DIRS):
                continue
            
            if item.is_file() and item.name not in IGNORE_FILES:
                file_info = FileInfo(item, self.root)
                self.files.append(file_info)
            elif item.is_dir():
                self.directories.add(item)
        
        print(f"✅ {len(self.files)} fichiers trouvés")
        print(f"✅ {len(self.directories)} dossiers trouvés")
    
    def get_files_in_dir(self, directory: Path) -> List[FileInfo]:
        """Retourne les fichiers d'un dossier spécifique (non récursif)"""
        return [
            f for f in self.files 
            if f.path.parent == directory
        ]
    
    def get_subdirs(self, directory: Path) -> List[Path]:
        """Retourne les sous-dossiers directs d'un dossier"""
        return sorted([
            d for d in self.directories 
            if d.parent == directory
        ])

# ============================================================================
# GÉNÉRATEURS HTML
# ============================================================================

class IndexGenerator:
    """Génère les fichiers index.html"""
    
    def __init__(self, base_url: str = "https://11drumboy11.github.io/Prof-de-basse"):
        self.base_url = base_url
    
    def generate_root_index(self, scanner: DirectoryScanner, output_path: Path):
        """Génère l'index.html de la racine (page d'accueil complète)"""
        
        # Statistiques
        stats = self._calculate_stats(scanner.files)
        
        # Grouper fichiers par catégorie
        files_by_category = self._group_by_category(scanner.files)
        
        # Grouper par dossier
        files_by_dir = self._group_by_directory(scanner.files)
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prof de Basse - Bibliothèque Complète</title>
    <meta name="description" content="Bibliothèque complète de ressources pédagogiques pour bassistes : méthodes, MP3, partitions, cours">
    <meta name="keywords" content="basse, cours, funk, jazz, slap, méthodes, mp3, partitions">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 48px;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .subtitle {{
            font-size: 20px;
            opacity: 0.95;
            margin-top: 10px;
        }}
        
        .update-info {{
            margin-top: 20px;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .search-bar {{
            position: sticky;
            top: 0;
            background: white;
            padding: 20px 40px;
            border-bottom: 3px solid #667eea;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        #searchInput {{
            width: 100%;
            padding: 15px 20px;
            font-size: 16px;
            border: 2px solid #667eea;
            border-radius: 10px;
            outline: none;
            transition: all 0.3s;
        }}
        
        #searchInput:focus {{
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }}
        
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        
        main {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .section-title {{
            font-size: 28px;
            color: #667eea;
        }}
        
        .section-count {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
        }}
        
        .file-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .file-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .file-card:hover {{
            border-color: #667eea;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
            transform: translateY(-3px);
        }}
        
        .file-icon {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .file-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            word-break: break-word;
        }}
        
        .file-meta {{
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .file-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }}
        
        .tag {{
            background: #e8eaf6;
            color: #667eea;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .directory-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        
        .dir-title {{
            font-size: 20px;
            color: #764ba2;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        
        .no-results-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        
        footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 40px 20px;
        }}
        
        footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .file-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎸 Prof de Basse</h1>
            <div class="subtitle">
                Bibliothèque Complète de Ressources Pédagogiques
            </div>
            <div class="update-info">
                📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </div>
        </header>
        
        <div class="search-bar">
            <input 
                type="text" 
                id="searchInput" 
                placeholder="🔍 Rechercher par nom, contenu ou tags (ex: funk, slap, débutant)..."
            >
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_files']}</div>
                <div class="stat-label">Fichiers Total</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['audio_files']}</div>
                <div class="stat-label">Fichiers MP3</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['html_files']}</div>
                <div class="stat-label">Pages HTML</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_size']}</div>
                <div class="stat-label">Taille Totale</div>
            </div>
        </div>
        
        <main id="mainContent">
"""
        
        # Section par catégorie
        for category, files in files_by_category.items():
            if not files:
                continue
            
            html += f"""
            <div class="section category-{category}">
                <div class="section-header">
                    <span class="section-title">{self._get_category_icon(category)} {self._get_category_name(category)}</span>
                    <span class="section-count">{len(files)}</span>
                </div>
                <div class="file-grid">
"""
            
            for file_info in sorted(files, key=lambda x: x.name)[:50]:  # Limiter à 50 par catégorie
                html += self._generate_file_card(file_info)
            
            html += """
                </div>
            </div>
"""
        
        # Section par répertoire
        html += """
            <div class="section">
                <div class="section-header">
                    <span class="section-title">📁 Par Répertoire</span>
                </div>
"""
        
        for directory, files in sorted(files_by_dir.items()):
            if not files:
                continue
            
            dir_name = directory.name if directory.name else "Racine"
            html += f"""
                <div class="directory-section">
                    <div class="dir-title">
                        📂 {dir_name}
                        <span class="section-count">{len(files)}</span>
                    </div>
                    <div class="file-grid">
"""
            
            for file_info in sorted(files, key=lambda x: x.name)[:20]:  # 20 fichiers par dossier
                html += self._generate_file_card(file_info)
            
            html += """
                    </div>
                </div>
"""
        
        html += """
        </main>
        
        <div id="noResults" class="no-results" style="display: none;">
            <div class="no-results-icon">🔍</div>
            <h2>Aucun résultat trouvé</h2>
            <p>Essayez avec d'autres mots-clés</p>
        </div>
        
        <footer>
            <p><strong>Prof de Basse - Système de Bibliothèque v1.0.0</strong></p>
            <p style="margin-top: 10px;">
                🤖 Index généré automatiquement par GitHub Actions
            </p>
            <p style="margin-top: 15px;">
                <a href="https://github.com/11drumboy11/Prof-de-basse" target="_blank">
                    📂 Voir sur GitHub
                </a>
            </p>
        </footer>
    </div>
    
    <script>
        // Données de recherche
        const filesData = """ + json.dumps([f.to_dict() for f in scanner.files], indent=2) + """;
        
        // Fonction de recherche
        const searchInput = document.getElementById('searchInput');
        const mainContent = document.getElementById('mainContent');
        const noResults = document.getElementById('noResults');
        
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            
            if (!query) {
                mainContent.style.display = 'block';
                noResults.style.display = 'none';
                return;
            }
            
            const results = filesData.filter(file => {
                // Recherche par nom
                if (file.name.toLowerCase().includes(query)) return true;
                
                // Recherche par path
                if (file.path.toLowerCase().includes(query)) return true;
                
                // Recherche par tags
                if (file.tags && file.tags.some(tag => tag.includes(query))) return true;
                
                // Recherche par preview
                if (file.preview && file.preview.toLowerCase().includes(query)) return true;
                
                return false;
            });
            
            if (results.length === 0) {
                mainContent.style.display = 'none';
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
                mainContent.style.display = 'block';
                
                // Masquer sections vides
                document.querySelectorAll('.section').forEach(section => {
                    section.style.display = 'none';
                });
                
                // Afficher seulement les fichiers qui matchent
                results.forEach(file => {
                    const card = document.querySelector(`[data-path="${file.path}"]`);
                    if (card) {
                        card.closest('.section').style.display = 'block';
                        card.style.display = 'block';
                    }
                });
                
                // Masquer les cartes qui ne matchent pas
                document.querySelectorAll('.file-card').forEach(card => {
                    const path = card.getAttribute('data-path');
                    const matches = results.some(f => f.path === path);
                    card.style.display = matches ? 'block' : 'none';
                });
            }
        });
    </script>
</body>
</html>
"""
        
        # Écrire le fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Index racine généré : {output_path}")
    
    def _calculate_stats(self, files: List[FileInfo]) -> dict:
        """Calcule les statistiques des fichiers"""
        total_size = sum(f.size for f in files)
        
        return {
            'total_files': len(files),
            'audio_files': len([f for f in files if f.category == 'audio']),
            'html_files': len([f for f in files if f.category == 'web']),
            'total_size': self._human_size(total_size)
        }
    
    def _human_size(self, size: int) -> str:
        """Convertit taille en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _group_by_category(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """Groupe les fichiers par catégorie"""
        result = {}
        for file_info in files:
            category = file_info.category
            if category not in result:
                result[category] = []
            result[category].append(file_info)
        return result
    
    def _group_by_directory(self, files: List[FileInfo]) -> Dict[Path, List[FileInfo]]:
        """Groupe les fichiers par répertoire"""
        result = {}
        for file_info in files:
            directory = file_info.path.parent
            if directory not in result:
                result[directory] = []
            result[directory].append(file_info)
        return result
    
    def _get_category_icon(self, category: str) -> str:
        """Retourne l'emoji de la catégorie"""
        icons = {
            'audio': '🎵',
            'image': '🖼️',
            'document': '📄',
            'sheet_music': '🎼',
            'web': '🌐',
            'data': '📊',
            'other': '📁'
        }
        return icons.get(category, '📁')
    
    def _get_category_name(self, category: str) -> str:
        """Retourne le nom français de la catégorie"""
        names = {
            'audio': 'Fichiers Audio (MP3)',
            'image': 'Images',
            'document': 'Documents',
            'sheet_music': 'Partitions',
            'web': 'Pages Web',
            'data': 'Données',
            'other': 'Autres'
        }
        return names.get(category, 'Autres')
    
    def _generate_file_card(self, file_info: FileInfo) -> str:
        """Génère une carte HTML pour un fichier"""
        
        url = file_info.get_url(self.base_url)
        icon = self._get_category_icon(file_info.category)
        
        tags_html = ""
        if file_info.tags:
            tags_html = '<div class="file-tags">'
            for tag in sorted(file_info.tags)[:5]:  # Max 5 tags
                tags_html += f'<span class="tag">{tag}</span>'
            tags_html += '</div>'
        
        preview_html = ""
        if file_info.content_preview:
            preview_html = f'<div class="file-meta">📝 {file_info.content_preview[:60]}...</div>'
        
        return f"""
                    <div class="file-card" data-path="{file_info.relative_path}" onclick="window.open('{url}', '_blank')">
                        <div class="file-icon">{icon}</div>
                        <div class="file-name">{file_info.name}</div>
                        {preview_html}
                        <div class="file-meta">
                            📏 {file_info._human_size()} | 
                            📅 {file_info.modified.strftime('%d/%m/%Y')}
                        </div>
                        {tags_html}
                    </div>
"""
    
    def generate_directory_index(self, scanner: DirectoryScanner, directory: Path, output_path: Path):
        """Génère un index.html pour un dossier spécifique"""
        
        files = scanner.get_files_in_dir(directory)
        subdirs = scanner.get_subdirs(directory)
        
        dir_name = directory.name if directory.name else "Racine"
        relative_from_root = directory.relative_to(scanner.root)
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dir_name} - Prof de Basse</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .breadcrumb {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .breadcrumb a {{
            color: white;
            text-decoration: none;
            border-bottom: 1px solid rgba(255,255,255,0.5);
        }}
        main {{ padding: 30px; }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .item-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }}
        .item-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
            cursor: pointer;
        }}
        .item-card:hover {{
            background: #e8eaf6;
            transform: translateX(5px);
        }}
        .item-name {{
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .item-meta {{
            font-size: 13px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📁 {dir_name}</h1>
            <div class="breadcrumb">
                <a href="/">🏠 Accueil</a> / {relative_from_root}
            </div>
        </header>
        
        <main>
"""
        
        # Sous-dossiers
        if subdirs:
            html += """
            <div class="section">
                <div class="section-title">📂 Sous-dossiers</div>
                <div class="item-grid">
"""
            for subdir in subdirs:
                subdir_name = subdir.name
                html += f"""
                    <div class="item-card" onclick="window.location.href='{subdir_name}/index.html'">
                        <div class="item-name">📂 {subdir_name}</div>
                    </div>
"""
            html += """
                </div>
            </div>
"""
        
        # Fichiers
        if files:
            html += """
            <div class="section">
                <div class="section-title">📄 Fichiers</div>
                <div class="item-grid">
"""
            for file_info in sorted(files, key=lambda x: x.name):
                url = file_info.get_url(self.base_url)
                icon = self._get_category_icon(file_info.category)
                
                html += f"""
                    <div class="item-card" onclick="window.open('{url}', '_blank')">
                        <div class="item-name">{icon} {file_info.name}</div>
                        <div class="item-meta">{file_info._human_size()}</div>
                    </div>
"""
            html += """
                </div>
            </div>
"""
        
        html += """
        </main>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Index créé : {output_path}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Fonction principale"""
    print("=" * 70)
    print("🎸 Prof de Basse - Générateur Automatique d'Index")
    print("=" * 70)
    print()
    
    # Détecter racine du projet
    root = Path.cwd()
    print(f"📂 Racine du projet : {root}")
    print()
    
    # Scanner
    scanner = DirectoryScanner(root)
    scanner.scan()
    print()
    
    # Générateur
    generator = IndexGenerator()
    
    # 1. Générer index racine
    print("📝 Génération index racine...")
    generator.generate_root_index(scanner, root / 'index.html')
    print()
    
    # 2. Générer index pour chaque dossier
    print("📝 Génération index par dossier...")
    for directory in scanner.directories:
        index_path = directory / 'index.html'
        generator.generate_directory_index(scanner, directory, index_path)
    
    print()
    print("=" * 70)
    print("✅ TERMINÉ ! Tous les index ont été générés.")
    print("=" * 70)

if __name__ == '__main__':
    main()
