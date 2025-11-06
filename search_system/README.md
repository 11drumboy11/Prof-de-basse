# 🔍 Super Moteur de Recherche Full-Text

## Installation

### 1. Structure des fichiers

```
search_system/
├── data/
│   └── search_index.json     # Index inversé (1.3 MB)
├── scripts/
│   ├── search_engine.py      # Moteur de recherche
│   └── full_text_indexer.py  # Indexeur
└── docs/
    ├── README.md             # Documentation complète
    └── dashboard.html        # Dashboard visuel
```

### 2. Utilisation

```python
from scripts.search_engine import search_documents

# Rechercher un morceau
results = search_documents("so what")
print(results['total_results'])
```

### 3. Mise à jour de l'index

```bash
cd search_system
python3 scripts/full_text_indexer.py
```

## Statistiques

- **1,288 documents** indexés
- **1,658 mots** uniques
- **354 morceaux** (Real Books)
- **934 ressources** (MP3, méthodes)

## Documentation

Voir [docs/README.md](docs/README.md) pour la documentation complète.
