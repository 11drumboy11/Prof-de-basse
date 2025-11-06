# 📊 STRUCTURE DU MEGA-INDEX

## 🎯 Vue d'ensemble

Le fichier `mega-search-index.json` contient **TOUTES** tes ressources dans un format unifié et optimisé pour la recherche.

---

## 📄 Structure Globale

```json
{
  "version": "3.0.0-MEGA",
  "generated_at": "2025-11-06T15:30:00.000Z",
  "total_resources": 1125,
  "sources": [
    "Prof-de-basse-OCR/search_index_ocr.json",
    "resources/resources_index.json",
    "resources/complete-resource-map.json",
    "Real_Books/Real_book_jazz/songs_index.json",
    "Methodes/70 Funk & Disco bass MP3/songs_index.json"
  ],
  "statistics": {
    "by_type": {
      "mp3": 363,
      "pdf": 71,
      "image": 508,
      "html": 56,
      "data": 127
    },
    "sources_merged": 8
  },
  "resources": [
    // ... toutes les ressources ci-dessous
  ]
}
```

---

## 📦 Format d'une Ressource

Chaque ressource dans le tableau `resources` suit ce format standard :

```json
{
  "id": "Methodes/70 Funk & Disco bass MP3/Track 01.mp3",
  "title": "Funk Groove Introduction",
  "type": "mp3",
  "url": "https://11drumboy11.github.io/Prof-de-basse/Methodes/70%20Funk%20%26%20Disco%20bass%20MP3/Track%2001.mp3",
  "source": "resources_index.json",
  "metadata": {
    "techniques": ["fingerstyle", "ghost notes"],
    "styles": ["funk"],
    "level": "débutant",
    "tempo": 90,
    "track": "01",
    "duration": "2:30"
  },
  "search_text": "funk groove introduction fingerstyle ghost notes débutant"
}
```

---

## 🎵 EXEMPLE 1 : MP3 (70s Funk)

```json
{
  "id": "Methodes/70 Funk & Disco bass MP3/Track 12.mp3",
  "title": "Get Up Style - Groove with Ghost Notes",
  "type": "mp3",
  "url": "https://11drumboy11.github.io/Prof-de-basse/Methodes/70%20Funk%20%26%20Disco%20bass%20MP3/Track%2012.mp3",
  "source": "complete-resource-map.json",
  "metadata": {
    "techniques": ["ghost notes", "fingerstyle", "syncopation"],
    "styles": ["funk", "james brown"],
    "level": "intermédiaire",
    "tempo": 100,
    "track": "12",
    "pattern": null,
    "duration": "3:15",
    "description": "Pattern funk inspiré de James Brown avec ghost notes et syncopations"
  },
  "search_text": "get up style groove ghost notes funk james brown intermédiaire fingerstyle syncopation"
}
```

**Utilisation :**
```javascript
// Chercher tous les MP3 funk intermédiaires
search('funk', { type: 'mp3', level: 'intermédiaire' })
```

---

## 🎼 EXEMPLE 2 : Partition Real Book (PNG)

```json
{
  "id": "Real_Books/Real_book_jazz/assets/page_0409.jpg",
  "title": "So What",
  "type": "image",
  "url": "https://11drumboy11.github.io/Prof-de-basse/Real_Books/Real_book_jazz/assets/page_0409.jpg",
  "source": "Real_book_jazz/songs_index.json",
  "metadata": {
    "composer": "Miles Davis",
    "page": 409,
    "key": "Dm",
    "tempo": 132,
    "styles": ["jazz", "modal"],
    "techniques": ["walking bass", "modal improvisation"],
    "level": "intermédiaire",
    "ocr_text": "So What Miles Davis Dm modal composition Kind of Blue 1959",
    "description": "Composition modale emblématique de Miles Davis utilisant le mode dorien"
  },
  "search_text": "so what miles davis dm modal composition kind of blue 1959 jazz walking bass dorien intermédiaire"
}
```

**Utilisation :**
```javascript
// Chercher "So What"
searchExact('So What')

// Chercher toutes partitions Miles Davis
search('Miles Davis', { type: 'image' })
```

