// Builds the site into dist/: every page from content/*.md, with the variants,
// syntax roles and port files from data.json, which tools/build.py writes.
// `bun build.ts` builds once; serve.ts builds and serves it while you edit.

import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { Marked, type Tokens } from "marked";
import { createHighlighter } from "shiki";

/** Where the site is served from: /rime/ on GitHub Pages. */
export const BASE = process.env.BASE ?? "/rime/";
export const OUT = join(import.meta.dir, "dist");
const ROOT = join(import.meta.dir, "..");
const CONTENT = join(import.meta.dir, "content");
const REPO = "https://github.com/w0x7y/rime";
const SITE_URL = "https://w0x7y.dev/rime/";

const json = (path: string) => JSON.parse(readFileSync(join(ROOT, path), "utf8"));
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// ------------------------------------------------------------------ the variants, from tools/build.py

type Variant = { slug: string; name: string; key: string; appearance: "dark" | "light"; colours: Record<string, string> };

/** Everything tools/build.py knows that the site shows, so the two can't disagree. Rerun it after a palette change. */
const DATA: {
  version: string;
  colour_names: { name: string; slot: string | null }[];
  variants: Variant[];
  syntax: { role: string; colour: string | null; style: string; note: string }[];
  downloads: Record<string, string>;
} = json("site/data.json");

const VERSION = DATA.version;
// in the order of ORDER in tools/build.py, whose first entry is the default variant
const VARIANTS = DATA.variants;
const DEFAULT = VARIANTS[0];
const LIGHT = VARIANTS.find((v) => v.appearance === "light") ?? DEFAULT;
// the 16 palette colors, base00 to base0F
const NAMES = DATA.colour_names.filter((c) => c.slot).map((c) => c.name);

/** A color name as a custom property: bg_alt -> --rime-bg-alt. */
const cssVar = (name: string) => `--rime-${name.replaceAll("_", "-")}`;

/** Each variant's colors as custom properties: the page is rime when dark and rime frost when light. */
function themeCss() {
  const vars = (v: Variant) => Object.entries(v.colours).map(([n, hex]) => `${cssVar(n)}:${hex}`).join(";") + `;color-scheme:${v.appearance}`;
  return [
    `:root,[data-theme="dark"]{${vars(DEFAULT)}}`,
    `[data-theme="light"]{${vars(LIGHT)}}`,
    `@media (prefers-color-scheme:light){:root:not([data-theme]){${vars(LIGHT)}}}`,
    ...VARIANTS.map((v) => `[data-variant="${v.slug}"]{${vars(v)}}`),
  ].join("\n");
}

// ------------------------------------------------------------------ ports, docs and syntax roles

type Port = { slug: string; name: string; group: "editors" | "terminals" | "more"; blurb: string };

const GROUPS = [
  { id: "editors", label: "editors" },
  { id: "terminals", label: "terminals" },
  { id: "more", label: "and the rest" },
] as const;

/** How the site lists each port; its files come from data.json. */
const PORTS: Port[] = [
  { slug: "neovim", name: "neovim", group: "editors", blurb: "lua, treesitter, lsp and lualine" },
  { slug: "vscode", name: "vs code", group: "editors", blurb: "on the marketplace and open vsx" },
  { slug: "zed", name: "zed", group: "editors", blurb: "all five in one theme file" },
  { slug: "helix", name: "helix", group: "editors", blurb: "a theme file" },
  { slug: "sublime", name: "sublime text", group: "editors", blurb: "a color scheme" },
  { slug: "vim", name: "vim", group: "editors", blurb: "vimscript, with 256-color fallbacks" },
  { slug: "kitty", name: "kitty", group: "terminals", blurb: "an include file" },
  { slug: "alacritty", name: "alacritty", group: "terminals", blurb: "a toml import" },
  { slug: "ghostty", name: "ghostty", group: "terminals", blurb: "a theme file" },
  { slug: "wezterm", name: "wezterm", group: "terminals", blurb: "a color scheme" },
  { slug: "foot", name: "foot", group: "terminals", blurb: "an ini include" },
  { slug: "windows-terminal", name: "windows terminal", group: "terminals", blurb: "five schemes in one json" },
  { slug: "iterm2", name: "iterm2", group: "terminals", blurb: "a color preset" },
  { slug: "xresources", name: "xresources", group: "terminals", blurb: "xterm, urxvt, st" },
  { slug: "noctalia", name: "noctalia", group: "more", blurb: "the desktop shell" },
  { slug: "tmux", name: "tmux", group: "more", blurb: "status bar, borders and copy mode" },
  { slug: "bat", name: "bat", group: "more", blurb: "a syntax theme" },
  { slug: "delta", name: "delta", group: "more", blurb: "the git diff pager" },
  { slug: "base16", name: "base16", group: "more", blurb: "for any base16 template" },
  { slug: "css", name: "css", group: "more", blurb: "custom properties" },
  { slug: "fzf", name: "fzf", group: "more", blurb: "FZF_DEFAULT_OPTS" },
];

