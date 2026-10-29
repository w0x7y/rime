---
title: warp
description: rime for the warp terminal.
---

# warp

a theme file for [warp](https://www.warp.dev), with the [16 terminal colors](/docs/colors#terminal-colors) the other terminal ports use. warp shades its own tabs and blocks from the background and the blue accent.

{{downloads}}

## install

on macos:

```sh
mkdir -p ~/.warp/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/warp/{{slug}}.yaml -o ~/.warp/themes/{{slug}}.yaml
```

on linux:

```sh
mkdir -p ~/.local/share/warp-terminal/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/warp/{{slug}}.yaml -o ~/.local/share/warp-terminal/themes/{{slug}}.yaml
```

on windows the folder is `%LOCALAPPDATA%\warp\Warp\data\themes`. then pick {{name}} in **settings → appearance → themes**.
