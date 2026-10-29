---
title: dunst
description: rime for the dunst notification daemon.
---

# dunst

a drop-in for the [dunst](https://dunst-project.org) notification daemon, version 1.9 or later. notifications take the editors' popup shade, framed blue, gray when low and red when critical.

{{downloads}}

## install

```sh
mkdir -p ~/.config/dunst/dunstrc.d
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/dunst/{{slug}}.conf -o ~/.config/dunst/dunstrc.d/{{slug}}.conf
dunstctl reload
```

dunst reads every `.conf` in `dunstrc.d` after `dunstrc`, so the colors win over any in your config.
