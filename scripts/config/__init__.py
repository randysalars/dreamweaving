"""
Centralized configuration module for the Dreamweaving project.

This module provides default values and configuration constants used
throughout the codebase, replacing scattered magic numbers.

Usage:
    from scripts.config import defaults

    # Access audio settings
    sample_rate = defaults.AUDIO['sample_rate_hz']

    # Access video settings
    width = defaults.VIDEO['width']
"""

from . import defaults

__all__ = ['defaults']
