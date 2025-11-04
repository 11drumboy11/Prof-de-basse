#!/bin/bash

# ============================================================================
# Script de test local - Prof de Basse
# ============================================================================
# Ce script teste le système de génération d'index localement AVANT de pusher
# ============================================================================

echo "=============================================="
echo "🎸 Prof de Basse - Test Local"
echo "=============================================="
echo ""

# 1. Vérifier Python
echo "📋 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé !"
    exit 1
fi
echo "✅ Python 3 trouvé : $(python3 --version)"
echo ""

# 2. Installer dépendances
echo "📦 Installation des dépendances..."
pip install beautifulsoup4 lxml --quiet
echo "✅ Dépendances installées"
echo ""

# 3. Vérifier structure
echo "📁 Vérification de la structure..."
if [ ! -f ".github/scripts/generate_all_indexes.py" ]; then
    echo "❌ Le script generate_all_indexes.py n'existe pas !"
    echo "   Il devrait être dans : .github/scripts/generate_all_indexes.py"
    exit 1
fi
echo "✅ Structure OK"
echo ""

# 4. Lancer le script
echo "🚀 Génération des index..."
python3 .github/scripts/generate_all_indexes.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ SUCCÈS ! Tous les index ont été générés."
    echo "=============================================="
    echo ""
    echo "📋 Fichiers générés :"
    echo "   - index.html (racine)"
    find . -name "index.html" -not -path "./.git/*" | head -20
    echo ""
    echo "🌐 Pour tester localement :"
    echo "   python3 -m http.server 8000"
    echo "   Puis ouvre : http://localhost:8000"
    echo ""
else
    echo ""
    echo "=============================================="
    echo "❌ ERREUR lors de la génération"
    echo "=============================================="
    echo ""
    echo "Regarde les messages d'erreur ci-dessus."
    exit 1
fi
