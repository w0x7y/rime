#!/usr/bin/env python3
"""Generate every Rime port from the palettes in ../palettes.

Usage: python3 tools/build.py            rewrite every generated file
       python3 tools/build.py --check    list generated files that are out of date or left over, exit 1 if any

The palettes are the single source of truth for colours, and SYNTAX below for which
colour each kind of code gets. Edit either, run this script, and the Neovim modules,
Zed theme, VS Code themes, extension manifests, icon, the terminal / general-purpose
files and the website's site/data.json are all rewritten. Only the Python standard library is used.
"""

import base64
import colorsys
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


# --------------------------------------------------------------------------- vim


def xterm256(h):
    """The nearest of xterm's 240 fixed colours (the 6x6x6 cube and the gray ramp) to h."""
    steps = [0, 95, 135, 175, 215, 255]
    cube = [(16 + 36 * r + 6 * g + b, (steps[r], steps[g], steps[b])) for r in range(6) for g in range(6) for b in range(6)]
    grays = [(232 + i, (8 + 10 * i,) * 3) for i in range(24)]
    target = rgb(h)
    return min(cube + grays, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], target)))[0]


def vim(spec):
    """A Vim colorscheme: Neovim's editor and legacy syntax groups, in true colour with 256-colour fallbacks."""
    c = colours(spec)

    def role(name):
        fg, style, _ = SYNTAX[name]
        return {"fg": fg, "style": style}

    # group: {fg, bg, sp: colour names, style: attributes}, or the name of a group to link to
    groups = {
        "Normal": {"fg": "fg", "bg": "bg"},
        "NormalFloat": {"fg": "fg", "bg": "bg_alt"},
        "Cursor": {"fg": "bg", "bg": "fg"},
        "lCursor": "Cursor",
        "CursorIM": "Cursor",
        "CursorLine": {"bg": "bg_alt"},
        "CursorColumn": {"bg": "bg_alt"},
        "ColorColumn": {"bg": "colorcolumn"},
        "CursorLineNr": {"fg": "fg_bright", "style": "bold"},
        "LineNr": {"fg": "comment"},
        "SignColumn": {"fg": "comment"},
        "FoldColumn": {"fg": "comment"},
        "Folded": {"fg": "muted", "bg": "bg_alt"},
        "VertSplit": {"fg": "border"},
        "StatusLine": {"fg": "muted", "bg": "bg_alt"},
        "StatusLineNC": {"fg": "comment", "bg": "bg_alt"},
        "StatusLineTerm": "StatusLine",
        "StatusLineTermNC": "StatusLineNC",
        "TabLine": {"fg": "comment", "bg": "bg_alt"},
        "TabLineSel": {"fg": "fg_bright", "bg": "bg", "style": "bold"},
        "TabLineFill": {"bg": "bg_dark"},
        "ToolbarLine": {"bg": "bg_alt"},
        "ToolbarButton": {"fg": "fg_bright", "bg": "bg_sel", "style": "bold"},
        "Pmenu": {"fg": "fg", "bg": "bg_alt"},
        "PmenuSel": {"bg": "bg_sel", "style": "bold"},
        "PmenuSbar": {"bg": "bg_alt"},
        "PmenuThumb": {"bg": "comment"},
        "PmenuMatch": {"fg": "blue", "style": "bold"},
        "PmenuMatchSel": {"fg": "blue", "bg": "bg_sel", "style": "bold"},
        "PmenuKind": {"fg": "violet"},
        "PmenuKindSel": {"fg": "violet", "bg": "bg_sel"},
        "PmenuExtra": {"fg": "muted"},
        "PmenuExtraSel": {"fg": "muted", "bg": "bg_sel"},
        "WildMenu": "PmenuSel",
        "Visual": {"bg": "bg_sel"},
        "VisualNOS": "Visual",
        "Search": {"fg": "fg_bright", "bg": "search"},
        "CurSearch": {"fg": "bg", "bg": "yellow", "style": "bold"},
        "IncSearch": "CurSearch",
        "MatchParen": {"fg": "fg_bright", "bg": "bg_sel", "style": "bold"},
        "NonText": {"fg": "whitespace"},
        "EndOfBuffer": {"fg": "bg_sel"},
        "SpecialKey": {"fg": "whitespace"},
        "Conceal": {"fg": "comment"},
        "Directory": {"fg": "blue"},
        "Title": {"fg": "blue", "style": "bold"},
        "Question": {"fg": "green"},
        "MoreMsg": {"fg": "green"},
        "ModeMsg": {"fg": "fg", "style": "bold"},
        "ErrorMsg": {"fg": "red"},
        "WarningMsg": {"fg": "yellow"},
        "QuickFixLine": {"bg": "bg_sel", "style": "bold"},
        "SpellBad": {"sp": "red", "style": "undercurl"},
        "SpellCap": {"sp": "yellow", "style": "undercurl"},
        "SpellRare": {"sp": "violet", "style": "undercurl"},
        "SpellLocal": {"sp": "cyan", "style": "undercurl"},
        "DiffAdd": {"bg": "diff_add"},
        "DiffChange": {"bg": "diff_change"},
        "DiffDelete": {"fg": "red", "bg": "diff_delete"},
        "DiffText": {"bg": "diff_text"},
        "Added": role("diff.plus"),
        "Changed": role("diff.delta"),
        "Removed": role("diff.minus"),
        "diffAdded": "Added",
        "diffChanged": "Changed",
        "diffRemoved": "Removed",
        "diffFile": {"fg": "blue", "style": "bold"},
        "diffLine": role("diff.range"),
        "diffIndexLine": {"fg": "muted"},
        "Comment": role("comment"),
        "Constant": role("constant"),
        "String": role("string"),
        "Character": {"fg": "green"},
        "Number": role("number"),
        "Boolean": role("boolean"),
        "Float": role("number"),
        "Identifier": role("variable"),
        "Function": role("function"),
        "Statement": role("keyword"),
        "Conditional": role("keyword.conditional"),
        "Repeat": role("keyword.repeat"),
        "Label": role("label"),
        "Operator": role("operator"),
        "Keyword": role("keyword"),
        "Exception": role("keyword.exception"),
        "PreProc": role("keyword.directive"),
        "Include": role("keyword.import"),
        "Define": {"fg": "violet"},
        "Macro": role("function.macro"),
        "PreCondit": role("keyword.directive"),
        "Type": role("type"),
        "StorageClass": role("keyword.modifier"),
        "Structure": role("type"),
        "Typedef": role("type"),
        "Special": {"fg": "cyan"},
        "SpecialChar": {"fg": "cyan"},
        "Tag": role("tag"),
        "Delimiter": role("punctuation"),
        "SpecialComment": role("comment.tag"),
        "Debug": {"fg": "red"},
        "Underlined": {"style": "underline"},
        "Ignore": {"fg": "comment"},
        "Error": {"fg": "red"},
        "Todo": {"fg": "bg", "bg": "yellow", "style": "bold"},
    }

    def hi(name, g):
        if isinstance(g, str):
            return f"hi! link {name} {g}"
        parts = [f"hi {name}"]
        for key, term in (("fg", "fg"), ("bg", "bg")):
            if g.get(key):
                h = c[g[key]]
                parts += [f"gui{term}={h}", f"cterm{term}={xterm256(h)}"]
        if g.get("sp"):
            parts.append(f"guisp={c[g['sp']]}")
        attrs = ",".join(g.get("style", "").split()) or "NONE"
        parts += [f"gui={attrs}", f"cterm={attrs}"]
        return " ".join(parts)

    ansi = ", ".join(f"'{h}'" for h in c["ansi"])
    return (
        header(spec, '"')
        + f"set background={spec['appearance']}\n"
        + "hi clear\n"
        + "if exists('syntax_on')\n  syntax reset\nendif\n"
        + f"let g:colors_name = '{spec['slug']}'\n\n"
        + "".join(hi(n, g) + "\n" for n, g in groups.items())
        + f"\nlet g:terminal_ansi_colors = [{ansi}]\n"
    )


# --------------------------------------------------------------------------- micro

# micro's colorscheme groups and the syntax role each takes. Its syntax files are regexes
# with coarse groups: `statement` holds every keyword, and `identifier` mostly functions.
MICRO_SYNTAX = {
    "comment": "comment",
    "identifier": "function",
    "identifier.class": "function",  # micro's syntax files use it for functions too
    "identifier.macro": "function.macro",
    "identifier.var": "variable",
    "constant": "constant",
    "constant.bool": "boolean",
    "constant.number": "number",
    "constant.specialChar": "string.escape",
    "constant.string": "string",
    "constant.string.url": "markup.link.url",
    "statement": "keyword",
    "symbol": "operator",
    "symbol.operator": "operator",
    "symbol.brackets": "punctuation",
    "symbol.tag": "tag",
    "preproc": "keyword.directive",
    "type": "type",
    "type.keyword": "keyword.modifier",
}


def micro(spec):
    """A micro colorscheme. micro picks the nearest of 256 colours itself when the terminal lacks true colour."""
    c = colours(spec)

    def link(fg=None, bg=None, style=""):
        return f'"{style + " " if style else ""}{c[fg] if fg else ""}{"," + c[bg] if bg else ""}"'

    groups = {"default": link("fg", "bg")}
    for group, r in MICRO_SYNTAX.items():
        fg, style, _ = SYNTAX[r]
        groups[group] = link(fg, style=style)
    groups |= {
        "special": link("cyan"),
        "underlined": link(style="underline"),
        "error": link("red"),
        "todo": link("bg", "yellow", "bold"),
        "ignore": link("comment"),
        "selection": link(bg="bg_sel"),
        "statusline": link("muted", "bg_alt"),
        "statusline.inactive": link("comment", "bg_alt"),
        "statusline.suggestions": link("fg", "bg_alt"),
        "tabbar": link("comment", "bg_alt"),
        "tabbar.active": link("fg_bright", "bg", "bold"),
        "indent-char": link("whitespace"),
        "line-number": link("comment", "bg"),
        "current-line-number": link("fg_bright", "bg", "bold"),
        "cursor-line": link(bg="bg_alt"),
        "color-column": link(bg="colorcolumn"),
        "gutter-info": link("blue"),
        "gutter-error": link("red"),
        "gutter-warning": link("yellow"),
        "diff-added": link("green"),
        "diff-modified": link("blue"),
        "diff-deleted": link("red"),
        "scrollbar": link("comment"),
        "divider": link("border", "bg"),
        "message": link("fg"),
        "error-message": link("red"),
        "match-brace": link("fg_bright", "bg_sel", "bold"),
        "hlsearch": link("fg_bright", "search"),
        "tab-error": link(bg="diff_delete"),
        "trailingws": link(bg="diff_delete"),
    }
    return header(spec) + "".join(f"color-link {g} {v}\n" for g, v in groups.items())


