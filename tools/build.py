#!/usr/bin/env python3
"""Generate every Rime port from the palettes in ../palettes.

Usage: python3 tools/build.py            rewrite every generated file
       python3 tools/build.py --check    list generated files that are out of date or left over, exit 1 if any

The palettes are the single source of truth for colours, and SYNTAX below for which
colour each kind of code gets. Edit either, run this script, and the Neovim modules,
Zed theme, VS Code themes, extension manifests, icon, the terminal / general-purpose
files and the website's site/data.json are all rewritten. Only the Python standard library is used.
"""

import json
import math
import pathlib
import plistlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = "0.5.1"
REPO = "https://github.com/w0x7y/rime"
AUTHOR = "Idan Gilboa"
EXTENSION_ID = "rime-theme"  # the Zed and VS Code extension id
DESCRIPTION = "A cold theme in five variants: Rime, Glacier, Aurora and Abyss, and the light Frost."
ORDER = [
    "rime",
    "rime-glacier",
    "rime-aurora",
    "rime-abyss",
    "rime-frost",
]  # the first is the default variant


# --------------------------------------------------------------------------- colour helpers


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def hexc(c):
    # round half up (not Python's half-to-even) so results match the Lua blend in lua/rime/util.lua;
    # tools/test_build.py checks that they agree
    return "#" + "".join(f"{max(0, min(255, int(v + 0.5))):02x}" for v in c)


def mix(a, b, t):
    """Blend colour a towards b by t (0 = a, 1 = b)."""
    ra, rb = rgb(a), rgb(b)
    return hexc(ra[i] + (rb[i] - ra[i]) * t for i in range(3))


def lift(spec, h, t):
    """Move colour h away from the background by t: towards white on a dark variant, black on a light one."""
    return mix(h, "#ffffff" if spec["appearance"] == "dark" else "#000000", t)


def alpha(h, a):
    """#rrggbb + alpha in 0..1 -> #rrggbbaa."""
    return h + f"{round(a * 255):02x}"


# --------------------------------------------------------------------------- colour names


# The colour name of each palette slot. lua/rime/init.lua repeats it, and a test checks the two agree.
SLOT_NAMES = {
    "base00": "bg",
    "base01": "bg_alt",
    "base02": "bg_sel",
    "base03": "comment",
    "base04": "muted",
    "base05": "fg",
    "base06": "fg_bright",
    "base07": "white",
    "base08": "red",
    "base09": "pink",
    "base0A": "yellow",
    "base0B": "green",
    "base0C": "cyan",
    "base0D": "blue",
    "base0E": "violet",
    "base0F": "steel",
}


def colours(spec):
    """The colour names of a variant (bg, fg, blue...), its derived shades and its 16 ANSI colours."""
    p = spec["palette"]
    r = {name: p[slot] for slot, name in SLOT_NAMES.items()}
    dark = spec["appearance"] == "dark"
    # derived shades, named as in lua/rime/init.lua, which blends the same way at load time.
    # bg_dark is the chrome (sidebars, bars); lighter than bg on a light variant so hovers still show
    r["bg_dark"] = (
        mix(r["bg"], "#000000", 0.18) if dark else mix(r["bg"], "#ffffff", 0.5)
    )
    r["border"] = mix(r["bg_alt"], r["bg_sel"], 0.5)
    r["colorcolumn"] = mix(r["bg"], r["bg_alt"], 0.5)
    r["whitespace"] = mix(r["comment"], r["bg"], 0.45)
    # backgrounds: an accent blended most of the way into bg
    for name, col, t in [
        ("diff_add", "green", 0.85),
        ("diff_change", "blue", 0.88),
        ("diff_text", "blue", 0.7),
        ("diff_delete", "red", 0.85),
        ("search", "yellow", 0.72),
        ("diag_error", "red", 0.9),
        ("diag_warn", "yellow", 0.9),
        ("diag_info", "blue", 0.9),
        ("diag_hint", "cyan", 0.9),
        ("diag_ok", "green", 0.9),
    ]:
        r[name] = mix(r[col], r["bg"], t)
    # 16 ANSI colours: black stays dark and white light, so a light variant swaps which is the text;
    # brights are lifted away from the background
    accents = [r[n] for n in ("red", "green", "yellow", "blue", "violet", "cyan")]
    if dark:
        black, white = r["bg_sel"], r["fg"]
        bright_black, bright_white = r["comment"], r["white"]
    else:
        black, white = r["fg"], r["comment"]
        bright_black, bright_white = r["muted"], mix(r["comment"], r["bg"], 0.25)
    normal = [black] + accents + [white]
    bright = [bright_black] + [lift(spec, c, 0.22) for c in accents] + [bright_white]
    r["ansi"] = normal + bright
    r["ansi_dim"] = [mix(c, r["bg"], 0.35) for c in normal]
    return r


ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


# --------------------------------------------------------------------------- syntax roles

# The colour name, default style and a note (shown on the website's syntax roles page) of
# every syntax role that two or more editor ports share. Role names follow Neovim's
# treesitter captures. Each port decides which of its own scopes belong to which role; the
# colours are decided only here. Neovim reads this table from lua/rime/syntax.lua, which is
# generated from it. Neovim users can restyle a whole group of roles at once (`styles` in
# lua/rime/init.lua), so roles in one group share one style.
SYNTAX = {
    "comment": ("comment", "italic", ""),
    "comment.tag": ("muted", "italic", "tags inside doc comments, such as @param"),
    "string": ("green", "", ""),
    "string.documentation": ("green", "", ""),
    "string.escape": ("cyan", "", ""),
    "string.regexp": ("cyan", "", ""),
    "string.special": ("cyan", "", ""),
    "string.special.symbol": ("pink", "", ""),
    "number": ("pink", "", ""),
    "boolean": ("pink", "", ""),
    "constant": ("pink", "", "also enum members"),
    "constant.builtin": ("cyan", "", "null, undefined"),
    "variable": ("fg", "", ""),
    "variable.builtin": ("cyan", "", "self, this"),
    "variable.parameter": ("fg", "", ""),
    "variable.member": ("fg", "", "fields and property access"),
    "property": ("red", "", "keys in key/value data such as JSON, YAML and CSS"),
    "function": ("blue", "", ""),
    "function.builtin": ("cyan", "", ""),
    "function.macro": ("cyan", "", ""),
    "constructor": ("cyan", "", ""),
    "attribute": ("cyan", "", "decorators and annotations"),
    "type": ("yellow", "", ""),
    "type.builtin": ("cyan", "", ""),
    "module": ("yellow", "", ""),
    "lifetime": ("pink", "italic", ""),
    "label": ("yellow", "", ""),
    "keyword": ("violet", "", ""),
    "keyword.conditional": ("red", "bold", ""),
    "keyword.repeat": ("yellow", "", ""),
    "keyword.return": ("red", "", ""),
    "keyword.exception": ("red", "", ""),
    "keyword.import": ("violet", "", ""),
    "keyword.modifier": ("violet", "", ""),
    "keyword.directive": ("yellow", "", "preprocessor"),
    "operator": ("muted", "", ""),
    "punctuation": ("steel", "", ""),
    "punctuation.special": ("cyan", "", "string interpolation brackets"),
    "tag": ("red", "", ""),
    "tag.attribute": ("yellow", "", ""),
    "selector": ("yellow", "", ""),
    "selector.pseudo": ("violet", "", ""),
    "markup.heading": ("blue", "bold", ""),
    "markup.strong": (None, "bold", ""),
    "markup.italic": (None, "italic", ""),
    "markup.strikethrough": (None, "strikethrough", ""),
    "markup.quote": ("muted", "italic", ""),
    "markup.list": ("red", "", ""),
    "markup.raw": ("green", "", ""),
    "markup.link.label": ("cyan", "", ""),
    "markup.link.url": ("blue", "underline", ""),
    "diff.plus": ("green", "", ""),
    "diff.minus": ("red", "", ""),
    "diff.delta": ("blue", "", ""),
    "diff.range": ("violet", "", ""),
    "deprecated": (None, "strikethrough", ""),
}


def syntax(c, role):
    """A syntax role as (colour or None, style), with the colour name resolved."""
    name, style, _ = SYNTAX[role]
    return (c[name] if name else None), style


def header(spec, comment="#"):
    return f"{comment} {spec['name']}: {spec['description']}\n" f"{comment} {REPO}\n"


# --------------------------------------------------------------------------- neovim


def nvim_key(slug):
    """The short variant name the Lua API uses: rime-glacier -> glacier, rime -> rime."""
    return slug.removeprefix("rime-")


def nvim_variants(specs):
    keys = ", ".join(f'"{nvim_key(spec["slug"])}"' for spec in specs)
    return (
        "-- Generated by tools/build.py from palettes/. Do not edit.\n"
        "-- Short variant names in order; the first is the default.\n"
        f"return {{ {keys} }}\n"
    )


def nvim_syntax():
    def entry(role):
        name, style, _ = SYNTAX[role]
        fg = f'fg = "{name}", ' if name else ""
        attrs = ", ".join(f"{a} = true" for a in style.split())
        return f'  ["{role}"] = {{ {fg}style = {{{f" {attrs} " if attrs else ""}}} }},'

    return (
        "-- Generated by tools/build.py from its SYNTAX table. Do not edit.\n"
        "-- The colour name and default style of every syntax role the editor ports share.\n"
        "return {\n" + "\n".join(entry(role) for role in SYNTAX) + "\n}\n"
    )


def nvim_palette(spec):
    p = spec["palette"]
    body = "\n".join(f'  {k} = "{v}",' for k, v in p.items())
    return (
        f"-- {spec['name']}: {spec['description']}\n"
        "-- Generated by tools/build.py from palettes/"
        + spec["slug"]
        + ".json. Do not edit.\n"
        f"return {{\n  name = \"{spec['name']}\",\n  appearance = \"{spec['appearance']}\",\n{body}\n}}\n"
    )


