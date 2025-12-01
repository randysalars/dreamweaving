#!/usr/bin/env python3
"""
Input validation utilities for Dreamweaving.

Provides argparse-compatible validation functions for common parameter types.

Usage:
    import argparse
    from scripts.utilities.validation import (
        validate_frequency,
        validate_duration,
        validate_speaking_rate,
        validate_pitch,
        validate_file_exists,
        validate_output_path,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--beat-hz", type=validate_frequency, default=7.83)
    parser.add_argument("--duration", type=validate_duration, default=1800)
    parser.add_argument("input_file", type=validate_file_exists)
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Union


def validate_frequency(value: str) -> float:
    """
    Validate frequency is in audible range (1-20000 Hz).

    Args:
        value: String value from argparse

    Returns:
        Validated frequency as float

    Raises:
        argparse.ArgumentTypeError: If frequency is out of range
    """
    try:
        freq = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid number")

    if not (0.1 <= freq <= 20000):
        raise argparse.ArgumentTypeError(
            f"Frequency must be between 0.1 and 20000 Hz, got {freq}"
        )
    return freq


def validate_binaural_offset(value: str) -> float:
    """
    Validate binaural beat offset frequency (0.5-100 Hz).

    Typical ranges:
        - Delta: 0.5-4 Hz (deep sleep)
        - Theta: 4-8 Hz (meditation, creativity)
        - Alpha: 8-12 Hz (relaxation)
        - Beta: 12-30 Hz (focus, alertness)
        - Gamma: 30-100 Hz (cognition)

    Args:
        value: String value from argparse

    Returns:
        Validated offset frequency as float

    Raises:
        argparse.ArgumentTypeError: If frequency is out of range
    """
    try:
        freq = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid number")

    if not (0.5 <= freq <= 100):
        raise argparse.ArgumentTypeError(
            f"Binaural offset must be between 0.5 and 100 Hz, got {freq}"
        )
    return freq


def validate_duration(value: str) -> int:
    """
    Validate session duration is reasonable (30 seconds to 3 hours).

    Args:
        value: String value from argparse (seconds)

    Returns:
        Validated duration as int

    Raises:
        argparse.ArgumentTypeError: If duration is out of range
    """
    try:
        duration = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer")

    if not (30 <= duration <= 10800):  # 30 sec to 3 hours
        raise argparse.ArgumentTypeError(
            f"Duration must be between 30 and 10800 seconds (3 hours), got {duration}"
        )
    return duration


def validate_speaking_rate(value: str) -> float:
    """
    Validate TTS speaking rate (0.25x to 4.0x).

    Typical values:
        - 0.75-0.85: Slow hypnotic pace
        - 1.0: Normal speed
        - 1.1-1.2: Slightly faster

    Args:
        value: String value from argparse

    Returns:
        Validated speaking rate as float

    Raises:
        argparse.ArgumentTypeError: If rate is out of range
    """
    try:
        rate = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid number")

    if not (0.25 <= rate <= 4.0):
        raise argparse.ArgumentTypeError(
            f"Speaking rate must be between 0.25 and 4.0, got {rate}"
        )
    return rate


def validate_pitch(value: str) -> float:
    """
    Validate TTS pitch adjustment (-20 to +20 semitones).

    Typical values:
        - -2 to -3: Warmer, deeper voice
        - 0: Natural pitch
        - +1 to +2: Brighter voice

    Args:
        value: String value from argparse

    Returns:
        Validated pitch as float

    Raises:
        argparse.ArgumentTypeError: If pitch is out of range
    """
    try:
        pitch = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid number")

    if not (-20 <= pitch <= 20):
        raise argparse.ArgumentTypeError(
            f"Pitch must be between -20 and +20 semitones, got {pitch}"
        )
    return pitch


def validate_volume_db(value: str) -> float:
    """
    Validate volume adjustment in dB (-40 to +10 dB).

    Args:
        value: String value from argparse

    Returns:
        Validated volume as float

    Raises:
        argparse.ArgumentTypeError: If volume is out of range
    """
    try:
        volume = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid number")

    if not (-40 <= volume <= 10):
        raise argparse.ArgumentTypeError(
            f"Volume must be between -40 and +10 dB, got {volume}"
        )
    return volume


def validate_sample_rate(value: str) -> int:
    """
    Validate audio sample rate.

    Standard rates: 16000, 22050, 24000, 44100, 48000, 96000

    Args:
        value: String value from argparse

    Returns:
        Validated sample rate as int

    Raises:
        argparse.ArgumentTypeError: If rate is invalid
    """
    valid_rates = {16000, 22050, 24000, 44100, 48000, 96000}

    try:
        rate = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer")

    if rate not in valid_rates:
        raise argparse.ArgumentTypeError(
            f"Sample rate must be one of {sorted(valid_rates)}, got {rate}"
        )
    return rate


def validate_file_exists(value: str) -> Path:
    """
    Validate that a file exists.

    Args:
        value: File path from argparse

    Returns:
        Path object for the file

    Raises:
        argparse.ArgumentTypeError: If file doesn't exist
    """
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File not found: {value}")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Not a file: {value}")
    return path


def validate_dir_exists(value: str) -> Path:
    """
    Validate that a directory exists.

    Args:
        value: Directory path from argparse

    Returns:
        Path object for the directory

    Raises:
        argparse.ArgumentTypeError: If directory doesn't exist
    """
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Directory not found: {value}")
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"Not a directory: {value}")
    return path


def validate_output_path(value: str) -> Path:
    """
    Validate that output path's parent directory exists.

    Args:
        value: Output file path from argparse

    Returns:
        Path object for the output file

    Raises:
        argparse.ArgumentTypeError: If parent directory doesn't exist
    """
    path = Path(value)
    parent = path.parent

    # If no parent specified (just filename), use current directory
    if str(parent) == ".":
        return path

    if not parent.exists():
        raise argparse.ArgumentTypeError(
            f"Output directory does not exist: {parent}"
        )
    return path


def validate_voice_name(value: str) -> str:
    """
    Validate Google Cloud TTS voice name format.

    Expected format: language-REGION-VoiceType-Letter
    Example: en-US-Neural2-A

    Args:
        value: Voice name from argparse

    Returns:
        Validated voice name

    Raises:
        argparse.ArgumentTypeError: If format is invalid
    """
    import re

    # Pattern for Google Cloud TTS voice names
    pattern = r'^[a-z]{2}-[A-Z]{2}-(Neural2|Wavenet|Standard|Journey|Polyglot)-[A-Z]$'

    if not re.match(pattern, value):
        raise argparse.ArgumentTypeError(
            f"Invalid voice name format: {value}. "
            f"Expected format like 'en-US-Neural2-A'"
        )
    return value


def validate_percentage(value: str) -> float:
    """
    Validate percentage value (0-100 or 0.0-1.0).

    Args:
        value: Percentage from argparse

    Returns:
        Normalized percentage as float (0.0-1.0)

    Raises:
        argparse.ArgumentTypeError: If value is invalid
    """
    try:
        pct = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid number")

    # Normalize percentage
    if pct > 1.0:
        pct = pct / 100.0

    if not (0.0 <= pct <= 1.0):
        raise argparse.ArgumentTypeError(
            f"Percentage must be between 0 and 100 (or 0.0 and 1.0), got {value}"
        )
    return pct


def validate_path_safety(path: str, safe_base: Path) -> Path:
    """
    Validate that a path is within a safe base directory.

    Prevents path traversal attacks by ensuring the resolved path
    is within the expected directory tree.

    Args:
        path: Path to validate (can be relative or absolute)
        safe_base: Base directory that path must be within

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path is outside safe_base directory
    """
    resolved = Path(path).resolve()
    safe_resolved = safe_base.resolve()

    try:
        resolved.relative_to(safe_resolved)
    except ValueError:
        raise ValueError(
            f"Path '{path}' resolves outside safe directory '{safe_base}'"
        )

    return resolved


def validate_safe_filename(filename: str) -> str:
    """
    Validate that a filename doesn't contain path traversal characters.

    Args:
        filename: Filename to validate (should not contain path separators)

    Returns:
        Validated filename

    Raises:
        argparse.ArgumentTypeError: If filename contains path separators
    """
    if '/' in filename or '\\' in filename:
        raise argparse.ArgumentTypeError(
            f"Filename cannot contain path separators: {filename}"
        )

    if filename.startswith('.'):
        raise argparse.ArgumentTypeError(
            f"Filename cannot start with '.': {filename}"
        )

    if filename in ('.', '..'):
        raise argparse.ArgumentTypeError(
            f"Invalid filename: {filename}"
        )

    return filename


# Example usage and testing
if __name__ == "__main__":
    print("Validation Utilities Test")
    print("=" * 60)

    # Test frequency validation
    print("\nTesting validate_frequency:")
    for val in ["7.83", "440", "0.05", "25000"]:
        try:
            result = validate_frequency(val)
            print(f"  '{val}' -> {result} ✓")
        except argparse.ArgumentTypeError as e:
            print(f"  '{val}' -> Error: {e}")

    # Test duration validation
    print("\nTesting validate_duration:")
    for val in ["1800", "60", "15", "20000"]:
        try:
            result = validate_duration(val)
            print(f"  '{val}' -> {result} ✓")
        except argparse.ArgumentTypeError as e:
            print(f"  '{val}' -> Error: {e}")

    # Test speaking rate validation
    print("\nTesting validate_speaking_rate:")
    for val in ["0.85", "1.0", "0.1", "5.0"]:
        try:
            result = validate_speaking_rate(val)
            print(f"  '{val}' -> {result} ✓")
        except argparse.ArgumentTypeError as e:
            print(f"  '{val}' -> Error: {e}")

    # Test voice name validation
    print("\nTesting validate_voice_name:")
    for val in ["en-US-Neural2-A", "en-US-Neural2-I", "invalid", "en-us-neural2-a"]:
        try:
            result = validate_voice_name(val)
            print(f"  '{val}' -> {result} ✓")
        except argparse.ArgumentTypeError as e:
            print(f"  '{val}' -> Error: {e}")

    print("\n" + "=" * 60)
    print("✓ Validation utilities ready for use")
