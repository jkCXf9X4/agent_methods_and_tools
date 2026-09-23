# Traceability Rules

Keeping `current-state leaf → decision record(s) → artifact(s)` unbroken. The
chain is **generated**, not hand-maintained.

## The Chain

- Every record names its `state:` leaf and its `artifacts:` (repo-relative paths).
- `scripts/pb registers` turns that front-matter into `traceability-map.md`
  (leaf → decisions → artifacts) and `design-choice-log.md`.
- Leaf `## Decisions` footers are also generated from `state:`.

## Forward Traceability (leaf → decision → artifact)

- Every record MUST set `state:` to an existing leaf and list `artifacts:` as
  concrete repo-relative paths. Enforced by `scripts/pb check`.
- When a choice affects different artifacts, update the record's `artifacts:` and
  regenerate; do not hand-edit the map.
- If a canonical artifact or leaf is renamed, update the record(s) in the same
  change and regenerate.

## Reverse Traceability (artifact → decision)

- The map is the index; reverse lookups resolve through each record's `state:`
  and `artifacts:`.
- A decision that builds on or refines another names it in `related:` (IDs).

## Supersession Protocol

- Supersession is **binary and bidirectional**: set `superseded_by` on the old
  record and `supersedes` on the new one.
- The checker verifies the pair; partial supersession must be stated explicitly
  in both records.
- Superseded records remain as history; the current truth is the `state:` leaf.

## Keeping the Chain Unbroken

- Registers are generated from real files: no map row without a record, no leaf
  footer without a record.
- Editing a record or leaf requires `scripts/pb registers --sync-footers`.
