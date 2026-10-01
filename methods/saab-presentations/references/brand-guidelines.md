# Saab Presentation Brand Guidelines

Style, typography, and figure direction for Saab decks built from the Marp theme.
Colour detail lives in `color-profile.md`.

## 1. Visual identity

| Element | Rule |
| ------- | ---- |
| Format | 16:9 widescreen (13.333 in × 7.5 in) |
| Typeface | Arial (`Helvetica Neue`/`Helvetica` fallback); monospace `Consolas`/`Liberation Mono` for code |
| Logo | Saab logo, top-right, on every slide; aspect ratio preserved |
| Footer | `COMPANY UNCLASSIFIED \| NOT EXPORT CONTROLLED \| NOT CLASSIFIED` on every slide |
| Page numbers | `paginate: true` |
| Cover | Saab blue with `cover_background.jpg`, yellow rule under the title |
| Closing | Reuses the cover treatment (`_class: thank`) |

Never stretch, recolour, rotate, or add effects to the logo. Never remove or
paraphrase the classification footer.

## 2. Typography

The theme sets sizes in `rem` relative to a 16:9 frame. Keep these proportions:

| Level | Colour | Weight | Size |
| ----- | ------ | ------ | ---- |
| Slide heading `h1` | `#0B3D6E` | 700 | 1.6rem, blue bottom rule |
| Sub-heading `h2` | `#0B3D6E` | 700 | 1.15rem |
| Sub-heading `h3` | Saab blue | 600 | 1rem |
| Body / list | `#1A1A1A` | 400 | default, ~1.3 line height |
| Strong | Saab blue | 700 | inherited |
| Emphasis | `#373737` italic | 400 | inherited |

Rules:

- **One `h1` per slide.** It carries the message, not a generic label.
  Write "Traceability breaks at the handover", not "Traceability".
- **Sentence case for headings.** Avoid ALL-CAPS except the classification footer.
- **Bullets: ≤ 5 per slide, one line each where possible.** Move detail into
  speaker notes (`<!-- ... -->`).
- **Do not hand-set font sizes or colours in Markdown/HTML.** Use `_class: small`
  for a single denser slide if unavoidable; prefer splitting the slide.
- **Code** is monospace on a light blue panel; keep snippets short and untruncated.

## 3. Layout and whitespace

- Prefer the **text + figure** two-column layout (`.cols`) for substantive slides.
- The theme reserves vertical padding (`3.8rem` top, `5.5rem` bottom) for the
  logo/footer band — **do not place content in those bands**; side figures are
  already bounded to the text band.
- Keep a clear reading path: heading → content → figure/edge. Left-align text.
- Fill the frame deliberately; an empty bottom third reads as an unfinished slide,
  but crowding is worse. Split instead.
- Use `![bg contain](figure.png)` for a full-slide figure and add at most a short
  heading/caption.
- Never allow text or image overflow in the exported PDF/PPTX — always build and
  inspect.

## 4. Figures and diagrams (graphical guidelines)

Two classes of visual, kept distinct:

- **STRUCTURED** — diagrams, architectures, flows, plots. Author as **editable
  vector source** (SVG, draw.io, TikZ, Mermaid) next to the deck, then export PNG.
- **PROMPT** — conceptual/illustrative art only. Generate with the direction below;
  never use generated art where an accurate technical diagram is required.

### 4.1 Figure style

- 16:9 composition, white or very light background, generous negative space for
  labels and overlays.
- Restrained blue / teal / charcoal palette with a **muted red accent** (use Saab
  blue `#00508C` as the dominant tone). Flat vector-like editorial style.
- Consistent stroke weights and label sizes; legible from the back of a room
  (min ~18 px equivalent for projected labels).
- Reuse the palette tokens from `color-profile.md`; a thin continuous "red thread"
  is the established motif for traceability.

### 4.2 Figure do-nots

Do not include in figures:

- Readable words, letters, or invented product names.
- Fake UI text, fake XML/code, or literal tool screenshots.
- Logos (the slide chrome supplies the Saab logo).
- Photorealistic, classified-looking aircraft detail.
- Decorative gradients, drop shadows on diagrams, or clip-art.

### 4.3 Reusable image-generation direction

Copy this preamble into any image-generation prompt for a Saab deck:

> Create a clean 16:9 conceptual systems-engineering visual, editorial and
> restrained rather than decorative. Use blue, teal, and charcoal with a muted red
> accent on a light background, flat vector-like style, with generous empty space
> for labels and arrows. Do not include readable words, letters, logos, XML, fake
> UI text, or detailed aircraft imagery.

The repository already stores production prompts for concept art in
`presentation/generation_prompts.md` — extend that file rather than duplicating
prompts here.

### 4.4 Exporting figures

```bash
bash presentation/export_svg_to_png.sh   # every SVG under presentation/ -> PNG
```

This uses Inkscape and falls back to ImageMagick `convert` at 300 dpi. Keep the
`.svg` source and the exported `.png` side by side; the deck references the PNG
(`![bg contain]`) or SVG directly in `.col-right`.

## 5. Language and tone

- Engineering-editorial: precise, calm, evidence-led. Short declarative sentences.
- Headlines state the **takeaway**; bullets give the supporting evidence.
- Define acronyms on first use (FMI, SSP, MBSE, SysML v2).
- Keep the classification footer wording exactly as specified — it is an
  export-control statement, not decoration.
- Put delivery cues in speaker notes: "whisper", "point to edge case", timing.

## 6. Quality checklist before export

- [ ] 16:9, Arial, theme `saab`.
- [ ] Saab logo top-right on every slide.
- [ ] Classification footer exact and present on every slide.
- [ ] One message per `h1`; ≤ 5 bullets; no overflow.
- [ ] Palette only; red used sparingly; yellow never as text on white.
- [ ] Figures are editable-source based, on-palette, and legible.
- [ ] Speaker notes present and inside HTML comments.
- [ ] PDF and PPTX both build without errors and were visually checked.
