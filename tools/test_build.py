"""Checks for the generator and the files it keeps in step.

Run: python3 -m unittest discover -s tools
"""

import json
import os
import pathlib
import plistlib
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import build


def contrast(a, b):
    """The WCAG contrast ratio of two hex colours, from 1 to 21."""

    def luminance(h):
        r, g, b = (
            v / 255 / 12.92 if v <= 10 else ((v / 255 + 0.055) / 1.055) ** 2.4
            for v in build.rgb(h)
        )
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class GeneratedFiles(unittest.TestCase):
    def test_committed_files_match_the_palettes(self):
        self.assertEqual(
            build.stale(build.build(*build.load())),
            [],
            "run python3 tools/build.py and commit the result",
        )

    def test_check_flags_files_build_no_longer_writes(self):
        files = build.build(*build.load())
        self.assertEqual(build.leftover(files), [], "delete these, or generate them again")
        del files["general/kitty/rime.conf"]  # as if the variant were renamed
        self.assertEqual(build.leftover(files), ["general/kitty/rime.conf"])

    def test_check_ignores_formatting(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            build, "ROOT", pathlib.Path(tmp)
        ):
            files = {
                "crlf.lua": ("a = 1\r\n", "a = 1\n"),
                "indent.lua": ("\ta = 1\n", "    a = 1\n"),
                "changed.lua": ("a = 1\n", "a = 2\n"),
                "wrapped.json": ('{"a": [1, 2]}\n', '{\n\t"a": [\n\t\t1,\n\t\t2\n\t]\n}\n'),
                "changed.json": ('{"a": 1}\n', '{"a": 2}\n'),
                "broken.json": ('{"a": 1\n', '{"a": 1}\n'),
            }
            for path, (on_disk, _) in files.items():
                (pathlib.Path(tmp) / path).write_bytes(on_disk.encode())
            generated = {path: text for path, (_, text) in files.items()}
            self.assertEqual(
                build.stale(generated | {"missing.lua": "a = 1\n"}),
                ["changed.lua", "changed.json", "broken.json", "missing.lua"],
            )

    def test_load_rejects_a_palette_with_the_wrong_slug_or_appearance(self):
        rime = json.loads((build.ROOT / "palettes/rime.json").read_text())
        cases = {
            "a copy that keeps its slug": (rime, "rime-copy"),
            "a mistyped appearance": (rime | {"slug": "rime-copy", "appearance": "Dark"}, "appearance"),
        }
        for case, (copy, error) in cases.items():
            with self.subTest(case), tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                build, "ROOT", pathlib.Path(tmp)
            ), mock.patch.object(build, "ORDER", ["rime", "rime-copy"]):
                (pathlib.Path(tmp) / "palettes").mkdir()
                (pathlib.Path(tmp) / "palettes/rime.json").write_text(json.dumps(rime))
                (pathlib.Path(tmp) / "palettes/rime-copy.json").write_text(json.dumps(copy))
                (pathlib.Path(tmp) / "LICENSE").write_text("")
                with self.assertRaisesRegex(ValueError, error):
                    build.load()


class Palettes(unittest.TestCase):
    """The rules in AGENTS.md for moving a dark variant's background."""

    def dark(self):
        return [s for s in build.load()[0] if s["appearance"] == "dark"]

    def test_panel_and_selection_keep_their_step_from_the_background(self):
        for spec in self.dark():
            p = spec["palette"]
            bg = build.rgb(p["base00"])
            steps = [[a - b for a, b in zip(build.rgb(p[slot]), bg)] for slot in ("base01", "base02")]
            self.assertEqual(steps, [[8, 9, 10], [23, 25, 29]], spec["slug"])

    def test_comments_stay_readable_on_the_background(self):
        for spec in self.dark():
            p = spec["palette"]
            self.assertGreaterEqual(contrast(p["base03"], p["base00"]), 3.2, spec["slug"])


