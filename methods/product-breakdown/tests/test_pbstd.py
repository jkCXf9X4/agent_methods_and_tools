"""Tests for the pbstd package."""
from __future__ import annotations

from pathlib import Path

from pbstd.checks import (
    check_decisions,
    check_ids,
    check_leaves,
    check_node_size,
    check_rejections,
)
from pbstd.config import DEFAULTS, find_root, load_config
from pbstd.records import parse_front_matter
from pbstd.registers import generate, sync_indexes

RECORD = """---
id: AD-001
title: Example choice
date: 2026-01-02
status: accepted
layers: [architecture]
state: leaf.md
artifacts:
  - product-breakdown/leaf.md
supersedes: []
superseded_by: []
related: []
---

# AD-001: Example choice

## Context
A force existed.

## Decision
On 2026-01-02, we chose it.

## Rationale
It fit the constraint.

## Alternatives Considered
- The other one

## Consequences
- Positive: good
- Negative: cost

## Verification
None

## Review Trigger
None
"""


def make_breakdown(tmp_path: Path) -> Path:
    root = tmp_path / "product-breakdown"
    (root / "decisions").mkdir(parents=True)
    (root / "pb.toml").write_text("", encoding="utf-8")
    (root / "leaf.md").write_text("# Leaf\n\nCurrent state.\n", encoding="utf-8")
    (root / "decisions" / "AD-001-example-choice.md").write_text(RECORD, encoding="utf-8")
    return root


def test_find_root(tmp_path):
    root = make_breakdown(tmp_path)
    assert find_root(root / "decisions") == root


def test_defaults_merge(tmp_path):
    root = make_breakdown(tmp_path)
    cfg = load_config(root)
    assert cfg.get("layers", "order") == DEFAULTS["layers"]["order"]
    assert cfg.decisions == root / "decisions"
    assert cfg.repo_root == tmp_path


def test_check_decisions_clean(tmp_path, capsys):
    cfg = load_config(make_breakdown(tmp_path))
    assert check_decisions(cfg, strict=True) == 0
    assert "valid" in capsys.readouterr().out


def test_check_decisions_catches_bad_status(tmp_path):
    root = make_breakdown(tmp_path)
    path = root / "decisions" / "AD-001-example-choice.md"
    path.write_text(RECORD.replace("status: accepted", "status: bogus"), encoding="utf-8")
    assert check_decisions(load_config(root), strict=True) == 1


def test_check_decisions_superseded_requires_forward_pointer(tmp_path, capsys):
    root = make_breakdown(tmp_path)
    path = root / "decisions" / "AD-001-example-choice.md"
    path.write_text(RECORD.replace("status: accepted", "status: superseded"), encoding="utf-8")
    assert check_decisions(load_config(root), strict=True) == 1
    assert "requires a forward pointer" in capsys.readouterr().out


def test_check_decisions_superseded_with_forward_pointer(tmp_path):
    """A superseded record that names its successor (bidirectionally) passes."""
    root = make_breakdown(tmp_path)
    (root / "decisions" / "AD-002-successor.md").write_text(
        RECORD.replace("id: AD-001", "id: AD-002")
        .replace("AD-001: Example choice", "AD-002: Successor")
        .replace("supersedes: []", "supersedes: [AD-001]"),
        encoding="utf-8",
    )
    path = root / "decisions" / "AD-001-example-choice.md"
    path.write_text(
        RECORD.replace("status: accepted", "status: superseded")
        .replace("superseded_by: []", "superseded_by: [AD-002]"),
        encoding="utf-8",
    )
    assert check_decisions(load_config(root), strict=True) == 0


def test_generate_writes_registers(tmp_path):
    cfg = load_config(make_breakdown(tmp_path))
    assert generate(cfg, sync_footers_flag=True) == 0
    index = (cfg.root / "decisions" / "README.md").read_text(encoding="utf-8")
    assert "GENERATED FILE" in index and "AD-001" in index
    assert "## Decisions" in (cfg.root / "leaf.md").read_text(encoding="utf-8")


def test_generate_skips_disabled_register_targets(tmp_path):
    """An empty [registers] target disables that generated register, so a repo
    that keeps a hand-written register (legacy decisions without records yet)
    is not clobbered by a generated duplicate."""
    root = make_breakdown(tmp_path)
    (root / "pb.toml").write_text(
        '[registers]\nlog = ""\ntraceability = ""\n', encoding="utf-8"
    )
    assert generate(load_config(root)) == 0
    assert (root / "decisions" / "README.md").exists()
    assert not (root / "design-choice-log.md").exists()
    assert not (root / "traceability-map.md").exists()