# --------------------------------------------------------------------------- zed


def zed_theme(spec):
    c = colours(spec)
    st = lambda col, a: alpha(col, a)
    style = {
        "background": c["bg_dark"],
        "background.appearance": "opaque",
        "border": c["border"],
        "border.variant": c["bg_alt"],
        "border.focused": st(c["blue"], 0.5),
        "border.selected": c["blue"],
        "border.transparent": "#00000000",
        "border.disabled": c["bg_alt"],
        "elevated_surface.background": c["bg_alt"],
        "surface.background": c["bg_dark"],
        "element.background": c["bg_alt"],
        "element.hover": st(c["fg"], 0.08),
        "element.active": st(c["fg"], 0.14),
        "element.selected": st(c["fg"], 0.12),
        "element.disabled": c["bg_alt"],
        "drop_target.background": st(c["blue"], 0.15),
        "ghost_element.background": "#00000000",
        "ghost_element.hover": st(c["fg"], 0.08),
        "ghost_element.active": st(c["fg"], 0.14),
        "ghost_element.selected": st(c["fg"], 0.12),
        "ghost_element.disabled": "#00000000",
        "text": c["fg"],
        "text.muted": c["muted"],
        "text.placeholder": c["comment"],
        "text.disabled": c["comment"],
        "text.accent": c["blue"],
        "icon": c["fg"],
        "icon.muted": c["muted"],
        "icon.disabled": c["comment"],
        "icon.placeholder": c["comment"],
        "icon.accent": c["blue"],
        "status_bar.background": c["bg_dark"],
        "title_bar.background": c["bg_dark"],
        "title_bar.inactive_background": c["bg_dark"],
        "toolbar.background": c["bg"],
        "tab_bar.background": c["bg_dark"],
        "tab.inactive_background": c["bg_dark"],
        "tab.active_background": c["bg"],
        "search.match_background": st(c["yellow"], 0.25),
        "panel.background": c["bg_dark"],
        "panel.focused_border": st(c["blue"], 0.5),
        "panel.indent_guide": c["bg_sel"],
        "panel.indent_guide_active": c["comment"],
        "panel.indent_guide_hover": c["comment"],
        "pane.focused_border": st(c["blue"], 0.4),
        "pane_group.border": c["border"],
        "scrollbar.thumb.background": st(c["comment"], 0.3),
        "scrollbar.thumb.hover_background": st(c["comment"], 0.55),
        "scrollbar.thumb.border": "#00000000",
        "scrollbar.track.background": "#00000000",
        "scrollbar.track.border": "#00000000",
        "editor.foreground": c["fg"],
        "editor.background": c["bg"],
        "editor.gutter.background": c["bg"],
        "editor.subheader.background": c["bg_alt"],
        "editor.active_line.background": c["bg_alt"],
        "editor.highlighted_line.background": c["bg_alt"],
        "editor.line_number": c["comment"],
        "editor.active_line_number": c["fg_bright"],
        "editor.invisible": c["bg_sel"],
        "editor.wrap_guide": c["bg_alt"],
        "editor.active_wrap_guide": c["bg_sel"],
        "editor.indent_guide": c["bg_sel"],
        "editor.indent_guide_active": c["comment"],
        "editor.document_highlight.read_background": st(c["blue"], 0.1),
        "editor.document_highlight.write_background": st(c["blue"], 0.18),
        "editor.document_highlight.bracket_background": c["bg_sel"],
        "terminal.background": c["bg"],
        "terminal.foreground": c["fg"],
        "terminal.bright_foreground": c["fg_bright"],
        "terminal.dim_foreground": c["muted"],
        "terminal.ansi.background": c["bg"],
        "link_text.hover": c["blue"],
    }
    for i, name in enumerate(ANSI_NAMES):
        style[f"terminal.ansi.{name}"] = c["ansi"][i]
        style[f"terminal.ansi.bright_{name}"] = c["ansi"][i + 8]
        style[f"terminal.ansi.dim_{name}"] = c["ansi_dim"][i]
    status = {
        "conflict": c["pink"],
        "created": c["green"],
        "deleted": c["red"],
        "error": c["red"],
        "hidden": c["comment"],
        "hint": c["cyan"],
        "ignored": c["comment"],
        "info": c["blue"],
        "modified": c["blue"],
        "predictive": c["comment"],
        "renamed": c["cyan"],
        "success": c["green"],
        "unreachable": c["comment"],
        "warning": c["yellow"],
    }
    for name, col in status.items():
        style[name] = col
        style[f"{name}.background"] = st(col, 0.1)
        style[f"{name}.border"] = st(col, 0.3)
    style["players"] = [
        {"cursor": col, "background": col, "selection": st(col, 0.24)}
        for col in (
            c["blue"],
            c["violet"],
            c["cyan"],
            c["green"],
            c["pink"],
            c["yellow"],
            c["red"],
            c["steel"],
        )
    ]
    style["accents"] = [
        c["blue"],
        c["violet"],
        c["cyan"],
        c["green"],
        c["yellow"],
        c["pink"],
    ]

    def s(col, italic=False, weight=None):
        d = {"color": col} if col else {}
        if italic:
            d["font_style"] = "italic"
        if weight:
            d["font_weight"] = weight
        return d

    def r(role):  # Zed has no underline or strikethrough in syntax styles
        col, style = syntax(c, role)
        return s(
            col, "italic" in style.split(), 700 if "bold" in style.split() else None
        )

    style["syntax"] = {
        "attribute": r("attribute"),
        "boolean": r("boolean"),
        "comment": r("comment"),
        "comment.doc": r("comment"),
        "constant": r("constant"),
        "constant.builtin": r("constant.builtin"),
        "constructor": r("constructor"),
        "embedded": s(c["fg"]),
        "emphasis": r("markup.italic"),
        "emphasis.strong": r("markup.strong"),
        "enum": r("type"),
        "function": r("function"),
        "function.builtin": r("function.builtin"),
        "function.method": r("function"),
        "hint": s(c["comment"], italic=True),
        "keyword": r("keyword"),
        # if, for, return and try share this capture in Zed, so they share the return colour
        "keyword.control": r("keyword.return"),
        "keyword.import": r("keyword.import"),
        "keyword.operator": r("keyword"),
        "label": r("label"),
        "lifetime": r("lifetime"),
        "link_text": r("markup.link.label"),
        "link_uri": r("markup.link.url"),
        "namespace": r("module"),
        "number": r("number"),
        "operator": r("operator"),
        "predictive": s(c["comment"], italic=True),
        "preproc": r("keyword.directive"),
        "primary": s(c["fg"]),
        "property": r(
            "variable.member"
        ),  # Zed uses one capture for keys and property access
        "property.json_key": r("property"),
        "punctuation": r("punctuation"),
        "punctuation.bracket": r("punctuation"),
        "punctuation.delimiter": r("punctuation"),
        "punctuation.list_marker": r("markup.list"),
        "punctuation.special": r("punctuation.special"),
        "selector": r("selector"),
        "selector.pseudo": r("selector.pseudo"),
        "string": r("string"),
        "string.doc": r("string.documentation"),
        "string.escape": r("string.escape"),
        "string.regex": r("string.regexp"),
        "string.special": r("string.special"),
        "string.special.symbol": r("string.special.symbol"),
        "tag": r("tag"),
        "text.literal": r("markup.raw"),
        "title": r("markup.heading"),
        "type": r("type"),
        "type.builtin": r("type.builtin"),
        "variable": r("variable"),
        "variable.parameter": r("variable.parameter"),
        "variable.special": r("variable.builtin"),
        "variant": r("constant"),
    }
    return {"name": spec["name"], "appearance": spec["appearance"], "style": style}


def zed_themes(specs):
    return (
        json.dumps(
            {
                "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
                "name": "Rime",
                "author": AUTHOR,
                "themes": [zed_theme(spec) for spec in specs],
            },
            indent=2,
        )
        + "\n"
    )


def zed_extension():
    return (
        "# Generated by tools/build.py. Change VERSION and DESCRIPTION there.\n"
        f'id = "{EXTENSION_ID}"\nname = "Rime"\nversion = "{VERSION}"\nschema_version = 1\n'
        f'authors = ["{AUTHOR}"]\ndescription = "{DESCRIPTION}"\nrepository = "{REPO}"\n'
    )


# --------------------------------------------------------------------------- vs code


