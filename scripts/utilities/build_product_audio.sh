#!/bin/bash
# Build all audio sessions for digital products
# Usage: ./build_product_audio.sh [product_name]

set -e

cd /home/rsalars/Projects/dreamweaving
source venv/bin/activate

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

build_session() {
    local session_path="$1"
    local session_name=$(basename "$session_path")

    log_info "Building: $session_name"

    # Check if script exists
    if [[ ! -f "$session_path/working_files/script.ssml" ]]; then
        log_error "No script.ssml found in $session_path/working_files/"
        return 1
    fi

    # Generate voice
    log_info "  Generating voice..."
    python3 scripts/core/generate_voice.py \
        "$session_path/working_files/script.ssml" \
        "$session_path/output" \
        --provider coqui \
        --quality hypnotic

    # Check for binaural settings in manifest
    if grep -q "binaural:" "$session_path/manifest.yaml" 2>/dev/null; then
        log_info "  Generating binaural beats..."
        python3 scripts/core/generate_binaural.py "$session_path" 2>/dev/null || log_warn "  Binaural generation skipped"
    fi

    # Run hypnotic post-processing
    log_info "  Applying hypnotic post-processing..."
    python3 scripts/core/hypnotic_post_process.py --session "$session_path" 2>/dev/null || log_warn "  Post-processing skipped"

    log_info "  Complete: $session_name"
}

build_product() {
    local product_dir="$1"
    local product_name=$(basename "$product_dir")

    log_info "=========================================="
    log_info "Building product: $product_name"
    log_info "=========================================="

    # Find all session directories (those with manifest.yaml)
    for session_dir in "$product_dir"/*/; do
        if [[ -f "${session_dir}manifest.yaml" ]]; then
            build_session "${session_dir%/}"
        fi
    done

    # Check if this is a single-session product
    if [[ -f "$product_dir/manifest.yaml" ]] && [[ -d "$product_dir/working_files" ]]; then
        build_session "$product_dir"
    fi

    log_info "Product complete: $product_name"
}

# Main
if [[ -n "$1" ]]; then
    # Build specific product
    if [[ -d "sessions/$1" ]]; then
        build_product "sessions/$1"
    else
        log_error "Product not found: sessions/$1"
        exit 1
    fi
else
    # Build all digital product audio
    log_info "Building all digital product audio..."

    products=(
        "consciousness-expansion-pack"
        "mind-expansion-techniques"
        "contemplative-practice"
        "holistic-wellness"
        "daily-joy-activation"
        "frontier-wisdom-narrated"
    )

    for product in "${products[@]}"; do
        if [[ -d "sessions/$product" ]]; then
            build_product "sessions/$product"
        else
            log_warn "Product not found: sessions/$product"
        fi
    done

    log_info "=========================================="
    log_info "All products complete!"
    log_info "=========================================="
fi
