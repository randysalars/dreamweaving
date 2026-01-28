"""
Project Setup and Health Checks
Tools for initializing projects and verifying environment health.
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    PASS = "✅"
    WARN = "⚠️"
    FAIL = "❌"


@dataclass
class HealthCheck:
    """Result of a health check."""
    name: str
    status: CheckStatus
    message: str
    fix_command: Optional[str] = None
    fix_message: Optional[str] = None


@dataclass
class DoctorReport:
    """Complete doctor/health check report."""
    checks: List[HealthCheck] = field(default_factory=list)
    
    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.PASS)
    
    @property
    def warnings(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.WARN)
    
    @property
    def failures(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.FAIL)
    
    @property
    def is_healthy(self) -> bool:
        return self.failures == 0
    
    def add(self, name: str, status: CheckStatus, message: str, 
            fix_command: str = None, fix_message: str = None):
        self.checks.append(HealthCheck(name, status, message, fix_command, fix_message))
    
    def format(self) -> str:
        lines = [
            "",
            "╔" + "═" * 68 + "╗",
            "║" + " " * 20 + "EPISTEMIC FACTORY DOCTOR" + " " * 24 + "║",
            "╠" + "═" * 68 + "╣",
        ]
        
        for check in self.checks:
            status = check.status.value
            lines.append(f"║ {status} {check.name:25} │ {check.message[:36]:36} ║")
            if check.fix_command and check.status != CheckStatus.PASS:
                lines.append(f"║   └── Fix: {check.fix_command[:53]:53} ║")
        
        lines.append("╠" + "═" * 68 + "╣")
        
        summary = f"Pass: {self.passed}  Warn: {self.warnings}  Fail: {self.failures}"
        overall = "HEALTHY ✓" if self.is_healthy else "ISSUES FOUND"
        lines.append(f"║ {summary:32} │ {overall:32} ║")
        lines.append("╚" + "═" * 68 + "╝")
        
        return "\n".join(lines)


def run_doctor() -> DoctorReport:
    """Run all health checks and return a report."""
    report = DoctorReport()
    
    # 1. Python version check
    py_version = sys.version_info
    if py_version >= (3, 10):
        report.add("Python Version", CheckStatus.PASS, f"Python {py_version.major}.{py_version.minor}")
    elif py_version >= (3, 8):
        report.add("Python Version", CheckStatus.WARN, f"Python {py_version.major}.{py_version.minor} (3.10+ recommended)")
    else:
        report.add("Python Version", CheckStatus.FAIL, f"Python {py_version.major}.{py_version.minor} (need 3.8+)")
    
    # 2. Virtual environment check
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        report.add("Virtual Environment", CheckStatus.PASS, "Activated")
    else:
        report.add("Virtual Environment", CheckStatus.WARN, "Not in venv",
                   fix_command="source venv/bin/activate")
    
    # 3. Required packages check
    required_packages = ["yaml", "reportlab", "PIL", "jinja2", "markdown"]
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg.replace("PIL", "PIL"))
        except ImportError:
            if pkg == "PIL":
                try:
                    __import__("PIL")
                except ImportError:
                    missing.append("pillow")
            else:
                missing.append(pkg)
    
    if not missing:
        report.add("Required Packages", CheckStatus.PASS, "All installed")
    else:
        report.add("Required Packages", CheckStatus.FAIL, f"Missing: {', '.join(missing)}",
                   fix_command=f"pip install {' '.join(missing)}")
    
    # 4. Products directory check
    products_dir = Path("./products")
    if products_dir.exists():
        product_count = len([d for d in products_dir.iterdir() if d.is_dir()])
        report.add("Products Directory", CheckStatus.PASS, f"{product_count} products found")
    else:
        report.add("Products Directory", CheckStatus.WARN, "Not found",
                   fix_command="mkdir -p products")
    
    # 5. Salarsu root check
    salarsu_root = os.environ.get("SALARSU_ROOT", "/home/rsalars/Projects/salarsu")
    salarsu_path = Path(salarsu_root)
    if salarsu_path.exists():
        report.add("Salarsu Root", CheckStatus.PASS, "Found")
    else:
        report.add("Salarsu Root", CheckStatus.WARN, "Not found (deployment disabled)",
                   fix_message="Set SALARSU_ROOT environment variable")
    
    # 6. Buffer token check
    buffer_token = os.environ.get("BUFFER_ACCESS_TOKEN")
    if buffer_token:
        report.add("Buffer Integration", CheckStatus.PASS, "Token configured")
    else:
        report.add("Buffer Integration", CheckStatus.WARN, "Not configured (scheduling disabled)",
                   fix_message="Set BUFFER_ACCESS_TOKEN env var")
    
    # 7. Git check
    git_available = shutil.which("git") is not None
    if git_available:
        report.add("Git", CheckStatus.PASS, "Available")
    else:
        report.add("Git", CheckStatus.FAIL, "Not found",
                   fix_command="sudo apt install git")
    
    # 8. PDF tools check (wkhtmltopdf or puppeteer)
    wkhtmltopdf = shutil.which("wkhtmltopdf")
    if wkhtmltopdf:
        report.add("PDF Generator", CheckStatus.PASS, "wkhtmltopdf found")
    else:
        # Check for puppeteer/chrome
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        if chrome:
            report.add("PDF Generator", CheckStatus.PASS, "Chrome/Chromium found")
        else:
            report.add("PDF Generator", CheckStatus.WARN, "No PDF tool found",
                       fix_command="sudo apt install wkhtmltopdf")
    
    # 9. Node.js check (for some features)
    node = shutil.which("node")
    if node:
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            version = result.stdout.strip()
            report.add("Node.js", CheckStatus.PASS, version)
        except Exception:
            report.add("Node.js", CheckStatus.WARN, "Error checking version")
    else:
        report.add("Node.js", CheckStatus.WARN, "Not found (video features disabled)",
                   fix_message="Install Node.js for video generation")
    
    # 10. TTS check (piper or espeak)
    piper = shutil.which("piper") or shutil.which("piper-tts")
    espeak = shutil.which("espeak") or shutil.which("espeak-ng")
    if piper:
        report.add("Text-to-Speech", CheckStatus.PASS, "Piper TTS found")
    elif espeak:
        report.add("Text-to-Speech", CheckStatus.PASS, "eSpeak found")
    else:
        report.add("Text-to-Speech", CheckStatus.WARN, "Not found (audio disabled)",
                   fix_message="Install piper-tts for audio narration")
    
    return report


def init_project(name: str, template: str = None, output_dir: Path = None) -> Tuple[bool, Path]:
    """
    Initialize a new product project with scaffolding.
    
    Returns (success, project_path)
    """
    from .templates import get_template, TEMPLATES
    
    # Normalize name
    slug = name.replace(" ", "_").lower()
    
    # Determine output directory
    if output_dir:
        project_path = output_dir
    else:
        project_path = Path("./products") / slug
    
    # Check if already exists
    if project_path.exists():
        return False, project_path
    
    # Create directory structure
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "output").mkdir()
    (project_path / "output" / "prompts").mkdir()
    (project_path / "output" / "responses").mkdir()
    (project_path / "output" / "visuals").mkdir()
    (project_path / "output" / "bonuses").mkdir()
    (project_path / "assets").mkdir()
    
    # Get template info
    template_obj = get_template(template) if template else None
    template_name = template_obj.name if template_obj else "Custom Product"
    
    # Create project config
    config = {
        "name": name,
        "slug": slug,
        "template": template or "custom",
        "created_at": __import__("datetime").datetime.now().isoformat(),
        "settings": {
            "chapters": template_obj.chapters if template_obj else 10,
            "audio": template_obj.audio if template_obj else False,
            "video": template_obj.video if template_obj else False,
            "bonuses": template_obj.bonuses if template_obj else [],
            "price": template_obj.default_price if template_obj else 47.00,
        }
    }
    
    import json
    (project_path / "project.json").write_text(json.dumps(config, indent=2))
    
    # Create README
    readme = f"""# {name}

