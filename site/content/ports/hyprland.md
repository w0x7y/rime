---
title: hyprland
description: rime for hyprland's window borders and groups.
---

# hyprland

a lua module for [hyprland](https://hypr.land) 0.55 or later, which reads `hyprland.lua`. it colors window borders, groups and the groupbar: the focused window and group in blue, the rest in the editors' selection gray, locked groups in yellow.

{{downloads}}

## install

```sh
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/hyprland/{{slug}}.lua -o ~/.config/hypr/{{slug}}.lua
echo 'require("{{slug}}")' >> ~/.config/hypr/hyprland.lua
```

put the `require` after your own `hl.config` calls, since the last value set wins. hyprland reloads the config on its own.

## notes

- older versions and configs still on `hyprland.conf` can't load it.
- it sets the background color behind the wallpaper too, which shows only with `misc.disable_hyprland_logo`.
