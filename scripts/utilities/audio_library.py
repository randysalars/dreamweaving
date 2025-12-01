#!/usr/bin/env python3
"""
Audio Library Manager
Provides easy access to reusable audio assets
"""

import os
import yaml
import subprocess
from pathlib import Path
from typing import Optional, List, Dict


class AudioLibrary:
    """Manages the Dreamweaving audio asset library"""

    def __init__(self):
        self.project_root = self._find_project_root()
        self.assets_dir = self.project_root / 'assets' / 'audio'
        self.catalog_path = self.assets_dir / 'LIBRARY_CATALOG.yaml'
        self.catalog = self._load_catalog()

    def _find_project_root(self) -> Path:
        """Find project root directory"""
        current = Path(__file__).resolve()
        # Go up from scripts/utilities/ to project root
        return current.parent.parent.parent

    def _load_catalog(self) -> Dict:
        """Load the asset catalog"""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")

        with open(self.catalog_path, 'r') as f:
            return yaml.safe_load(f)

    def get_asset_path(self, asset_name: str, category: str = None) -> Optional[Path]:
        """
        Get full path to an asset

        Args:
            asset_name: Name of the asset (e.g., 'crystal_bell')
            category: Optional category ('ambient', 'effects', 'binaural')

        Returns:
            Path to asset file, or None if not found
        """
        if category:
            assets = self.catalog.get(category, {})
            if asset_name in assets:
                rel_path = assets[asset_name]['file']
                return self.assets_dir / rel_path
        else:
            # Search all categories
            for cat in ['ambient', 'effects', 'binaural']:
                assets = self.catalog.get(cat, {})
                if asset_name in assets:
                    rel_path = assets[asset_name]['file']
                    return self.assets_dir / rel_path

        return None

    def get_asset_info(self, asset_name: str) -> Optional[Dict]:
        """Get metadata about an asset"""
        for category in ['ambient', 'effects', 'binaural']:
            assets = self.catalog.get(category, {})
            if asset_name in assets:
                info = assets[asset_name].copy()
                info['category'] = category
                info['name'] = asset_name
                return info
        return None

    def list_by_tag(self, tag: str) -> List[str]:
        """Find all assets with a specific tag"""
        return self.catalog.get('by_tag', {}).get(tag, [])

    def list_by_use_case(self, use_case: str) -> List[str]:
        """Find assets suitable for a use case"""
        return self.catalog.get('by_use_case', {}).get(use_case, [])

    def get_duration(self, asset_name: str) -> Optional[float]:
        """Get duration of an asset in seconds"""
        info = self.get_asset_info(asset_name)
        if info:
            return info.get('duration')
        return None

    def copy_to_session(self, asset_name: str, dest_path: str):
        """
        Copy asset to session directory.

        For security, destination must be within the project's sessions directory.

        Args:
            asset_name: Name of the asset to copy
            dest_path: Destination path (must be within sessions/)

        Raises:
            FileNotFoundError: If asset doesn't exist
            ValueError: If destination is outside safe directory
        """
        src_path = self.get_asset_path(asset_name)
        if not src_path or not src_path.exists():
            raise FileNotFoundError(f"Asset not found: {asset_name}")

        # Validate destination is within safe directory (sessions/)
        dest = Path(dest_path).resolve()
        safe_dir = (self.project_root / "sessions").resolve()

        # Check that dest is within safe_dir (prevent path traversal)
        try:
            dest.relative_to(safe_dir)
        except ValueError:
            raise ValueError(
                f"Destination must be within {safe_dir}. "
                f"Got: {dest}"
            )

        dest.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(['cp', str(src_path), str(dest)], check=True)

    def verify_assets(self) -> Dict[str, bool]:
        """Verify all cataloged assets exist"""
        results = {}
        for category in ['ambient', 'effects', 'binaural']:
            assets = self.catalog.get(category, {})
            if assets and isinstance(assets, dict):
                for name, info in assets.items():
                    path = self.assets_dir / info['file']
                    results[f"{category}/{name}"] = path.exists()
        return results

    def list_all(self) -> Dict[str, List[str]]:
        """List all assets by category"""
        result = {}
        for category in ['ambient', 'effects', 'binaural']:
            assets = self.catalog.get(category, {})
            if assets and isinstance(assets, dict):
                result[category] = list(assets.keys())
            else:
                result[category] = []
        return result

    def search(self, query: str) -> List[Dict]:
        """
        Search assets by name, tag, or use case
        Returns list of matching asset info dicts
        """
        results = []
        query_lower = query.lower()

        for category in ['ambient', 'effects', 'binaural']:
            assets = self.catalog.get(category, {})
            if not assets or not isinstance(assets, dict):
                continue
            for name, info in assets.items():
                # Check name
                if query_lower in name.lower():
                    info_copy = info.copy()
                    info_copy['name'] = name
                    info_copy['category'] = category
                    results.append(info_copy)
                    continue

                # Check tags
                tags = info.get('tags', [])
                if any(query_lower in tag.lower() for tag in tags):
                    info_copy = info.copy()
                    info_copy['name'] = name
                    info_copy['category'] = category
                    results.append(info_copy)
                    continue

                # Check description
                desc = info.get('description', '')
                if query_lower in desc.lower():
                    info_copy = info.copy()
                    info_copy['name'] = name
                    info_copy['category'] = category
                    results.append(info_copy)

        return results


