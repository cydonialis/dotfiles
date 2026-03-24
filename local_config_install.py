#!/bin/python3
# Install _config/ and _local/share/ to $HOME/.config/ and $HOME/.local/share/
# Used for installing dotfiles to a non-network device where nvim plugins
# don't need to be downloaded (pre-downloaded plugins are in _local/share/nvim/lazy/)

import argparse
import os
import shutil
import sys


CUR_DIR: str = os.path.abspath(os.path.dirname(__file__))
DST_DIR = os.path.realpath(os.path.expandvars("$HOME"))
BAK_DIR: str = os.path.join(CUR_DIR, ".BAK")


def _ensure_bakdir(bakdir: str):
    """Ensure backup directory exists."""
    if not os.path.exists(bakdir):
        print(f"Backup directory {bakdir} does not exist.", file=sys.stderr)
        try:
            os.makedirs(bakdir)
            print(f"Created backup directory: {bakdir}")
        except OSError as e:
            print(f"Failed to create backup directory: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Using backup directory: {bakdir}")


def _get_src_files(root: str) -> list[str]:
    src_files: list[str] = []
    for src in os.listdir(os.path.join(root, "_config")):
        src_files.append(os.path.join("_config", src))
    for src in os.listdir(os.path.join(root, "_local", "share")):
        src_files.append(os.path.join("_local", "share", src))
    return src_files


def _get_backup_path(src: str, bakdir: str) -> str:
    """Compute backup path preserving source hierarchy.

    Example: src='/path/to/_config/nvim' -> bakdir/_config/nvim
    """
    # Get path relative to CUR_DIR
    src_rel = os.path.relpath(src, CUR_DIR)
    # Backup path mirrors source hierarchy under bakdir
    backup_path = os.path.join(bakdir, src_rel)
    # Ensure backup path is unique if it already exists
    if os.path.exists(backup_path):
        # Add incremental suffix .bak.1, .bak.2, etc.
        base = backup_path
        counter = 1
        while os.path.exists(f"{base}.bak.{counter}"):
            counter += 1
        backup_path = f"{base}.bak.{counter}"
    return backup_path


def _dot(src: str, dst: str, bakdir: str):
    """Create symlink, backing up existing file/directory."""
    dst_exist = os.path.exists(dst) or os.path.islink(dst)
    if dst_exist:
        if os.path.islink(dst):
            print(f"Removing existing symlink: {dst}", file=sys.stderr)
            os.unlink(dst)
        else:
            # Backup preserving hierarchy
            backup_path = _get_backup_path(src, bakdir)
            print(f"Backing up {dst} to {backup_path}", file=sys.stderr)
            # Ensure parent directory of backup exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.move(dst, backup_path)
    # Ensure parent directory of destination exists (e.g., ~/.config, ~/.local/share)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    # Create absolute symlink
    os.symlink(src, dst)


def _dot_dryrun(src: str, dst: str, bakdir: str):
    """Dry-run: print what would be done."""
    dst_exist = os.path.exists(dst) or os.path.islink(dst)
    if dst_exist:
        if os.path.islink(dst):
            print(f"[dryrun] Would remove symlink: {dst}")
        else:
            backup_path = _get_backup_path(src, bakdir)
            print(f"[dryrun] Would backup {dst} to {backup_path}")
    else:
        print(f"[dryrun] Would create symlink: {dst} -> {src}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install _config/ and _local/share/ to $HOME/.config/ and $HOME/.local/share/",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-n",
        "--dryrun",
        dest="dryrun",
        action="store_true",
        required=False,
        help="print the effect rather than run it",
    )
    parser.add_argument(
        "-d",
        "--bakdir",
        dest="bakdir",
        default=BAK_DIR,
        required=False,
        help="backup directory",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.dryrun:
        _ensure_bakdir(args.bakdir)

    src_files = _get_src_files(CUR_DIR)
    print(f"Found {len(src_files)} config/local items to symlink:")

    for src_file in src_files:
        src_abs = os.path.join(CUR_DIR, src_file)
        dst = os.path.join(DST_DIR, "." + src_file[1:])  # Remove leading '_'
        print(f"  {src_file} -> {dst}")
        if args.dryrun:
            _dot_dryrun(src_abs, dst, args.bakdir)
        else:
            _dot(src_abs, dst, args.bakdir)

    print("Done.")


if __name__ == "__main__":
    main()