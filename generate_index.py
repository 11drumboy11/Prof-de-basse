#!/usr/bin/env python3
"""
Script pour générer automatiquement index.html basé sur la structure du repository
Usage: python generate_index.py
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# Configuration
REPO_ROOT = Path(".")
LEVELS_PATTERN = re.compile(r'^Niveau-(\d+)$', re.IGNORECASE)
LESSON_PATTERN = re.compile(r'^.*\.html?$', re.IGNORECASE)
AUDIO_PATTERNS = ['.mp3', '.mid', '.midi']

def scan_repository():
    """Scanne le repository et organise les fichiers"""
    levels = {}
    stats = {
        'levels': 0,
        'lessons': 0,
        'audio': 0
    }
    
    # Parcourir tous les dossiers
    for item in REPO_ROOT.iterdir():
        if not item.is_dir():
            continue
            
        # Vérifier si c'est un dossier de niveau
        match = LEVELS_PATTERN.match(item.name)
        if match:
            level_num = int(match.group(1))
            level_name = f"Niveau-{level_num}"
            
            # Trouver toutes les leçons HTML dans ce dossier
            lessons = []
            for lesson_file in item.glob('*.html'):
                if lesson_file.name.lower() != 'index.html':
                    lessons.append({
                        'name': lesson_file.name,
                        'path': f"{level_name}/{lesson_file.name}",
                        'title': format_lesson_title(lesson_file.name)
                    })
                    stats['lessons'] += 1
            
            if lessons:
                # Trier les leçons par numéro
                lessons.sort(key=lambda x: extract_lesson_number(x['name']))
                levels[level_num] = {
                    'name': level_name,
                    'lessons': lessons
                }
                stats['levels'] += 1
    
    # Compter les fichiers audio
    for ext in AUDIO_PATTERNS:
        stats['audio'] += len(list(REPO_ROOT.rglob(f'*{ext}')))
    
    return levels, stats

def extract_lesson_number(filename):
    """Extrait le numéro de leçon du nom de fichier"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0

def format_lesson_title(filename):
    """Formate le nom de fichier en titre lisible"""
    title = filename.replace('.html', '').replace('-', ' ').replace('_', ' ')
    return ' '.join(word.capitalize() for word in title.split())

