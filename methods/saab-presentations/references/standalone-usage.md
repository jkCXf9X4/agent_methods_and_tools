# Standalone usage

This skill ships everything needed to produce a Saab deck **without** the
repository: a self-contained theme, brand assets, build scripts, and a starter
deck. Use this page when working outside `presentation/versions/`.

## Bundled resources

```text
saab-presentations/
├── assets/
│   ├── brand/
│   │   ├── saab-logo.svg            # vector Saab logo
│   │   ├── saab-logo.png            # 349×108 logo from saab_template.pptx
│   │   ├── cover_background.jpg     # official cover photograph
│   │   └── footer-classification.svg
│   └── theme/
│       ├── saab-theme.css           # self-contained @theme saab (generated)
│       └── README.md                # provenance + regeneration
├── scripts/
│   ├── build_slides.sh              # marp -> PDF/PPTX with the bundled theme
│   ├── export_svg_to_png.sh         # figures: SVG -> PNG
│   └── make_theme.py                # regenerate the bundled theme
└── templates/
    └── standalone.marp.md           # dependency-free starter deck
```

## Quick start

```bash
SKILL=.opencode/skills/saab-presentations

# 1. start from the template
cp "$SKILL/templates/standalone.marp.md" my-talk/slides.md

# 2. author the deck, then build
bash "$SKILL/scripts/build_slides.sh" my-talk/slides.md --pdf
bash "$SKILL/scripts/build_slides.sh" my-talk/slides.md --pptx
bash "$SKILL/scripts/build_slides.sh" my-talk --both   # dir containing slides.md
```

`build_slides.sh` defaults to the bundled theme; override with `--theme FILE`.
It always passes `--allow-local-files` so deck-local images resolve.

## Requirements

- `marp` CLI (`npm i -g @marp-team/marp-cli`)
- Optional: `inkscape` or ImageMagick for `export_svg_to_png.sh`

## Standalone vs repository theme

| Behaviour | Repository theme | Bundled standalone theme |
| --------- | ---------------- | -------------------------|
| Location dependency | needs a `themes/` symlink | none (self-contained) |
| Logo on title/closing | yes | yes |
| Logo on content slides | **no** | **yes** (matches the .pptx template) |
| Classification footer | deck `footer:` directive | deck `footer:` directive |
| Cover background | relative `themes/` path | inlined data URI |

Both themes keep the same palette, typography, and `.cols` layout classes, so a
deck authored against one renders with the other.

## Regenerating the theme

The bundled theme is generated from the repository's `@theme saab` source:

```bash
python3 scripts/make_theme.py            # default source + bundled assets
python3 scripts/make_theme.py --source path/to/saab-theme.css
```

Re-run it whenever the upstream theme changes. Edit `make_theme.py` (not the
generated CSS) if the transformation needs to change.

## Using the official PowerPoint template

The authoritative master is
`3rd_party/article_common_artifacts/pressentation/templates/saab_template.pptx`
(16:9, Arial, Saab palette, logo on every layout). It is **not** bundled here
because it is ~12 MB; copy it into your deck folder when you need the native
PowerPoint master, and keep this skill's Marp theme as the source for
Markdown-driven decks.

## Adding figures

```bash
bash scripts/export_svg_to_png.sh my-talk/figures
```

Then reference the PNG (or SVG) from the deck. Follow
`references/brand-guidelines.md` for figure style.
