#!/usr/bin/env python3
"""
Sync YouTube Playlist IDs

Queries YouTube for existing playlists and updates config/youtube_playlists.yaml
with the actual playlist IDs. Optionally creates missing playlists.

Usage:
    # Show what would be synced (dry run)
    python scripts/utilities/sync_playlist_ids.py --dry-run

    # Sync playlist IDs from YouTube
    python scripts/utilities/sync_playlist_ids.py

    # Create missing playlists on YouTube
    python scripts/utilities/sync_playlist_ids.py --create-missing

    # Validate current config against YouTube
    python scripts/utilities/sync_playlist_ids.py --validate-only
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.automation.youtube_client import YouTubeClient

logger = logging.getLogger(__name__)

# Default config path
DEFAULT_CONFIG_PATH = PROJECT_ROOT / 'config' / 'youtube_playlists.yaml'


def load_config(config_path: Path) -> dict:
    """Load playlist configuration from YAML."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict, config_path: Path) -> None:
    """Save playlist configuration to YAML."""
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def collect_all_playlists(config: dict) -> list:
    """
    Collect all playlist entries from config.

    Returns list of dicts with keys: type, slug, name, youtube_id
    """
    playlists = []

    # Master and fallback playlists
    for key in ['master_playlist', 'fallback_playlist']:
        if key in config:
            playlists.append({
                'type': key,
                'slug': key,
                'name': config[key]['name'],
                'youtube_id': config[key].get('youtube_id', ''),
            })

    # Category playlists
    for playlist_type in ['content_playlists', 'format_playlists',
                          'duration_playlists', 'series_playlists']:
        for slug, data in config.get(playlist_type, {}).items():
            playlists.append({
                'type': playlist_type,
                'slug': slug,
                'name': data['name'],
                'youtube_id': data.get('youtube_id', ''),
            })

    return playlists


def sync_playlist_ids(
    youtube: YouTubeClient,
    config: dict,
    config_path: Path,
    create_missing: bool = False,
    dry_run: bool = False
) -> dict:
    """
    Sync playlist IDs from YouTube.

    Args:
        youtube: Authenticated YouTubeClient
        config: Loaded config dict
        config_path: Path to config file
        create_missing: Whether to create missing playlists
        dry_run: If True, don't make changes

    Returns:
        Summary dict with counts
    """
    # Get all playlists from YouTube
    logger.info("Fetching playlists from YouTube...")
    youtube_playlists = youtube.list_playlists(max_results=50)
    yt_by_name = {p['title'].lower(): p for p in youtube_playlists}

    logger.info(f"Found {len(youtube_playlists)} playlists on YouTube")

    # Collect all config playlists
    config_playlists = collect_all_playlists(config)

    # Track changes
    updates = []
    missing = []
    valid = []
    created = []

    # Process each playlist
    for playlist in config_playlists:
        name = playlist['name']
        current_id = playlist['youtube_id']
        name_lower = name.lower()

        # Check if exists on YouTube
        yt_playlist = yt_by_name.get(name_lower)

        if yt_playlist:
            # Found on YouTube
            if current_id != yt_playlist['id']:
                updates.append({
                    **playlist,
                    'old_id': current_id,
                    'new_id': yt_playlist['id']
                })
            else:
                valid.append(playlist)
        else:
            # Not found on YouTube
            missing.append(playlist)

    # Report findings
    print(f"\n{'='*60}")
    print("PLAYLIST SYNC REPORT")
    print(f"{'='*60}\n")

    print(f"Playlists in config: {len(config_playlists)}")
    print(f"Playlists on YouTube: {len(youtube_playlists)}")
    print(f"Already synced: {len(valid)}")
    print(f"Need ID update: {len(updates)}")
    print(f"Missing on YouTube: {len(missing)}")

    if updates:
        print(f"\n--- Updates Needed ({len(updates)}) ---")
        for u in updates:
            old_display = u['old_id'] or '(empty)'
            print(f"  {u['name']}")
            print(f"    {old_display} -> {u['new_id']}")

    if missing:
        print(f"\n--- Missing on YouTube ({len(missing)}) ---")
        for m in missing:
            print(f"  {m['name']} ({m['type']})")

    # Apply updates
    if not dry_run and updates:
        print(f"\nApplying {len(updates)} ID updates...")
        for u in updates:
            _update_config_id(config, u['type'], u['slug'], u['new_id'])

        save_config(config, config_path)
        print(f"Config saved to {config_path}")

    # Create missing playlists if requested
    if create_missing and missing:
        print(f"\nCreating {len(missing)} missing playlists...")
        for m in missing:
            if dry_run:
                print(f"  [DRY RUN] Would create: {m['name']}")
            else:
                description = f"Dreamweaving {m['name']} collection"
                playlist_id = youtube.create_playlist(
                    title=m['name'],
                    description=description,
                    privacy_status='public'
                )
                if playlist_id:
                    _update_config_id(config, m['type'], m['slug'], playlist_id)
                    created.append({**m, 'new_id': playlist_id})
                    print(f"  Created: {m['name']} -> {playlist_id}")
                else:
                    print(f"  FAILED: {m['name']}")

        if created and not dry_run:
            save_config(config, config_path)
            print(f"Config updated with {len(created)} new playlist IDs")

    if dry_run:
        print("\n[DRY RUN] No changes made")

    return {
        'total': len(config_playlists),
        'valid': len(valid),
        'updated': len(updates),
        'missing': len(missing),
        'created': len(created),
    }