def test_node_size_flags_oversize_leaf(tmp_path):
    root = make_breakdown(tmp_path)
    (root / "big.md").write_text("\n".join(f"line {i}" for i in range(120)), encoding="utf-8")
    assert check_node_size(load_config(root), strict=True) == 1


def test_node_size_skips_records(tmp_path):
    """Records are sized by their section budgets in check_decisions, not by
    the leaf budget: a long record under decisions/ must not fail node-size."""
    root = make_breakdown(tmp_path)
    (root / "decisions" / "AD-002-long-background.md").write_text(
        "---\nid: AD-002\ntitle: Long\n"
        + "date: 2026-09-22\nstatus: accepted\nlayers: [architecture]\nstate: \nartifacts: []\n"
        + "supersedes: []\nsuperseded_by: []\nrelated: []\n---\n\n"
        + "\n".join(f"line {i}" for i in range(140)),
        encoding="utf-8",
    )
    assert check_node_size(load_config(root), strict=True) == 0


def test_node_size_skips_deprecated_tombstones(tmp_path):
    """A quarantined file under deprecated/ is a tombstone, not a live node:
    its size is irrelevant (and it is hidden from browsing by the path)."""
    root = make_breakdown(tmp_path)
    tomb = root / "deprecated"
    tomb.mkdir()
    (tomb / "old-notes.md").write_text("\n".join(f"line {i}" for i in range(120)), encoding="utf-8")
    assert check_node_size(load_config(root), strict=True) == 0


def test_check_ids_superseded_leaf_requires_replacement(tmp_path, capsys):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "a.md", "A", "A", ident="INFO-020")
    make_leaf(
        root / "02-architecture" / "old.md",
        "Old",
        "Predecessor",
        ident="INFO-021",
        status="superseded",
        body="Current state.",
    )
    assert check_ids(load_config(root), strict=True) == 1
    assert "superseded leaf must name its replacement by ID" in capsys.readouterr().out


def test_check_ids_superseded_leaf_with_replacement_passes(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "a.md", "A", "A", ident="INFO-020")
    make_leaf(
        root / "02-architecture" / "old.md",
        "Old",
        "Predecessor",
        ident="INFO-021",
        status="superseded",
        body="Superseded by `INFO-020`.",
    )
    assert check_ids(load_config(root), strict=True) == 0


def test_node_size_three_tiers(tmp_path, capsys):
    root = make_breakdown(tmp_path)
    (root / "goal.md").write_text("\n".join(f"g{i}" for i in range(60)), encoding="utf-8")
    (root / "warn.md").write_text("\n".join(f"w{i}" for i in range(90)), encoding="utf-8")
    (root / "strict.md").write_text("\n".join(f"s{i}" for i in range(120)), encoding="utf-8")
    assert check_node_size(load_config(root), strict=True) == 1
    out = capsys.readouterr().out
    assert "info" in out and "over leaf goal 50, under warning 75" in out
    assert "warn" in out and "over leaf warning 75, under strict 100" in out
    assert "HARD" in out and "exceeds leaf strict 100" in out


def test_node_size_index_tiers(tmp_path, capsys):
    root = make_breakdown(tmp_path)
    warn = root / "02-architecture"
    warn.mkdir()
    (warn / "README.md").write_text("\n".join(f"row {i}" for i in range(60)), encoding="utf-8")
    hard = root / "05-operation"
    hard.mkdir()
    (hard / "README.md").write_text("\n".join(f"row {i}" for i in range(90)), encoding="utf-8")
    assert check_node_size(load_config(root), strict=True) == 1
    out = capsys.readouterr().out
    assert "over index warning 50, under strict 75" in out
    assert "exceeds index strict 75" in out


def test_node_size_frontmatter_exempt(tmp_path):
    root = make_breakdown(tmp_path)
    (root / "long.md").write_text(
        "---\npb_exempt: true\n---\n\n" + "\n".join(f"line {i}" for i in range(120)),
        encoding="utf-8",
    )
    assert check_node_size(load_config(root), strict=True) == 0