def textmate_rules(c):
    """TextMate scopes mapped onto syntax roles: VS Code's token colors, which bat's tmTheme reuses."""

    def tc(name, scope, fg=None, style=None):
        settings = {}
        if fg:
            settings["foreground"] = fg
        if style is not None:
            settings["fontStyle"] = style
        return {"name": name, "scope": scope, "settings": settings}

    def rule(name, scope, role):
        col, style = syntax(c, role)
        return tc(name, scope, col, style or None)

    return [
        rule("Comments", ["comment", "punctuation.definition.comment"], "comment"),
        rule(
            "Doc comment tags",
            [
                "comment.block.documentation storage.type",
                "comment.block.documentation entity.name.type",
            ],
            "comment.tag",
        ),
        rule(
            "Variables",
            [
                "variable",
                "variable.other.readwrite",
                "variable.other.object",
                "meta.definition.variable",
            ],
            "variable",
        ),
        rule("Parameters", ["variable.parameter"], "variable.parameter"),
        rule(
            "Properties",
            ["variable.other.property", "variable.other.object.property"],
            "variable.member",
        ),
        rule(
            "Builtin variables",
            [
                "variable.language",
                "support.variable",
                "variable.language.this",
                "variable.language.self",
                "variable.language.super",
            ],
            "variable.builtin",
        ),
        rule(
            "JSON, YAML and CSS keys",
            [
                "support.type.property-name",
                "entity.name.tag.yaml",
                "support.type.property-name.json",
            ],
            "property",
        ),
        rule(
            "Strings",
            [
                "string",
                "punctuation.definition.string",
                "string.quoted",
                "string.template",
            ],
            "string",
        ),
        rule("Inline code", ["markup.inline.raw"], "markup.raw"),
        rule(
            "Symbols",
            ["constant.other.symbol", "constant.language.symbol"],
            "string.special.symbol",
        ),
        rule(
            "Escapes",
            ["constant.character.escape", "constant.character.format.placeholder"],
            "string.escape",
        ),
        rule(
            "Regex",
            ["string.regexp", "constant.other.character-class"],
            "string.regexp",
        ),
        rule(
            "Embedded expression brackets",
            [
                "punctuation.definition.template-expression",
                "punctuation.section.embedded",
            ],
            "punctuation.special",
        ),
        rule(
            "Numbers",
            [
                "constant.numeric",
                "constant.other.color",
                "keyword.other.unit",
                "constant.character",
            ],
            "number",
        ),
        rule("Booleans", ["constant.language.boolean"], "boolean"),
        rule(
            "Constants",
            [
                "constant.other",
                "variable.other.constant.property",
                "entity.name.constant",
                "support.constant",
                "variable.other.enummember",
            ],
            "constant",
        ),
        rule(
            "null, undefined and builtins",
            ["constant.language", "support.constant.math", "support.constant.json"],
            "constant.builtin",
        ),
        rule(
            "Functions",
            [
                "entity.name.function",
                "support.function",
                "meta.function-call.generic",
                "variable.function",
                "entity.name.method",
            ],
            "function",
        ),
        rule(
            "Macros",
            ["entity.name.function.macro", "entity.name.function.preprocessor"],
            "function.macro",
        ),
        rule(
            "Decorators and attributes",
            [
                "meta.decorator",
                "punctuation.decorator",
                "entity.name.function.decorator",
                "meta.attribute",
                "entity.other.attribute-name.pragma",
            ],
            "attribute",
        ),
        rule(
            "Types",
            [
                "entity.name.type",
                "entity.name.class",
                "entity.name.struct",
                "entity.name.enum",
                "entity.name.interface",
                "entity.name.trait",
                "entity.other.inherited-class",
                "entity.name.type.class",
                "support.type",
                "support.class",
            ],
            "type",
        ),
        rule(
            "Modules",
            [
                "entity.name.namespace",
                "entity.name.type.module",
                "entity.name.scope-resolution",
            ],
            "module",
        ),
        rule(
            "Builtin types",
            [
                "support.type.primitive",
                "support.type.builtin",
                "keyword.type",
                "storage.type.primitive",
                "storage.type.built-in",
                "support.class.builtin",
                "support.class.promise",
                "support.class.console",
            ],
            "type.builtin",
        ),
        rule(
            "Keywords",
            [
                "keyword",
                "storage.type",
                "keyword.control",
                "keyword.operator.new",
                "keyword.operator.expression",
                "keyword.operator.logical.python",
                "keyword.other",
                "storage.type.function.arrow",
            ],
            "keyword",
        ),
        rule("Modifiers", ["storage.modifier"], "keyword.modifier"),
        rule(
            "Imports",
            [
                "keyword.control.import",
                "keyword.control.export",
                "keyword.control.from",
            ],
            "keyword.import",
        ),
        rule(
            "Conditionals",
            [
                "keyword.control.conditional",
                "keyword.control.switch",
                "keyword.control.case",
                "keyword.control.else",
                "keyword.control.if",
            ],
            "keyword.conditional",
        ),
        rule(
            "Loops",
            [
                "keyword.control.loop",
                "keyword.control.for",
                "keyword.control.while",
                "keyword.control.do",
                "keyword.control.repeat",
                "keyword.control.break",
                "keyword.control.continue",
                "keyword.operator.expression.of",
            ],
            "keyword.repeat",
        ),
        rule(
            "Returns",
            ["keyword.control.return", "keyword.control.flow"],
            "keyword.return",
        ),
        rule(
            "Exceptions",
            [
                "keyword.control.trycatch",
                "keyword.control.exception",
                "keyword.control.throw",
                "keyword.control.try",
                "keyword.control.catch",
                "keyword.control.finally",
            ],
            "keyword.exception",
        ),
        rule(
            "Operators",
            [
                "keyword.operator",
                "punctuation.accessor",
                "punctuation.separator.key-value",
            ],
            "operator",
        ),
        rule(
            "Punctuation",
            [
                "punctuation",
                "meta.brace",
                "punctuation.separator",
                "punctuation.terminator",
                "punctuation.definition.block",
                "punctuation.definition.parameters",
                "punctuation.definition.array",
                "punctuation.definition.dictionary",
                "punctuation.section",
                "punctuation.definition.tag",
                "meta.tag.sgml",
            ],
            "punctuation",
        ),
        rule(
            "Template and string interpolation brackets",
            [
                "punctuation.definition.template-expression.begin",
                "punctuation.definition.template-expression.end",
                "punctuation.section.interpolation",
            ],
            "punctuation.special",
        ),
        rule(
            "Tags",
            ["entity.name.tag", "support.class.component", "entity.name.tag.html"],
            "tag",
        ),
        rule(
            "Attributes",
            [
                "entity.other.attribute-name",
                "entity.other.attribute-name.html",
                "entity.other.attribute-name.jsx",
            ],
            "tag.attribute",
        ),
        rule(
            "CSS selectors",
            [
                "entity.other.attribute-name.class.css",
                "entity.other.attribute-name.id.css",
                "entity.name.tag.css",
            ],
            "selector",
        ),
        rule(
            "CSS pseudo",
            [
                "entity.other.attribute-name.pseudo-class",
                "entity.other.attribute-name.pseudo-element",
            ],
            "selector.pseudo",
        ),
        tc(
            "CSS values",
            ["support.constant.property-value", "support.constant.font-name"],
            c["cyan"],
        ),
        rule("Labels", ["entity.name.label", "punctuation.definition.label"], "label"),
        rule(
            "Lifetimes",
            ["entity.name.type.lifetime", "storage.modifier.lifetime"],
            "lifetime",
        ),
        rule(
            "Headings",
            ["markup.heading", "entity.name.section", "markup.heading entity.name"],
            "markup.heading",
        ),
        rule("Bold", ["markup.bold"], "markup.strong"),
        rule("Italic", ["markup.italic"], "markup.italic"),
        rule("Strikethrough", ["markup.strikethrough"], "markup.strikethrough"),
        rule("Link URLs", ["markup.underline.link"], "markup.link.url"),
        rule(
            "Link text",
            ["string.other.link", "constant.other.reference.link"],
            "markup.link.label",
        ),
        rule("Quotes", ["markup.quote"], "markup.quote"),
        rule(
            "Lists",
            [
                "markup.list punctuation.definition.list",
                "punctuation.definition.list.begin.markdown",
            ],
            "markup.list",
        ),
        rule(
            "Diff inserted",
            ["markup.inserted", "meta.diff.header.to-file"],
            "diff.plus",
        ),
        rule(
            "Diff deleted",
            ["markup.deleted", "meta.diff.header.from-file"],
            "diff.minus",
        ),
        rule("Diff changed", ["markup.changed"], "diff.delta"),
        rule("Diff ranges", ["meta.diff.range", "meta.diff.header"], "diff.range"),
        tc("Invalid", ["invalid", "invalid.illegal"], c["red"], "underline"),
        tc("Deprecated", ["invalid.deprecated"], c["muted"], "strikethrough"),
    ]


