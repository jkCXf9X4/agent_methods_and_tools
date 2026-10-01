---
name: LaTeX Article
description: Structure (disposition) and build LaTeX articles with the common_article scaffold and latex_build toolchain (latexmk + lualatex + biber, SVG/DOT figure conversion, release publishing)
---

# LaTeX Article

Reusable instructions for working with **LaTeX research papers** in this
repository. Source of truth is the `article_common_artifacts` submodule
(`3rd_party/article_common_artifacts/latex/`), which ships two things this skill
captures:

- **Disposition** — the paper scaffold: a small `main.tex`, an ordered
  `article/sections/` tree, shared preamble/commands/acronyms, and reusable
  artifacts (figures, tables, algorithms, TikZ).
- **Build** — the `latex_build` Python toolchain: `latexmk` + `lualatex` +
  `biber` into a local `build/`, optional SVG/DOT figure conversion, and tagged
  release PDFs.

## When to use

Use this skill when the task involves:

- Creating, editing, or restructuring a LaTeX paper or its sections.
- Applying the ordered-section disposition, shared preamble, or artifact layout.
- Building the PDF (`build.py`), converting figures, or publishing a release.
- Troubleshooting a build or adding the scaffold to a new paper repository.

## Non-negotiables

1. **Keep `main.tex` small and stable.** Content lives in section files
   (`article/sections/` in a scaffold repo, `sections/` here at top level).
   Do not move section content into `main.tex`.
2. **Preserve the structure, citation style, and section naming** already in the
   repo unless the task explicitly asks for restructure.
3. **Build through the shared entrypoint** — `python3 build.py` here (a thin
   wrapper that puts the submodule toolchain on `PYTHONPATH` and delegates to
   `latex_build.cli`). Use the standalone runner
   `scripts/build_paper.sh` from this skill when working outside the repo.
4. **Treat LaTeX errors as blockers.** After substantive edits, build and confirm
   the PDF is produced. Note unrelated pre-existing warnings separately.
5. **Use `--release` only when a release PDF is intentionally wanted.**
6. **Figures are generated** from `figures/**/*.svg`, `*.dot`, `*.gv` sources into
   `build/svgpdf/` and `build/dotpdf/`; reference the converted PDF (by stem),
   never commit generated PDFs.

## Toolchain

| Item | Value |
| ---- | ----- |
| Build entrypoint (repo) | `python3 build.py` → `latex_build.cli` |
| Standalone runner (skill) | `bash scripts/build_paper.sh` |
| Engine | `latexmk -pdf` driving `lualatex` (nonstopmode, halt-on-error) |
| Bibliography | `biber` via biblatex (`backend=biber`) |
| Build output dir | `build/` next to the root `.tex`; sandboxed TeX caches under `build/tex-cache/` |
| Figure conversion | SVG → `build/svgpdf/` (Inkscape), DOT/GV → `build/dotpdf/` (Graphviz) |
| Release dir | `release/article_<tag>.pdf` with `--release` / `--release-tag` |
| Requirements | `python3`, `latexmk`, `lualatex`, `biber` (+ optional `inkscape`, `dot`) |

Ensure submodules are initialised before building:

```bash
git submodule update --init --recursive
python3 build.py              # -> build/main.pdf
python3 build.py --release    # -> release/article_<timestamp>.pdf (only when needed)
```

### Standalone use (bundled resources)

The skill bundles everything needed to scaffold and build a paper without the
submodule:

| Resource | Purpose |
| -------- | ------- |
| `templates/scaffold/` | Copy of the shared article scaffold (disposition) |
| `scripts/latex_build/` | Copy of the build toolchain (used as fallback) |
| `scripts/build_paper.sh` | Runner that prefers the repo submodule, falls back to the bundled copy |

```bash
SKILL=.opencode/skills/latex-article
cp -r "$SKILL/templates/scaffold" my-paper && cd my-paper
bash "$SKILL/scripts/build_paper.sh"           # -> build/main.pdf
```

## Workflow

1. **Locate the disposition.** In this repo the sections are `sections/`
   (`00_abstract` … `11_conclusion_future_work`) wired into `main.tex`. In a
   scaffold repo they are `article/sections/` (`00_pre` … `90_post`) wired via
   `article/structure.tex`.
2. **Edit section files only.** Add content into the matching numbered section;
   only add a new file when a genuinely new top-level part is needed, using the
   next free index and naming pattern.
3. **Reuse artifacts and shared commands.** Figures/tables/algorithms/TikZ go in
   `article/artifacts/` and are `\input` from the section that owns them
   (see `references/disposition.md`). Use `\gls{...}` acronyms and the shared
   column types before reaching for new packages.
4. **Build and verify.** `python3 build.py`, then check `build/main.pdf` exists,
   page count is sensible, and the log has no new errors.
5. **Release only on request.** `python3 build.py --release` / `--release-tag <tag>`.
6. **Figures.** Add SVG (`figures/**/*.svg`) or DOT/GV (`*.dot`, `*.gv`) sources;
   the build converts them automatically. Do not hand-commit the converted PDFs.

## Disposition (summary)

Standard scaffold, root `.tex` = `main.tex`:

```
main.tex                      # thin: doc class, shared inputs, bib, title, \maketitle
article/
  structure.tex               # ordered \input of sections/00_pre .. 90_post
  shared/                     # preamble.tex, commands.tex, algorithm_setup.tex, acronyms.tex
  sections/                   # 00_pre .. 90_post (ordered, non-numbered TeX section headings)
  artifacts/                  # figures/ tables/ tikz/ algorithms/ (reusable \input snippets)
  bibliography.bib            # biber entries
figures/                      # SVG/DOT/GV sources (auto-converted at build time)
```

Key wiring (from `article/shared/preamble.tex`): `\input@path` adds `article/`,
`article/sections/`, `article/artifacts/...` and `\graphicspath` adds
`build/svgpdf/`, `build/dotpdf/`, `figures/` — so `\input{artifact_name}` and
`\includegraphics{stem}` resolve out of the box.

Full detail — including the section-by-section intent, artifact idioms, naming
rules, and how `main.tex` stays thin: `references/disposition.md`.

## Build (summary)

`build.py` sets `PYTHONPATH` to `3rd_party/article_common_artifacts/latex/scripts`
and calls `python3 -m latex_build.cli`:

- `--tex <path>` root `.tex` to build (default `./main.tex`)
- `--release` copy the PDF into `release/article_<tag>.pdf`
- `--release-tag <tag>` same, with your tag
- `--figures-out-dir <dir>` override where converted figures go (default `build`)

The toolchain sandboxes TeX/XDG state under `build/` so one project's build never
pollutes another, converts figures incrementally (mtime-based), and errors with a
clear message when `latexmk`, `biber`, or the expected PDF is missing.

Full detail — flags, inner modules (`config` / `graphics` / `text`), env
sandboxing, and troubleshooting: `references/build.md`.

## Reference files

- `references/disposition.md` — full scaffold layout, section intents, artifact idioms, naming rules.
- `references/build.md` — toolchain internals, flags, outputs, env sandboxing, troubleshooting.
- `references/snippets.md` — copy-paste LaTeX for figures, tables, algorithms, TikZ, acronyms, cross-refs.
- `templates/scaffold/` — ready-to-copy paper scaffold.
- `scripts/build_paper.sh` — standalone build runner (uses submodule when present, else bundled).
- `scripts/latex_build/` — bundled copy of the build toolchain (fallback).