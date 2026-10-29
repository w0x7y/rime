---
title: gitui
description: rime for gitui, a terminal ui for git.
---

# gitui

a theme for [gitui](https://github.com/gitui-org/gitui) 0.28 or later, with the selection and focus colors of the [lazygit](/ports/lazygit) theme: blue for the focused panel's title and the current tab, the editors' selection gray for the selected line. file contents are highlighted with the [bat](/ports/bat) theme of the same name.

{{downloads}}

## install

```sh
mkdir -p ~/.config/gitui
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/gitui/{{slug}}.ron -o ~/.config/gitui/theme.ron
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/bat/{{slug}}.tmTheme -o ~/.config/gitui/{{slug}}.tmTheme
```

gitui reads `theme.ron` from its config folder. to keep several themes, save each under its own name instead and pick one when you start gitui:

```sh
gitui -t {{slug}}.ron
```

on windows the folder is `%APPDATA%\gitui`.
