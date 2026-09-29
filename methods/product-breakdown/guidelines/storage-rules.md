# Storage Rules

How information is stored in `product-breakdown/`.

## Canonical State, Never Accumulation

- Each fact has exactly one home. When a fact changes, **update, replace, or
  supersede** the existing representation; never append a second truth beside it.
- The layer leaves hold the **current state**; the flat decision stream
  (`decisions/`) holds dated **history and rationale**; Evolution holds
  **candidates** for change. Do not re-describe current state in Evolution, and
  do not store rationale inside an index.
- A file that is no longer current is **moved to a `deprecated/` subfolder**
  and any links or status info pointing from it are left stale (never chased) —
  see [deprecated-files.md](deprecated-files.md).
- Information flows downward only (Intent → Product → Architecture →
  Implementation → Verification → Operation). Do not push design detail up.

## Ownership and the Boundary Rule

- Route every addition through the boundary rule in the breakdown's top-level
  `README.md`: reason-to-exist → Intent; promised deliverable
  → Product; organizing design → Architecture; files/scripts/interfaces/configs
  → Implementation; proof/acceptance → Verification; routine build/release →
  Operation; future work or risk → Evolution.
- For cross-layer material, keep the canonical statement at the layer owning the
  primary concern and defer the secondary concern by reference; state carve-outs
  explicitly at the owning layer.

## Node Budget (AD-009)

Three size tiers per node, enforced by `scripts/pb node-size --strict`:

- **Index node** (one per folder/layer, `README.md`): goal ≤40 lines, warning
  50, strict 75; purpose, owns/excludes, a `link → one-line description` table,
  decisions pointer. No rationale or substantive detail.
- **Leaf node**: one concern; goal ≤50 lines, warning 75, strict 100, minimum
  ~10 lines of unique content.
- At or under the goal → silent; over the goal → `info`; over the warning →
  `warn`; over the strict tier → `HARD`, which fails `node-size --strict`
  (exit 1).
- A node can exempt itself from the node budget by declaring `pb_exempt: true`
  in its front matter — the front-matter counterpart to the path-based
  `[nodes] exempt` config list. Reserve it for genuinely long reference
  material; the default remedy is trim → link → split.
- Over strict → **trim** material owned elsewhere, **link** instead of repeat,
  then **split** along a concern seam. Keep exactly one canonical leaf per fact.
- Never split a decision record; tighten it or supersede it.
- A decision record leads with `Context`, `Decision` (dated, past tense), and
  `Rationale`; it never states current state. `Decision` target ≤4 lines (cap 6);
  `Rationale` and `Context` target ≤5 (cap 8). Enforced by
  `scripts/pb check --strict`.
- Name files by role; folder indexes are `README.md`.
- The writing form inside a node is governed by
  [readability-rules.md](readability-rules.md).

## Routing Table

| Type of information | Home |
|---|---|
| Current scope / state / requirements / interfaces | owning layer index + leaves |
| One committed choice, as dated history | `decisions/<PREFIX>-NNN-<slug>.md` |
| Candidate / future change (not yet decided) | `06-evolution/selected/` as an IMP |
| Registry / changelog of decisions (generated) | `decisions/README.md`, `design-choice-log.md` |
| Leaf → decision → artifact links (generated) | `traceability-map.md` |
