---
title: micro
description: a rime colorscheme for the micro editor.
---

# micro

a colorscheme per variant for [micro](https://micro-editor.github.io). it colors the editor, statusline, tabs, gutter and the syntax groups micro's syntax files use. tested on micro 2.0.15.

{{downloads}}

## install

```sh
mkdir -p ~/.config/micro/colorschemes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/micro/{{slug}}.micro -o ~/.config/micro/colorschemes/{{slug}}.micro
```

then press `ctrl-e` and run `set colorscheme {{slug}}`, or add it to `~/.config/micro/settings.json`:

```json
{
  "colorscheme": "{{slug}}"
}
```

## notes

- micro's syntax files put every keyword in one `statement` group, so `if`, `for` and `return` share the violet keyword color.
- the colors are hex. micro uses them as they are when your terminal has true color, and picks the nearest of 256 colors when it doesn't.
