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

## Helix

A theme per variant, with the same syntax roles as Neovim, Zed and VS Code. Helix names a theme after its file, so this one is `rime`.

```sh
mkdir -p ~/.config/helix/themes
cp helix/rime.toml ~/.config/helix/themes/
```

Then run `:theme rime`, or put `theme = "rime"` at the top of `~/.config/helix/config.toml`.

Helix gives struct fields and JSON, YAML and TOML keys one scope, so keys are plain text, as in Zed. HTML attributes share the `attribute` scope with decorators.

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

## Other formats

| Folder    | Use                                                                                                                                                                             |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `base16/` | base16 scheme files in the [tinted-theming](https://github.com/tinted-theming/home) format. Feed them to a builder such as `tinty` to theme any app that has a base16 template. |
| `css/`    | CSS custom properties, with both the base16 slots (`--base0D`) and color names (`--rime-blue`).                                                                                 |
| `fzf/`    | `source fzf/rime.sh` to add Rime colors to `FZF_DEFAULT_OPTS`.                                                                                                                  |
