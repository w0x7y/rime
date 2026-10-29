# Rime for terminals and everything else

Every file here comes in five variants (`rime`, `rime-glacier`, `rime-aurora`, `rime-abyss` and the light `rime-frost`). The examples use `rime`. Swap in the variant you want. Run the commands from this `general/` folder.

All files are generated from `palettes/` by `tools/build.py`, so edit the palettes rather than these files.

## Terminal colors

The dark variants use these 16 colors:

| Slot      | Color                       | Slot              | Color                   |
| --------- | --------------------------- | ----------------- | ----------------------- |
| 0 black   | selection gray (`base02`)   | 8 bright black    | comment gray (`base03`) |
| 1 red     | rose                        | 9 bright red      | lighter rose            |
| 2 green   | green                       | 10 bright green   | lighter green           |
| 3 yellow  | yellow (pale aqua in Abyss) | 11 bright yellow  | lighter yellow          |
| 4 blue    | blue                        | 12 bright blue    | lighter blue            |
| 5 magenta | violet                      | 13 bright magenta | lighter violet          |
| 6 cyan    | cyan                        | 14 bright cyan    | lighter cyan            |
| 7 white   | text (`base05`)             | 15 bright white   | `base07`                |

Black is a visible dark gray rather than the background color, so programs that print black text stay readable.

Rime Frost keeps black dark and white light, as most light terminal themes do: black is the text color (`base05`), white a readable gray (`base03`), bright black `base04` and bright white a lighter gray. Its bright accents are darker than the normal ones rather than lighter, so they stand out on the light background.

### kitty

```sh
mkdir -p ~/.config/kitty
cp kitty/rime.conf ~/.config/kitty/rime.conf
echo 'include rime.conf' >> ~/.config/kitty/kitty.conf
```

### Alacritty

```sh
mkdir -p ~/.config/alacritty/themes
cp alacritty/rime.toml ~/.config/alacritty/themes/
```

```toml
# alacritty.toml
[general]
import = ["~/.config/alacritty/themes/rime.toml"]
```

Before Alacritty 0.14, `import` was a top-level key instead of living under `[general]`.

### Ghostty

```sh
mkdir -p ~/.config/ghostty/themes
cp ghostty/rime ~/.config/ghostty/themes/
echo 'theme = rime' >> ~/.config/ghostty/config
```

### WezTerm

```sh
mkdir -p ~/.config/wezterm/colors
cp wezterm/rime.toml ~/.config/wezterm/colors/
```

```lua
-- wezterm.lua
config.color_scheme = "Rime"  -- or "Rime Glacier", "Rime Aurora", "Rime Abyss", "Rime Frost"
```

### foot

```sh
cp foot/rime.ini ~/.config/foot/rime.ini
```

```ini
# foot.ini
[main]
include=~/.config/foot/rime.ini
```

The files use foot 1.26's `[colors-dark]` section, or `[colors-light]` for Rime Frost. On older foot versions, rename it to `[colors]`.

### Windows Terminal

Open **Settings → Open JSON file** and add the entries from `windows-terminal/rime.json` to the `"schemes"` array. Then pick the scheme under your profile's **Appearance** settings.

### iTerm2

Double-click `iterm2/rime.itermcolors` to import it. Then select it in **Settings → Profiles → Colors → Color Presets**.

### Warp

```sh
mkdir -p ~/.warp/themes  # macOS; ~/.local/share/warp-terminal/themes on Linux, %LOCALAPPDATA%\warp\Warp\data\themes on Windows
cp warp/rime.yaml ~/.warp/themes/
```

Then pick Rime in **Settings → Appearance → Themes**. Warp shades its own tabs and blocks from the background and the blue accent.

### Xresources (xterm, urxvt, st and others)

```sh
xrdb -merge xresources/rime.Xresources
```

## Noctalia

