# Slide Patterns (Marp + `saab` theme)

Copy-paste markup for decks built with `@theme saab`. Deck files live at
`presentation/versions/<version>/slides.marp.md` and must have a sibling
`themes` symlink (`themes -> ../../themes`).

## Front matter (every deck)

```markdown
---
marp: true
theme: saab
paginate: true
size: 16:9
footer: "COMPANY UNCLASSIFIED | NOT EXPORT CONTROLLED | NOT CLASSIFIED\n <Author> | Version <n>"
---
```

The `footer` directive renders the classification strip bottom-centre; `theme:
saab` resolves to `presentation/themes/saab-theme.css` (pass it with `--theme` if
the deck is not under `presentation/versions/`).

## Title / cover slide

```markdown
<!-- _class: title -->

# Deck title — the main claim
## Subtitle in yellow

Author · Affiliation
Co-author · Affiliation

<!--
Speaker notes go here; never exported.
-->
```

## Content slide (heading + bullets)

```markdown
# Headline states the takeaway

- First supporting point
- Second point with **branded emphasis**
- Limit to five bullets

> Optional callout: one sentence that carries the core claim.
```

## Text + figure (two-column)

```markdown
# From architecture to executable simulation

<div class="cols">

<div class="col-left">

- Architecture is the source of intent
- Artifacts are generated, not hand-edited
- Reverse sync is validated and gated

</div>

<div class="col-right">
<img src="../../assets/use_case_round_trip.png" alt="Round-trip workflow" />
</div>

</div>
```

Column ratios: the theme defaults to `1.4 : 1`. Use the helper classes rather
than inline styles (Marp strips inline `style`):

- `<div class="cols cols-left-lg">` — wider text column (`1.6 : 1`).
- `<div class="cols cols-right-lg">` — wider figure column (`1 : 1.4`).

## Full-slide figure

```markdown
![bg contain](../../assets/structured_slide06_ssp.png)

<!--
Interpret the figure in the notes.
-->
```

Use `![bg contain](...)` to fit the whole figure inside the frame; `cover` crops.
Keep the figure on-palette and legible (see `brand-guidelines.md`).

## Stacked figures in one column

Decks may add a tiny local style block for a vertical stack inside `.col-right`:

```markdown
<style>
section .col-right .stacked { display: flex; flex-direction: column; justify-content: center; }
section .col-right .stacked img { max-height: 46%; }
</style>
```

```markdown
<div class="col-right">
<div class="stacked">
<img src="../../assets/simulators/small.png" />
<img src="../../assets/simulators/large.png" />
</div>
</div>
```

## Tables

```markdown
| Prefix | Means |
|---|---|
| **Interface** | visible contract, hides internals |
| **Composite** | many parts as one whole |
| **Executable** | runnable → produces behavior |
```

Rendered with a Saab-blue header row and zebra striping.

## Denser slide (use sparingly)

```markdown
<!-- _class: small -->

# A deliberately dense summary

...
```

`small` reduces base font size to `0.85em`. Prefer splitting into two slides.

## Closing slide

```markdown
<!-- _class: thank -->

# Thank you — Q&A

- Tool / repository pointer
- Contact and affiliations
```

## Notes and gotchas

- **Speaker notes** go in HTML comments (`<!-- ... -->`) and are excluded from export.
- **No inline `style` for layout** — Marp strips it. Use the theme classes.
- **Image paths** are relative to the deck file (`../../assets/...`,
  `../../figures/...`); run the build from the repository root and pass
  `--allow-local-files`.
- **Do not edit the shared theme** in the submodule unless the change is meant for
  every deck; the theme is `3rd_party/article_common_artifacts/pressentation/themes/saab/saab-theme.css`
  and is reached through `presentation/themes/saab-theme.css`.
- The theme's regular slides intentionally clear the base logo/footer background;
  the logo/footer come from the `title`/`thank` backgrounds and the `footer:`
  directive respectively. Verify both appear after export.
