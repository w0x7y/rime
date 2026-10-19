---
title: tmux
description: rime for tmux's status bar, pane borders and copy mode.
---

# tmux

colors for the status bar, pane borders, messages, copy mode and popups. the text inside panes keeps your terminal's colors, so pair it with a terminal port. it needs tmux 3.2 or later.

{{downloads}}

## install

```sh
mkdir -p ~/.config/tmux
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/tmux/{{slug}}.conf -o ~/.config/tmux/{{slug}}.conf
echo 'source-file ~/.config/tmux/{{slug}}.conf' >> ~/.config/tmux/tmux.conf
```

if your config is `~/.tmux.conf`, append the line there instead. then reload it with `tmux source-file ~/.config/tmux/tmux.conf`, or restart tmux.
