#!/usr/bin/env python3
"""Install a method's skill bundle into an opencode skills directory.

    python3 install.py --method product-breakdown
    python3 install.py --method product-breakdown --into .opencode/skills

Global skills (the default) load in every repository; ``--into .opencode/skills``
installs into the current project only.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_INTO = Path.home() / ".config" / "opencode" / "skills"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", required=True, help="method name under methods/")
    parser.add_argument(
        "--into", default=str(DEFAULT_INTO), help="skills directory to install into"
    )
    args = parser.parse_args()

    source = ROOT / "methods" / args.method
    if not (source / "SKILL.md").is_file():
        print(f"no skill bundle at {source}")
        return 1

    dest = Path(args.into).expanduser().resolve() / args.method
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    print(f"installed {args.method} -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