def main():
    """CLI interface for audio library"""
    import argparse

    parser = argparse.ArgumentParser(description='Audio Library Manager')
    parser.add_argument('command', choices=['list', 'info', 'search', 'verify', 'path'],
                       help='Command to execute')
    parser.add_argument('query', nargs='?', help='Asset name or search query')
    parser.add_argument('--tag', help='Filter by tag')
    parser.add_argument('--use-case', help='Filter by use case')
    parser.add_argument('--category', choices=['ambient', 'effects', 'binaural'],
                       help='Limit to category')

    args = parser.parse_args()

    lib = AudioLibrary()

    if args.command == 'list':
        if args.tag:
            assets = lib.list_by_tag(args.tag)
            print(f"Assets with tag '{args.tag}':")
            for asset in assets:
                print(f"  - {asset}")
        elif args.use_case:
            assets = lib.list_by_use_case(args.use_case)
            print(f"Assets for '{args.use_case}':")
            for asset in assets:
                print(f"  - {asset}")
        else:
            all_assets = lib.list_all()
            for category, assets in all_assets.items():
                print(f"\n{category.upper()}:")
                for asset in assets:
                    info = lib.get_asset_info(asset)
                    duration = info.get('duration', 'unknown')
                    print(f"  - {asset} ({duration}s)")

    elif args.command == 'info':
        if not args.query:
            print("Error: Asset name required")
            return 1

        info = lib.get_asset_info(args.query)
        if not info:
            print(f"Asset not found: {args.query}")
            return 1

        print(f"\nAsset: {info['name']}")
        print(f"Category: {info['category']}")
        print(f"File: {info['file']}")
        print(f"Duration: {info.get('duration', 'unknown')}s")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Tags: {', '.join(info.get('tags', []))}")
        if 'use_cases' in info:
            print(f"Use cases:")
            for uc in info['use_cases']:
                print(f"  - {uc}")

    elif args.command == 'search':
        if not args.query:
            print("Error: Search query required")
            return 1

        results = lib.search(args.query)
        if not results:
            print(f"No assets found matching: {args.query}")
            return 0

        print(f"\nFound {len(results)} asset(s):")
        for result in results:
            print(f"\n  {result['name']} ({result['category']})")
            print(f"    {result.get('description', 'No description')}")
            print(f"    Duration: {result.get('duration', '?')}s")

    elif args.command == 'verify':
        results = lib.verify_assets()
        print("\nAsset Verification:")
        all_exist = True
        for asset, exists in results.items():
            status = "✓" if exists else "✗"
            print(f"  {status} {asset}")
            if not exists:
                all_exist = False

        if all_exist:
            print("\n✓ All assets verified!")
        else:
            print("\n⚠ Some assets are missing")
            return 1

    elif args.command == 'path':
        if not args.query:
            print("Error: Asset name required")
            return 1

        path = lib.get_asset_path(args.query, args.category)
        if not path:
            print(f"Asset not found: {args.query}")
            return 1

        print(path)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