# --------------------------------------------------------------------------- emacs

# Emacs's font-lock faces and the syntax role each takes. Emacs has one keyword face,
# so `if`, `for` and `return` share the keyword colour.
EMACS_SYNTAX = {
    "font-lock-comment-face": "comment",
    "font-lock-comment-delimiter-face": "comment",
    "font-lock-doc-face": "string.documentation",
    "font-lock-doc-markup-face": "comment.tag",
    "font-lock-string-face": "string",
    "font-lock-escape-face": "string.escape",
    "font-lock-regexp-face": "string.regexp",
    "font-lock-regexp-grouping-backslash": "string.regexp",
    "font-lock-regexp-grouping-construct": "string.regexp",
    "font-lock-number-face": "number",
    "font-lock-constant-face": "constant",
    "font-lock-builtin-face": "function.builtin",
    "font-lock-keyword-face": "keyword",
    "font-lock-function-name-face": "function",
    "font-lock-function-call-face": "function",
    "font-lock-variable-name-face": "variable",
    "font-lock-variable-use-face": "variable",
    "font-lock-type-face": "type",
    "font-lock-property-name-face": "property",  # keys and field definitions
    "font-lock-property-use-face": "variable.member",
    "font-lock-preprocessor-face": "keyword.directive",
    "font-lock-operator-face": "operator",
    "font-lock-negation-char-face": "operator",
    "font-lock-punctuation-face": "punctuation",
    "font-lock-bracket-face": "punctuation",
    "font-lock-delimiter-face": "punctuation",
    "font-lock-misc-punctuation-face": "punctuation",
    "diff-added": "diff.plus",
    "diff-removed": "diff.minus",
    "diff-changed": "diff.delta",
    "diff-hunk-header": "diff.range",
}


def emacs(spec):
    """An Emacs theme, named after the variant: (load-theme 'rime t)."""
    c = colours(spec)
    slug = spec["slug"]

    def face(fg=None, bg=None, style="", curl=None, inherit=None, box=None):
        a = []
        if inherit:
            a.append(f":inherit {inherit}")
        if fg:
            a.append(f':foreground "{c[fg]}"')
        if bg:
            a.append(f':background "{c[bg]}"')
        words = style.split()
        if "bold" in words:
            a.append(":weight bold")
        if "italic" in words:
            a.append(":slant italic")
        if "underline" in words:
            a.append(":underline t")
        if "strikethrough" in words:
            a.append(":strike-through t")
        if curl:
            a.append(f':underline (:style wave :color "{c[curl]}")')
        if box:
            a.append(f':box (:line-width 4 :color "{c[box]}")')
        return " ".join(a)

    faces = {}
    for name, r in EMACS_SYNTAX.items():
        fg, style, _ = SYNTAX[r]
        faces[name] = face(fg, style=style)
    faces |= {
        "default": face("fg", "bg"),
        "cursor": face(bg="fg"),
        "region": face(bg="bg_sel", inherit="nil"),  # nil: keep the text's own colours
        "secondary-selection": face(bg="border"),
        "highlight": face(bg="bg_sel"),
        "hl-line": face(bg="bg_alt"),
        "fringe": face("comment", "bg"),
        "line-number": face("comment", "bg"),
        "line-number-current-line": face("fg_bright", "bg_alt", "bold"),
        "fill-column-indicator": face("bg_sel"),
        "vertical-border": face("border"),
        "window-divider": face("border"),
        "mode-line": face("muted", "bg_alt", box="bg_alt"),
        "mode-line-inactive": face("comment", "bg_dark", box="bg_dark"),
        "mode-line-buffer-id": face("fg_bright", style="bold"),
        "header-line": face("muted", "bg_alt"),
        "tab-bar": face("comment", "bg_dark"),
        "tab-bar-tab": face("fg_bright", "bg", "bold"),
        "tab-bar-tab-inactive": face("comment", "bg_alt"),
        "minibuffer-prompt": face("blue", style="bold"),
        "isearch": face("bg", "yellow", "bold"),
        "lazy-highlight": face("fg_bright", "search"),
        "isearch-fail": face("red", "diag_error"),
        "match": face("fg_bright", "search"),
        "show-paren-match": face("fg_bright", "bg_sel", "bold"),
        "show-paren-mismatch": face("bg", "red", "bold"),
        "link": face("blue", style="underline"),
        "link-visited": face("violet", style="underline"),
        "error": face("red"),
        "warning": face("yellow"),
        "success": face("green"),
        "font-lock-warning-face": face("yellow", style="bold"),
        "shadow": face("comment"),
        "trailing-whitespace": face(bg="diff_delete"),
        "whitespace-space": face("whitespace"),
        "whitespace-tab": face("whitespace"),
        "whitespace-newline": face("whitespace"),
        "whitespace-trailing": face(bg="diff_delete"),
        "tooltip": face("fg", "bg_alt"),
        "completions-common-part": face("blue", style="bold"),
        "completions-first-difference": face("fg_bright", style="bold"),
        "flymake-error": face(curl="red"),
        "flymake-warning": face(curl="yellow"),
        "flymake-note": face(curl="cyan"),
        "diff-refine-added": face(bg="diff_add", style="bold"),
        "diff-refine-removed": face(bg="diff_delete", style="bold"),
        "diff-refine-changed": face(bg="diff_text", style="bold"),
        "diff-header": face("muted", "bg_alt"),
        "diff-file-header": face("blue", "bg_alt", "bold"),
    }
    # the 16 terminal colours, for shell, term and compilation buffers (Emacs 28+)
    for i, name in enumerate(ANSI_NAMES):
        for prefix, h in (("", c["ansi"][i]), ("bright-", c["ansi"][i + 8])):
            faces[f"ansi-color-{prefix}{name}"] = f':foreground "{h}" :background "{h}"'
    body = "\n".join(f" '({name} ((t ({attrs}))))" for name, attrs in faces.items())
    return (
        f";;; {slug}-theme.el --- {spec['name']}: {spec['description']}  -*- lexical-binding: t -*-\n"
        f";; {REPO}\n;; Generated by tools/build.py from palettes/{slug}.json. Do not edit.\n\n"
        ";;; Code:\n\n"
        f'(deftheme {slug} "{spec["name"]}: {spec["description"]}")\n\n'
        f"(custom-theme-set-faces\n '{slug}\n{body})\n\n"
        f"(provide-theme '{slug})\n\n"
        f";;; {slug}-theme.el ends here\n"
    )


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



def warp(spec):
    """A Warp theme. Warp shades its own chrome from the background, the accent and `details`."""
    c = colours(spec)
    block = lambda cols: "".join(f'    {n}: "{cols[i]}"\n' for i, n in enumerate(ANSI_NAMES))
    return (
        header(spec)
        + f'name: "{spec["name"]}"\naccent: "{c["blue"]}"\ncursor: "{c["fg"]}"\n'
        f'background: "{c["bg"]}"\nforeground: "{c["fg"]}"\n'
        f'details: {"darker" if spec["appearance"] == "dark" else "lighter"}\n'
        "terminal_colors:\n  normal:\n" + block(c["ansi"][:8]) + "  bright:\n" + block(c["ansi"][8:])
    )


def css_block(selector, props):
    return selector + " {\n" + "".join(f"  --{k}: {v};\n" for k, v in props.items()) + "}\n"


# Obsidian's code block colours and the syntax role each takes. Prism, which highlights them,
# puts numbers, booleans and constants in one `value` group, and regexes in `important`.
OBSIDIAN_SYNTAX = {
    "comment": "comment",
    "function": "function",
    "important": "string.regexp",
    "keyword": "keyword",
    "operator": "operator",
    "property": "property",
    "punctuation": "punctuation",
    "string": "string",
    "tag": "tag",
    "value": "constant",
}


def obsidian(spec):
    """An Obsidian CSS snippet over the default theme, dressed like the GUI editors: sidebars in the chrome shade."""
    c = colours(spec)
    accent_hsl = colorsys.rgb_to_hls(*(v / 255 for v in rgb(c["blue"])))
    accents = {"red": "red", "orange": "yellow", "yellow": "yellow", "green": "green", "cyan": "cyan", "blue": "blue", "purple": "violet", "pink": "pink"}
    v = {
        "color-base-00": c["bg"],
        "color-base-05": c["colorcolumn"],
        "color-base-10": c["bg_alt"],
        "color-base-20": c["bg_dark"],
        "color-base-25": c["bg_alt"],
        "color-base-30": c["border"],
        "color-base-35": c["bg_sel"],
        "color-base-40": c["whitespace"],
        "color-base-50": c["comment"],
        "color-base-60": c["comment"],
        "color-base-70": c["muted"],
        "color-base-100": c["fg"],
        "color-accent": c["blue"],
        "color-accent-1": lift(spec, c["blue"], 0.1),
        "color-accent-2": lift(spec, c["blue"], 0.2),
        "color-accent-hsl": f"{round(accent_hsl[0] * 360)}, {round(accent_hsl[2] * 100)}%, {round(accent_hsl[1] * 100)}%",
    }
    for name, colour in accents.items():
        v[f"color-{name}"] = c[colour]
        v[f"color-{name}-rgb"] = ", ".join(str(n) for n in rgb(c[colour]))
    v |= {
        "background-primary": c["bg"],
        "background-primary-alt": c["bg_alt"],
        "background-secondary": c["bg_dark"],
        "background-secondary-alt": c["bg_alt"],
        "background-modifier-hover": alpha(c["fg"], 0.08),
        "background-modifier-active-hover": alpha(c["blue"], 0.15),
        "background-modifier-border": c["border"],
        "background-modifier-border-hover": c["bg_sel"],
        "background-modifier-border-focus": c["bg_sel"],
        "background-modifier-form-field": c["bg_alt"],
        "background-modifier-error": c["red"],
        "background-modifier-success": c["green"],
        "text-normal": c["fg"],
        "text-muted": c["muted"],
        "text-faint": c["comment"],
        "text-on-accent": c["bg"],
        "text-accent": c["blue"],
        "text-accent-hover": c["cyan"],
        "text-selection": c["bg_sel"],
        "text-highlight-bg": alpha(c["yellow"], 0.3),
        "text-error": c["red"],
        "text-warning": c["yellow"],
        "text-success": c["green"],
        "interactive-normal": c["bg_alt"],
        "interactive-hover": c["bg_sel"],
        "interactive-accent": c["blue"],
        "interactive-accent-hover": lift(spec, c["blue"], 0.15),
        "code-background": c["bg_alt"],
        "code-normal": c["fg"],
    }
    v |= {f"code-{name}": syntax(c, role)[0] for name, role in OBSIDIAN_SYNTAX.items()}
    v |= {f"h{i}-color": syntax(c, "markup.heading")[0] for i in range(1, 7)}
    return (
        f"/* {spec['name']}: {spec['description']} */\n/* {REPO} */\n"
        f"/* turn it on under Appearance > CSS snippets, with Obsidian's base color scheme set to {spec['appearance']} */\n"
        + css_block(f".theme-{spec['appearance']}", v)
    )


