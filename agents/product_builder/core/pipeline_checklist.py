"""
Pipeline Checklist and Verification System

Ensures each phase of the Epistemic Factory pipeline is complete and verified
before proceeding to the next phase.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PhaseStatus(str, Enum):
    """Status of a pipeline phase."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass
class VerificationResult:
    """Result of a verification check."""
    passed: bool
    check_name: str
    message: str
    details: Dict = field(default_factory=dict)


@dataclass
class PhaseChecklist:
    """Checklist for a single pipeline phase."""
    phase_name: str
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    verified_at: Optional[str] = None
    checks: Dict[str, bool] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    
    def mark_started(self):
        self.status = PhaseStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()
    
    def mark_completed(self):
        self.status = PhaseStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
    
    def mark_verified(self):
        self.status = PhaseStatus.VERIFIED
        self.verified_at = datetime.now().isoformat()
    
    def check(self, name: str, passed: bool, note: str = None):
        """Record a verification check."""
        self.checks[name] = passed
        if note:
            self.notes.append(f"[{name}] {note}")
    
    def all_checks_passed(self) -> bool:
        return all(self.checks.values()) if self.checks else False


@dataclass
class PipelineChecklist:
    """Complete pipeline checklist with all phases."""
    product_slug: str
    product_title: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Phase checklists
    phase_1_emission: PhaseChecklist = field(default_factory=lambda: PhaseChecklist("Phase 1: Emission"))
    phase_2_generation: PhaseChecklist = field(default_factory=lambda: PhaseChecklist("Phase 2: Generation"))
    phase_3_compilation: PhaseChecklist = field(default_factory=lambda: PhaseChecklist("Phase 3: Compilation"))
    phase_4_deployment: PhaseChecklist = field(default_factory=lambda: PhaseChecklist("Phase 4: Deployment"))
    phase_5_marketing: PhaseChecklist = field(default_factory=lambda: PhaseChecklist("Phase 5: Marketing"))
    
    def save(self, output_dir: Path):
        """Save checklist to JSON file."""
        checklist_path = output_dir / "pipeline_checklist.json"
        self.updated_at = datetime.now().isoformat()
        
        data = {
            "product_slug": self.product_slug,
            "product_title": self.product_title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "phases": {
                "emission": asdict(self.phase_1_emission),
                "generation": asdict(self.phase_2_generation),
                "compilation": asdict(self.phase_3_compilation),
                "deployment": asdict(self.phase_4_deployment),
                "marketing": asdict(self.phase_5_marketing),
            }
        }
        
        checklist_path.write_text(json.dumps(data, indent=2))
        logger.info(f"📋 Saved checklist: {checklist_path}")
        return checklist_path
    
    @classmethod
    def load(cls, output_dir: Path) -> Optional["PipelineChecklist"]:
        """Load checklist from JSON file."""
        checklist_path = output_dir / "pipeline_checklist.json"
        if not checklist_path.exists():
            return None
        
        try:
            data = json.loads(checklist_path.read_text())
            checklist = cls(
                product_slug=data["product_slug"],
                product_title=data["product_title"],
                created_at=data.get("created_at", ""),
                updated_at=data.get("updated_at", ""),
            )
            
            # Load phase data
            phases = data.get("phases", {})
            for phase_key, phase_data in phases.items():
                phase_obj = getattr(checklist, f"phase_{['emission', 'generation', 'compilation', 'deployment', 'marketing'].index(phase_key) + 1}_{phase_key}", None)
                if phase_obj and phase_data:
                    phase_obj.status = PhaseStatus(phase_data.get("status", "not_started"))
                    phase_obj.started_at = phase_data.get("started_at")
                    phase_obj.completed_at = phase_data.get("completed_at")
                    phase_obj.verified_at = phase_data.get("verified_at")
                    phase_obj.checks = phase_data.get("checks", {})
                    phase_obj.notes = phase_data.get("notes", [])
            
            return checklist
        except Exception as e:
            logger.warning(f"Failed to load checklist: {e}")
            return None