def test_node_size_frontmatter_exempt_is_opt_in(tmp_path):
    root = make_breakdown(tmp_path)
    (root / "long.md").write_text(
        "---\npb_exempt: false\n---\n\n" + "\n".join(f"line {i}" for i in range(120)),
        encoding="utf-8",
    )
    assert check_node_size(load_config(root), strict=True) == 1


def test_node_size_exempt_bare_folder(tmp_path):
    root = make_breakdown(tmp_path)
    folder = root / "analysis-algebraic-loop-constraint"
    folder.mkdir()
    (folder / "big.md").write_text("\n".join(f"line {i}" for i in range(120)), encoding="utf-8")
    (root / "pb.toml").write_text(
        '[nodes]\nexempt = ["analysis-algebraic-loop-constraint"]\n',
        encoding="utf-8",
    )
    assert check_node_size(load_config(root), strict=True) == 0


def test_node_size_exempt_nested_dir_path(tmp_path):
    root = make_breakdown(tmp_path)
    folder = root / "02-architecture" / "analysis-algebraic-loop-constraint"
    folder.mkdir(parents=True)
    (folder / "big.md").write_text("\n".join(f"line {i}" for i in range(120)), encoding="utf-8")
    # Wholesale list replacement (merge semantics): only the pinned folder is exempt.
    (root / "pb.toml").write_text(
        '[nodes]\nexempt = ["02-architecture/analysis-algebraic-loop-constraint"]\n',
        encoding="utf-8",
    )
    assert check_node_size(load_config(root), strict=True) == 0


def test_node_size_folder_exempt_does_not_leak(tmp_path):
    root = make_breakdown(tmp_path)
    folder = root / "analysis-algebraic-loop-constraint"
    folder.mkdir()
    (folder / "small.md").write_text("fine", encoding="utf-8")
    (root / "big.md").write_text("\n".join(f"line {i}" for i in range(120)), encoding="utf-8")
    (root / "pb.toml").write_text(
        '[nodes]\nexempt = ["analysis-algebraic-loop-constraint"]\n',
        encoding="utf-8",
    )
    assert check_node_size(load_config(root), strict=True) == 1


def test_parse_front_matter_lists():
    data, body = parse_front_matter(RECORD)
    assert data["id"] == "AD-001"
    assert data["layers"] == ["architecture"]
    assert data["artifacts"] == ["product-breakdown/leaf.md"]
    assert "## Context" in body


def test_parse_front_matter_strips_quotes():
    data, _ = parse_front_matter('---\ntitle: "Plan — Why a Layer"\nnote: \'single\'\n---\n\nBody\n')
    assert data["title"] == "Plan — Why a Layer"
    assert data["note"] == "single"


def test_parse_front_matter_folded_scalar():
    text = (
        "---\nsummary: >\n  What separates Dynamic Harness from other harnesses:\n"
        "  mechanically-enforced guarantees.\nrelated:\n  - ../VISION.md\n---\n\nBody\n"
    )
    data, _ = parse_front_matter(text)
    assert data["summary"] == "What separates Dynamic Harness from other harnesses: mechanically-enforced guarantees."
    assert data["related"] == ["../VISION.md"]


# --- generated index Contents (link-minimization) ---

_ID_COUNTER = [0]


def make_leaf(
    path: Path,
    title: str,
    summary: str,
    body: str = "Current state.",
    ident: str | None = None,
    type_: str = "info",
    date: str = "2026-09-29",
    status: str = "current",
) -> None:
    _ID_COUNTER[0] += 1
    ident = ident or f"INFO-{_ID_COUNTER[0]:03d}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nid: {ident}\ntype: {type_}\ntitle: {title}\nsummary: {summary}\n"
        f"date: {date}\nstatus: {status}\n---\n\n# {title}\n\n{body}\n",
        encoding="utf-8",
    )


def make_layer(tmp_path: Path, with_frontmatter: bool = True) -> Path:
    root = tmp_path / "product-breakdown"
    (root / "decisions").mkdir(parents=True)
    (root / "02-architecture").mkdir(parents=True)
    (root / "pb.toml").write_text("", encoding="utf-8")
    (root / "02-architecture" / "README.md").write_text(
        "# Architecture\n\n## Owns\n- organizing design\n\n## Contents\n- [stale](stale.md) — old\n",
        encoding="utf-8",
    )
    leaf_p = root / "02-architecture" / "delegation-model.md"
    if with_frontmatter:
        make_leaf(leaf_p, "Delegation model", "How parents decompose work")
    else:
        leaf_p.write_text("# Delegation model\n\nPlain leaf, no front-matter.\n", encoding="utf-8")
    return root


