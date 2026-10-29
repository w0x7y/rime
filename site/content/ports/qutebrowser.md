---
title: qutebrowser
description: rime for qutebrowser, the keyboard-driven browser.
---

# qutebrowser

a config file for [qutebrowser](https://qutebrowser.org). tabs look like [kitty](/ports/kitty)'s, the status bar keeps the darker chrome shade and tints its text by mode (green for insert, violet for caret), menus and completion take the popup shade with the selection gray, and link hints are yellow like search matches. pages keep their own colors.

{{downloads}}

## install

```sh
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/qutebrowser/{{slug}}.py -o ~/.config/qutebrowser/{{slug}}.py
echo 'config.source("{{slug}}.py")' >> ~/.config/qutebrowser/config.py
```

then run `:config-source`, or restart qutebrowser. if `config.py` is new, put `config.load_autoconfig()` above that line, or the settings you change inside qutebrowser stop loading. on macos the folder is `~/.qutebrowser`.