---

## 📄 EXEMPLE 3 : PDF Théorie

```json
{
  "id": "Theorie/Gammes_et_Modes.pdf",
  "title": "Gammes et Modes - Guide Complet",
  "type": "pdf",
  "url": "https://11drumboy11.github.io/Prof-de-basse/Theorie/Gammes_et_Modes.pdf",
  "source": "search_index_ocr.json",
  "metadata": {
    "styles": ["théorie"],
    "techniques": ["gammes", "modes", "intervalles"],
    "level": "tous niveaux",
    "tags": ["dorien", "mixolydien", "pentatonique"],
    "ocr_text": "Gammes et modes pour bassistes. Gamme majeure, gamme mineure naturelle, gamme pentatonique mineure, modes grecs : ionien, dorien, phrygien, lydien, mixolydien, éolien, locrien. Application pratique sur le manche.",
    "pages": [5, 12, 18, 24],
    "size": "2.5 MB"
  },
  "search_text": "gammes modes guide complet théorie dorien mixolydien pentatonique majeure mineure ionien phrygien lydien éolien locrien manche"
}
```

**Utilisation :**
```javascript
// Chercher "gamme pentatonique mineure"
search('gamme pentatonique mineure')

// Chercher tout sur les modes
search('modes', { type: 'pdf' })
```

---

## 🖼️ EXEMPLE 4 : Capture Méthode (PNG)

```json
{
  "id": "Methodes/70 Funk & Disco bass/assets/page_0010.jpg",
  "title": "Pattern 31 - Slap Funk Advanced",
  "type": "image",
  "url": "https://11drumboy11.github.io/Prof-de-basse/Methodes/70%20Funk%20%26%20Disco%20bass/assets/page_0010.jpg",
  "source": "search_index_ocr.json",
  "metadata": {
    "pattern": "31",
    "track": "31",
    "page": 10,
    "techniques": ["slap", "pop", "thumb"],
    "styles": ["funk"],
    "level": "avancé",
    "tempo": 110,
    "key": "Em",
    "ocr_text": "Pattern 31 Slap technique avancée avec doubles croches syncopées Track 31 Tempo 110 BPM",
    "description": "Pattern slap funk avancé avec technique double-thumb"
  },
  "search_text": "pattern 31 slap funk advanced pop thumb em doubles croches syncopées tempo 110"
}
```

**Utilisation :**
```javascript
// Chercher Pattern 31
search('pattern 31')

// Chercher tous les exercices slap avancés
search('slap', { level: 'avancé' })
```

---

## 📝 EXEMPLE 5 : Cours HTML

```json
{
  "id": "Cours/Cours_Funk_Debutant.html",
  "title": "Cours Complet : Funk pour Débutant",
  "type": "html",
  "url": "https://11drumboy11.github.io/Prof-de-basse/Cours/Cours_Funk_Debutant.html",
  "source": "resources_index.json",
  "metadata": {
    "styles": ["funk"],
    "level": "débutant",
    "techniques": ["fingerstyle", "ghost notes", "groove"],
    "tags": ["cours complet", "5 parties", "james brown"],
    "content": "Cours 5 parties : Échauffement, Théorie, Application, Improvisation, Fun. Découverte du funk avec James Jamerson et Bootsy Collins.",
    "duration": "60 min",
    "exercises": 8
  },
  "search_text": "cours complet funk débutant fingerstyle ghost notes groove james brown jamerson bootsy collins 5 parties"
}
```

**Utilisation :**
```javascript
// Chercher cours funk
search('cours funk', { level: 'débutant' })
```

---

## 🔍 CHAMPS UTILISÉS POUR LA RECHERCHE

### Champs Primaires (Poids fort)
1. **`title`** - Titre de la ressource (poids x10)
2. **`metadata.composer`** - Compositeur
3. **`metadata.ocr_text`** - Texte extrait par OCR

