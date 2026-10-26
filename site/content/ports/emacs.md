---
title: emacs
description: a rime theme for emacs, with the same syntax roles as the other editors.
---

# emacs

a theme per variant, for emacs 28 and later. it colors the font-lock faces, including the tree-sitter ones from emacs 29, plus the mode line, tab bar, line numbers, search, parens, completions, diffs, flymake and the 16 terminal colors of shell and compilation buffers. tested on emacs 31.1.

{{downloads}}

## install

```sh
mkdir -p ~/.emacs.d/themes
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/emacs/{{slug}}-theme.el -o ~/.emacs.d/themes/{{slug}}-theme.el
```

then in your `init.el`:

```elisp
(add-to-list 'custom-theme-load-path "~/.emacs.d/themes")
(load-theme '{{slug}} t)
```

the `t` skips emacs's question about whether to trust the theme. to switch variants, `M-x disable-theme` the old one before loading the next, or the two mix.

## notes

- emacs has one keyword face, so `if`, `for` and `return` share the violet keyword color.
- `font-lock-property-name-face` covers json keys and field definitions, which are rose, and `font-lock-property-use-face` covers field access, which is plain text.
- in a terminal, emacs uses the exact colors when `COLORTERM=truecolor` is set, and the nearest of 256 colors otherwise.