class SyntaxRoles(unittest.TestCase):
    """build.SYNTAX decides the colour of each syntax role once, for every editor port."""

    def lua(self, name):
        return (build.ROOT / "lua/rime" / name).read_text()

    def neovim_roles(self):
        return set(
            re.findall(
                r'\b(?:role|colour|role_style)\("([^"]+)"',
                self.lua("groups.lua") + self.lua("init.lua"),
            )
        )

    def roles_used_by(self, port):
        used = set()

        class Recording(dict):
            def __getitem__(self, role):
                used.add(role)
                return super().__getitem__(role)

        with mock.patch.object(build, "SYNTAX", Recording(build.SYNTAX)):
            port(build.load()[0][0])
        return used

    def test_neovim_names_only_known_roles(self):
        self.assertEqual(
            self.neovim_roles() - set(build.SYNTAX), set(), "unknown roles in lua/rime"
        )

    def test_roles_in_a_neovim_style_group_share_its_default(self):
        # e.g. Neovim styles keyword.return with `styles.keywords`, whose default is the keyword role's style
        defaults = dict(
            re.findall(r'(\w+) = role_style\("([^"]+)"\)', self.lua("init.lua"))
        )
        for role, group in re.findall(
            r'\brole\("([^"]+)", st\.(\w+)\)', self.lua("groups.lua")
        ):
            self.assertEqual(
                build.SYNTAX[role][1],
                build.SYNTAX[defaults[group]][1],
                f"Neovim styles {role} with styles.{group}, which defaults to {defaults[group]}'s style",
            )

    def test_every_role_is_shared_by_two_ports(self):
        ports = {
            "Neovim": self.neovim_roles(),
            "Zed": self.roles_used_by(build.zed_theme),
            "VS Code": self.roles_used_by(build.vscode_theme),
            "Helix": self.roles_used_by(build.helix),
            "Vim": self.roles_used_by(build.vim),
        }
        for role in build.SYNTAX:
            users = [port for port, roles in ports.items() if role in roles]
            self.assertGreaterEqual(
                len(users), 2, f"{role} is only used by {users}; keep it in that port"
            )


@unittest.skipUnless(
    shutil.which("nvim") or os.environ.get("RIME_REQUIRE_NVIM"), "needs nvim"
)
class LuaMatchesPython(unittest.TestCase):
    """Neovim names the palette slots and blends its derived shades at load time, after on_colors. Unchanged, they must equal the generated ports'."""

    def nvim(self, lua):
        """What a Lua script run with the plugin on the runtimepath writes to stdout, as JSON."""
        with tempfile.NamedTemporaryFile("w", suffix=".lua") as script:
            script.write(lua)
            script.flush()
            run = subprocess.run(
                ["nvim", "--headless", "-u", "NONE", "--cmd", f"set rtp^={build.ROOT}", "-l", script.name],
                capture_output=True,
                text=True,
                check=True,
            )
        return json.loads(run.stdout)

    LUA = """
    local rime = require("rime")
    local out = {}
    for _, v in ipairs(rime.variants) do
      rime.load(v)
      local c, names, term = rime.colors(v), {}, {}
      for k, colour in pairs(c) do
        if type(colour) == "string" then names[k] = colour end
      end
      for i = 0, 15 do term[i + 1] = vim.g["terminal_color_" .. i] end
      out[#out + 1] = { names = names, ansi = term }
    end
    io.stdout:write(vim.json.encode(out))
    """

    def test_colour_names_derived_shades_and_terminal_colours(self):
        for spec, lua in zip(build.load()[0], self.nvim(self.LUA)):
            py = build.colours(spec)
            # every colour name and derived shade the ports use; the plugin has more shades of its own
            names = {k: v for k, v in py.items() if isinstance(v, str)}
            self.assertEqual({k: lua["names"].get(k) for k in names}, names, spec["slug"])
            self.assertEqual(lua["ansi"], py["ansi"], spec["slug"])

    def test_options_the_readme_documents(self):
        lua = self.nvim("""
        local rime = require("rime")
        rime.setup({
          on_colors = function(c) c.bg = "#101010"; c.border = "#123456" end,
          styles = { comments = {} },
        })
        rime.load("rime")
        local c = rime.colors("rime")
        local comment = vim.api.nvim_get_hl(0, { name = "Comment" })
        io.stdout:write(vim.json.encode({ bg_dark = c.bg_dark, border = c.border, italic = comment.italic == true }))
        """)
        spec = build.load()[0][0]
        changed = spec | {"palette": spec["palette"] | {"base00": "#101010"}}
        # a derived shade follows a colour on_colors changes; one on_colors sets is kept
        self.assertEqual(lua["bg_dark"], build.colours(changed)["bg_dark"])
        self.assertEqual(lua["border"], "#123456")
        # a style replaces the default instead of merging into it
        self.assertFalse(lua["italic"])