def test_sync_indexes_rebuilds_contents_from_frontmatter(tmp_path):
    cfg = load_config(make_layer(tmp_path))
    leaf_p = cfg.root / "02-architecture" / "delegation-model.md"
    make_leaf(leaf_p, "Delegation model", "How parents decompose work", ident="INFO-042")
    changed = sync_indexes(cfg)
    assert changed == ["02-architecture/README.md"]
    index = (cfg.root / "02-architecture" / "README.md").read_text(encoding="utf-8")
    assert (
        "- **INFO-042** [Delegation model](delegation-model.md) — How parents decompose work"
        in index
    )
    assert "[stale](stale.md)" not in index
    # repeated syncs are stable
    assert sync_indexes(cfg) == []


def test_sync_indexes_skips_index_without_contents_section(tmp_path):
    root = tmp_path / "product-breakdown"
    (root / "02-architecture").mkdir(parents=True)
    (root / "pb.toml").write_text("", encoding="utf-8")
    make_leaf(root / "02-architecture" / "leaf.md", "Leaf", "Summary")
    (root / "02-architecture" / "README.md").write_text(
        "# Architecture\n\nNo Contents heading here.\n", encoding="utf-8"
    )
    cfg = load_config(root)
    assert sync_indexes(cfg) == []
    assert "pb:index" not in (cfg.root / "02-architecture" / "README.md").read_text(encoding="utf-8")


def test_generate_syncs_indexes_and_footers(tmp_path):
    cfg = load_config(make_layer(tmp_path))
    assert generate(cfg, sync_footers_flag=True) == 0
    index = (cfg.root / "02-architecture" / "README.md").read_text(encoding="utf-8")
    assert "pb:index:start" in index and "Delegation model" in index


def test_check_leaves_requires_frontmatter(tmp_path):
    cfg = load_config(make_layer(tmp_path, with_frontmatter=False))
    assert check_leaves(cfg, strict=True) == 1


def test_check_leaves_rejects_path_link_in_leaf(tmp_path):
    root = make_layer(tmp_path)
    leaf = root / "02-architecture" / "delegation-model.md"
    leaf.write_text(
        leaf.read_text(encoding="utf-8").replace(
            "Current state.", "See [other.md](other.md)."
        ),
        encoding="utf-8",
    )
    assert check_leaves(load_config(root), strict=True) == 1


def test_check_leaves_allows_links_in_index(tmp_path):
    cfg = load_config(make_layer(tmp_path))
    # the index keeps its hand-written Table-of-Contents style links
    assert check_leaves(cfg, strict=True) == 0


def test_check_leaves_ignores_links_inside_fenced_code(tmp_path):
    root = make_layer(tmp_path)
    leaf = root / "02-architecture" / "delegation-model.md"
    leaf.write_text(
        leaf.read_text(encoding="utf-8").replace(
            "Current state.",
            "Example:\n\n```markdown\n[link](../other.md)\n```\n",
        ),
        encoding="utf-8",
    )
    assert check_leaves(load_config(root), strict=True) == 0


def test_check_ids_ignores_citations_inside_fenced_code(tmp_path):
    root = make_layer(tmp_path)
    leaf = root / "02-architecture" / "delegation-model.md"
    leaf.write_text(
        leaf.read_text(encoding="utf-8").replace(
            "Current state.",
            "```\ncitation `INFO-999`\n```\n",
        ),
        encoding="utf-8",
    )
    assert check_ids(load_config(root), strict=True) == 0


def test_check_leaves_ignores_generated_and_decisions(tmp_path):
    root = make_layer(tmp_path)
    (root / "decisions" / "AD-001-example-choice.md").write_text(RECORD, encoding="utf-8")
    cfg = load_config(root)
    assert check_leaves(cfg, strict=True) == 0


def test_node_size_excludes_generated_index_region(tmp_path):
    root = make_layer(tmp_path)
    cfg = load_config(root)
    sync_indexes(cfg)
    index = root / "02-architecture" / "README.md"
    text = index.read_text(encoding="utf-8")
    start, end = "<!-- pb:index:start -->", "<!-- pb:index:end -->"
    fat = start + "\n" + "\n".join(f"- [f{i}](f{i}.md) — filler" for i in range(500)) + "\n" + end
    index.write_text(
        text[: text.index(start)] + fat + text[text.index(end) + len(end):],
        encoding="utf-8",
    )
    assert check_node_size(cfg, strict=True) == 0


