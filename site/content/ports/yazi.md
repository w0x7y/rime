---
title: yazi
description: rime flavors for the yazi file manager.
---

# yazi

a flavor for the [yazi](https://yazi-rs.github.io) file manager, version 26.8 or later. modes and tabs look like the [neovim](/ports/neovim) statusline, popups are framed blue, the hovered file sits on the selection gray, and files take the colors of the [vivid](/ports/vivid) theme. each flavor carries the [bat](/ports/bat) theme as `tmtheme.xml`, so previews highlight code the same way.

{{downloads}}

## install

a flavor is a folder holding both files:

```sh
mkdir -p ~/.config/yazi/flavors/{{slug}}.yazi
cd ~/.config/yazi/flavors/{{slug}}.yazi
curl -fsSLO https://raw.githubusercontent.com/w0x7y/rime/main/general/yazi/{{slug}}.yazi/flavor.toml
curl -fsSLO https://raw.githubusercontent.com/w0x7y/rime/main/general/yazi/{{slug}}.yazi/tmtheme.xml
```

then pick it in `~/.config/yazi/theme.toml`. yazi asks the terminal whether it's dark or light, so install a dark variant and frost and give it one of each:

```toml
[flavor]
dark = "rime"
light = "rime-frost"
```

anything else in `theme.toml` overrides the flavor.
