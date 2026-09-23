# Edit Checklist

For humans and agents editing `product-breakdown/`.

## Before Writing

1. Locate the canonical home (see the routing table in
   [`storage-rules.md`](storage-rules.md)).
2. Decide whether the change is **state** (edit a layer leaf) or **history** (add
   a dated decision record); a change to an accepted baseline needs a record.
3. Check for an existing representation; decide create / update / merge /
   supersede / remove.
4. Respect the node budget (AD-009): index target ≤40 / cap 75, leaf ≤50 / cap 75.
5. Write for ingestion ease (see [`readability-rules.md`](readability-rules.md)):
   one fact per line, scannable structure, plain language, no padding.

## After Editing

1. If you added or changed a record or leaf, run
   `scripts/pb registers --sync-footers`; never
   hand-edit the generated registers.
2. Run `scripts/pb node-size --strict` and resolve
   any node over cap (trim → link → split).
3. Run `scripts/pb check --strict` and keep
   every record's front-matter, sections, and budgets valid.
4. Confirm readability: dense bullets are de-compacted into sub-bullets, and no
   node is cramped.
5. Run the consuming repo's own build and test checks.
