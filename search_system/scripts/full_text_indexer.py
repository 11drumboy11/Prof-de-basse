#!/usr/bin/env python3
"""
Full-Text Indexer v1.0.0
Système d'indexation complète pour Prof de Basse

Crée un index inversé depuis songs_index.json et resources_index.json
pour permettre la recherche full-text ultra-rapide.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime


class FullTextIndexer:
    """Indexeur full-text avec index inversé"""
    
    def __init__(self):
        self.inverted_index: Dict[str, Dict] = defaultdict(lambda: {
            'documents': [],
            'frequencies': [],
            'positions': []
        })
        self.documents: Dict[str, Dict] = {}
        self.doc_id_counter = 0
        
    def normalize_text(self, text: str) -> str:
        """
        Normalise le texte pour la recherche
        - Lowercase
        - Supprime caractères spéciaux
        - Garde les espaces et tirets
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Garde lettres, chiffres, espaces, tirets, apostrophes
        text = re.sub(r"[^a-z0-9\s\-'àâäéèêëïîôùûüÿæœç]", " ", text)
        
        # Normalise espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Découpe le texte en tokens (mots)"""
        normalized = self.normalize_text(text)
        tokens = normalized.split()
        return tokens
    
    def add_document(self, doc_id: str, content: Dict, source: str):
        """
        Ajoute un document à l'index
        
        Args:
            doc_id: Identifiant unique du document
            content: Dictionnaire avec le contenu du document
            source: Source du document ('songs_index' ou 'resources_index')
        """
        # Extraire tout le texte indexable
        text_parts = []
        
        # Pour songs_index
        if source == 'songs_index':
            title = content.get('title', '')
            ocr_raw = content.get('ocr_raw', '')
            
            text_parts.append(title)
            text_parts.append(ocr_raw)
            
            # Stocker métadonnées
            self.documents[doc_id] = {
                'id': doc_id,
                'source': source,
                'title': title,
                'page': content.get('page'),
                'file': content.get('file'),
                'confidence': content.get('confidence'),
                'type': 'song'
            }
        
        # Pour resources_index
        elif source == 'resources_index':
            filename = content.get('filename', '')
            title = content.get('title', '')
            tags = content.get('tags', [])
            collection = content.get('collection', '')
            
            text_parts.append(filename)
            text_parts.append(title)
            text_parts.extend(tags)
            text_parts.append(collection)
            
            # Stocker métadonnées
            self.documents[doc_id] = {
                'id': doc_id,
                'source': source,
                'filename': filename,
                'title': title,
                'path': content.get('path', ''),
                'url': content.get('url', ''),
                'extension': content.get('extension', ''),
                'type': content.get('type', ''),
                'collection': collection,
                'tags': tags,
                'track_number': content.get('track_number', 0)
            }
        
        # Combiner tout le texte
        full_text = ' '.join(text_parts)
        
        # Tokenizer
        tokens = self.tokenize(full_text)
        
        # Indexer chaque token
        word_positions = defaultdict(list)
        for position, token in enumerate(tokens):
            word_positions[token].append(position)
        
        # Ajouter à l'index inversé
        for word, positions in word_positions.items():
            self.inverted_index[word]['documents'].append(doc_id)
            self.inverted_index[word]['frequencies'].append(len(positions))
            self.inverted_index[word]['positions'].append(positions)
    
    def index_songs(self, songs_path: str):
        """Indexe le fichier songs_index.json"""
        print(f"📖 Indexation de {songs_path}...")
        
        with open(songs_path, 'r', encoding='utf-8') as f:
            songs_data = json.load(f)
        
        for key, song_data in songs_data.items():
            doc_id = f"song_{self.doc_id_counter}"
            self.add_document(doc_id, song_data, 'songs_index')
            self.doc_id_counter += 1
        
        print(f"  ✅ {len(songs_data)} morceaux indexés")
    
    def index_resources(self, resources_path: str):
        """Indexe le fichier resources_index.json"""
        print(f"📖 Indexation de {resources_path}...")
        
        with open(resources_path, 'r', encoding='utf-8') as f:
            resources_data = json.load(f)
        
        resources = resources_data.get('resources', [])
        
        for resource in resources:
            doc_id = f"resource_{self.doc_id_counter}"
            self.add_document(doc_id, resource, 'resources_index')
            self.doc_id_counter += 1
        
        print(f"  ✅ {len(resources)} ressources indexées")
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques de l'index"""
        total_words = 0
        for data in self.inverted_index.values():
            frequencies = data.get('frequencies', [])
            if isinstance(frequencies, list):
                total_words += sum(frequencies)
        
        return {
            'total_documents': len(self.documents),
            'total_unique_words': len(self.inverted_index),
            'total_words_indexed': total_words,
            'songs_count': sum(1 for doc in self.documents.values() if doc['source'] == 'songs_index'),
            'resources_count': sum(1 for doc in self.documents.values() if doc['source'] == 'resources_index')
        }
    
    def save_index(self, output_path: str):
        """Sauvegarde l'index dans un fichier JSON"""
        print(f"\n💾 Sauvegarde de l'index dans {output_path}...")
        
        # Préparer structure
        index_data = {
            'metadata': {
                'version': '1.0.0',
                'generated_at': datetime.now().isoformat(),
                'description': 'Index inversé full-text pour Prof de Basse',
                'statistics': self.get_statistics()
            },
            'inverted_index': dict(self.inverted_index),
            'documents': self.documents
        }
        
        # Sauvegarder
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        stats = self.get_statistics()
        print(f"\n✅ Index sauvegardé avec succès !")
        print(f"  📊 {stats['total_documents']:,} documents")
        print(f"  📝 {stats['total_unique_words']:,} mots uniques")
        print(f"  🎵 {stats['songs_count']:,} morceaux")
        print(f"  📁 {stats['resources_count']:,} ressources")


def main():
    """Fonction principale d'indexation"""
    print("=" * 60)
    print("🔍 FULL-TEXT INDEXER - Prof de Basse")
    print("=" * 60)
    print()
    
    # Chemins des fichiers
    songs_path = '/mnt/user-data/uploads/songs_index.json'
    resources_path = '/mnt/user-data/uploads/resources_index.json'
    output_path = '/mnt/user-data/outputs/search_index.json'
    
    # Créer indexeur
    indexer = FullTextIndexer()
    
    # Indexer les fichiers
    indexer.index_songs(songs_path)
    indexer.index_resources(resources_path)
    
    # Sauvegarder
    indexer.save_index(output_path)
    
    print(f"\n🎸 Index prêt pour la recherche full-text !")


if __name__ == '__main__':
    main()