const DOCS = [
  { slug: "colors", title: "colors", blurb: "the 16 color names, their base16 slots and the shades made from them" },
  { slug: "syntax", title: "syntax roles", blurb: "which color each kind of code gets, in every editor" },
  { slug: "customizing", title: "customizing", blurb: "change a color in neovim, or rebuild every port from a palette" },
  { slug: "porting", title: "porting", blurb: "bring rime to software it doesn't support yet" },
];

/** A port's files from data.json: one per variant when its path names the variant, otherwise one. */
function portFiles(port: Port) {
  const path = DATA.downloads[port.slug];
  if (!path) return [];
  return path.includes("{slug}") ? VARIANTS.map((v) => path.replaceAll("{slug}", v.slug)) : [path];
}

// ------------------------------------------------------------------ the logo in ASCII

/**
 * The logo (assets/icon.svg) as ASCII art: six arms in blue, cyan and violet
 * with a pair of branches on each. It's turned a quarter turn so the slanted
 * arms run at 60°, which / and \ draw cleanly. Lines are laid out in columns
 * both ways (a row is two columns tall) and step one character along their
 * longer axis.
 */
function asciiLogo(cols = 41, rows = 21) {
  const arms = [
    { angle: 0, colour: "blue" },
    { angle: 60, colour: "violet" },
    { angle: 120, colour: "cyan" },
    { angle: 180, colour: "blue" },
    { angle: 240, colour: "violet" },
    { angle: 300, colour: "cyan" },
  ];
  const cells: ({ ch: string; colour: string } | null)[][] = Array.from({ length: rows }, () => Array(cols).fill(null));
  const scale = cols / 184; // the icon's crystal spans 184 units
  const centre = [Math.floor(cols / 2), Math.floor(rows / 2) * 2];
  const toward = ([x, y]: number[], length: number, deg: number) => [x + length * Math.cos((deg * Math.PI) / 180), y + length * Math.sin((deg * Math.PI) / 180)];
  const glyph = (dx: number, dy: number) => {
    const a = ((((Math.atan2(dy, dx) * 180) / Math.PI) % 180) + 180) % 180;
    return a < 25 || a >= 155 ? "-" : a < 75 ? "\\" : a < 105 ? "|" : "/";
  };
  const draw = (from: number[], length: number, deg: number, colour: string) => {
    const [dx, dy] = toward([0, 0], length * scale, deg);
    const steps = Math.max(1, Math.round(Math.abs(dy) > Math.abs(dx) ? Math.abs(dy) / 2 : Math.abs(dx)));
    for (let i = 1; i <= steps; i++) {
      const x = Math.round(from[0] + (dx * i) / steps);
      const y = Math.round((from[1] + (dy * i) / steps) / 2);
      if (cells[y]?.[x] === null) cells[y][x] = { ch: glyph(dx, dy), colour };
    }
  };
  for (const { angle, colour } of arms) {
    draw(centre, 82, angle, colour);
    for (const [dist, length] of [[48, 22], [68, 14]]) {
      const base = toward(centre, dist * scale, angle);
      for (const turn of [-60, 60]) draw(base, length, angle + turn, colour);
    }
  }
  cells[centre[1] / 2][centre[0]] = { ch: "O", colour: "white" };
  // one span per run of a color
  const lines = cells.map((row) => {
    let out = "";
    let run = "";
    let colour: string | undefined;
    const flush = () => {
      if (run) out += colour ? `<span style="color:var(--rime-${colour})">${esc(run)}</span>` : run;
      run = "";
    };
    for (const cell of row) {
      const c = cell?.colour;
      if (c !== colour) flush();
      colour = c;
      run += cell?.ch ?? " ";
    }
    flush();
    return out.trimEnd();
  });
  return `<pre class="logo" role="img" aria-label="the rime logo, a six-armed frost crystal">${lines.join("\n")}</pre>`;
}

// ------------------------------------------------------------------ html pieces