def generate_html(levels, stats):
    """Génère le code HTML de l'index"""
    
    # Générer les sections de niveaux
    levels_html = ""
    for level_num in sorted(levels.keys()):
        level = levels[level_num]
        lessons_html = ""
        
        for idx, lesson in enumerate(level['lessons'], 1):
            lessons_html += f"""
                <li class="lesson-item" style="animation-delay: {idx * 0.1}s">
                    <a href="./{lesson['path']}" class="lesson-link">
                        <span class="lesson-number">{idx}</span>
                        <span>{lesson['title']}</span>
                    </a>
                </li>"""
        
        badge_text = "DÉBUTANT" if level_num == 1 else "INTERMÉDIAIRE" if level_num == 2 else f"NIVEAU {level_num}"
        
        levels_html += f"""
            <div class="level-section">
                <h3>
                    <span class="level-badge">{badge_text}</span>
                    {len(level['lessons'])} leçon{'s' if len(level['lessons']) > 1 else ''}
                </h3>
                <ul class="lessons-list">
                    {lessons_html}
                </ul>
            </div>"""
    
    # Template HTML complet
    html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Prof de Basse - Méthode interactive d'apprentissage de la basse électrique">
    <meta name="generator" content="Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}">
    <title>Prof de Basse - Apprendre la basse en ligne</title>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary-color: #FF6B35;
            --secondary-color: #004E89;
            --accent-color: #F7B267;
            --dark-bg: #1a1a2e;
            --light-bg: #16213e;
            --text-light: #ffffff;
            --text-gray: #b4b4b4;
            --success: #4CAF50;
            --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--light-bg) 100%);
            color: var(--text-light);
            min-height: 100vh;
            line-height: 1.6;
        }}

        header {{
            background: rgba(26, 26, 46, 0.95);
            padding: 1.5rem 0;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
            position: sticky;
            top: 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }}

        nav {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}

        .logo {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .logo span {{
            font-size: 2.5rem;
        }}

        .nav-links {{
            display: flex;
            gap: 2rem;
            list-style: none;
        }}

        .nav-links a {{
            color: var(--text-light);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }}

        .nav-links a:hover {{
            color: var(--primary-color);
            background: rgba(255, 107, 53, 0.1);
        }}

        .hero {{
            max-width: 1200px;
            margin: 4rem auto;
            padding: 0 2rem;
            text-align: center;
        }}

        .hero h1 {{
            font-size: 3.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .hero p {{
            font-size: 1.3rem;
            color: var(--text-gray);
            margin-bottom: 2rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }}

        .cta-buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 2rem;
        }}

        .btn {{
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .btn-primary {{
            background: var(--primary-color);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        }}

        .btn-primary:hover {{
            background: #ff5522;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.6);
        }}

        .btn-secondary {{
            background: transparent;
            color: var(--text-light);
            border: 2px solid var(--primary-color);
        }}

        .btn-secondary:hover {{
            background: var(--primary-color);
            transform: translateY(-2px);
        }}

        .section {{
            max-width: 1200px;
            margin: 5rem auto;
            padding: 0 2rem;
        }}

        .section-title {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: var(--accent-color);
        }}

        .lessons-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}

        .level-section {{
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: var(--card-shadow);
            border: 2px solid rgba(255, 107, 53, 0.3);
        }}

        .level-section h3 {{
            color: var(--primary-color);
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .level-badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            background: var(--primary-color);
            color: white;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .lessons-list {{
            list-style: none;
        }}

        .lesson-item {{
            margin-bottom: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            transition: all 0.3s;
            border-left: 3px solid transparent;
        }}

        .lesson-item:hover {{
            background: rgba(255, 107, 53, 0.1);
            border-left-color: var(--primary-color);
            transform: translateX(5px);
        }}

        .lesson-link {{
            color: var(--text-light);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .lesson-link:hover {{
            color: var(--primary-color);
        }}

        .lesson-number {{
            background: var(--primary-color);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            flex-shrink: 0;
        }}

        .stats {{
            max-width: 1200px;
            margin: 5rem auto;
            padding: 3rem 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 2rem;
            text-align: center;
        }}

        .stat-item h4 {{
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }}

        .stat-item p {{
            color: var(--text-gray);
            font-size: 1rem;
        }}

        footer {{
            background: rgba(26, 26, 46, 0.95);
            padding: 3rem 2rem;
            margin-top: 5rem;
            text-align: center;
        }}

        .footer-content {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .footer-text {{
            color: var(--text-gray);
            margin-top: 2rem;
        }}

        .footer-text a {{
            color: var(--primary-color);
            text-decoration: none;
        }}

        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.5rem;
            }}

            .nav-links {{
                flex-direction: column;
                gap: 0.5rem;
            }}

            .lessons-container {{
                grid-template-columns: 1fr;
            }}
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .lesson-item {{
            animation: fadeIn 0.5s ease-out;
        }}
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo">
                <span>🎸</span>
                <span>Prof de Basse</span>
            </div>
            <ul class="nav-links">
                <li><a href="#accueil">Accueil</a></li>
                <li><a href="#lecons">Leçons</a></li>
                <li><a href="https://github.com/11drumboy11/Prof-de-basse" target="_blank">GitHub</a></li>
            </ul>
        </nav>
    </header>

    <section class="hero" id="accueil">
        <h1>Apprenez la Basse Électrique</h1>
        <p>Une méthode interactive et progressive pour maîtriser la basse, avec des leçons structurées et des exemples audio</p>
        
        <div class="cta-buttons">
            <a href="#lecons" class="btn btn-primary">
                🚀 Voir les leçons
            </a>
            <a href="https://github.com/11drumboy11/Prof-de-basse" target="_blank" class="btn btn-secondary">
                ⭐ GitHub
            </a>
        </div>
    </section>

    <section class="stats">
        <div class="stats-grid">
            <div class="stat-item">
                <h4>{stats['levels']}</h4>
                <p>Niveau{'x' if stats['levels'] > 1 else ''}</p>
            </div>
            <div class="stat-item">
                <h4>{stats['lessons']}</h4>
                <p>Leçon{'s' if stats['lessons'] > 1 else ''}</p>
            </div>
            <div class="stat-item">
                <h4>{stats['audio']}</h4>
                <p>Fichiers audio</p>
            </div>
        </div>
    </section>

    <section class="section" id="lecons">
        <h2 class="section-title">📚 Leçons disponibles</h2>
        
        <div class="lessons-container">
            {levels_html}
        </div>
    </section>

    <footer>
        <div class="footer-content">
            <div class="logo" style="justify-content: center; margin-bottom: 1rem;">
                <span>🎸</span>
                <span>Prof de Basse</span>
            </div>
            
            <p style="color: var(--text-gray); margin-bottom: 1.5rem;">
                Méthode interactive d'apprentissage de la basse électrique
            </p>
            
            <div class="footer-text">
                <p>&copy; 2024 Prof de Basse. Projet open source.</p>
                <p style="margin-top: 0.5rem;">
                    Créé avec ❤️ par <a href="https://github.com/11drumboy11" target="_blank">11drumboy11</a>
                </p>
                <p style="margin-top: 1rem; font-size: 0.9rem;">
                    Généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
                </p>
            </div>
        </div>
    </footer>

    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>"""
    
    return html_template

def main():
    """Fonction principale"""
    print("🎸 Prof de Basse - Générateur d'index automatique")
    print("=" * 50)
    
    print("\n📁 Scan du repository...")
    levels, stats = scan_repository()
    
    print(f"✅ Trouvé: {stats['levels']} niveau(x), {stats['lessons']} leçon(s), {stats['audio']} fichier(s) audio")
    
    print("\n🔨 Génération de index.html...")
    html_content = generate_html(levels, stats)
    
    output_file = REPO_ROOT / "index.html"
    output_file.write_text(html_content, encoding='utf-8')
    
    print(f"✅ Fichier généré: {output_file}")
    print(f"📊 Statistiques:")
    print(f"   - Niveaux: {stats['levels']}")
    print(f"   - Leçons: {stats['lessons']}")
    print(f"   - Fichiers audio: {stats['audio']}")
    print("\n✨ Terminé!")

if __name__ == "__main__":
    main()
