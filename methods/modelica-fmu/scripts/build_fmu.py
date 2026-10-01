#!/usr/bin/env python3
"""Compatibility wrapper for the generic FMU build CLI."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from fmu_build.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
