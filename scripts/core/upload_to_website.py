#!/usr/bin/env python3
"""
Upload dreamweaving session to Salarsu website.

This script uploads a completed dreamweaving session to the Salarsu website,
including media files (audio, video, thumbnail, subtitles) and metadata.

Supports two storage backends:
  - Cloudflare R2 (recommended - free egress, cheap storage)
  - Vercel Blob (legacy - limited to 1GB on hobby plan)

Usage:
    python3 scripts/core/upload_to_website.py --session sessions/forest-of-lost-instincts/
    python3 scripts/core/upload_to_website.py --session sessions/forest-of-lost-instincts/ --dry-run
    python3 scripts/core/upload_to_website.py --session sessions/forest-of-lost-instincts/ --storage r2
    python3 scripts/core/upload_to_website.py --session sessions/forest-of-lost-instincts/ --category nature-forest

Options:
    --session PATH      Path to session directory (required)
    --dry-run           Validate without uploading
    --no-git            Skip git operations
    --api-url URL       Override API endpoint (default: https://www.salars.net)
    --category SLUG     Override auto-detected category
    --storage BACKEND   Storage backend: 'r2' (default) or 'vercel'

Environment Variables (for R2 - recommended):
    R2_ACCOUNT_ID       Cloudflare account ID
    R2_ACCESS_KEY_ID    R2 access key ID
    R2_SECRET_ACCESS_KEY R2 secret access key
    R2_BUCKET_NAME      R2 bucket name (default: dreamweavings)
    R2_PUBLIC_URL       Public URL for the bucket (e.g., https://media.salars.net)

Environment Variables (for Vercel Blob - legacy):
    BLOB_READ_WRITE_TOKEN  Vercel Blob token
    SALARSU_API_TOKEN      API authentication token
"""

import argparse
import json
import os
import sys
import requests
import yaml
import hashlib
import hmac
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote

# Import SEO title generator
from scripts.core.seo_title_generator import generate_seo_title, generate_seo_metadata as generate_seo_package

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on environment

# Configuration
DEFAULT_API_URL = "https://www.salars.net"
SALARSU_PROJECT_PATH = "/media/rsalars/elements/Projects/salarsu"

# Category mapping based on session themes/keywords
def extract_display_title(topic: str, slug: str) -> str:
    """
    Extract a clean display title from the topic string or slug.

    Examples:
        "Ascent to Olympus: The Throne of Zeus | Explore Zeus'..." -> "Ascent to Olympus: The Throne of Zeus"
        "Journey to Tír na nÓg — The Land of Eternal Youth | ..." -> "Journey to Tír na nÓg: The Land of Eternal Youth"
        "ascent-to-olympus-the-throne-of-zeus-exp-20251204" -> "Ascent to Olympus: The Throne of Zeus"
    """
    import re

    if topic:
        title = _extract_title_from_topic(topic)
        # Normalize em-dashes to colons for consistency
        title = title.replace(" — ", ": ").replace(" – ", ": ")
        return title

    # Fallback: Convert slug to title
    return _convert_slug_to_title(slug)


def _extract_title_from_topic(topic: str) -> str:
    """Extract title portion from a topic string."""
    # Split on pipe first (most common delimiter)
    if " | " in topic:
        return topic.split(" | ")[0].strip()

    # Handle em-dash subtitles
    if " — " in topic:
        parts = topic.split(" — ")
        if len(parts) >= 2 and len(parts[1]) < 50:
            return f"{parts[0]}: {parts[1]}".strip()
        return parts[0].strip()

    return topic.strip()


def _convert_slug_to_title(slug: str) -> str:
    """Convert a kebab-case slug to a proper title."""
    import re

    # Remove date suffixes
    clean_slug = re.sub(r'-exp-\d{8}$', '', slug)
    clean_slug = re.sub(r'-\d{8}$', '', clean_slug)

    # Convert kebab-case to words
    words = clean_slug.split('-')

    # Smart capitalization
    small_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by', 'of', 'in'}
    result = [
        word.capitalize() if (i == 0 or word not in small_words) else word
        for i, word in enumerate(words)
    ]

    return ' '.join(result)


# Import the enhanced categorization system
try:
    from categorization import ContentAnalyzer, categorize_session, get_available_categories
    from categorization.keywords import get_db_category
    ENHANCED_CATEGORIZATION = True
except ImportError:
    ENHANCED_CATEGORIZATION = False
    # Provide a fallback get_db_category function
    def get_db_category(slug: str) -> str:
        """Fallback mapping when categorization module unavailable."""
        return slug  # Return as-is if module not available
    # Fallback simple mapping (used only if categorization module unavailable)
    CATEGORY_MAPPING = {
        "forest": "nature-elements", "nature": "nature-elements", "garden": "nature-elements",
        "eden": "nature-elements", "tree": "nature-elements",
        "cosmic": "microscopic-cosmic", "space": "microscopic-cosmic", "star": "microscopic-cosmic",
        "astral": "paranormal-esoteric", "galaxy": "microscopic-cosmic",
        "healing": "healing-journeys", "restore": "healing-journeys", "heal": "healing-journeys",
        "shadow": "shadow-depths", "dark": "shadow-depths", "unconscious": "shadow-depths",
        "archetype": "archetypal-encounters", "journey": "guided-visualization",
        "guide": "guided-visualization", "animal": "shamanic-journeying",
        "sacred": "spiritual-religious", "divine": "spiritual-religious",
        "spiritual": "spiritual-religious", "holy": "spiritual-religious",
        "confidence": "personal-development", "power": "personal-development",
        "strength": "personal-development", "courage": "personal-development",
        "relax": "mindfulness-pathworkings", "sleep": "mindfulness-pathworkings",
        "calm": "mindfulness-pathworkings", "meditation": "mindfulness-pathworkings",
        "creative": "creative-inspiration", "inspiration": "creative-inspiration",
        "lucid": "lucid-dream-induction", "dream": "lucid-dream-induction",
        "mythic": "mythic-storywork", "myth": "mythic-storywork", "legend": "mythic-storywork",
        "quantum": "scientific-dimensional", "physics": "scientific-dimensional",
        "ai": "scientific-dimensional", "neural": "scientific-dimensional",
    }