def vscode_theme(spec):
    c = colours(spec)
    a = alpha
    dark = spec["appearance"] == "dark"
    colors = {
        "foreground": c["fg"],
        "descriptionForeground": c["muted"],
        "errorForeground": c["red"],
        "icon.foreground": c["muted"],
        "focusBorder": a(c["blue"], 0.45),
        "selection.background": a(c["blue"], 0.3),
        "widget.shadow": "#00000066" if dark else "#00000029",
        "scrollbar.shadow": "#00000040" if dark else "#0000001a",
        "textLink.foreground": c["blue"],
        "textLink.activeForeground": c["cyan"],
        "textPreformat.foreground": c["green"],
        "textBlockQuote.background": c["bg_alt"],
        "textBlockQuote.border": c["steel"],
        "textCodeBlock.background": c["bg_alt"],
        "textSeparator.foreground": c["border"],
        "button.background": c["blue"],
        "button.foreground": c["bg"],
        "button.hoverBackground": lift(spec, c["blue"], 0.15),
        "button.secondaryBackground": c["bg_sel"],
        "button.secondaryForeground": c["fg"],
        "button.secondaryHoverBackground": lift(spec, c["bg_sel"], 0.06),
        "badge.background": c["blue"],
        "badge.foreground": c["bg"],
        "progressBar.background": c["blue"],
        "checkbox.background": c["bg_alt"],
        "checkbox.border": c["border"],
        "checkbox.foreground": c["fg"],
        "dropdown.background": c["bg_alt"],
        "dropdown.border": c["border"],
        "dropdown.foreground": c["fg"],
        "input.background": c["bg"],
        "input.border": c["border"],
        "input.foreground": c["fg"],
        "input.placeholderForeground": c["comment"],
        "inputOption.activeBackground": a(c["blue"], 0.25),
        "inputOption.activeBorder": a(c["blue"], 0.6),
        "inputOption.activeForeground": c["fg_bright"],
        "inputValidation.errorBackground": c["bg_alt"],
        "inputValidation.errorBorder": c["red"],
        "inputValidation.warningBackground": c["bg_alt"],
        "inputValidation.warningBorder": c["yellow"],
        "inputValidation.infoBackground": c["bg_alt"],
        "inputValidation.infoBorder": c["blue"],
        "scrollbarSlider.background": a(c["comment"], 0.3),
        "scrollbarSlider.hoverBackground": a(c["comment"], 0.5),
        "scrollbarSlider.activeBackground": a(c["comment"], 0.7),
        "titleBar.activeBackground": c["bg_dark"],
        "titleBar.activeForeground": c["muted"],
        "titleBar.inactiveBackground": c["bg_dark"],
        "titleBar.inactiveForeground": c["comment"],
        "titleBar.border": c["bg_dark"],
        "menu.background": c["bg_alt"],
        "menu.foreground": c["fg"],
        "menu.selectionBackground": c["bg_sel"],
        "menu.selectionForeground": c["fg_bright"],
        "menu.separatorBackground": c["border"],
        "menu.border": c["border"],
        "menubar.selectionBackground": c["bg_alt"],
        "activityBar.background": c["bg_dark"],
        "activityBar.foreground": c["fg"],
        "activityBar.inactiveForeground": c["comment"],
        "activityBar.activeBorder": c["blue"],
        "activityBar.border": c["bg_dark"],
        "activityBarBadge.background": c["blue"],
        "activityBarBadge.foreground": c["bg"],
        "sideBar.background": c["bg_dark"],
        "sideBar.foreground": c["muted"],
        "sideBar.border": c["bg_dark"],
        "sideBarTitle.foreground": c["muted"],
        "sideBarSectionHeader.background": c["bg_dark"],
        "sideBarSectionHeader.foreground": c["fg"],
        "sideBarSectionHeader.border": c["border"],
        "list.activeSelectionBackground": c["bg_sel"],
        "list.activeSelectionForeground": c["fg_bright"],
        "list.inactiveSelectionBackground": c["bg_alt"],
        "list.inactiveSelectionForeground": c["fg"],
        "list.hoverBackground": c["bg_alt"],
        "list.hoverForeground": c["fg"],
        "list.focusBackground": c["bg_sel"],
        "list.focusOutline": a(c["blue"], 0.45),
        "list.highlightForeground": c["blue"],
        "list.errorForeground": c["red"],
        "list.warningForeground": c["yellow"],
        "list.invalidItemForeground": c["red"],
        "list.dropBackground": a(c["blue"], 0.15),
        "tree.indentGuidesStroke": c["bg_sel"],
        "quickInput.background": c["bg_alt"],
        "quickInput.foreground": c["fg"],
        "quickInputList.focusBackground": c["bg_sel"],
        "quickInputTitle.background": c["bg_alt"],
        "pickerGroup.foreground": c["blue"],
        "pickerGroup.border": c["border"],
        "commandCenter.background": c["bg_alt"],
        "commandCenter.foreground": c["muted"],
        "commandCenter.border": c["border"],
        "editorGroup.border": c["border"],
        "editorGroup.dropBackground": a(c["blue"], 0.12),
        "editorGroupHeader.tabsBackground": c["bg_dark"],
        "editorGroupHeader.tabsBorder": c["bg_dark"],
        "editorGroupHeader.noTabsBackground": c["bg_dark"],
        "tab.activeBackground": c["bg"],
        "tab.activeForeground": c["fg_bright"],
        "tab.activeBorderTop": c["blue"],
        "tab.inactiveBackground": c["bg_dark"],
        "tab.inactiveForeground": c["comment"],
        "tab.hoverBackground": c["bg_alt"],
        "tab.border": c["bg_dark"],
        "tab.unfocusedActiveBorderTop": c["comment"],
        "tab.unfocusedActiveForeground": c["muted"],
        "tab.unfocusedInactiveForeground": c["comment"],
        "breadcrumb.background": c["bg"],
        "breadcrumb.foreground": c["muted"],
        "breadcrumb.focusForeground": c["fg"],
        "breadcrumb.activeSelectionForeground": c["blue"],
        "breadcrumbPicker.background": c["bg_alt"],
        "editor.background": c["bg"],
        "editor.foreground": c["fg"],
        "editorLineNumber.foreground": c["comment"],
        "editorLineNumber.activeForeground": c["fg_bright"],
        "editorCursor.foreground": c["fg"],
        "editor.lineHighlightBackground": c["bg_alt"],
        "editor.lineHighlightBorder": "#00000000",
        "editor.selectionBackground": a(c["blue"], 0.25),
        "editor.inactiveSelectionBackground": a(c["blue"], 0.14),
        "editor.selectionHighlightBackground": a(c["blue"], 0.14),
        "editor.wordHighlightBackground": a(c["blue"], 0.14),
        "editor.wordHighlightStrongBackground": a(c["blue"], 0.22),
        "editor.findMatchBackground": a(c["yellow"], 0.35),
        "editor.findMatchBorder": c["yellow"],
        "editor.findMatchHighlightBackground": a(c["yellow"], 0.18),
        "editor.findRangeHighlightBackground": a(c["bg_sel"], 0.6),
        "editor.rangeHighlightBackground": a(c["bg_sel"], 0.5),
        "editor.hoverHighlightBackground": a(c["blue"], 0.12),
        "editor.foldBackground": a(c["bg_sel"], 0.5),
        "editorLink.activeForeground": c["blue"],
        "editorWhitespace.foreground": c["bg_sel"],
        "editorIndentGuide.background1": c["bg_sel"],
        "editorIndentGuide.activeBackground1": c["comment"],
        "editorRuler.foreground": c["bg_alt"],
        "editorCodeLens.foreground": c["comment"],
        "editorInlayHint.foreground": c["muted"],
        "editorInlayHint.background": c["bg_alt"],
        "editorGhostText.foreground": c["comment"],
        "editorBracketMatch.background": a(c["bg_sel"], 0.8),
        "editorBracketMatch.border": c["comment"],
        "editorBracketHighlight.foreground1": c["blue"],
        "editorBracketHighlight.foreground2": c["violet"],
        "editorBracketHighlight.foreground3": c["cyan"],
        "editorBracketHighlight.foreground4": c["blue"],
        "editorBracketHighlight.foreground5": c["violet"],
        "editorBracketHighlight.foreground6": c["cyan"],
        "editorBracketHighlight.unexpectedBracket.foreground": c["red"],
        "editorError.foreground": c["red"],
        "editorWarning.foreground": c["yellow"],
        "editorInfo.foreground": c["blue"],
        "editorHint.foreground": c["cyan"],
        "editorUnnecessaryCode.opacity": "#00000080",
        "editorGutter.background": c["bg"],
        "editorGutter.addedBackground": c["green"],
        "editorGutter.modifiedBackground": c["blue"],
        "editorGutter.deletedBackground": c["red"],
        "editorGutter.foldingControlForeground": c["muted"],
        "editorOverviewRuler.border": "#00000000",
        "editorOverviewRuler.errorForeground": c["red"],
        "editorOverviewRuler.warningForeground": c["yellow"],
        "editorOverviewRuler.infoForeground": c["blue"],
        "editorOverviewRuler.addedForeground": c["green"],
        "editorOverviewRuler.modifiedForeground": c["blue"],
        "editorOverviewRuler.deletedForeground": c["red"],
        "editorOverviewRuler.findMatchForeground": c["yellow"],
        "editorStickyScroll.background": c["bg"],
        "editorStickyScrollHover.background": c["bg_alt"],
        "editorWidget.background": c["bg_alt"],
        "editorWidget.foreground": c["fg"],
        "editorWidget.border": c["border"],
        "editorSuggestWidget.background": c["bg_alt"],
        "editorSuggestWidget.border": c["border"],
        "editorSuggestWidget.foreground": c["fg"],
        "editorSuggestWidget.highlightForeground": c["blue"],
        "editorSuggestWidget.focusHighlightForeground": c["blue"],
        "editorSuggestWidget.selectedBackground": c["bg_sel"],
        "editorHoverWidget.background": c["bg_alt"],
        "editorHoverWidget.border": c["border"],
        "editorHoverWidget.statusBarBackground": c["bg_alt"],
        "debugExceptionWidget.background": c["bg_alt"],
        "debugExceptionWidget.border": c["red"],
        "debugToolBar.background": c["bg_alt"],
        "peekView.border": c["blue"],
        "peekViewEditor.background": c["bg_alt"],
        "peekViewEditor.matchHighlightBackground": a(c["yellow"], 0.25),
        "peekViewResult.background": c["bg_dark"],
        "peekViewResult.matchHighlightBackground": a(c["yellow"], 0.25),
        "peekViewResult.selectionBackground": c["bg_sel"],
        "peekViewTitle.background": c["bg_dark"],
        "peekViewTitleLabel.foreground": c["fg_bright"],
        "peekViewTitleDescription.foreground": c["muted"],
        "minimapSlider.background": a(c["comment"], 0.2),
        "minimapSlider.hoverBackground": a(c["comment"], 0.35),
        "minimapSlider.activeBackground": a(c["comment"], 0.5),
        "minimapGutter.addedBackground": c["green"],
        "minimapGutter.modifiedBackground": c["blue"],
        "minimapGutter.deletedBackground": c["red"],
        "diffEditor.insertedTextBackground": a(c["green"], 0.15),
        "diffEditor.removedTextBackground": a(c["red"], 0.15),
        "diffEditor.insertedLineBackground": a(c["green"], 0.08),
        "diffEditor.removedLineBackground": a(c["red"], 0.08),
        "diffEditor.diagonalFill": c["bg_sel"],
        "merge.currentHeaderBackground": a(c["green"], 0.35),
        "merge.currentContentBackground": a(c["green"], 0.12),
        "merge.incomingHeaderBackground": a(c["blue"], 0.35),
        "merge.incomingContentBackground": a(c["blue"], 0.12),
        "panel.background": c["bg_dark"],
        "panel.border": c["border"],
        "panelTitle.activeBorder": c["blue"],
        "panelTitle.activeForeground": c["fg_bright"],
        "panelTitle.inactiveForeground": c["comment"],
        "panelInput.border": c["border"],
        "statusBar.background": c["bg_dark"],
        "statusBar.foreground": c["muted"],
        "statusBar.border": c["bg_dark"],
        "statusBar.noFolderBackground": c["bg_dark"],
        "statusBar.debuggingBackground": c["violet"],
        "statusBar.debuggingForeground": c["bg"],
        "statusBarItem.hoverBackground": c["bg_alt"],
        "statusBarItem.remoteBackground": c["blue"],
        "statusBarItem.remoteForeground": c["bg"],
        "statusBarItem.errorBackground": c["red"],
        "statusBarItem.errorForeground": c["bg"],
        "statusBarItem.warningBackground": c["yellow"],
        "statusBarItem.warningForeground": c["bg"],
        "notifications.background": c["bg_alt"],
        "notifications.foreground": c["fg"],
        "notifications.border": c["border"],
        "notificationCenterHeader.background": c["bg_dark"],
        "notificationCenterHeader.foreground": c["fg"],
        "notificationLink.foreground": c["blue"],
        "notificationsErrorIcon.foreground": c["red"],
        "notificationsWarningIcon.foreground": c["yellow"],
        "notificationsInfoIcon.foreground": c["blue"],
        "terminal.background": c["bg"],
        "terminal.foreground": c["fg"],
        "terminal.selectionBackground": a(c["blue"], 0.3),
        "terminalCursor.foreground": c["fg"],
        "terminal.border": c["border"],
        "gitDecoration.addedResourceForeground": c["green"],
        "gitDecoration.modifiedResourceForeground": c["blue"],
        "gitDecoration.deletedResourceForeground": c["red"],
        "gitDecoration.renamedResourceForeground": c["cyan"],
        "gitDecoration.untrackedResourceForeground": c["green"],
        "gitDecoration.ignoredResourceForeground": c["comment"],
        "gitDecoration.conflictingResourceForeground": c["pink"],
        "gitDecoration.stageModifiedResourceForeground": c["blue"],
        "gitDecoration.stageDeletedResourceForeground": c["red"],
        "gitDecoration.submoduleResourceForeground": c["cyan"],
        "settings.headerForeground": c["fg_bright"],
        "settings.modifiedItemIndicator": c["blue"],
        "keybindingLabel.background": c["bg_sel"],
        "keybindingLabel.foreground": c["fg"],
        "keybindingLabel.border": c["border"],
        "keybindingLabel.bottomBorder": c["border"],
        "welcomePage.tileBackground": c["bg_alt"],
        "walkThrough.embeddedEditorBackground": c["bg_alt"],
        "charts.foreground": c["fg"],
        "charts.lines": c["comment"],
        "charts.red": c["red"],
        "charts.blue": c["blue"],
        "charts.yellow": c["yellow"],
        "charts.orange": c["pink"],
        "charts.green": c["green"],
        "charts.purple": c["violet"],
    }
    for i, name in enumerate(ANSI_NAMES):
        cap = name.capitalize()
        colors[f"terminal.ansi{cap}"] = c["ansi"][i]
        colors[f"terminal.ansiBright{cap}"] = c["ansi"][i + 8]

    token_colors = textmate_rules(c)

    def sem(role):
        col, style = syntax(c, role)
        if not style:
            return col
        return {
            **({"foreground": col} if col else {}),
            **{attr: True for attr in style.split()},
        }

    semantic = {
        "namespace": sem("module"),
        "type": sem("type"),
        "class": sem("type"),
        "enum": sem("type"),
        "interface": sem("type"),
        "struct": sem("type"),
        "typeParameter": sem("type"),
        "builtinType": sem("type.builtin"),
        "class.defaultLibrary": sem("type.builtin"),
        "type.defaultLibrary": sem("type.builtin"),
        "variable.defaultLibrary": sem("variable.builtin"),
        "function.defaultLibrary": sem("function.builtin"),
        "selfKeyword": sem("variable.builtin"),
        "parameter": sem("variable.parameter"),
        "variable": sem("variable"),
        "property": sem("variable.member"),
        "enumMember": sem("constant"),
        "function": sem("function"),
        "method": sem("function"),
        "macro": sem("function.macro"),
        "decorator": sem("attribute"),
        "lifetime": sem("lifetime"),
        "*.deprecated": sem("deprecated"),
    }
    return {
        "$schema": "vscode://schemas/color-theme",
        "name": spec["name"],
        "type": spec["appearance"],
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": token_colors,
        "semanticTokenColors": semantic,
    }