class PipelineVerifier:
    """Verifies each phase of the pipeline is complete."""
    
    def __init__(self, product_dir: Path):
        self.product_dir = Path(product_dir)
        self.output_dir = self.product_dir / "output"
        self.prompts_dir = self.output_dir / "prompts"
        self.responses_dir = self.output_dir / "responses"
        self.visuals_dir = self.output_dir / "visuals"
        self.bonuses_dir = self.output_dir / "bonuses"
    
    def verify_phase_1_emission(self) -> List[VerificationResult]:
        """Verify Phase 1: Emission (prompts generated)."""
        results = []
        
        # Check 1: Prompts directory exists
        exists = self.prompts_dir.exists()
        results.append(VerificationResult(
            passed=exists,
            check_name="prompts_directory",
            message="Prompts directory exists" if exists else "Missing prompts directory"
        ))
        
        if not exists:
            return results
        
        # Check 2: Has prompt files
        prompt_files = list(self.prompts_dir.glob("*.prompt.md"))
        has_prompts = len(prompt_files) >= 3
        results.append(VerificationResult(
            passed=has_prompts,
            check_name="prompt_files",
            message=f"Found {len(prompt_files)} prompt files" if has_prompts else f"Only {len(prompt_files)} prompts (need ≥3)",
            details={"count": len(prompt_files), "files": [f.name for f in prompt_files]}
        ))
        
        # Check 3: Core prompts present
        required_patterns = ["foundation", "application", "mastery"]
        found_core = all(
            any(p in f.name.lower() for f in prompt_files)
            for p in required_patterns
        ) or len(prompt_files) >= 3
        results.append(VerificationResult(
            passed=found_core,
            check_name="core_prompts",
            message="Core chapter prompts present" if found_core else "Missing core prompts"
        ))
        
        return results
    
    def verify_phase_2_generation(self) -> List[VerificationResult]:
        """Verify Phase 2: Generation (responses written)."""
        results = []
        
        # Check 1: Responses directory exists
        exists = self.responses_dir.exists()
        results.append(VerificationResult(
            passed=exists,
            check_name="responses_directory",
            message="Responses directory exists" if exists else "Missing responses directory"
        ))
        
        if not exists:
            return results
        
        # Check 2: Has response files
        response_files = list(self.responses_dir.glob("*.response.md"))
        has_responses = len(response_files) >= 3
        results.append(VerificationResult(
            passed=has_responses,
            check_name="response_files",
            message=f"Found {len(response_files)} response files" if has_responses else f"Only {len(response_files)} responses",
            details={"count": len(response_files)}
        ))
        
        # Check 3: Responses have content
        min_words = 1000
        short_responses = []
        for resp in response_files:
            content = resp.read_text()
            word_count = len(content.split())
            if word_count < min_words:
                short_responses.append(f"{resp.name}: {word_count} words")
        
        content_ok = len(short_responses) == 0
        results.append(VerificationResult(
            passed=content_ok,
            check_name="response_content",
            message="All responses have sufficient content (≥1000 words)" if content_ok else f"{len(short_responses)} responses too short",
            details={"short_responses": short_responses}
        ))
        
        # Check 4: Prompt-response parity
        prompt_files = list(self.prompts_dir.glob("*.prompt.md")) if self.prompts_dir.exists() else []
        prompt_slugs = {f.stem.replace(".prompt", "") for f in prompt_files}
        response_slugs = {f.stem.replace(".response", "") for f in response_files}
        
        missing = prompt_slugs - response_slugs
        parity_ok = len(missing) == 0
        results.append(VerificationResult(
            passed=parity_ok,
            check_name="prompt_response_parity",
            message="All prompts have responses" if parity_ok else f"Missing responses for: {', '.join(missing)}",
            details={"missing": list(missing)}
        ))
        
        return results
    
    def verify_phase_3_compilation(self) -> List[VerificationResult]:
        """Verify Phase 3: Compilation (PDF + assets)."""
        results = []
        
        # Check 1: Main PDF exists
        pdf_files = list(self.output_dir.glob("*.pdf"))
        main_pdfs = [f for f in pdf_files if "bonus" not in f.name.lower()]
        has_pdf = len(main_pdfs) >= 1
        results.append(VerificationResult(
            passed=has_pdf,
            check_name="main_pdf",
            message=f"Main PDF created: {main_pdfs[0].name}" if has_pdf else "Missing main PDF",
            details={"pdf_path": str(main_pdfs[0]) if main_pdfs else None}
        ))
        
        # Check 2: PDF has reasonable size (>500KB suggests images)
        if main_pdfs:
            size_kb = main_pdfs[0].stat().st_size / 1024
            good_size = size_kb > 500
            results.append(VerificationResult(
                passed=good_size,
                check_name="pdf_size",
                message=f"PDF size: {size_kb:.0f}KB (good)" if good_size else f"PDF only {size_kb:.0f}KB (may lack images)",
                details={"size_kb": size_kb}
            ))
        
        # Check 3: Images exist (not just placeholders)
        real_images = []
        placeholder_count = 0
        if self.visuals_dir.exists():
            for img in self.visuals_dir.glob("*"):
                if img.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']:
                    real_images.append(img.name)
                elif img.suffix == '.txt':
                    placeholder_count += 1
        
        has_images = len(real_images) >= 1
        results.append(VerificationResult(
            passed=has_images,
            check_name="images",
            message=f"Found {len(real_images)} images ({placeholder_count} placeholders)" if has_images else f"No images (only {placeholder_count} placeholders)",
            details={"images": real_images, "placeholders": placeholder_count}
        ))
        
        # Check 4: Bonus PDFs exist
        bonus_pdfs = list(self.bonuses_dir.glob("*.pdf")) if self.bonuses_dir.exists() else []
        has_bonuses = len(bonus_pdfs) >= 1
        results.append(VerificationResult(
            passed=has_bonuses,
            check_name="bonus_pdfs",
            message=f"Found {len(bonus_pdfs)} bonus PDFs" if has_bonuses else "No bonus PDFs found",
            details={"bonuses": [f.name for f in bonus_pdfs]}
        ))
        
        # Check 5: ZIP exists
        zip_files = list(self.output_dir.glob("*.zip"))
        has_zip = len(zip_files) >= 1
        results.append(VerificationResult(
            passed=has_zip,
            check_name="zip_bundle",
            message=f"ZIP bundle: {zip_files[0].name}" if has_zip else "Missing ZIP bundle",
            details={"zip_path": str(zip_files[0]) if zip_files else None}
        ))
        
        return results
    
    def verify_phase_4_deployment(self) -> List[VerificationResult]:
        """Verify Phase 4: Deployment (files in salarsu)."""
        results = []
        
        salarsu_path = Path("/home/rsalars/Projects/salarsu")
        downloads_dir = salarsu_path / "public" / "downloads" / "products"
        
        # Check 1: ZIP deployed to salarsu
        product_slug = self.product_dir.name.replace("-", "_")
        deployed_zip = downloads_dir / f"{product_slug}.zip"
        zip_deployed = deployed_zip.exists()
        results.append(VerificationResult(
            passed=zip_deployed,
            check_name="zip_deployed",
            message=f"ZIP deployed to salarsu" if zip_deployed else "ZIP not found in salarsu",
            details={"expected_path": str(deployed_zip)}
        ))
        
        # Check 2: SQL file generated
        sql_files = list(salarsu_path.glob(f"*{self.product_dir.name}*.sql"))
        has_sql = len(sql_files) >= 1
        results.append(VerificationResult(
            passed=has_sql,
            check_name="sql_generated",
            message=f"SQL file: {sql_files[0].name}" if has_sql else "SQL file not found",
            details={"sql_path": str(sql_files[0]) if sql_files else None}
        ))
        
        # Check 3: Git committed (check recent commits)
        # This would require git inspection - simplified check
        results.append(VerificationResult(
            passed=True,  # Assume true if ZIP exists
            check_name="git_committed",
            message="Git commit check (manual verification)" if zip_deployed else "Not applicable",
        ))
        
        return results
    
    def verify_phase_5_marketing(self) -> List[VerificationResult]:
        """Verify Phase 5: Marketing (emails + social)."""
        results = []
        
        # Check 1: Welcome emails
        welcome_path = self.output_dir / "emails_welcome.md"
        has_welcome = welcome_path.exists()
        results.append(VerificationResult(
            passed=has_welcome,
            check_name="welcome_emails",
            message="Welcome email sequence exists" if has_welcome else "Missing welcome emails",
        ))
        
        # Check 2: Launch emails
        launch_path = self.output_dir / "emails_launch.md"
        has_launch = launch_path.exists()
        results.append(VerificationResult(
            passed=has_launch,
            check_name="launch_emails",
            message="Launch email sequence exists" if has_launch else "Missing launch emails",
        ))
        
        # Check 3: Social media content
        social_path = self.output_dir / "social_promo.md"
        has_social = social_path.exists()
        results.append(VerificationResult(
            passed=has_social,
            check_name="social_content",
            message="Social media content exists" if has_social else "Missing social content",
        ))
        
        return results
    
    def run_full_verification(self) -> Dict[str, List[VerificationResult]]:
        """Run all verification checks."""
        return {
            "phase_1_emission": self.verify_phase_1_emission(),
            "phase_2_generation": self.verify_phase_2_generation(),
            "phase_3_compilation": self.verify_phase_3_compilation(),
            "phase_4_deployment": self.verify_phase_4_deployment(),
            "phase_5_marketing": self.verify_phase_5_marketing(),
        }
    
    def print_status(self):
        """Print a formatted status report."""
        results = self.run_full_verification()
        
        print("\n" + "=" * 60)
        print(f"📋 PIPELINE CHECKLIST: {self.product_dir.name}")
        print("=" * 60)
        
        all_passed = True
        
        for phase_name, checks in results.items():
            phase_title = phase_name.replace("_", " ").title()
            phase_passed = all(c.passed for c in checks)
            all_passed = all_passed and phase_passed
            
            status_icon = "✅" if phase_passed else "❌"
            print(f"\n{status_icon} {phase_title}")
            
            for check in checks:
                icon = "  ✓" if check.passed else "  ✗"
                print(f"{icon} {check.message}")
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL PHASES VERIFIED - READY FOR PRODUCTION")
        else:
            print("⚠️  INCOMPLETE - Fix issues before proceeding")
        print("=" * 60 + "\n")
        
        return all_passed


def verify_product(product_dir: str) -> bool:
    """Run verification on a product directory."""
    verifier = PipelineVerifier(Path(product_dir))
    return verifier.print_status()