# --- stable leaf ids (INFO-/EVAL-), uniqueness, citations, scaffolding ---

from pbstd.ids import backfill_leaves, next_id, scaffold_leaf  # noqa: E402


def test_check_ids_duplicate_across_leaf_and_record(tmp_path, capsys):
    root = tmp_path / "product-breakdown"
    (root / "02-architecture").mkdir(parents=True)
    (root / "decisions").mkdir(parents=True)
    (root / "pb.toml").write_text("", encoding="utf-8")
    make_leaf(root / "02-architecture" / "leaf.md", "Leaf", "Sum", ident="AD-001")
    (root / "decisions" / "AD-001-example-choice.md").write_text(RECORD, encoding="utf-8")
    cfg = load_config(root)
    assert check_ids(cfg, strict=True) == 1
    assert "duplicate id 'AD-001'" in capsys.readouterr().out


def test_check_ids_requires_leaf_identity_keys(tmp_path, capsys):
    root = make_layer(tmp_path)
    (root / "02-architecture" / "old.md").write_text(
        "---\ntitle: Old\nsummary: Pre-id leaf\n---\n\n# Old\n\nBody.\n", encoding="utf-8"
    )
    assert check_ids(load_config(root), strict=True) == 1
    out = capsys.readouterr().out
    assert "missing front-matter key 'id'" in out and "missing front-matter key 'status'" in out


def test_check_ids_type_prefix_mismatch(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(
        root / "02-architecture" / "analysis.md",
        "Analysis",
        "An evaluation",
        ident="INFO-042",
        type_="eval",
    )
    assert check_ids(load_config(root), strict=True) == 1


def test_check_ids_resolves_valid_citation(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "a.md", "A", "A", ident="INFO-020")
    make_leaf(
        root / "02-architecture" / "b.md",
        "B",
        "B",
        ident="INFO-021",
        body="Governing analysis: `INFO-020`.",
    )
    assert check_ids(load_config(root), strict=True) == 0


def test_check_ids_ignores_non_registered_tokens(tmp_path):
    root = make_layer(tmp_path)
    for path in root.rglob("delegation-model.md"):
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Current state.", "Standard HTTP-2, ISO-9001 not ids."
            ),
            encoding="utf-8",
        )
    assert check_ids(load_config(root), strict=True) == 0


def test_check_ids_flags_unresolved_citation(tmp_path):
    root = make_layer(tmp_path)
    for path in root.rglob("delegation-model.md"):
        path.write_text(
            path.read_text(encoding="utf-8").replace("Current state.", "See `INFO-999`."),
            encoding="utf-8",
        )
    assert check_ids(load_config(root), strict=True) == 1


def test_check_ids_registers_ids_in_exempt_subtree(tmp_path):
    """A grandfathered node in an exempt folder still registers its id.

    Its id must resolve from live leaves (existing prose keeps working), while
    the exempt file itself skips the leaf-shape rules — it may stay legacy.
    """
    root = make_layer(tmp_path)
    (root / "02-architecture" / "legacy").mkdir(parents=True)
    (root / "02-architecture" / "legacy" / "AD-009.md").write_text(
        "---\nid: AD-009\ntype: decision\ntitle: Node model\nstatus: accepted\n---\n\n"
        "# AD-009: Node Model\n\n## Status\nAccepted\n",
        encoding="utf-8",
    )
    (root / "pb.toml").write_text(
        '[nodes]\nexempt = ["02-architecture/legacy"]\n', encoding="utf-8"
    )
    for path in root.rglob("delegation-model.md"):
        path.write_text(
            path.read_text(encoding="utf-8").replace("Current state.", "Enforced by `AD-009`."),
            encoding="utf-8",
        )
    assert check_ids(load_config(root), strict=True) == 0


def test_check_ids_reserved_ids_resolve(tmp_path, capsys):
    root = make_layer(tmp_path)
    (root / "pb.toml").write_text(
        '[ids]\nreserved_ids = ["IMP-015"]\n', encoding="utf-8"
    )
    for path in root.rglob("delegation-model.md"):
        path.write_text(
            path.read_text(encoding="utf-8").replace("Current state.", "Tracked as `IMP-015`."),
            encoding="utf-8",
        )
    assert check_ids(load_config(root), strict=True) == 0


