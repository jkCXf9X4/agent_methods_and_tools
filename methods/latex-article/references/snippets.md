# Snippets

Copy-paste building blocks that are known to work with the shared scaffold
(`preamble.tex`, `commands.tex`, `algorithm_setup.tex`, `acronyms.tex`).
Adapt names/paths; keep labels consistent (`fig:`, `tab:`, `algo:`, `sec:`).

## Untitled preamble (keywords / abstract)

```latex
\textbf{Keywords.} MBSE; SysML v2; co-simulation; round-trip engineering
\medskip
```

```latex
\textbf{Abstract.} One or two sentences stating the problem, method, and result.
```

## Figure (in `article/artifacts/figures/`)

```latex
\begin{figure}
    \centering
    \includegraphics[width=\linewidth]{my_diagram}   % SVG/DOT compiled to PDF; reference by stem
    \caption{Short caption.}
    \label{fig:my_diagram}
\end{figure}
```

## Table (in `article/artifacts/tables/`)

Uses the shared ragged-right `Y` column type and `booktabs` rules:

```latex
\begin{table}[t]
\centering
\caption{Short caption.}
\label{tab:metrics}
\begin{tabularx}{\linewidth}{Y Y Y}
\toprule
\textbf{Column A} & \textbf{Column B} & \textbf{Column C} \\
\midrule
value & value & value \\
value & value & value \\
\bottomrule
\end{tabularx}
\end{table}
```

## Algorithm (in `article/artifacts/algorithms/`)

```latex
\begin{algorithm}[tb]
\caption{Orchestration algorithm}
\label{algo:orchestrate}
\SetAlgoNoLine
\DontPrintSemicolon

\KwSeq{
    \ForEach{macro step $H$}{
        \KwPar{
            \ForEach{group $G_k$}{
                Execute the group schedule\;
            }
        }
    }
}
\end{algorithm}
```

## TikZ picture (in `article/artifacts/tikz/`)

Pure picture, no `figure` wrapper — embed it via `resizebox` inside a figure:

```latex
\begin{tikzpicture}[
  >=Latex,
  node/.style={circle,draw,inner sep=0pt,minimum size=3.2mm},
  solid/.style={-Latex,thick}
]
\node[node] (a) at (0, 0) {};
\node[node] (b) at (2, 0) {};
\draw[solid] (a) -- (b);
\end{tikzpicture}
```

In the figure artifact:

```latex
\begin{figure}
    \centering
    \resizebox{0.75\linewidth}{!}{\input{artifacts/tikz/my_diagram}}
    \caption{...}
    \label{fig:my_diagram}
\end{figure}
```

## Cross-references (cleveref)

```latex
As shown in \cref{fig:my_diagram} and \cref{tab:metrics}, ...
\Cref{algo:orchestrate} summarizes the orchestration.
See \cref{sec:methodology}.
```

## Acronyms (glossaries)

Register in `article/shared/acronyms.tex`, then use anywhere:

```latex
\newacronym{fmi}{FMI}{Functional Mock-up Interface}
```

```latex
\gls{fmi}  % first use: "Functional Mock-up Interface (FMI)"; then "FMI"
\glspl{uc} % "Use Cases (UCs)" / "UCs"
```

## Citations

Bib entries go in `article/bibliography.bib` (this repo: top-level
`references.bib`); cite with biblatex:

```latex
\cite{key}         % [1]
\parencite{key}    % (Key, 2026) for style=apa
\citetitle*{key}   % title only, no brackets
```

## New numbered section file

Follow the `NN_slug.tex` pattern (e.g. `45_experiments.tex`) and wire it into
`article/structure.tex` at the right position — that file is the single ordering
point, so reordering the paper never touches content files.