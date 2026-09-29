"""Generate the decision registers from the flat decision stream.

Reads record front-matter from ``<root>/decisions/*.md`` and writes the index,
changelog, and traceability map (all generated; never edit by hand), plus each
``state:`` leaf's ``## Decisions`` footer and each index's ``## Contents`` list
when ``--sync-footers`` is given.
"""
from __future__ import annotations

import re
from pathlib import Path

from .config import Config
from .records import as_list, parse_front_matter

FOOTER_RE = re.compile(r"^## Decisions\s*$.*?(?=^## |\Z)", re.M | re.S)


def _section_re(section: str) -> re.Pattern:
    return re.compile(rf"^## {re.escape(section)}\s*$(.*?)(?=^## |\Z)", re.M | re.S)


def load_records(cfg: Config) -> list[dict]:
    skip = set(cfg.get("layout", "record_skip"))
    records: list[dict] = []
    if not cfg.decisions.exists():
        return records
    for path in sorted(cfg.decisions.glob("*.md")):
        if path.name in skip:
            continue
        data = parse_front_matter(path.read_text(encoding="utf-8"))[0]
        if not data:
            continue
        data["_path"] = path
        records.append(data)
    return records


def primary_layer(rec: dict) -> str:
    layers = as_list(rec.get("layers"))
    return layers[0] if layers else "unassigned"


def render_index(cfg: Config, records: list[dict]) -> str:
    banner = cfg.get("registers", "banner")
    out = [
        banner,
        "",
        "# Decision Stream",
        "",
        "Flat, dated history of every committed design choice. Current state lives",
        "in the layer leaves named by each record's `state:` field.",
        "",
        "## By Layer",
        "",
    ]
    for layer in cfg.get("layers", "order"):
        group = [r for r in records if primary_layer(r) == layer]
        if not group:
            continue
        out.append(f"### {layer.capitalize()}")
        out.append("")
        for rec in group:
            out.append(
                f"- **{rec['id']}** — {rec['title']} · {rec.get('status')} · "
                f"{rec.get('date')} · [record]({rec['_path'].name})"
            )
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_log(cfg: Config, records: list[dict]) -> str:
    banner = cfg.get("registers", "banner")
    title = cfg.get("registers", "log_title")
    out = [
        banner,
        "",
        f"# {title}",
        "",
        "Chronological history, newest first. Generated from the flat decision",
        "stream.",
        "",
        "| Date | ID | Decision | Layers | Status | Record |",
        "|---|---|---|---|---|---|",
    ]
    for rec in sorted(
        records, key=lambda r: (str(r.get("date", "")), str(r.get("id", ""))), reverse=True
    ):
        layers = ", ".join(as_list(rec.get("layers")))
        out.append(
            f"| {rec.get('date')} | {rec['id']} | {rec['title']} | {layers} | "
            f"{rec.get('status')} | [record](decisions/{rec['_path'].name}) |"
        )
    return "\n".join(out) + "\n"


def render_traceability(cfg: Config, records: list[dict]) -> str:
    banner = cfg.get("registers", "banner")
    by_state: dict[str, list[dict]] = {}
    for rec in records:
        by_state.setdefault(str(rec.get("state", "")), []).append(rec)
    out = [
        banner,
        "",
        "# Traceability Map",
        "",
        "Generated from each record's `state:` field: current-state leaf ->",
        "decisions -> artifacts. Current state is the leaf; the records are its",
        "history.",
        "",
    ]
    for state in sorted(by_state):
        recs = sorted(by_state[state], key=lambda r: str(r.get("id")))
        title = state
        path = cfg.root / state
        if path.exists():
            title = next(
                (
                    line[2:].strip()
                    for line in path.read_text(encoding="utf-8").splitlines()
                    if line.startswith("# ")
                ),
                state,
            )
        ids = ", ".join(r["id"] for r in recs)
        artifacts: list[str] = []
        for rec in recs:
            for artifact in as_list(rec.get("artifacts")):
                if artifact not in artifacts:
                    artifacts.append(artifact)
        arts = ", ".join(f"`{a}`" for a in artifacts) or "—"
        out.append(f"- **{title}** — Decisions: {ids} · Artifacts: {arts} · State: `{state}`")
    return "\n".join(out) + "\n"


def sync_footers(cfg: Config, records: list[dict]) -> list[str]:
    by_state: dict[str, list[dict]] = {}
    for rec in records:
        by_state.setdefault(str(rec.get("state", "")), []).append(rec)
    changed: list[str] = []
    for state, recs in sorted(by_state.items()):
        path = cfg.root / state
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lines = [f"- {r['id']} — {r['title']}" for r in sorted(recs, key=lambda r: str(r.get("id")))]
        section = "## Decisions\n\n" + "\n".join(lines) + "\n"
        new = (
            FOOTER_RE.sub(section, text).rstrip() + "\n"
            if FOOTER_RE.search(text)
            else text.rstrip() + "\n\n" + section
        )
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(state)
    return changed


