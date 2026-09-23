---
name: product-breakdown
description: Use when working in product-breakdown/ — the seven-layer current-state hierarchy, the flat dated decisions/ stream (ID-/PD-/AD-/IMD-/VD-/OD-), IMP candidates (IMP-), the generated registers, or the operating guidelines. Covers how to route an edit (state vs history), the decision-record model and budgets, and the regenerate/check commands. Use ONLY for the repo's product breakdown structure; do not use for ordinary paper or experiment edits.
---

# Product Breakdown Structure

`product-breakdown/` is the repo's systems-engineering record, split into two
surfaces plus a generated layer:

| Surface | Location | Holds |
|---|---|---|
| Current state | `00-intent/` … `06-evolution/` leaves | the design as it is now, present tense |
| History | `decisions/<ID>-<slug>.md` | one dated, immutable record per committed choice |
| Generated | `decisions/README.md`, `design-choice-log.md`, `traceability-map.md`, leaf footers | derived registers; never hand-edit |

## Why this shape

- **State and history are separate**, so a reader can act on the design without reconstructing a decision thread, and there is one current truth.
- **Records are dated, immutable events**: a change writes a new record and supersedes the old, so history survives instead of being overwritten.
- **Registers are generated** from record front-matter, so an index cannot drift into rows without files — it fails fast instead.
- **Enforcement is automated** (`check`, `node-size`); a violation is a blocker, not a style note.
- Full reasoning: `guidelines/workflow-rationale.md` (in this skill bundle).

## Canonical sources

All paths are relative to this skill's base directory.

| Task | Read |
|---|---|
| Layer ownership / boundary rule | the breakdown's top-level `README.md` |
| Where a fact is stored; routing | `guidelines/storage-rules.md` |
| Writing form | `guidelines/readability-rules.md` |
| Idea → IMP → decision → task; gates | `guidelines/change-pipeline.md` |
| Leaf → decision → artifact chain | `guidelines/traceability-rules.md` |
| Before/after edit steps | `guidelines/edit-checklist.md` |
| Record shape | `templates/TEMPLATE.md` |
| Config schema (only if overriding defaults) | `templates/pb.toml` |

## Route an edit

Decide the disposition before writing (create / update / merge / supersede /
remove):

- **State changed** → edit the owning layer leaf, present tense; a baseline change also needs a record.
- **New committed choice** → add a dated record to `decisions/`.
- **Not-yet-decided candidate** → file an IMP under `06-evolution/selected/`.
- **Already decided, only doing left** → a task, not a new record.

Route by concern: reason-to-exist → Intent; promised deliverable → Product;
organizing design → Architecture; files/scripts/interfaces/configs →
Implementation; proof/acceptance → Verification; routine build/release →
Operation; future work/risk → Evolution.

## Decision records

One committed choice = one file at `decisions/<PREFIX>-<NNN>-<slug>.md`, following
`templates/TEMPLATE.md` exactly. The prefix is a stable citation label; a
cross-layer choice is one record with several `layers:` values.

- Front-matter: `id, title, date, status, layers, state, artifacts, supersedes, superseded_by, related`.
- `Decision` is past tense and dated; `state:` names the leaf that holds current state.
- Supersession is binary and bidirectional; the checker verifies the pair.
- Budgets (enforced): `Decision` ≤4 lines (cap 6); `Context` ≤5 (cap 8); `Rationale` ≤5 (cap 8).

## Registers are generated

`registers --sync-footers` writes the index, changelog, traceability map, and each
`state:` leaf's `## Decisions` footer. Never hand-edit the output.

## Commands

Run from the breakdown's repository root; paths are relative to this skill's base
directory. No config is required — the standard's defaults apply, and the root is
discovered from `pb.toml` or `decisions/`.

```bash
python3 scripts/pb registers --sync-footers   # after record/leaf edits
python3 scripts/pb node-size --strict         # node budget (AD-009)
python3 scripts/pb check --strict             # front-matter, sections, budgets, supersession
python3 scripts/pb doctor                     # show the resolved configuration
```

Treat failures as blockers.
