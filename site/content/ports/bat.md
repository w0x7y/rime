---
title: bat
description: a rime syntax theme for bat, which delta uses too.
---

# bat

a syntax theme for [bat](https://github.com/sharkdp/bat), with the same token colors as the vs code theme. [delta](/ports/delta) highlights diffs with it too.

{{downloads}}

## install

```sh
mkdir -p "$(bat --config-dir)/themes"
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/bat/{{slug}}.tmTheme -o "$(bat --config-dir)/themes/{{slug}}.tmTheme"
bat cache --build
echo '--theme="{{slug}}"' >> "$(bat --config-file)"
```

bat names a theme after its file, so keep the file name. comments are italic, which bat only shows with `--italic-text=always`.
