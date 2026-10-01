# Saab Colour Profile

Source of truth: the Office theme inside
`3rd_party/article_common_artifacts/pressentation/templates/saab_template.pptx`
(`ppt/theme/theme1.xml`, accent colours), mirrored by the CSS custom properties in
`3rd_party/article_common_artifacts/pressentation/themes/saab/saab-theme.css`.

## Core palette

| Token | Hex | RGB | PPTX slot | Role |
| ----- | --- | --- | --------- | ---- |
| Saab Blue | `#00508C` | 0, 80, 140 | accent5 | Primary brand; headings, rules, table headers, links |
| Saab Yellow | `#FAB900` | 250, 185, 0 | accent3 | Highlight; cover rule, blockquote border |
| Saab Red | `#E61419` | 230, 20, 25 | accent6 | Sparing alert/emphasis accent only |
| Saab Dark Grey | `#373737` | 55, 55, 55 | dk2 / accent1 | Body headings and body text |
| Saab Beige | `#BEAF96` | 190, 175, 150 | accent4 | Secondary neutral, subtle fills |
| Light Warm Grey | `#E1E1DC` | 225, 225, 220 | lt2 / accent2 | Panel / surface tint |
| Deep Navy (override) | `#0B3D6E` | 11, 61, 110 | — | Deck-level `h1`/`h2` colour |
| Ink | `#1A1A1A` | 26, 26, 26 | — | Slide body text |
| Muted Grey | `#5A5A5A` | 90, 90, 90 | — | Secondary text |
| White | `#FFFFFF` | 255, 255, 255 | lt1 | Slide background |

## Supporting surfaces and lines

These are the exact values used by the Marp theme. Reuse them instead of inventing
new tints.

| Use | Hex | Where |
| --- | --- | ------ |
| Light blue panel | `#F4F7FA` | Blockquote background, zebra table rows, code block background |
| Code inline background | `#EEF2F6` | Inline `code` |
| Hairline border | `#DBE4EE` | Table/code borders, figure frames |
| Cover gradient | `rgba(11,61,110,.30)` → `rgba(0,40,80,.45)` | Over `cover_background.jpg` |
| Cover wash | `rgba(0,80,140,.55)` | Title/thank background tint |

## Usage rules

- **Blue is the primary.** Headings, emphasis, list markers, table headers and
  accents are Saab blue. Deep Navy (`#0B3D6E`) is the deck-level heading colour.
- **Yellow is a highlight, not a text colour on white** (poor contrast). Use it for
  rules/underlines and small emphasis marks.
- **Red is an accent, ≤ 10% of a slide.** Never red text on blue, never red fill
  behind body text.
- **Body text is `#1A1A1A` on white.** Keep large filled areas light.
- **Never recolour, outline, or add effects to the Saab logo.**
- Keep total colour count per slide low: one primary, one neutral surface, one
  accent.

## Accessibility / presentation safety

- Primary contrast pairs (measured): White on Saab Blue ≈ **8.6:1**; Dark Grey
  `#373737` on White ≈ **12:1**; Ink on White ≈ **17:1** — all pass WCAG AA/AAA.
- Avoid Saab Yellow on White for text (≈ **1.7:1**); pair yellow with blue or grey.
- The blue/yellow/red accent system survives common colour-vision deficiencies
  because blue carries meaning (headings/accents) while red is only supplementary.
  **Do not rely on colour alone** — label or annotate status in diagrams.
- Export at full colour; do not use grayscale or "print economy" modes for decks.
- Verify exported PDF/PPTX colour: Marp and Office render hex values directly, so
  no CMYK conversion is needed for on-screen or projector use.

## Applying the palette outside the theme

When a figure or diagram needs the brand colours, use the CSS custom properties in
SVG/HTML (they inherit from the theme):

```css
color: var(--saab-blue);        /* #00508C */
stroke: var(--saab-dark);       /* #373737 */
fill: var(--saab-yellow);       /* #FAB900 */
```

For standalone SVG, hard-code the hex values above so the file renders correctly
before it is embedded in a slide.