> Generated by Epistemic Factory
> Template: {template_name}

## Project Structure

```
{slug}/
├── project.json         # Project configuration
├── assets/              # Source images, logos, etc.
└── output/
    ├── prompts/         # Generated prompts (read these)
    ├── responses/       # Your responses (write here)
    ├── visuals/         # Generated images
    └── bonuses/         # Bonus PDFs
```

## Quick Start

1. **Generate prompts:**
   ```bash
   product-builder create --topic "your topic" --title "{name}" --generate-prompts-only
   ```

2. **Write responses:** Read each `prompts/*.prompt.md` and write matching `responses/*.response.md`

3. **Compile product:**
   ```bash
   product-builder compile --product-dir . --title "{name}"
   ```

4. **Deploy:**
   ```bash
   product-builder deploy --product-dir . --name "{name}" --slug "{slug}"
   ```

## Settings

- **Chapters:** {config['settings']['chapters']}
- **Audio:** {'Yes' if config['settings']['audio'] else 'No'}
- **Video:** {'Yes' if config['settings']['video'] else 'No'}
- **Price:** ${config['settings']['price']:.2f}
"""
    
    (project_path / "README.md").write_text(readme)
    
    # Create .gitignore
    gitignore = """# Build artifacts
output/*.pdf
output/*.zip

# OS files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~

# Python
__pycache__/
*.pyc
"""
    (project_path / ".gitignore").write_text(gitignore)
    
    return True, project_path


def generate_env_template(output_path: Path) -> bool:
    """Generate a .env.template file with all required/optional variables."""
    env_template = """# Epistemic Factory Environment Variables
# Copy this to .env and fill in your values

# ═══════════════════════════════════════════════════════════════
# REQUIRED
# ═══════════════════════════════════════════════════════════════

# Path to the salarsu repository (for deployment)
SALARSU_ROOT="/home/rsalars/Projects/salarsu"

# ═══════════════════════════════════════════════════════════════
# OPTIONAL: Marketing Integrations
# ═══════════════════════════════════════════════════════════════

# Buffer - Social media scheduling
# Get token: https://buffer.com/developers/api
BUFFER_ACCESS_TOKEN=""

# SalarsNet Email API
SALARSNET_API_KEY=""
SALARSNET_API_URL="https://salars.net"

# ═══════════════════════════════════════════════════════════════
# OPTIONAL: AI/LLM APIs (for non-Antigravity mode)
# ═══════════════════════════════════════════════════════════════

# Google Vertex AI (for content generation)
GOOGLE_CLOUD_PROJECT=""
VERTEX_AI_LOCATION="us-central1"

# OpenAI (for image generation)
OPENAI_API_KEY=""

# ═══════════════════════════════════════════════════════════════
# OPTIONAL: TTS/Audio
# ═══════════════════════════════════════════════════════════════

# ElevenLabs (premium TTS)
ELEVENLABS_API_KEY=""

# Default TTS voice (piper model name)
TTS_VOICE="en_US-lessac-medium"
"""
    
    output_path.write_text(env_template)
    return True


# Project templates for quick scaffolding
PROJECT_TEMPLATES = {
    "minimal": {
        "description": "Basic product structure, no extras",
        "dirs": ["output/prompts", "output/responses"],
    },
    "standard": {
        "description": "Standard product with visuals and bonuses",
        "dirs": ["output/prompts", "output/responses", "output/visuals", "output/bonuses", "assets"],
    },
    "full": {
        "description": "Full product with audio, video, marketing",
        "dirs": ["output/prompts", "output/responses", "output/visuals", "output/bonuses", 
                 "output/audio", "output/video", "output/marketing", "assets"],
    },
}