# where each variant's VS Code theme sits inside the extension folder
VSCODE_THEME = "themes/{slug}-color-theme.json"


def vscode_package(specs):
    return {
        "name": EXTENSION_ID,
        "displayName": "Rime Theme",
        "description": DESCRIPTION,
        "version": VERSION,
        "publisher": "w0x7y",
        "license": "MIT",
        "repository": {"type": "git", "url": REPO},
        "engines": {"vscode": "^1.70.0"},
        "categories": ["Themes"],
        "keywords": ["theme", "dark", "light", "cold", "blue", "rime", "base16"],
        "icon": "icon.png",
        "galleryBanner": {
            "color": specs[0]["palette"]["base00"],
            "theme": specs[0]["appearance"],
        },
        "contributes": {
            "themes": [
                {
                    "label": s["name"],
                    "uiTheme": "vs-dark" if s["appearance"] == "dark" else "vs",
                    "path": "./" + VSCODE_THEME.format(slug=s["slug"]),
                }
                for s in specs
            ]
        },
    }


# --------------------------------------------------------------------------- helix

# Helix's highlight scopes and the syntax role each takes. Helix falls back to the longest
# matching key, so `function.method` takes `function` unless it is listed.
HELIX_SYNTAX = {
    "attribute": "attribute",  # also HTML attributes, which Helix doesn't tell apart
    "type": "type",
    "type.builtin": "type.builtin",
    "type.enum.variant": "constant",
    "constructor": "constructor",
    "constant": "constant",
    "constant.builtin": "constant.builtin",
    "constant.builtin.boolean": "boolean",
    "constant.character": "string",
    "constant.character.escape": "string.escape",
    "constant.numeric": "number",
    "string": "string",
    "string.regexp": "string.regexp",
    "string.special": "string.special",
    "string.special.url": "markup.link.url",
    "string.special.symbol": "string.special.symbol",
    "comment": "comment",
    "variable": "variable",
    "variable.builtin": "variable.builtin",
    "variable.parameter": "variable.parameter",
    # Helix gives fields and JSON, YAML and TOML keys this one scope, as Zed does
    "variable.other.member": "variable.member",
    "label": "label",
    "punctuation": "punctuation",
    "punctuation.special": "punctuation.special",
    "keyword": "keyword",
    "keyword.control.conditional": "keyword.conditional",
    "keyword.control.repeat": "keyword.repeat",
    "keyword.control.import": "keyword.import",
    "keyword.control.return": "keyword.return",
    "keyword.control.exception": "keyword.exception",
    "keyword.directive": "keyword.directive",
    "keyword.storage.modifier": "keyword.modifier",
    "operator": "operator",
    "function": "function",
    "function.builtin": "function.builtin",
    "function.macro": "function.macro",
    "function.special": "keyword.directive",  # the C preprocessor
    "tag": "tag",
    "namespace": "module",
    "markup.heading": "markup.heading",
    "markup.list": "markup.list",
    "markup.bold": "markup.strong",
    "markup.italic": "markup.italic",
    "markup.strikethrough": "markup.strikethrough",
    "markup.link.url": "markup.link.url",
    "markup.link.label": "markup.link.label",
    "markup.link.text": "markup.link.label",
    "markup.quote": "markup.quote",
    "markup.raw": "markup.raw",
    "diff.plus": "diff.plus",
    "diff.minus": "diff.minus",
    "diff.delta": "diff.delta",
}


