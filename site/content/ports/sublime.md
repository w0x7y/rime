---
title: sublime text
description: a rime color scheme for sublime text 4, with the same token colors as vs code.
---

# sublime text

a color scheme per variant, with the same token colors as the [vs code theme](/ports/vscode). it also colors the gutter's diff markers and the regions that plugins such as lsp draw. it needs sublime text 4.

{{downloads}}

## install

on linux:

```sh
mkdir -p ~/.config/sublime-text/Packages/User
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/sublime/{{slug}}.sublime-color-scheme -o ~/.config/sublime-text/Packages/User/{{slug}}.sublime-color-scheme
```

on macos the folder is `~/Library/Application Support/Sublime Text/Packages/User`, and on windows `%APPDATA%\Sublime Text\Packages\User`. `Preferences: Browse Packages` from the command palette opens it.

then run `UI: Select Color Scheme` and pick it, or set it in your preferences:

```json
{
  "color_scheme": "{{slug}}.sublime-color-scheme"
}
```

to follow the system's light and dark mode:

```json
{
  "color_scheme": "auto",
  "dark_color_scheme": "rime.sublime-color-scheme",
  "light_color_scheme": "rime-frost.sublime-color-scheme"
}
```

## notes

- sublime text has no strikethrough, so deprecated code and markdown's `~~text~~` keep their color without the line.
- the scheme colors the editor. the sidebar and tabs come from your ui theme; the built-in adaptive theme takes its colors from the scheme.
