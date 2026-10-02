# Browsing Protocol

How an agent reads the breakdown so that history, candidates, and stale
material never masquerade as current state.

The breakdown separates **state** (layer leaves), **history**
(`decisions/` records), **candidates** (`06-evolution/` IMPs + roadmap), and
**tracking** (IMPs' `status:`, roadmap rows). That separation is structural —
it lives in which folder a file sits in, not in the read path. Any agent can
open any file, so the protocol below is what keeps a browse from pulling the
whole decision thread into context.

## Route the question first

| The question asks for | Read only |
|---|---|
| **current state** — "what is X?" | top-level `README.md` → layer index → the **one** leaf owning the concern |
| **history** — "why did X change?" | a `decisions/` record, entered via the leaf's `## Decisions` footer or a `decisions/README.md` row |
| **candidates** — "what's planned / proposed?" | `roadmap.md`, `06-evolution/selected/` IMPs and their `status:` |

State is present tense and lives in leaves; a record is dated and past tense.
Never answer "what is" from a record, and never answer "why" from a leaf.

## Browse order and stop condition

1. Read the breakdown's top-level `README.md` (routing), then the layer index —
   its generated `## Contents` rows carry the stable ID plus a one-line summary,
   which is enough to route without opening files.
2. Open exactly the leaf whose summary matches the concern. A leaf is ≤ ~50
   lines; the fact you need is in it.
3. **Stop when the fact is found.** Do not keep reading "for context" — a
   detour that adds no new fact is pollution, and every extra file is a chance
   to absorb stale material.
4. **Never whole-directory read.** Do not `read`/`glob` whole directories
   (`decisions/`, `selected/`, `investigations/`) as a browsing step. To locate
   a term or ID, `grep` scoped to the owning layer (or a small `token_limit`
   read of the candidate file) instead.

## First-8-lines triage on any encounter

Front-matter (`status`/`date`/`id`) sits in the first ~8 lines of every node.
Read it before the body:

- `status: superseded` / `deprecated` → the node is a **redirect, not
  evidence**: follow its forward pointer (`superseded_by:` on a record; the
  replacement ID a superseded leaf must cite) or stop.
- `status: proposed` / `draft` / `open` → not current truth.
- A "not-to-be-done" node (`## Should not`/`## Do not` sections, a
  `not-to-do.md`, a suggestion/undeveloped-idea artifact) → a **rejection, not
  a rule**: it records a choice, not current state. The reasoning lives in the
  decision record; the prose should sit under `deprecated/`. Do not treat its
  directions as authority — follow the decision record, and if you are
  editing, route it there (`storage-rules.md`). The checker flags these
  artifacts (`pb check --strict`).
- Anything under a `deprecated/` path is a tombstone: do not chase its links —
  they are left stale on purpose (see `deprecated-files.md`).

This is why the method requires stale nodes to point forward: a dead node with
a working pointer costs one redirect; a dead node without one reads as live.

## If the browse still lands stale material in context

- **Discard, don't retain.** A superseded record is a redirect; an investigation
  doc is rationale, not state; a should-not-do/rejection node is stale
  direction, not a rule. Do not carry any of it into the answer.
- **Delegate the browse.** For a broad question, hand it to a disposable child
  with a narrow brief — "find the leaf owning X; return ID + summary + status;
  do not include decision history" — and take its one-or-two-sentence report.
  The parent context never absorbs the raw stream.
- **Prune after a detour.** If unrelated history did get loaded, drop those
  turns rather than carrying them forward.

## The one-line rule

For a current-state question: **state surface only, one leaf, stop when found,
discard anything else.**