---
title: k9s
description: rime for k9s, the kubernetes terminal ui.
---

# k9s

a skin for [k9s](https://k9scli.io). frames and the table cursor match the other ports: gray borders with a blue one around the focused view, and the editors' selection gray under the cursor. resource yaml takes the editors' [syntax colors](/docs/syntax) for keys and strings.

{{downloads}}

## install

```sh
mkdir -p ~/.config/k9s/skins
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/k9s/{{slug}}.yaml -o ~/.config/k9s/skins/{{slug}}.yaml
```

then set it in `~/.config/k9s/config.yaml`:

```yaml
k9s:
  ui:
    skin: {{slug}}
```

or try it for one session:

```sh
K9S_SKIN={{slug}} k9s
```

on macos the config folder is `~/Library/Application Support/k9s` unless `XDG_CONFIG_HOME` is set; `k9s info` prints it.
