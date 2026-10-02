"""Config-driven checks: decision records and node size (AD-009)."""
from __future__ import annotations

import re
from pathlib import Path

from .config import Config
from .ids import ID_RE, prefix_for, registered_prefixes
from .records import (
    as_list,
    headings,
    is_exempt,
    is_generated,
    parse_front_matter,
    section_body,
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE_RE = re.compile(r"```.*?```", re.S)


def without_fences(text: str) -> str:
    """Body text with fenced code blocks removed.

    Link and citation rules apply to authorial prose, not to code examples
    that legitimately show markdown syntax (``[x](y.md)`` as sample input).
    """
    return FENCE_RE.sub("", text)


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
        successors = as_list(data.get("superseded_by"))
        # Stale nodes must point forward: a superseded/deprecated record with
        # no successor reads as live to a browsing agent (the exact failure
        # mode info-hygiene exists to prevent).
        if str(data.get("status", "")) in ("superseded", "deprecated") and not successors:
            violations.append(
                f"{rid}: status '{data.get('status')}' requires a forward pointer in superseded_by"
            )
        for other in successors:
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


# Front-matter key a node can use to exempt itself from the node budget.
EXEMPT_KEY = "pb_exempt"
_FALSY = {"false", "no", "off", "0", "none", "null", "[]"}


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


def effective_lines(text: str, start: str, end: str) -> int:
    """Line count excluding the generated region between *start* and *end*.

    Used for indexes whose Contents list is generated: the hand-written part is
    what the budget governs; the generated table floats freely above it.
    """
    si, ei = text.find(start), text.find(end)
    if si == -1 or ei == -1 or ei < si:
        return len(text.splitlines())
    return len(text[:si].splitlines()) + len(text[ei + len(end):].splitlines())


def check_node_size(cfg: Config, strict: bool) -> int:
    index_names = set(cfg.get("layout", "index_names"))
    exclude_dirs = set(cfg.get("layout", "exclude_dirs"))
    marker = cfg.get("layout", "generated_marker")
    exempt = set(cfg.get("nodes", "exempt"))
    idx_start = cfg.get("indexes", "start_marker", default="<!-- pb:index:start -->")
    idx_end = cfg.get("indexes", "end_marker", default="<!-- pb:index:end -->")
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
        if _in_deprecated(rel):
            continue  # tombstones are quarantined, not live nodes
        if cfg.decisions.exists() and path.is_relative_to(cfg.decisions):
            continue  # records are governed by check_decisions' section budgets
        if is_exempt(rel, exempt) or is_generated(path, marker):
            continue
        text = path.read_text(encoding="utf-8")
        if is_frontmatter_exempt(text):
            continue
        if rel.name in index_names:
            # Generated Contents lists are navigation output, not authorial
            # content: count only the lines outside the marker region so a
            # growing table cannot push a hand-written index over its budget.
            lines = effective_lines(text, idx_start, idx_end)
        else:
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


def _in_deprecated(rel: Path) -> bool:
    return "deprecated" in rel.parts


def check_leaves(cfg: Config, strict: bool) -> int:
    """Enforce the ID-citation rule on live leaves.

    Live leaves (non-index, non-generated, non-exempt, outside ``decisions/``
    and ``deprecated/``) must carry ``title`` + ``summary`` front-matter (the
    generated indexes read it) and must not link to other nodes by path —
    nodes are cited by ID, and the registers resolve IDs to locations. Indexes
    are exempt: their Contents lists are generated, and their hand-written
    sections keep the level of linking they already have.
    """
    index_names = set(cfg.get("layout", "index_names"))
    exclude_dirs = set(cfg.get("layout", "exclude_dirs"))
    marker = cfg.get("layout", "generated_marker")
    exempt = set(cfg.get("nodes", "exempt"))
    require_fm = cfg.get("indexes", "require_leaf_frontmatter", default=True)
    enforce_links = cfg.get("indexes", "enforce_id_citations", default=True)
    title_key = cfg.get("indexes", "title_key", default="title")
    summary_key = cfg.get("indexes", "summary_key", default="summary")

    violations: list[str] = []
    for path in sorted(cfg.root.rglob("*.md")):
        rel = path.relative_to(cfg.root)
        if rel.parts[0] in exclude_dirs or _in_deprecated(rel):
            continue
        if rel.name in index_names or rel.name.startswith("."):
            continue
        if cfg.decisions.exists() and path.is_relative_to(cfg.decisions):
            continue
        if is_exempt(rel, exempt) or is_generated(path, marker):
            continue
        text = path.read_text(encoding="utf-8")
        if is_frontmatter_exempt(text):
            continue
        data, body = parse_front_matter(text)
        if require_fm:
            if data is None:
                violations.append(
                    f"{rel}: missing front-matter ('{title_key}' + '{summary_key}' "
                    "required for the generated index)"
                )
            else:
                for key in (title_key, summary_key):
                    if not str(data.get(key, "")).strip():
                        violations.append(f"{rel}: missing front-matter key '{key}'")
        if enforce_links:
            for link in re.finditer(r"\]\(([^)]+)\)", without_fences(body)):
                target = link.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if target.endswith(".md"):
                    violations.append(
                        f"{rel}: path link to '{target}' — cite by ID instead"
                    )

    for line in violations:
        print(f"HARD  {line}")
    if not violations:
        print("All leaves valid: front-matter present, no path links.")
    return 1 if strict and violations else 0


# --- Rejection routing: "should not do X" is a decision, not state ---
#
# A live leaf holds current state. A list of what should not be done — a
# decided rejection, an undeveloped suggestion, a "not-to-do" appendix — is
# not state: the *choice* belongs in a decision record (a rejection is a
# committed choice and `[records].statuses` admits `rejected`), and the prose
# is archived under `deprecated/` or deleted. The signals below are the
# unambiguous *artifact* markers — a filename that names the artifact class
# (not-to-do.md, suggestions.md, ...), a whole-section denied heading, a
# rejection-like leaf status — deliberately not prose tone and not title text,
# so a boundary phrased as present-tense state ("X is out of scope", "records
# are write-once, never modified") and a tracker holding raw ideas with
# disposition markers (the `99_open-items.md` pattern) always pass.
REJECTION_NAME_TOKENS = (
    "suggestion",
    "undeveloped",
    "not-to-do",
    "should-not",
    "do-not",
    "dont",  # also matches "don't" in filenames/slugs
    "wontfix",
    "forbidden",
    "rejected",
    "abandoned",
)
# Whole H2 sections that announce not-to-be-done direction. Heading text is
# lowercased before matching.
REJECTION_HEADINGS = (
    "should not",
    "don't",
    "do not",
    "what not to do",
    "not to be done",
    "forbidden",
    "rejected",
    "never",
)
# Leaf statuses that mean "this choice was rejected" — history, not a live
# leaf lifecycle. They are already invalid leaf statuses; check_ids adds the
# routing hint so the message says where the material goes.
REJECTION_STATUSES = ("rejected", "abandoned", "withdrawn", "parked")
_REJECTION_ROUTE = (
    "this is not state: record the choice as a decision record, then move "
    "this file under deprecated/ (or delete it if fully dead)"
)


def check_rejections(cfg: Config, strict: bool) -> int:
    """A live leaf must be current state, never a "should not do X" artifact.

    "Don't do X" sections, suggestion/not-to-do files, and undeveloped-idea
    artifacts are the stale direction a browsing agent reads as current truth.
    They are misclassified rejections: the choice belongs in ``decisions/`` and
    the prose in ``deprecated/``. Scanned signals are structural only — the
    filename (a leaf that names the artifact class), whole-section headings,
    and rejection-like statuses — so present-tense boundaries ("X is out of
    scope", "records are write-once, never modified") and trackers of raw
    ideas (``99_open-items.md`` pattern) always pass. One finding per node; a
    matching filename wins over a matching heading.
    """
    index_names = set(cfg.get("layout", "index_names"))
    exclude_dirs = set(cfg.get("layout", "exclude_dirs"))
    marker = cfg.get("layout", "generated_marker")
    exempt = set(cfg.get("nodes", "exempt"))

    violations: list[str] = []
    for path in sorted(cfg.root.rglob("*.md")):
        rel = path.relative_to(cfg.root)
        if rel.parts[0] in exclude_dirs or _in_deprecated(rel):
            continue
        if rel.name in index_names or rel.name.startswith("."):
            continue
        if cfg.decisions.exists() and path.is_relative_to(cfg.decisions):
            continue
        if is_exempt(rel, exempt) or is_generated(path, marker):
            continue
        text = path.read_text(encoding="utf-8")
        if is_frontmatter_exempt(text):
            continue
        _data, body = parse_front_matter(text)

        name = rel.name.lower()
        headings_l = [h.lower() for h in headings(without_fences(body))]
        if any(tok in name for tok in REJECTION_NAME_TOKENS):
            violations.append(f"{rel}: name looks like a rejection/suggestion artifact — {_REJECTION_ROUTE}")
        else:
            denied = next((h for h in headings_l if h in REJECTION_HEADINGS), None)
            if denied:
                violations.append(
                    f"{rel}: 'not-to-be-done' section '## {denied}' — {_REJECTION_ROUTE}"
                )

    for line in violations:
        print(f"HARD  {line}")
    if not violations:
        print("All leaves valid: no rejection/not-to-be-done artifacts masquerading as state.")
    return 1 if strict and violations else 0


def check_ids(cfg: Config, strict: bool) -> int:
    """Enforce the stable-ID scheme on every node.

    * Every ``id`` across leaves AND records must be globally unique.
    * A leaf id is ``<PREFIX>-<NNN>``; when the leaf declares ``type:`` the
      prefix must be the one configured for that type.
    * Live leaves must carry the identity keys ``id``/``type``/``date``/
      ``status`` (config ``[ids].require``) and a valid leaf ``status``.
    * Every registered-prefix ID token in body text (``INFO-007``, ``AD-012``,
      ...) must resolve to an existing node id, so a citation survives a move
      or flags the moment a node it points at disappears.
    """
    id_key = cfg.get("ids", "key", default="id")
    type_key = cfg.get("ids", "type_key", default="type")
    date_key = cfg.get("ids", "date_key", default="date")
    status_key = cfg.get("ids", "status_key", default="status")
    require = cfg.get("ids", "require", default=True)
    enforce_citations = cfg.get("ids", "enforce_citations", default=True)
    leaf_statuses = set(cfg.get("ids", "leaf_statuses", default=["current", "draft", "superseded"]))
    type_prefixes = set(cfg.get("ids", "prefixes", default={}))
    # Longest-first so `ID` never shadows `IMD`/`INFO`-style prefixes. Tokens
    # need a zero-padded number (`\d{2,}`), so generic prose like "ID-1" or
    # "HTTP-2" is never mistaken for a citation.
    cite_re = re.compile(
        r"(?<![A-Z0-9])(%s)-\d{2,}(?!\w)"
        % "|".join(sorted(registered_prefixes(cfg), key=len, reverse=True))
    )
    index_names = set(cfg.get("layout", "index_names"))
    exclude_dirs = set(cfg.get("layout", "exclude_dirs"))
    marker = cfg.get("layout", "generated_marker")
    exempt = set(cfg.get("nodes", "exempt"))
    record_skip = set(cfg.get("layout", "record_skip"))

    violations: list[str] = []
    known: dict[str, Path] = {}
    candidates: list[tuple[Path, str]] = []  # (rel, body) for citation resolution
    superseded_leaves: list[tuple[Path, str]] = []  # (rel, body+summary) needing a forward pointer
    for path in sorted(cfg.root.rglob("*.md")):
        rel = path.relative_to(cfg.root)
        if rel.parts[0] in exclude_dirs or _in_deprecated(rel):
            continue
        if cfg.decisions.exists() and path.is_relative_to(cfg.decisions) and rel.name in record_skip:
            continue  # templates/README inside decisions/ carry no real id
        if rel.name.startswith(".") or is_generated(path, marker):
            continue
        data, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if data is None:
            continue
        ident = str(data.get(id_key, "")).strip()
        if ident:
            # The id registry is global: ids under exempt subtrees (e.g. a
            # grandfathered per-layer decisions/ folder at a different path)
            # still register, so existing citations of them keep resolving.
            # Exempt affects the leaf-shape rules below, never the registry.
            if ident in known:
                violations.append(f"duplicate id '{ident}': {known[ident]} and {rel}")
            else:
                known[ident] = rel
            if not ID_RE.match(ident):
                violations.append(f"{rel}: id '{ident}' is not <PREFIX>-<NNN>")
        if is_exempt(rel, exempt):
            continue
        if rel.name in index_names:
            continue
        if cfg.decisions.exists() and path.is_relative_to(cfg.decisions):
            candidates.append((rel, body))
            continue
        type_ = str(data.get(type_key, "")).strip()
        if ident and type_:
            want = prefix_for(cfg, type_)
            if want and not ident.startswith(want + "-"):
                violations.append(
                    f"{rel}: id '{ident}' does not match type '{type_}' prefix '{want}-'"
                )
        if require:
            for k in (id_key, type_key, date_key, status_key):
                if not str(data.get(k, "")).strip():
                    violations.append(f"{rel}: missing front-matter key '{k}' (leaf identity)")
            if type_ and type_ not in type_prefixes:
                violations.append(
                    f"{rel}: unknown leaf type '{type_}' (expected one of {', '.join(sorted(type_prefixes))})"
                )
            status_val = str(data.get(status_key, "")).strip()
            if status_val and status_val not in leaf_statuses:
                if status_val.lower() in REJECTION_STATUSES:
                    violations.append(
                        f"{rel}: invalid leaf status '{status_val}' — a rejection is a "
                        f"decision record: record the choice in decisions/, then move "
                        f"this file under deprecated/ (or delete it)"
                    )
                else:
                    violations.append(f"{rel}: invalid leaf status '{status_val}'")
            if status_val == "superseded":
                # A leaf kept in place as superseded must still point at its
                # replacement, or a browsing agent reads the tombstone as live.
                search_text = body + "\n" + str(data.get("summary", ""))
                superseded_leaves.append((rel, search_text))
        candidates.append((rel, body))

    for reserved in cfg.get("ids", "reserved_ids", default=[]):
        rid = str(reserved).strip()
        if not rid:
            continue
        if not ID_RE.match(rid):
            violations.append(f"reserved id '{rid}' is not <PREFIX>-<NNN>")
        elif rid in known:
            violations.append(f"reserved id '{rid}' duplicates {known[rid]}")
        else:
            known[rid] = Path("<reserved>")

    if enforce_citations:
        for rel, body in candidates:
            for match in cite_re.finditer(without_fences(body)):
                token = match.group(0)
                if token not in known:
                    violations.append(f"{rel}: citation '{token}' does not resolve to a known id")
        for rel, text in superseded_leaves:
            tokens = {m.group(0) for m in cite_re.finditer(without_fences(text))}
            if not any(t in known for t in tokens):
                violations.append(
                    f"{rel}: superseded leaf must name its replacement by ID "
                    f"(a resolvable citation like `INFO-140`)"
                )

    for line in violations:
        print(f"HARD  {line}")
    if not violations:
        print("All ids unique and every citation resolves.")
    return 1 if strict and violations else 0
