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
    (root / "big.md").write_text("\n".join(f"line {i}" for i in range(80)), encoding="utf-8")
    assert check_node_size(load_config(root), strict=True) == 1


def test_parse_front_matter_lists():
    data, body = parse_front_matter(RECORD)
    assert data["id"] == "AD-001"
    assert data["layers"] == ["architecture"]
    assert data["artifacts"] == ["product-breakdown/leaf.md"]
    assert "## Context" in body
