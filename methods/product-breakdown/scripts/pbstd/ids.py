"""Stable node IDs and front-matter scaffolding.

Every live node (leaf or record) carries a unique front-matter
``id: <PREFIX>-<NNN>`` where the prefix encodes the *content type* (INFO, DEC,
EVAL), never the location — so moving or renaming a file does not change its
identity. ``pb new`` scaffolds new leaves with the full front-matter block;
``pb check --fix`` backfills ``id``/``type``/``date``/``status`` onto existing
leaves that predate the ID scheme.
"""
from __future__ import annotations

import re
from datetime import date as date_cls
from pathlib import Path

from .config import Config
from .records import is_exempt, is_generated, parse_front_matter

ID_RE = re.compile(r"^([A-Z][A-Z0-9]*)-(\d+)$")


def registered_prefixes(cfg: Config) -> set[str]:
    """Every ID prefix the checker recognises.

    The content-type prefixes from ``[ids] prefixes`` plus the grandfathered
    per-layer record prefixes (ID-, PD-, AD-, ...) and IMP- for evolution
    candidates. A token matching any of these is treated as a citation and
    must resolve to an existing node id.
    """
    prefixes = set(cfg.get("ids", "prefixes", default={}).values())
    for prefix in cfg.get("layers", "prefixes", default={}).values():
        prefixes.add(prefix)
    prefixes.add("IMP")  # evolution candidates
    return {p for p in prefixes if p}


def prefix_for(cfg: Config, type_: str) -> str | None:
    """The ID prefix configured for *type_* (e.g. ``info`` -> ``INFO``)."""
    return cfg.get("ids", "prefixes", default={}).get(type_)


def next_id(cfg: Config, type_: str) -> str:
    """Next free id for *type_*: max existing suffix + 1, zero-padded.

    Scans every markdown file under the root for ids whose prefix matches the
    type; the template placeholder (``<PREFIX>-<NNN>``) never matches the
    strict ``ID_RE``, so it is ignored.
    """
    prefix = prefix_for(cfg, type_)
    if not prefix:
        raise ValueError(f"no id prefix configured for type '{type_}'")
    width = cfg.get("ids", "width", default=3)
    key = cfg.get("ids", "key", default="id")
    max_n = 0
    for path in cfg.root.rglob("*.md"):
        data = parse_front_matter(path.read_text(encoding="utf-8"))[0]
        if not data:
            continue
        match = ID_RE.match(str(data.get(key, "")).strip())
        if match and match.group(1) == prefix:
            max_n = max(max_n, int(match.group(2)))
    return f"{prefix}-{max_n + 1:0{width}d}"