def test_check_ids_reserved_duplicate(tmp_path):
    root = make_layer(tmp_path)
    (root / "02-architecture" / "real.md").write_text(
        "---\nid: INFO-001\ntype: info\ntitle: R\nsummary: S\ndate: 2026-09-29\nstatus: current\n---\n\n# R\n",
        encoding="utf-8",
    )
    (root / "pb.toml").write_text(
        '[ids]\nreserved_ids = ["INFO-001"]\n', encoding="utf-8"
    )
    assert check_ids(load_config(root), strict=True) == 1


def test_backfill_leaves_adds_identity(tmp_path, capsys):
    root = make_layer(tmp_path)
    (root / "02-architecture" / "old.md").write_text(
        "---\ntitle: Old\nsummary: Pre-id leaf\n---\n\n# Old\n\nBody.\n", encoding="utf-8"
    )
    cfg = load_config(root)
    changed = backfill_leaves(cfg)
    assert changed and "backfilled 02-architecture/old.md" in changed[0]
    text = (root / "02-architecture" / "old.md").read_text(encoding="utf-8")
    assert "id: INFO-" in text and "type: info" in text and "status: current" in text
    assert "date: 2026-" in text
    assert check_ids(cfg, strict=True) == 0
    # idempotent: a second pass changes nothing
    assert backfill_leaves(cfg) == []


def _min_root(tmp_path: Path) -> Path:
    """A bare root with one layer folder; no leaves, fully deterministic ids."""
    root = tmp_path / "product-breakdown"
    (root / "02-architecture").mkdir(parents=True)
    (root / "pb.toml").write_text("", encoding="utf-8")
    return root


def test_scaffold_new_leaf(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "first.md", "First", "One", ident="INFO-001")
    cfg = load_config(root)
    rel, ident, text = scaffold_leaf(cfg, "02-architecture", "Delegation model", summary="How")
    assert ident == "INFO-002"
    assert rel == Path("02-architecture/delegation-model.md")
    assert "id: INFO-002" in text and "status: current" in text and "date: 2026-" in text
    assert "summary: How" in text and "## Owns" in text


def test_scaffold_refuses_existing_file(tmp_path):
    root = _min_root(tmp_path)
    cfg = load_config(root)
    rel, _ident, text = scaffold_leaf(cfg, "02-architecture", "Delegation model", summary="How")
    (root / rel).write_text(text, encoding="utf-8")
    try:
        scaffold_leaf(cfg, "02-architecture", "Delegation model", summary="How again")
        raise AssertionError("expected FileExistsError")
    except FileExistsError:
        pass


def test_next_id_pads_and_continues(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "a.md", "A", "A", ident="INFO-007")
    make_leaf(root / "02-architecture" / "b.md", "B", "B", ident="INFO-009")
    assert next_id(load_config(root), "info") == "INFO-010"
    assert next_id(load_config(root), "eval") == "EVAL-001"


def test_next_id_additional_prefix_types(tmp_path):
    root = _min_root(tmp_path)
    cfg = load_config(root)
    for type_, expected in [
        ("research-question", "RQ-001"),
        ("constraint", "CON-001"),
        ("trace", "TR-001"),
        ("capability", "CP-001"),
        ("requirement", "REQ-001"),
        ("test", "TEST-001"),
    ]:
        assert next_id(cfg, type_) == expected, type_


def test_scaffold_additional_type_prefix(tmp_path):
    root = _min_root(tmp_path)
    cfg = load_config(root)
    rel, ident, text = scaffold_leaf(
        cfg, "02-architecture", "Acceptance test", summary="How it is verified", type_="test"
    )
    assert ident == "TEST-001"
    assert rel == Path("02-architecture/acceptance-test.md")
    assert "id: TEST-001" in text and "type: test" in text


