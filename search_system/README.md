# 🔍 Universal Resource Finder - Prof de Basse

## Vue d'ensemble

Système de recherche complet pour naviguer parmi **363+ ressources pédagogiques** :
- 📚 **99 MP3** : 70s Funk & Disco Bass
- 🎸 **50 MP3** : John Liebman Funk Fusion
- 📖 **100+ standards** : Real Books (Jazz, Funk/Soul)
- 💪 **Exercices techniques** : Tous niveaux

## 🚀 Installation

### Option 1 : Interface HTML standalone (Recommandée)

Ouvrir simplement `universal-search-system.html` dans un navigateur. Tout fonctionne en local !

```bash
# Ouvrir dans votre navigateur
open universal-search-system.html
# ou double-cliquer sur le fichier
```

### Option 2 : Avec index JSON (Pour grandes bases)

1. **Générer l'index** :
```bash
python generate_search_index.py
```

2. **Ouvrir l'interface** :
```bash
open universal-search-system.html
```

## 📁 Structure des fichiers

```
search_system/
├── universal-search-system.html  # Interface de recherche principale
├── config.json                   # Configuration globale
├── generate_search_index.py      # Générateur d'index automatique
├── data/
│   └── search_index.json        # Index complet (généré)
└── README.md                     # Cette documentation
```

## 🎯 Fonctionnalités

### Recherche instantanée
- ⚡ **Recherche textuelle** : Par titre, artiste, compositeur, description
- 🔍 **Recherche intelligente** : Détection automatique de patterns (Track 12, So What, etc.)
- 📊 **Filtres multiples** : Type, style, niveau, technique
- 🎨 **Interface moderne** : Design responsive et élégant

### Filtres disponibles

#### 📁 Type de ressource
- MP3
- Méthode complète
- Real Book
- Exercice technique

#### 🎸 Style musical
- Funk
- Jazz
- Disco
- Slap
- Rock
- Blues
- Latin

#### 📊 Niveau
- Débutant
- Intermédiaire
- Avancé

#### 🎯 Technique
- Fingerstyle
- Slap
- Ghost Notes
- Walking Bass
- Arpèges
- Gammes

## 💡 Exemples d'utilisation

### Recherche simple
```
Recherche : "funk"
Résultat : Tous les tracks funk (99 MP3 de 70s Funk & Disco)
```

### Recherche par numéro de track
```
Recherche : "Track 12"
Résultat : Track 12 de 70s Funk & Disco + Track 12 de Liebman
```

### Recherche par compositeur
```
Recherche : "Miles Davis"
Résultat : So What (Real Book Jazz)
```

### Recherche combinée
```
Recherche : "walking"
Filtre Style : Jazz
Filtre Niveau : Intermédiaire
Résultat : Standards jazz avec walking bass niveau intermédiaire
```

## 🔧 Personnalisation

### Modifier la configuration

Éditer `config.json` :

```json
{
  "search_settings": {
    "max_results_display": 50,  // Nombre max de résultats
    "search_delay_ms": 300,     // Délai avant recherche (ms)
    "enable_fuzzy_search": true // Recherche approximative
  }
}
```

### Ajouter de nouvelles ressources

Éditer `generate_search_index.py` et ajouter dans la méthode appropriée :

```python
def generate_new_method_resources(self):
    """Génère les entrées pour une nouvelle méthode"""
    for i in range(1, 51):
        resource = {
            "id": f"new-method-{i}",
            "title": f"Exercise {i}",
            "type": "mp3",
            "source": "New Method Name",
            "url": f"{REPO_BASE}Path/To/File.mp3",
            "style": "rock",
            "level": "intermediate",
            "technique": "fingerstyle"
        }
        self.add_resource(resource)
```

Puis regénérer l'index :
```bash
python generate_search_index.py
```

## 📊 Statistiques

L'interface affiche automatiquement :
- 📈 **Ressources totales** : Nombre total dans la base
- 🔍 **Résultats affichés** : Nombre après filtres
- 🎧 **Fichiers MP3** : 363+ disponibles

## 🎨 Interface

### Design responsive
- 💻 **Desktop** : Layout 4 colonnes pour les filtres
- 📱 **Mobile** : Layout adaptatif avec filtres empilés

### Couleurs du thème
- **Primaire** : #667eea (Violet)
- **Secondaire** : #764ba2 (Pourpre)
- **Succès** : #4caf50 (Vert)
- **Info** : #2196F3 (Bleu)

### Badges colorés
- **Style** : Orange (#e65100)
- **Niveau** : Bleu (#1565c0)
- **Technique** : Vert (#2e7d32)

## 🚀 Performance

- ⚡ **Recherche instantanée** : < 0.1s pour 363+ ressources
- 📦 **Léger** : ~100KB (HTML + JS intégré)
- 🔒 **Aucune dépendance** : Fonctionne 100% en local
- 🌐 **Pas de serveur** : Tout s'exécute dans le navigateur

## 🔗 Liens utiles

- **Repo GitHub** : https://github.com/11drumboy11/Prof-de-basse
- **Site principal** : https://11drumboy11.github.io/Prof-de-basse/
- **Documentation** : Voir les 4 HTML de référence dans le repo

## 📝 Format des ressources

Chaque ressource dans l'index contient :

```json
{
  "id": "funk-disco-12",
  "title": "Track 12",
  "type": "mp3",
  "source": "70s Funk & Disco Bass",
  "url": "https://11drumboy11.github.io/Prof-de-basse/Methodes/...",
  "style": "funk",
  "level": "beginner",
  "technique": "fingerstyle",
  "tempo": 102,
  "description": "Exercice de funk niveau débutant",
  "tags": ["funk", "beginner", "fingerstyle"],
  "searchable_text": "track 12 funk disco beginner fingerstyle"
}
```

## 🛠️ Développement

### Ajouter un nouveau type de filtre

1. Modifier `config.json` :
```json
"filters": {
  "new_filter": {
    "label": "🎵 Nouveau Filtre",
    "options": [...]
  }
}
```

2. Modifier `universal-search-system.html` :
```html
<select id="filterNew">...</select>
```

3. Ajouter la logique de filtrage dans `performSearch()`

### Debug

Ouvrir la console du navigateur (F12) pour voir :
- Nombre de ressources chargées
- Temps de recherche
- Erreurs éventuelles

## 📄 License

MIT - Libre d'utilisation pour Prof de Basse

## 🎸 Auteur

**Prof de Basse** - Expert pédagogue inspiré de Berklee, Victor Wooten, Adam Neely

---

**Version** : 1.0.0  
**Dernière mise à jour** : 6 novembre 2025
