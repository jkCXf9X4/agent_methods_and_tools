"""Command-line entry points for pbstd.

The wrappers under a consuming repo's ``tools/`` call these with ``default_root``
set; installed console scripts (``pb-check``, ``pb-registers``, ...) call them
with none and rely on root discovery.
"""
from __future__ import annotations

import argparse

from .checks import check_decisions, check_node_size
from .config import load_config, resolve_root
from .registers import generate


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        help="breakdown root (default: discovered from pb.toml, then decisions/)",
    )
    parser.add_argument("--config", help="explicit pb.toml path")


def decisions_main(default_root=None, argv=None) -> int:
    parser = argparse.ArgumentParser(prog="pb-check", description="Validate decision records.")
    _common(parser)
    parser.add_argument("--strict", action="store_true", help="exit non-zero on a hard violation")
    parser.add_argument("--glob", default="*.md", help="filename glob to scope the check")
    args = parser.parse_args(argv)
    cfg = load_config(resolve_root(args.root, default_root), args.config)
    return check_decisions(cfg, args.strict, args.glob)


def node_size_main(default_root=None, argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pb-node-size", description="Check the node size budget (AD-009)."
    )
    _common(parser)
    parser.add_argument(
        "--strict", action="store_true", help="exit non-zero when a node exceeds its hard cap"
    )
    args = parser.parse_args(argv)
    cfg = load_config(resolve_root(args.root, default_root), args.config)
    return check_node_size(cfg, args.strict)


def registers_main(default_root=None, argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pb-registers", description="Generate the decision registers."
    )
    _common(parser)
    parser.add_argument("--out-dir", help="output root (default: the breakdown root)")
    parser.add_argument(
        "--sync-footers", action="store_true", help="rewrite each state leaf's '## Decisions' footer"
    )
    args = parser.parse_args(argv)
    cfg = load_config(resolve_root(args.root, default_root), args.config)
    return generate(cfg, args.out_dir, args.sync_footers)


def doctor_main(default_root=None, argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pb-doctor", description="Report the resolved pbstd configuration."
    )
    _common(parser)
    args = parser.parse_args(argv)
    cfg = load_config(resolve_root(args.root, default_root), args.config)
    print(f"root:      {cfg.root}")
    print(f"config:    {cfg.path or '(built-in defaults)'}")
    print(f"repo root: {cfg.repo_root}")
    print(f"decisions: {cfg.decisions}")
    print(f"layers:    {', '.join(cfg.get('layers', 'order'))}")
    print(
        "registers: "
        + ", ".join(
            cfg.get("registers", key) for key in ("index", "log", "traceability")
        )
    )
    return 0
