#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a .zip archive of dotfiles for offline installation.

The archive includes all configuration files and pre-downloaded plugins,
excluding version control, backups, and Python cache files.
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path
from typing import List, Optional


def should_exclude(path: Path, exclude_patterns: List[str], root_dir: Optional[Path] = None) -> bool:
    """Return True if path matches any exclude pattern.

    Pattern matching rules:
    - If pattern starts with '^/': match from root directory (root-relative)
    - Else if pattern contains '/': match as substring (path fragment)
    - Else if pattern starts with '.': match as file extension (if path is a file)
      AND also match as exact component name (for directory names starting with dot)
    - Else: match as exact component name (directory or file name)
    """
    # Compute relative path if root_dir provided
    rel_path = None
    if root_dir:
        try:
            rel_path = path.relative_to(root_dir)
        except ValueError:
            rel_path = None

    path_str = str(path)
    parts = path.parts

    for pattern in exclude_patterns:
        # Root-relative pattern (new feature: starts with '^/')
        if pattern.startswith('^/') and rel_path:
            pattern_suffix = pattern[2:]  # Remove '^/' prefix
            if pattern_suffix:
                pattern_parts = pattern_suffix.split('/')
                pattern_parts = [p for p in pattern_parts if p]  # Remove empty parts
                # Check if path starts with pattern components
                if rel_path.parts[:len(pattern_parts)] == tuple(pattern_parts):
                    return True
            continue  # Don't fall through to other pattern types

        # Path fragment match (contains '/')
        if '/' in pattern:
            if pattern in path_str:
                return True
            continue

        # Exact component match (directory or file name)
        if pattern in parts:
            return True

        # File extension match (pattern starts with dot)
        if pattern.startswith('.') and path.is_file() and path.name.endswith(pattern):
            return True

    return False


def collect_files(root_dir: Path, exclude_patterns: List[str]) -> List[Path]:
    """Collect all files to include in archive."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in-place to skip excluded directories
        dirnames[:] = [
            d for d in dirnames
            if not should_exclude(Path(dirpath) / d, exclude_patterns, root_dir)
        ]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            if not should_exclude(filepath, exclude_patterns, root_dir):
                files.append(filepath)
    return files


def create_dotfiles_zip(
    source_dir: str,
    output_zip: str,
    exclude_patterns: Optional[List[str]] = None,
    verbose: bool = False,
    dryrun: bool = False,
) -> None:
    """Create a zip archive of dotfiles."""
    if exclude_patterns is None:
        exclude_patterns = [
            "^/.git",
            ".BAK",
            "__pycache__",
            ".pyc",
            ".zip",  # exclude existing zip files
        ]

    source_path = Path(source_dir).resolve()
    output_path = Path(output_zip).resolve()

    # Ensure source directory exists
    if not source_path.exists():
        print(f"Error: Source directory '{source_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Collect files
    print(f"Scanning '{source_path}' for files...")
    files = collect_files(source_path, exclude_patterns)
    print(f"Found {len(files)} files to include.")

    if dryrun:
        print(f"Dry run: would create archive '{output_path}' with {len(files)} files.")
        if verbose:
            for file in files:
                arcname = file.relative_to(source_path)
                print(f"  Would add: {arcname}")
        return

    # Create zip archive
    print(f"Creating archive '{output_path}'...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            # Calculate relative path within archive
            arcname = file.relative_to(source_path)
            if verbose:
                print(f"  Adding: {arcname}")
            zf.write(file, arcname)

    print(f"Done. Archive size: {output_path.stat().st_size / (1024*1024):.2f} MB")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a .zip archive of dotfiles for offline installation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--source",
        dest="source_dir",
        default=".",
        required=False,
        help="source directory containing dotfiles",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_zip",
        default="dotfiles.zip",
        required=False,
        help="output .zip file path",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        required=False,
        help="verbose output listing files added",
    )
    parser.add_argument(
        "-n",
        "--dryrun",
        dest="dryrun",
        action="store_true",
        required=False,
        help="list files that would be added without creating archive",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        dest="exclude_patterns",
        action="append",
        default=[],
        required=False,
        help="additional exclude patterns (can be used multiple times)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Default exclude patterns
    default_exclude = [
        "^/.git",
        ".BAK",
        "__pycache__",
        ".pyc",
        ".zip",
    ]

    # Combine default and user-provided exclude patterns
    exclude_patterns = default_exclude + args.exclude_patterns

    create_dotfiles_zip(
        source_dir=args.source_dir,
        output_zip=args.output_zip,
        exclude_patterns=exclude_patterns,
        verbose=args.verbose,
        dryrun=args.dryrun,
    )


if __name__ == "__main__":
    main()