---
title: delta
description: rime for delta, the git diff pager.
---

# delta

colors for [delta](https://github.com/dandavison/delta), the git diff pager: the backgrounds of removed and added lines and of the words that changed, the file and hunk headers, line numbers and the alternating backgrounds of `git blame`. delta highlights the code itself with a syntax theme from bat's cache, so it needs the [bat theme](/ports/bat) too.

{{downloads}}

## install

install delta and bat. on macos:

```sh
brew install git-delta bat
```

on arch:

```sh
sudo pacman -S git-delta bat
```

then put the bat theme in bat's cache, and include the delta file in your git config:

```sh
mkdir -p "$(bat --config-dir)/themes"
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/bat/{{slug}}.tmTheme -o "$(bat --config-dir)/themes/{{slug}}.tmTheme"
bat cache --build

mkdir -p ~/.config/delta
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/delta/{{slug}}.gitconfig -o ~/.config/delta/{{slug}}.gitconfig
git config --global --add include.path ~/.config/delta/{{slug}}.gitconfig
git config --global core.pager delta
git config --global interactive.diffFilter 'delta --color-only'
git config --global delta.features {{slug}}
```

each file is a delta feature named after its variant. if you already use features, such as `side-by-side`, list them together:

```sh
git config --global delta.features "{{slug}} side-by-side"
```

to switch variants later, add the other variant's two files the same way and change `delta.features`.

## notes

- it sets colors only; layout options such as `line-numbers` and `side-by-side` are yours.
- your terminal needs 24-bit color. delta assumes it when `COLORTERM` is `truecolor` or `24bit`; otherwise set `delta.true-color always`.
- if delta warns `Unknown theme`, the theme isn't in bat's cache: run `bat cache --build` again. delta reads the cache from bat's default place, so it won't find one you moved with `BAT_CACHE_PATH`.