def discord(spec):
    """A Discord theme for BetterDiscord and Vencord: the chat on the background, the lists around it in the chrome shade."""
    c = colours(spec)
    hover, selected = alpha(c["bg_sel"], 0.5), c["bg_sel"]
    v = {
        # Discord's older names, which some screens and plugins still read
        "background-primary": c["bg"],
        "background-secondary": c["bg_dark"],
        "background-secondary-alt": c["bg_dark"],
        "background-tertiary": c["bg_dark"],
        "background-accent": c["bg_sel"],
        "background-floating": c["bg_alt"],
        "background-nested-floating": c["bg_alt"],
        "background-mobile-primary": c["bg"],
        "background-mobile-secondary": c["bg_dark"],
        "background-modifier-hover": hover,
        "background-modifier-active": selected,
        "background-modifier-selected": selected,
        "background-modifier-accent": c["border"],
        "channeltextarea-background": c["bg_alt"],
        "header-primary": c["fg_bright"],
        "header-secondary": c["muted"],
        "text-normal": c["fg"],
        "text-positive": c["green"],
        "text-warning": c["yellow"],
        "text-danger": c["red"],
        "interactive-normal": c["muted"],
        "interactive-hover": c["fg"],
        "interactive-active": c["fg_bright"],
        "brand-experiment": c["blue"],
        # the names since Discord's 2025 visual refresh
        "app-frame-background": c["bg_dark"],
        "app-frame-border": c["border"],
        "background-base-lowest": c["bg_dark"],
        "background-base-lower": c["bg"],
        "background-base-low": c["bg_dark"],
        "background-surface-high": c["bg_alt"],
        "background-surface-higher": c["bg_alt"],
        "background-surface-highest": c["bg_sel"],
        "background-mod-subtle": hover,
        "background-mod-muted": hover,
        "background-mod-normal": c["bg_alt"],
        "background-mod-strong": c["bg_sel"],
        "background-code": c["bg_dark"],
        "chat-background-default": c["bg"],
        "home-background": c["bg_dark"],
        "modal-background": c["bg_alt"],
        "modal-footer-background": c["bg_dark"],
        "card-background-default": c["bg_alt"],
        "border-subtle": c["border"],
        "border-normal": c["border"],
        "border-strong": c["bg_sel"],
        "text-default": c["fg"],
        "text-strong": c["fg_bright"],
        "text-subtle": c["muted"],
        "text-muted": c["comment"],
        "text-link": c["blue"],
        "text-brand": c["blue"],
        "text-feedback-critical": c["red"],
        "text-feedback-positive": c["green"],
        "text-feedback-warning": c["yellow"],
        "text-feedback-info": c["blue"],
        "channels-default": c["muted"],
        "channel-icon": c["muted"],
        "icon-default": c["muted"],
        "icon-subtle": c["muted"],
        "icon-strong": c["fg"],
        "icon-muted": c["comment"],
        "interactive-text-default": c["muted"],
        "interactive-text-hover": c["fg"],
        "interactive-text-active": c["fg_bright"],
        "interactive-icon-default": c["muted"],
        "interactive-icon-hover": c["fg"],
        "interactive-icon-active": c["fg_bright"],
        "interactive-muted": c["comment"],
        "interactive-background-hover": hover,
        "interactive-background-active": selected,
        "interactive-background-selected": selected,
        "input-background-default": c["bg_alt"],
        "input-border-default": c["border"],
        "input-text-default": c["fg"],
        "input-placeholder-text-default": c["comment"],
        "message-background-hover": c["bg_alt"],
        "mention-foreground": c["blue"],
        "mention-background": alpha(c["blue"], 0.2),
        "message-mentioned-background-default": alpha(c["yellow"], 0.08),
        "message-mentioned-background-hover": alpha(c["yellow"], 0.12),
        "status-danger": c["red"],
        "status-positive": c["green"],
        "status-warning": c["yellow"],
        "control-primary-background-default": c["blue"],
        "control-primary-background-hover": lift(spec, c["blue"], 0.1),
        "control-primary-background-active": lift(spec, c["blue"], 0.2),
        "control-primary-text-default": c["bg"],
        "control-primary-text-hover": c["bg"],
        "control-primary-text-active": c["bg"],
        "control-secondary-background-default": c["bg_alt"],
        "control-secondary-background-hover": c["bg_sel"],
        "control-secondary-background-active": c["bg_sel"],
        "control-secondary-text-default": c["fg"],
        "control-critical-primary-background-default": c["red"],
        "control-critical-primary-background-hover": lift(spec, c["red"], 0.1),
        "control-critical-primary-text-default": c["bg"],
        "scrollbar-auto-thumb": c["bg_sel"],
        "scrollbar-auto-track": "transparent",
        "scrollbar-thin-thumb": c["bg_sel"],
        "scrollbar-thin-track": "transparent",
        "brand-500": c["blue"],
        "brand-560": lift(spec, c["blue"], 0.1),
    }
    # the dark or light modes Discord can be in; a custom profile theme keeps its own colours
    modes = ["dark", "darker", "midnight"] if spec["appearance"] == "dark" else ["light"]
    meta = {"name": spec["name"], "author": AUTHOR, "description": spec["description"], "version": VERSION, "source": REPO}
    return (
        "/**\n" + "".join(f" * @{k} {val}\n" for k, val in meta.items()) + " */\n\n"
        + css_block(",\n".join(f".theme-{m}:not(.custom-user-profile-theme)" for m in modes), v)
    )


def spicetify(specs):
    """Spicetify's color.ini, a colour scheme per variant. Its colours are hex without the #."""
    out = [f"; Rime for Spotify, through Spicetify\n; {REPO}\n"]
    for spec in specs:
        c = colours(spec)
        keys = {
            "text": c["fg"],
            "subtext": c["muted"],
            "main": c["bg"],
            "main-elevated": c["bg_alt"],
            "highlight": c["bg_alt"],
            "highlight-elevated": c["bg_sel"],
            "sidebar": c["bg_dark"],
            "player": c["bg_dark"],
            "card": c["bg_alt"],
            "shadow": "#000000",
            "selected-row": c["fg"],
            "button": c["blue"],
            "button-active": lift(spec, c["blue"], 0.15),
            "button-disabled": c["comment"],
            "tab-active": c["bg_sel"],
            "notification": c["blue"],
            "notification-error": c["red"],
            "misc": c["comment"],
        }
        out.append(f"\n[{spec['slug']}]\n; {spec['description']}\n" + "".join(f"{k:<18} = {h.lstrip('#')}\n" for k, h in keys.items()))
    return "".join(out)


def msgpack(value):
    """The MessagePack encoding of the dicts, strings and small ints a Firefox Color theme holds."""
    if isinstance(value, dict):
        n = len(value)
        head = bytes([0x80 | n]) if n < 16 else b"\xde" + n.to_bytes(2, "big")
        return head + b"".join(msgpack(k) + msgpack(v) for k, v in value.items())
    if isinstance(value, list):
        return bytes([0x90 | len(value)]) + b"".join(msgpack(v) for v in value)
    if isinstance(value, str):
        b = value.encode()
        return (bytes([0xA0 | len(b)]) if len(b) < 32 else bytes([0xD9, len(b)])) + b
    if isinstance(value, int) and 0 <= value < 256:
        return bytes([value]) if value < 128 else bytes([0xCC, value])
    raise TypeError(f"msgpack() can't encode {value!r}")


def lzma_literals(data):
    """data as an .lzma stream of literals only: no compression, but bytes that depend on nothing
    else, where liblzma's can change between versions and leave the generated files stale."""
    lc, prob_init = 3, 1024
    is_match = [prob_init] * 4  # the state stays 0 after literals, so one per position state (pb = 2)
    literal = [prob_init] * (0x300 << lc)
    out = bytearray(b"\x5d" + (1 << 16).to_bytes(4, "little") + len(data).to_bytes(8, "little"))
    low, rng, cache, cache_size = 0, 0xFFFFFFFF, 0, 1

    def shift_low():
        nonlocal low, cache, cache_size
        if (low & 0xFFFFFFFF) < 0xFF000000 or low >> 32:
            carry, temp = low >> 32, cache
            while cache_size:
                out.append((temp + carry) & 0xFF)
                temp, cache_size = 0xFF, cache_size - 1
            cache = (low >> 24) & 0xFF
        cache_size += 1
        low = (low & 0x00FFFFFF) << 8

    def bit(probs, i, b):
        nonlocal low, rng
        bound = (rng >> 11) * probs[i]
        if b:
            low, rng = low + bound, rng - bound
            probs[i] -= probs[i] >> 5
        else:
            rng = bound
            probs[i] += (2048 - probs[i]) >> 5
        while rng < 1 << 24:
            rng = (rng << 8) & 0xFFFFFFFF
            shift_low()

    prev = 0
    for pos, byte in enumerate(data):
        bit(is_match, pos & 3, 0)
        base, symbol = (prev >> (8 - lc)) * 0x300, 1
        for i in range(7, -1, -1):
            b = (byte >> i) & 1
            bit(literal, base + symbol, b)
            symbol = symbol << 1 | b
        prev = byte
    for _ in range(5):
        shift_low()
    return bytes(out)


