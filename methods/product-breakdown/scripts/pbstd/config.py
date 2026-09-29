"""Configuration for the product-breakdown standard.

Loads ``pb.toml`` from the breakdown root and deep-merges it over ``DEFAULTS``,
so a repository only has to state what differs from the standard.
"""
from __future__ import annotations

from pathlib import Path

try:  # Python >= 3.11
    import tomllib as _toml
except ModuleNotFoundError:  # Python < 3.11
    import tomli as _toml

DEFAULTS: dict = {
    "layout": {
        "index_names": ["README.md", "WORKING-GUIDELINES.md"],
        "decisions_dir": "decisions",
        "record_skip": ["TEMPLATE.md", "README.md"],
        "generated_marker": "GENERATED FILE",
        "exclude_dirs": ["tools"],
    },
    "layers": {
        "order": [
            "intent",
            "product",
            "architecture",
            "implementation",
            "verification",
            "operation",
        ],
        "prefixes": {
            "intent": "ID",
            "product": "PD",
            "architecture": "AD",
            "implementation": "IMD",
            "verification": "VD",
            "operation": "OD",
        },
    },
    "records": {
        "sections": [
            "Context",
            "Decision",
            "Rationale",
            "Alternatives Considered",
            "Consequences",
            "Verification",
            "Review Trigger",
        ],
        "legacy_sections": ["Current Choice", "Status", "Layer"],
        "statuses": ["proposed", "accepted", "superseded", "rejected", "deprecated"],
        "required_keys": [
            "id",
            "title",
            "date",
            "status",
            "layers",
            "state",
            "artifacts",
            "supersedes",
            "superseded_by",
            "related",
        ],
        "budgets": {"Context": [5, 8], "Decision": [4, 6], "Rationale": [5, 8]},
    },
    "nodes": {
        # Three size tiers per node kind: goal / warning / strict (hard).
        "index_goal": 40,
        "index_warning": 50,
        "index_strict": 75,
        "leaf_goal": 50,
        "leaf_warning": 75,
        "leaf_strict": 100,
        "leaf_min": 10,
        "exempt": ["design-choice-log.md", "traceability-map.md"],
    },
    "registers": {
        "index": "decisions/README.md",
        "log": "design-choice-log.md",
        "traceability": "traceability-map.md",
        "log_title": "Decision Log",
        "banner": "<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->",
    },
    # Stable node IDs: every live node carries `<PREFIX>-<NNN>` in front-matter
    # where the prefix encodes the CONTENT TYPE, never the
    # location — so moving or renaming a file never changes its identity.
    # Decision records keep their per-layer citation prefixes (ID-/PD-/AD-/...),
    # which are grandfathered into the uniqueness and citation checks.
    "ids": {
        # Front-matter keys of the node identity.
        "key": "id",
        "type_key": "type",
        "date_key": "date",
        "status_key": "status",
        # Zero-padded width of the sequence number (INFO-001).
        "width": 3,
        # Content type -> ID prefix. The type is what survives a move.
        "prefixes": {
            "info": "INFO",
            "decision": "DEC",
            "eval": "EVAL",
            "research-question": "RQ",
            "constraint": "CON",
            "trace": "TR",
            "capability": "CP",
            "requirement": "REQ",
            "test": "TEST",
        },
        # Leaf `status:` values; decision records use [records].statuses.
        "leaf_statuses": ["current", "draft", "superseded"],
        "default_status": "current",
        # Require id/type/date/status on live leaves (check_ids).
        "require": True,
        # Resolve every registered-prefix ID token in body text (check_ids).
        "enforce_citations": True,
        # Ids that are known but not yet filed (planned handles, e.g. an IMP
        # referenced from a roadmap before it lands). They resolve in
        # citations but have no path.
        "reserved_ids": [],
    },
    # Generated index navigation: each index's Contents list is rebuilt from
    # direct-child front-matter so moves never require editing links by hand.
    "indexes": {
        "enabled": True,
        # Heading whose list is regenerated (searched with `## ` prefix).
        "section": "Contents",
        # Markers bracketing the generated list inside that section.
        "start_marker": "<!-- pb:index:start -->",
        "end_marker": "<!-- pb:index:end -->",
        # Front-matter keys used for the row label and one-line description.
        "title_key": "title",
        "summary_key": "summary",
        # Leaf checks: live leaves must carry title/summary front-matter and
        # must cite other nodes by ID, never by a markdown path link.
        "require_leaf_frontmatter": True,
        "enforce_id_citations": True,
    },
}


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def find_root(start: Path) -> Path:
    """Locate the breakdown root near *start*: ``pb.toml``, then ``decisions/``."""
    start = Path(start).resolve()
    for parent in [start, *start.parents]:
        if (parent / "pb.toml").is_file():
            return parent
    for parent in [start, *start.parents]:
        if (parent / "decisions").is_dir():
            return parent
    if start.is_dir():
        for child in sorted(start.iterdir()):
            if not child.is_dir():
                continue
            if (child / "pb.toml").is_file() or (child / "decisions").is_dir():
                return child
    return start


def resolve_root(cli_root=None, default_root=None) -> Path:
    """Resolve the breakdown root: explicit ``--root``, then a known default."""
    if cli_root:
        return Path(cli_root).expanduser().resolve()
    if default_root is not None and Path(default_root).is_dir():
        return Path(default_root).resolve()
    return find_root(Path.cwd())


class Config:
    """Merged configuration plus the breakdown root it was resolved against."""

    def __init__(self, data: dict, root: Path, path: Path | None = None):
        self.data = data
        self.root = root
        self.path = path

    def get(self, *keys, default=None):
        node = self.data
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    @property
    def decisions(self) -> Path:
        return self.root / self.get("layout", "decisions_dir", default="decisions")

    @property
    def repo_root(self) -> Path:
        rel = self.get("layout", "repo_root", default=None)
        return (self.root / rel).resolve() if rel else self.root.parent


def load_config(root: Path, explicit=None) -> Config:
    """Load ``<root>/pb.toml`` (or *explicit*) over the built-in defaults."""
    root = Path(root).resolve()
    path = Path(explicit).expanduser().resolve() if explicit else root / "pb.toml"
    data = _toml.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    return Config(_merge(DEFAULTS, data), root, path if path.is_file() else None)