// a real setup() from the neovim page, wide enough to fill a preview
const PREVIEW = `-- lua/plugins/rime.lua: the defaults, plus one change for abyss
require("rime").setup({
  transparent = false, -- let the terminal's background show through
  styles = { comments = { italic = true }, conditionals = { bold = true } },
  on_colors = function(c, variant)
    if variant == "abyss" then c.yellow = "#e3dc9e" end
  end,
})
vim.cmd.colorscheme("{{slug}}")`;

/** The base colors and the accents: one strip on a wide screen, two stacked on a phone. */
const swatches = (v: Variant) => {
  const strip = (names: string[]) => `<div>${names.map((n) => `<span style="background:${v.colours[n]}" title="${n} ${v.colours[n]}"></span>`).join("")}</div>`;
  return `<div class="swatches">${strip(NAMES.slice(0, 8))}${strip(NAMES.slice(8))}</div>`;
};

const fill = (text: string, v: Variant) => text.replace(/\{\{(slug|name|key|appearance)\}\}/g, (_, k: keyof Variant) => String(v[k]));
const fileName = (path: string) => path.split("/").pop()!;

function downloads(port: Port) {
  const paths = portFiles(port);
  if (paths.length === 0) return "";
  const links = paths.map((p) => `<a href="/files/${p}" download>${esc(fileName(p))}</a>`).join(" · ");
  return `<p class="files"><span class="dim">${paths.length > 1 ? "files" : "file"}:</span> ${links} · <a href="${REPO}/tree/main/${dirname(paths[0])}">on github</a></p>`;
}

function portList() {
  return GROUPS.map(
    (g) =>
      `<h2 id="${g.id}">${g.label}</h2><ul class="list">${PORTS.filter((p) => p.group === g.id)
        .map((p) => `<li><a href="/ports/${p.slug}">${esc(p.name)}</a> <span class="dim">${esc(p.blurb)}</span></li>`)
        .join("")}</ul>`,
  ).join("");
}

const docList = () => `<ul class="list">${DOCS.map((d) => `<li><a href="/docs/${d.slug}">${d.title}</a> <span class="dim">${d.blurb}</span></li>`).join("")}</ul>`;

function colourTable() {
  const head = `<tr><th>name</th><th>slot</th>${VARIANTS.map((v) => `<th>${v.key}</th>`).join("")}</tr>`;
  const body = DATA.colour_names
    .map(({ name: n, slot }) => {
      const cells = VARIANTS.map((v) => `<td><span class="chip" style="background:${v.colours[n]}"></span>${v.colours[n]}</td>`).join("");
      return `<tr><td><code>${n}</code></td><td class="dim">${slot ?? "derived"}</td>${cells}</tr>`;
    })
    .join("");
  return `<div class="table"><table><thead>${head}</thead><tbody>${body}</tbody></table></div>`;
}

function syntaxTable() {
  const css: Record<string, string> = { italic: "font-style:italic;", bold: "font-weight:700;", underline: "text-decoration:underline;", strikethrough: "text-decoration:line-through;" };
  // a style may be several words, as in tools/build.py
  const style = (s: string) => s.split(/\s+/).map((word) => css[word] ?? "").join("");
  const body = DATA.syntax
    .map(
      (r) =>
        `<tr><td><code style="${r.colour ? `color:var(${cssVar(r.colour)});` : ""}${style(r.style)}">${r.role}</code></td><td class="dim">${r.colour ?? "text"}</td><td class="dim">${r.style}</td><td>${esc(r.note)}</td></tr>`,
    )
    .join("");
  return `<div class="table"><table><thead><tr><th>role</th><th>color</th><th>style</th><th>note</th></tr></thead><tbody>${body}</tbody></table></div>`;
}

// ------------------------------------------------------------------ pages

type Page = { path: string; title: string; description: string; body: string };

function frontmatter(raw: string) {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n/);
  const meta: Record<string, string> = {};
  for (const line of m?.[1].split("\n") ?? []) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) meta[kv[1]] = kv[2];
  }
  return { meta, text: m ? raw.slice(m[0].length) : raw };
}

const NAV = [
  { href: "/", label: "home" },
  { href: "/ports", label: "ports" },
  { href: "/docs", label: "docs" },
  { href: REPO, label: "github" },
];

/** The repository's star count, or undefined when GitHub doesn't answer: offline, or over its rate limit. */
async function starCount(): Promise<number | undefined> {
  try {
    const res = await fetch("https://api.github.com/repos/w0x7y/rime", {
      headers: process.env.GITHUB_TOKEN ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {},
      signal: AbortSignal.timeout(5000),
    });
    return res.ok ? (await res.json()).stargazers_count : undefined;
  } catch {
    return undefined;
  }
}

