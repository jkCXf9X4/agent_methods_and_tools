from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .config import BuildConfig


def build_text_artifacts(config: BuildConfig) -> Path:
    config.build_dir.mkdir(parents=True, exist_ok=True)
    ensure_text_toolchain()
    build_env = create_text_build_env(config)

    latexmk_cmd = [
        "latexmk",
        "-pdf",
        "-e",
        "$bibtex_use = 2;",
        "-pdflatex=lualatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S",
        f"-outdir={config.build_dir.resolve()}",
        str(config.tex_path),
    ]

    code = run_command(latexmk_cmd, cwd=config.project_dir, env=build_env)
    if code != 0:
        raise RuntimeError("latexmk failed")

    built_pdf = config.build_dir / f"{config.tex_path.stem}.pdf"
    if not built_pdf.exists():
        raise RuntimeError(f"Expected PDF not found at {built_pdf}")

    return built_pdf


def ensure_text_toolchain() -> None:
    if shutil.which("latexmk") is None:
        raise RuntimeError("latexmk not found in PATH (install TeX Live or latexmk)")
    if shutil.which("biber") is None:
        raise RuntimeError("biber not found in PATH (required by biblatex backend=biber)")


def create_text_build_env(config: BuildConfig) -> dict[str, str]:
    env = os.environ.copy()
    cache_root = config.build_dir / "tex-cache"
    texmf_var = cache_root / "texmf-var"
    texmf_config = cache_root / "texmf-config"
    texmf_home = cache_root / "texmf-home"
    xdg_cache = cache_root / "xdg-cache"

    for path in (texmf_var, texmf_config, texmf_home, xdg_cache):
        path.mkdir(parents=True, exist_ok=True)

    env["TEXMFVAR"] = str(texmf_var.resolve())
    env["TEXMFCONFIG"] = str(texmf_config.resolve())
    env["TEXMFHOME"] = str(texmf_home.resolve())
    env["XDG_CACHE_HOME"] = str(xdg_cache.resolve())
    env["HOME"] = env.get("HOME", str(config.project_dir.resolve()))
    return env


def publish_release_pdf(built_pdf: Path, release_dir: Path, release_tag: str | None = None) -> Path:
    release_dir.mkdir(parents=True, exist_ok=True)
    tag = release_tag if release_tag else datetime.now().strftime("%Y%m%d_%H%M%S")
    release_pdf = release_dir / f"article_{tag}.pdf"
    shutil.copy2(built_pdf, release_pdf)
    return release_pdf


def run_command(arguments: list[str], cwd: Path, env: dict[str, str] | None = None) -> int:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    print(result.stdout)
    print(result.stderr)
    return result.returncode
