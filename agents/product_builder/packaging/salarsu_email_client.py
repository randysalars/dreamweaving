"""
Salarsu Email Client
Registers generated email sequences with the SalarsNet email system.
"""

import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)


@dataclass
class RegistrationResult:
    """Result of registering an email sequence."""
    success: bool
    product_slug: str
    templates_registered: int
    message: str
    template_ids: List[str] = None
    error: str = None


class SalarsuEmailClient:
    """
    Client for registering email sequences with the SalarsNet email system.
    
    Uses the /api/admin/email-sequences endpoint.
    """
    
    def __init__(self, api_base_url: str = None, api_key: str = None):
        self.api_base_url = api_base_url or os.getenv("SALARSU_API_URL", "https://www.salars.net")
        self.api_key = api_key or os.getenv("SALARSU_ADMIN_API_KEY", "")
        
        if not self.api_key:
            logger.warning("No SALARSU_ADMIN_API_KEY set. Registration will require login session.")
    
    def register_sequence(
        self,
        product_slug: str,
        product_title: str,
        emails: List[Dict],
        dry_run: bool = False
    ) -> RegistrationResult:
        """
        Register an email sequence with SalarsNet.
        
        Args:
            product_slug: URL-safe product identifier
            product_title: Display name of the product
            emails: List of email dicts with subject, body, send_delay_hours
            dry_run: If True, validate without actually registering
            
        Returns:
            RegistrationResult with success status
        """
        logger.info(f"📧 Registering email sequence for: {product_title}")
        logger.info(f"   Product slug: {product_slug}")
        logger.info(f"   Emails to register: {len(emails)}")
        
        if dry_run:
            logger.info("   🧪 Dry run mode - no actual registration")
            return RegistrationResult(
                success=True,
                product_slug=product_slug,
                templates_registered=len(emails),
                message=f"[DRY RUN] Would register {len(emails)} templates"
            )
        
        # Prepare request
        endpoint = f"{self.api_base_url}/api/admin/email-sequences"
        
        payload = {
            "product_slug": product_slug,
            "product_title": product_title,
            "emails": emails
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info(f"✅ Registration successful: {data.get('message')}")
                
                return RegistrationResult(
                    success=True,
                    product_slug=product_slug,
                    templates_registered=len(data.get('templates', [])),
                    message=data.get('message', 'Success'),
                    template_ids=[t['id'] for t in data.get('templates', [])]
                )
            
            elif response.status_code == 401:
                logger.error("❌ Authentication failed. Check SALARSU_ADMIN_API_KEY.")
                return RegistrationResult(
                    success=False,
                    product_slug=product_slug,
                    templates_registered=0,
                    message="Authentication failed",
                    error="401 Unauthorized - Check API key"
                )
            
            else:
                error_data = response.json() if response.content else {}
                logger.error(f"❌ Registration failed: {response.status_code}")
                return RegistrationResult(
                    success=False,
                    product_slug=product_slug,
                    templates_registered=0,
                    message="Registration failed",
                    error=error_data.get('error', f"HTTP {response.status_code}")
                )
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Could not connect to {self.api_base_url}")
            return RegistrationResult(
                success=False,
                product_slug=product_slug,
                templates_registered=0,
                message="Connection failed",
                error=f"Could not connect to {self.api_base_url}"
            )
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return RegistrationResult(
                success=False,
                product_slug=product_slug,
                templates_registered=0,
                message="Error",
                error=str(e)
            )
    
    def register_from_file(
        self,
        product_slug: str,
        product_title: str,
        email_file: Path,
        dry_run: bool = False
    ) -> RegistrationResult:
        """
        Register emails from a markdown file (generated by EmailSequenceGenerator).
        
        Args:
            product_slug: URL-safe product identifier
            product_title: Display name
            email_file: Path to emails_*.md file
            dry_run: If True, validate without registering
            
        Returns:
            RegistrationResult
        """
        logger.info(f"📄 Reading emails from: {email_file}")
        
        if not email_file.exists():
            return RegistrationResult(
                success=False,
                product_slug=product_slug,
                templates_registered=0,
                message="File not found",
                error=f"Email file not found: {email_file}"
            )
        
        # Parse the markdown file
        emails = self._parse_email_markdown(email_file)
        
        if not emails:
            return RegistrationResult(
                success=False,
                product_slug=product_slug,
                templates_registered=0,
                message="No emails found",
                error="Could not parse any emails from the file"
            )
        
        return self.register_sequence(product_slug, product_title, emails, dry_run)
    
    def _parse_email_markdown(self, file_path: Path) -> List[Dict]:
        """Parse emails from a markdown file."""
        content = file_path.read_text()
        emails = []
        
        # Simple parser for the email markdown format
        import re
        
        # Split by email sections
        email_sections = re.split(r'## Email \d+:', content)
        
        for section in email_sections[1:]:  # Skip header
            email = {}
            
            # Extract subject
            subject_match = re.search(r'\*\*Subject:\*\* (.+)', section)
            if subject_match:
                email['subject'] = subject_match.group(1).strip()
            
            # Extract send delay
            day_match = re.search(r'\*\*Send:\*\* Day (\d+)', section)
            if day_match:
                email['send_delay_hours'] = int(day_match.group(1)) * 24
            
            # Extract body (between ``` markers)
            body_match = re.search(r'```\n(.*?)\n```', section, re.DOTALL)
            if body_match:
                email['body'] = body_match.group(1).strip()
            
            if email.get('subject') and email.get('body'):
                emails.append(email)
        
        logger.info(f"   Parsed {len(emails)} emails from file")
        return emails
    
    def list_sequences(self, product_slug: str = None) -> List[Dict]:
        """List registered email sequences."""
        endpoint = f"{self.api_base_url}/api/admin/email-sequences"
        
        if product_slug:
            endpoint += f"?product_slug={product_slug}"
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('templates', [])
            else:
                logger.error(f"Failed to list sequences: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing sequences: {e}")
            return []
    
    def delete_sequence(self, product_slug: str) -> bool:
        """Delete all email templates for a product."""
        endpoint = f"{self.api_base_url}/api/admin/email-sequences"
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.delete(
                endpoint,
                json={"product_slug": product_slug},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Deleted {data.get('count', 0)} templates")
                return True
            else:
                logger.error(f"Failed to delete: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting sequence: {e}")
            return False


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    return "".join(c if c.isalnum() or c == " " else "" for c in text).replace(" ", "-").lower()