def firefox_color_url(theme):
    """A color.firefox.com link that opens theme: json-url's lzma codec, which is MessagePack, LZMA and URL-safe base64."""
    return "https://color.firefox.com/?theme=" + base64.urlsafe_b64encode(lzma_literals(msgpack(theme))).decode().rstrip("=")


def firefox(spec):
    """A page that opens the variant in Firefox Color, with the tab strip, sidebars and toolbar like the GUI editors'."""
    c = colours(spec)
    names = {
        "frame": "bg_dark",
        "frame_inactive": "bg_dark",
        "tab_background_text": "muted",
        "tab_background_separator": "border",
        "tab_selected": "bg",
        "tab_text": "fg_bright",
        "tab_line": "blue",
        "tab_loading": "blue",
        "toolbar": "bg",
        "toolbar_text": "fg",
        "toolbar_top_separator": "bg_dark",
        "toolbar_bottom_separator": "border",
        "toolbar_vertical_separator": "border",
        "toolbar_field": "bg_alt",
        "toolbar_field_text": "fg",
        "toolbar_field_border": "border",
        "toolbar_field_focus": "bg_alt",
        "toolbar_field_text_focus": "fg_bright",
        "toolbar_field_border_focus": "blue",
        "toolbar_field_highlight": "bg_sel",
        "toolbar_field_highlight_text": "fg_bright",
        "toolbar_field_separator": "border",
        "icons": "fg",
        "icons_attention": "blue",
        "button_background_hover": "bg_alt",
        "button_background_active": "bg_sel",
        "popup": "bg_alt",
        "popup_text": "fg",
        "popup_border": "border",
        "popup_highlight": "bg_sel",
        "popup_highlight_text": "fg_bright",
        "sidebar": "bg_dark",
        "sidebar_text": "fg",
        "sidebar_border": "border",
        "sidebar_highlight": "bg_sel",
        "sidebar_highlight_text": "fg_bright",
        "ntp_background": "bg",
        "ntp_text": "fg",
    }
    theme = {
        "colors": {k: dict(zip("rgb", rgb(c[n]))) for k, n in names.items()},
        "images": {"additional_backgrounds": []},
        "title": spec["name"],
    }
    url = firefox_color_url(theme)
    return (
        f"<!doctype html>\n<!-- {spec['name']}: {spec['description']} -->\n<!-- {REPO} -->\n"
        f'<meta charset="utf-8">\n<title>{spec["name"]} for Firefox Color</title>\n'
        f'<meta http-equiv="refresh" content="0; url={url}">\n'
        f'<p><a href="{url}">Open {spec["name"]} in Firefox Color</a></p>\n'
    )


def telegram(spec):
    """A Telegram Desktop palette. Keys it leaves out that Telegram defines through another key follow that key."""
    c = colours(spec)
    shade = lambda col, t: mix(c[col], c["bg"], 1 - t)
    keys = {
        "windowBg": c["bg"],
        "windowFg": c["fg"],
        "windowBgOver": c["bg_alt"],
        "windowBgRipple": c["bg_sel"],
        "windowSubTextFg": c["muted"],
        "windowSubTextFgOver": c["muted"],
        "windowBoldFg": c["fg_bright"],
        "windowBoldFgOver": c["fg_bright"],
        "windowBgActive": c["blue"],
        "windowFgActive": c["bg"],
        "windowActiveTextFg": c["blue"],
        "windowShadowFgFallback": c["bg_dark"],
        "activeButtonBgOver": lift(spec, c["blue"], 0.1),
        "activeButtonBgRipple": lift(spec, c["blue"], 0.2),
        "activeButtonSecondaryFg": c["bg_sel"],
        "activeLineFg": c["blue"],
        "activeLineFgError": c["red"],
        "lightButtonBgOver": c["bg_alt"],
        "lightButtonBgRipple": c["bg_sel"],
        "attentionButtonFg": c["red"],
        "attentionButtonFgOver": c["red"],
        "attentionButtonBgOver": c["diag_error"],
        "attentionButtonBgRipple": c["diff_delete"],
        "menuBg": c["bg_alt"],
        "menuBgOver": c["bg_sel"],
        "menuBgRipple": c["border"],
        "menuIconFg": c["muted"],
        "menuIconFgOver": c["fg"],
        "menuSubmenuArrowFg": c["muted"],
        "menuFgDisabled": c["comment"],
        "menuSeparatorFg": c["border"],
        "scrollBarBg": alpha(c["comment"], 0.6),
        "scrollBarBgOver": alpha(c["comment"], 0.9),
        "scrollBg": alpha(c["comment"], 0.1),
        "scrollBgOver": alpha(c["comment"], 0.2),
        "smallCloseIconFg": c["comment"],
        "smallCloseIconFgOver": c["muted"],
        "placeholderFgActive": c["comment"],
        "inputBorderFg": c["border"],
        "filterInputBorderFg": c["blue"],
        "filterInputActiveBg": c["bg_alt"],
        "filterInputInactiveBg": c["bg_alt"],
        "checkboxFg": c["comment"],
        "sliderBgInactive": c["bg_sel"],
        "tooltipBg": c["bg_alt"],
        "tooltipFg": c["fg"],
        "tooltipBorderFg": c["border"],
        "titleBg": c["bg_dark"],
        "titleFg": c["comment"],
        "titleFgActive": c["muted"],
        "titleButtonFg": c["comment"],
        "titleButtonBgOver": c["bg_alt"],
        "titleButtonFgOver": c["fg"],
        "titleButtonCloseBgOver": c["red"],
        "layerBg": alpha("#000000", 0.5),
        "boxBg": c["bg"],
        "boxDividerBg": c["bg_dark"],
        "boxTextFgGood": c["green"],
        "boxTextFgError": c["red"],
        "boxTitleFg": c["fg_bright"],
        "boxTitleAdditionalFg": c["muted"],
        "introCoverTopBg": c["blue"],
        "introCoverBottomBg": c["cyan"],
        "introCoverIconsFg": lift(spec, c["cyan"], 0.2),
        "dialogsBg": c["bg_dark"],
        "dialogsBgOver": c["bg_alt"],
        "dialogsBgActive": c["bg_sel"],
        "dialogsNameFgActive": c["fg_bright"],
        "dialogsTextFgActive": c["fg"],
        "dialogsDateFgActive": c["muted"],
        "dialogsChatIconFgActive": c["fg_bright"],
        "dialogsDraftFg": c["red"],
        "dialogsDraftFgActive": c["red"],
        "dialogsSendingIconFg": c["comment"],
        "dialogsSendingIconFgActive": c["muted"],
        "dialogsSentIconFg": c["green"],
        "dialogsSentIconFgOver": c["green"],
        "dialogsSentIconFgActive": c["green"],
        "dialogsUnreadBg": c["blue"],
        "dialogsUnreadFg": c["bg"],
        "dialogsUnreadBgMuted": c["comment"],
        "dialogsUnreadBgActive": c["blue"],
        "dialogsUnreadFgActive": c["bg"],
        "dialogsUnreadBgMutedActive": c["comment"],
        "dialogsVerifiedIconBgActive": c["blue"],
        "dialogsVerifiedIconFgActive": c["bg"],
        "dialogsOnlineBadgeFg": c["green"],
        "dialogsOnlineBadgeFgActive": c["green"],
        "dialogsRippleBgActive": c["border"],
        "searchedTextMatchBg": c["search"],
        "searchedTextMatchFg": c["fg_bright"],
        "searchedTextCurrentMatchBg": c["yellow"],
        "searchedTextCurrentMatchFg": c["bg"],
        "emojiIconFg": c["muted"],
        "stickerPreviewBg": alpha(c["bg"], 0.7),
        "historyComposeAreaBg": c["bg_alt"],
        "historyOutIconFg": c["green"],
        "historyOutIconFgSelected": c["green"],
        "historySendingOutIconFg": c["comment"],
        "historySendingInIconFg": c["comment"],
        "historyCallArrowInFg": c["green"],
        "historyCallArrowInFgSelected": c["green"],
        "historyUnreadBarBg": c["bg_alt"],
        "historyUnreadBarFg": c["blue"],
        "historyScrollBarBg": alpha(c["comment"], 0.6),
        "historyScrollBarBgOver": alpha(c["comment"], 0.9),
        "historyScrollBg": alpha(c["comment"], 0.1),
        "historyScrollBgOver": alpha(c["comment"], 0.2),
        "msgInBg": c["bg_alt"],
        "msgInBgSelected": c["bg_sel"],
        "msgOutBg": shade("blue", 0.22),
        "msgOutBgSelected": shade("blue", 0.35),
        "msgInServiceFg": c["blue"],
        "msgOutServiceFg": c["blue"],
        "msgOutServiceFgSelected": c["blue"],
        "msgInDateFg": c["comment"],
        "msgInDateFgSelected": c["muted"],
        "msgOutDateFg": c["muted"],
        "msgOutDateFgSelected": c["muted"],
        "msgServiceBg": alpha(c["bg_dark"], 0.7),
        "msgServiceBgSelected": alpha(c["bg_sel"], 0.8),
        "msgServiceFg": c["fg"],
        "msgInShadow": alpha("#000000", 0.15),
        "msgInShadowSelected": alpha("#000000", 0.15),
        "msgOutShadow": alpha("#000000", 0.15),
        "msgOutShadowSelected": alpha("#000000", 0.15),
        "msgSelectOverlay": alpha(c["blue"], 0.3),
        "msgStickerOverlay": alpha(c["blue"], 0.5),
        "msgOutReplyBarColor": c["blue"],
        "msgInMonoFg": c["cyan"],
        "msgOutMonoFg": c["cyan"],
        "msgDateImgBg": alpha(c["bg"], 0.6),
        "msgDateImgBgOver": alpha(c["bg"], 0.8),
        "msgDateImgBgSelected": alpha(c["bg_sel"], 0.8),
        "msgFileThumbLinkOutFg": c["blue"],
        "msgFileThumbLinkOutFgSelected": c["blue"],
        "msgFileInBgOver": lift(spec, c["blue"], 0.1),
        "msgFileInBgSelected": c["blue"],
        "msgFileOutBg": c["blue"],
        "msgFileOutBgSelected": c["blue"],
        "msgWaveformInActiveSelected": c["blue"],
        "msgWaveformInInactive": c["comment"],
        "msgWaveformInInactiveSelected": c["comment"],
        "msgWaveformOutActive": c["blue"],
        "msgWaveformOutActiveSelected": c["blue"],
        "msgWaveformOutInactive": c["comment"],
        "msgWaveformOutInactiveSelected": c["comment"],
        "msgBotKbOverBgAdd": alpha(c["fg"], 0.1),
        "botKbPrimaryBg": alpha(c["blue"], 0.8),
        "botKbDangerBg": alpha(c["red"], 0.8),
        "botKbSuccessBg": alpha(c["green"], 0.8),
        "toastBg": alpha(c["bg_alt"], 0.95),
        "toastFg": c["fg"],
        "profileStatusFgOver": c["muted"],
        "mediaPlayerDisabledFg": c["comment"],
        "sideBarBg": c["bg_dark"],
        "sideBarBgActive": c["bg_sel"],
        "sideBarBgRipple": c["border"],
        "sideBarTextFg": c["muted"],
        "sideBarTextFgActive": c["fg_bright"],
        "sideBarIconFg": c["muted"],
        "sideBarIconFgActive": c["blue"],
        "sideBarBadgeBg": c["blue"],
        "sideBarBadgeBgMuted": c["comment"],
        "sideBarBadgeFg": c["bg"],
    }
    # the colours of names and profile pictures in groups, in Telegram's order
    for i, name in enumerate(["red", "green", "yellow", "blue", "violet", "pink", "cyan", "steel"], 1):
        keys[f"historyPeer{i}NameFg"] = c[name]
        keys[f"historyPeer{i}UserpicBg"] = c[name]
    keys["historyPeerUserpicFg"] = c["bg"]
    return header(spec, "//") + "".join(f"{k}: {v};\n" for k, v in keys.items())



