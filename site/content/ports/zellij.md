---
title: zellij
description: rime for the zellij terminal multiplexer.
---

# zellij

a theme for [zellij](https://zellij.dev) 0.42 or later. the tab bar and status bar take the darker chrome shade, as in [tmux](/ports/tmux). the focused tab, the current mode and the focused pane's frame are blue, and the frame turns yellow while you're in a mode such as `PANE` or `TAB`. the text inside panes keeps your terminal's colors, so pair it with a terminal port.

{{downloads}}

## install

```sh
mkdir -p ~/.config/zellij/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/zellij/{{slug}}.kdl -o ~/.config/zellij/themes/{{slug}}.kdl
echo 'theme "{{slug}}"' >> ~/.config/zellij/config.kdl
```

zellij picks up changes to the themes folder without a restart. `zellij setup --check` prints where your config folder is if it isn't `~/.config/zellij`.

## dark and light

zellij 0.45 can switch themes when the terminal switches between dark and light. set both instead of `theme`:

```kdl
theme_dark "rime"
theme_light "rime-frost"
```

download both files first.
