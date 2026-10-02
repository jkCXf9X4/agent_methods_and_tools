# Change Pipeline

How future changes are worked before they are implemented.

## The Pipeline

```
Idea → IMP (Proposed) → IMP (Selected, scoped) → decision record in the flat
       stream (if baseline-changing or cross-layer) → owning layer adopts →
       task contract → implement → verify → IMP moved to 06-evolution/implemented/
```

- **Scoped candidate:** an IMP is a scoped candidate, not implementation
  approval.
- **Task contract gate:** a change is implementable only once it has a task
  contract (Objective / Scope / Acceptance).
- **Design-choice gate:** if it alters an accepted baseline or spans layers, it
  also needs an accepted decision record that the owning layer cites as authority.

## Choosing IMP vs Decision Record vs Task

- **IMP**
  - Any improvement candidate with an evidence-backed pain/risk that is not yet
    decided.
  - Creating an IMP requires no permission and confers no approval.
- **Decision record** — a change that:
  - (a) modifies an accepted owning-layer baseline,
  - (b) spans more than one layer, or
  - (c) supersedes an existing decision.
  - Filed at `decisions/<PREFIX>-NNN-<slug>.md` (the prefix keeps its layer
   label), follows `decisions/TEMPLATE.md`, and is picked up by the generated
   registers.
- **Task**
  - Concrete work derived from an accepted IMP/decision record, with explicit
    scope and acceptance.
  - Only tasks produce code changes.

**Rule of thumb:**
- If the change is already decided and only the doing is left, it is a task, not
  a new record.
- Prefer updating an existing IMP/record over creating a new number.

## IMP Lifecycle

- **Lifecycle:** `Proposed → Selected → Implemented`. A live IMP file lives in
  `06-evolution/selected/`; once implemented, it is **moved** to
  `06-evolution/implemented/` (`./implemented/` relative to the layer).
- **Not tracked after the move:** an implemented IMP is no longer tracked. Drop
  it from the `06-evolution/README.md` cross-listing and from the roadmap
  register; its status is no longer maintained, and it must not be re-added to
  any open-work tracker. The file survives under `implemented/` only as a
  historical record of what was done.
- **Status source:** status is read **only** from the IMP file header; never
  maintain a second status copy.
- **Cross-listing:** every open IMP (Proposed/Selected) is cross-listed in
  `06-evolution/README.md`; implemented IMPs are not.
  - A listed IMP must have a real file.
  - Do not list phantom IDs.
- Update an IMP's status in place; do not create competing records for the same
  candidate.
- **Update status after every job.** Working an IMP — any job, partial or
  complete — ends with a status update in the **same change**: partial work
  records what is done and what remains; completed work sets the final status,
  updates the header, and moves the file to `06-evolution/implemented/` (see
  "Not tracked after the move" above). A `status:` left standing from before
  the job is stale information; a status written anywhere else (a second file,
  a hand-edited register row, a stale roadmap cell) is a duplicate that can
  contradict the header. Both are conflicting information, not documentation —
  the file header is the only status copy.

## Graduating to Implementation

A change may be implemented only when all hold:

1. Owning layer cites the accepted decision record (or an adopted IMP) as authority.
2. Task contract has Objective / Scope / Acceptance.
3. Verification/acceptance criteria are defined.
4. The resulting state is written into the owning layer in the same change, and
   the registers are regenerated.
