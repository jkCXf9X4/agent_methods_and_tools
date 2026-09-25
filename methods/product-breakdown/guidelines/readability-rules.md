# Readability Rules

Write every node for the reader or agent who will ingest and act on it. The node
budget (AD-009) keeps a node small; these rules keep it easy to read. Compact is
not cramped: the same set of facts should be scannable, quotable, and cheap to
re-use.

## One Fact Per Line

- Break a bullet that carries several facts into a bold label plus sub-bullets:
  `- **Label**`, then one fact per indented `  - ` sub-bullet.
- Keep a single-fact bullet on one line.
- Do not chain distinct facts with semicolons or dashes.

## Scannable Structure

- Lead with the label or conclusion, then the supporting facts.
- Separate distinct groups with a blank line.
- Turn inline enumerations into bullets.

## Avoid Tables

A table makes a fact depend on its row and column to mean anything, so a fact in
a cell cannot be quoted, linked, or re-used on its own, and editing one cell
forces the reader to re-parse the whole row. That hidden dependence is exactly
what a labeled bullet removes: each line carries its own meaning and stands
alone.

- **Default to bullets.** Keep every fact on its own labeled line. If
  independent facts are being forced into a grid, the content is not tabular.
- **Never hide prose in a cell.** A cell holds a value, not a sentence. When a
  cell fills with a clause, move it to a `- **Label**` bullet.
- **One fact per cell.** Two facts in one cell violate One Fact Per Line; split
  them into sub-bullets.
- **Use a table only when the row-and-column relationship is the fact** — a
  comparison matrix or a key → value lookup whose value needs both axes to make
  sense. Where a single line can carry the pairing, prefer a `key → value`
  bullet.
- **Do not store an idea across a row.** If a reader must scan left-to-right and
  stitch cells into one thought, that thought is prose; write it as a labeled
  bullet.
- The index link table and the generated registers are deliberate exceptions:
  they are lookups, and registers are never hand-edited.

## Plain Language

- Split sentences longer than ~35 words.
- Prefer active voice and plain verbs; avoid nominalizations.
- Expand abbreviations in prose (`incl.` → `including`, `e.g.` → `for example`).
- Keep identifiers, keys, paths, and commands exact.

## Proportional, Never Padded

- Add structure, not claims: never invent facts, examples, or rationale.
- Reformatting must preserve every fact, ID, link, number, and table row.
- If it does not fit, use the node-budget remedy in
  [storage-rules.md](storage-rules.md) (trim → link → split). Do not re-compact,
  overflow, or duplicate to make room.
