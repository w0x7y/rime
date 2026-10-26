# Port ideas

Programs Rime could be ported to, best value first in each section. Tick an item once its port ships. Adding a port means a generator in `tools/build.py`, a page in `site/content/ports/` and an entry in `PORTS` in `site/build.ts` (see `AGENTS.md`).

## Editors

These have syntax highlighting, so their generators read `SYNTAX`.

- [x] Helix: one TOML file per variant. Its highlight names are treesitter scopes and map almost one-to-one onto the `SYNTAX` roles.
- [x] Sublime Text: `.sublime-color-scheme`, from the same token rules as VS Code and bat.
- [x] Vim: classic Vimscript colorscheme, for Vim users without Lua.
- [ ] Emacs: a `deftheme` file.
- [ ] micro: `.micro` colorscheme.

## Terminals

- [ ] Warp: YAML.

## CLI and TUI tools

Each is a small file per variant, about the size of the tmux or fzf ports.

- [ ] lazygit
- [ ] btop
- [ ] yazi
- [ ] zellij: KDL.
- [ ] herdr: themes go in `config.toml` and can ship as a herdr plugin.
- [ ] starship: a `[palettes.rime]` block.
- [ ] fish: `.theme` file for `fish_config theme`.
- [ ] k9s
- [ ] vivid, for `LS_COLORS`
- [ ] gitui
- [ ] glamour, used by glow

## Linux desktop

- [ ] rofi: `.rasi`.
- [ ] dunst
- [ ] mako
- [ ] Hyprland: border and group colors.
- [ ] KDE color scheme: `.colors`.
- [ ] qutebrowser

## Apps

Mostly CSS variables, so the CSS port covers much of the work.

- [ ] Obsidian
- [ ] Discord, through Vencord or BetterDiscord
- [ ] Spicetify, for Spotify
- [ ] Firefox Color
- [ ] Telegram
