#!/bin/bash

# 🚀 INSTALLATION AUTOMATIQUE DU SYSTÈME D'INDEXATION
# Prof de Basse - Auto-Index System

echo "=========================================="
echo "🎸 PROF DE BASSE - AUTO-INDEX INSTALLER"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Vérifier qu'on est dans le bon repo
echo "📁 Vérification du répertoire..."
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Erreur: Ce script doit être exécuté à la racine d'un repo Git${NC}"
    exit 1
fi

if [ ! -d "Methodes" ] && [ ! -d "Theorie" ]; then
    echo -e "${YELLOW}⚠️  Avertissement: Dossiers Methodes/ ou Theorie/ non trouvés${NC}"
    echo "   Êtes-vous sûr d'être dans le bon repo?"
    read -p "   Continuer quand même? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ Répertoire valide${NC}"

# 2. Créer la structure GitHub Actions
echo ""
echo "📂 Création de la structure GitHub Actions..."
mkdir -p .github/workflows
mkdir -p .github/scripts

echo -e "${GREEN}✅ Structure créée${NC}"

# 3. Télécharger les fichiers depuis les outputs
echo ""
echo "📥 Installation des fichiers..."

# Workflow
if [ -f "/mnt/user-data/outputs/.github-workflows-auto-index.yml" ]; then
    cp /mnt/user-data/outputs/.github-workflows-auto-index.yml .github/workflows/auto-index.yml
    echo -e "${GREEN}✅ Workflow installé${NC}"
else
    echo -e "${RED}❌ Fichier workflow non trouvé${NC}"
fi

# Mega Scanner
if [ -f "/mnt/user-data/outputs/mega-scanner.py" ]; then
    cp /mnt/user-data/outputs/mega-scanner.py .github/scripts/mega-scanner.py
    chmod +x .github/scripts/mega-scanner.py
    echo -e "${GREEN}✅ Mega Scanner installé${NC}"
else
    echo -e "${RED}❌ Fichier mega-scanner.py non trouvé${NC}"
fi

# Index Generator
if [ -f "/mnt/user-data/outputs/generate-mega-index.py" ]; then
    cp /mnt/user-data/outputs/generate-mega-index.py .github/scripts/generate-mega-index.py
    chmod +x .github/scripts/generate-mega-index.py
    echo -e "${GREEN}✅ Index Generator installé${NC}"
else
    echo -e "${RED}❌ Fichier generate-mega-index.py non trouvé${NC}"
fi

# README
if [ -f "/mnt/user-data/outputs/INSTALLATION-AUTO-INDEX.md" ]; then
    cp /mnt/user-data/outputs/INSTALLATION-AUTO-INDEX.md .
    echo -e "${GREEN}✅ Documentation installée${NC}"
fi

# 4. Vérifier les dépendances Python
echo ""
echo "🐍 Vérification des dépendances Python..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 non installé${NC}"
    echo "   Installez Python 3 : https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 trouvé: $(python3 --version)${NC}"

# 5. Test local (optionnel)
echo ""
echo "🧪 Test du scanner en local..."
read -p "Voulez-vous tester le scanner maintenant? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔍 Lancement du scan..."
    
    # Installer les dépendances si besoin
    pip3 install --quiet Pillow pytesseract 2>/dev/null || true
    
    # Lancer le scan
    python3 .github/scripts/mega-scanner.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Scan réussi !${NC}"
        
        # Générer l'index
        echo "📊 Génération de l'index..."
        python3 .github/scripts/generate-mega-index.py
        
        if [ -f "mega-search-index.json" ]; then
            echo -e "${GREEN}✅ mega-search-index.json généré !${NC}"
            
            # Afficher les stats
            if command -v jq &> /dev/null; then
                echo ""
                echo "📊 Statistiques:"
                jq '.metadata' mega-search-index.json
            fi
        fi
    else
        echo -e "${RED}❌ Erreur lors du scan${NC}"
    fi
fi

# 6. Configuration Git
echo ""
echo "🔧 Configuration Git..."

# Vérifier si l'user est configuré
if [ -z "$(git config user.name)" ]; then
    echo -e "${YELLOW}⚠️  Git user.name non configuré${NC}"
    read -p "   Entrez votre nom: " git_name
    git config user.name "$git_name"
fi

if [ -z "$(git config user.email)" ]; then
    echo -e "${YELLOW}⚠️  Git user.email non configuré${NC}"
    read -p "   Entrez votre email: " git_email
    git config user.email "$git_email"
fi

echo -e "${GREEN}✅ Git configuré${NC}"

# 7. Commit des changements
echo ""
echo "💾 Commit des fichiers d'indexation..."
git add .github/ INSTALLATION-AUTO-INDEX.md
git status --short

read -p "Voulez-vous commiter maintenant? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "🤖 Add auto-indexing system

- GitHub Actions workflow for automatic scanning
- Python scripts for mega-scanner and index generation
- Supports all method folders (Methodes, Theorie, Pratique, etc.)
- Generates unified mega-search-index.json"
    
    echo -e "${GREEN}✅ Commit créé${NC}"
    
    # 8. Push
    echo ""
    read -p "Voulez-vous push vers GitHub maintenant? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Push réussi !${NC}"
            echo ""
            echo "=========================================="
            echo "🎉 INSTALLATION TERMINÉE !"
            echo "=========================================="
            echo ""
            echo "Prochaines étapes:"
            echo "1. Va sur GitHub → onglet 'Actions'"
            echo "2. Le workflow 'Auto-Index & OCR Scan' devrait se lancer"
            echo "3. Attends 2-5 minutes"
            echo "4. Le fichier mega-search-index.json sera créé automatiquement"
            echo ""
            echo "Pour ajouter une nouvelle méthode:"
            echo "1. Crée un dossier dans Methodes/ (ou Theorie/, etc.)"
            echo "2. Ajoute songs_index.json + assets/pages/"
            echo "3. Commit & Push"
            echo "4. L'indexation se fait automatiquement !"
            echo ""
        else
            echo -e "${RED}❌ Erreur lors du push${NC}"
            echo "   Vérifiez vos permissions GitHub"
        fi
    fi
fi

# 9. Infos finales
echo ""
echo "=========================================="
echo "📚 DOCUMENTATION"
echo "=========================================="
echo "Consultez INSTALLATION-AUTO-INDEX.md pour:"
echo "  - Format des fichiers songs_index.json"
echo "  - Structure des dossiers méthodes"
echo "  - Utilisation de mega-search-index.json"
echo "  - Résolution des problèmes"
echo ""
echo "Questions? Contacte Christophe ! 🎸"
echo ""
