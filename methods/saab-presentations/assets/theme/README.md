# Bundled theme (standalone)

`saab-theme.css` is a self-contained `@theme saab` Marp theme for Saab decks.
Unlike the repository theme (which lives in the `article_common_artifacts`
submodule and expects a sibling `themes/` symlink), this copy:

- inlines the Saab logo and cover background as **data URIs**, so it renders from
  any location with no supporting files;
- keeps the logo on **every** slide, matching `saab_template.pptx` (the official
  template references the logo from all 19 slide layouts);
- relies on the deck front matter `footer:` directive for the classification strip.

## Generated, not hand-edited

Do not edit `saab-theme.css` directly — regenerate it:

```bash
python3 scripts/make_theme.py            # uses repo + bundled assets by default
python3 scripts/make_theme.py --help     # --source / --logo / --cover / --out
```

`make_theme.py` derives the file from the source `@theme saab` CSS (the repo
submodule theme by default) plus `assets/brand/saab-logo.svg` and
`assets/brand/cover_background.jpg`.

## Kept in sync

If the upstream theme changes, re-run `make_theme.py`. The generated file is
committed so the skill works without the submodule or network access.

## Source of truth

| Asset | Origin |
| ----- | ------ |
| `assets/theme/saab-theme.css` | Generated from the `saab` theme (`themes/saab/saab-theme.css`) |
| `assets/brand/saab-logo.svg` | `presentation/themes/saab_logo_extracted.svg` |
| `assets/brand/saab-logo.png` | `saab_template.pptx` → `ppt/media/image2.png` (layout logo) |
| `assets/brand/cover_background.jpg` | `saab_template.pptx` → `ppt/media/image1.jpg` |
| `assets/brand/footer-classification.svg` | `themes/shared/footer-classification.svg` |
