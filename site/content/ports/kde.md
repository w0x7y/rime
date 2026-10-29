---
title: kde plasma
description: rime color schemes for kde plasma and its apps.
---

# kde plasma

a color scheme for kde plasma and the qt and kde apps that follow it. lists and text areas take the editors' background, window chrome and title bars the darker sidebar shade, and buttons and tooltips the popup shade. the selection is blue, and plasma uses it as the accent color too.

{{downloads}}

## install

```sh
mkdir -p ~/.local/share/color-schemes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/kde/{{slug}}.colors -o ~/.local/share/color-schemes/{{slug}}.colors
plasma-apply-colorscheme {{slug}}
```

or pick it under **system settings → colors & themes → colors**, where **install from file** works too. keep the accent color on **from current color scheme** to get rime's blue.