class RollbackManager:
    """Track uploaded resources for rollback on failure."""

    def __init__(self):
        self.uploaded_urls = []
        self.db_record_slug = None

    def add_upload(self, url):
        """Track an uploaded file URL."""
        if url:
            self.uploaded_urls.append(url)

    def set_db_record(self, slug):
        """Track the created database record."""
        self.db_record_slug = slug

    def rollback(self, api_url, token):
        """Rollback all tracked resources."""
        print("\n=== ROLLING BACK ===")

        # Delete uploaded files
        for url in self.uploaded_urls:
            try:
                response = requests.delete(
                    f"{api_url}/api/dreamweavings/upload",
                    json={"url": url},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
                if response.status_code == 200:
                    print(f"  Deleted: {url[:60]}...")
                else:
                    print(f"  Failed to delete: {url[:60]}... ({response.status_code})")
            except Exception as e:
                print(f"  Error deleting {url[:60]}...: {e}")

        # Delete database record
        if self.db_record_slug:
            try:
                response = requests.delete(
                    f"{api_url}/api/dreamweavings/{self.db_record_slug}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
                if response.status_code == 200:
                    print(f"  Deleted DB record: {self.db_record_slug}")
                else:
                    print(f"  Failed to delete DB record: {self.db_record_slug} ({response.status_code})")
            except Exception as e:
                print(f"  Error deleting DB record: {e}")

        print("Rollback complete.")


# =============================================================================
# CLOUDFLARE R2 STORAGE BACKEND
# =============================================================================

class R2Storage:
    """Upload files to Cloudflare R2 using boto3 (S3-compatible API)."""

    def __init__(self):
        self.account_id = os.environ.get("R2_ACCOUNT_ID")
        self.access_key_id = os.environ.get("R2_ACCESS_KEY_ID")
        self.secret_access_key = os.environ.get("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.environ.get("R2_BUCKET_NAME", "dreamweavings")
        self.public_url = os.environ.get("R2_PUBLIC_URL", "").rstrip("/")

        # R2 endpoint
        if self.account_id:
            self.endpoint = f"https://{self.account_id}.r2.cloudflarestorage.com"
        else:
            self.endpoint = None

        # Initialize boto3 client for reliable uploads
        self._s3_client = None

    def _get_s3_client(self):
        """Get boto3 S3 client configured for R2."""
        if self._s3_client is None:
            try:
                import boto3
                from botocore.config import Config

                self._s3_client = boto3.client(
                    's3',
                    endpoint_url=self.endpoint,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    config=Config(
                        signature_version='s3v4',
                        retries={'max_attempts': 3, 'mode': 'adaptive'},
                        connect_timeout=30,
                        read_timeout=600,
                    ),
                    region_name='auto',  # R2 uses 'auto'
                )
            except ImportError:
                return None
        return self._s3_client

    def is_configured(self) -> bool:
        """Check if R2 is properly configured."""
        return all([
            self.account_id,
            self.access_key_id,
            self.secret_access_key,
            self.public_url,
        ])

    def get_missing_config(self) -> list:
        """Return list of missing environment variables."""
        missing = []
        if not self.account_id:
            missing.append("R2_ACCOUNT_ID")
        if not self.access_key_id:
            missing.append("R2_ACCESS_KEY_ID")
        if not self.secret_access_key:
            missing.append("R2_SECRET_ACCESS_KEY")
        if not self.public_url:
            missing.append("R2_PUBLIC_URL")
        return missing

    def _sign_request(self, method: str, path: str, headers: dict, payload_hash: str) -> dict:
        """Sign request using AWS Signature Version 4."""
        # AWS Sig V4 implementation for R2
        service = "s3"
        region = "auto"  # R2 uses 'auto' region

        now = datetime.now(timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        # Canonical request components
        canonical_uri = path
        canonical_querystring = ""

        # Build signed headers
        host = f"{self.account_id}.r2.cloudflarestorage.com"
        headers["host"] = host
        headers["x-amz-date"] = amz_date
        headers["x-amz-content-sha256"] = payload_hash

        signed_headers = ";".join(sorted(headers.keys()))
        canonical_headers = "\n".join(f"{k}:{v}" for k, v in sorted(headers.items())) + "\n"

        canonical_request = "\n".join([
            method,
            canonical_uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash,
        ])

        # Create string to sign
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = "\n".join([
            algorithm,
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ])

        # Calculate signature
        def sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        k_date = sign(("AWS4" + self.secret_access_key).encode("utf-8"), date_stamp)
        k_region = sign(k_date, region)
        k_service = sign(k_region, service)
        k_signing = sign(k_service, "aws4_request")
        signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # Build authorization header
        authorization = (
            f"{algorithm} "
            f"Credential={self.access_key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )

        return {
            "Authorization": authorization,
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
        }

    def upload_file(self, file_path: Path, slug: str, file_type: str) -> str:
        """Upload a file to R2 and return the public URL."""
        # Determine content type and extension
        content_types = {
            "audio": "audio/mpeg",
            "video": "video/mp4",
            "thumbnail": "image/png",
            "subtitles": "text/vtt",
        }
        extensions = {
            "audio": "mp3",
            "video": "mp4",
            "thumbnail": "png",
            "subtitles": "vtt",
        }

        content_type = content_types.get(file_type, "application/octet-stream")
        extension = extensions.get(file_type, "bin")
        object_key = f"dreamweavings/{slug}/{file_type}.{extension}"

        # Try boto3 first (handles multipart uploads for large files)
        s3_client = self._get_s3_client()
        if s3_client:
            return self._upload_with_boto3(s3_client, file_path, object_key, content_type)

        # Fallback to manual upload with requests
        return self._upload_with_requests(file_path, object_key, content_type)

    def _upload_with_boto3(self, s3_client, file_path: Path, object_key: str, content_type: str) -> str:
        """Upload using boto3 with automatic multipart for large files."""
        from boto3.s3.transfer import TransferConfig

        # Configure multipart: 8MB chunks, multipart for files > 25MB
        config = TransferConfig(
            multipart_threshold=25 * 1024 * 1024,  # 25MB
            multipart_chunksize=8 * 1024 * 1024,   # 8MB chunks
            max_concurrency=4,
            use_threads=True,
        )

        extra_args = {'ContentType': content_type}

        s3_client.upload_file(
            str(file_path),
            self.bucket_name,
            object_key,
            ExtraArgs=extra_args,
            Config=config,
        )

        return f"{self.public_url}/{object_key}"

    def _upload_with_requests(self, file_path: Path, object_key: str, content_type: str) -> str:
        """Fallback upload using requests (for small files or when boto3 unavailable)."""
        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Calculate payload hash
        payload_hash = hashlib.sha256(file_content).hexdigest()

        # Build request
        path = f"/{self.bucket_name}/{object_key}"
        url = f"{self.endpoint}{path}"

        headers = {
            "content-type": content_type,
            "content-length": str(len(file_content)),
        }

        # Sign the request
        auth_headers = self._sign_request("PUT", path, headers.copy(), payload_hash)
        headers.update(auth_headers)

        # Upload with retry logic
        import time
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                response = requests.put(
                    url,
                    data=file_content,
                    headers=headers,
                    timeout=600,
                )

                if response.status_code in [200, 201]:
                    return f"{self.public_url}/{object_key}"
                else:
                    last_error = f"R2 upload failed: {response.status_code} - {response.text}"

            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                last_error = f"Connection error: {e}"

            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))

        raise RuntimeError(last_error)

    def delete_file(self, url: str) -> bool:
        """Delete a file from R2."""
        # Extract object key from URL
        if not url.startswith(self.public_url):
            return False

        object_key = url[len(self.public_url) + 1:]
        path = f"/{self.bucket_name}/{object_key}"
        request_url = f"{self.endpoint}{path}"

        # Empty payload for DELETE
        payload_hash = hashlib.sha256(b"").hexdigest()

        headers = {}
        auth_headers = self._sign_request("DELETE", path, headers.copy(), payload_hash)
        headers.update(auth_headers)

        response = requests.delete(request_url, headers=headers, timeout=30)
        return response.status_code in [200, 204]


# =============================================================================
# VERCEL BLOB STORAGE BACKEND (Legacy)
# =============================================================================

class VercelBlobStorage:
    """Upload files to Vercel Blob (legacy, limited storage)."""

    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token
        self.blob_token = os.environ.get("BLOB_READ_WRITE_TOKEN")

    def is_configured(self) -> bool:
        """Check if Vercel Blob is configured."""
        return bool(self.blob_token or self.api_token)

    def get_missing_config(self) -> list:
        """Return list of missing environment variables."""
        missing = []
        if not self.blob_token and not self.api_token:
            missing.append("BLOB_READ_WRITE_TOKEN or SALARSU_API_TOKEN")
        return missing

    def upload_file(self, file_path: Path, slug: str, file_type: str) -> str:
        """Upload a file to Vercel Blob."""
        if self.blob_token:
            return self._upload_direct(file_path, slug, file_type)
        return self._upload_via_api(file_path, slug, file_type)

    def _upload_direct(self, file_path: Path, slug: str, file_type: str) -> str:
        """Upload directly to Vercel Blob."""
        content_types = {
            "audio": "audio/mpeg",
            "video": "video/mp4",
            "thumbnail": "image/png",
            "subtitles": "text/vtt",
        }
        extensions = {
            "audio": "mp3",
            "video": "mp4",
            "thumbnail": "png",
            "subtitles": "vtt",
        }

        content_type = content_types.get(file_type, "application/octet-stream")
        extension = extensions.get(file_type, "bin")
        blob_pathname = f"dreamweavings/{slug}/{file_type}.{extension}"

        upload_url = f"https://blob.vercel-storage.com/{blob_pathname}"
        file_size = file_path.stat().st_size

        with open(file_path, "rb") as f:
            response = requests.put(
                upload_url,
                data=f,
                headers={
                    "Authorization": f"Bearer {self.blob_token}",
                    "Content-Type": content_type,
                    "Content-Length": str(file_size),
                    "x-api-version": "7",
                    "x-content-type": content_type,
                },
                timeout=600,
            )

        if response.status_code not in [200, 201]:
            raise Exception(f"Blob upload failed: {response.status_code} - {response.text}")

        return response.json().get("url")

    def _upload_via_api(self, file_path: Path, slug: str, file_type: str) -> str:
        """Upload via API endpoint."""
        upload_url = f"{self.api_url}/api/dreamweavings/upload"

        with open(file_path, "rb") as f:
            file_data = f.read()

        response = requests.post(
            upload_url,
            files={"file": (file_path.name, file_data)},
            data={"slug": slug, "type": file_type},
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=300,
        )

        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")

        return response.json().get("url")

    def delete_file(self, url: str) -> bool:
        """Delete a file from Vercel Blob."""
        try:
            response = requests.delete(
                f"{self.api_url}/api/dreamweavings/upload",
                json={"url": url},
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=30,
            )
            return response.status_code == 200
        except Exception:
            return False


class DreamweavingUploader:
    """Upload dreamweaving sessions to Salarsu website."""

    def __init__(
        self,
        session_path: Path,
        api_url: str,
        dry_run: bool = False,
        no_git: bool = False,
        storage_backend: str = "r2",
    ):
        self.session_path = session_path
        self.api_url = api_url.rstrip("/")
        self.dry_run = dry_run
        self.no_git = no_git
        self.storage_backend = storage_backend
        self.api_token = os.environ.get("SALARSU_API_TOKEN") or os.environ.get("DREAMWEAVING_API_TOKEN")
        self.rollback = RollbackManager()

        # Initialize storage backend
        if storage_backend == "r2":
            self.storage = R2Storage()
        else:
            self.storage = VercelBlobStorage(self.api_url, self.api_token)

    def _format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS or H:MM:SS."""
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    def _get_duration(self, manifest: dict) -> int:
        """Extract duration from manifest (handles int or nested dict)."""
        duration = manifest.get("duration", 25)
        if isinstance(duration, int):
            return duration
        if isinstance(duration, dict):
            return duration.get("target_minutes", 25)
        return 25

    def load_session_data(self) -> dict:
        """Load all session metadata files."""
        data = {}

        # Load manifest.yaml
        manifest_path = self.session_path / "manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path) as f:
                data["manifest"] = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"manifest.yaml not found in {self.session_path}")

        # Load youtube_metadata.yaml
        youtube_path = self.session_path / "working_files" / "youtube_metadata.yaml"
        if youtube_path.exists():
            with open(youtube_path) as f:
                data["youtube_metadata"] = yaml.safe_load(f)

        # Load journey_concept.json
        concept_path = self.session_path / "working_files" / "journey_concept.json"
        if concept_path.exists():
            with open(concept_path) as f:
                data["journey_concept"] = json.load(f)

        # Load binaural_config.json
        binaural_path = self.session_path / "working_files" / "binaural_config.json"
        if binaural_path.exists():
            with open(binaural_path) as f:
                data["binaural_config"] = json.load(f)

        return data

    def detect_category(self, data: dict) -> dict:
        """
        Auto-detect category from session content using enhanced multi-signal analysis.

        Returns:
            dict with keys:
                - category: The selected category slug
                - confidence: Confidence score (0-1)
                - auto: Whether auto-categorized
                - alternatives: List of alternative categories
                - review_suggested: Whether manual review is recommended
        """
        manifest = data.get("manifest", {})
        session_info = manifest.get("session", {})
        theme_raw = manifest.get("theme", {})
        theme_info = theme_raw if isinstance(theme_raw, dict) else {}
        concept = data.get("journey_concept", {})
        youtube = data.get("youtube_metadata", {})
        binaural = data.get("binaural_config", {})

        # Build session data dict for analyzer
        session_data = {
            "title": session_info.get("title", "") or manifest.get("title", "") or session_info.get("name", ""),
            "description": session_info.get("description", "") or manifest.get("description", ""),
            "topic": session_info.get("topic", ""),
            "theme": theme_info.get("primary", "") if isinstance(theme_info, dict) else str(theme_raw),
            "tags": manifest.get("youtube", {}).get("tags", []) or youtube.get("tags", []),
            "archetypes": [],
            "binaural_frequency": None,
        }

        # Extract archetypes from multiple sources
        if manifest.get("archetypes"):
            archs = manifest["archetypes"]
            if isinstance(archs, list):
                session_data["archetypes"] = [
                    a.get("name", a) if isinstance(a, dict) else a
                    for a in archs
                ]
        elif theme_info.get("archetypes"):
            session_data["archetypes"] = theme_info["archetypes"]
        elif concept.get("archetypes"):
            archs = concept["archetypes"]
            if isinstance(archs, dict):
                session_data["archetypes"] = list(archs.keys())
            elif isinstance(archs, list):
                session_data["archetypes"] = archs

        # Extract binaural frequency if available
        if binaural:
            freq = binaural.get("beat_frequency") or binaural.get("target_frequency")
            if freq:
                session_data["binaural_frequency"] = freq

        # Use enhanced categorization if available
        if ENHANCED_CATEGORIZATION:
            result = categorize_session(session_data)
            return result

        # Fallback to simple keyword matching
        search_text = " ".join([
            str(session_data["title"]).lower(),
            str(session_data["description"]).lower(),
            str(session_data["topic"]).lower(),
            str(session_data["theme"]).lower(),
            " ".join(str(t).lower() for t in session_data.get("tags", [])),
        ])

        for keyword, category in CATEGORY_MAPPING.items():
            if keyword in search_text:
                return {
                    "category": category,
                    "confidence": 0.5,
                    "auto": True,
                    "alternatives": [],
                    "review_suggested": True,
                    "message": f"Simple keyword match: {keyword}",
                }

        return {
            "category": "guided-visualization",  # Safe default
            "confidence": 0.0,
            "auto": False,
            "alternatives": [],
            "review_suggested": True,
            "needs_review": True,
            "message": "No keywords matched. Using default category.",
        }

    def get_media_files(self) -> dict:
        """Locate all required media files."""
        output_dir = self.session_path / "output"
        youtube_dir = output_dir / "youtube_package"

        files = {}

        # Find master audio - try multiple patterns in priority order
        audio_patterns = [
            "*_MASTER.mp3",           # Standard naming (e.g., forest-of-lost-instincts_MASTER.mp3)
            "final_master.mp3",       # Alternative naming
            "*_final.mp3",            # Session-specific final (e.g., atlas_starship_final.mp3)
            "*-final.mp3",            # Hyphenated final (e.g., iron-soul-forge-final.mp3)
            "*-atlas-enhanced-final.mp3",  # Enhanced versions
            "*-session-final.mp3",    # Session final
        ]
        for pattern in audio_patterns:
            matches = list(output_dir.glob(pattern))
            if matches:
                # If multiple matches, prefer the largest file (likely the final version)
                files["audio"] = max(matches, key=lambda p: p.stat().st_size)
                break

        # Find video - try multiple patterns and locations
        video_found = False

        # Check youtube_package first
        youtube_video = youtube_dir / "final_video.mp4"
        if youtube_video.exists():
            files["video"] = youtube_video
            video_found = True

        # Check for symlink in youtube_package (e.g., atlas_starship_final.mp4 -> ../atlas_starship_final.mp4)
        if not video_found:
            for video_file in youtube_dir.glob("*.mp4"):
                files["video"] = video_file.resolve()  # Resolve symlinks
                video_found = True
                break

        # Check output/video directory
        if not video_found:
            video_dir = output_dir / "video"
            for video_file in video_dir.glob("*.mp4"):
                if "solid_background" not in video_file.name:  # Skip background files
                    files["video"] = video_file
                    video_found = True
                    break

        # Check output directory directly
        if not video_found:
            for video_file in output_dir.glob("*.mp4"):
                if "solid_background" not in video_file.name:
                    files["video"] = video_file
                    break

        # Find thumbnail
        thumb_path = youtube_dir / "thumbnail.png"
        if not thumb_path.exists():
            thumb_path = output_dir / "youtube_thumbnail.png"
        if thumb_path.exists():
            files["thumbnail"] = thumb_path

        # Find subtitles
        vtt_path = youtube_dir / "subtitles.vtt"
        if vtt_path.exists():
            files["subtitles"] = vtt_path

        return files

    def validate_session(self, data: dict, files: dict) -> list:
        """Validate session is ready for upload."""
        errors = []

        if not data.get("manifest"):
            errors.append("Missing manifest.yaml")

        if "audio" not in files:
            errors.append("Missing master audio file (*_MASTER.mp3)")

        # Check file sizes (only enforce limits for Vercel Blob)
        if self.storage_backend == "vercel":
            if files.get("audio"):
                size_mb = files["audio"].stat().st_size / (1024 * 1024)
                if size_mb > 100:
                    errors.append(f"Audio file too large: {size_mb:.1f}MB (max 100MB for Vercel)")

            if files.get("video"):
                size_mb = files["video"].stat().st_size / (1024 * 1024)
                if size_mb > 500:
                    errors.append(f"Video file too large: {size_mb:.1f}MB (max 500MB for Vercel)")

        # Check storage backend configuration
        if not self.dry_run and not self.storage.is_configured():
            missing = self.storage.get_missing_config()
            errors.append(f"Storage not configured. Missing: {', '.join(missing)}")

        # Check API token (for database operations)
        if not self.api_token and not self.dry_run:
            errors.append("Missing API token (set SALARSU_API_TOKEN or DREAMWEAVING_API_TOKEN)")

        return errors

    def build_payload(self, data: dict, category_slug: str) -> dict:
        """Build API payload from session data."""
        manifest = data.get("manifest", {})
        session_info = manifest.get("session", {})
        # theme can be a dict or a string - handle both
        theme_raw = manifest.get("theme", {})
        theme_info = theme_raw if isinstance(theme_raw, dict) else {}
        youtube_meta = data.get("youtube_metadata", {})
        journey = data.get("journey_concept", {})
        binaural = data.get("binaural_config", {})

        # Extract slug from session name (try multiple locations)
        slug = (
            session_info.get("name")
            or manifest.get("name")
            or self.session_path.name
        )

        # Get topic (needed for description generation even if not used for title)
        topic = session_info.get("topic", "")

        # Get title - check multiple sources in order of preference
        # 1. session.title (explicit title field)
        # 2. youtube.title (if short enough, <150 chars)
        # 3. Extract from topic string
        # 4. Convert from slug
        title_text = session_info.get("title", "")
        youtube_info = manifest.get("youtube", {})
        youtube_title = youtube_info.get("title", "")

        if not title_text and youtube_title and len(youtube_title) < 150:
            # Use youtube title if it's reasonable length (strip trailing metadata)
            title_text = youtube_title.split(" | ")[0].strip()

        if not title_text:
            # Fall back to extracting from topic
            title_text = extract_display_title(topic, slug)

        # Build archetypes array from multiple possible structures
        archetypes = []
        # Try manifest.archetypes (list of dicts with name, role, description)
        if manifest.get("archetypes") and isinstance(manifest["archetypes"], list):
            archetypes = manifest["archetypes"]
        # Try theme_info.archetypes (list of strings)
        elif theme_info.get("archetypes"):
            archetypes = [{"name": a} for a in theme_info["archetypes"]]
        # Try journey_concept.archetypes (dict)
        elif journey.get("archetypes") and isinstance(journey["archetypes"], dict):
            archetypes = [
                {
                    "name": k.replace("_", " ").title(),
                    "essence": v.get("essence", ""),
                    "animal_form": v.get("animal_form", ""),
                    "gift": v.get("gift", ""),
                    "teaching": v.get("teaching", ""),
                }
                for k, v in journey.get("archetypes", {}).items()
            ]

        # Build chapters from multiple sources
        chapters = youtube_meta.get("chapters", [])
        # Try manifest.sections for iron-soul-forge style
        if not chapters and manifest.get("sections"):
            chapters = [
                {"time": self._format_time(s.get("start", 0)), "title": s.get("description", s.get("name", ""))}
                for s in manifest["sections"]
            ]

        # Extract tags from multiple sources
        tags = []
        if youtube_meta.get("tags"):
            tag_data = youtube_meta["tags"]
            if isinstance(tag_data, dict):
                tags = tag_data.get("primary", []) + tag_data.get("secondary", [])
            elif isinstance(tag_data, list):
                tags = tag_data
        elif manifest.get("youtube", {}).get("tags"):
            tags = manifest["youtube"]["tags"]

        # Get description from multiple sources
        description = youtube_meta.get("description", "")
        if not description:
            description = session_info.get("description", "")
        if not description:
            description = manifest.get("description", "")

        # === SEO ENHANCEMENT: Dreamweaver Traffic System Integration ===
        # Implements Phase 1 (Zero-Competition Keywords), Phase 2 (SEO Page Template),
        # and Phase 3 (Product Schema) from the Notion knowledge base
        seo_metadata = self._generate_seo_metadata(
            topic=topic,
            title=title_text,
            category=category_slug,
            slug=slug,
            archetypes=[a.get("name", "") for a in archetypes if isinstance(a, dict)],
            description=description
        )

        payload = {
            "slug": slug,
            "title": title_text,
            "subtitle": session_info.get("subtitle", ""),
            "description": description,
            "duration_minutes": self._get_duration(manifest),
            "category": category_slug,
            "theme": {
                "primary": theme_info.get("primary", ""),
                "secondary": theme_info.get("secondary", ""),
                "environment": theme_info.get("environment", ""),
                "emotional_arc": theme_info.get("emotional_arc", []),
            },
            "archetypes": archetypes,
            "journey_concept": journey.get("journey_concept", {}),
            "binaural_config": binaural,
            "youtube_metadata": {
                "title": youtube_meta.get("title", {}),
                "tags": youtube_meta.get("tags", {}),
                "category": youtube_meta.get("category", "Education"),
            },
            "tags": ",".join(tags[:20]),  # Limit to 20 tags
            "chapters": chapters,
            "status": "published",
            # SEO Enhancement Fields (Dreamweaver Traffic System)
            "seo": {
                "primary_keyword": seo_metadata.get("primary_keyword", ""),
                "meta_title": seo_metadata.get("meta_title", ""),
                "meta_description": seo_metadata.get("meta_description", ""),
                "h1_title": seo_metadata.get("h1_title", ""),
                "long_description": seo_metadata.get("long_description", ""),
                "image_alt_text": seo_metadata.get("alt_text", ""),
                "sku": seo_metadata.get("sku", ""),
            },
            "product_schema": seo_metadata.get("product_schema", {}),
            "related_sessions": seo_metadata.get("related_sessions", []),
        }

        return payload

    def _generate_seo_metadata(
        self,
        topic: str,
        title: str,
        category: str,
        slug: str,
        archetypes: list,
        description: str
    ) -> dict:
        """
        Generate SEO metadata following Dreamweaver Traffic System.

        Implements:
        - Phase 1: Zero-Competition Keyword Domination
        - Phase 2: SEO Product Page Template
        - Phase 3: Product Schema for Rich Snippets

        First tries to use RAG from knowledge base, falls back to local generation.
        """
        # Try RAG-enhanced SEO generation
        try:
            # Try multiple import paths for flexibility
            try:
                from scripts.ai.knowledge_tools import get_website_seo_context
            except ImportError:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from scripts.ai.knowledge_tools import get_website_seo_context

            # Build page URL for schema
            page_url = f"{self.api_url}/dreamweavings/{slug}"

            seo_context = get_website_seo_context(
                topic=topic,
                title=title,
                category=category,
                slug=slug,
                archetypes=archetypes,
                description=description,
                thumbnail_url="",  # Will be filled after upload
                page_url=page_url
            )

            if seo_context.get("primary_keyword"):
                print("  Generated SEO metadata from knowledge base (RAG)")
                return seo_context

        except ImportError:
            print("  Warning: knowledge_tools not available, using fallback SEO")
        except Exception as e:
            print(f"  Warning: RAG SEO generation failed: {e}, using fallback")

        # Fallback: Generate basic SEO metadata without RAG
        return self._generate_basic_seo_metadata(
            title=title,
            description=description,
            category=category,
            slug=slug,
            archetypes=archetypes
        )

    def _generate_basic_seo_metadata(
        self,
        title: str,
        description: str,
        category: str,
        slug: str,
        archetypes: list
    ) -> dict:
        """
        Generate basic SEO metadata without RAG (fallback).
        Follows Phase 1-3 patterns from the Dreamweaver Traffic System.
        """
        import hashlib

        # === PHASE 1: Zero-Competition Keyword ===
        primary_keyword = f"{title} - Dreamweaver Guided Meditation"

        # Generate SKU: DW-{CATEGORY}-{THEME}-{NUMBER}
        category_codes = {
            "starlight": "STL", "celestial": "STL",
            "atlantean": "ATL", "atlantis": "ATL",
            "eden": "EDN", "garden": "EDN",
            "shadow": "SHD", "shadow-work": "SHD",
            "archetypal": "ARC", "archetype": "ARC",
            "cosmic": "COS", "cosmic-space": "COS", "space": "COS",
            "healing": "HEL",
            "navigator": "NAV",
            "nature": "NAT", "forest": "NAT",
            "spiritual": "SPI", "sacred": "SPI",
            "confidence": "CNF",
            "relaxation": "RLX",
        }
        cat_code = category_codes.get(category.lower().replace("-", "_"), "GEN")

        # Theme code from slug
        slug_parts = slug.replace("-", " ").split()
        theme_code = ""
        for part in slug_parts[:2]:
            if len(part) >= 3 and part.lower() not in ["the", "and", "for", "with"]:
                theme_code += part[:3].upper()
        if not theme_code:
            theme_code = slug[:4].upper()

        hash_num = int(hashlib.md5(slug.encode()).hexdigest()[:4], 16) % 100
        sku = f"DW-{cat_code}-{theme_code}-{hash_num:02d}"

        # === PHASE 2: SEO Page Template ===
        # Meta title (≤60 chars) - use optimized SEO title generator
        # This extracts the core concept and strips redundant phrases
        meta_title = generate_seo_title(
            full_title=title,
            topic=description,
            category=category,
            archetypes=archetypes
        )

        # Meta description (≤160 chars)
        if description:
            meta_description = description[:157] + "..." if len(description) > 160 else description
        else:
            meta_description = f"Experience the transformative {title} - a guided Dreamweaver meditation with binaural beats and archetypal journeywork."

        # Image ALT text
        archetype_str = f" featuring {', '.join(archetypes[:2])}" if archetypes else ""
        alt_text = f"{title}{archetype_str} - Dreamweaver Hypnotic Journey Artwork"

        # Long description (300-700 words) with safety disclaimer
        # Use the new generate_benefit_laden_description function for clean, benefit-focused content
        try:
            from scripts.ai.knowledge_tools import generate_benefit_laden_description, inject_semantic_field

            # Generate benefit-laden description with safety disclaimer included
            long_description = generate_benefit_laden_description(
                title=title,
                archetypes=archetypes,
                outcome="transformation",  # Default outcome for fallback
                duration_minutes=None,  # Unknown in fallback
                include_disclaimer=True  # Include full safety disclaimer
            )

            # Apply Layer 2 semantic field saturation
            session_elements = {
                "archetypes": archetypes,
                "outcome": "transformation",
            }
            long_description = inject_semantic_field(
                long_description,
                session_elements=session_elements,
                num_glossary_terms=4,
                include_definition=True,
                include_glossary=True
            )
            print("  Applied benefit-laden description with safety disclaimer and semantic field")

        except ImportError:
            # Fallback if knowledge_tools not available
            long_desc_parts = [
                f"**{title}** is a transformative guided meditation experience designed to take you on a profound inner journey.",
                "",
                "## About This Journey",
                description if description else "This Dreamweaver session combines professional voice guidance, binaural beats, and symbolic imagery to create a deeply immersive experience.",
                "",
                "## What's Included",
                "- High-quality audio with binaural beats tuned for deep theta state",
                "- Professional voice guidance by Randy Salars",
                "- Carefully crafted narrative with archetypal imagery",
                "- Safe return protocol for gentle re-awakening",
            ]
            if archetypes:
                long_desc_parts.extend([
                    "",
                    "## Archetypal Guides",
                    f"This journey features the following archetypal energies: {', '.join(archetypes)}.",
                ])
            long_desc_parts.extend([
                "",
                "## Perfect For",
                "- Meditation practitioners seeking deeper experiences",
                "- Spiritual seekers exploring inner landscapes",
                "- Anyone wanting deep relaxation and stress relief",
                "- Those interested in Jungian archetypes and symbolic work",
                "",
                "## ⚠️ Important Safety Information",
                "",
                "**Please read before listening:**",
                "",
                "- **Do NOT listen while driving** or operating heavy machinery",
                "- This is **not medical, financial, or professional advice**",
                "- Consult a qualified healthcare provider for medical concerns",
                "- Listen only in a **safe, comfortable environment** where you can fully relax",
                "- If you experience any discomfort or distress, discontinue use immediately",
                "",
                "*By listening, you agree that this content is for entertainment and personal development purposes only.*"
            ])
            long_description = "\n".join(long_desc_parts)
        except Exception as e:
            print(f"  Warning: Benefit-laden description generation failed: {e}, using basic fallback")
            long_description = f"**{title}** is a transformative Dreamweaver meditation experience.\n\n⚠️ SAFETY: Do not listen while driving. Not medical advice. Use in a safe environment."

        # === PHASE 3: Product Schema ===
        category_display = category.replace("-", " ").title() if category else "Guided Meditation"
        page_url = f"{self.api_url}/dreamweavings/{slug}"

        product_schema = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": primary_keyword,
            "description": meta_description,
            "sku": sku,
            "brand": {
                "@type": "Brand",
                "name": "Salars Dreamweaver"
            },
            "author": {
                "@type": "Person",
                "name": "Randy Salars"
            },
            "category": f"Digital Download > Guided Meditation > {category_display}",
            "offers": {
                "@type": "Offer",
                "url": page_url,
                "price": "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2026-12-31"
            }
        }

        return {
            "primary_keyword": primary_keyword,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "h1_title": title,
            "long_description": "\n".join(long_desc_parts),
            "product_schema": product_schema,
            "related_sessions": [],
            "alt_text": alt_text,
            "sku": sku,
        }

    def _save_seo_artifacts(self, payload: dict) -> None:
        """
        Save SEO artifacts to session output directory.

        Saves:
        - product_schema.json: JSON-LD schema for rich snippets
        - seo_metadata.json: Full SEO metadata for reference
        """
        import json

        output_dir = self.session_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save product schema
        product_schema = payload.get("product_schema", {})
        if product_schema:
            schema_path = output_dir / "product_schema.json"
            with open(schema_path, "w") as f:
                json.dump(product_schema, f, indent=2)
            print(f"  Saved: {schema_path.name}")

        # Save full SEO metadata
        seo_data = payload.get("seo", {})
        if seo_data:
            seo_path = output_dir / "seo_metadata.json"
            full_seo = {
                **seo_data,
                "product_schema": product_schema,
                "related_sessions": payload.get("related_sessions", []),
            }
            with open(seo_path, "w") as f:
                json.dump(full_seo, f, indent=2)
            print(f"  Saved: {seo_path.name}")

        # Log summary
        sku = seo_data.get("sku", "N/A")
        keyword = seo_data.get("primary_keyword", "N/A")
        print(f"  SKU: {sku}")
        print(f"  Primary Keyword: {keyword[:50]}..." if len(keyword) > 50 else f"  Primary Keyword: {keyword}")

    def upload_file(self, file_path: Path, slug: str, file_type: str) -> str:
        """Upload a single file using the configured storage backend."""
        if self.dry_run:
            return f"https://example.com/dry-run/{slug}/{file_type}"

        return self.storage.upload_file(file_path, slug, file_type)

    def upload_files(self, files: dict, slug: str) -> dict:
        """Upload all media files using the configured storage backend."""
        if self.dry_run:
            print("  [DRY RUN] Would upload files:")
            for name, path in files.items():
                print(f"    - {name}: {path.name} ({path.stat().st_size / (1024*1024):.1f}MB)")
            return {
                "audio_url": "https://example.com/dry-run/audio.mp3",
                "video_url": "https://example.com/dry-run/video.mp4",
                "thumbnail_url": "https://example.com/dry-run/thumbnail.png",
                "subtitles_url": "https://example.com/dry-run/subtitles.vtt",
            }

        urls = {}

        for file_type, file_path in files.items():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"  Uploading {file_type}: {file_path.name} ({size_mb:.1f}MB)...")

            url = self.upload_file(file_path, slug, file_type)
            url_key = f"{file_type}_url"
            urls[url_key] = url
            self.rollback.add_upload(url)

            print(f"    Done: {url[:60]}...")

        return urls

    def create_dreamweaving(self, payload: dict) -> dict:
        """Create dreamweaving record via API."""
        if self.dry_run:
            print("  [DRY RUN] Would create dreamweaving:")
            print(f"    Slug: {payload['slug']}")
            print(f"    Title: {payload['title'][:60]}...")
            print(f"    Category: {payload['category']}")
            return {"id": 0, "slug": payload["slug"]}

        api_url = f"{self.api_url}/api/dreamweavings"

        response = requests.post(
            api_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}",
            },
            timeout=30,
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"API error: {response.status_code} - {response.text}")

        result = response.json()
        self.rollback.set_db_record(payload["slug"])
        return result

    def delete_dreamweaving(self, slug: str) -> bool:
        """Delete existing dreamweaving record via API."""
        if self.dry_run:
            print(f"  [DRY RUN] Would delete dreamweaving: {slug}")
            return True

        api_url = f"{self.api_url}/api/dreamweavings/{slug}"

        response = requests.delete(
            api_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
            },
            timeout=30,
        )

        if response.status_code == 404:
            print(f"  Record not found (already deleted): {slug}")
            return True

        if response.status_code not in [200, 204]:
            raise Exception(f"Delete API error: {response.status_code} - {response.text}")

        return True

    def update_dreamweaving(self, payload: dict) -> dict:
        """Update existing dreamweaving record via DELETE + POST (workaround for missing PUT support)."""
        if self.dry_run:
            print("  [DRY RUN] Would update dreamweaving:")
            print(f"    Slug: {payload['slug']}")
            print(f"    Title: {payload['title'][:60]}...")
            return {"id": 0, "slug": payload["slug"]}

        slug = payload['slug']

        # Step 1: Delete existing record
        print(f"  Deleting existing record: {slug}")
        self.delete_dreamweaving(slug)

        # Step 2: Create new record with same slug
        print(f"  Creating updated record: {slug}")
        return self.create_dreamweaving(payload)

    def run(self, category_override: str = None, update_mode: bool = False) -> dict:
        """Execute the complete upload workflow."""
        print("=" * 70)
        print("DREAMWEAVING WEBSITE UPLOAD")
        print("=" * 70)
        print(f"Session:  {self.session_path}")
        print(f"API URL:  {self.api_url}")
        print(f"Storage:  {self.storage_backend.upper()}")
        print(f"Dry Run:  {self.dry_run}")
        print(f"No Git:   {self.no_git}")
        print(f"Update:   {update_mode}")
        print()

        try:
            # Step 1: Load session data
            print("=== Loading Session Data ===")
            data = self.load_session_data()
            print(f"  Loaded: manifest.yaml")
            if data.get("youtube_metadata"):
                print(f"  Loaded: youtube_metadata.yaml")
            if data.get("journey_concept"):
                print(f"  Loaded: journey_concept.json")
            if data.get("binaural_config"):
                print(f"  Loaded: binaural_config.json")

            # Step 2: Get media files
            print("\n=== Locating Media Files ===")
            files = self.get_media_files()
            for name, path in files.items():
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"  {name}: {path.name} ({size_mb:.1f}MB)")

            if not files:
                raise Exception("No media files found")

            # Step 3: Validate
            print("\n=== Validating Session ===")
            errors = self.validate_session(data, files)
            if errors:
                print("  ERRORS:")
                for e in errors:
                    print(f"    - {e}")
                raise ValueError("Session validation failed")
            print("  Validation passed")

            # Step 4: Detect category
            print(f"\n=== Category Detection ===")
            if category_override:
                category_slug = category_override
                print(f"  Override: {category_slug}")
            else:
                cat_result = self.detect_category(data)
                raw_category = cat_result["category"]
                confidence = cat_result.get("confidence", 0)
                print(f"  Detected: {raw_category}")
                print(f"  Confidence: {confidence:.0%}")
                if cat_result.get("alternatives"):
                    print(f"  Alternatives: {', '.join(cat_result['alternatives'][:3])}")
                if cat_result.get("review_suggested"):
                    print("  Note: Manual review suggested")
                if cat_result.get("message"):
                    print(f"  {cat_result['message']}")

                # Map the detected category to database category
                category_slug = get_db_category(raw_category)
                if category_slug != raw_category:
                    print(f"  Mapped to DB: {category_slug}")

            # Step 5: Build payload
            print("\n=== Building API Payload ===")
            payload = self.build_payload(data, category_slug)
            print(f"  Slug: {payload['slug']}")
            print(f"  Title: {payload['title'][:60]}...")
            print(f"  Duration: {payload['duration_minutes']} min")
            print(f"  Archetypes: {len(payload['archetypes'])}")
            print(f"  Chapters: {len(payload['chapters'])}")

            # Step 6: Upload media files
            print("\n=== Uploading Media Files ===")
            urls = self.upload_files(files, payload["slug"])
            payload.update(urls)

            # Step 7: Create or update database record
            if update_mode:
                print("\n=== Updating Database Record ===")
                result = self.update_dreamweaving(payload)
                print(f"  Updated ID: {result.get('id')}")
            else:
                print("\n=== Creating Database Record ===")
                result = self.create_dreamweaving(payload)
                print(f"  Created ID: {result.get('id')}")

            # Step 8: Save product schema to session
            print("\n=== Saving SEO Artifacts ===")
            self._save_seo_artifacts(payload)

            # Success!
            print("\n" + "=" * 70)
            print("UPLOAD COMPLETE")
            print("=" * 70)
            print(f"View at: {self.api_url}/dreamweavings/{payload['slug']}")

            return result

        except Exception as e:
            print(f"\n!!! ERROR: {e}")

            if not self.dry_run and (self.rollback.uploaded_urls or self.rollback.db_record_slug):
                self.rollback.rollback(self.api_url, self.api_token)

            raise


def main():
    parser = argparse.ArgumentParser(
        description="Upload dreamweaving to website",
        epilog="""
Storage Backends:
  r2      Cloudflare R2 (recommended - free egress, unlimited storage)
  vercel  Vercel Blob (legacy - 1GB limit on hobby plan)

Environment Variables for R2:
  R2_ACCOUNT_ID         Cloudflare account ID
  R2_ACCESS_KEY_ID      R2 API token access key
  R2_SECRET_ACCESS_KEY  R2 API token secret
  R2_BUCKET_NAME        Bucket name (default: dreamweavings)
  R2_PUBLIC_URL         Public URL (e.g., https://media.salars.net)

Environment Variables for Vercel Blob:
  BLOB_READ_WRITE_TOKEN  Vercel Blob token
  SALARSU_API_TOKEN      API authentication
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--session", help="Path to session directory")
    parser.add_argument("--list-categories", action="store_true", help="List available categories and exit")
    parser.add_argument("--dry-run", action="store_true", help="Validate without uploading")
    parser.add_argument("--no-git", action="store_true", help="Skip git operations")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL")
    parser.add_argument("--category", help="Override auto-detected category")
    parser.add_argument("--update", action="store_true", help="Update existing record (PUT instead of POST)")
    parser.add_argument(
        "--storage",
        choices=["r2", "vercel"],
        default="r2",
        help="Storage backend (default: r2)",
    )

    args = parser.parse_args()

    # Handle --list-categories
    if args.list_categories:
        print("=" * 60)
        print("AVAILABLE CATEGORIES")
        print("=" * 60)
        if ENHANCED_CATEGORIZATION:
            categories = get_available_categories()
            # Group by priority ranges
            core = [c for c in categories if c["priority"] < 100]
            extended = [c for c in categories if 100 <= c["priority"] < 200]
            theme = [c for c in categories if 200 <= c["priority"] < 400]
            growth = [c for c in categories if c["priority"] >= 400]

            if core:
                print("\nCore Categories (from /types):")
                for cat in core:
                    print(f"  {cat['slug']:<35} {cat['name']}")
            if extended:
                print("\nExtended Categories (from /more):")
                for cat in extended:
                    print(f"  {cat['slug']:<35} {cat['name']}")
            if theme:
                print("\nTheme Categories:")
                for cat in theme:
                    print(f"  {cat['slug']:<35} {cat['name']}")
            if growth:
                print("\nGrowth Experience Categories:")
                for cat in growth:
                    print(f"  {cat['slug']:<35} {cat['name']}")
        else:
            print("\nSimple category mapping (enhanced categorization not available):")
            seen = set()
            for _, category in sorted(CATEGORY_MAPPING.items(), key=lambda x: x[1]):
                if category not in seen:
                    print(f"  {category}")
                    seen.add(category)
        sys.exit(0)

    # Require session for upload
    if not args.session:
        parser.error("--session is required (unless using --list-categories)")

    session_path = Path(args.session).resolve()
    if not session_path.exists():
        print(f"Error: Session path not found: {session_path}")
        sys.exit(1)

    uploader = DreamweavingUploader(
        session_path=session_path,
        api_url=args.api_url,
        dry_run=args.dry_run,
        no_git=args.no_git,
        storage_backend=args.storage,
    )

    try:
        result = uploader.run(category_override=args.category, update_mode=args.update)
        sys.exit(0)
    except Exception as e:
        print(f"\nFATAL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