/** A page's absolute address, for its canonical link and the sitemap. */
const pageUrl = (page: Page) => SITE_URL + (page.path ? `${page.path}/` : "");

const starText = (n: number) => `${n} ${n === 1 ? "star" : "stars"} on github`;

function layout(page: Page, stars?: number) {
  const section = "/" + page.path.split("/")[0];
  const nav = NAV.map((n) => `<a href="${n.href}"${n.href === section ? ' aria-current="page"' : ""}>${n.label}</a>`).join(" / ");
  const title = page.path === "" ? "rime · a colder colorscheme" : `${page.title} · rime`;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(page.description)}">
${page.path === "404" ? "" : `<link rel="canonical" href="${pageUrl(page)}">`}
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(page.description)}">
<meta property="og:image" content="${SITE_URL}og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/theme.css">
<link rel="stylesheet" href="/style.css">
<script>try{var t=localStorage.getItem("rime:theme");if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
</head>
<body>
<header>
<div class="row">
<a class="name" href="/">rime</a>
<a class="stars" href="${REPO}/stargazers"${stars === undefined ? " hidden>" : `>${starText(stars)}`}</a>
</div>
<div class="row">
<nav aria-label="main">${nav}</nav>
<p class="theme"><button type="button" data-theme-set="dark">dark</button> / <button type="button" data-theme-set="light">light</button></p>
</div>
</header>
<main>
${page.body}
</main>
<footer>
<p>rime is <a href="${REPO}/blob/main/LICENSE">mit licensed</a>. it flips <a href="https://github.com/if-not-nil/bark">bark</a> by if-not-nil around, with a little <a href="https://github.com/Binaryify/OneDark-Pro">one dark pro</a>.</p>
</footer>
<span id="new-tab" hidden>opens in a new tab</span>
<script>
const root = document.documentElement;
const current = () => root.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
const buttons = document.querySelectorAll("[data-theme-set]");
const mark = () => buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.themeSet === current())));
buttons.forEach((b) => (b.onclick = () => {
  root.dataset.theme = b.dataset.themeSet;
  try { localStorage.setItem("rime:theme", b.dataset.themeSet); } catch (e) {}
  mark();
}));
mark();

// the build writes the star count in; this refreshes it, at most once an hour
const stars = document.querySelector(".stars");
const show = (n) => { stars.textContent = n + (n === 1 ? " star" : " stars") + " on github"; stars.hidden = false; };
let cached = null;
try { cached = JSON.parse(localStorage.getItem("rime:stars")); } catch (e) {}
if (cached) show(cached.n);
if (!cached || Date.now() - cached.t > 36e5)
  fetch("https://api.github.com/repos/w0x7y/rime")
    .then((r) => (r.ok ? r.json() : Promise.reject()))
    .then((d) => {
      show(d.stargazers_count);
      try { localStorage.setItem("rime:stars", JSON.stringify({ n: d.stargazers_count, t: Date.now() })); } catch (e) {}
    })
    .catch(() => {});
