"""Tests for the pbstd package."""
from __future__ import annotations

from pathlib import Path

from pbstd.checks import check_decisions, check_node_size
from pbstd.config import DEFAULTS, find_root, load_config
from pbstd.records import parse_front_matter
from pbstd.registers import generate

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


def test_generate_writes_registers(tmp_path):
    cfg = load_config(make_breakdown(tmp_path))
    assert generate(cfg, sync_footers_flag=True) == 0
    index = (cfg.root / "decisions" / "README.md").read_text(encoding="utf-8")
    assert "GENERATED FILE" in index and "AD-001" in index
    assert "## Decisions" in (cfg.root / "leaf.md").read_text(encoding="utf-8")


def test_node_size_flags_oversize_leaf(tmp_path):
    root = make_breakdown(tmp_path)
    (root / "big.md").write_text("\n".join(f"line {i}" for i in range(120)), encoding="utf-8")
    assert check_node_size(load_config(root), strict=True) == 1


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
