from __future__ import annotations

import argparse
from pathlib import Path

from .config import resolve_build_config
from .graphics import prepare_graphics
from .text import build_text_artifacts, publish_release_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the LaTeX document in this repository.")
    parser.add_argument(
        "--tex",
        default="./main.tex",
        help="Path to the root .tex document to build, relative to the current working directory or absolute.",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Publish a release copy in release/article_[time_tag].pdf.",
    )
    parser.add_argument(
        "--figures-out-dir",
        default="build",
        help="Directory where generated SVG/DOT figure PDFs are written. Defaults to the local build directory.",
    )
    parser.add_argument(
        "--release-tag",
        default=None,
        help="Optional release tag used in release filename; implies --release behavior.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = resolve_build_config(
            tex_argument=args.tex,
            figures_out_argument=args.figures_out_dir,
            release=args.release,
            release_tag=args.release_tag,
        )
        prepare_graphics(config)

        built_pdf = build_text_artifacts(config)
    except ValueError as exc:
        print(f"error: {exc}")
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1

    print(f"Wrote {built_pdf}")
    if config.release or config.release_tag:
        release_pdf = publish_release_pdf(
            built_pdf=built_pdf,
            release_dir=config.release_dir,
            release_tag=config.release_tag,
        )
        print(f"Published release PDF to {release_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
