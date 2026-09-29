"""Config-driven checks: decision records and node size (AD-009)."""
from __future__ import annotations

import re
from pathlib import Path

from .config import Config
from .records import (
    as_list,
    headings,
    parse_front_matter,
    read_first_line,
    section_body,
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def check_decisions(cfg: Config, strict: bool, glob: str = "*.md") -> int:
    skip = set(cfg.get("layout", "record_skip"))
    sections = cfg.get("records", "sections")
    legacy = cfg.get("records", "legacy_sections")
    statuses = set(cfg.get("records", "statuses"))
    layers = set(cfg.get("layers", "order"))
    required = cfg.get("records", "required_keys")
    budgets = {name: tuple(bounds) for name, bounds in cfg.get("records", "budgets").items()}
    repo_root = cfg.repo_root

    violations: list[str] = []
    warnings: list[str] = []
    records: dict[str, dict] = {}

    decisions = cfg.decisions
    paths = [p for p in sorted(decisions.glob(glob)) if p.name not in skip] if decisions.exists() else []
    if not paths:
        print("No decision records found.")
        return 0

    for path in paths:
        rel = path.relative_to(cfg.root)
        data, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if data is None:
            violations.append(f"{rel}: missing YAML front-matter")
            continue

        for key in required:
            if key not in data:
                violations.append(f"{rel}: missing front-matter key '{key}'")

        rid = str(data.get("id", ""))
        if rid and not path.name.startswith(f"{rid}-"):
            violations.append(f"{rel}: filename does not start with id '{rid}-'")
        if rid in records:
            violations.append(f"{rel}: duplicate id '{rid}'")
        records[rid] = data

        if data.get("status") not in statuses:
            violations.append(f"{rel}: invalid status '{data.get('status')}'")
        if not DATE_RE.match(str(data.get("date", ""))):
            violations.append(f"{rel}: date must be YYYY-MM-DD")

        record_layers = as_list(data.get("layers"))
        if not record_layers:
            violations.append(f"{rel}: no layers")
        for layer in record_layers:
            if layer not in layers:
                violations.append(f"{rel}: invalid layer '{layer}'")

        state = str(data.get("state", ""))
        if state and not (cfg.root / state).exists():
            violations.append(f"{rel}: state path does not exist: {state}")

        for artifact in as_list(data.get("artifacts")):
            if not (repo_root / artifact).exists():
                warnings.append(f"{rel}: artifact path not found: {artifact}")

        found = headings(body)
        for name in legacy:
            if name in found:
                violations.append(
                    f"{rel}: legacy heading '## {name}' "
                    f"(state belongs in {state or 'the layer leaf'})"
                )
        missing = [s for s in sections if s not in found]
        extra = [h for h in found if h not in sections]
        if missing:
            violations.append(f"{rel}: missing sections {missing}")
        if extra:
            violations.append(f"{rel}: non-template sections {extra}")
        if [h for h in found if h in sections] != [s for s in sections if s in found]:
            violations.append(f"{rel}: sections out of template order")

        for name, (target, cap) in budgets.items():
            lines = section_body(body, name)
            if not lines:
                violations.append(f"{rel}: {name} is empty")
            elif len(lines) > cap:
                violations.append(f"{rel}: {name} is {len(lines)} lines (cap {cap})")
            elif len(lines) > target:
                warnings.append(
                    f"{rel}: {name} is {len(lines)} lines (over target {target}, under cap)"
                )

    for rid, data in records.items():
        for other in as_list(data.get("superseded_by")):
            if other not in records:
                warnings.append(f"{rid}: superseded_by references missing record '{other}'")
            elif rid not in as_list(records[other].get("supersedes")):
                violations.append(f"{rid}: {other}.supersedes does not list {rid}")

    for line in violations:
        print(f"HARD  {line}")
    for line in warnings:
        print(f"warn  {line}")
    if not violations and not warnings:
        print("All decision records valid.")
    return 1 if strict and violations else 0


def is_generated(path: Path, marker: str) -> bool:
    return bool(marker) and marker in read_first_line(path)


# Front-matter key a node can use to exempt itself from the node budget.
EXEMPT_KEY = "pb_exempt"
_FALSY = {"false", "no", "off", "0", "none", "null", "[]"}


def is_exempt(rel: Path, exempt: set[str]) -> bool:
    """Node-budget exemption test against the relative path from the root.

    An ``exempt`` entry matches when it is:

    * a bare filename — ``rel.name`` (previous behaviour); or
    * a bare folder name — any path component of *rel*, exempting that folder
      and its whole subtree wherever it appears under the root; or
    * a forward-slash relative path — a leading directory prefix of *rel*,
      pinning one specific nested folder.
    """
    posix = rel.parent.as_posix()
    for entry in exempt:
        entry = entry.rstrip("/")
        if not entry:
            continue
        if "/" in entry:
            if posix == entry or posix.startswith(entry + "/"):
                return True
        elif entry in rel.parts:
            return True
    return False


def is_frontmatter_exempt(text: str) -> bool:
    """True when the node exempts itself via ``pb_exempt`` in its front matter.

    The exemption is opt-in per file: a truthy ``pb_exempt`` value (anything
    but ``false``/``no``/``off``/``0``/``none``/``null``) skips the node budget
    entirely, complementing the path-based ``[nodes] exempt`` config list.
    """
    data, _ = parse_front_matter(text)
    if not data:
        return False
    value = data.get(EXEMPT_KEY)
    if value is None or value == []:
        return False
    return str(value).strip().lower() not in _FALSY


def check_node_size(cfg: Config, strict: bool) -> int:
    index_names = set(cfg.get("layout", "index_names"))
    exclude_dirs = set(cfg.get("layout", "exclude_dirs"))
    marker = cfg.get("layout", "generated_marker")
    exempt = set(cfg.get("nodes", "exempt"))
    index_goal = cfg.get("nodes", "index_goal")
    index_warning = cfg.get("nodes", "index_warning")
    index_strict = cfg.get("nodes", "index_strict")
    leaf_goal = cfg.get("nodes", "leaf_goal")
    leaf_warning = cfg.get("nodes", "leaf_warning")
    leaf_strict = cfg.get("nodes", "leaf_strict")
    leaf_min = cfg.get("nodes", "leaf_min")

    violations: list[tuple[Path, int, str]] = []
    warnings: list[tuple[Path, int, str]] = []
    notices: list[tuple[Path, int, str]] = []
    shorts: list[tuple[Path, int]] = []

    for path in sorted(cfg.root.rglob("*.md")):
        rel = path.relative_to(cfg.root)
        if rel.parts and rel.parts[0] in exclude_dirs:
            continue
        if is_exempt(rel, exempt) or is_generated(path, marker):
            continue
        text = path.read_text(encoding="utf-8")
        if is_frontmatter_exempt(text):
            continue
        lines = len(text.splitlines())
        if rel.name in index_names:
            if lines > index_strict:
                violations.append((rel, lines, f"exceeds index strict {index_strict}"))
            elif lines > index_warning:
                warnings.append(
                    (rel, lines, f"over index warning {index_warning}, under strict {index_strict}")
                )
            elif lines > index_goal:
                notices.append(
                    (rel, lines, f"over index goal {index_goal}, under warning {index_warning}")
                )
        else:
            if lines > leaf_strict:
                violations.append((rel, lines, f"exceeds leaf strict {leaf_strict}"))
            elif lines > leaf_warning:
                warnings.append(
                    (rel, lines, f"over leaf warning {leaf_warning}, under strict {leaf_strict}")
                )
            elif lines > leaf_goal:
                notices.append(
                    (rel, lines, f"over leaf goal {leaf_goal}, under warning {leaf_warning}")
                )
            if lines < leaf_min:
                shorts.append((rel, lines))

    for rel, lines, rule in violations:
        print(f"HARD  {lines:>4}  {rel}  ({rule})")
    for rel, lines, rule in warnings:
        print(f"warn  {lines:>4}  {rel}  ({rule})")
    for rel, lines, rule in notices:
        print(f"info  {lines:>4}  {rel}  ({rule})")
    for rel, lines in shorts:
        print(f"short {lines:>3}  {rel}  (below min {leaf_min})")

    if not violations and not warnings and not notices and not shorts:
        print("All nodes within budget.")
    return 1 if strict and violations else 0