For the [Noctalia](https://github.com/noctalia-dev/noctalia) desktop shell, version 5 or later:

```sh
mkdir -p ~/.config/noctalia/palettes
cp noctalia/rime.json ~/.config/noctalia/palettes/
```

```toml
# ~/.config/noctalia/config.toml, or any .toml file in that folder
[theme]
mode           = "dark"
source         = "custom"
custom_palette = "rime"  # or "rime-glacier", "rime-aurora", "rime-abyss", "rime-frost"
```

You can also pick the palette in Noctalia's settings after choosing the custom source, or run `noctalia msg color-scheme-set custom rime`.

The shell takes its colors from Rime's Zed and VS Code themes. The bar and panels use the editors' background, cards use their popup background, and hovered items use the gray of their list selection. Blue is the primary accent, violet the secondary and cyan the tertiary. Its terminal colors are the 16 above, and Noctalia's terminal templates (kitty, foot, Ghostty, Alacritty and others) pass them on.

Each palette holds one variant, so Noctalia uses the same colors in light and dark mode. With a dark variant, keep `mode = "dark"` so the apps Noctalia themes stay dark as well; with `rime-frost`, set `mode = "light"`.

Noctalia 4 called these color schemes and read the same file from `~/.config/noctalia/colorschemes/rime/rime.json`.

## tmux

For tmux 3.2 or later. It colors the status bar, pane borders, messages, copy mode and popups; the text in panes keeps your terminal's colors.

```sh
mkdir -p ~/.config/tmux
cp tmux/rime.conf ~/.config/tmux/rime.conf
echo 'source-file ~/.config/tmux/rime.conf' >> ~/.config/tmux/tmux.conf
```

If your config is `~/.tmux.conf`, add the line there instead.

## zellij

A theme per variant for zellij 0.42 or later. The tab bar and status bar take the darker chrome shade, as in tmux. The focused tab, the current mode and the focused pane's frame are blue, and the frame turns yellow while you're in a mode such as `PANE` or `TAB`.

```sh
mkdir -p ~/.config/zellij/themes
cp zellij/rime.kdl ~/.config/zellij/themes/
echo 'theme "rime"' >> ~/.config/zellij/config.kdl
```

To follow the terminal's dark or light mode, set both `theme_dark "rime"` and `theme_light "rime-frost"` instead (zellij 0.45 or later).

## Helix

A theme per variant, with the same syntax roles as Neovim, Zed and VS Code. Helix names a theme after its file, so this one is `rime`.

```sh
mkdir -p ~/.config/helix/themes
cp helix/rime.toml ~/.config/helix/themes/
```

Then run `:theme rime`, or put `theme = "rime"` at the top of `~/.config/helix/config.toml`.

Helix gives struct fields and JSON, YAML and TOML keys one scope, so keys are plain text, as in Zed. HTML attributes share the `attribute` scope with decorators.

## Emacs

A theme per variant for Emacs 28 and later.

```sh
mkdir -p ~/.emacs.d/themes
cp emacs/rime-theme.el ~/.emacs.d/themes/
```

```elisp
;; init.el
(add-to-list 'custom-theme-load-path "~/.emacs.d/themes")
(load-theme 'rime t)
```

Emacs has one keyword face, so `if`, `for` and `return` share the keyword color.

## micro

A colorscheme per variant for [micro](https://micro-editor.github.io).

```sh
mkdir -p ~/.config/micro/colorschemes
cp micro/rime.micro ~/.config/micro/colorschemes/
```

Then press `Ctrl-e` and run `set colorscheme rime`, or set `"colorscheme": "rime"` in `~/.config/micro/settings.json`. micro's syntax files put every keyword in one `statement` group, so `if`, `for` and `return` share the keyword color.

## Sublime Text

A color scheme per variant for Sublime Text 4, with the same token colors as the VS Code theme. On Linux:

```sh
mkdir -p ~/.config/sublime-text/Packages/User
cp sublime/rime.sublime-color-scheme ~/.config/sublime-text/Packages/User/
```

On macOS the folder is `~/Library/Application Support/Sublime Text/Packages/User`. Then run `UI: Select Color Scheme`, or set `"color_scheme": "rime.sublime-color-scheme"` in your preferences. Sublime Text has no strikethrough, so deprecated code keeps its color without the line.

## bat

A syntax theme for [bat](https://github.com/sharkdp/bat), with the same token colors as the VS Code theme. bat names a theme after its file, so this one is `rime`.

```sh
mkdir -p "$(bat --config-dir)/themes"
cp bat/rime.tmTheme "$(bat --config-dir)/themes/"
bat cache --build
echo '--theme="rime"' >> "$(bat --config-file)"
```

Comments are italic, which bat only shows with `--italic-text=always`.

## delta

For [delta](https://github.com/dandavison/delta), the git diff pager. delta highlights code with a syntax theme from bat's cache, so it needs the bat theme above; its file here adds the diff colors and names that theme.

Install both. On macOS:

```sh
brew install git-delta bat
```

On Arch:

```sh
sudo pacman -S git-delta bat
```

Then put the theme in bat's cache and include the delta file:

```sh
mkdir -p "$(bat --config-dir)/themes"
cp bat/rime.tmTheme "$(bat --config-dir)/themes/"
bat cache --build

mkdir -p ~/.config/delta
cp delta/rime.gitconfig ~/.config/delta/
git config --global --add include.path ~/.config/delta/rime.gitconfig
git config --global core.pager delta
git config --global interactive.diffFilter 'delta --color-only'
git config --global delta.features rime
```

Each file is a delta feature named after its variant. If you already use features, list them together: `git config --global delta.features "rime side-by-side"`.

It sets colors only: the backgrounds of removed and added lines and of the words that changed, the file and hunk headers, line numbers (with `delta.line-numbers true`) and the alternating backgrounds of `git blame`. Your terminal needs 24-bit color. delta assumes it when `COLORTERM` is `truecolor` or `24bit`; otherwise set `delta.true-color always`.

If delta warns `Unknown theme 'rime'`, the theme isn't in bat's cache: run `bat cache --build` again. delta reads the cache from bat's default place, so it won't find one you moved with `BAT_CACHE_PATH`.

## Obsidian

A CSS snippet per variant that recolors Obsidian's default theme. Code blocks follow the same syntax roles as the editor ports.

```sh
cp obsidian/rime.css /path/to/vault/.obsidian/snippets/
```

Then turn on `rime` under **Settings → Appearance → CSS snippets**. A snippet only applies in its own mode, so set **Base color scheme** to dark for the dark variants and to light for `rime-frost`.

## Discord

A theme per variant for [BetterDiscord](https://betterdiscord.app) or [Vencord](https://vencord.dev). Copy `discord/rime.theme.css` into the themes folder (**Settings → Themes → Open Themes Folder** in either), then turn it on there.

It colors Discord's dark modes (dark, darker and midnight); `rime-frost` colors light mode. Discord renames its color variables now and then, so a Discord update can leave parts of the app in its own colors until the theme catches up.

## Spicetify

All five variants as color schemes of one [Spicetify](https://spicetify.app) theme, for Spotify.

```sh
mkdir -p "$(dirname "$(spicetify -c)")/Themes/Rime"
cp spicetify/color.ini "$(dirname "$(spicetify -c)")/Themes/Rime/"
spicetify config current_theme Rime color_scheme rime inject_css 0 replace_colors 1
spicetify apply
```

The schemes are named after the variants: `rime`, `rime-glacier`, `rime-aurora`, `rime-abyss` and `rime-frost`.

## Firefox Color

Open `firefox/rime.html` in Firefox. It sends you to [Firefox Color](https://color.firefox.com) with Rime loaded; install the Firefox Color extension when it asks, and the theme applies. Save it there to keep it.

The tab strip and sidebars use the darker chrome shade, the selected tab and toolbar the background, and the address bar and menus the popup shade, as in the GUI editors.

## Telegram

A palette per variant for Telegram Desktop. Send `telegram/rime.tdesktop-palette` to your Saved Messages and click it, or pick it with **Settings → Chat Settings → Chat background → Choose from file**. Telegram shows a preview; apply it from there.

A palette has no chat background, so Telegram keeps your current wallpaper. For a plain one, open **Chat background** and pick the solid color closest to the theme's background.

## fish

A theme per variant for fish's `fish_config theme`. The command line follows the same syntax roles as the editor ports.

```sh
mkdir -p ~/.config/fish/themes
cp fish/rime.theme ~/.config/fish/themes/
fish_config theme choose rime
```

`choose` applies it to the current session; add the same line to `config.fish` to keep it. fish has one color for every keyword, so `if`, `for` and `return` share it.

## starship

A [starship](https://starship.rs) palette per variant. Starship's modules name terminal colors (`blue`, `bold green`), so the palette sets those to the 16 terminal colors above. It also adds the color names (`bg`, `fg`, `comment`, `pink`, `steel` and the rest) for your own styles.

```sh
cat starship/rime.toml >> ~/.config/starship.toml
```

Then put `palette = "rime"` near the top of `starship.toml`, before any `[section]`.

## lazygit

A [lazygit](https://github.com/jesseduffield/lazygit) theme per variant, as a config file that lazygit reads after yours.

```sh
cp lazygit/rime.yml ~/.config/lazygit/rime.yml
export LG_CONFIG_FILE="$HOME/.config/lazygit/config.yml,$HOME/.config/lazygit/rime.yml"
```

Put the `export` in your shell's startup file. On macOS lazygit's config folder is `~/Library/Application Support/lazygit` unless `XDG_CONFIG_HOME` is set.

## dunst

A drop-in per variant for the [dunst](https://dunst-project.org) notification daemon, version 1.9 or later. Notifications take the popup shade, framed blue, gray when low and red when critical.

```sh
mkdir -p ~/.config/dunst/dunstrc.d
cp dunst/rime.conf ~/.config/dunst/dunstrc.d/
dunstctl reload
```

## mako

The same notifications for [mako](https://github.com/emersion/mako).

```sh
cp mako/rime ~/.config/mako/rime
```

Add `include=~/.config/mako/rime` as the first line of `~/.config/mako/config`, before any `[section]`, then run `makoctl reload`.

## Hyprland

A Lua module per variant for Hyprland 0.55 or later, which reads `hyprland.lua`. It colors window borders, groups and the groupbar: the focused window and group in blue, locked groups in yellow.

```sh
cp hyprland/rime.lua ~/.config/hypr/rime.lua
echo 'require("rime")' >> ~/.config/hypr/hyprland.lua
```

Put the `require` after your own `hl.config` calls; the last value set wins.

## Other formats

| Folder    | Use                                                                                                                                                                             |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `base16/` | base16 scheme files in the [tinted-theming](https://github.com/tinted-theming/home) format. Feed them to a builder such as `tinty` to theme any app that has a base16 template. |
| `css/`    | CSS custom properties, with both the base16 slots (`--base0D`) and color names (`--rime-blue`).                                                                                 |
| `fzf/`    | `source fzf/rime.sh` to add Rime colors to `FZF_DEFAULT_OPTS`.                                                                                                                  |