### Champs Secondaires (Poids moyen)
4. **`metadata.description`** - Description
5. **`metadata.content`** - Contenu HTML
6. **`metadata.techniques`** - Techniques (slap, walking, etc.)
7. **`metadata.styles`** - Styles musicaux (funk, jazz, etc.)

### Champs Tertiaires (Poids faible)
8. **`metadata.tags`** - Tags divers
9. **`metadata.key`** - Tonalité (Dm, Em, etc.)
10. **`search_text`** - Texte de recherche concaténé

---

## 🎯 FILTRES DISPONIBLES

### Par Type
```json
"type": "mp3" | "pdf" | "image" | "html" | "data"
```

### Par Style
```json
"styles": ["funk", "jazz", "slap", "walking bass", "disco", "rock", "blues", "reggae", "latin"]
```

### Par Niveau
```json
"level": "débutant" | "intermédiaire" | "avancé" | "tous niveaux"
```

### Par Technique
```json
"techniques": [
  "fingerstyle",
  "slap",
  "pop",
  "thumb",
  "ghost notes",
  "walking bass",
  "tapping",
  "harmonics",
  "double-thumb"
]
```

---

## 📈 STATISTIQUES CALCULÉES

### Total par Type
```json
{
  "mp3": 363,
  "pdf": 71,
  "image": 508,
  "html": 56,
  "data": 127
}
```

### Total par Style
```json
{
  "funk": 280,
  "jazz": 195,
  "slap": 140,
  "walking bass": 98,
  "disco": 87,
  "rock": 65,
  "blues": 42
}
```

### Total par Niveau
```json
{
  "débutant": 387,
  "intermédiaire": 452,
  "avancé": 286
}
```

---

## 🔗 FORMAT DES URLS

Toutes les URLs sont **encodées correctement** pour GitHub Pages :

```javascript
// Espaces → %20
"Track 01.mp3" → "Track%2001.mp3"

// & → %26
"70 Funk & Disco" → "70%20Funk%20%26%20Disco"

// URL finale
"https://11drumboy11.github.io/Prof-de-basse/Methodes/70%20Funk%20%26%20Disco%20bass%20MP3/Track%2001.mp3"
```

**Toutes les URLs sont cliquables et fonctionnelles ! ✅**

---

## 🚀 UTILISATION DANS LE CODE

### Charger l'index
```javascript
const response = await fetch('mega-search-index.json');
const data = await response.json();
console.log(`Total : ${data.total_resources} ressources`);
```

### Recherche simple
```javascript
const results = data.resources.filter(r => 
  r.search_text.includes('funk')
);
```

### Recherche avec filtres
```javascript
const results = data.resources.filter(r => 
  r.type === 'mp3' &&
  r.metadata.styles?.includes('funk') &&
  r.metadata.level === 'débutant'
);
```

### Recherche full-text
```javascript
const query = "gamme pentatonique mineure";
const terms = query.split(' ');

const results = data.resources.filter(r => 
  terms.every(term => r.search_text.includes(term))
);
```

---

## 💾 TAILLE DU FICHIER

**Estimations :**
- ~1000 ressources sans OCR : **~1-2 MB**
- ~1000 ressources avec OCR : **~5-10 MB**
- ~2000 ressources avec OCR : **~10-20 MB**

**C'est léger et rapide à charger ! ⚡**

---

## ✅ VALIDATION

### Vérifier le format
```bash
# Valider JSON
python3 -m json.tool mega-search-index.json > /dev/null && echo "✅ JSON valide"

# Compter ressources
cat mega-search-index.json | grep -c '"id"'

# Taille fichier
ls -lh mega-search-index.json
```

---

## 🎸 CONCLUSION

Le `mega-search-index.json` est le **cœur du système** :

✅ Format unifié et normalisé  
✅ Toutes les métadonnées essentielles  
✅ Texte full-text pour recherche  
✅ URLs encodées et fonctionnelles  
✅ Statistiques calculées  
✅ Optimisé pour la vitesse  

**Prêt à chercher n'importe quoi en < 100ms ! 🚀**

---

**Créé avec ❤️ pour Prof de Basse 3.0**  
*Documentation structure - Novembre 2025*