def helix(spec):
    """A Helix theme. It names the colours in a [palette] table and refers to them by name."""
    c = colours(spec)

    def st(fg=None, bg=None, mods=(), curl=None, line=False):
        parts = [f'{k} = "{v}"' for k, v in (("fg", fg), ("bg", bg)) if v]
        if curl:
            parts.append(f'underline = {{ color = "{curl}", style = "curl" }}')
        if line:
            parts.append('underline = { style = "line" }')
        if mods:
            parts.append("modifiers = [" + ", ".join(f'"{m}"' for m in mods) + "]")
        return "{ " + ", ".join(parts) + " }"

    def role(name):
        fg, style, _ = SYNTAX[name]
        words = style.split()
        mods = [{"strikethrough": "crossed_out"}.get(w, w) for w in words if w != "underline"]
        return st(fg, mods=mods, line="underline" in words)

    def mode(accent):
        return st("bg", accent, ["bold"])

    keys = {scope: role(r) for scope, r in HELIX_SYNTAX.items()}
    keys |= {
        "special": st("blue", mods=["bold"]),  # also the matched letters in pickers
        "ui.background": st(bg="bg"),
        "ui.background.separator": st("border"),
        "ui.text": st("fg"),
        "ui.text.focus": st("fg_bright", "bg_sel", ["bold"]),
        "ui.text.inactive": st("comment"),
        "ui.text.directory": st("blue"),
        "ui.cursor": st("bg", "muted"),
        "ui.cursor.primary": st("bg", "fg"),
        "ui.cursor.match": st("fg_bright", "bg_sel", ["bold"]),
        "ui.selection": st(bg="border"),
        "ui.selection.primary": st(bg="bg_sel"),
        "ui.highlight": st(bg="bg_sel"),
        "ui.cursorline.primary": st(bg="bg_alt"),
        "ui.cursorcolumn.primary": st(bg="bg_alt"),
        "ui.linenr": st("comment"),
        "ui.linenr.selected": st("fg_bright", mods=["bold"]),
        "ui.statusline": st("muted", "bg_alt"),
        "ui.statusline.inactive": st("comment", "bg_alt"),
        "ui.statusline.normal": mode("blue"),
        "ui.statusline.insert": mode("green"),
        "ui.statusline.select": mode("violet"),
        "ui.bufferline": st("comment", "bg_alt"),
        "ui.bufferline.active": st("fg_bright", "bg", ["bold"]),
        "ui.bufferline.background": st(bg="bg_dark"),
        "ui.popup": st("fg", "bg_alt"),
        "ui.window": st("border"),
        "ui.help": st("fg", "bg_alt"),
        "ui.menu": st("fg", "bg_alt"),
        "ui.menu.selected": st(bg="bg_sel", mods=["bold"]),
        "ui.menu.scroll": st("comment", "bg_alt"),
        "ui.virtual.ruler": st(bg="colorcolumn"),
        "ui.virtual.whitespace": st("whitespace"),
        "ui.virtual.indent-guide": st("bg_sel"),
        "ui.virtual.inlay-hint": st("comment", "bg_alt"),
        "ui.virtual.wrap": st("whitespace"),
        "ui.virtual.jump-label": st("bg", "red", ["bold"]),
        "ui.debug.breakpoint": st("red"),
        "ui.debug.active": st("yellow"),
        "tabstop": st(bg="bg_sel"),
        "diagnostic.unnecessary": st("comment"),
        "diagnostic.deprecated": st(mods=["crossed_out"]),
    }
    for level, col, shade in [
        ("error", "red", "diag_error"),
        ("warning", "yellow", "diag_warn"),
        ("info", "blue", "diag_info"),
        ("hint", "cyan", "diag_hint"),
    ]:
        keys[level] = st(col)
        keys[f"{level}.diagnostic.inline"] = st(col, shade)
        keys[f"diagnostic.{level}"] = st(curl=col)
    palette = {n: v for n, v in c.items() if isinstance(v, str)}
    return (
        header(spec)
        + "".join(f'"{k}" = {v}\n' for k, v in keys.items())
        + "\n[palette]\n"
        + "".join(f'{k} = "{v}"\n' for k, v in palette.items())
    )


# --------------------------------------------------------------------------- sublime text


def sublime(spec):
    """A Sublime Text color scheme: VS Code's token rules, which mostly use Sublime's own scope names."""
    c = colours(spec)
    rules = []
    for r in textmate_rules(c):
        s = r["settings"]
        # Sublime has no strikethrough
        style = " ".join(w for w in s.get("fontStyle", "").split() if w in ("bold", "italic", "underline"))
        rule = {"name": r["name"], "scope": ", ".join(r["scope"])}
        if "foreground" in s:
            rule["foreground"] = s["foreground"]
        if style:
            rule["font_style"] = style
        if len(rule) > 2:
            rules.append(rule)
    # the colors plugins such as LSP and GitGutter draw with
    regions = {
        "redish": "red", "orangish": "pink", "yellowish": "yellow", "greenish": "green",
        "cyanish": "cyan", "bluish": "blue", "purplish": "violet", "pinkish": "pink",
    }
    rules += [{"scope": f"region.{k}", "foreground": c[v]} for k, v in regions.items()]
    globals_ = {
        "background": c["bg"],
        "foreground": c["fg"],
        "caret": c["fg"],
        "invisibles": c["whitespace"],
        "line_highlight": c["bg_alt"],
        "selection": c["bg_sel"],
        "inactive_selection": c["border"],
        "highlight": c["yellow"],
        "find_highlight": c["yellow"],
        "find_highlight_foreground": c["bg"],
        "accent": c["blue"],
        "gutter": c["bg"],
        "gutter_foreground": c["comment"],
        "gutter_foreground_highlight": c["fg_bright"],
        "guide": c["bg_sel"],
        "active_guide": c["comment"],
        "stack_guide": c["border"],
        "rulers": c["bg_sel"],
        "brackets_foreground": c["fg_bright"],
        "brackets_options": "underline",
        "bracket_contents_foreground": c["fg_bright"],
        "bracket_contents_options": "underline",
        "tags_foreground": c["fg_bright"],
        "tags_options": "underline",
        "misspelling": c["red"],
        "fold_marker": c["muted"],
        "minimap_border": c["border"],
        "line_diff_added": c["green"],
        "line_diff_modified": c["blue"],
        "line_diff_deleted": c["red"],
        "shadow": alpha("#000000", 0.25),
    }
    theme = {
        "name": spec["name"],
        "author": f"{AUTHOR} ({REPO})",
        "globals": globals_,
        "rules": rules,
    }
    return json.dumps(theme, indent=2) + "\n"


# --------------------------------------------------------------------------- general use


def base16_yaml(spec):
    lines = [
        f'system: "base16"',
        f'name: "{spec["name"]}"',
        f'author: "{AUTHOR} ({REPO})"',
        f'description: "{spec["description"]}"',
        f'variant: "{spec["appearance"]}"',
        "palette:",
    ]
    lines += [f'  {k}: "{v}"' for k, v in spec["palette"].items()]
    return "\n".join(lines) + "\n"


def kitty(spec):
    c = colours(spec)
    out = [
        header(spec),
        f"foreground {c['fg']}",
        f"background {c['bg']}",
        f"selection_foreground {c['fg_bright']}",
        f"selection_background {c['bg_sel']}",
        f"cursor {c['fg']}",
        f"cursor_text_color {c['bg']}",
        f"url_color {c['blue']}",
        f"active_border_color {c['blue']}",
        f"inactive_border_color {c['bg_sel']}",
        f"bell_border_color {c['yellow']}",
        f"active_tab_foreground {c['fg_bright']}",
        f"active_tab_background {c['bg']}",
        f"inactive_tab_foreground {c['comment']}",
        f"inactive_tab_background {c['bg_dark']}",
        f"tab_bar_background {c['bg_dark']}",
        f"mark1_background {c['blue']}",
        f"mark2_background {c['violet']}",
        f"mark3_background {c['cyan']}",
        "",
    ]
    out += [f"color{i} {col}" for i, col in enumerate(c["ansi"])]
    return "\n".join(out) + "\n"


def alacritty(spec):
    c = colours(spec)

    def block(name, cols):
        return (
            f"[colors.{name}]\n"
            + "\n".join(f'{n} = "{cols[i]}"' for i, n in enumerate(ANSI_NAMES))
            + "\n"
        )

    return (
        header(spec)
        + f'\n[colors.primary]\nbackground = "{c["bg"]}"\nforeground = "{c["fg"]}"\n'
        f'dim_foreground = "{c["muted"]}"\nbright_foreground = "{c["fg_bright"]}"\n'
        f'\n[colors.cursor]\ntext = "{c["bg"]}"\ncursor = "{c["fg"]}"\n'
        f'\n[colors.selection]\ntext = "CellForeground"\nbackground = "{c["bg_sel"]}"\n'
        f'\n[colors.search.matches]\nforeground = "{c["bg"]}"\nbackground = "{c["yellow"]}"\n'
        f'\n[colors.search.focused_match]\nforeground = "{c["bg"]}"\nbackground = "{c["blue"]}"\n\n'
        + block("normal", c["ansi"][:8])
        + "\n"
        + block("bright", c["ansi"][8:])
        + "\n"
        + block("dim", c["ansi_dim"])
    )


def ghostty(spec):
    c = colours(spec)
    out = [header(spec)] + [f"palette = {i}={col}" for i, col in enumerate(c["ansi"])]
    out += [
        f"background = {c['bg']}",
        f"foreground = {c['fg']}",
        f"cursor-color = {c['fg']}",
        f"cursor-text = {c['bg']}",
        f"selection-background = {c['bg_sel']}",
        f"selection-foreground = {c['fg_bright']}",
    ]
    return "\n".join(out) + "\n"


def wezterm(spec):
    c = colours(spec)
    q = lambda cols: "[" + ", ".join(f'"{x}"' for x in cols) + "]"
    return (
        header(spec)
        + f'\n[colors]\nforeground = "{c["fg"]}"\nbackground = "{c["bg"]}"\n'
        f'cursor_bg = "{c["fg"]}"\ncursor_fg = "{c["bg"]}"\ncursor_border = "{c["fg"]}"\n'
        f'selection_fg = "{c["fg_bright"]}"\nselection_bg = "{c["bg_sel"]}"\n'
        f'scrollbar_thumb = "{c["bg_sel"]}"\nsplit = "{c["border"]}"\n'
        f'ansi = {q(c["ansi"][:8])}\nbrights = {q(c["ansi"][8:])}\n'
        f'\n[colors.tab_bar]\nbackground = "{c["bg_dark"]}"\n'
        f'\n[colors.tab_bar.active_tab]\nbg_color = "{c["bg"]}"\nfg_color = "{c["fg_bright"]}"\n'
        f'\n[colors.tab_bar.inactive_tab]\nbg_color = "{c["bg_dark"]}"\nfg_color = "{c["comment"]}"\n'
        f'\n[metadata]\nname = "{spec["name"]}"\nauthor = "{AUTHOR}"\norigin_url = "{REPO}"\n'
    )


def foot(spec):
    c = colours(spec)
    n = lambda h: h.lstrip("#")
    out = [
        header(spec),
        "# foot 1.26+; rename the section to [colors] for older versions",
        f"[colors-{spec['appearance']}]",
        f"foreground={n(c['fg'])}",
        f"background={n(c['bg'])}",
        f"selection-foreground={n(c['fg_bright'])}",
        f"selection-background={n(c['bg_sel'])}",
        f"urls={n(c['blue'])}",
    ]
    out += [f"regular{i}={n(col)}" for i, col in enumerate(c["ansi"][:8])]
    out += [f"bright{i}={n(col)}" for i, col in enumerate(c["ansi"][8:])]
    out += [f"dim{i}={n(col)}" for i, col in enumerate(c["ansi_dim"])]
    return "\n".join(out) + "\n"