def slugify(title: str) -> str:
    """Kebab-case filename stem from a title (role name, not the id)."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "untitled"


def scaffold_leaf(
    cfg: Config,
    directory: str,
    title: str,
    summary: str = "",
    type_: str = "info",
    status: str | None = None,
    today: str | None = None,
) -> tuple[Path, str, str]:
    """Build a new leaf under *directory* with the full front-matter block.

    Returns ``(relative_path, id, text)`` without writing anything, so callers
    can dry-run. Refuses to overwrite an existing file.
    """
    prefixes = cfg.get("ids", "prefixes", default={})
    if type_ not in prefixes:
        raise ValueError(f"unknown leaf type '{type_}' (expected one of {', '.join(sorted(prefixes))})")
    valid = cfg.get("ids", "leaf_statuses", default=["current", "draft", "superseded"])
    status = status or cfg.get("ids", "default_status", default="current")
    if status not in valid:
        raise ValueError(f"invalid leaf status '{status}' (expected one of {', '.join(valid)})")
    if not summary.strip():
        raise ValueError("a one-line --summary is required (the generated index reads it)")

    target = (cfg.root / directory).resolve() if directory not in ("", ".") else cfg.root.resolve()
    if not target.is_dir():
        raise ValueError(f"directory does not exist: {directory}")
    path = target / (slugify(title) + ".md")
    if path.exists():
        raise FileExistsError(f"file already exists: {path.relative_to(cfg.root)}")

    ident = next_id(cfg, type_)
    today = today or date_cls.today().isoformat()
    text = (
        "---\n"
        f"id: {ident}\n"
        f"type: {type_}\n"
        f"title: {title}\n"
        f"summary: {summary}\n"
        f"date: {today}\n"
        f"status: {status}\n"
        "---\n"
        f"\n# {title}\n\n"
        "<One current-state fact per line, present tense.>\n\n"
        "## Owns\n"
        "- <one concern this leaf is the canonical home for>\n\n"
        "## Excludes\n"
        "- <concerns owned elsewhere, cited by ID>\n"
    )
    return path.relative_to(cfg.root), ident, text


def backfill_leaves(cfg: Config) -> list[str]:
    """Add missing ``id``/``type``/``date``/``status`` to live leaves.

    Only leaves that already carry ``title`` + ``summary`` front-matter are
    touched (a nod without a title cannot be identified); the identity keys
    are inserted in canonical order. Duplicate ids are never renumbered — that
    would break existing citations — so a duplicate is left for manual
    resolution and reported by ``check_ids``. Returns one report line per
    changed file.
    """
    key = cfg.get("ids", "key", default="id")
    type_key = cfg.get("ids", "type_key", default="type")
    date_key = cfg.get("ids", "date_key", default="date")
    status_key = cfg.get("ids", "status_key", default="status")
    today = date_cls.today().isoformat()
    default_status = cfg.get("ids", "default_status", default="current")
    index_names = set(cfg.get("layout", "index_names"))
    exclude_dirs = set(cfg.get("layout", "exclude_dirs"))
    marker = cfg.get("layout", "generated_marker")
    exempt = set(cfg.get("nodes", "exempt"))
    order = [key, type_key, "title", "summary", date_key, status_key]

    changed: list[str] = []
    for path in sorted(cfg.root.rglob("*.md")):
        rel = path.relative_to(cfg.root)
        if rel.parts[0] in exclude_dirs or "deprecated" in rel.parts:
            continue
        if rel.name in index_names or rel.name.startswith("."):
            continue
        if cfg.decisions.exists() and path.is_relative_to(cfg.decisions):
            continue
        if is_exempt(rel, exempt) or is_generated(path, marker):
            continue
        data, _body = parse_front_matter(path.read_text(encoding="utf-8"))
        if not data:
            continue
        if not str(data.get("title", "")).strip() or not str(data.get("summary", "")).strip():
            continue
        fills: dict[str, str] = {}
        if not str(data.get(key, "")).strip():
            type_ = str(data.get(type_key, "")).strip() or "info"
            fills[key] = next_id(cfg, type_)
        if not str(data.get(type_key, "")).strip():
            fills[type_key] = "info"
        if not str(data.get(date_key, "")).strip():
            fills[date_key] = today
        if not str(data.get(status_key, "")).strip():
            fills[status_key] = default_status
        if not fills:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = _insert_keys(text, fills, order)
        path.write_text(new_text, encoding="utf-8")
        labels = ", ".join(f"{k} {v}" for k, v in fills.items())
        changed.append(f"backfilled {rel}: {labels}")
    return changed


def _insert_keys(text: str, fills: dict[str, str], order: list[str]) -> str:
    """Insert missing front-matter keys into *fills* at their canonical position.

    Existing keys and their order are preserved; unknown keys (e.g. ``pb_exempt``)
    keep their position; list items attached to a key stay attached.
    """
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return text
    entries: list[list[str | None]] = []
    for raw in lines[1:end]:
        match = re.match(r"^([A-Za-z_]+):", raw)
        entries.append([match.group(1), raw] if match else [None, raw])
    present = {entry[0] for entry in entries if entry[0]}
    rank = {name: pos for pos, name in enumerate(order)}
    for k in order:
        if k in present or k not in fills:
            continue
        pos = len(entries)
        for index, entry in enumerate(entries):
            if entry[0] in rank and rank[entry[0]] > rank[k]:
                pos = index
                break
        entries.insert(pos, [k, f"{k}: {fills[k]}"])
    block = "\n".join(str(entry[1]) for entry in entries)
    return "\n".join([lines[0], block, *lines[end:]])