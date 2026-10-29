---
title: vivid
description: rime colors for ls and every other program that reads LS_COLORS, through vivid.
---

# vivid

a theme for [vivid](https://github.com/sharkdp/vivid), which turns it into `LS_COLORS` for `ls`, `eza`, `fd`, `tree` and other programs that read it. directories are blue as in [neovim](/ports/neovim), readme-style files and config files yellow, source code violet, media pink, archives bold red and executables bold green. backups and lock files take the comment gray, and documents the plain text color.

{{downloads}}

## install

```sh
mkdir -p ~/.config/vivid/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/vivid/{{slug}}.yml -o ~/.config/vivid/themes/{{slug}}.yml
echo 'export LS_COLORS="$(vivid generate {{slug}})"' >> ~/.bashrc  # or ~/.zshrc
```

in fish, add this to `~/.config/fish/config.fish` instead:

```sh
set -gx LS_COLORS (vivid generate {{slug}})
```
