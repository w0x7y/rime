---
title: mako
description: rime for the mako notification daemon.
---

# mako

colors for the [mako](https://github.com/emersion/mako) notification daemon, the same as the [dunst](/ports/dunst) port: the editors' popup shade, framed blue, gray when low and red when critical.

{{downloads}}

## install

```sh
mkdir -p ~/.config/mako
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/mako/{{slug}} -o ~/.config/mako/{{slug}}
```

then add the include as the first line of `~/.config/mako/config`, before any `[section]`, and run `makoctl reload`:

```ini
include=~/.config/mako/{{slug}}
```