# fish's syntax colours and the syntax role each takes. fish has one colour for every keyword.
FISH_SYNTAX = {
    "command": "function",
    "keyword": "keyword",
    "quote": "string",
    "redirection": "operator",
    "end": "operator",
    "param": "variable.parameter",
    "option": "variable.parameter",
    "comment": "comment",
    "operator": "operator",
    "escape": "string.escape",
}


def fish(spec):
    """A fish theme for `fish_config theme choose`: the command line by SYNTAX, the prompt and pager like the editors'."""
    c = colours(spec)
    n = lambda name: c[name].lstrip("#")
    flags = {"bold": " --bold", "italic": " --italics", "underline": " --underline"}

    def role(r):
        colour, style = syntax(c, r)
        return colour.lstrip("#") + "".join(flags.get(w, "") for w in style.split())

    v = {"fish_color_normal": n("fg")}
    v |= {f"fish_color_{k}": role(r) for k, r in FISH_SYNTAX.items()}
    v |= {
        "fish_color_error": n("red"),
        "fish_color_autosuggestion": n("comment"),
        "fish_color_selection": f"--background={n('bg_sel')}",
        "fish_color_search_match": f"--background={n('bg_sel')}",
        "fish_color_valid_path": "--underline",
        "fish_color_history_current": "--bold",
        "fish_color_cancel": "--reverse",
        "fish_color_cwd": n("blue"),
        "fish_color_cwd_root": n("red"),
        "fish_color_user": n("green"),
        "fish_color_host": n("fg"),
        "fish_color_host_remote": n("yellow"),
        "fish_color_status": n("red"),
        "fish_pager_color_progress": f"{n('fg_bright')} --background={n('bg_sel')}",
        "fish_pager_color_prefix": f"{n('blue')} --bold",
        "fish_pager_color_completion": n("fg"),
        "fish_pager_color_description": n("comment"),
        "fish_pager_color_selected_background": f"--background={n('bg_sel')}",
    }
    return (
        header(spec)
        + f"# name: '{spec['name']}'\n# preferred_background: {n('bg')}\n\n"
        + "".join(f"{k} {val}\n" for k, val in v.items())
    )


def starship(spec):
    """A starship palette. Starship's modules name terminal colours, so the palette sets those to the 16 terminal colours, and adds the colour names."""
    c = colours(spec)
    names = ANSI_NAMES[:5] + ["purple"] + ANSI_NAMES[6:]  # starship calls magenta purple
    v = dict(zip(names, c["ansi"][:8]))
    v |= {f"bright-{name}": col for name, col in zip(names, c["ansi"][8:])}
    v |= {name: c[name] for name in SLOT_NAMES.values() if name not in v}
    return header(spec) + f"[palettes.{spec['slug']}]\n" + "".join(f'{k} = "{col}"\n' for k, col in v.items())


def lazygit(spec):
    """lazygit's theme, as a config file to list after your own in LG_CONFIG_FILE."""
    c = colours(spec)
    theme = {
        "activeBorderColor": [c["blue"], "bold"],
        "inactiveBorderColor": [c["comment"]],
        "searchingActiveBorderColor": [c["yellow"], "bold"],
        "optionsTextColor": [c["blue"]],
        "selectedLineBgColor": [c["bg_sel"]],
        "inactiveViewSelectedLineBgColor": [c["bg_alt"]],
        "cherryPickedCommitFgColor": [c["blue"]],
        "cherryPickedCommitBgColor": [c["bg_sel"]],
        "markedBaseCommitFgColor": [c["bg"]],
        "markedBaseCommitBgColor": [c["yellow"]],
        "unstagedChangesColor": [c["red"]],
        "defaultFgColor": [c["fg"]],
    }
    lines = "".join(f"    {k}:\n" + "".join(f"      - '{v}'\n" for v in vals) for k, vals in theme.items())
    return header(spec) + "gui:\n  theme:\n" + lines + f"  authorColors:\n    '*': '{c['violet']}'\n"


def dunst(spec):
    """A dunst drop-in: notifications in the popup shade, framed blue, or red when critical."""
    c = colours(spec)
    sections = {
        "global": {"separator_color": "frame", "highlight": c["blue"]},
        "urgency_low": {"background": c["bg_alt"], "foreground": c["muted"], "frame_color": c["bg_sel"]},
        "urgency_normal": {"background": c["bg_alt"], "foreground": c["fg"], "frame_color": c["blue"]},
        "urgency_critical": {"background": c["bg_alt"], "foreground": c["fg"], "frame_color": c["red"], "highlight": c["red"]},
    }
    return header(spec) + "\n".join(
        f"[{name}]\n" + "".join(f'    {k} = "{v}"\n' for k, v in keys.items()) for name, keys in sections.items()
    )


def mako(spec):
    """A mako config to include: the same notifications as the dunst port."""
    c = colours(spec)
    return header(spec) + (
        f"background-color={c['bg_alt']}\ntext-color={c['fg']}\nborder-color={c['blue']}\n"
        f"progress-color=over {c['bg_sel']}\n"
        f"\n[urgency=low]\ntext-color={c['muted']}\nborder-color={c['bg_sel']}\n"
        f"\n[urgency=critical]\nborder-color={c['red']}\n"
    )


def hyprland(spec):
    """A Hyprland Lua module (Hyprland 0.55+): window borders and groups, focused in blue and locked groups in yellow."""
    c = colours(spec)
    q = lambda name: f'"rgb({c[name].lstrip("#")})"'
    return header(spec, "--") + (
        "hl.config({\n"
        "    general = {\n"
        f"        col = {{ active_border = {q('blue')}, inactive_border = {q('bg_sel')}, "
        f"nogroup_border = {q('bg_sel')}, nogroup_border_active = {q('violet')} }},\n"
        "    },\n"
        "    group = {\n"
        f"        col = {{ border_active = {q('blue')}, border_inactive = {q('bg_sel')}, "
        f"border_locked_active = {q('yellow')}, border_locked_inactive = {q('bg_sel')} }},\n"
        "        groupbar = {\n"
        f"            text_color = {q('fg')},\n"
        f"            text_color_inactive = {q('comment')},\n"
        f"            col = {{ active = {q('blue')}, inactive = {q('bg_sel')}, "
        f"locked_active = {q('yellow')}, locked_inactive = {q('bg_sel')} }},\n"
        "        },\n"
        "    },\n"
        f"    misc = {{ background_color = {q('bg')} }},\n"
        "})\n"
    )


def zellij(spec):
    """A zellij 0.42+ theme: bars in the chrome shade as in the tmux port, blue for the focused tab, mode and pane."""
    c = colours(spec)
    accents = [c[n] for n in ("yellow", "cyan", "green", "violet")]  # emphasis_0 (key hints) to emphasis_3
    # component: (base, background or None to leave it unset, the four emphases)
    components = {
        "text_unselected": (c["fg"], c["bg_dark"], accents),
        "text_selected": (c["fg_bright"], c["bg_sel"], accents),
        # emphasis_1 is the hovered tab's background and emphasis_3 a tab's text when its bell rings
        "ribbon_unselected": (c["fg"], c["bg_sel"], [c["yellow"], c["bg_alt"], c["blue"], c["red"]]),
        "ribbon_selected": (c["bg"], c["blue"], [c["bg_dark"]] * 4),
        "table_title": (c["blue"], c["bg"], accents),
        "table_cell_unselected": (c["fg"], c["bg"], accents),
        "table_cell_selected": (c["fg_bright"], c["bg_sel"], accents),
        "list_unselected": (c["fg"], c["bg"], accents),
        "list_selected": (c["fg_bright"], c["bg_sel"], accents),
        # an unfocused frame colors its title too, so it takes the comment gray rather than bg_sel
        "frame_unselected": (c["comment"], None, accents),
        "frame_selected": (c["blue"], None, accents),
        "frame_highlight": (c["yellow"], None, [c["violet"]] + [c["yellow"]] * 3),
        "exit_code_success": (c["green"], None, accents),
        "exit_code_error": (c["red"], None, accents),
    }
    players = [c[n] for n in ("violet", "blue", "green", "yellow", "cyan", "pink", "red", "steel", "muted", "fg_bright")]

    def node(name, entries):
        return f"        {name} {{\n" + "".join(f'            {k} "{v}"\n' for k, v in entries) + "        }\n"

    out = []
    for name, (base, background, emphases) in components.items():
        entries = [("base", base)] + ([("background", background)] if background else [])
        out.append(node(name, entries + [(f"emphasis_{i}", e) for i, e in enumerate(emphases)]))
    out.append(node("multiplayer_user_colors", [(f"player_{i}", p) for i, p in enumerate(players, 1)]))
    return header(spec, "//") + f"themes {{\n    {spec['slug']} {{\n" + "".join(out) + "    }\n}\n"


