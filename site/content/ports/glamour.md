---
title: glamour
description: rime for markdown in glow and gh, through a glamour style.
---

# glamour

a [glamour](https://github.com/charmbracelet/glamour) style, for markdown in [glow](https://github.com/charmbracelet/glow) and in `gh`'s issues, pull requests and readmes. headings, links, quotes and inline code take the editors' markdown colors, and code blocks follow the [syntax roles](/docs/syntax) of the editor ports.

{{downloads}}

## install

```sh
mkdir -p ~/.config/glow
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/glamour/{{slug}}.json -o ~/.config/glow/{{slug}}.json
glow -s ~/.config/glow/{{slug}}.json README.md
```

## make it the default

for glow, run `glow config` and set `style:` to the file's full path. glow doesn't expand `~` in its config:

```yaml
style: "/home/you/.config/glow/{{slug}}.json"
```

for `gh`, set `GLAMOUR_STYLE` in your shell's startup file:

```sh
export GLAMOUR_STYLE="$HOME/.config/glow/{{slug}}.json"
```

glow draws code blocks in the nearest of the 256 terminal colors, so they come out slightly off.
