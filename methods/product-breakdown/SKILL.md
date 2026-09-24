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
| Per-layer detail and worked routing examples | `guidelines/layer-guide.md` |
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

Route by concern; the boundary rule is the table in **The seven layers** below.

## The seven layers

The current state is a seven-layer hierarchy, `00-intent/` … `06-evolution/`.
Each layer has one index (`README.md`: purpose, owns/excludes, a link table) and
small leaves, each holding one present-tense fact. Read top-down; write by
routing each fact to exactly one home.

| Layer | Directory (record prefix) | Holds | Routing concern | Example fact |
|---|---|---|---|---|
| Intent | `00-intent/` (ID-) | why the product exists: scope, goals, mission, boundaries | reason-to-exist | the operator persona and in/out scope |
| Product | `01-product/` (PD-) | the promised deliverable: capabilities and requirements others rely on | promised deliverable | an API surface contract promised to integrators |
| Architecture | `02-architecture/` (AD-) | the organizing design: how parts fit and interact | organizing design | component decomposition and the message flow between services |
| Implementation | `03-implementation/` (IMD-) | files, scripts, interfaces, configs | files/scripts/interfaces/configs | the CLI's config schema in `pb.toml` |
| Verification | `04-verification/` (VD-) | proof and acceptance: how each claim is checked | proof/acceptance | the acceptance test for the checkout flow |
| Operation | `05-operation/` (OD-) | routine build, release, and run concerns | routine build/release | the release steps and on-call runbook |
| Evolution | `06-evolution/` (IMP-) | future work and risk: IMP candidates, never current state | future work/risk | an IMP proposing an alternative storage format |

### How agents should work with them

- **Read top-down, then into leaves.** Start at the breakdown's top-level
  `README.md`, open the layer index, then the leaf that owns the concern. Indexes
  are navigation, not content; leaves are the current-state facts.
- **Route each fact to one home.** Use the routing concern in the table; where
  the top-level `README.md` states the boundary rule, the `README.md` wins.
- **Information flows downward only** (Intent → Product → Architecture →
  Implementation → Verification → Operation). Never push design detail up a layer.
- **Cross-layer material** keeps its canonical statement at the layer owning the
  primary concern and defers the rest by reference; say the carve-out explicitly.
- **Evolution holds candidates, not current state.** IMPs live there until their
  resulting state is written into an owning layer; do not restate current state in
  Evolution, and do not store rationale in an index.
- **History points at state.** A record's `layers:` names the layers it touches
  and `state:` names the canonical leaf; a cross-layer choice is one record with
  several `layers:` values.

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
