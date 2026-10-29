---
title: rofi
description: rime for the rofi launcher.
---

# rofi

a theme for [rofi](https://github.com/davatorium/rofi) 1.7 or later. it keeps rofi's default layout and changes only the colors: the window takes the editors' popup shade and a blue frame, like the [dunst](/ports/dunst) and [mako](/ports/mako) notifications, the selected entry takes the selection gray, and matched letters are bold blue.

{{downloads}}

## install

```sh
mkdir -p ~/.config/rofi/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/rofi/{{slug}}.rasi -o ~/.config/rofi/themes/{{slug}}.rasi
echo '@theme "{{slug}}"' >> ~/.config/rofi/config.rasi
```

`@theme` drops any theme loaded before it, so keep your own tweaks below that line. to try it without changing your config:

```sh
rofi -show drun -theme {{slug}}
```

`rofi-theme-selector` lists it too.
