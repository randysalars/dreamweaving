#!/bin/bash
# Smart Environment Setup with Enhanced Auto-Fix
# Handles more complex setup scenarios automatically

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${BOLD}=== Smart Environment Setup ===${NC}\n"

FIXES_APPLIED=0
FIXES_FAILED=0

# Function to apply a fix
apply_fix() {
    local description="$1"
    local command="$2"
    
    echo -e "${BLUE}Fixing:${NC} $description"
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $description fixed\n"
        ((FIXES_APPLIED++))
        return 0
    else
        echo -e "${RED}✗${NC} Failed to fix: $description\n"
        ((FIXES_FAILED++))
        return 1
    fi
}

# Check if we're in virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}Not in virtual environment${NC}"
    
    # Check if venv exists
    if [ -d "venv" ]; then
        echo -e "${BLUE}Found existing venv${NC}"
        echo -e "${YELLOW}Please run: source venv/bin/activate${NC}\n"
    else
        # Create venv automatically
        echo -e "${BLUE}Creating virtual environment...${NC}"
        if python3 -m venv venv; then
            echo -e "${GREEN}✓${NC} Virtual environment created"
            echo -e "${GREEN}Activating...${NC}"
            source venv/bin/activate
            ((FIXES_APPLIED++))
        else
            echo -e "${RED}✗${NC} Failed to create venv"
            ((FIXES_FAILED++))
        fi
    fi
else
    echo -e "${GREEN}✓${NC} Running in virtual environment\n"
fi

# Install/upgrade pip
echo -e "${BLUE}Ensuring pip is up to date...${NC}"
python3 -m pip install --upgrade pip > /dev/null 2>&1 && echo -e "${GREEN}✓${NC} pip updated\n"

# Check and install required packages
echo -e "${BOLD}Checking Python packages...${NC}\n"

PACKAGES=(
    "google-cloud-texttospeech"
    "pydub"
    "mutagen"
    "tqdm"
)

MISSING_PACKAGES=()

for package in "${PACKAGES[@]}"; do
    if python3 -c "import ${package//-/_}" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package"
    else
        echo -e "${RED}✗${NC} $package (missing)"
        MISSING_PACKAGES+=("$package")
    fi
done
echo ""

# Install missing packages
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${BLUE}Installing ${#MISSING_PACKAGES[@]} missing packages...${NC}"
    if python3 -m pip install "${MISSING_PACKAGES[@]}" --quiet; then
        echo -e "${GREEN}✓${NC} All packages installed\n"
        ((FIXES_APPLIED++))
    else
        echo -e "${RED}✗${NC} Package installation failed\n"
        ((FIXES_FAILED++))
    fi
fi

# Check FFmpeg
echo -e "${BOLD}Checking FFmpeg...${NC}"
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC} FFmpeg installed\n"
else
    echo -e "${YELLOW}⚠${NC} FFmpeg not found"
    echo -e "${BLUE}Installation commands:${NC}"
    echo -e "  Ubuntu/Debian: ${BOLD}sudo apt install ffmpeg${NC}"
    echo -e "  macOS:         ${BOLD}brew install ffmpeg${NC}\n"
fi

# Check gcloud
echo -e "${BOLD}Checking Google Cloud SDK...${NC}"
if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}✓${NC} Google Cloud SDK installed"
    
    # Check authentication
    if gcloud auth application-default print-access-token &> /dev/null; then
        echo -e "${GREEN}✓${NC} Google Cloud authenticated\n"
    else
        echo -e "${YELLOW}⚠${NC} Not authenticated with Google Cloud"
        echo -e "${BLUE}Run:${NC} ${BOLD}gcloud auth application-default login${NC}\n"
        
        # Offer to authenticate
        read -p "Authenticate now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if gcloud auth application-default login; then
                echo -e "${GREEN}✓${NC} Authentication successful\n"
                ((FIXES_APPLIED++))
            else
                echo -e "${RED}✗${NC} Authentication failed\n"
                ((FIXES_FAILED++))
            fi
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Google Cloud SDK not found"
    echo -e "${BLUE}Install:${NC} ${BOLD}curl https://sdk.cloud.google.com | bash${NC}\n"
fi

# Create missing directories
echo -e "${BOLD}Checking directory structure...${NC}"
REQUIRED_DIRS=("sessions" "scripts/core" "scripts/utilities" "docs" "config" "templates")
CREATED_DIRS=()

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        CREATED_DIRS+=("$dir")
    fi
done

if [ ${#CREATED_DIRS[@]} -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Created ${#CREATED_DIRS[@]} directories: ${CREATED_DIRS[*]}\n"
    ((FIXES_APPLIED++))
else
    echo -e "${GREEN}✓${NC} All directories present\n"
fi

# Fix permissions
echo -e "${BOLD}Checking permissions...${NC}"
FIXED_PERMS=0

for dir in sessions scripts; do
    if [ -d "$dir" ] && [ ! -w "$dir" ]; then
        chmod -R u+w "$dir" 2>/dev/null && ((FIXED_PERMS++))
    fi
done

if [ $FIXED_PERMS -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Fixed permissions on $FIXED_PERMS directories\n"
    ((FIXES_APPLIED++))
else
    echo -e "${GREEN}✓${NC} Permissions OK\n"
fi

# Create requirements.txt if missing
if [ ! -f "requirements.txt" ]; then
    echo -e "${BLUE}Creating requirements.txt...${NC}"
    cat > requirements.txt << 'REQUIREMENTS'
google-cloud-texttospeech>=2.14.0
pydub>=0.25.0
mutagen>=1.45.0
tqdm>=4.65.0
REQUIREMENTS
    echo -e "${GREEN}✓${NC} requirements.txt created\n"
    ((FIXES_APPLIED++))
fi

# Create .gitignore if missing
if [ ! -f ".gitignore" ]; then
    echo -e "${BLUE}Creating .gitignore...${NC}"
    cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Audio files
*.wav
*.mp3
*.aac
!templates/*.mp3

# Video files
*.mp4
*.avi
*.mov
!templates/*.mp4

# Backups
*.bak
*.backup

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Session outputs
sessions/*/output/
sessions/*/working_files/
sessions/*/final_export/

# Temporary
temp_audio/
test_output/
GITIGNORE
    echo -e "${GREEN}✓${NC} .gitignore created\n"
    ((FIXES_APPLIED++))
fi

# Summary
echo -e "${BOLD}=== Setup Summary ===${NC}\n"
echo -e "${GREEN}Fixes applied:${NC} $FIXES_APPLIED"
echo -e "${RED}Fixes failed:${NC}  $FIXES_FAILED"
echo ""

if [ $FIXES_APPLIED -gt 0 ]; then
    echo -e "${GREEN}${BOLD}✓ Environment improved!${NC}"
    echo -e "${BLUE}Run check_env.py to verify:${NC}"
    echo -e "  python3 scripts/core/check_env.py\n"
fi

# Final recommendation
if [ $FIXES_FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ Ready to use Dreamweaving!${NC}\n"
    exit 0
else
    echo -e "${YELLOW}⚠ Some fixes require manual intervention${NC}"
    echo -e "${BLUE}See messages above for details${NC}\n"
    exit 1
fi
