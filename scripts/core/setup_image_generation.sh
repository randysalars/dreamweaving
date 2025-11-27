#!/bin/bash
# Setup script for Stable Diffusion image generation

set -e

echo "=================================================="
echo "STABLE DIFFUSION IMAGE GENERATION SETUP"
echo "=================================================="
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
echo ""

# Check for GPU
echo "🎮 Checking for GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠️  No NVIDIA GPU detected - will use CPU (slower)"
fi
echo ""

# Install PyTorch
echo "📦 Installing PyTorch..."
if command -v nvidia-smi &> /dev/null; then
    echo "Installing CUDA version..."
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
else
    echo "Installing CPU version..."
    pip install torch torchvision
fi
echo ""

# Install Diffusers and dependencies
echo "📦 Installing Diffusers library and dependencies..."
pip install diffusers transformers accelerate safetensors pillow huggingface-hub
echo ""

# Optional: Install xformers for better performance
echo "💡 Installing xformers for better performance (optional)..."
if command -v nvidia-smi &> /dev/null; then
    pip install xformers || echo "⚠️  xformers installation failed (optional, will work without it)"
fi
echo ""

# Login to Hugging Face (optional, some models require it)
echo "🤗 Hugging Face Hub Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Some models require a Hugging Face account and token."
echo "SDXL base model is public and doesn't require login."
echo ""
echo "To login (optional):"
echo "  pip install -U huggingface_hub"
echo "  huggingface-cli login"
echo ""
echo "Get your token at: https://huggingface.co/settings/tokens"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import torch
import diffusers
import transformers
print('✅ All required packages installed successfully')
print(f'PyTorch version: {torch.__version__}')
print(f'Diffusers version: {diffusers.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
"
echo ""

echo "=================================================="
echo "✅ SETUP COMPLETE"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run: python3 scripts/core/generate_images_sd.py"
echo "  2. First run will download SDXL model (~13 GB)"
echo "  3. Model will be cached at ~/.cache/huggingface/hub/"
echo ""
echo "Usage examples:"
echo "  # Generate with default settings (normal quality)"
echo "  python3 scripts/core/generate_images_sd.py"
echo ""
echo "  # High quality (slower, better results)"
echo "  python3 scripts/core/generate_images_sd.py --quality high"
echo ""
echo "  # Draft mode (faster, test prompts)"
echo "  python3 scripts/core/generate_images_sd.py --quality draft --candidates 1"
echo ""
echo "System Requirements:"
echo "  • GPU: 10+ GB VRAM recommended (works with 8GB using optimizations)"
echo "  • RAM: 16 GB minimum"
echo "  • Storage: 15 GB free (for model cache)"
echo "  • Time: ~30-60 seconds per image (GPU) or 5-10 min (CPU)"
echo ""