def gitui(spec):
    """A gitui 0.28+ theme.ron: selection and focus as in the lazygit port. Diffs are highlighted with bat's theme."""
    c = colours(spec)
    theme = {
        "selected_tab": c["blue"],
        "block_title_focused": c["blue"],
        "command_fg": c["fg_bright"],
        "cmdbar_bg": c["bg_dark"],
        "selection_bg": c["bg_sel"],
        "selection_fg": c["fg_bright"],
        "disabled_fg": c["comment"],
        "diff_line_add": c["green"],
        "diff_line_delete": c["red"],
        "diff_file_added": c["green"],
        "diff_file_removed": c["red"],
        "diff_file_moved": c["violet"],
        "diff_file_modified": c["yellow"],
        "commit_hash": c["violet"],
        "commit_time": c["cyan"],
        "commit_author": c["green"],
        "danger_fg": c["red"],
        "push_gauge_bg": c["blue"],
        "push_gauge_fg": c["bg"],
        "tag_fg": c["pink"],
        "branch_fg": c["yellow"],
        "syntax": spec["slug"],  # the bat theme, copied next to theme.ron as <slug>.tmTheme
    }
    return header(spec, "//") + "(\n" + "".join(f'    {k}: Some("{v}"),\n' for k, v in theme.items()) + ")\n"


def btop(spec):
    """A btop theme: borders and selection as in the other ports; meters run from the dimmed to the bright terminal accent."""
    c = colours(spec)
    slot = {"red": 1, "green": 2, "yellow": 3, "blue": 4, "violet": 5, "cyan": 6}
    ramp = lambda name: (c["ansi_dim"][slot[name]], c["ansi"][slot[name]], c["ansi"][slot[name] + 8])
    load = (c["green"], c["yellow"], c["red"])
    v = {
        "main_bg": c["bg"],
        "main_fg": c["fg"],
        "title": c["fg_bright"],
        "hi_fg": c["blue"],
        "selected_bg": c["bg_sel"],
        "selected_fg": c["fg_bright"],
        "inactive_fg": c["comment"],
        "graph_text": c["muted"],
        "meter_bg": c["bg_sel"],
        "proc_misc": c["cyan"],
    }
    v |= {f"{box}_box": c["bg_sel"] for box in ("cpu", "mem", "net", "proc")}
    v["div_line"] = c["bg_sel"]
    gradients = {
        "temp": (c["blue"], c["violet"], c["red"]),
        "cpu": load,
        "free": ramp("green"),
        "cached": ramp("cyan"),
        "available": ramp("yellow"),
        "used": ramp("red"),
        "download": ramp("blue"),
        "upload": ramp("violet"),
        "process": load,
    }
    v |= {f"{k}_{end}": col for k, cols in gradients.items() for end, col in zip(("start", "mid", "end"), cols)}
    # btop 1.4.8 added the follow and banner keys; older versions skip keys they don't know
    v |= {
        "proc_pause_bg": c["red"],
        "proc_follow_bg": c["blue"],
        "proc_banner_bg": c["violet"],
        "proc_banner_fg": c["bg"],
        "followed_bg": c["blue"],
        "followed_fg": c["bg"],
    }
    return header(spec) + "".join(f'theme[{k}]="{col}"\n' for k, col in v.items())


def k9s(spec):
    """A k9s skin: tables, frames and selection as in the other ports, and resource YAML colored by SYNTAX."""
    c = colours(spec)
    bg, fg = c["bg"], c["fg"]
    skin = {
        "body": {
            "fgColor": fg, "bgColor": bg, "logoColor": c["blue"], "logoColorMsg": fg,
            "logoColorInfo": c["green"], "logoColorWarn": c["yellow"], "logoColorError": c["red"],
        },
        "prompt": {
            "fgColor": fg, "bgColor": bg, "suggestColor": c["comment"],
            "border": {"default": c["blue"], "command": c["violet"]},
        },
        "info": {
            "fgColor": fg, "sectionColor": c["muted"], "cpuColor": c["green"],
            "memColor": c["cyan"], "k9sRevColor": c["blue"],
        },
        "help": {
            "fgColor": fg, "bgColor": bg, "sectionColor": c["violet"],
            "keyColor": c["blue"], "numKeyColor": c["pink"],
        },
        "dialog": {
            "fgColor": fg, "bgColor": bg, "buttonFgColor": fg, "buttonBgColor": c["bg_sel"],
            "buttonFocusFgColor": bg, "buttonFocusBgColor": c["blue"],
            "labelFgColor": c["yellow"], "fieldFgColor": fg,
        },
        "frame": {
            "border": {"fgColor": c["bg_sel"], "focusColor": c["blue"]},
            "menu": {"fgColor": c["muted"], "keyColor": c["blue"], "numKeyColor": c["pink"]},
            "crumbs": {"fgColor": bg, "bgColor": c["muted"], "activeColor": c["blue"]},
            "status": {
                "newColor": c["blue"], "modifyColor": c["green"], "addColor": c["cyan"],
                "pendingColor": c["yellow"], "errorColor": c["red"], "highlightColor": c["pink"],
                "killColor": c["violet"], "completedColor": c["comment"],
            },
            "title": {
                "fgColor": c["fg_bright"], "bgColor": bg, "highlightColor": c["blue"],
                "counterColor": c["muted"], "filterColor": c["violet"],
            },
        },
        "views": {
            "charts": {
                "bgColor": bg, "dialBgColor": bg, "chartBgColor": bg,
                "defaultDialColors": [c["green"], c["red"]], "defaultChartColors": [c["green"], c["red"]],
                "resourceColors": {"cpu": [c["blue"], c["violet"]], "mem": [c["yellow"], c["pink"]]},
                "focusFgColor": c["fg_bright"], "focusBgColor": c["bg_sel"],
            },
            "table": {
                "fgColor": fg, "bgColor": bg, "cursorFgColor": c["fg_bright"], "cursorBgColor": c["bg_sel"],
                "markColor": c["yellow"],
                "header": {
                    "fgColor": c["muted"], "bgColor": bg, "sorterColor": c["cyan"],
                    "selectedSortColumnColor": c["blue"],
                },
            },
            "xray": {
                "fgColor": fg, "bgColor": bg, "cursorColor": c["bg_sel"],
                "cursorTextColor": c["fg_bright"], "graphicColor": c["comment"],
            },
            "yaml": {
                "keyColor": syntax(c, "property")[0], "colonColor": syntax(c, "punctuation")[0],
                "valueColor": syntax(c, "string")[0],
            },
            "picker": {"mainColor": fg, "focusColor": c["blue"], "shortcutColor": c["pink"]},
            "logs": {
                "fgColor": fg, "bgColor": bg,
                "indicator": {"fgColor": c["blue"], "bgColor": bg, "toggleOnColor": c["green"], "toggleOffColor": c["comment"]},
            },
        },
    }

    def emit(d, depth):
        pad = "  " * depth
        return "".join(
            f"{pad}{k}:\n" + emit(v, depth + 1) if isinstance(v, dict)
            else f"{pad}{k}: [" + ", ".join(f'"{x}"' for x in v) + "]\n" if isinstance(v, list)
            else f'{pad}{k}: "{v}"\n'
            for k, v in d.items()
        )

    return header(spec) + "k9s:\n" + emit(skin, 1)


def rofi(spec):
    """A rofi 1.7+ theme: rofi's own layout, recolored like the dunst port's popups, with the editors' selection gray."""
    c = colours(spec)
    v = {"background": c["bg_alt"], "foreground": c["fg"], "border-color": c["blue"], "separatorcolor": c["bg_sel"]}
    for state, fg in (("normal", c["fg"]), ("active", c["blue"]), ("urgent", c["red"])):
        # rofi stripes alternate rows; the editors don't, so both kinds of row get one background
        for kind in ("", "alternate-"):
            v[f"{kind}{state}-background"] = c["bg_alt"]
            v[f"{kind}{state}-foreground"] = fg
        v[f"selected-{state}-background"] = c["bg_sel"]
        v[f"selected-{state}-foreground"] = c["fg_bright"] if state == "normal" else fg
    rules = {
        "*": v,
        "element-text": {"highlight": f"bold {c['blue']}"},
        "prompt": {"text-color": c["violet"]},
        "entry": {"placeholder-color": c["comment"]},
        "num-filtered-rows, num-rows, textbox-num-sep": {"text-color": c["comment"]},
        "scrollbar": {"handle-color": c["bg_sel"]},
    }
    # "default" names the theme built into rofi, so only the colors change
    block = lambda sel, props: sel + " {\n" + "".join(f"    {k}: {val};\n" for k, val in props.items()) + "}\n"
    return header(spec, "//") + '@import "default"\n\n' + "\n".join(block(sel, props) for sel, props in rules.items())


