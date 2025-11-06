#!/bin/bash

# Script d'installation automatique - Prof de Basse Search System
# Ce script télécharge et installe tous les fichiers nécessaires

echo "=============================================="
echo "🎸 PROF DE BASSE - Installation Système"
echo "=============================================="
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -d "Methodes" ] && [ ! -d "Real_Books" ]; then
    echo "❌ ERREUR: Tu n'es pas dans le dossier Prof-de-basse"
    echo ""
    echo "📍 Lance ces commandes d'abord:"
    echo "   cd ~/Documents/GitHub/Prof-de-basse"
    echo "   bash install-search-system.sh"
    exit 1
fi

echo "✅ Bon dossier détecté"
echo ""

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p .github/workflows
echo "   ✓ .github/workflows créé"
echo ""

# Fonction pour télécharger ou créer les fichiers
echo "📥 Installation des fichiers..."
echo ""

# Liste des fichiers à vérifier
declare -a files=(
    "fusion-all-indexes.py:Script de fusion"
    "search-engine-pro.js:Moteur de recherche"
    "advanced-search.html:Page recherche avancée"
    ".github/workflows/mega-index-fusion.yml:Workflow GitHub Actions"
)

missing_count=0

for item in "${files[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    
    if [ -f "$file" ]; then
        echo "   ✓ $desc déjà présent"
    else
        echo "   ✗ $desc MANQUANT"
        ((missing_count++))
    fi
done

echo ""

if [ $missing_count -gt 0 ]; then
    echo "⚠️  $missing_count fichier(s) manquant(s)"
    echo ""
    echo "📋 INSTRUCTIONS:"
    echo ""
    echo "1. Télécharge ces fichiers depuis Claude:"
    echo "   - fusion-all-indexes-v2.py"
    echo "   - search-engine-pro.js"
    echo "   - index-with-universal-search.html"
    echo "   - advanced-search.html"
    echo "   - mega-index-fusion.yml"
    echo ""
    echo "2. Copie-les dans ce dossier:"
    echo "   cp ~/Downloads/fusion-all-indexes-v2.py fusion-all-indexes.py"
    echo "   cp ~/Downloads/search-engine-pro.js ."
    echo "   cp ~/Downloads/advanced-search.html ."
    echo "   mv index.html index-OLD-backup.html"
    echo "   cp ~/Downloads/index-with-universal-search.html index.html"
    echo "   cp ~/Downloads/mega-index-fusion.yml .github/workflows/"
    echo ""
    echo "3. Relance ce script:"
    echo "   bash install-search-system.sh"
    echo ""
else
    echo "✅ Tous les fichiers sont présents!"
    echo ""
    
    # Vérifier Python
    echo "🐍 Vérification Python..."
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version)
        echo "   ✓ Python installé: $python_version"
        echo ""
        
        # Lancer la fusion
        echo "🚀 Génération du mega-index..."
        python3 fusion-all-indexes.py
        
        if [ -f "mega-search-index.json" ]; then
            size=$(du -h mega-search-index.json | cut -f1)
            echo ""
            echo "✅ mega-search-index.json créé ($size)"
            echo ""
            
            # Instructions finales
            echo "=============================================="
            echo "🎉 INSTALLATION TERMINÉE !"
            echo "=============================================="
            echo ""
            echo "📋 PROCHAINES ÉTAPES:"
            echo ""
            echo "1. Commit + Push avec GitHub Desktop"
            echo "2. Attends 5 min (GitHub Actions)"
            echo "3. Va sur: https://11drumboy11.github.io/Prof-de-basse/"
            echo ""
            echo "✅ Le système de recherche sera opérationnel!"
            echo ""
        else
            echo ""
            echo "❌ Erreur: mega-search-index.json non créé"
            echo ""
            echo "🔍 Vérifie les messages d'erreur ci-dessus"
            echo ""
        fi
    else
        echo "   ✗ Python 3 non trouvé"
        echo ""
        echo "📦 Installe Python 3:"
        echo "   brew install python3"
        echo ""
    fi
fi
