# Disposition: the article scaffold

This is the structure this repository's LaTeX papers follow. The canonical copy
lives in `3rd_party/article_common_artifacts/latex/template/`; the skill bundles
it at `templates/scaffold/`.

## Design idea

`main.tex` stays small and stable. All structure and content live in
`article/`, and the parts that change most — sections and reusable artifacts —
are separate files with predictable names. Reordering a paper is a one-line edit
in `article/structure.tex`.

## Full tree

```
main.tex
article/
  structure.tex                # the ONLY place that orders sections
  bibliography.bib             # biber / biblatex entries
  shared/
    preamble.tex               # packages, geometry, graphicspath, input@path
    commands.tex               # custom column types, \nohyphens, parindent
    algorithm_setup.tex        # algorithm2e setup + custom keywords
    acronyms.tex               # \newacronym definitions used via \gls
  sections/
    00_pre.tex                 # front-matter hooks, journal metadata, custom cmds
    10_keywords.tex            # \textbf{Keywords.} ... \medskip
    20_abstract.tex            # \textbf{Abstract.} ... (no \section)
    30_introduction.tex        # \section{Introduction}
    40_background.tex          # \section{Background}  (theory/assumptions/prior work)
    50_methodology.tex         # \section{Methodology} (+ \input algorithms)
    60_result.tex              # \section{Results}    (+ \input figures/tables)
    70_discussion.tex          # \section{Discussion}
    80_conclusion.tex          # \section{Conclusion}
    90_post.tex                # \subsection{Acknowledgments.} + \section*{References}
  artifacts/
    figures/   example_figure.tex   # \begin{figure} ... \end{figure}
    tables/    example_table.tex    # \begin{table}[t] ... \end{table}
    tikz/      example_tikz.tex     # \begin{tikzpicture} ... \end{tikzpicture}
    algorithms/example_algorithm.tex# \begin{algorithm}[tb] ... \end{algorithm}
```

## Section convention

- Files are **numbered by position**, not by heading: `00_`, `10_`, `20_`, …
  `90_`. The numeric prefix fixes order even though the TeX headings themselves
  are unnumbered by default.
- Only `10_keywords`/`20_abstract` and `90_post` use rich text; the rest each
  own one `\section{}` and hold the prose for that part.
- Front matter (`00_pre`) and back matter (`90_post`) get their own files so the
  `\section*{References}` / `\printbibliography[heading=none]` block is not
  buried in `main.tex`.
- Add new content to the existing file that owns that part of the paper. Only
  add a new numbered file for a genuinely new top-level part (insert between two
  numbers, e.g. `45_experiments.tex`), then wire it in `structure.tex`.

## How `main.tex` stays thin

```latex
\documentclass[12pt]{article}
\input{article/shared/preamble}
\input{article/shared/commands}
\input{article/shared/algorithm_setup}
\input{article/shared/acronyms}
\addbibresource{article/bibliography.bib}
\title{...} \author[...]{...} \affil[...]{...}
\begin{document}
\maketitle
\input{article/structure}
\section*{References}
\printbibliography[heading=none]
\end{document}
```

## Path magic (do not fight it)

`article/shared/preamble.tex` sets:

```latex
\makeatletter
\def\input@path{{article/}{article/sections/}{article/artifacts/}%
  {article/artifacts/figures/}{article/artifacts/tables/}{article/artifacts/tikz/}}
\makeatother
\graphicspath{{build/svgpdf/}{build/dotpdf/}{figures/}}
```

Consequences:

- `\input{50_methodology}` works from anywhere (file lives in `sections/`).
- `\input{example_algorithm}` resolves from the artifacts dirs.
- `\includegraphics{stem}` finds figures in `build/svgpdf/`, `build/dotpdf/`,
  and `figures/` — so SVG/DOT sources are compiled to PDF and then referenced by
  bare stem, e.g. `\includegraphics[width=0.8\linewidth]{my_diagram}`.

## Artifact idioms

- **Figure** (`artifacts/figures/`): `\begin{figure}` + `\centering` +
  `\resizebox{0.75\linewidth}{!}{\input{artifacts/tikz/...}}` or
  `\includegraphics{...}` + `\caption{...}` + `\label{fig:...}`.
- **Table** (`artifacts/tables/`): `table[t]`, `tabularx` + shared `Y`/`L`/`N`
  column types, `booktabs` rules, `\caption` + `\label{tab:...}`.
- **Algorithm** (`artifacts/algorithms/`): `algorithm2e` float with
  `\SetAlgoNoLine`, `\KwSeq{...}`, `\ForEach{...}`, `\KwPar{...}`; label
  `algo:...`; `\Cref` gives "Algorithm 1".
- **TikZ** (`artifacts/tikz/`): pure picture snippet (no `figure` wrapper) so it
  can be `\input` inside a `resizebox`/`figure`. `\usetikzlibrary{arrows.meta,positioning}`
  is already loaded.

## Shared commands worth reusing

- Column types: `N{width}`, `Y`, `L{width}` (ragged-right, no hyphenation) from
  `commands.tex`.
- `\gls{acronym}` / `\glspl{acronym}` for every term registered in
  `acronyms.tex` (`\glsdisablehyper` is set, first use prints full form).
- Algorithm keywords `\KwPar in parallel`, `\KwSeq in sequence`, `\KwCommit`,
  `\KwRollback`, `\KwSync`, `\KwLet`, `\KwBreak`, `\KwContinue` from
  `algorithm_setup.tex`.
- `\cref{...}` / `\Cref{...}` (cleveref) instead of writing "Figure/Table/
  Algorithm" by hand.

## This repository's concrete disposition

This paper (`2026_purpose_driven_modelling`) uses a repo-local INCOSE-flavoured
`main.tex` with top-level `sections/`:

- `sections/00_abstract.tex` … `sections/11_conclusion_future_work.tex`,
  each numbered by position: `00_abstract`, `01_introduction`,
  `02_related_work`, `03_problem_statement`, `04_implementation`,
  `05_methodology`, `07_case_study`, `08_results`, `09_discussion`,
  `11_conclusion_future_work`.
- `main.tex` inputs them in order between the abstract/keywords block and
  `\section{References}`.
- Figures are `figures/**/*.{svg,dot,gv}` compiled by the build into
  `build/svgpdf/` / `build/dotpdf/`; `\graphicspath` includes
  `{./}{figures/}{build/svgpdf/}{build/dotpdf/}`.
- Bibliography: top-level `references.bib`, `style=apa`, `backend=biber`.

Same rules apply: edit the numbered section file, keep `main.tex`'s structure
intact, and build with `python3 build.py`.