def vivid(spec):
    """A vivid theme for LS_COLORS. Directories are blue as in Neovim, special files yellow as in its file trees,
    and executables and archives keep GNU's bold green and bold red. Documents take the text color."""
    c = colours(spec)
    style = lambda fg=None, bg=None, font=None: {
        k: v for k, v in (("foreground", fg), ("background", bg), ("font-style", font)) if v
    }
    on = lambda accent: style("bg", accent)  # GNU's special permissions: dark text on a colored block
    categories = {
        "core": {
            **{k: {} for k in ("normal_text", "regular_file", "reset_to_normal", "multi_hard_link", "file_with_capability")},
            "directory": style("blue"),
            "symlink": style("cyan"),
            "fifo": style("yellow"),
            "socket": style("violet"),
            "door": style("violet"),
            "block_device": style("yellow", font="bold"),
            "character_device": style("yellow", font="bold"),
            "broken_symlink": style("red"),
            "missing_symlink_target": style("red"),
            "setuid": on("red"),
            "setgid": on("yellow"),
            "sticky_other_writable": on("green"),
            "other_writable": style("blue", "diag_ok"),
            "sticky": on("blue"),
            "executable_file": style("green", font="bold"),
        },
        "text": {
            "special": style("yellow", font="bold"),
            "todo": style("yellow", font="bold"),
            "licenses": style("muted"),
            "configuration": style("yellow"),
            "other": style("fg"),
        },
        "markup": style("fg"),
        "programming": {"source": style("violet"), "tooling": style("yellow")},
        "media": style("pink"),
        # vivid needs a style for every category; an empty one only works on a leaf such as core.regular_file
        "office": style("fg"),
        "archives": style("red", font="bold"),
        "executable": style("green", font="bold"),
        "unimportant": style("comment"),
    }
    def names(d):  # the colour names the styles use, which vivid wants defined under colors:
        for k, v in d.items():
            if isinstance(v, dict):
                yield from names(v)
            elif k != "font-style":
                yield v

    def emit(d, depth):
        pad = "  " * depth
        return "".join(
            f"{pad}{k}: {{}}\n" if v == {} else f"{pad}{k}:\n" + emit(v, depth + 1) if isinstance(v, dict) else f"{pad}{k}: {v}\n"
            for k, v in d.items()
        )

    colors = "colors:\n" + "".join(f"  {n}: '{c[n].lstrip('#')}'\n" for n in dict.fromkeys(names(categories)))
    return header(spec) + colors + "\n" + emit(categories, 0)


# glamour's chroma token names and the syntax role each takes, for code blocks in glow and gh
GLAMOUR_SYNTAX = {
    "text": "variable",
    "comment": "comment",
    "comment_preproc": "keyword.directive",
    "keyword": "keyword",
    "keyword_reserved": "keyword",
    "keyword_namespace": "keyword.import",
    "keyword_type": "type.builtin",
    "operator": "operator",
    "punctuation": "punctuation",
    "name": "variable",
    "name_builtin": "function.builtin",
    "name_tag": "tag",
    "name_attribute": "tag.attribute",
    "name_class": "type",
    "name_constant": "constant",
    "name_decorator": "attribute",
    "name_exception": "type",
    "name_function": "function",
    "name_other": "variable",
    "literal": "constant",
    "literal_number": "number",
    "literal_date": "number",
    "literal_string": "string",
    "literal_string_escape": "string.escape",
    "generic_deleted": "diff.minus",
    "generic_emph": "markup.italic",
    "generic_inserted": "diff.plus",
    "generic_strong": "markup.strong",
    "generic_subheading": "diff.range",
}


def glamour(spec):
    """A glamour style for glow and gh: glamour's dark layout, with Markdown and code by SYNTAX."""
    c = colours(spec)
    flags = {"bold": "bold", "italic": "italic", "underline": "underline", "strikethrough": "crossed_out"}

    def role(r, **extra):
        colour, style = syntax(c, r)
        return ({"color": colour} if colour else {}) | {flags[w]: True for w in style.split()} | extra

    chroma = {k: role(r) for k, r in GLAMOUR_SYNTAX.items()}
    chroma["error"] = {"color": c["red"]}
    chroma["background"] = {"background_color": c["bg_alt"]}
    # the layout (prefixes, margins, indents) is glamour's dark.json; a style file replaces all of it
    style = {
        "document": {"block_prefix": "\n", "block_suffix": "\n", "color": c["fg"], "margin": 2},
        "block_quote": role("markup.quote", indent=1, indent_token="│ "),
        "paragraph": {},
        "list": {"level_indent": 2},
        "heading": role("markup.heading", block_suffix="\n"),
        "h1": {"prefix": " ", "suffix": " ", "color": c["bg"], "background_color": c["blue"], "bold": True},
        **{f"h{n}": {"prefix": "#" * n + " "} for n in range(2, 7)},
        "text": {},
        "strikethrough": {"crossed_out": True},
        "emph": {"italic": True},
        "strong": {"bold": True},
        "hr": {"color": c["comment"], "format": "\n--------\n"},
        "item": {"block_prefix": "• "},
        "enumeration": {"block_prefix": ". "},
        "task": {"ticked": "[✓] ", "unticked": "[ ] "},
        "link": role("markup.link.url"),
        "link_text": role("markup.link.label", bold=True),
        "image": role("markup.link.url"),
        "image_text": {"color": c["comment"], "format": "Image: {{.text}} →"},
        "code": role("markup.raw", prefix=" ", suffix=" ", background_color=c["bg_alt"]),
        "code_block": {"color": c["fg"], "margin": 2, "chroma": chroma},
        "table": {},
        "definition_list": {},
        "definition_term": {},
        "definition_description": {"block_prefix": "\n🠶 "},
        "html_block": {},
        "html_span": {},
    }
    return json.dumps(style, indent=2, ensure_ascii=False) + "\n"


def yazi(spec):
    """A yazi flavor.toml: modes and tabs like the lualine theme, popups framed blue, and file colors as in the
    vivid port. Symbols and icons stay yazi's. build() writes the bat theme next to it as tmtheme.xml."""
    c = colours(spec)

    def s(fg=None, bg=None, **flags):
        props = {"fg": c[fg] if fg else None, "bg": c[bg] if bg else None}
        return {k: v for k, v in props.items() if v} | flags

    block = lambda accent: (s("bg", accent, bold=True), s(accent, "bg_sel"))  # lualine's a and b sections
    popup = {"border": s("blue"), "title": s("blue")}
    sections = {
        "mgr": {
            "cwd": s("cyan"),
            "find_keyword": s("yellow", bold=True, italic=True, underline=True),
            "find_position": s("violet", bold=True, italic=True),
            "marker_copied": s("green", "green"),
            "marker_cut": s("red", "red"),
            "marker_marked": s("cyan", "cyan"),
            "marker_selected": s("yellow", "yellow"),
            "count_copied": s("bg", "green"),
            "count_cut": s("bg", "red"),
            "count_selected": s("bg", "yellow"),
            "border_style": s("bg_sel"),
        },
        "tabs": dict(zip(("active", "inactive"), block("blue"))),
        "mode": {
            f"{mode}_{part}": style
            for mode, accent in (("normal", "blue"), ("select", "violet"), ("unset", "red"))
            for part, style in zip(("main", "alt"), block(accent))
        },
        # the hovered file keeps its own color, on the selection gray
        "indicator": {"parent": s(bg="bg_alt"), "current": s(bg="bg_sel"), "preview": s(underline=True)},
        "status": {
            "perm_sep": s("comment"),
            "perm_type": s("green"),
            "perm_read": s("yellow"),
            "perm_write": s("red"),
            "perm_exec": s("cyan"),
            "progress_label": s("fg_bright", bold=True),
            "progress_normal": s("blue", "bg_sel"),
            "progress_error": s("red", "bg_sel"),
        },
        "which": {
            "border": s("blue"),
            "mask": s(bg="bg_alt"),
            "cand": s("cyan"),
            "rest": s("comment"),
            "desc": s("violet"),
            "separator_style": s("comment"),
        },
        "confirm": popup | {"btn_yes": s("bg", "blue")},
        "spot": popup | {"tbl_col": s("blue"), "tbl_cell": s("fg_bright", "bg_sel")},
        "notify": {"title_info": s("green"), "title_warn": s("yellow"), "title_error": s("red")},
        "pick": {"border": s("blue"), "active": s("violet", bold=True)},
        "input": {"border": s("blue"), "selected": s(bg="bg_sel")},
        "cmp": {"border": s("blue"), "active": s(bg="bg_sel")},
        "tasks": {"border": s("blue"), "hovered": s("violet", bold=True)},
        "help": {"border": s("blue"), "chord": s("cyan"), "hovered": s(bg="bg_sel", bold=True)},
    }
    # the vivid port's file colors; documents keep the text color
    archives = "**/application/{zip,rar,7z*,tar,gzip,xz,zstd,bzip*,lzma,compress,archive,cpio,arj,xar,ms-cab*}"
    rules = [
        {"mime": "**/{image,audio,video}/*"} | s("pink"),
        {"mime": archives} | s("red", bold=True),
        {"mime": "vfs/{absent,stale}"} | s("comment"),
        {"url": "*", "is": "orphan"} | s("red"),
        {"url": "*", "is": "exec"} | s("green", bold=True),
        {"url": "*", "is": "dummy"} | s("red"),
        {"url": "*/", "is": "dummy"} | s("red"),
        {"url": "*/"} | s("blue"),
    ]

    value = lambda v: "true" if v is True else f'"{v}"'
    inline = lambda d: "{ " + ", ".join(f"{k} = {value(v)}" for k, v in d.items()) + " }"
    out = [header(spec)]
    for name, keys in sections.items():
        out.append(f"[{name}]\n" + "".join(f"{k} = {inline(v)}\n" for k, v in keys.items()))
    out.append("[filetype]\nrules = [\n" + "".join(f"\t{inline(r)},\n" for r in rules) + "]\n")
    return "\n".join(out)


