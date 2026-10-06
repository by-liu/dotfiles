# Dotfiles

Portable configuration managed with [chezmoi](https://www.chezmoi.io/).

Currently included:

- LazyVim (language extras and remote clipboard support)
- Herdr (navigation keys and pane layout shortcut)
- tmux (`~/.config/tmux/tmux.conf`)

Machine-specific files, secrets, and Omarchy-managed files are intentionally
excluded.

## Install

```bash
# Omarchy / Arch Linux
omarchy-pkg-add chezmoi

# macOS
brew install chezmoi
```

## Set up a machine

Authenticate GitHub first, then:

```bash
chezmoi init https://github.com/by-liu/dotfiles.git
chezmoi diff
chezmoi apply -v
```

Always review `chezmoi diff` before the first apply.

## Save a change

After editing a live config:

```bash
chezmoi diff
chezmoi re-add ~/.config/nvim/lua/config/keymaps.lua

chezmoi cd
git diff
git add .
git commit -m "Update dotfiles"
git push
exit
```

Replace the path with the file or directory that changed.

## Get updates

```bash
chezmoi update -v
```

