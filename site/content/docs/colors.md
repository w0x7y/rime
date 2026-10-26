---
title: colors
description: rime's 16 color names, their base16 slots and the shades made from them, for every variant.
---

# colors

every variant is 16 colors, the base16 slots `base00` to `base0F`. rime gives each slot a color name, and every port, syntax role and shade is built from those names.

{{colors}}

`bg_dark` and `border` are derived shades, blends of the color names. `bg_dark` is the chrome: sidebars and bars. it's darker than `bg` on the dark variants and lighter on rime frost, so hovers still show.

glacier has a lighter background (`bg`), and aurora and abyss darker ones. glacier's `comment` is a little lighter too, so comments stay readable on it.

neovim's `on_colors` gets the same names, plus more derived shades: `colorcolumn`, `whitespace`, `search`, the diff backgrounds `diff_add`, `diff_change`, `diff_text` and `diff_delete`, and the diagnostic backgrounds `diag_error`, `diag_warn`, `diag_info`, `diag_hint` and `diag_ok`. those extra shades are the plugin's own, though [delta](/ports/delta) blends its removed and added lines the same way as `diff_delete` and `diff_add`. `bg_dark` and `border` are the only named shades the other ports use, and the plugin blends them the same way `tools/build.py` does, so they match in every port.

## terminal colors

the dark variants give terminals these 16 colors:

| slot | color | slot | color |
| --- | --- | --- | --- |
| 0 black | selection gray (`base02`) | 8 bright black | comment gray (`base03`) |
| 1 red | rose | 9 bright red | lighter rose |
| 2 green | green | 10 bright green | lighter green |
| 3 yellow | yellow (pale aqua in abyss) | 11 bright yellow | lighter yellow |
| 4 blue | blue | 12 bright blue | lighter blue |
| 5 magenta | violet | 13 bright magenta | lighter violet |
| 6 cyan | cyan | 14 bright cyan | lighter cyan |
| 7 white | text (`base05`) | 15 bright white | `base07` |

black is a visible dark gray rather than the background, so programs that print black text stay readable.

rime frost keeps black dark and white light, as most light terminal themes do: black is the text color (`base05`), white a readable gray (`base03`), bright black `base04` and bright white a lighter gray. its bright accents are darker than the normal ones rather than lighter, so they stand out on the light background.

## in your own code

- the [css port](/ports/css) has every name as a custom property, such as `--rime-blue`.
- in neovim, `require("rime").colors("glacier")` returns them as a table.
- the [base16 port](/ports/base16) has the 16 slots for any base16 template.
