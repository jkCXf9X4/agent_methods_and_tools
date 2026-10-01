# Build: the latex_build toolchain

The build is a Python entrypoint, `latex_build.cli`, living in the
`article_common_artifacts` submodule under
`3rd_party/article_common_artifacts/latex/scripts/`. A thin `build.py` at the
repository root puts that directory on `PYTHONPATH` and delegates:

```bash
python3 build.py                 # -> build/main.pdf
python3 build.py --release       # -> release/article_<timestamp>.pdf
python3 build.py --release-tag v2
python3 build.py --tex path/to/other.tex
python3 build.py --figures-out-dir build
```

Standalone runner (skill's copy, prefers submodule, falls back to bundled):

```bash
bash .opencode/skills/latex-article/scripts/build_paper.sh
bash .opencode/skills/latex-article/scripts/build_paper.sh --tex mypaper/main.tex
```

## Flags

| Flag | Default | Effect |
| ---- | ------- | ------ |
| `--tex` | `./main.tex` | Root `.tex` to build (must exist, must be `.tex`) |
| `--release` | off | Copy built PDF to `release/article_<time_tag>.pdf` |
| `--release-tag <tag>` | — | Same as `--release` but with your tag in the name |
| `--figures-out-dir <dir>` | `build` | Where converted SVG/DOT PDFs are written |

## What a build does

1. **Resolve config** (`config.py`). Everything is derived from the root `.tex`:
   - `project_dir` = directory of the `.tex`
   - `build_dir` = `project_dir/build`
   - `figures_dir` = `project_dir/figures`
   - `figures_output_dir` = `project_dir/<figures-out-dir>` (default `build`)
   - `release_dir` = `project_dir/release`
2. **Prepare graphics** (`graphics.py`), incrementally (skips regeneration when
   the output PDF is newer than the source):
   - `figures/**/*.svg` → `build/svgpdf/<stem>.pdf` via `inkscape`
     (`--export-type=pdf --export-text-to-path --export-area-drawing`), with a
     sandboxed `HOME`/`XDG_*` under `build/`.
   - `figures/**/*.dot` & `*.gv` → `build/dotpdf/<stem>.pdf` via `dot -Tpdf`.
   - Skips anything under a path segment named `__in_work__`.
   - Missing `inkscape`/`dot` is not fatal — SVG/DOT conversion is simply
     skipped (a warning is printed for dot).
3. **Build the paper** (`text.py`): runs

   ```
   latexmk -pdf \
     -e '$bibtex_use = 2;' \
     -pdflatex='lualatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S' \
     -outdir=<build_dir> <root.tex>
   ```
   after verifying `latexmk` and `biber` exist. Bibliography is `biblatex` with
   backend `biber`.
4. **Sandbox TeX state** under `build/tex-cache/` (`TEXMFVAR`, `TEXMFCONFIG`,
   `TEXMFHOME`, `XDG_CACHE_HOME`) so builds are reproducible and don't touch the
   user TeX tree.
5. **Publish release** only when `--release`/`--release-tag`: copy the built PDF
   to `release/article_<tag>.pdf`.

Expected outputs for `./main.tex`:

```
build/main.pdf
build/main.log
build/svgpdf/    (when SVG sources + inkscape)
build/dotpdf/    (when DOT/GV sources + dot)
release/         (only with --release)
```

## Error behaviour (blockers)

- `LaTeX source not found: <path>` / `expected a .tex file` — bad `--tex`.
- `latexmk not found in PATH` / `biber not found in PATH` — missing TeX Live tool.
- `latexmk failed` — a real LaTeX error; inspect `build/main.log` for the first
  `!` line and fix it before re-running.
- `Expected PDF not found at build/main.pdf` — most likely failure: the engine
  ended before producing output; check the log.

Treat these as blockers. Non-blocking warnings (e.g. overfull boxes, font
substitutions) can be noted but do not gate the build.

## Troubleshooting

- **First build is slow** — graphics conversion + `luaotfload` cache population.
  Subsequent builds are incremental.
- **`lualatex` hangs or restarts fonts** — the `build/tex-cache` is sandboxed by
  design; delete `build/` (or `build/tex-cache/`) and rebuild.
- **Biber version mismatches `main.bcf`** — delete `build/main.bcf` and rebuild.
- **Figure not updating after an SVG edit** — conversion is mtime-based; touch
  the `.svg` (or remove `build/svgpdf/<stem>.pdf`) and rebuild.
- **Submodule not initialised** — `git submodule update --init --recursive`,
  otherwise `build.py` prints the exact command to run.
- **Prefer the local environment** — if a venv/toolchain is present, use it
  (see `AGENTS.md`); the toolchain is plain `python3` + system TeX Live, no pip
  deps required.

## Keeping the bundled copy in sync

The skill bundles a copy of the toolchain at `scripts/latex_build/` so paper
builds work outside the repository. It is a verbatim copy of
`3rd_party/article_common_artifacts/latex/scripts/latex_build/`. Re-sync it
whenever the submodule version changes:

```bash
cp -r 3rd_party/article_common_artifacts/latex/scripts/latex_build \
      .opencode/skills/latex-article/scripts/latex_build
```

`scripts/build_paper.sh` uses the repository submodule when it exists and only
falls back to the bundled copy — so in this repo the submodule is always the
authority.