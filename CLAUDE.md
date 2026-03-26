# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a dotfiles repository that manages configuration files for various tools (zsh, tmux, nvim, wezterm, etc.) using symlinks. Files prefixed with `_` in the repository root become dotfiles in `$HOME` (e.g., `_tmux.conf` → `~/.tmux.conf`). Platform‑specific files are placed in `Linux/` or `Darwin/` subdirectories.

## Common Development Tasks

### Installing Dotfiles

```bash
python3 install.py                 # normal installation (creates symlinks, backs up existing files)
python3 install.py --dryrun        # preview what will be done
python3 install.py --recover       # restore original dotfiles from `.BAK/`
```

The script automatically skips `_config` and `_local` directories; those are handled separately (see below).

### Installing Local Configurations

```bash
python3 local_config_install.py    # symlink contents of `_config/` and `_local/share/` to `$HOME/.config/` and `$HOME/.local/share/`
```

This script is intended for offline installation where Neovim plugins are already downloaded (they reside in `_local/share/nvim/lazy/`). It preserves directory hierarchy when backing up existing files (e.g., `~/.config/nvim` → `.BAK/_config/nvim`).

### Adding a New Dotfile

1. Add the configuration file with an underscore prefix (e.g., `_newtool.conf`) in the repository root or in the platform‑specific directory (`Linux/` or `Darwin/`).
2. Run `install.py --dryrun` to verify the symlink target.
3. Commit the file and install.

### Updating a Configuration

Edit the underscored file in the repository; the symlink in `$HOME` will point to the updated version. For changes to take effect, you may need to reload the tool (e.g., `source ~/.zshrc`, `tmux source-file ~/.tmux.conf`).

### Platform‑Specific Files

- Files placed in `Linux/` are used only on Linux systems.
- Files placed in `Darwin/` are used only on macOS.
- The install script merges the platform directory with the root when gathering source files.

### Creating Offline Archives

```bash
python3 package.py                 # create dotfiles.zip archive for offline installation
python3 package.py --dryrun        # list files that would be included
python3 package.py --verbose       # verbose output showing files added
python3 package.py --output custom.zip  # custom output filename
python3 package.py --exclude ".tmp" --exclude ".log"  # exclude additional patterns
```

The archive includes all configuration files and pre‑downloaded plugins, excluding version control (`.git`), backups (`.BAK`), Python cache files, and existing `.zip` files. Patterns starting with `^/` match from the root directory (e.g., `^/.git` excludes only the root `.git` directory, not submodule `.git` directories). Use this archive to install dotfiles on a non‑network device. After transferring the archive to the target device, extract it and run `python3 install.py` and `python3 local_config_install.py`.

## Repository Structure

- `_*` – source dotfiles (zsh, tmux, vim, etc.)
- `_config/` – configuration directories (nvim, wezterm) that are symlinked to `~/.config/`
- `_local/share/` – local data (Neovim plugins, etc.) symlinked to `~/.local/share/`
- `Linux/`, `Darwin/` – platform‑specific dotfiles (`Windows/` exists but is not used by install.py)
- `.BAK/` – backup directory created by the install script
- `misc/` – miscellaneous scripts and packages
- `install.py` – main installation script
- `local_config_install.py` – script for `_config` and `_local`
- `package.py` – create .zip archive for offline installation

## Git Submodules

This repository uses Git submodules for external plugins and configurations:

- `_oh-my-zsh/custom/plugins/fast-syntax-highlighting` – Zsh syntax highlighting
- `_vim_runtime` – Vim configuration bundle
- `_tmux/plugins/tpm` – Tmux Plugin Manager
- `_oh-my-zsh/custom/themes/powerlevel10k` – Zsh theme
- `_oh-my-zsh/custom/plugins/you-should-use` – Zsh plugin
- `_config/wezterm` – WezTerm configuration (private submodule)

To initialize and update submodules:

```bash
git submodule update --init --recursive
```

## Plugin Management

- **tmux**: Uses [TPM](https://github.com/tmux-plugins/tpm). Plugins are listed in `_tmux.conf`. After installing tmux config, press `<prefix> + I` to install plugins.
- **Neovim**: Uses [lazy.nvim](https://github.com/folke/lazy.nvim). Plugins are installed under `_local/share/nvim/lazy/`. The Neovim configuration is in `_config/nvim/`.
- **zsh**: Uses [Oh My Zsh](https://ohmyz.sh/) with plugins defined in `_zshrc`. The theme is Powerlevel10k.

## Notes

- The install script backs up existing dotfiles to `.BAK/_bak/` preserving source hierarchy (e.g., `Linux/_file` → `.BAK/_bak/Linux/_file`). Use `--recover` to restore them.
- `local_config_install.py` backs up to `.BAK/` preserving source hierarchy (e.g., `_config/nvim` → `.BAK/_config/nvim`).
- Files starting with `_config` or `_local` are intentionally skipped by `install.py`; use `local_config_install.py` for those.
- The repository contains a `requirements.txt` (in `misc/pkgs/`) listing Python dependencies for Neovim and other tools.
- Recent changes are documented in `History.md`.
