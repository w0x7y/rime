---
title: fish
description: rime for the fish shell's command line and completion pager.
---

# fish

a theme for fish's `fish_config theme`. the command line follows the same [syntax roles](/docs/syntax) as the editors: commands blue, keywords violet, strings green, comments italic gray. the completion pager selects in the editors' selection gray.

{{downloads}}

## install

```sh
mkdir -p ~/.config/fish/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/fish/{{slug}}.theme -o ~/.config/fish/themes/{{slug}}.theme
fish_config theme choose {{slug}}
```

`choose` applies it to the current session. add the same line to `~/.config/fish/config.fish` to keep it.

## notes

- fish has one color for every keyword, so `if`, `for` and `return` share it.
