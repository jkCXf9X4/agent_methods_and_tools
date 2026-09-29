# Front-Matter Structure

Every live node carries one YAML front-matter block. The generated registers
read it, and the checks enforce it. The block is the node's **identity** (the
stable ``id``), its **description** (``title``/``summary``), and its
**lifecycle** (``type``/``date``/``status``).

## Leaf front-matter (canonical order)

```yaml
---
id: INFO-001
type: info
title: <Same as the H1; index label>
summary: <One line; index row description>
date: 2026-09-29
status: current
---
```

| Key | Meaning | Notes |
|---|---|---|
| `id` | Stable, unique reference: `<PREFIX>-<NNN>` | The citation handle. Assigned by `pb new`, guaranteed globally unique by `pb check`. **Never** the filename or a path. |
| `type` | Content type: `info` \| `eval` | Drives the ID prefix (`info` → `INFO-`, `eval` → `EVAL-`). The type is what survives a move. |
| `title` | Same as the H1 | The generated index label. |
| `summary` | One line | The generated index row description. |
| `date` | `YYYY-MM-DD` | Created or last reviewed. |
| `status` | `current` \| `draft` \| `superseded` | Leaf lifecycle. Decision records use the record statuses instead. |

- Decision records use their own block ([`templates/TEMPLATE.md`](../templates/TEMPLATE.md)):
  the per-layer citation prefixes (`ID-`, `PD-`, `AD-`, …) are grandfathered,
  and their ids are uniqueness-checked against every other node.
- Indexes carry only `title`/`summary` (their own row in the layer above); they
  hold no id.

## How IDs are displayed and used

- **Front-matter** — `id:` is the single source of truth.
- **Generated index rows** — `- **INFO-001** [Title](leaf.md) — summary`: the
  id is shown so a reader can cite it straight from the index. Never hand-write
  this list; `pb registers --sync-footers` rebuilds it.
- **Citations** — `` `INFO-001` `` in backticks in hand-written content. The
  checker resolves every registered-prefix token in body text and flags one
  that does not exist, so a stale reference after a move or delete is a
  blocker, not a silent break.
- **Never in paths** — an id never appears in a filename, folder, or link
  target, so moving or renaming a file costs zero reference edits plus one
  `pb registers --sync-footers` run.

## Creating and backfilling

- `python3 scripts/pb new <directory> "<Title>" --summary "…" [--type info|eval]`
  scaffolds a leaf with the full block: next free id for the type's prefix,
  today's date, `status: current`, and an Owns/Excludes skeleton. It refuses to
  overwrite an existing file.
- `python3 scripts/pb check --fix` fills missing `id`/`type`/`date`/`status`
  onto existing leaves that already carry `title` + `summary` — an opt-in
  backfill *while running the checks*. Duplicate ids are never renumbered
  (that would break citations); they are reported for a manual resolution,
  which is one edit plus a sync.