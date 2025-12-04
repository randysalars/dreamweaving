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
CATEGORY_MAPPING = {
    # Nature & Forest
    "forest": "nature-forest",
    "nature": "nature-forest",
    "garden": "nature-forest",
    "eden": "nature-forest",
    "tree": "nature-forest",
    "meadow": "nature-forest",
    "river": "nature-forest",
    "mountain": "nature-forest",
    # Cosmic & Space
    "cosmic": "cosmic-space",
    "space": "cosmic-space",
    "star": "cosmic-space",
    "astral": "cosmic-space",
    "galaxy": "cosmic-space",
    "universe": "cosmic-space",
    "celestial": "cosmic-space",
    # Healing & Restoration
    "healing": "healing",
    "restore": "healing",
    "repair": "healing",
    "recover": "healing",
    "therapy": "healing",
    "wellness": "healing",
    # Shadow Work
    "shadow": "shadow-work",
    "dark": "shadow-work",
    "unconscious": "shadow-work",
    "integration": "shadow-work",
    # Archetypal Journey
    "archetype": "archetypal",
    "journey": "archetypal",
    "guide": "archetypal",
    "animal": "archetypal",
    "totem": "archetypal",
    "spirit": "archetypal",
    # Sacred & Spiritual
    "sacred": "sacred-spiritual",
    "divine": "sacred-spiritual",
    "spiritual": "sacred-spiritual",
    "holy": "sacred-spiritual",
    "temple": "sacred-spiritual",
    "altar": "sacred-spiritual",
    # Confidence & Empowerment
    "confidence": "confidence",
    "power": "confidence",
    "strength": "confidence",
    "courage": "confidence",
    "empowerment": "confidence",
    # Deep Relaxation
    "relax": "relaxation",
    "sleep": "relaxation",
    "calm": "relaxation",
    "peaceful": "relaxation",
    "rest": "relaxation",
    "tranquil": "relaxation",
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
    """Upload files to Cloudflare R2 using S3-compatible API."""

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

        # Upload
        response = requests.put(
            url,
            data=file_content,
            headers=headers,
            timeout=600,  # 10 min for large files
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"R2 upload failed: {response.status_code} - {response.text}")

        # Return public URL
        return f"{self.public_url}/{object_key}"

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

    def detect_category(self, data: dict) -> str:
        """Auto-detect category from session content."""
        # Build searchable text from various sources
        search_text = ""

        manifest = data.get("manifest", {})
        session_info = manifest.get("session", {})
        # theme can be a string or dict - handle both
        theme_raw = manifest.get("theme", {})
        theme_info = theme_raw if isinstance(theme_raw, dict) else {}
        # If theme is a string, add it to search text directly
        if isinstance(theme_raw, str):
            search_text += theme_raw.lower() + " "

        search_text += session_info.get("name", "").lower() + " "
        search_text += session_info.get("title", "").lower() + " "
        # Also add manifest-level title for iron-soul-forge style
        search_text += manifest.get("title", "").lower() + " "
        search_text += str(theme_info.get("primary", "")).lower() + " "
        search_text += str(theme_info.get("environment", "")).lower() + " "

        concept = data.get("journey_concept", {})
        search_text += str(concept.get("theme", "")).lower() + " "

        youtube = data.get("youtube_metadata", {})
        title = youtube.get("title", {})
        if isinstance(title, dict):
            search_text += str(title.get("primary", "")).lower() + " "
        else:
            search_text += str(title).lower() + " "

        # Find best matching category
        for keyword, category in CATEGORY_MAPPING.items():
            if keyword in search_text:
                return category

        return "archetypal"  # Default fallback

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

        # Get title from multiple possible locations
        title_text = None
        # Try youtube metadata first
        yt_title = youtube_meta.get("title", {})
        if isinstance(yt_title, dict):
            title_text = yt_title.get("primary")
        elif yt_title:
            title_text = str(yt_title)
        # Try session info
        if not title_text:
            title_text = session_info.get("title")
        # Try manifest root (iron-soul-forge style)
        if not title_text:
            title_text = manifest.get("title")
        # Try youtube optimized_title
        if not title_text:
            title_text = manifest.get("youtube", {}).get("optimized_title")
        # Fallback to slug
        if not title_text:
            title_text = slug

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
        }

        return payload

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

    def run(self, category_override: str = None) -> dict:
        """Execute the complete upload workflow."""
        print("=" * 70)
        print("DREAMWEAVING WEBSITE UPLOAD")
        print("=" * 70)
        print(f"Session:  {self.session_path}")
        print(f"API URL:  {self.api_url}")
        print(f"Storage:  {self.storage_backend.upper()}")
        print(f"Dry Run:  {self.dry_run}")
        print(f"No Git:   {self.no_git}")
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
            category = category_override or self.detect_category(data)
            print(f"\n=== Category Detection ===")
            print(f"  Detected: {category}")

            # Step 5: Build payload
            print("\n=== Building API Payload ===")
            payload = self.build_payload(data, category)
            print(f"  Slug: {payload['slug']}")
            print(f"  Title: {payload['title'][:60]}...")
            print(f"  Duration: {payload['duration_minutes']} min")
            print(f"  Archetypes: {len(payload['archetypes'])}")
            print(f"  Chapters: {len(payload['chapters'])}")

            # Step 6: Upload media files
            print("\n=== Uploading Media Files ===")
            urls = self.upload_files(files, payload["slug"])
            payload.update(urls)

            # Step 7: Create database record
            print("\n=== Creating Database Record ===")
            result = self.create_dreamweaving(payload)
            print(f"  Created ID: {result.get('id')}")

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
    parser.add_argument("--session", required=True, help="Path to session directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate without uploading")
    parser.add_argument("--no-git", action="store_true", help="Skip git operations")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL")
    parser.add_argument("--category", help="Override auto-detected category")
    parser.add_argument(
        "--storage",
        choices=["r2", "vercel"],
        default="r2",
        help="Storage backend (default: r2)",
    )

    args = parser.parse_args()

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
        result = uploader.run(category_override=args.category)
        sys.exit(0)
    except Exception as e:
        print(f"\nFATAL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