def windows_terminal(specs):
    schemes = []
    for spec in specs:
        c = colours(spec)
        names = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
        s = {
            "name": spec["name"],
            "background": c["bg"],
            "foreground": c["fg"],
            "cursorColor": c["fg"],
            "selectionBackground": c["bg_sel"],
        }
        for i, nm in enumerate(names):
            s[nm] = c["ansi"][i]
            s["bright" + nm.capitalize()] = c["ansi"][i + 8]
        schemes.append(s)
    return json.dumps(schemes, indent=2) + "\n"


def xresources(spec):
    c = colours(spec)
    out = [
        header(spec, "!"),
        f"*.foreground: {c['fg']}",
        f"*.background: {c['bg']}",
        f"*.cursorColor: {c['fg']}",
    ]
    out += [f"*.color{i}: {col}" for i, col in enumerate(c["ansi"])]
    return "\n".join(out) + "\n"


def iterm(spec):
    c = colours(spec)

    def entry(key, h):
        r, g, b = (v / 255 for v in rgb(h))
        return (
            f"\t<key>{key}</key>\n\t<dict>\n"
            f"\t\t<key>Alpha Component</key>\n\t\t<real>1</real>\n"
            f"\t\t<key>Blue Component</key>\n\t\t<real>{b:.6f}</real>\n"
            f"\t\t<key>Color Space</key>\n\t\t<string>sRGB</string>\n"
            f"\t\t<key>Green Component</key>\n\t\t<real>{g:.6f}</real>\n"
            f"\t\t<key>Red Component</key>\n\t\t<real>{r:.6f}</real>\n\t</dict>\n"
        )

    items = [entry(f"Ansi {i} Color", col) for i, col in enumerate(c["ansi"])]
    items += [
        entry("Background Color", c["bg"]),
        entry("Foreground Color", c["fg"]),
        entry("Bold Color", c["fg_bright"]),
        entry("Cursor Color", c["fg"]),
        entry("Cursor Text Color", c["bg"]),
        entry("Selection Color", c["bg_sel"]),
        entry("Selected Text Color", c["fg_bright"]),
        entry("Link Color", c["blue"]),
    ]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n<dict>\n' + "".join(items) + "</dict>\n</plist>\n"
    )


def css(spec):
    c = colours(spec)
    base = "\n".join(f"  --{k}: {v};" for k, v in spec["palette"].items())
    sem = "\n".join(f"  --rime-{n.replace('_', '-')}: {c[n]};" for n in SLOT_NAMES.values())
    return (
        f"/* {spec['name']}: {spec['description']} */\n/* {REPO} */\n"
        f":root {{\n  /* base16 slots */\n{base}\n\n  /* colour names */\n{sem}\n}}\n"
    )


def fzf(spec):
    c = colours(spec)
    colors = ",".join(
        [
            f"fg:{c['fg']}",
            f"bg:{c['bg']}",
            f"hl:{c['blue']}",
            f"fg+:{c['fg_bright']}",
            f"bg+:{c['bg_alt']}",
            f"hl+:{c['blue']}",
            f"info:{c['muted']}",
            f"prompt:{c['violet']}",
            f"pointer:{c['cyan']}",
            f"marker:{c['green']}",
            f"spinner:{c['cyan']}",
            f"header:{c['yellow']}",
            f"border:{c['border']}",
            f"gutter:{c['bg']}",
        ]
    )
    return (
        header(spec) + f'export FZF_DEFAULT_OPTS="$FZF_DEFAULT_OPTS --color={colors}"\n'
    )


def tmux(spec):
    """tmux 3.2+ styles, dressed like the kitty and WezTerm tab bars; the 16 colors come from the terminal."""
    c = colours(spec)
    out = [
        header(spec),
        f'set -g status-style "fg={c["muted"]},bg={c["bg_dark"]}"',
        f'set -g window-status-style "fg={c["comment"]}"',
        f'set -g window-status-current-style "fg={c["fg_bright"]},bg={c["bg"]}"',
        f'set -g window-status-activity-style "fg={c["yellow"]}"',
        f'set -g window-status-bell-style "fg={c["red"]}"',
        f'set -g pane-border-style "fg={c["bg_sel"]}"',
        f'set -g pane-active-border-style "fg={c["blue"]}"',
        f'set -g message-style "fg={c["fg"]},bg={c["bg_alt"]}"',
        f'set -g message-command-style "fg={c["fg"]},bg={c["bg_alt"]}"',
        f'set -g mode-style "fg={c["fg_bright"]},bg={c["bg_sel"]}"',
        f'set -g copy-mode-match-style "fg={c["bg"]},bg={c["yellow"]}"',
        f'set -g copy-mode-current-match-style "fg={c["bg"]},bg={c["blue"]}"',
        f'set -g clock-mode-colour "{c["blue"]}"',
        f'set -g display-panes-colour "{c["comment"]}"',
        f'set -g display-panes-active-colour "{c["blue"]}"',
        "# -q: popups arrived in tmux 3.3, so 3.2 skips this line instead of failing",
        f'set -gq popup-border-style "fg={c["border"]}"',
    ]
    return "\n".join(out) + "\n"


def bat(spec):
    """bat's syntax theme: VS Code's token rules as a tmTheme. delta reads it from bat's cache."""
    c = colours(spec)
    rules = []
    for r in textmate_rules(c):
        s = dict(r["settings"])
        # syntect skips a whole rule whose fontStyle has a word it doesn't know, such as strikethrough
        style = " ".join(w for w in s.pop("fontStyle", "").split() if w in ("bold", "italic", "underline"))
        if style:
            s["fontStyle"] = style
        if s:
            rules.append({"name": r["name"], "scope": ", ".join(r["scope"]), "settings": s})
    editor = {
        "background": c["bg"],
        "foreground": c["fg"],
        "caret": c["fg"],
        "selection": c["bg_sel"],
        "lineHighlight": c["bg_alt"],
        "gutterForeground": c["comment"],
    }
    theme = {
        "name": spec["name"],
        "author": AUTHOR,
        "comment": f"{spec['description']} {REPO}",
        "settings": [{"settings": editor}] + rules,
    }
    return plistlib.dumps(theme, sort_keys=False).decode()


def delta(spec):
    """A delta feature named after the variant: diff backgrounds and decorations. The code takes bat's theme."""
    c = colours(spec)
    # lines get Neovim's DiffDelete and DiffAdd shades; the words that changed get twice as much red or green
    shade = lambda col, t: mix(c[col], c["bg"], 1 - t)
    out = [
        header(spec),
        f'[delta "{spec["slug"]}"]',
        f"\t{spec['appearance']} = true",
        f"\tsyntax-theme = {spec['slug']}",
        f'\tminus-style = syntax "{shade("red", 0.15)}"',
        f'\tminus-emph-style = syntax "{shade("red", 0.3)}"',
        f'\tplus-style = syntax "{shade("green", 0.15)}"',
        f'\tplus-emph-style = syntax "{shade("green", 0.3)}"',
        f'\tfile-style = "{c["blue"]}" bold',
        f'\tfile-decoration-style = "{c["bg_sel"]}" ul',
        f'\thunk-header-decoration-style = "{c["bg_sel"]}" box',
        f'\thunk-header-file-style = "{c["blue"]}"',
        f'\thunk-header-line-number-style = "{c["violet"]}"',
        f'\tline-numbers-minus-style = "{c["red"]}"',
        f'\tline-numbers-plus-style = "{c["green"]}"',
        f'\tline-numbers-zero-style = "{c["comment"]}"',
        f'\tline-numbers-left-style = "{c["bg_sel"]}"',
        f'\tline-numbers-right-style = "{c["bg_sel"]}"',
        f'\tblame-palette = "{c["bg"]} {c["bg_alt"]}"',
    ]
    return "\n".join(out) + "\n"


def noctalia(spec):
    """A Noctalia v5 palette: the shell's 16 colour roles, plus the terminal colours its templates write."""
    c = colours(spec)
    ansi = lambda cols: dict(zip(ANSI_NAMES, cols))
    # the shell is dressed like the GUI editors: bars and panels on the theme background, cards as
    # their popups, hover as their list and menu selection, text on accents as on their buttons
    mode = {
        "mPrimary": c["blue"],
        "mOnPrimary": c["bg"],
        "mSecondary": c["violet"],
        "mOnSecondary": c["bg"],
        "mTertiary": c["cyan"],
        "mOnTertiary": c["bg"],
        "mError": c["red"],
        "mOnError": c["bg"],
        "mSurface": c["bg"],
        "mOnSurface": c["fg"],
        "mSurfaceVariant": c["bg_alt"],
        "mOnSurfaceVariant": c["muted"],
        # Noctalia lifts the outline to 3:1 against the surface, then draws borders a shade darker;
        # starting from the editors' border keeps them as close to it as Noctalia allows
        "mOutline": c["border"],
        "mShadow": "#000000",
        "mHover": c["bg_sel"],
        "mOnHover": c["fg_bright"],
        "terminal": {
            "background": c["bg"],
            "foreground": c["fg"],
            "cursor": c["fg"],
            "cursorText": c["bg"],
            "selectionBg": c["bg_sel"],
            "selectionFg": c["fg_bright"],
            "normal": ansi(c["ansi"][:8]),
            "bright": ansi(c["ansi"][8:]),
        },
    }
    # Noctalia requires a dark mode and reuses it when there is no light one, so a light variant fills both
    return (
        {"dark": mode}
        if spec["appearance"] == "dark"
        else {"dark": mode, "light": mode}
    )


