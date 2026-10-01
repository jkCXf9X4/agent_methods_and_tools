from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from .config import BuildConfig


def prepare_graphics(config: BuildConfig) -> None:
    svg_sources = list(iter_graphic_sources(config.figures_dir, extensions=(".svg",)))
    convert_svgs_to_pdf(svg_sources, config.figures_output_dir / "svgpdf", temp_path=config.build_dir)

    dot_sources = list(iter_graphic_sources(config.figures_dir, extensions=(".dot", ".gv")))
    print(f"Dot sources: {dot_sources}")
    convert_graphviz_to_pdf(dot_sources, config.figures_output_dir / "dotpdf")


def iter_graphic_sources(figures_dir: Path, *, extensions: tuple[str, ...]) -> Iterable[Path]:
    if not figures_dir.exists():
        return []

    sources: list[Path] = []
    for extension in extensions:
        for path in figures_dir.rglob(f"*{extension}"):
            if "__in_work__" in path.parts:
                continue
            sources.append(path)
    return sorted(sources)


def convert_svgs_to_pdf(svg_files: Iterable[Path], out_dir: Path, temp_path: Path) -> None:
    """Convert SVG files into PDF for LaTeX inclusion."""

    if shutil.which("inkscape") is None:
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    ink_env = os.environ.copy()
    ink_env["HOME"] = str((temp_path / "inkscape_home").resolve())
    ink_env["XDG_CONFIG_HOME"] = str((temp_path / "xdg_config").resolve())
    ink_env["XDG_DATA_HOME"] = str((temp_path / "xdg_data").resolve())
    Path(ink_env["HOME"]).mkdir(parents=True, exist_ok=True)
    Path(ink_env["XDG_CONFIG_HOME"]).mkdir(parents=True, exist_ok=True)
    Path(ink_env["XDG_DATA_HOME"]).mkdir(parents=True, exist_ok=True)

    for svg in svg_files:
        if not svg.exists():
            continue
        out_pdf = out_dir / f"{svg.stem}.pdf"
        if out_pdf.exists() and out_pdf.stat().st_mtime >= svg.stat().st_mtime:
            continue
        result = subprocess.run(
            [
                "inkscape",
                str(svg),
                "--export-type=pdf",
                f"--export-filename={out_pdf}",
                "--export-text-to-path",
                "--export-area-drawing",
            ],
            capture_output=True,
            text=True,
            env=ink_env,
        )
        if result.returncode != 0:
            print(f"warning: failed to convert {svg} -> {out_pdf}")
            print(result.stdout)
            print(result.stderr)


def convert_graphviz_to_pdf(dot_files: Iterable[Path], out_dir: Path) -> None:
    """Convert Graphviz DOT or GV files into PDF for LaTeX inclusion."""

    if shutil.which("dot") is None:
        print("warning: Graphviz 'dot' not found; skipping .dot -> PDF conversion")
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    for dot_file in dot_files:
        if not dot_file.exists():
            continue
        out_pdf = out_dir / f"{dot_file.stem}.pdf"
        if out_pdf.exists() and out_pdf.stat().st_mtime >= dot_file.stat().st_mtime:
            continue
        result = subprocess.run(
            ["dot", "-Tpdf", str(dot_file), "-o", str(out_pdf)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            print(f"warning: failed to convert {dot_file} -> {out_pdf}")
            print(result.stdout)
            print(result.stderr)
