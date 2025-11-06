#!/usr/bin/env python3
"""
Full-Text Search Engine v1.0.0
Moteur de recherche pour Prof de Basse

Recherche exacte de phrases dans l'index inversé pré-calculé.
Conçu pour être appelé automatiquement par le GPT pendant les conversations.
"""

import json
import re
from typing import Dict, List, Tuple
from pathlib import Path


class FullTextSearchEngine:
    """Moteur de recherche full-text"""
    
    def __init__(self, index_path: str):
        """
        Initialise le moteur de recherche
        
        Args:
            index_path: Chemin vers le fichier search_index.json
        """
        print(f"📚 Chargement de l'index depuis {index_path}...")
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        self.metadata = index_data['metadata']
        self.inverted_index = index_data['inverted_index']
        self.documents = index_data['documents']
        
        stats = self.metadata['statistics']
        print(f"✅ Index chargé : {stats['total_documents']:,} docs, {stats['total_unique_words']:,} mots")
    
    def normalize_text(self, text: str) -> str:
        """Normalise le texte (identique à l'indexeur)"""
        if not text:
            return ""
        
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s\-'àâäéèêëïîôùûüÿæœç]", " ", text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Découpe le texte en tokens"""
        normalized = self.normalize_text(text)
        return normalized.split()
    
    def search_exact_phrase(self, phrase: str) -> List[Dict]:
        """
        Recherche une phrase exacte
        
        Args:
            phrase: Phrase à rechercher (ex: "gamme mineure")
        
        Returns:
            Liste de documents contenant la phrase exacte, avec score de pertinence
        """
        # Tokenizer la phrase
        query_tokens = self.tokenize(phrase)
        
        if not query_tokens:
            return []
        
        # Si un seul mot, recherche simple
        if len(query_tokens) == 1:
            return self._search_single_word(query_tokens[0])
        
        # Sinon, recherche de phrase multi-mots
        return self._search_multi_word_phrase(query_tokens)
    
    def _search_single_word(self, word: str) -> List[Dict]:
        """Recherche un seul mot"""
        if word not in self.inverted_index:
            return []
        
        word_data = self.inverted_index[word]
        doc_ids = word_data['documents']
        frequencies = word_data['frequencies']
        
        results = []
        for doc_id, freq in zip(doc_ids, frequencies):
            doc = self.documents.get(doc_id)
            if doc:
                results.append({
                    'document': doc,
                    'score': freq,  # Score = fréquence du mot
                    'matched_phrase': word
                })
        
        # Trier par score décroissant
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _search_multi_word_phrase(self, tokens: List[str]) -> List[Dict]:
        """
        Recherche une phrase multi-mots (recherche exacte)
        
        Trouve les documents où tous les mots apparaissent CONSÉCUTIVEMENT
        """
        # Trouver les documents contenant TOUS les mots
        doc_sets = []
        for token in tokens:
            if token in self.inverted_index:
                docs = set(self.inverted_index[token]['documents'])
                doc_sets.append(docs)
            else:
                # Si un mot n'existe pas, aucun résultat
                return []
        
        # Intersection : documents contenant tous les mots
        common_docs = set.intersection(*doc_sets)
        
        if not common_docs:
            return []
        
        # Vérifier que les mots sont consécutifs (phrase exacte)
        results = []
        
        for doc_id in common_docs:
            # Récupérer les positions de chaque mot
            positions_lists = []
            for token in tokens:
                word_data = self.inverted_index[token]
                doc_index = word_data['documents'].index(doc_id)
                positions = word_data['positions'][doc_index]
                positions_lists.append(set(positions))
            
            # Vérifier si la phrase existe (positions consécutives)
            phrase_found = self._check_consecutive_positions(positions_lists, len(tokens))
            
            if phrase_found:
                # Calculer score (somme des fréquences)
                score = sum(len(pos_set) for pos_set in positions_lists)
                
                doc = self.documents.get(doc_id)
                if doc:
                    results.append({
                        'document': doc,
                        'score': score,
                        'matched_phrase': ' '.join(tokens)
                    })
        
        # Trier par score décroissant
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _check_consecutive_positions(self, positions_lists: List[set], num_words: int) -> bool:
        """
        Vérifie si les positions forment une séquence consécutive
        
        Args:
            positions_lists: Liste de sets de positions pour chaque mot
            num_words: Nombre de mots dans la phrase
        
        Returns:
            True si au moins une occurrence consécutive existe
        """
        # Pour chaque position du premier mot
        for start_pos in positions_lists[0]:
            # Vérifier si les mots suivants sont aux positions +1, +2, etc.
            is_consecutive = True
            for i in range(1, num_words):
                expected_pos = start_pos + i
                if expected_pos not in positions_lists[i]:
                    is_consecutive = False
                    break
            
            if is_consecutive:
                return True
        
        return False
    
    def search(self, query: str, max_results: int = 20) -> Dict:
        """
        Fonction de recherche principale (pour appel GPT)
        
        Args:
            query: Requête de recherche
            max_results: Nombre maximum de résultats
        
        Returns:
            Dictionnaire avec métadonnées et résultats
        """
        results = self.search_exact_phrase(query)
        
        # Limiter les résultats
        results = results[:max_results]
        
        # Formater la réponse
        return {
            'query': query,
            'total_results': len(results),
            'results': results,
            'metadata': {
                'search_type': 'exact_phrase',
                'index_version': self.metadata['version'],
                'total_documents_searched': self.metadata['statistics']['total_documents']
            }
        }
    
    def format_results_for_display(self, search_results: Dict) -> str:
        """
        Formate les résultats pour affichage lisible
        
        Args:
            search_results: Résultats de la fonction search()
        
        Returns:
            String formaté pour affichage
        """
        output = []
        output.append("=" * 60)
        output.append(f"🔍 Recherche : \"{search_results['query']}\"")
        output.append(f"📊 {search_results['total_results']} résultat(s) trouvé(s)")
        output.append("=" * 60)
        output.append("")
        
        for i, result in enumerate(search_results['results'], 1):
            doc = result['document']
            score = result['score']
            phrase = result['matched_phrase']
            
            output.append(f"[{i}] Score: {score}")
            
            if doc['source'] == 'songs_index':
                output.append(f"    🎵 Morceau : {doc['title']}")
                output.append(f"    📄 Page : {doc['page']}")
                output.append(f"    📁 Fichier : {doc['file']}")
            else:  # resources_index
                output.append(f"    📁 Fichier : {doc['filename']}")
                output.append(f"    📚 Collection : {doc['collection']}")
                if doc.get('tags'):
                    output.append(f"    🏷️  Tags : {', '.join(doc['tags'])}")
                output.append(f"    🔗 URL : {doc['url']}")
            
            output.append("")
        
        return '\n'.join(output)


def search_documents(query: str, max_results: int = 20, index_path: str = '/mnt/user-data/outputs/search_index.json') -> Dict:
    """
    Fonction principale pour recherche (appelable par GPT)
    
    Args:
        query: Requête de recherche (ex: "gamme mineure")
        max_results: Nombre maximum de résultats
        index_path: Chemin vers l'index (par défaut dans outputs)
    
    Returns:
        Dictionnaire avec les résultats de recherche
    """
    engine = FullTextSearchEngine(index_path)
    return engine.search(query, max_results)


def main():
    """Fonction de test en CLI"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 search_engine.py \"votre requête\"")
        print("Exemple: python3 search_engine.py \"gamme mineure\"")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    
    # Rechercher
    results = search_documents(query)
    
    # Afficher
    engine = FullTextSearchEngine('/mnt/user-data/outputs/search_index.json')
    formatted = engine.format_results_for_display(results)
    print(formatted)


if __name__ == '__main__':
    main()