def _update_config_id(config: dict, playlist_type: str, slug: str, new_id: str) -> None:
    """Update a playlist ID in the config dict."""
    if playlist_type in ['master_playlist', 'fallback_playlist']:
        config[playlist_type]['youtube_id'] = new_id
    else:
        config[playlist_type][slug]['youtube_id'] = new_id


def validate_config(youtube: YouTubeClient, config: dict) -> dict:
    """
    Validate that all playlist IDs in config are accessible.

    Returns:
        Summary dict with validation results
    """
    config_playlists = collect_all_playlists(config)

    valid = []
    invalid = []
    missing_id = []

    print(f"\n{'='*60}")
    print("PLAYLIST VALIDATION REPORT")
    print(f"{'='*60}\n")

    for playlist in config_playlists:
        playlist_id = playlist['youtube_id']
        name = playlist['name']

        if not playlist_id:
            missing_id.append(playlist)
            print(f"  [NO ID] {name}")
        elif youtube.validate_playlist_exists(playlist_id):
            valid.append(playlist)
            print(f"  [OK] {name}")
        else:
            invalid.append(playlist)
            print(f"  [INVALID] {name} ({playlist_id})")

    print(f"\n--- Summary ---")
    print(f"Valid: {len(valid)}")
    print(f"Invalid IDs: {len(invalid)}")
    print(f"Missing IDs: {len(missing_id)}")

    return {
        'valid': len(valid),
        'invalid': len(invalid),
        'missing': len(missing_id),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Sync YouTube playlist IDs to configuration file'
    )
    parser.add_argument(
        '--create-missing',
        action='store_true',
        help='Create playlists on YouTube if they do not exist'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing IDs, do not sync'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help='Path to playlist config file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    config_path = Path(args.config)

    # Load config
    try:
        config = load_config(config_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Initialize YouTube client
    try:
        youtube = YouTubeClient()
    except Exception as e:
        print(f"ERROR: Failed to initialize YouTube client: {e}", file=sys.stderr)
        print("Make sure you have valid OAuth credentials in config/youtube_credentials/")
        return 1

    # Run requested operation
    if args.validate_only:
        result = validate_config(youtube, config)
        return 0 if result['invalid'] == 0 else 1
    else:
        result = sync_playlist_ids(
            youtube=youtube,
            config=config,
            config_path=config_path,
            create_missing=args.create_missing,
            dry_run=args.dry_run
        )
        return 0


if __name__ == '__main__':
    sys.exit(main())
