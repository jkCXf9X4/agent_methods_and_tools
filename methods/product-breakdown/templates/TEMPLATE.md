---
id: <PREFIX>-<NNN>
title: <Design Choice Title>
date: <YYYY-MM-DD>
status: <proposed|accepted|superseded|rejected|deprecated>
layers: [<intent|product|architecture|implementation|verification|operation>]
state: <repo-relative path to the canonical current-state leaf>
artifacts:
  - <repo-relative path>
supersedes: []
superseded_by: []
related: []
---

# <ID>: <Title>

<!-- A decision record is history: one dated event, immutable once written. It
     answers "what was decided, when, and why" — never "what is the design now".
     Current state lives in the owning layer's leaf named by `state:`.
     Budgets (enforced by tools/check_decisions.py --strict):
       - Decision: target ≤4 lines, hard cap 6.
       - Rationale: target ≤5 lines, hard cap 8.
       - Context: target ≤5 lines, hard cap 8.
     Do not edit a record as the design evolves; write a new record and set
     `superseded_by` / `supersedes` on both. -->

## Context
<The situation and forces at decision time. Historical framing only.>

## Decision
<What was chosen, as a dated event. No present-tense current-state claim.>

## Rationale
<The problem, constraint, or need that made this the choice; 2–5 lines.>

## Alternatives Considered
- <Alternative 1>
- <Alternative 2>

## Consequences
- Positive: <...>
- Negative: <...>

## Verification
<How the choice is checked in the owning layer's verification, or "None".>

## Review Trigger
<When this choice should be revisited, or "None".>
