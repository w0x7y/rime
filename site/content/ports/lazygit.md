---
title: lazygit
description: rime for lazygit, the git tui.
---

# lazygit

a theme for [lazygit](https://github.com/jesseduffield/lazygit): blue for the focused panel, the editors' selection gray for the selected line, yellow while searching.

{{downloads}}

## install

lazygit reads several config files from `LG_CONFIG_FILE`, so the theme stays out of yours:

```sh
mkdir -p ~/.config/lazygit
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/lazygit/{{slug}}.yml -o ~/.config/lazygit/{{slug}}.yml
export LG_CONFIG_FILE="$HOME/.config/lazygit/config.yml,$HOME/.config/lazygit/{{slug}}.yml"
```

put the `export` in your shell's startup file. on macos the config folder is `~/Library/Application Support/lazygit` unless `XDG_CONFIG_HOME` is set.