</script>
</body>
</html>
`;
}

/** Put BASE in front of every site-relative link, with a trailing slash on pages, and open other sites in a new tab, which screen readers announce through #new-tab. */
function rebase(html: string) {
  return html
    .replace(/(href|src)="\/(?!\/)([^"#?]*)([#?][^"]*)?"/g, (_, attr, path: string, rest = "") => {
      // ghostty's theme files have no extension, so files/ is never a page
      const page = path !== "" && !path.endsWith("/") && !/\.\w+$/.test(path) && !path.startsWith("files/");
      return `${attr}="${BASE}${path}${page ? "/" : ""}${rest}"`;
    })
    .replace(/<a ([^>]*?)href="(https?:)/g, '<a target="_blank" rel="noopener" aria-describedby="new-tab" $1href="$2');
}

// ------------------------------------------------------------------ build

async function build() {
  const started = performance.now();
  const highlighter = await createHighlighter({
    themes: [shikiTheme()],
    langs: ["lua", "shellscript", "toml", "ini", "json", "jsonc", "css", "viml"],
  });
  const highlight = (code: string, lang: string) => highlighter.codeToHtml(code, { lang: lang || "text", theme: "rime" });

  const marked = new Marked({
    renderer: {
      // an id on every heading, so a link can point at its section
      heading({ tokens, depth, text }: Tokens.Heading) {
        const id = text.toLowerCase().replace(/`/g, "").replace(/[^\w\s-]/g, "").trim().replace(/\s+/g, "-");
        return `<h${depth} id="${id}">${this.parser.parseInline(tokens)}</h${depth}>\n`;
      },
      // a fence that names the variant shows rime, and the other four under it
      code({ text, lang = "" }: Tokens.Code) {
        if (!/\{\{(slug|name|key|appearance)\}\}/.test(text)) return highlight(text, lang);
        const others = VARIANTS.slice(1)
          .map((v) => `<p class="dim">${v.slug}</p>${highlight(fill(text, v), lang)}`)
          .join("");
        return `${highlight(fill(text, DEFAULT), lang)}<details><summary>other variants</summary>${others}</details>`;
      },
    },
  });

  const blocks: Record<string, (port?: Port) => string> = {
    logo: () => asciiLogo(),
    variants: () =>
      VARIANTS.map(
        (v) =>
          `<section class="variant" id="${v.slug}"><h3>${v.name.toLowerCase()} <span class="dim">· ${v.appearance}</span></h3>${swatches(v)}<div class="preview" data-variant="${v.slug}">${highlight(fill(PREVIEW, v), "lua")}<p class="statusline" aria-hidden="true"><span class="mode">NORMAL</span><span>rime.lua</span><span class="pos">lua · 9:1</span></p></div></section>`,
      ).join(""),
    ports: () => portList(),
    "ports-inline": () =>
      GROUPS.map((g) => `<p><span class="dim">${g.label}:</span> ${PORTS.filter((p) => p.group === g.id).map((p) => `<a href="/ports/${p.slug}">${esc(p.name).replace(/ /g, "&nbsp;")}</a>`).join(" · ")}</p>`).join(""),
    docs: docList,
    downloads: (port) => (port ? downloads(port) : ""),
    colors: colourTable,
    syntax: syntaxTable,
  };

  const pages: Page[] = [];
  const walk = (dir: string, prefix = "") => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) walk(join(dir, entry.name), `${prefix}${entry.name}/`);
      else if (entry.name.endsWith(".md")) {
        const name = entry.name.replace(/\.md$/, "");
        const path = name === "index" ? prefix.replace(/\/$/, "") : `${prefix}${name}`;
        const { meta, text } = frontmatter(readFileSync(join(dir, entry.name), "utf8"));
        const port = path.startsWith("ports/") ? PORTS.find((p) => `ports/${p.slug}` === path) : undefined;
        // block placeholders sit on lines of their own; they become tokens markdown leaves alone
        const html: string[] = [];
        const md = text.replace(/\{\{version\}\}/g, `v${VERSION}`).replace(/^\{\{([\w-]+)\}\}$/gm, (m, name: string) => {
          if (!(name in blocks)) throw new Error(`${path || "index"}: unknown block ${m}`);
          html.push(blocks[name](port));
          return `BLOCK${html.length - 1}`;
        });
        // markdown tables scroll on their own on a phone, as the generated ones do
        const body = (marked.parse(md) as string)
          .replace(/<table>/g, '<div class="table"><table>')
          .replace(/<\/table>/g, "</table></div>")
          .replace(/<p>BLOCK(\d+)<\/p>/g, (_, i) => html[Number(i)]);
        pages.push({ path, title: meta.title ?? name, description: meta.description ?? "", body });
      }
    }
  };
  walk(CONTENT);
  for (const p of PORTS) if (!pages.some((page) => page.path === `ports/${p.slug}`)) throw new Error(`content/ports/${p.slug}.md is missing`);
  for (const page of pages) if (page.path.startsWith("ports/") && !PORTS.some((p) => `ports/${p.slug}` === page.path)) throw new Error(`content/${page.path}.md has no entry in PORTS`);
  for (const slug of Object.keys(DATA.downloads)) if (!PORTS.some((p) => p.slug === slug)) throw new Error(`tools/build.py writes files for a port named ${slug}, which PORTS doesn't list`);

  const stars = await starCount();
  if (stars === undefined) console.warn("github didn't answer, so the star count is left for the browser to fill in");

  rmSync(OUT, { recursive: true, force: true });
  mkdirSync(OUT, { recursive: true });
  for (const page of pages) {
    const file = join(OUT, page.path, "index.html");
    mkdirSync(dirname(file), { recursive: true });
    writeFileSync(file, rebase(layout(page, stars)));
  }
  writeFileSync(
    join(OUT, "404.html"),
    rebase(layout({ path: "404", title: "not found", description: "", body: `<p class="dim">E484: Can't open file</p><h1>nothing here</h1><p>this page doesn't exist, or it moved. <a href="/">back home</a>.</p>` }, stars)),
  );

  // every page for search engines; robots.txt lives at the domain root, in the w0x7y.github.io repository
  writeFileSync(
    join(OUT, "sitemap.xml"),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${pages.map((p) => `<url><loc>${pageUrl(p)}</loc></url>`).join("\n")}\n</urlset>\n`,
  );

  // assets: the stylesheet, the font, the icon, the social image and every port's files
  writeFileSync(join(OUT, "theme.css"), themeCss());
  cpSync(join(import.meta.dir, "style.css"), join(OUT, "style.css"));
  const fonts = join(import.meta.dir, "node_modules/@fontsource/maple-mono/files");
  for (const f of ["400-normal", "400-italic", "700-normal"]) cpSync(join(fonts, `maple-mono-latin-${f}.woff2`), join(OUT, "fonts", `maple-mono-${f}.woff2`));
  cpSync(join(ROOT, "assets/icon.svg"), join(OUT, "favicon.svg"));
  cpSync(join(ROOT, "assets/screenshot-all.png"), join(OUT, "og.png"));
  for (const port of PORTS) {
    for (const path of portFiles(port)) {
      if (!existsSync(join(ROOT, path))) throw new Error(`the ${port.name} port lists ${path}, which does not exist`);
      cpSync(join(ROOT, path), join(OUT, "files", path));
    }
  }

  checkLinks();
  console.log(`built ${pages.length + 1} pages into dist/ in ${Math.round(performance.now() - started)}ms`);
}

/** Every link and asset under BASE must point at something that was built, and a #section at an id on that page. */
function checkLinks() {
  const broken: string[] = [];
  const visit = (dir: string) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const file = join(dir, entry.name);
      if (entry.isDirectory()) visit(file);
      else if (entry.name.endsWith(".html")) {
        for (const [, url, hash] of readFileSync(file, "utf8").matchAll(/(?:href|src)="([^"#?]*)(?:#([^"?]*))?/g)) {
          if (!url.startsWith(BASE)) continue;
          const target = url.endsWith("/") ? join(OUT, url.slice(BASE.length), "index.html") : join(OUT, url.slice(BASE.length));
          const missing = !existsSync(target) || (hash && target.endsWith(".html") && !readFileSync(target, "utf8").includes(`id="${hash}"`));
          if (missing) broken.push(`${file.slice(OUT.length)} -> ${url}${hash ? `#${hash}` : ""}`);
        }
      }
    }
  };
  visit(OUT);
  if (broken.length) throw new Error(`broken links:\n${[...new Set(broken)].join("\n")}`);
}

/**
 * A Shiki theme made from rime's VS Code theme with every palette hex swapped
 * for its custom property, so one highlight follows whichever variant draws it.
 * Every variant gives each syntax role the same color name (tools/build.py's
 * SYNTAX), so the default variant's theme works for all of them.
 */
function shikiTheme() {
  const vscode = json(`vscode/themes/${DEFAULT.slug}-color-theme.json`);
  // the theme names colors by hex, so two names with one hex would leave the highlighting guessing
  const byHex = new Map<string, string>();
  for (const [n, hex] of Object.entries(DEFAULT.colours)) {
    const taken = byHex.get(hex.toLowerCase());
    if (taken) throw new Error(`${n} and ${taken} are both ${hex} in ${DEFAULT.slug}, so the highlighting can't tell which the VS Code theme means`);
    byHex.set(hex.toLowerCase(), n);
  }
  const toVar = (hex?: string) => {
    if (!hex) return undefined;
    const name = byHex.get(hex.toLowerCase());
    if (!name) throw new Error(`${hex} in the rime VS Code theme is not a palette color`);
    return `var(${cssVar(name)})`;
  };
  return {
    name: "rime",
    type: "dark" as const,
    colors: { "editor.foreground": "var(--rime-fg)", "editor.background": "var(--rime-bg)" },
    settings: [
      { settings: { foreground: "var(--rime-fg)", background: "var(--rime-bg)" } },
      ...vscode.tokenColors.map((r: { scope?: string | string[]; settings: { foreground?: string; fontStyle?: string } }) => ({
        scope: r.scope,
        settings: { foreground: toVar(r.settings.foreground), fontStyle: r.settings.fontStyle },
      })),
    ],
  };
}

if (import.meta.main) await build();
