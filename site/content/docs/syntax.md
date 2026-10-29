---
title: syntax roles
description: which color each kind of code gets in rime, shared by neovim, vim, emacs, zed, vs code, helix and micro.
---

# syntax roles

a syntax role is what a piece of code is (a function, a keyword, a comment, a json key) and the color and style it gets. neovim, vim, emacs, zed, vs code, helix and micro share one table of roles, `SYNTAX` in `tools/build.py`, so a function is blue in all seven. the [sublime text](/ports/sublime) scheme and the [bat theme](/ports/bat), which [delta](/ports/delta) uses too, take vs code's colors, and [obsidian](/ports/obsidian)'s code blocks, [fish](/ports/fish)'s command line and [k9s](/ports/k9s)'s yaml view read the table too. this is that table, read from the script when the site is built.

{{syntax}}

## keywords

rime splits keywords by kind instead of painting them one color: declarations are violet, loops yellow, conditionals bold rose, and returns and exceptions rose. the [neovim page](/ports/neovim#keyword-colors) shows how to make them one color again.

## where the editors differ

- role names follow neovim's treesitter captures. each port maps its own scope names onto them.
- zed puts `if`, `for`, `return` and `try` into one `keyword.control` capture, so those share the rose color.
- zed and helix give struct fields and json keys one scope, so json keys are plain text there.
- in vs code, typescript and javascript give `return`, `await` and `yield` the same scope, so all three are rose.
- neovim's `styles` option restyles a group of roles at once, so every role in a group carries the group's default style.
