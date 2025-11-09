#!/bin/bash

# 🧹 SCRIPT DE NETTOYAGE - Prof de Basse
# Supprime tous les fichiers et dossiers inutiles/redondants

cd /Users/christophebonnet/Documents/GitHub/Prof-de-basse

echo "======================================"
echo "🧹 NETTOYAGE DU REPO - Prof de Basse"
echo "======================================"
echo ""

# Créer un dossier backup avant suppression
BACKUP_DIR="BACKUP-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Backup créé: $BACKUP_DIR"
echo ""

# ====================
# 1. DOSSIER search_system/ (ANCIEN SYSTÈME - INUTILE)
# ====================
echo "🗑️  1. Suppression search_system/ (ancien système)..."
if [ -d "search_system" ]; then
    mv search_system "$BACKUP_DIR/"
    echo "   ✅ search_system/ déplacé vers backup"
else
    echo "   ⏭️  Déjà supprimé"
fi

# ====================
# 2. DOSSIER scripts/ (REDONDANT avec .github/scripts/)
# ====================
echo ""
echo "🗑️  2. Suppression scripts/ (redondant)..."
if [ -d "scripts" ]; then
    mv scripts "$BACKUP_DIR/"
    echo "   ✅ scripts/ déplacé vers backup"
else
    echo "   ⏭️  Déjà supprimé"
fi

# ====================
# 3. FICHIERS .DS_Store (macOS)
# ====================
echo ""
echo "🗑️  3. Suppression .DS_Store (fichiers macOS)..."
find . -name ".DS_Store" -type f -delete 2>/dev/null
echo "   ✅ Tous les .DS_Store supprimés"

# ====================
# 4. CACHE PYTHON
# ====================
echo ""
echo "🗑️  4. Suppression cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -type f -delete 2>/dev/null
echo "   ✅ Cache Python supprimé"

# ====================
# 5. SCRIPTS REDONDANTS .github/scripts/
# ====================
echo ""
echo "🗑️  5. Nettoyage .github/scripts/..."

if [ -f ".github/scripts/generate_all_indexes.py" ]; then
    mv .github/scripts/generate_all_indexes.py "$BACKUP_DIR/"
    echo "   ✅ generate_all_indexes.py déplacé vers backup"
fi

if [ -f ".github/scripts/generate-mega-index.py.OLD" ]; then
    mv .github/scripts/generate-mega-index.py.OLD "$BACKUP_DIR/"
    echo "   ✅ generate-mega-index.py.OLD déplacé vers backup"
fi

# ====================
# 6. FICHIER scan-report.json (généré automatiquement)
# ====================
echo ""
echo "🗑️  6. Suppression scan-report.json (sera régénéré)..."
if [ -f "scan-report.json" ]; then
    mv scan-report.json "$BACKUP_DIR/"
    echo "   ✅ scan-report.json déplacé vers backup"
fi

# ====================
# 7. AJOUTER AU .gitignore
# ====================
echo ""
echo "📝 7. Mise à jour .gitignore..."

cat >> .gitignore << 'EOF'

# macOS
.DS_Store

# Python
__pycache__/
*.pyc
*.pyo

# Fichiers générés automatiquement (ne pas commiter)
scan-report.json

# Backups
BACKUP-*/
EOF

echo "   ✅ .gitignore mis à jour"

# ====================
# RÉSUMÉ
# ====================
echo ""
echo "======================================"
echo "✅ NETTOYAGE TERMINÉ"
echo "======================================"
echo ""
echo "📊 Résumé:"
echo "   🗑️  search_system/ → BACKUP (ancien système)"
echo "   🗑️  scripts/ → BACKUP (redondant)"
echo "   🗑️  .DS_Store → supprimés"
echo "   🗑️  __pycache__ → supprimés"
echo "   🗑️  Scripts redondants → BACKUP"
echo ""
echo "📦 Backup sauvegardé dans: $BACKUP_DIR"
echo ""
echo "⚠️  IMPORTANT: Vérifie le backup avant de commit !"
echo ""
echo "🚀 Prochaine étape:"
echo "   1. Vérifie que tout marche: ls -la"
echo "   2. GitHub Desktop: commit + push"
echo ""
