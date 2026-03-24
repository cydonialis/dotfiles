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


class MLevel(object):
    check = "✔"
    cross = "✗"
    other = "○"


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


def __dot_mark(dst: str) -> str:
    if not os.path.exists(dst):
        mark = MLevel.check
    elif os.path.islink(dst):
        mark = MLevel.other
    else:
        mark = MLevel.cross
    return mark


def _find_backup_path(src: str, bakdir: str) -> str | None:
    """Find existing backup path for src, checking for .bak.{n} suffixes."""
    src_rel = os.path.relpath(src, CUR_DIR)
    backup_path = os.path.join(bakdir, src_rel)
    if os.path.exists(backup_path) and not os.path.islink(backup_path):
        return backup_path
    # Check for .bak.{n} suffixes
    base = backup_path
    counter = 1
    while os.path.exists(f"{base}.bak.{counter}"):
        if not os.path.islink(f"{base}.bak.{counter}"):
            return f"{base}.bak.{counter}"
        counter += 1
    return None


def __recover_mark(src: str, bakdir: str) -> str:
    return MLevel.check if _find_backup_path(src, bakdir) is not None else MLevel.cross


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
    """Dry-run: print what would be done with install.py style."""
    mark = __dot_mark(dst)
    rel_src = os.path.relpath(src, DST_DIR)
    print("{0:<60} ⇒ \t[{m}] {1:<50}".format(rel_src, dst, m=mark))


def _recover_dryrun(src: str, dst: str, bakdir: str):
    """Dry-run for recovery."""
    mark = __recover_mark(src, bakdir)
    backup_path = _find_backup_path(src, bakdir)
    if backup_path:
        rel_bak = os.path.relpath(backup_path, CUR_DIR)
        print("{0:<60} ->\t[{m}] {1:<50}".format(rel_bak, dst, m=mark))
    else:
        # No backup found
        rel_src = os.path.relpath(src, CUR_DIR)
        print("{0:<60} ->\t[{m}] {1:<50}".format(rel_src, dst, m=mark))


def _recover(src: str, dst: str, bakdir: str):
    """Restore original file from backup."""
    backup_path = _find_backup_path(src, bakdir)
    if backup_path is None:
        print(f"No backup found for {dst}", file=sys.stderr)
        return

    # Remove destination symlink if it exists
    if os.path.exists(dst) or os.path.islink(dst):
        if os.path.islink(dst):
            os.unlink(dst)
        else:
            # Should not happen - dst should be symlink we created
            # But just in case, backup current dst before overwriting
            temp_backup = backup_path + ".temp"
            shutil.move(dst, temp_backup)
            print(f"Warning: {dst} was not a symlink, backed up to {temp_backup}", file=sys.stderr)

    # Restore from backup
    print(f"Restoring {dst} from {backup_path}", file=sys.stderr)
    shutil.move(backup_path, dst)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install _config/ and _local/share/ to $HOME/.config/ and $HOME/.local/share/",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--recover",
        dest="recover",
        action="store_true",
        required=False,
        help="restore original config/local files from backup",
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

    if not args.recover:
        # Install mode
        if not args.dryrun:
            _ensure_bakdir(args.bakdir)

        src_files = _get_src_files(CUR_DIR)
        print(f"Found {len(src_files)} config/local items to symlink:")

        for src_file in src_files:
            src_abs = os.path.join(CUR_DIR, src_file)
            dst = os.path.join(DST_DIR, "." + src_file[1:])  # Remove leading '_'
            if args.dryrun:
                _dot_dryrun(src_abs, dst, args.bakdir)
            else:
                _dot(src_abs, dst, args.bakdir)
    else:
        # Recover mode
        if not args.dryrun:
            # Ensure backup directory exists for recovery
            if not os.path.exists(args.bakdir):
                print(f"Backup directory {args.bakdir} does not exist, nothing to recover.", file=sys.stderr)
                return

        src_files = _get_src_files(CUR_DIR)
        print(f"Found {len(src_files)} config/local items to recover:")

        for src_file in src_files:
            src_abs = os.path.join(CUR_DIR, src_file)
            dst = os.path.join(DST_DIR, "." + src_file[1:])  # Remove leading '_'
            if args.dryrun:
                _recover_dryrun(src_abs, dst, args.bakdir)
            else:
                _recover(src_abs, dst, args.bakdir)

    print("Done.")


if __name__ == "__main__":
    main()