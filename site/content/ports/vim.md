---
title: vim
description: a rime colorscheme for vim, in true color with 256-color fallbacks.
---

# vim

a vimscript colorscheme per variant, for vim 8.2 and later. it colors the editor, the popup menu, diffs, spelling, the standard syntax groups and `:terminal`. with `termguicolors` on you get rime's exact colors; without it, the nearest of the 256 terminal colors. tested on vim 9.2.

neovim users want the [neovim port](/ports/neovim), which also covers treesitter, lsp and plugins.

{{downloads}}

## install

with [vim-plug](https://github.com/junegunn/vim-plug), pointing it at the `vim/` folder:

```vim
Plug 'w0x7y/rime', { 'rtp': 'vim' }
" after plug#end()
set termguicolors
colorscheme {{slug}}
```

or by hand:

```sh
mkdir -p ~/.vim/colors
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/vim/colors/{{slug}}.vim -o ~/.vim/colors/{{slug}}.vim
```

then add to your `vimrc`:

```vim
set termguicolors
colorscheme {{slug}}
```

## notes

- vim's syntax files put `return`, `break` and most other keywords in one `Statement` group, so they share the violet keyword color. conditionals, loops and exceptions keep their own colors where the syntax file marks them.
- inside tmux, true color needs `set -ga terminal-overrides ",*:Tc"` in your tmux config.
