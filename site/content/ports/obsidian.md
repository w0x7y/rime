---
title: obsidian
description: rime for obsidian, as a css snippet over the default theme.
---

# obsidian

a css snippet that recolors obsidian's default theme. sidebars take the darker chrome shade, notes the background, and code blocks the same [syntax roles](/docs/syntax) as the editors.

{{downloads}}

## install

```sh
cd /path/to/your/vault
mkdir -p .obsidian/snippets
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/obsidian/{{slug}}.css -o .obsidian/snippets/{{slug}}.css
```

then turn on `{{slug}}` under **settings → appearance → css snippets**, and set **base color scheme** to {{appearance}}. a snippet only colors its own mode, so a dark variant does nothing while obsidian is light.

## notes

- it works over the default theme. a community theme sets the same variables, so the result depends on which loads last.
- obsidian highlights code with prism, which gives numbers, booleans and constants one color, and keeps `if`, `for` and `return` in one keyword group.
