---
title: btop
description: rime for the btop system monitor.
---

# btop

a theme for [btop](https://github.com/aristocratos/btop). box outlines and empty meters take the editors' selection gray, cpu and process graphs go from green through yellow to red, and each memory and network meter runs from its dimmed terminal color to the bright one.

{{downloads}}

## install

```sh
mkdir -p ~/.config/btop/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/btop/{{slug}}.theme -o ~/.config/btop/themes/{{slug}}.theme
```

then pick it in btop's options menu (`o`), or set it in `~/.config/btop/btop.conf`:

```ini
color_theme = "{{slug}}"
```

set `theme_background = false` as well to keep your terminal's own background, such as a transparent one.
