---
title: starship
description: rime for the starship prompt, as a palette.
---

# starship

a [starship](https://starship.rs) palette. starship's modules name terminal colors (`blue`, `bold green`), so the palette sets those to the [16 terminal colors](/docs/colors#terminal-colors) and your prompt keeps its layout. it also adds the [color names](/docs/colors) (`bg`, `fg`, `comment`, `pink`, `steel` and the rest) for your own styles.

{{downloads}}

## install

```sh
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/starship/{{slug}}.toml >> ~/.config/starship.toml
```

then turn the palette on near the top of `starship.toml`, before any `[section]`:

```toml
palette = "{{slug}}"
```

## notes

- with a rime terminal port the standard names already show rime's colors. the palette matters in a terminal with other colors, and for the color names.
- `white` is the terminal white, so the palette leaves out the color name of the same name.
