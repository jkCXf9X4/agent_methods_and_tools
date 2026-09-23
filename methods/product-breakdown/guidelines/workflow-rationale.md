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

## Records are history, not a palimpsest

- A record is written once; when the design changes, a new record supersedes the
  old in both directions. History survives by supersession, not by editing.
- "Decision record" (not "design choice") names what it is: one event.

## The registers are generated

- `decisions/README.md`, `design-choice-log.md`, `traceability-map.md`, and leaf
  `## Decisions` footers are all generated from record front-matter.
- Hand-maintained indexes drift (rows without files, mirrored rationales); a
  generated register fails fast instead.

## Enforcement is automated

- `scripts/pb node-size` enforces the node budget (AD-009).
- `scripts/pb check` enforces front-matter, template order, budgets, and
  state/artifact existence; a violation is a blocker, not a style note.
