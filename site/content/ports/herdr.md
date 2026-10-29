---
title: herdr
description: rime for herdr, the terminal workspace for coding agents.
---

# herdr

colors for [herdr](https://herdr.dev) 0.9 or later. like the [zellij](/ports/zellij) theme, its tab bar, panels and sidebar take the darker chrome shade and the focused pane is framed blue. the file is a `[theme.custom]` table that sets every color herdr has, so it works over any built-in theme.

{{downloads}}

## install

```sh
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/herdr/{{slug}}.toml >> ~/.config/herdr/config.toml
herdr server reload-config
```

if your config already has a `[theme.custom]` table, replace it instead of appending. `herdr --help` prints where your config is.
