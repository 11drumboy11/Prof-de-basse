#!/usr/bin/env python3
"""
Master Resources Index Generator for Prof de Basse
Scans all directories and creates a unified searchable index
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import mimetypes

# Configuration
REPO_ROOT = Path(__file__).parent.parent
BASE_URL = "https://11drumboy11.github.io/Prof-de-basse"

# Directories to scan
SCAN_DIRS = [
    "Methodes",
    "Partitions", 
    "Exercices",
    "Cours",
    "Real_Books",
    "Captures_PNG"
]

# File extensions to index
INDEXED_EXTENSIONS = {
    '.mp3': 'audio',
    '.pdf': 'document',
    '.html': 'document',
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.svg': 'image',
    '.json': 'data'
}

# Style/genre keywords for auto-tagging
STYLE_KEYWORDS = {
    'funk': ['funk', 'groove', 'ghost', 'slap'],
    'jazz': ['jazz', 'swing', 'walking', 'bebop', 'standard'],
    'rock': ['rock', 'metal', 'punk'],
    'blues': ['blues', '12bar', 'shuffle'],
    'latin': ['latin', 'samba', 'bossa', 'salsa', 'afrobeat'],
    'disco': ['disco', '70s'],
    'soul': ['soul', 'motown', 'r&b', 'rnb'],
    'reggae': ['reggae', 'ska', 'dub'],
    'fusion': ['fusion', 'prog']
}

# Level keywords
LEVEL_KEYWORDS = {
    'débutant': ['débutant', 'beginner', 'basic', 'intro', 'simple', 'easy'],
    'intermédiaire': ['intermédiaire', 'intermediate', 'medium'],
    'avancé': ['avancé', 'advanced', 'complex', 'expert', 'pro']
}

# Technique keywords
TECHNIQUE_KEYWORDS = {
    'slap': ['slap', 'thumb', 'pop'],
    'fingerstyle': ['fingerstyle', 'finger', 'plucking'],
    'picking': ['pick', 'plectrum', 'mediator'],
    'tapping': ['tap', 'tapping'],
    'harmonics': ['harmonic', 'harmonique'],
    'ghost_notes': ['ghost', 'note morte', 'étouffée']
}


def extract_track_number(filename: str) -> int:
    """Extract track number from filename"""
    match = re.search(r'[Tt]rack\s*(\d+)', filename)
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0


def extract_tags(text: str) -> List[str]:
    """Extract tags from text based on keywords"""
    tags = set()
    text_lower = text.lower()
    
    # Style tags
    for style, keywords in STYLE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.add(style)
    
    # Level tags
    for level, keywords in LEVEL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.add(level)
    
    # Technique tags
    for technique, keywords in TECHNIQUE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.add(technique)
    
    return sorted(list(tags))


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Extract information from a file"""
    relative_path = file_path.relative_to(REPO_ROOT)
    url = f"{BASE_URL}/{str(relative_path).replace(os.sep, '/')}"
    
    # Basic info
    info = {
        'filename': file_path.name,
        'path': str(relative_path),
        'url': url,
        'extension': file_path.suffix.lower(),
        'type': INDEXED_EXTENSIONS.get(file_path.suffix.lower(), 'other'),
        'size': file_path.stat().st_size,
        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
    }
    
    # Extract track number
    info['track_number'] = extract_track_number(file_path.name)
    
    # Generate search text from filename and path
    search_text = f"{file_path.name} {file_path.parent.name}"
    
    # Auto-generate title from filename
    title = file_path.stem
    title = re.sub(r'[_-]+', ' ', title)
    title = re.sub(r'\d{1,3}(?:\s*-\s*Track\s*\d+)?', '', title)
    title = title.strip()
    info['title'] = title or file_path.name
    
    # Extract tags
    info['tags'] = extract_tags(search_text)
    
    # Method/collection detection
    parts = relative_path.parts
    if len(parts) > 1:
        info['collection'] = parts[1]
    else:
        info['collection'] = parts[0]
    
    return info


def merge_existing_json(directory: Path) -> List[Dict[str, Any]]:
    """Merge existing songs_index.json files"""
    merged = []
    
    for json_file in directory.rglob('songs_index.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    merged.extend(data)
                elif isinstance(data, dict) and 'songs' in data:
                    merged.extend(data['songs'])
        except Exception as e:
            print(f"⚠️  Error reading {json_file}: {e}")
    
    return merged


def generate_master_index() -> Dict[str, Any]:
    """Generate the master index"""
    print("🔍 Scanning repository for resources...")
    
    all_resources = []
    stats = {
        'total_files': 0,
        'by_type': {},
        'by_collection': {}
    }
    
    # Scan each directory
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {scan_dir}")
            continue
        
        print(f"📂 Scanning {scan_dir}...")
        
        # First, merge existing JSON indexes
        existing = merge_existing_json(dir_path)
        if existing:
            print(f"  ✅ Merged {len(existing)} entries from existing indexes")
            all_resources.extend(existing)
        
        # Then scan for all files
        for file_path in dir_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            if file_path.suffix.lower() not in INDEXED_EXTENSIONS:
                continue
            
            # Skip already indexed files (avoid duplicates)
            if any(r.get('path') == str(file_path.relative_to(REPO_ROOT)) for r in all_resources):
                continue
            
            try:
                info = get_file_info(file_path)
                all_resources.append(info)
                stats['total_files'] += 1
                
                # Update stats
                file_type = info['type']
                stats['by_type'][file_type] = stats['by_type'].get(file_type, 0) + 1
                
                collection = info['collection']
                stats['by_collection'][collection] = stats['by_collection'].get(collection, 0) + 1
                
            except Exception as e:
                print(f"⚠️  Error processing {file_path}: {e}")
    
    # Sort resources
    all_resources.sort(key=lambda x: (x.get('collection', ''), x.get('track_number', 0), x.get('filename', '')))
    
    # Build master index
    master_index = {
        'generated_at': datetime.now().isoformat(),
        'version': '1.0.0',
        'base_url': BASE_URL,
        'total_resources': len(all_resources),
        'statistics': stats,
        'resources': all_resources
    }
    
    print(f"\n✅ Indexed {len(all_resources)} resources")
    print(f"📊 Statistics:")
    for type_name, count in stats['by_type'].items():
        print(f"   - {type_name}: {count}")
    
    return master_index


def generate_search_text_index(resources: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    """Generate full-text search index"""
    search_index = {}
    
    for idx, resource in enumerate(resources):
        # Build searchable text
        searchable = [
            resource.get('title', ''),
            resource.get('filename', ''),
            resource.get('collection', ''),
            ' '.join(resource.get('tags', []))
        ]
        
        text = ' '.join(searchable).lower()
        words = re.findall(r'\w+', text)
        
        # Index each word
        for word in words:
            if word not in search_index:
                search_index[word] = []
            if idx not in search_index[word]:
                search_index[word].append(idx)
    
    return search_index


def main():
    print("🎸 Prof de Basse - Master Index Generator")
    print("=" * 60)
    
    # Generate master index
    master_index = generate_master_index()
    
    # Generate search index
    print("\n🔍 Generating full-text search index...")
    search_index = generate_search_text_index(master_index['resources'])
    master_index['search_index'] = search_index
    print(f"✅ Indexed {len(search_index)} unique words")
    
    # Save to JSON
    output_file = REPO_ROOT / 'resources_index.json'
    print(f"\n💾 Saving to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Master index saved!")
    print(f"\n🌐 Access at: {BASE_URL}/resources_index.json")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
