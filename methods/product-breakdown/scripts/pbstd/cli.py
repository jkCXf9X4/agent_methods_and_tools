"""Command-line entry points for pbstd.

The wrappers under a consuming repo's ``tools/`` call these with ``default_root``
set; installed console scripts (``pb-check``, ``pb-registers``, ...) call them
with none and rely on root discovery.
"""
from __future__ import annotations

import argparse

from .checks import check_decisions, check_ids, check_leaves, check_node_size
from .config import load_config, resolve_root
from .ids import backfill_leaves, scaffold_leaf
from .registers import generate


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        help="breakdown root (default: discovered from pb.toml, then decisions/)",
    )
    parser.add_argument("--config", help="explicit pb.toml path")


def decisions_main(default_root=None, argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pb-check", description="Validate decision records and live leaves."
    )
    _common(parser)
    parser.add_argument("--strict", action="store_true", help="exit non-zero on a hard violation")
    parser.add_argument("--glob", default="*.md", help="filename glob to scope the check")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="backfill missing leaf id/type/date/status front-matter, then re-check",
    )
    args = parser.parse_args(argv)
    cfg = load_config(resolve_root(args.root, default_root), args.config)

    def run() -> int:
        rc = check_decisions(cfg, args.strict, args.glob)
        rc |= check_leaves(cfg, args.strict)
        rc |= check_ids(cfg, args.strict)
        return rc

    rc = run()
    if args.fix:
        changed = backfill_leaves(cfg)
        for line in changed:
            print(line)
        if changed:
            print(f"backfilled {len(changed)} leaves; re-checking")
            rc = run()
    return rc


def node_size_main(default_root=None, argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pb-node-size",
        description="Check the three-tier node size budget (AD-009): goal / warning / strict.",
    )
    _common(parser)
    parser.add_argument(
        "--strict", action="store_true", help="exit non-zero when a node exceeds its strict tier"
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


def new_main(default_root=None, argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pb-new",
        description="Scaffold a new leaf with the full front-matter block: a stable, "
        "unique id (next free for the type's prefix), type, title, summary, date, status.",
    )
    _common(parser)
    parser.add_argument("directory", help="breakdown-relative target directory, e.g. '02-architecture' or '.'")
    parser.add_argument("title", help="leaf title; also the H1 and the generated index label")
    parser.add_argument("--summary", default="", help="one-line description for the generated index row (required)")
    parser.add_argument("--type", default="info", help="content type driving the id prefix")
    parser.add_argument("--status", default=None, help="leaf status (default: [ids].default_status)")
    parser.add_argument("--dry-run", action="store_true", help="print the id and path without writing")
    args = parser.parse_args(argv)
    cfg = load_config(resolve_root(args.root, default_root), args.config)
    prefixes = cfg.get("ids", "prefixes", default={})
    types = [t for t in sorted(prefixes) if t != "decision"]
    if args.type not in types:
        print(f"error: unknown leaf type '{args.type}' (expected one of {', '.join(types)})")
        return 1
    try:
        rel, ident, text = scaffold_leaf(
            cfg,
            args.directory,
            args.title,
            summary=args.summary,
            type_=args.type,
            status=args.status,
        )
    except (ValueError, FileExistsError) as exc:
        print(f"error: {exc}")
        return 1
    if args.dry_run:
        print(f"would create {rel} with id {ident}")
        return 0
    (cfg.root / rel).write_text(text, encoding="utf-8")
    print(f"created {rel} (id {ident})")
    return 0


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
