# Workflow Rationale

Why the breakdown is written and changed this way. The executable rules are in
[storage-rules.md](storage-rules.md), [change-pipeline.md](change-pipeline.md),
[traceability-rules.md](traceability-rules.md), and
[readability-rules.md](readability-rules.md); this note records the reasoning
those rules serve.

## State and history are separate surfaces

- Current state lives only in layer leaves, in the present tense, so a reader or
  agent can act on the design without reconstructing a decision thread.
- Decision records are dated, immutable events: what was chosen, when, and why.
  They never restate current state, so there is exactly one current truth.

## Status and events are not current state

- A leaf states what **is**, not what happened and not how far along the work
  is. A dated event ("on 2026-09-29, X changed") is history and belongs in a
  record; a progress marker ("3 of 5 done") is tracking and belongs in a
  tracker or the IMP's `status:`. Both smuggled into a leaf turn the leaf into
  a journal, and a journal cannot be acted on as current truth.
- A separated tracker (for example a `99_open-items.md` beside the leaves) is a
  pointer, not a content home: it enumerates open work and points at the
  canonical leaf or record by ID. When it starts absorbing dated events or
  progress narrative, it becomes a second leaf or a second history — the same
  drift the generated registers exist to prevent.

## Records are history, not a palimpsest

- A record is written once; when the design changes, a new record supersedes the
  old in both directions. History survives by supersession, not by editing.
- "Decision record" (not "design choice") names what it is: one event.

## The registers are generated

- `decisions/README.md`, `design-choice-log.md`, `traceability-map.md`, leaf
  `## Decisions` footers, and each index's `## Contents` list are all generated
  from record and leaf front-matter.
- Hand-maintained indexes drift (rows without files, mirrored rationales); a
  generated register fails fast instead.
- Generated navigation is what makes link minimization safe: hand-written
  content cites by ID, and the generated indexes/registers are the only place
  a location is written — so a move re-resolves on the next run instead of
  requiring a link sweep.

## Enforcement is automated

- `scripts/pb node-size` enforces the node budget (AD-009).
- `scripts/pb check` enforces front-matter, template order, budgets, and
  state/artifact existence; a violation is a blocker, not a style note.