def kde(spec):
    """A KDE Plasma color scheme, laid out like the editors: views on bg, window chrome in bg_dark, buttons and
    tooltips in the popup shade. Blue is the selection, which Plasma also uses as its accent."""
    c = colours(spec)
    rgb_ = lambda h: ",".join(str(v) for v in rgb(h))

    def colour_set(normal, alternate, **over):
        keys = {
            "BackgroundAlternate": alternate,
            "BackgroundNormal": normal,
            "DecorationFocus": c["blue"],
            "DecorationHover": c["blue"],
            "ForegroundActive": c["blue"],
            "ForegroundInactive": c["muted"],
            "ForegroundLink": c["blue"],
            "ForegroundNegative": c["red"],
            "ForegroundNeutral": c["yellow"],
            "ForegroundPositive": c["green"],
            "ForegroundNormal": c["fg"],
            "ForegroundVisited": c["violet"],
        } | over
        return {k: rgb_(v) for k, v in sorted(keys.items())}

    window = colour_set(c["bg_dark"], c["bg"])
    # text on the blue selection takes the background color; its accents go most of the way there, about 4:1 on blue
    on_blue = {f"Foreground{k}": mix(c[a], c["bg"], 0.85) for k, a in (("Negative", "red"), ("Neutral", "yellow"), ("Positive", "green"))}
    sections = {
        "ColorEffects:Disabled": {
            "Color": rgb_(c["bg_sel"]), "ColorAmount": "0", "ColorEffect": "0", "ContrastAmount": "0.65",
            "ContrastEffect": "1", "IntensityAmount": "0.1", "IntensityEffect": "2",
        },
        "ColorEffects:Inactive": {
            "ChangeSelectionColor": "true", "Color": rgb_(c["bg_sel"]), "ColorAmount": "0.025", "ColorEffect": "2",
            "ContrastAmount": "0.1", "ContrastEffect": "2", "Enable": "false", "IntensityAmount": "0", "IntensityEffect": "0",
        },
        "Colors:Button": colour_set(c["bg_alt"], c["diff_text"]),
        "Colors:Complementary": window,
        "Colors:Header": window,
        "Colors:Header][Inactive": window,
        "Colors:Selection": colour_set(
            c["blue"], c["diff_text"], ForegroundNormal=c["bg"], ForegroundActive=c["bg"], ForegroundInactive=c["bg_sel"],
            ForegroundLink=c["bg"], ForegroundVisited=c["bg_sel"], **on_blue,
        ),
        "Colors:Tooltip": colour_set(c["bg_alt"], c["bg"]),
        "Colors:View": colour_set(c["bg"], c["colorcolumn"]),
        "Colors:Window": window,
        "General": {"ColorScheme": spec["slug"], "Name": spec["name"], "shadeSortColumn": "true"},
        "KDE": {"contrast": "4"},
        "WM": {
            "activeBackground": rgb_(c["bg_dark"]), "activeBlend": rgb_(c["fg_bright"]), "activeForeground": rgb_(c["fg"]),
            "inactiveBackground": rgb_(c["bg_dark"]), "inactiveBlend": rgb_(c["comment"]), "inactiveForeground": rgb_(c["comment"]),
        },
    }
    return header(spec) + "\n" + "\n".join(
        f"[{name}]\n" + "".join(f"{k}={v}\n" for k, v in keys.items()) for name, keys in sections.items()
    )


def qutebrowser(spec):
    """A qutebrowser config to source: tabs like kitty's, the status bar in the chrome shade with each mode tinting
    its text, popups in the popup shade with the selection gray, and link hints yellow like search matches."""
    c = colours(spec)
    v = {
        "completion.fg": c["fg"],
        "completion.odd.bg": c["bg_alt"],
        "completion.even.bg": c["bg_alt"],
        "completion.category.fg": c["blue"],
        "completion.category.bg": c["bg_dark"],
        "completion.category.border.top": c["bg_dark"],
        "completion.category.border.bottom": c["bg_dark"],
        "completion.item.selected.fg": c["fg_bright"],
        "completion.item.selected.bg": c["bg_sel"],
        "completion.item.selected.border.top": c["bg_sel"],
        "completion.item.selected.border.bottom": c["bg_sel"],
        "completion.item.selected.match.fg": c["blue"],
        "completion.match.fg": c["blue"],
        "completion.scrollbar.fg": c["bg_sel"],
        "completion.scrollbar.bg": c["bg_alt"],
        "contextmenu.menu.fg": c["fg"],
        "contextmenu.menu.bg": c["bg_alt"],
        "contextmenu.selected.fg": c["fg_bright"],
        "contextmenu.selected.bg": c["bg_sel"],
        "contextmenu.disabled.fg": c["comment"],
        "contextmenu.disabled.bg": c["bg_alt"],
        "tooltip.fg": c["fg"],
        "tooltip.bg": c["bg_alt"],
        "downloads.bar.bg": c["bg_dark"],
        "downloads.start.fg": c["bg"],
        "downloads.start.bg": c["blue"],
        "downloads.stop.fg": c["bg"],
        "downloads.stop.bg": c["green"],
        "downloads.error.fg": c["bg"],
        "downloads.error.bg": c["red"],
        "hints.fg": c["bg"],
        "hints.bg": c["yellow"],
        "hints.match.fg": c["bg_sel"],  # the letters already typed
        "keyhint.fg": c["fg"],
        "keyhint.suffix.fg": c["yellow"],
        "keyhint.bg": c["bg_alt"],
        "prompts.fg": c["fg"],
        "prompts.border": f"1px solid {c['bg_sel']}",
        "prompts.bg": c["bg_alt"],
        "prompts.selected.fg": c["fg_bright"],
        "prompts.selected.bg": c["bg_sel"],
    }
    # messages sit in the popup shade with a colored frame, like the dunst port's notifications
    for level, fg, frame in (("error", "red", "red"), ("warning", "yellow", "yellow"), ("info", "fg", "bg_sel")):
        v |= {f"messages.{level}.fg": c[fg], f"messages.{level}.bg": c["bg_alt"], f"messages.{level}.border": c[frame]}
    # the bar stays in the chrome shade, so the URL colors below stay readable in every mode
    modes = {"normal": "fg", "insert": "green", "passthrough": "cyan", "command": "fg", "caret": "violet", "caret.selection": "violet"}
    for mode, fg in modes.items():
        v |= {f"statusbar.{mode}.fg": c[fg], f"statusbar.{mode}.bg": c["bg_dark"]}
    for mode in ("private", "command.private"):
        v |= {f"statusbar.{mode}.fg": c["fg"], f"statusbar.{mode}.bg": c["bg_sel"]}
    v |= {
        "statusbar.progress.bg": c["blue"],
        "statusbar.url.fg": c["fg"],
        "statusbar.url.error.fg": c["red"],
        "statusbar.url.hover.fg": c["cyan"],
        "statusbar.url.success.http.fg": c["fg"],
        "statusbar.url.success.https.fg": c["green"],
        "statusbar.url.warn.fg": c["yellow"],
        "tabs.bar.bg": c["bg_dark"],
        "tabs.indicator.start": c["blue"],
        "tabs.indicator.stop": c["green"],
        "tabs.indicator.error": c["red"],
    }
    tabs = {"": (c["comment"], c["bg_dark"]), "selected.": (c["fg_bright"], c["bg"]), "pinned.": (c["muted"], c["bg_alt"]), "pinned.selected.": (c["fg_bright"], c["bg"])}
    for kind, (fg, bg) in tabs.items():
        for parity in ("odd", "even"):
            v |= {f"tabs.{kind}{parity}.fg": fg, f"tabs.{kind}{parity}.bg": bg}
    v["webpage.bg"] = c["bg"]  # shown before a page paints, instead of a white flash
    return header(spec) + "".join(f'c.colors.{k} = "{col}"\n' for k, col in v.items())


def herdr(spec):
    """A [theme.custom] table for herdr's config.toml. It sets every token, so the built-in theme under it doesn't
    matter. herdr names its tokens after Catppuccin's; the bars, sidebar and rows follow the zellij port."""
    c = colours(spec)
    tokens = {
        "accent": "blue",
        "panel_bg": "bg_dark",  # tab bar, floating panels and modals
        "sidebar_bg": "bg_dark",
        "active_row_bg": "bg_alt",
        "selection_bg": "bg_sel",
        "surface0": "bg_alt",
        "surface1": "bg_sel",
        "surface_dim": "bg_sel",  # separators
        "overlay0": "comment",  # unfocused pane borders and muted text, so readable rather than bg_sel
        "overlay1": "steel",
        "text": "fg",
        "subtext0": "muted",
        "mauve": "violet",
        "green": "green",
        "yellow": "yellow",
        "red": "red",
        "blue": "blue",
        "teal": "cyan",
        "peach": "pink",  # herdr's interrupted state; Rime has no orange
    }
    return header(spec) + "[theme.custom]\n" + "".join(f'{k} = "{c[n]}"\n' for k, n in tokens.items())


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
    ("vim", "vim/colors/{slug}.vim", vim),
    ("micro", "general/micro/{slug}.micro", micro),
    ("emacs", "general/emacs/{slug}-theme.el", emacs),
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
    ("warp", "general/warp/{slug}.yaml", warp),
    ("obsidian", "general/obsidian/{slug}.css", obsidian),
    ("discord", "general/discord/{slug}.theme.css", discord),
    ("firefox", "general/firefox/{slug}.html", firefox),
    ("telegram", "general/telegram/{slug}.tdesktop-palette", telegram),
    ("mako", "general/mako/{slug}", mako),
    ("hyprland", "general/hyprland/{slug}.lua", hyprland),
    ("fish", "general/fish/{slug}.theme", fish),
    ("starship", "general/starship/{slug}.toml", starship),
    ("lazygit", "general/lazygit/{slug}.yml", lazygit),
    ("dunst", "general/dunst/{slug}.conf", dunst),
    ("zellij", "general/zellij/{slug}.kdl", zellij),
    ("gitui", "general/gitui/{slug}.ron", gitui),
    ("btop", "general/btop/{slug}.theme", btop),
    ("k9s", "general/k9s/{slug}.yaml", k9s),
    ("rofi", "general/rofi/{slug}.rasi", rofi),
    ("vivid", "general/vivid/{slug}.yml", vivid),
    ("glamour", "general/glamour/{slug}.json", glamour),
    ("yazi", "general/yazi/{slug}.yazi/flavor.toml", yazi),
    ("kde", "general/kde/{slug}.colors", kde),
    ("qutebrowser", "general/qutebrowser/{slug}.py", qutebrowser),
    ("herdr", "general/herdr/{slug}.toml", herdr),
]


# The ports that are one file holding every variant: (port, its path, its text from all the specs).
ALL_IN_ONE = [
    ("zed", "zed/themes/rime.json", zed_themes),
    ("windows-terminal", "general/windows-terminal/rime.json", windows_terminal),
    ("spicetify", "general/spicetify/color.ini", spicetify),
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
        # a yazi flavor is a folder; its code previews take the bat theme under the name yazi looks for
        files[f"general/yazi/{slug}.yazi/tmtheme.xml"] = bat(spec)
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
    "general/yazi/*/*",
    "colors/*",
    "vim/colors/*",
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
