---
title: spicetify
description: rime for spotify, through spicetify. all five variants in one theme.
---

# spicetify

all five variants as color schemes of one [spicetify](https://spicetify.app) theme, for spotify.

{{downloads}}

## install

```sh
theme="$(dirname "$(spicetify -c)")/Themes/Rime"
mkdir -p "$theme"
curl -fsSL https://raw.githubusercontent.com/w0x7y/rime/main/general/spicetify/color.ini -o "$theme/color.ini"
spicetify config current_theme Rime color_scheme {{slug}} inject_css 0 replace_colors 1
spicetify apply
```

the schemes are named after the variants. switch with `spicetify config color_scheme <variant>` and `spicetify apply`.
