#!/usr/bin/env python3
"""
Enhanced SSML Validator with Auto-Fix
Validates SSML syntax, provides detailed feedback, and can auto-fix common issues.

Usage:
    python3 scripts/utilities/validate_ssml_enhanced.py path/to/script.ssml
    python3 scripts/utilities/validate_ssml_enhanced.py path/to/script.ssml --fix
"""

import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Tuple

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

class SSMLValidator:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.content = ""
        self.issues = []
        self.warnings = []
        self.fixes_applied = []
        
    def validate(self) -> bool:
        """Run all validation checks"""
        print(f"{BOLD}=== SSML Validator ==={RESET}\n")
        print(f"File: {self.file_path}\n")
        
        # Load file
        if not self.load_file():
            return False
        
        # Run checks
        self.check_file_size()
        self.check_xml_structure()
        self.check_required_tags()
        self.check_break_tags()
        self.check_prosody_tags()
        self.check_emphasis_tags()
        self.check_common_errors()
        
        # Print results
        self.print_results()
        
        return len(self.issues) == 0
    
    def load_file(self) -> bool:
        """Load SSML file"""
        if not self.file_path.exists():
            print(f"{RED}✗ File not found: {self.file_path}{RESET}\n")
            return False
        
        try:
            self.content = self.file_path.read_text(encoding='utf-8')
            return True
        except Exception as e:
            print(f"{RED}✗ Error reading file: {e}{RESET}\n")
            return False
    
    def check_file_size(self):
        """Check file size and warn if large"""
        size = len(self.content.encode('utf-8'))
        
        if size > 5000:
            self.warnings.append({
                'check': 'File Size',
                'problem': f'Large file ({size} bytes)',
                'fix': 'Use generate_audio_chunked.py for files >5KB',
                'auto_fix': None
            })
        elif size == 0:
            self.issues.append({
                'check': 'File Size',
                'problem': 'Empty file',
                'fix': 'Add SSML content',
                'auto_fix': None
            })
    
    def check_xml_structure(self):
        """Validate XML structure"""
        try:
            # Try to parse as XML
            root = ET.fromstring(self.content)
            
        except ET.ParseError as e:
            self.issues.append({
                'check': 'XML Structure',
                'problem': f'Invalid XML: {e}',
                'fix': 'Fix XML syntax errors',
                'auto_fix': None
            })
            
            # Try to auto-detect common XML errors
            self.detect_xml_errors()
    
    def detect_xml_errors(self):
        """Detect common XML errors and suggest fixes"""
        # Unclosed tags
        open_tags = re.findall(r'<(\w+)(?:\s|>)', self.content)
        close_tags = re.findall(r'</(\w+)>', self.content)
        
        for tag in open_tags:
            if tag not in ['break', 'phoneme']:  # Self-closing tags
                if open_tags.count(tag) != close_tags.count(tag):
                    self.issues.append({
                        'check': 'Unclosed Tag',
                        'problem': f'Tag <{tag}> may be unclosed',
                        'fix': f'Ensure all <{tag}> tags have matching </{tag}>',
                        'auto_fix': None
                    })
        
        # Unescaped special characters
        if '&' in self.content and not re.search(r'&[a-z]+;', self.content):
            self.warnings.append({
                'check': 'Special Characters',
                'problem': 'Unescaped & character found',
                'fix': 'Replace & with &amp;',
                'auto_fix': 'escape_ampersand'
            })
        
        if '<' in self.content.replace('</', '').replace('<?', ''):
            # Check for < not in tags
            if re.search(r'>[^<]*<(?![/!?\w])', self.content):
                self.warnings.append({
                    'check': 'Special Characters',
                    'problem': 'Unescaped < character found',
                    'fix': 'Replace < with &lt;',
                    'auto_fix': 'escape_lt'
                })
    
    def check_required_tags(self):
        """Check for required SSML structure"""
        if '<speak' not in self.content:
            self.issues.append({
                'check': 'Required Tags',
                'problem': 'Missing <speak> root tag',
                'fix': 'Wrap content in <speak>...</speak>',
                'auto_fix': 'add_speak_tag'
            })
    
    def check_break_tags(self):
        """Validate break tags"""
        breaks = re.findall(r'<break\s+time="([^"]+)"\s*/>', self.content)
        
        for break_time in breaks:
            # Check format
            if not re.match(r'^\d+(\.\d+)?(ms|s)$', break_time):
                self.warnings.append({
                    'check': 'Break Tag',
                    'problem': f'Invalid break time format: {break_time}',
                    'fix': 'Use format: "1s" or "500ms"',
                    'auto_fix': None
                })
            
            # Check for very long breaks
            if break_time.endswith('s'):
                seconds = float(break_time[:-1])
                if seconds > 10:
                    self.warnings.append({
                        'check': 'Break Tag',
                        'problem': f'Very long break: {break_time}',
                        'fix': 'Consider if {seconds}s pause is intentional',
                        'auto_fix': None
                    })
    
    def check_prosody_tags(self):
        """Validate prosody tags"""
        prosody_tags = re.findall(r'<prosody([^>]+)>', self.content)

        for attrs in prosody_tags:
            # Check rate
            if 'rate=' in attrs:
                rate = re.search(r'rate="([^"]+)"', attrs)
                if rate:
                    rate_val = rate.group(1)
                    valid_rates = ['x-slow', 'slow', 'medium', 'fast', 'x-fast']
                    # Check if it's a decimal (like 0.85) and convert to percentage
                    if re.match(r'^0?\.\d+$', rate_val):
                        self.warnings.append({
                            'check': 'Prosody Tag',
                            'problem': f'Rate {rate_val} should be percentage',
                            'fix': f'Convert to percentage (e.g., "85%")',
                            'auto_fix': 'convert_rate_to_percentage'
                        })
                    elif rate_val not in valid_rates and not re.match(r'\d+%', rate_val):
                        self.warnings.append({
                            'check': 'Prosody Tag',
                            'problem': f'Invalid rate: {rate_val}',
                            'fix': f'Use: {", ".join(valid_rates)} or percentage (e.g., "85%")',
                            'auto_fix': None
                        })
            
            # Check pitch
            if 'pitch=' in attrs:
                pitch = re.search(r'pitch="([^"]+)"', attrs)
                if pitch:
                    pitch_val = pitch.group(1)
                    if not re.match(r'[+-]?\d+(\.\d+)?(st|Hz)?', pitch_val):
                        valid_pitches = ['x-low', 'low', 'medium', 'high', 'x-high']
                        if pitch_val not in valid_pitches:
                            self.warnings.append({
                                'check': 'Prosody Tag',
                                'problem': f'Invalid pitch: {pitch_val}',
                                'fix': f'Use: {", ".join(valid_pitches)} or semitones (e.g., "-2st")',
                                'auto_fix': None
                            })
    
    def check_emphasis_tags(self):
        """Validate emphasis tags"""
        emphasis_tags = re.findall(r'<emphasis level="([^"]+)">', self.content)
        
        valid_levels = ['strong', 'moderate', 'reduced']
        for level in emphasis_tags:
            if level not in valid_levels:
                self.warnings.append({
                    'check': 'Emphasis Tag',
                    'problem': f'Invalid emphasis level: {level}',
                    'fix': f'Use: {", ".join(valid_levels)}',
                    'auto_fix': None
                })
    
    def check_common_errors(self):
        """Check for common SSML errors"""
        # Check for invalid break syntax
        if re.search(r'<break time="\d+">', self.content):  # Missing unit
            self.warnings.append({
                'check': 'Break Syntax',
                'problem': 'Break tag missing time unit (s or ms)',
                'fix': 'Add unit: <break time="1s"/> or <break time="500ms"/>',
                'auto_fix': 'add_break_units'
            })
        
        # Check for self-closing tags that aren't self-closed
        if re.search(r'<break[^/]*></break>', self.content):
            self.warnings.append({
                'check': 'Break Syntax',
                'problem': 'Break tag should be self-closing',
                'fix': 'Use: <break time="1s"/> not <break time="1s"></break>',
                'auto_fix': 'fix_break_closing'
            })
        
        # Check for very long content without breaks
        paragraphs = self.content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if len(para) > 500 and '<break' not in para:
                self.warnings.append({
                    'check': 'Content Flow',
                    'problem': f'Paragraph {i+1} is long ({len(para)} chars) with no breaks',
                    'fix': 'Consider adding <break/> tags for natural pauses',
                    'auto_fix': None
                })
    
    def print_results(self):
        """Print validation results"""
        print(f"\n{BOLD}=== Results ==={RESET}\n")
        
        # File info
        size = len(self.content.encode('utf-8'))
        lines = self.content.count('\n') + 1
        print(f"{BLUE}File:{RESET} {size} bytes, {lines} lines\n")
        
        # Issues
        if self.issues:
            print(f"{RED}{BOLD}✗ Issues ({len(self.issues)}):{RESET}")
            for issue in self.issues:
                print(f"  {RED}✗{RESET} {BOLD}{issue['check']}:{RESET} {issue['problem']}")
                print(f"    {BLUE}Fix:{RESET} {issue['fix']}")
            print()
        
        # Warnings
        if self.warnings:
            print(f"{YELLOW}{BOLD}⚠ Warnings ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {BOLD}{warning['check']}:{RESET} {warning['problem']}")
                print(f"    {BLUE}Fix:{RESET} {warning['fix']}")
            print()
        
        # Success
        if not self.issues and not self.warnings:
            print(f"{GREEN}{BOLD}✓ SSML is valid!{RESET}\n")
        elif not self.issues:
            print(f"{GREEN}✓ No critical issues (only warnings){RESET}\n")
        
        # Auto-fix available?
        auto_fixable = [w for w in self.warnings + self.issues if w.get('auto_fix')]
        if auto_fixable:
            print(f"{BOLD}=== Auto-Fix Available ==={RESET}\n")
            print(f"Can automatically fix {len(auto_fixable)} issue(s)")
            print(f"\nRun with --fix to apply: {BLUE}python3 {sys.argv[0]} {self.file_path} --fix{RESET}\n")
    
    def apply_fixes(self):
        """Apply automatic fixes"""
        print(f"{BOLD}=== Applying Auto-Fixes ==={RESET}\n")
        
        original = self.content
        
        # Apply each fix
        for item in self.warnings + self.issues:
            auto_fix = item.get('auto_fix')
            if not auto_fix:
                continue
            
            if auto_fix == 'escape_ampersand':
                # Don't escape already-escaped ampersands
                self.content = re.sub(r'&(?![a-z]+;)', '&amp;', self.content)
                print(f"{GREEN}✓{RESET} Escaped & characters")
                self.fixes_applied.append('Escaped ampersands')
            
            elif auto_fix == 'add_speak_tag':
                self.content = f'<speak>\n{self.content}\n</speak>'
                print(f"{GREEN}✓{RESET} Added <speak> wrapper")
                self.fixes_applied.append('Added speak tag')
            
            elif auto_fix == 'add_break_units':
                # Add 's' to breaks without units
                self.content = re.sub(r'<break time="(\d+)"', r'<break time="\1s"', self.content)
                print(f"{GREEN}✓{RESET} Added time units to break tags")
                self.fixes_applied.append('Added break time units')
            
            elif auto_fix == 'fix_break_closing':
                # Convert <break></break> to <break/>
                self.content = re.sub(r'<break([^>]*)></break>', r'<break\1/>', self.content)
                print(f"{GREEN}✓{RESET} Fixed break tag closing")
                self.fixes_applied.append('Fixed break tag syntax')

            elif auto_fix == 'convert_rate_to_percentage':
                # Convert decimal rates (0.85) to percentages (85%)
                def convert_rate(match):
                    rate_val = match.group(1)
                    percentage = int(float(rate_val) * 100)
                    return f'rate="{percentage}%"'

                self.content = re.sub(r'rate="(0?\.\d+)"', convert_rate, self.content)
                print(f"{GREEN}✓{RESET} Converted decimal rates to percentages")
                self.fixes_applied.append('Converted rates to percentages')
        
        # Save if changes were made
        if self.content != original:
            # Backup original
            backup_path = self.file_path.with_suffix('.ssml.bak')
            backup_path.write_text(original, encoding='utf-8')
            print(f"\n{BLUE}Backup saved:{RESET} {backup_path}")
            
            # Save fixed version
            self.file_path.write_text(self.content, encoding='utf-8')
            print(f"{GREEN}✓ Fixed version saved:{RESET} {self.file_path}\n")
            
            print(f"{GREEN}{BOLD}Applied {len(self.fixes_applied)} fixes{RESET}\n")
        else:
            print(f"{YELLOW}No auto-fixable issues found{RESET}\n")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <ssml_file> [--fix]")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    validator = SSMLValidator(file_path)
    
    # Validate
    valid = validator.validate()
    
    # Apply fixes if requested
    if '--fix' in sys.argv:
        validator.apply_fixes()
        # Re-validate
        print(f"{BOLD}=== Re-validating ==={RESET}\n")
        validator = SSMLValidator(file_path)
        valid = validator.validate()
    
    # Exit code
    sys.exit(0 if valid else 1)

if __name__ == '__main__':
    main()