class Noctalia(unittest.TestCase):
    """Noctalia sets text in each on_* colour on its role's fill, so a palette edit must keep them readable."""

    def test_on_colours_are_readable(self):
        for spec in build.load()[0]:
            for mode in build.noctalia(spec).values():
                for role in (
                    "Primary",
                    "Secondary",
                    "Tertiary",
                    "Error",
                    "Surface",
                    "SurfaceVariant",
                    "Hover",
                ):
                    self.assertGreaterEqual(
                        contrast(mode[f"mOn{role}"], mode[f"m{role}"]),
                        4.5,
                        f"{spec['slug']}: mOn{role}",
                    )

    def test_shell_matches_the_editor_chrome(self):
        for spec in build.load()[0]:
            zed, vscode = (
                build.zed_theme(spec)["style"],
                build.vscode_theme(spec)["colors"],
            )
            mode = build.noctalia(spec)["dark"]
            self.assertEqual(mode["mSurface"], zed["editor.background"], spec["slug"])
            self.assertEqual(
                mode["mSurface"], vscode["editor.background"], spec["slug"]
            )
            self.assertEqual(
                mode["mSurfaceVariant"],
                zed["elevated_surface.background"],
                spec["slug"],
            )
            self.assertEqual(
                mode["mHover"], vscode["list.activeSelectionBackground"], spec["slug"]
            )
            self.assertEqual(
                mode["mOnPrimary"], vscode["button.foreground"], spec["slug"]
            )
            self.assertEqual(mode["mOutline"], zed["border"], spec["slug"])

    def test_terminals_share_the_theme_background(self):
        for spec in build.load()[0]:
            zed, vscode = (
                build.zed_theme(spec)["style"],
                build.vscode_theme(spec)["colors"],
            )
            terminals = [
                zed["terminal.background"],
                vscode["terminal.background"],
                build.noctalia(spec)["dark"]["terminal"]["background"],
            ]
            self.assertEqual(terminals, [spec["palette"]["base00"]] * 3, spec["slug"])


class Bat(unittest.TestCase):
    """bat and delta read the tmTheme with syntect, which skips a whole rule whose fontStyle has a word it doesn't know."""

    def test_keeps_every_vscode_token_colour(self):
        for spec in build.load()[0]:
            theme = plistlib.loads(build.bat(spec).encode())
            rules = {r["name"]: r["settings"] for r in theme["settings"][1:]}
            for rule in build.vscode_theme(spec)["tokenColors"]:
                if "foreground" in rule["settings"]:
                    self.assertEqual(rules[rule["name"]]["foreground"], rule["settings"]["foreground"], spec["slug"])
            for settings in rules.values():
                self.assertLessEqual(set(settings.get("fontStyle", "").split()), {"bold", "italic", "underline"})


class Sublime(unittest.TestCase):
    def test_keeps_every_vscode_token_colour(self):
        for spec in build.load()[0]:
            rules = {r.get("name"): r for r in json.loads(build.sublime(spec))["rules"]}
            for rule in build.vscode_theme(spec)["tokenColors"]:
                if "foreground" in rule["settings"]:
                    self.assertEqual(rules[rule["name"]]["foreground"], rule["settings"]["foreground"], spec["slug"])
            for rule in rules.values():
                self.assertLessEqual(set(rule.get("font_style", "").split()), {"bold", "italic", "underline"})


class Docs(unittest.TestCase):
    """Prose that quotes generated values, so a release or palette change can't leave it behind."""

    def read(self, path):
        return (build.ROOT / path).read_text()

    def test_install_from_source_names_the_current_version(self):
        versions = re.findall(
            rf"{build.EXTENSION_ID}-(\d+\.\d+\.\d+)\.vsix",
            self.read("vscode/README.md"),
        )
        self.assertEqual(set(versions), {build.VERSION})

    def test_quoted_backgrounds_are_current(self):
        backgrounds = {spec["palette"]["base00"] for spec in build.load()[0]}
        for path in ("README.md", "vscode/README.md"):
            for line in self.read(path).splitlines():
                if "background" in line:
                    for quoted in re.findall(r"`(#[0-9a-fA-F]{6})`", line):
                        self.assertIn(quoted.lower(), backgrounds, f"{path}: {line}")


if __name__ == "__main__":
    unittest.main()
