# Port ideas

Programs Rime could be ported to, best value first in each section. Tick an item once its port ships. Adding a port means a generator in `tools/build.py`, a page in `site/content/ports/` and an entry in `PORTS` in `site/build.ts` (see `AGENTS.md`).

## Editors

All shipped. Each reads `SYNTAX`, so code gets the same colors as in Neovim, Zed and VS Code.

- [x] Helix: `general/helix/`, a TOML theme per variant.
- [x] Sublime Text: `general/sublime/`, a `.sublime-color-scheme` from the same token rules as VS Code and bat.
- [x] Vim: `vim/colors/`, Vimscript with 256-color fallbacks. Kept out of `colors/` so Neovim still loads the Lua plugin.
- [x] micro: `general/micro/`, a `.micro` colorscheme.
- [x] Emacs: `general/emacs/`, a `deftheme` per variant.

## Terminals

All shipped.

- [x] Warp: `general/warp/`, a YAML theme per variant.

## CLI and TUI tools

All shipped. Each is a small file per variant, about the size of the tmux or fzf ports; yazi's is a folder.

- [x] lazygit: `general/lazygit/`, a config file to list in `LG_CONFIG_FILE`.
- [x] btop: `general/btop/`, a `.theme` file.
- [x] yazi: `general/yazi/`, a flavor folder per variant, with the bat theme for previews.
- [x] zellij: `general/zellij/`, a KDL theme for zellij 0.42+.
- [x] herdr: `general/herdr/`, a `[theme.custom]` table for `config.toml`. Plugins can't carry themes, as of 0.9.5.
- [x] starship: `general/starship/`, a `[palettes.<variant>]` block.
- [x] fish: `general/fish/`, a `.theme` file for `fish_config theme`. The command line reads `SYNTAX`.
- [x] k9s: `general/k9s/`, a skin. Resource YAML reads `SYNTAX`.
- [x] vivid: `general/vivid/`, a theme that `vivid generate` turns into `LS_COLORS`.
- [x] gitui: `general/gitui/`, a `theme.ron` that highlights files with the bat theme.
- [x] glamour: `general/glamour/`, a style for glow and gh. Code blocks read `SYNTAX`.

## Linux desktop

All shipped.

- [x] rofi: `general/rofi/`, a `.rasi` that recolors rofi's default layout, for rofi 1.7+.
- [x] dunst: `general/dunst/`, a `dunstrc.d` drop-in.
- [x] mako: `general/mako/`, a config to `include`.
- [x] Hyprland: `general/hyprland/`, a Lua module with border and group colors, for Hyprland 0.55+.
- [x] KDE color scheme: `general/kde/`, a `.colors` file for Plasma and its apps.
- [x] qutebrowser: `general/qutebrowser/`, a config file to `config.source()`.

## Apps

All shipped.

- [x] Obsidian: `general/obsidian/`, a CSS snippet per variant over the default theme. Code blocks read `SYNTAX`.
- [x] Discord: `general/discord/`, a `.theme.css` per variant for BetterDiscord and Vencord.
- [x] Spicetify: `general/spicetify/color.ini`, every variant as a color scheme of one theme.
- [x] Firefox Color: `general/firefox/`, a page per variant that opens it in Firefox Color.
- [x] Telegram: `general/telegram/`, a Telegram Desktop `.tdesktop-palette` per variant.