def _in_deprecated(rel: Path) -> bool:
    return "deprecated" in rel.parts


def _leaf_meta(path: Path, title_key: str, summary_key: str, fallback: str) -> tuple[str, str]:
    """Return ``(label, summary)`` for a node from its front-matter."""
    data, _body = parse_front_matter(path.read_text(encoding="utf-8"))
    if not data:
        return fallback, ""
    label = str(data.get(title_key, "")).strip() or fallback
    summary = str(data.get(summary_key, "")).strip()
    return label, summary


def index_rows(folder: Path, cfg: Config) -> list[str]:
    """One generated Contents row per direct child of *folder*.

    Directories point at their ``README.md``; leaf files are listed directly.
    Deprecated entries and index files themselves are skipped — deprecated
    tombstones are dropped by regeneration, not re-wired.
    """
    title_key = cfg.get("indexes", "title_key", default="title")
    summary_key = cfg.get("indexes", "summary_key", default="summary")
    index_names = set(cfg.get("layout", "index_names"))
    rows: list[tuple[str, str, str]] = []
    for child in sorted(folder.iterdir()):
        rel = child.relative_to(cfg.root)
        if _in_deprecated(rel):
            continue
        if child.is_dir():
            readme = child / "README.md"
            if not readme.is_file():
                continue
            label, summary = _leaf_meta(readme, title_key, summary_key, fallback=child.name)
            rows.append((label, f"{child.name}/README.md", summary))
        elif child.suffix == ".md" and child.name not in index_names:
            label, summary = _leaf_meta(child, title_key, summary_key, fallback=child.stem)
            rows.append((label, child.name, summary))
    out: list[str] = []
    for label, target, summary in sorted(rows):
        out.append(f"- [{label}]({target})" + (f" — {summary}" if summary else ""))
    return out


def sync_indexes(cfg: Config) -> list[str]:
    """Regenerate each index's ``## <section>`` list from its direct children.

    Only indexes that already carry the section heading are touched (none are
    invented); the list between the start/end markers is replaced, and the
    markers are inserted on first sync. Returns the changed relative paths.
    """
    if not cfg.get("indexes", "enabled", default=True):
        return []
    section = cfg.get("indexes", "section", default="Contents")
    start = cfg.get("indexes", "start_marker", default="<!-- pb:index:start -->")
    end = cfg.get("indexes", "end_marker", default="<!-- pb:index:end -->")
    index_names = set(cfg.get("layout", "index_names"))
    exclude_dirs = set(cfg.get("layout", "exclude_dirs"))
    marker = cfg.get("layout", "generated_marker")
    section_re = _section_re(section)

    changed: list[str] = []
    for path in sorted(cfg.root.rglob("*.md")):
        rel = path.relative_to(cfg.root)
        if rel.name not in index_names or _in_deprecated(rel):
            continue
        if rel.parts[0] in exclude_dirs:
            continue
        if is_generated(path, marker):
            continue
        text = path.read_text(encoding="utf-8")
        match = section_re.search(text)
        if match is None:
            continue
        rows = index_rows(path.parent, cfg)
        block = f"{start}\n" + "\n".join(rows) + f"\n{end}"
        new = _replace_section(text, match, block, start, end)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(rel.as_posix())
    return changed


def _replace_section(text: str, match: re.Match, block: str, start: str, end: str) -> str:
    """Replace a ``## <section>`` (from *match*) with a generated *block*.

    If the markers already exist inside the section, only the list between them
    is replaced; otherwise the old list is replaced and the markers inserted.
    """
    body = match.group(1)
    si, ei = body.find(start), body.find(end)
    if si != -1 and ei != -1 and ei > si:
        new_body = body[:si] + block + body[ei + len(end):]
    else:
        new_body = block + "\n" + body.lstrip("\n").rstrip()
        # keep any trailing prose after the old list? no: the list is the section
    return text[: match.start()] + match.group(0)[: match.group(0).index("\n") + 1] + new_body + text[match.end():]
    out_dir = Path(out_dir).resolve() if out_dir else cfg.root
    records = load_records(cfg)
    if not records:
        print("No decision records found.")
        return 0

    outputs = {
        out_dir / cfg.get("registers", "index"): render_index(cfg, records),
        out_dir / cfg.get("registers", "log"): render_log(cfg, records),
        out_dir / cfg.get("registers", "traceability"): render_traceability(cfg, records),
    }
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")
    if sync_footers_flag:
        changed = sync_footers(cfg, records)
        print(f"synced footers in {len(changed)} leaves")
    print(f"{len(records)} decision records processed.")
    return 0
