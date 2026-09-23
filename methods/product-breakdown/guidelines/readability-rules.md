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
- Use a table only for genuinely tabular data; do not hide prose in a cell.

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
