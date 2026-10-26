**Rime**

a colder colorscheme. [website](https://w0x7y.dev/rime/)

<img width="370" alt="rust code in rime" src="assets/demo.png" />

the opposite of [bark](https://github.com/if-not-nil/bark), with a little [one dark pro](https://github.com/Binaryify/OneDark-Pro) mixed in

**variants**

- **rime**: soft and muted pastels.

    ![rime palette](assets/palette-rime.svg)

- **rime glacier**: crisper accents that keep every syntax role apart, on a lighter background.

    ![rime glacier palette](assets/palette-rime-glacier.svg)

- **rime aurora**: vivid neon on a darker background.

    ![rime aurora palette](assets/palette-rime-aurora.svg)

- **rime abyss**: the coldest one, on a darker background.

    ![rime abyss palette](assets/palette-rime-abyss.svg)

- **rime frost**: the light one, the same cold accents deepened to read on frost white.

    ![rime frost palette](assets/palette-rime-frost.svg)

<img alt="all five variants" src="assets/screenshot-all.png" />

**[neovim](./nvim)**

with lazy.nvim

```lua
{
  "w0x7y/rime",
  lazy = false,
  priority = 1000,
  config = function()
    vim.cmd.colorscheme("rime")
  end,
}
```

then `:colorscheme rime`, `rime-glacier`, `rime-aurora`, `rime-abyss` or `rime-frost`. other plugin managers, options and lualine are in [nvim/](./nvim)

**[zed](./zed)**

put `zed/themes/rime.json` into `~/.config/zed/themes/`, or run `zed: install dev extension` and pick the `zed/` folder. then choose a rime variant in the theme selector

zed puts `if`, `for` and `return` in one group, so there they share a color

**[vscode](./vscode)**

search for **rime theme** in the extensions view, or run

```sh
code --install-extension w0x7y.rime-theme
```

it's on the [vs code marketplace](https://marketplace.visualstudio.com/items?itemName=w0x7y.rime-theme), and on [open vsx](https://open-vsx.org/extension/w0x7y/rime-theme) for vscodium, cursor and other forks. then `Preferences: Color Theme` and pick a rime variant. building it from source is in [vscode/](./vscode)

**[helix](./general#helix)**

put `general/helix/rime.toml` into `~/.config/helix/themes/`, then `:theme rime` or `theme = "rime"` in your helix config

**[sublime text](./general#sublime-text)**

put `general/sublime/rime.sublime-color-scheme` into your `Packages/User` folder, then `UI: Select Color Scheme`

**[base16](./general/base16)**

the same 16 colors per variant. there's a base16 template for almost any software, so you can feed these to a builder like tinty

- [tinted-theming](https://github.com/tinted-theming/home) is a good place to find templates and builders

**[terminals and the rest](./general)**

kitty, alacritty, ghostty, wezterm, foot, windows terminal, iterm2, xresources, the noctalia shell, tmux, bat, delta, css variables and fzf

for kitty, put `general/kitty/rime.conf` into `~/.config/kitty/rime.conf`, then add `include rime.conf` to your kitty config. install a Noctalia palette from `general/noctalia/` with the [setup instructions](./general#noctalia); the others are explained in [general/](./general)

**[changing colors](./palettes)**

every variant is 16 colors in `palettes/`. which color each kind of code gets (functions, keywords, comments) is the `SYNTAX` table in `tools/build.py`, shared by the editor ports. edit either and run `python3 tools/build.py`. it rewrites the neovim, zed, vscode and terminal files and the website's data with only the python standard library

`python3 tools/build.py --check` lists anything out of date or no longer generated, and `python3 -m unittest discover -s tools` runs the tests. the screenshots and the vscode icon png come from `python3 tools/screenshots/render.py`

**[website](./site)**

the site at [w0x7y.dev/rime](https://w0x7y.dev/rime/) is built from `site/` and deployed from `main`. how to run it is in [site/](./site)

**[your own](https://github.com/w0x7y/rime/pulls)**

if you port it into your software of choice, open a pull request. the [porting guide](https://w0x7y.dev/rime/docs/porting/) shows how ports are made

_credits: [bark](https://github.com/if-not-nil/bark) by if-not-nil, the warm scheme rime flips around. license: [mit](./LICENSE)_