def swatch_svg(spec):
    """A small palette strip for the README."""
    p = spec["palette"]
    accents = list(SLOT_NAMES)[8:]
    w, h, gap, pad = 56, 40, 6, 16
    width = pad * 2 + len(accents) * w + (len(accents) - 1) * gap
    rects = "".join(
        f'<rect x="{pad + i * (w + gap)}" y="{pad}" width="{w}" height="{h}" rx="6" fill="{p[k]}"/>'
        f'<text x="{pad + i * (w + gap) + w / 2}" y="{pad + h + 16}" fill="{p["base03"]}" '
        f'font-family="monospace" font-size="10" text-anchor="middle">{p[k]}</text>'
        for i, k in enumerate(accents)
    )
    height = pad * 2 + h + 18
    # sized in units: some viewers resolve a 100% background against the wrong box
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}"><rect width="{width}" height="{height}" rx="10" fill="{p["base00"]}"/>'
        f"{rects}</svg>\n"
    )


def icon_svg(spec):
    """The extension icon: a frost crystal with blue, cyan and violet arms."""
    p = spec["palette"]

    def line(x1, y1, x2, y2, colour):
        return (
            f'<line x1="{x1}" y1="{y1}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colour}"/>'
        )

    arms = []
    for angle, colour in (
        (90, p["base0D"]),
        (270, p["base0D"]),
        (150, p["base0C"]),
        (330, p["base0C"]),
        (210, p["base0E"]),
        (30, p["base0E"]),
    ):

        def step(x, y, length, a):
            return x + length * math.cos(math.radians(a)), y - length * math.sin(
                math.radians(a)
            )

        arms.append(line(128, 128, *step(128, 128, 82, angle), colour))
        for dist, length in (
            (48, 22),
            (68, 14),
        ):  # two pairs of side branches along each arm
            bx, by = step(128, 128, dist, angle)
            for turn in (40, -40):
                arms.append(
                    line(
                        f"{bx:.1f}",
                        f"{by:.1f}",
                        *step(bx, by, length, angle + turn),
                        colour,
                    )
                )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
        f'<rect width="256" height="256" rx="56" fill="{p["base00"]}"/>'
        f'<rect x="1.5" y="1.5" width="253" height="253" rx="55" fill="none" stroke="{p["base02"]}" stroke-width="3"/>'
        f'<g stroke-width="10" stroke-linecap="round">{"".join(arms)}</g>'
        f'<circle cx="128" cy="128" r="10" fill="{p["base07"]}"/></svg>\n'
    )


# --------------------------------------------------------------------------- main


def load():
    """The inputs: every palette in ORDER, and the licence text."""
    specs = [
        json.loads((ROOT / "palettes" / f"{slug}.json").read_text(encoding="utf-8"))
        for slug in ORDER
    ]
    for slug, spec in zip(ORDER, specs):
        # nvim_key and the plugin's colors_name read a slug as "rime" or "rime-<key>", and it
        # becomes part of every generated file's path
        if not re.fullmatch(r"rime(-[a-z0-9]+)*", spec["slug"]):
            raise ValueError(f'{spec["slug"]}: a variant\'s slug is "rime" or "rime-" and lowercase letters, digits and dashes')
        # a copied palette that keeps its old slug would overwrite that variant's files
        if spec["slug"] != slug:
            raise ValueError(f'palettes/{slug}.json: its slug is "{spec["slug"]}"; make it "{slug}"')
        # Python reads anything but "dark" as light and Lua anything but "light" as dark
        if spec.get("appearance") not in ("dark", "light"):
            raise ValueError(f'palettes/{slug}.json: appearance is "dark" or "light"')
    return specs, (ROOT / "LICENSE").read_text(encoding="utf-8")


# The ports that are one file per variant: (port, its path with {slug} for the variant, its text).
# build() writes them and ALL_IN_ONE's from here, and the website offers them as downloads.
PER_VARIANT = [
    ("helix", "general/helix/{slug}.toml", helix),
    ("sublime", "general/sublime/{slug}.sublime-color-scheme", sublime),
    ("base16", "general/base16/{slug}.yaml", base16_yaml),
    ("kitty", "general/kitty/{slug}.conf", kitty),
    ("alacritty", "general/alacritty/{slug}.toml", alacritty),
    ("ghostty", "general/ghostty/{slug}", ghostty),
    ("wezterm", "general/wezterm/{slug}.toml", wezterm),
    ("foot", "general/foot/{slug}.ini", foot),
    ("xresources", "general/xresources/{slug}.Xresources", xresources),
    ("iterm2", "general/iterm2/{slug}.itermcolors", iterm),
    ("css", "general/css/{slug}.css", css),
    ("fzf", "general/fzf/{slug}.sh", fzf),
    ("tmux", "general/tmux/{slug}.conf", tmux),
    ("bat", "general/bat/{slug}.tmTheme", bat),
    ("delta", "general/delta/{slug}.gitconfig", delta),
    ("noctalia", "general/noctalia/{slug}.json", lambda spec: json.dumps(noctalia(spec), indent=2) + "\n"),
]


# The ports that are one file holding every variant: (port, its path, its text from all the specs).
ALL_IN_ONE = [
    ("zed", "zed/themes/rime.json", zed_themes),
    ("windows-terminal", "general/windows-terminal/rime.json", windows_terminal),
]


def site_data(specs, downloads):
    """What site/build.ts shows: the colour names, each variant's colours, the syntax roles and each port's files."""
    derived = [n for n, v in colours(specs[0]).items() if isinstance(v, str) and n not in SLOT_NAMES.values()]
    return {
        "version": VERSION,
        "colour_names": [{"name": n, "slot": s} for s, n in SLOT_NAMES.items()] + [{"name": n, "slot": None} for n in derived],
        "variants": [
            {
                "slug": spec["slug"],
                "name": spec["name"],
                "key": nvim_key(spec["slug"]),
                "appearance": spec["appearance"],
                "colours": {n: v for n, v in colours(spec).items() if isinstance(v, str)},
            }
            for spec in specs
        ],
        "syntax": [{"role": r, "colour": c, "style": st, "note": note} for r, (c, st, note) in SYNTAX.items()],
        "downloads": downloads,
    }


def build(specs, licence):
    """Every generated file as {path relative to the repository: contents}. Writes nothing."""
    files = {}
    for spec in specs:
        slug = spec["slug"]
        key = nvim_key(slug)
        files[f"lua/rime/palettes/{key}.lua"] = nvim_palette(spec)
        files[f"colors/{slug}.lua"] = f'require("rime").load("{key}")\n'
        files[f"lua/lualine/themes/{slug}.lua"] = (
            f'return require("rime.lualine").theme("{key}")\n'
        )
        files["vscode/" + VSCODE_THEME.format(slug=slug)] = (
            json.dumps(vscode_theme(spec), indent=2) + "\n"
        )
        for _, path, text in PER_VARIANT:
            files[path.format(slug=slug)] = text(spec)
        files[f"assets/palette-{slug}.svg"] = swatch_svg(spec)
    for _, path, text in ALL_IN_ONE:
        files[path] = text(specs)
    files["lua/rime/variants.lua"] = nvim_variants(specs)
    files["lua/rime/syntax.lua"] = nvim_syntax()
    files["zed/extension.toml"] = zed_extension()
    files["vscode/package.json"] = json.dumps(vscode_package(specs), indent=2) + "\n"
    files["assets/icon.svg"] = icon_svg(specs[0])
    # extension folders are published on their own, so each carries the licence
    for folder in ("zed", "vscode"):
        files[f"{folder}/LICENSE"] = licence
    downloads = {port: path for port, path, _ in PER_VARIANT + ALL_IN_ONE}
    files["site/data.json"] = json.dumps(site_data(specs, downloads), indent=2) + "\n"
    return files


def same_content(path, a, b):
    """Whether two versions of a generated file say the same thing, however they are formatted.

    JSON is compared as parsed values; anything else as its whitespace-separated tokens,
    so indentation, line endings and line wrapping don't count."""
    if path.endswith(".json"):
        try:
            return json.loads(a) == json.loads(b)
        except ValueError:
            return False
    return a.split() == b.split()


def stale(files):
    """The paths whose contents on disk differ from `files`, ignoring formatting."""
    return [
        path
        for path, text in files.items()
        if not (ROOT / path).is_file()
        or not same_content(path, (ROOT / path).read_text("utf-8"), text)
    ]


# paths that hold only generated files, so any other match is left over from an older build
GENERATED = [
    "general/*/*",
    "colors/*",
    "lua/lualine/themes/*",
    "lua/rime/palettes/*",
    "vscode/themes/*",
    "zed/themes/*",
    "assets/palette-*.svg",
]


def leftover(files):
    """Generated-looking files that `files` doesn't include, such as a renamed variant's."""
    return sorted(
        path.relative_to(ROOT).as_posix()
        for pattern in GENERATED
        for path in ROOT.glob(pattern)
        if path.is_file() and path.relative_to(ROOT).as_posix() not in files
    )


def main(args):
    if args not in ([], ["--check"]):
        print(__doc__, file=sys.stderr)
        return 2
    files = build(*load())
    old = leftover(files)
    for path in old:
        print(f"no longer generated, delete it: {path}")
    if args == ["--check"]:
        outdated = stale(files)
        for path in outdated:
            print(f"out of date: {path}")
        if outdated:
            print("run python3 tools/build.py to regenerate them", file=sys.stderr)
        return 1 if outdated or old else 0
    outdated = stale(files)  # leave files that only differ in formatting alone
    for path in outdated:
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[path].encode("utf-8"))  # always UTF-8 with LF line endings
    print(f"wrote {len(outdated)} of {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