def test_check_ids_resolves_citations_for_additional_prefixes(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(
        root / "02-architecture" / "t.md", "Test", "Verify", ident="TEST-001", type_="test"
    )
    make_leaf(
        root / "02-architecture" / "c.md",
        "Capability",
        "Promise",
        ident="CP-001",
        type_="capability",
        body="Verified by `TEST-001` per `REQ-001`.",
    )
    # REQ-001 is a planned requirement; reserve it so the citation resolves.
    (root / "pb.toml").write_text('[ids]\nreserved_ids = ["REQ-001"]\n', encoding="utf-8")
    assert check_ids(load_config(root), strict=True) == 0


def test_check_ids_rejects_unknown_leaf_type(tmp_path, capsys):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "x.md", "X", "X", ident="INFO-001", type_="bogus")
    assert check_ids(load_config(root), strict=True) == 1
    assert "unknown leaf type 'bogus'" in capsys.readouterr().out


# --- rejection routing: "should not do X" is a decision, not a leaf ---


def test_check_rejections_flags_not_to_do_named_leaf(tmp_path, capsys):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "not-to-do.md", "Not to do", "Don'ts")
    assert check_rejections(load_config(root), strict=True) == 1
    out = capsys.readouterr().out
    assert "rejection" in out and "decision record" in out and "deprecated/" in out


def test_check_rejections_flags_undeveloped_suggestion_named_leaf(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(
        root / "06-evolution" / "undeveloped-suggestions.md", "Suggestions", "Maybe"
    )
    assert check_rejections(load_config(root), strict=True) == 1


def test_check_rejections_ignores_tracker_titled_suggestion_log(tmp_path):
    """A live *tracker* of raw ideas (the 99_open-items.md pattern, e.g. a
    backlog) is not a rejection artifact: it tracks dispositions and points at
    canonical open work. Only the filename/headings signal the artifact."""
    root = _min_root(tmp_path)
    make_leaf(
        root / "06-evolution" / "backlog.md",
        "Backlog — raw suggestion log",
        "Raw idea log",
        body="Disposition: DONE / OPEN. Canonical open work: `INFO-196`.\n",
        ident="INFO-140",
    )
    assert check_rejections(load_config(root), strict=True) == 0


def test_check_rejections_flags_should_not_heading(tmp_path, capsys):
    root = _min_root(tmp_path)
    make_leaf(
        root / "02-architecture" / "concepts.md",
        "Concepts",
        "Sum",
        body="## Should not\n\nDo not do this thing.\n",
    )
    assert check_rejections(load_config(root), strict=True) == 1
    out = capsys.readouterr().out
    assert "not-to-be-done" in out and "decision record" in out


def test_check_rejections_ignores_present_tense_boundary(tmp_path):
    """A boundary IS state: 'X is out of scope' phrased present-tense passes,
    even when it uses 'never'/'do not' prose — the scan is artifact-level."""
    root = _min_root(tmp_path)
    make_leaf(
        root / "02-architecture" / "boundaries.md",
        "Boundaries",
        "Sum",
        body="The runtime has no root shell; a root shell is out of scope. "
        "Records are write-once, never modified.\n",
    )
    assert check_rejections(load_config(root), strict=True) == 0


def test_check_rejections_ignores_headings_inside_fenced_code(tmp_path):
    root = _min_root(tmp_path)
    make_leaf(
        root / "02-architecture" / "examples.md",
        "Examples",
        "Sum",
        body="Sample input:\n\n```markdown\n## Should not\n```\n",
    )
    assert check_rejections(load_config(root), strict=True) == 0


def test_check_rejections_skips_deprecated_tombstones(tmp_path):
    root = _min_root(tmp_path)
    tomb = root / "02-architecture" / "deprecated"
    tomb.mkdir(parents=True)
    (tomb / "undeveloped-suggestions.md").write_text("old\n", encoding="utf-8")
    assert check_rejections(load_config(root), strict=True) == 0


def test_check_rejections_skips_decision_records(tmp_path):
    """A rejection is a decision record: the record itself must never be
    flagged — decisions/ is the correct home for 'we chose not to do X'."""
    root = make_breakdown(tmp_path)
    (root / "decisions" / "AD-001-reject-the-thing.md").write_text(
        RECORD.replace("AD-001: Example choice", "AD-001: Reject The Thing"),
        encoding="utf-8",
    )
    assert check_rejections(load_config(root), strict=True) == 0


def test_check_ids_rejection_status_routes_to_decision(tmp_path, capsys):
    root = _min_root(tmp_path)
    make_leaf(root / "02-architecture" / "x.md", "X", "X", status="rejected")
    assert check_ids(load_config(root), strict=True) == 1
    out = capsys.readouterr().out
    assert "rejection is a decision record" in out and "deprecated/" in out
