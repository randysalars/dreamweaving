#!/usr/bin/env python3
"""
Custom exception hierarchy for Dreamweaving.

Provides structured exception types for different failure categories,
enabling more specific error handling throughout the codebase.

Usage:
    from scripts.utilities.exceptions import (
        DreamweavingError,
        APIError,
        ValidationError,
        ConfigurationError,
        AudioProcessingError,
        SessionError,
    )

    try:
        # ... operation
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
    except APIError as e:
        logger.error(f"API call failed: {e}")
"""

from __future__ import annotations


class DreamweavingError(Exception):
    """Base exception for all Dreamweaving errors.

    All custom exceptions in this project should inherit from this class.
    """

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIError(DreamweavingError):
    """External API communication error.

    Raised when calls to external services fail:
    - Google Cloud TTS
    - Notion API
    - YouTube API
    - Vercel/deployment APIs
    """

    def __init__(
        self,
        message: str,
        service: str | None = None,
        status_code: int | None = None,
        details: dict | None = None,
    ):
        super().__init__(message, details)
        self.service = service
        self.status_code = status_code


class ValidationError(DreamweavingError):
    """Input validation error.

    Raised when input data fails validation:
    - Invalid SSML syntax
    - Malformed manifest
    - Missing required fields
    - Out-of-range values
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: object = None,
        details: dict | None = None,
    ):
        super().__init__(message, details)
        self.field = field
        self.value = value


class ConfigurationError(DreamweavingError):
    """Configuration or environment error.

    Raised when configuration is missing or invalid:
    - Missing environment variables
    - Invalid config file
    - Missing credentials
    - Incompatible settings
    """

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(message, details)
        self.config_key = config_key


class AudioProcessingError(DreamweavingError):
    """Audio processing pipeline error.

    Raised when audio operations fail:
    - TTS generation failure
    - FFmpeg processing error
    - Invalid audio format
    - Mixing/mastering issues
    """

    def __init__(
        self,
        message: str,
        stage: str | None = None,
        file_path: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(message, details)
        self.stage = stage
        self.file_path = file_path


class SessionError(DreamweavingError):
    """Session-related error.

    Raised when session operations fail:
    - Session not found
    - Invalid session structure
    - Missing session files
    - Session state issues
    """

    def __init__(
        self,
        message: str,
        session_name: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(message, details)
        self.session_name = session_name


class VideoProcessingError(DreamweavingError):
    """Video processing pipeline error.

    Raised when video operations fail:
    - FFmpeg video encoding error
    - Image processing failure
    - Assembly issues
    """

    def __init__(
        self,
        message: str,
        stage: str | None = None,
        file_path: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(message, details)
        self.stage = stage
        self.file_path = file_path


# Convenience aliases for common import patterns
__all__ = [
    "DreamweavingError",
    "APIError",
    "ValidationError",
    "ConfigurationError",
    "AudioProcessingError",
    "SessionError",
    "VideoProcessingError",
]
