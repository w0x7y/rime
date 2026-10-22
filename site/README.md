# Rime's website

The site at <https://w0x7y.dev/rime/>: static HTML and one stylesheet, built by one script. No framework and no client-side app; the only JavaScript is the dark/light switch and a refresh of the GitHub star count, which the build writes into every page (with `GITHUB_TOKEN` when it's set) and the browser updates at most once an hour.

## Develop

Needs [Bun](https://bun.sh).

```sh
cd site
bun install
bun run dev        # http://localhost:4321/rime/, rebuilds when content/, style.css or build.ts changes
bun run typecheck
bun run build      # static site in dist/
```

`BASE=/ bun run build` builds for the root of a domain instead of `/rime/`.

## How it works

- **Pages** are markdown in `content/`. `content/ports/kitty.md` becomes `/ports/kitty/`.
- **`build.ts`** reads `data.json`, which `python3 tools/build.py` writes: the version, the color names with their slots, each variant's colors and derived shades in `ORDER`, the syntax roles with their notes, and each port's files. So the site can't disagree with the ports; rerun `tools/build.py` after changing a palette or `SYNTAX`. It renders the markdown, highlights code with Shiki (from the generated VS Code theme), copies every port's files into `dist/files/`, and fails if a link points at a page, file or section that wasn't built.
- **Blocks** are a placeholder on a line of their own that `build.ts` fills in: `{{logo}}`, `{{variants}}`, `{{ports}}`, `{{ports-inline}}`, `{{docs}}`, `{{downloads}}`, `{{colors}}` and `{{syntax}}`. `{{version}}` works inside a line.
- **Variant snippets**: a code fence that mentions `{{slug}}`, `{{name}}`, `{{key}}` or `{{appearance}}` shows rime, with the other four under "other variants".
- **Colors** are custom properties in `theme.css`, which `build.ts` writes: rime when dark, rime frost when light, and each variant under `[data-variant]` for the previews on the home page. Code is highlighted once with a theme made of those properties, so one highlight follows any variant.
- **Search engines** get a canonical link on every page and `sitemap.xml`, listing every page, at <https://w0x7y.dev/rime/sitemap.xml>. `robots.txt` only works at the domain root, so it lives in the w0x7y.github.io repository, which points at this sitemap.
- **Links** in content start with `/` (`[ports](/ports)`); `build.ts` adds the base path and a trailing slash, and opens links to other sites in a new tab, telling screen readers so. Every heading gets an id from its text, so `/docs/colors#terminal-colors` links to a section, and the build checks those too.

## Deploy

`.github/workflows/site.yml` typechecks and builds every push and pull request, and deploys `main` to GitHub Pages. In the repository settings, under **Pages**, set the source to **GitHub Actions**. Dependabot opens a pull request each month when the packages have updates, and the workflow builds it like any other.
