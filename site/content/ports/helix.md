---
title: helix
description: a rime theme for helix, with the same syntax roles as neovim, zed and vs code.
---

# helix

a theme file per variant. it colors the editor, pickers, popups, statusline, diagnostics and the tree-sitter scopes, with the same [syntax roles](/docs/syntax) as the other editors. tested on helix 25.07.

{{downloads}}

## install

```sh
mkdir -p ~/.config/helix/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/helix/{{slug}}.toml -o ~/.config/helix/themes/{{slug}}.toml
```

helix names a theme after its file. pick it with `:theme {{slug}}`, or set it at the top of `~/.config/helix/config.toml`:

```toml
theme = "{{slug}}"
```

to follow the terminal's light and dark mode:

```toml
[theme]
dark = "rime"
light = "rime-frost"
```

## notes

- helix gives struct fields and the keys in json, yaml and toml one scope, so keys are plain text, as in zed.
- html attributes share the `attribute` scope with decorators, so they're teal instead of yellow.
- the statusline colors its mode the way rime's lualine theme does when `editor.color-modes` is on.
