from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuildConfig:
    latex_dir: Path
    tex_path: Path
    project_dir: Path
    build_dir: Path
    figures_output_dir: Path
    release_dir: Path
    figures_dir: Path
    release: bool
    release_tag: str | None


def resolve_build_config(
    *,
    tex_argument: str,
    figures_out_argument: str | None,
    release: bool,
    release_tag: str | None,
) -> BuildConfig:
    tex_path = Path(tex_argument).resolve()
    latex_dir = tex_path.parent
    if not tex_path.exists():
        raise ValueError(f"LaTeX source not found: {tex_path}")
    if tex_path.suffix.lower() != ".tex":
        raise ValueError(f"expected a .tex file, got: {tex_path}")

    project_dir = tex_path.parent
    figures_output_dir = project_dir / figures_out_argument

    return BuildConfig(
        latex_dir=latex_dir,
        tex_path=tex_path,
        project_dir=project_dir,
        build_dir=project_dir / "build",
        figures_output_dir=figures_output_dir,
        release_dir=project_dir / "release",
        figures_dir=project_dir / "figures",
        release=release,
        release_tag=release_tag,
    )
