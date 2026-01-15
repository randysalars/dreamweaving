#!/bin/bash

# Garden of Eden Path-Working - Complete Setup & Audio Generator
# This script automates everything from setup to audio generation

set -e  # Exit on any error

# Color codes for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Header
echo -e "${PURPLE}"
echo "════════════════════════════════════════════════════════════════════════"
echo "   🌿 Garden of Eden Path-Working: Complete Setup & Generator 🌿"
echo "════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if Google Cloud SDK is installed
print_status "Checking for Google Cloud SDK..."
if command_exists gcloud; then
    print_success "Google Cloud SDK is installed"
else
    print_warning "Google Cloud SDK not found"
    echo ""
    echo "To use this script, you need Google Cloud SDK installed."
    echo ""
    echo "Install with:"
    echo "  curl https://sdk.cloud.google.com | bash"
    echo "  exec -l \$SHELL"
    echo "  gcloud init"
    echo ""
    read -p "Would you like to see the full setup instructions? (y/n): " show_setup
    if [[ $show_setup == "y" || $show_setup == "Y" ]]; then
        echo ""
        echo "Setup Instructions:"
        echo "1. Install Google Cloud SDK:"
        echo "   curl https://sdk.cloud.google.com | bash"
        echo ""
        echo "2. Restart your shell:"
        echo "   exec -l \$SHELL"
        echo ""
        echo "3. Initialize gcloud:"
        echo "   gcloud init"
        echo ""
        echo "4. Authenticate:"
        echo "   gcloud auth application-default login"
        echo ""
        echo "5. Enable TTS API:"
        echo "   gcloud services enable texttospeech.googleapis.com"
        echo ""
        echo "6. Install Python library:"
        echo "   pip install google-cloud-texttospeech"
        echo ""
    fi
    exit 1
fi

# Check if authenticated
print_status "Checking authentication..."
if gcloud auth application-default print-access-token >/dev/null 2>&1; then
    print_success "Authentication is set up"
else
    print_warning "Not authenticated with Google Cloud"
    echo ""
    echo "Run: gcloud auth application-default login"
    exit 1
fi

# Check if Python library is installed
print_status "Checking for google-cloud-texttospeech..."
if python3 -c "import google.cloud.texttospeech" 2>/dev/null; then
    print_success "Python library is installed"
else
    print_warning "google-cloud-texttospeech not found"
    echo ""
    read -p "Install it now? (y/n): " install_lib
    if [[ $install_lib == "y" || $install_lib == "Y" ]]; then
        print_status "Installing google-cloud-texttospeech..."
        pip install google-cloud-texttospeech
        print_success "Library installed"
    else
        echo "Cannot continue without the library. Exiting."
        exit 1
    fi
fi

# Check if SSML file exists
if [ ! -f "garden_of_eden_hypnosis.ssml" ]; then
    print_error "garden_of_eden_hypnosis.ssml not found in current directory"
    echo "Make sure you're running this script from the same directory as the SSML file."
    exit 1
fi

# Voice selection
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo "Voice Selection"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Choose a voice for your hypnotic audio:"
echo ""
echo "Female Voices (Recommended for soothing hypnosis):"
echo "  1) en-US-Neural2-A  [DEFAULT - Warm, naturally calming, BEST]"
echo "  2) en-US-Neural2-C  [Soft, nurturing, maternal]"
echo "  3) en-US-Neural2-E  [Deeper, very relaxing]"
echo "  4) en-US-Neural2-F  [Clear, serene, meditative]"
echo ""
echo "Male Voices (Deep and grounding):"
echo "  5) en-US-Neural2-D  [Deep, resonant, authoritative yet gentle]"
echo "  6) en-US-Neural2-I  [Warm, compassionate, therapeutic]"
echo "  7) en-US-Neural2-J  [Rich, mature, very calming]"
echo ""
read -p "Enter choice (1-7) or press Enter for default [1]: " voice_choice

case $voice_choice in
    2) VOICE="en-US-Neural2-C" ;;
    3) VOICE="en-US-Neural2-E" ;;
    4) VOICE="en-US-Neural2-F" ;;
    5) VOICE="en-US-Neural2-D" ;;
    6) VOICE="en-US-Neural2-I" ;;
    7) VOICE="en-US-Neural2-J" ;;
    *) VOICE="en-US-Neural2-A" ;;
esac

# Output filename
echo ""
read -p "Enter output filename [garden_of_eden.mp3]: " output_file
output_file=${output_file:-garden_of_eden.mp3}

# Confirm settings
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo "Generation Settings"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo "Input:         garden_of_eden_hypnosis.ssml"
echo "Output:        $output_file"
echo "Voice:         $VOICE"
echo "Speaking Rate: 0.85 (hypnotic pace)"
echo "Pitch:         -2.0 semitones (calming)"
echo "Duration:      ~25-30 minutes"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo ""
read -p "Proceed with generation? (y/n): " proceed

if [[ $proceed != "y" && $proceed != "Y" ]]; then
    echo "Generation cancelled."
    exit 0
fi

# Generate audio
echo ""
print_status "Starting audio generation..."
echo ""

if python3 generate_audio.py garden_of_eden_hypnosis.ssml "$output_file" "$VOICE"; then
    echo ""
    echo -e "${GREEN}"
    echo "════════════════════════════════════════════════════════════════════════"
    echo "                    ✨ Generation Complete! ✨"
    echo "════════════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
    echo ""
    echo "Your hypnotic audio is ready: $output_file"
    echo ""
    echo "🎧 Listening Tips:"
    echo "   • Use headphones for best experience"
    echo "   • Find a quiet, comfortable space"
    echo "   • Do not listen while driving"
    echo "   • Allow 25-30 minutes uninterrupted"
    echo ""
    echo "🌟 After listening, you'll have 5 powerful anchors:"
    echo "   1. Three Sacred Breaths (return to innocence)"
    echo "   2. Pause for Discernment (access wisdom)"
    echo "   3. Rainbow Seed Meditation (daily wholeness)"
    echo "   4. Garden Doorway (instant peace)"
    echo "   5. Divine Embrace (self-comfort)"
    echo ""
    echo "Walk in innocence. Choose with wisdom. Live in wholeness."
    echo ""
    echo "🌿 Blessed be. 🌿"
    echo ""
else
    print_error "Generation failed. Check error messages above."
    exit 1
fi
