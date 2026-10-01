---
name: Saab Presentations
description: Build and style Saab-branded presentation decks (Marp to PDF/PPTX) using the Saab palette, Arial typography, logo placement, classification footer, and slide layouts
---

# Saab Presentations

Reusable instructions for producing **Saab-branded presentations** in this repository.
Decks are authored in Markdown for [Marp](https://marp.app) and export to PDF and
PowerPoint. The look is modelled on `saab_template.pptx`: 16:9, Arial, the Saab
brand palette, a Saab logo top-right, and a classification footer on every slide.

## When to use

Use this skill when the task involves:

- Creating, editing, or restructuring a Saab presentation deck.
- Applying Saab brand style, colours, typography, or figure guidelines.
- Exporting slides to PDF/PPTX, or setting up a new deck version.

## Non-negotiables

Every Saab deck must keep these six rules. Treat violations as blockers.

1. **16:9 widescreen** (`size: 16:9`) — never 4:3.
2. **Arial** (with `Helvetica Neue`/`Helvetica` fallback). Do not introduce other typefaces.
3. **Saab logo top-right** on every slide. The bundled standalone theme does this
   on all slides; the repository theme only shows it on title/closing slides
   (see *Standalone use*).
4. **Classification footer** on every slide:
   `COMPANY UNCLASSIFIED | NOT EXPORT CONTROLLED | NOT CLASSIFIED`.
5. **Brand palette only** — navy blue as primary, yellow as highlight, red as a
   sparing accent. See `references/color-profile.md`.
6. **Generous whitespace, restrained editorial style** — no decorative clutter,
   no invented logos or readable pseudo-text in figures.

## Toolchain

| Item | Value |
| ---- | ----- |
| Deck source | `presentation/versions/<version>/slides.marp.md` |
| Theme | `@theme saab` in `presentation/themes/saab-theme.css` (symlink into the `article_common_artifacts` submodule) |
| Build entrypoint | `bash presentation/build_slides.sh` |
| Build options | `--version <name>`, `--pdf`, `--pptx`, `--watch` |
| Requirements | `marp` CLI; `--allow-local-files` is required for local images |

Run builds **from the repository root** so `figures/` and `presentation/assets/`
paths resolve. Ensure submodules are initialised first:

```bash
git submodule update --init --recursive
bash presentation/build_slides.sh                 # all versions -> PDF + PPTX
bash presentation/build_slides.sh --version 20min # one version
bash presentation/build_slides.sh --version 20min --watch
```

Each deck directory needs a `themes` symlink (`versions/<v>/themes -> ../../themes`)
so the theme's relative `themes/saab_logo_extracted.svg` and
`themes/cover_background.jpg` backgrounds resolve for both the Marp CLI and the
VS Code Marp extension.

### Standalone use (bundled resources)

The skill also ships a **self-contained** set of resources so it can build Saab
decks outside this repository:

| Resource | Purpose |
| -------- | ------- |
| `assets/theme/saab-theme.css` | Self-contained `@theme saab` (logo + cover inlined; logo on every slide) |
| `assets/brand/` | Saab logo (SVG + PNG), cover background, classification strip |
| `scripts/build_slides.sh` | Marp → PDF/PPTX using the bundled theme (no symlinks needed) |
| `scripts/export_svg_to_png.sh` | Batch-convert figure SVGs to PNG |
| `scripts/make_theme.py` | Regenerate the bundled theme from the repo source |
| `templates/standalone.marp.md` | Dependency-free starter deck |

```bash
SKILL=.opencode/skills/saab-presentations
cp "$SKILL/templates/standalone.marp.md" my-talk/slides.md
bash "$SKILL/scripts/build_slides.sh" my-talk/slides.md --both
```

See `references/standalone-usage.md` for details and the differences between the
repository and bundled themes. Do not hand-edit the generated theme; run
`scripts/make_theme.py` instead.

## Workflow

1. Clarify **audience, duration, and language**; pick or create a version
   (`presentation/versions/<version>/`).
2. Draft the narrative **outline first** (one message per slide, 3–5 bullets max),
   then fill slides from the template.
3. Copy `templates/deck.marp.md` and set the front matter (theme, footer author,
   version).
4. Author each slide with a known archetype and the shared CSS classes
   (see `references/slide-patterns.md`).
5. Build with `build_slides.sh` and **verify** the PDF/PPTX: logo present, footer
   correct, no text or image overflow, figures legible at projection size.
6. Treat Marp/LaTeX build errors as blockers.

## Slide archetypes

| Archetype | How | Notes |
| --------- | --- | ----- |
| Title / cover | `<!-- _class: title -->` | Blue cover, yellow rule, logo + footer |
| Section content | `# Heading` + bullets | Default white slide, navy heading rule |
| Text + figure | `.cols` → `.col-left` / `.col-right` | Primary content layout |
| Full-bleed figure | `![bg contain](path)` | Only a caption/heading if needed |
| Data / comparison | Markdown table | Branded header row, zebra rows |
| Closing | `<!-- _class: thank -->` | Reuses cover treatment |

Before using any class or snippet, read `references/slide-patterns.md` — it holds
the exact, working markup for this theme.

## Style summary

- **Voice:** precise, calm, engineering-editorial. Short declarative sentences.
- **Structure:** one idea per slide; headline states the takeaway, not the topic.
- **Emphasis:** use `**bold**` (renders Saab blue), not colour names or HTML.
- **Density:** ≤ 5 bullets per slide; prefer figures over walls of text.
- **Speaker notes:** put them in HTML comments (`<!-- ... -->`), omitted from export.
- **Numbers:** use tables for anything comparative.

Full detail: `references/brand-guidelines.md`.

## Colour profile (summary)

Extracted from `saab_template.pptx` (Office theme accents) and the Marp theme.

| Token | Hex | Role |
| ----- | --- | ---- |
| Saab Blue | `#00508C` | Primary brand, headings, accents, table headers |
| Saab Yellow | `#FAB900` | Highlight, rules, cover underline |
| Saab Red | `#E61419` | Sparing alert/emphasis accent |
| Saab Dark Grey | `#373737` | Body headings, body text |
| Saab Beige | `#BEAF96` | Secondary neutral |
| Light Warm Grey | `#E1E1DC` | Panel / surface tint |
| Deep Navy (override) | `#0B3D6E` | Deck-level `h1`/`h2` colour |
| White | `#FFFFFF` | Slide background |

Never place red text on blue, never recolour the logo, and keep PDF/PPTX output
colour-accurate. Full profile with RGB values, tints, and contrast notes:
`references/color-profile.md`.

## Graphical guidelines (summary)

- Prefer **editable vector sources** (SVG / draw.io / TikZ / Mermaid) for
  diagrams so they stay on-brand and re-exportable; export PNGs with
  `bash presentation/export_svg_to_png.sh` (repo) or
  `bash scripts/export_svg_to_png.sh <dir>` (bundled).
- Figures use **blue / teal / charcoal with a muted red accent on a light
  background**, flat editorial style, with room for labels and arrows.
- **Do not** put readable words, fake UI/XML, tool screenshots, or photoreal
  classified-looking aircraft detail into generated art.
- Match figure colours to the palette tokens; keep line weights and label sizes
  legible at the back of a room.
- Always fill the slide, never let text or images overflow the frame.

Full detail and reusable image-generation direction:
`references/brand-guidelines.md`.

## Reference files

- `references/color-profile.md` — full palette, tints, usage, contrast/accessibility.
- `references/brand-guidelines.md` — style, typography, graphical/figure guidelines.
- `references/slide-patterns.md` — copy-paste Marp markup and CSS classes.
- `references/standalone-usage.md` — building a deck outside this repository.
- `templates/deck.marp.md` — starter deck scaffold for a repository version.
- `templates/standalone.marp.md` — dependency-free starter deck.
- `assets/theme/saab-theme.css` — self-contained bundled theme (generated).
- `assets/brand/` — Saab logo, cover background, classification strip.
- `scripts/build_slides.sh`, `scripts/export_svg_to_png.sh`, `scripts/make_theme.py`.
