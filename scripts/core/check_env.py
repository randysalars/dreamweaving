#!/usr/bin/env python3
"""
Environment Validation and Setup Script
Checks all prerequisites and provides fixes for common issues.
"""

import sys
import subprocess
import os
import shutil
from pathlib import Path
import json

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

class EnvironmentChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        self.project_root = Path(__file__).parent.parent.parent
        
    def check_all(self):
        """Run all environment checks"""
        print(f"{BOLD}=== Dreamweaving Environment Validator ==={RESET}\n")
        
        # Core checks
        self.check_python_version()
        self.check_virtual_env()
        self.check_python_packages()
        self.check_ffmpeg()
        self.check_gcloud()
        self.check_google_auth()
        self.check_disk_space()
        self.check_permissions()
        self.check_directory_structure()
        
        # Print results
        self.print_results()
        
        # Offer fixes
        if self.issues:
            self.offer_fixes()
        
        return len(self.issues) == 0
    
    def check_python_version(self):
        """Check Python version is 3.8+"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.passed.append(f"Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.issues.append({
                'check': 'Python Version',
                'problem': f'Python {version.major}.{version.minor} found, need 3.8+',
                'fix': 'Install Python 3.8 or higher'
            })
    
    def check_virtual_env(self):
        """Check if running in virtual environment"""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            self.passed.append(f"Virtual environment active: {sys.prefix}")
        else:
            self.warnings.append({
                'check': 'Virtual Environment',
                'problem': 'Not running in virtual environment',
                'fix': 'Run: source venv/bin/activate'
            })
    
    def check_python_packages(self):
        """Check required Python packages"""
        required_packages = {
            'google.cloud.texttospeech': 'google-cloud-texttospeech',
            'pydub': 'pydub',
            'mutagen': 'mutagen',
            'tqdm': 'tqdm'
        }
        
        missing = []
        for import_name, package_name in required_packages.items():
            try:
                __import__(import_name)
                self.passed.append(f"Package: {package_name}")
            except ImportError:
                missing.append(package_name)
        
        if missing:
            self.issues.append({
                'check': 'Python Packages',
                'problem': f"Missing packages: {', '.join(missing)}",
                'fix': f"pip install {' '.join(missing)}"
            })
    
    def check_ffmpeg(self):
        """Check FFmpeg installation"""
        if shutil.which('ffmpeg'):
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version_line = result.stdout.split('\n')[0]
                self.passed.append(f"FFmpeg: {version_line}")
            except Exception as e:
                self.warnings.append({
                    'check': 'FFmpeg',
                    'problem': f'FFmpeg found but error checking version: {e}',
                    'fix': 'Reinstall FFmpeg'
                })
        else:
            self.issues.append({
                'check': 'FFmpeg',
                'problem': 'FFmpeg not found in PATH',
                'fix': 'Ubuntu/Debian: sudo apt install ffmpeg\nmacOS: brew install ffmpeg'
            })
    
    def check_gcloud(self):
        """Check Google Cloud SDK"""
        if shutil.which('gcloud'):
            try:
                result = subprocess.run(
                    ['gcloud', 'version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                self.passed.append("Google Cloud SDK installed")
            except Exception as e:
                self.warnings.append({
                    'check': 'gcloud',
                    'problem': f'gcloud found but error: {e}',
                    'fix': 'Reinstall Google Cloud SDK'
                })
        else:
            self.issues.append({
                'check': 'Google Cloud SDK',
                'problem': 'gcloud not found in PATH',
                'fix': 'Install: curl https://sdk.cloud.google.com | bash'
            })
    
    def check_google_auth(self):
        """Check Google Cloud authentication"""
        if not shutil.which('gcloud'):
            return  # Already flagged in check_gcloud
        
        try:
            result = subprocess.run(
                ['gcloud', 'auth', 'application-default', 'print-access-token'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.passed.append("Google Cloud authentication configured")
            else:
                self.issues.append({
                    'check': 'Google Cloud Auth',
                    'problem': 'Not authenticated with Google Cloud',
                    'fix': 'Run: gcloud auth application-default login'
                })
        except Exception as e:
            self.issues.append({
                'check': 'Google Cloud Auth',
                'problem': f'Error checking authentication: {e}',
                'fix': 'Run: gcloud auth application-default login'
            })
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            stat = os.statvfs(self.project_root)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            
            if free_gb >= 5:
                self.passed.append(f"Disk space: {free_gb:.1f} GB available")
            elif free_gb >= 1:
                self.warnings.append({
                    'check': 'Disk Space',
                    'problem': f'Low disk space: {free_gb:.1f} GB available',
                    'fix': 'Free up disk space (recommend 5+ GB for audio generation)'
                })
            else:
                self.issues.append({
                    'check': 'Disk Space',
                    'problem': f'Critical disk space: {free_gb:.1f} GB available',
                    'fix': 'Free up disk space immediately'
                })
        except Exception as e:
            self.warnings.append({
                'check': 'Disk Space',
                'problem': f'Could not check disk space: {e}',
                'fix': 'Manually verify sufficient disk space'
            })
    
    def check_permissions(self):
        """Check file permissions"""
        test_dirs = [
            self.project_root / 'sessions',
            self.project_root / 'scripts',
        ]
        
        issues = []
        for dir_path in test_dirs:
            if not dir_path.exists():
                continue
            if not os.access(dir_path, os.W_OK):
                issues.append(str(dir_path))
        
        if issues:
            self.issues.append({
                'check': 'File Permissions',
                'problem': f'No write access to: {", ".join(issues)}',
                'fix': f'Fix permissions: chmod -R u+w {" ".join(issues)}'
            })
        else:
            self.passed.append("File permissions OK")
    
    def check_directory_structure(self):
        """Check required directories exist"""
        required_dirs = [
            'sessions',
            'scripts/core',
            'scripts/utilities',
            'docs',
            'config'
        ]
        
        missing = []
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing.append(dir_name)
        
        if missing:
            self.warnings.append({
                'check': 'Directory Structure',
                'problem': f'Missing directories: {", ".join(missing)}',
                'fix': f'Create: mkdir -p {" ".join(missing)}'
            })
        else:
            self.passed.append("Directory structure OK")
    
    def print_results(self):
        """Print check results"""
        print(f"\n{BOLD}=== Results ==={RESET}\n")
        
        # Passed checks
        if self.passed:
            print(f"{GREEN}{BOLD}✓ Passed ({len(self.passed)}):{RESET}")
            for item in self.passed:
                print(f"  {GREEN}✓{RESET} {item}")
            print()
        
        # Warnings
        if self.warnings:
            print(f"{YELLOW}{BOLD}⚠ Warnings ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {BOLD}{warning['check']}:{RESET} {warning['problem']}")
                print(f"    {BLUE}Fix:{RESET} {warning['fix']}")
            print()
        
        # Issues
        if self.issues:
            print(f"{RED}{BOLD}✗ Issues ({len(self.issues)}):{RESET}")
            for issue in self.issues:
                print(f"  {RED}✗{RESET} {BOLD}{issue['check']}:{RESET} {issue['problem']}")
                print(f"    {BLUE}Fix:{RESET} {issue['fix']}")
            print()
    
    def offer_fixes(self):
        """Offer to auto-fix issues"""
        print(f"{BOLD}=== Auto-Fix Available ==={RESET}\n")
        
        fixable = []
        for issue in self.issues:
            if issue['check'] in ['Python Packages', 'Directory Structure']:
                fixable.append(issue)
        
        if not fixable:
            print(f"{YELLOW}No auto-fixable issues. Please apply fixes manually.{RESET}\n")
            return
        
        print(f"Can automatically fix {len(fixable)} issue(s):\n")
        for issue in fixable:
            print(f"  • {issue['check']}: {issue['problem']}")
        
        print(f"\n{BOLD}Run with --fix to apply automatic fixes{RESET}")
        print(f"Example: {BLUE}python3 scripts/core/check_env.py --fix{RESET}\n")
    
    def apply_fixes(self):
        """Apply automatic fixes"""
        print(f"{BOLD}=== Applying Auto-Fixes ==={RESET}\n")
        
        for issue in self.issues:
            if issue['check'] == 'Python Packages':
                print(f"{BLUE}Installing missing Python packages...{RESET}")
                # Extract package names from fix command
                packages = issue['fix'].replace('pip install ', '').split()
                try:
                    subprocess.run(
                        [sys.executable, '-m', 'pip', 'install'] + packages,
                        check=True
                    )
                    print(f"{GREEN}✓ Packages installed{RESET}\n")
                except subprocess.CalledProcessError as e:
                    print(f"{RED}✗ Failed to install packages: {e}{RESET}\n")
            
            elif issue['check'] == 'Directory Structure':
                print(f"{BLUE}Creating missing directories...{RESET}")
                # Extract directory names from problem
                dirs = issue['problem'].replace('Missing directories: ', '').split(', ')
                for dir_name in dirs:
                    dir_path = self.project_root / dir_name
                    dir_path.mkdir(parents=True, exist_ok=True)
                print(f"{GREEN}✓ Directories created{RESET}\n")
        
        print(f"{GREEN}{BOLD}Auto-fixes applied. Re-run check to verify.{RESET}\n")

def main():
    checker = EnvironmentChecker()
    
    # Check for --fix flag
    if '--fix' in sys.argv:
        checker.check_all()
        if checker.issues:
            checker.apply_fixes()
            # Re-check
            print(f"\n{BOLD}=== Re-checking Environment ==={RESET}\n")
            checker = EnvironmentChecker()
            success = checker.check_all()
        else:
            success = True
    else:
        success = checker.check_all()
    
    # Exit code
    if success:
        print(f"{GREEN}{BOLD}✓ Environment ready for Dreamweaving!{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}✗ Please fix issues before proceeding.{RESET}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
