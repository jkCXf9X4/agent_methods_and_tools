# Edit Checklist

For humans and agents editing `product-breakdown/`.

## Before Writing

1. Locate the canonical home (see the routing table in
   [`storage-rules.md`](storage-rules.md)).
2. Decide whether the change is **state** (edit a layer leaf) or **history** (add
   a dated decision record); a change to an accepted baseline needs a record.
3. Check for an existing representation; decide create / update / merge /
   supersede / remove.
4. Respect the node budget (AD-009): index goal ≤40 / warning 50 / strict 75,
   leaf goal ≤50 / warning 75 / strict 100.
5. Write for ingestion ease (see [`readability-rules.md`](readability-rules.md)):
   one fact per line, scannable structure, plain language, no padding.
6. Give every leaf the full front-matter block (`id`/`type`/`title`/`summary`/
   `date`/`status` — see [`templates/LEAF.md`](../templates/LEAF.md) and
   [`frontmatter.md`](frontmatter.md)); `pb new` scaffolds it, `pb check --fix`
   backfills the identity keys). Cite other nodes by ID, never by path link.

## After Editing

1. If you added, changed, or **moved** a record or leaf, update the moved leaf's
   front-matter and any record `state:`/`artifacts:` paths, then run
   `scripts/pb registers --sync-footers`; it
   regenerates the registers, leaf `## Decisions` footers, and index
   `## Contents` lists. Never hand-edit the generated registers or a generated
   index list. Because content cites by ID, no other file needs touching.
2. Run `scripts/pb node-size --strict` and resolve
   any node over strict (trim → cite → split).
3. Run `scripts/pb check --strict` and keep
   every record's front-matter, sections, budgets, and the leaf rules
   (full front-matter incl. a unique id, no path links, every citation
   resolving) valid.
4. Confirm readability: dense bullets are de-compacted into sub-bullets, and no
   node is cramped.
5. Run the consuming repo's own build and test checks.
