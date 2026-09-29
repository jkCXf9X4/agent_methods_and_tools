# Deprecated Files

How files that are no longer current are retired: quarantined where they were,
never re-wired outgoing links.

## The rule

- When a file is deprecated, **move it into a `deprecated/` subfolder** of the
  directory that held it (for example `02-architecture/foo.md` →
  `02-architecture/deprecated/foo.md`). A consuming repo may instead designate
  a single top-level `deprecated/`; either way, the folder is the tombstone.
- Update the status to deprecated and add a deprecated header.
  Do not rewrite the file's contents, and do not update anything that refers to it.

## Leave internal references stale

- File links and other status information that point from the deprecated file are
  **left stale, not fixed**: links in other files, `state:` fields, status rows,
  "superseded by" notes, decision-log rows, and generated-register footers.

## Why

- Updating every reference from a dead file is busywork: the file contributes no
  new state, so maintaining its web of pointers adds cost without value, and
  falls out of date again anyway.
- The `deprecated/` path is the single, unambiguous marker: a reader or agent
  that sees it knows the file is dead and stops trusting anything that points
  there.

## Boundaries

- Quarantine is not accumulation: `deprecated/` holds only files that may still
  be consulted for context; a fully dead file is removed outright instead of
  moved.
- Leaving references stale is a deliberate carve-out from keeping links current;
  it applies only to `deprecated/`, never to live files.
- The deprecation itself is still recorded where the repo records history
  (a decision record or log entry): the event is documented — only the
  references it would sweep are not maintained.