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

## Three surfaces: state, history, tracking

Every fact lands on exactly one of three surfaces. Before writing, name the
category:

| Category | The fact says | Home |
|---|---|---|
| **Current state** | "X is …" — timeless, present tense | owning layer leaf |
| **History** | "On 2026-09-29, X changed …" — dated, immutable | `decisions/` record |
| **Tracking** | "X is open / in progress / done", "N of M remain" | tracker pointer, or the IMP's `status:` |

- A **dated event inside a leaf** is history in the wrong place: a leaf records
  what is, not what happened. "On 2026-09-29 we chose A" belongs in a record;
  the leaf states the outcome — "A is …".
- A **progress marker inside a leaf** is tracking in the wrong place: a leaf
  records the fact, not how far along it is. "3 of 5 done" belongs in the
  tracker; the leaf states the design fact unchanged.
- A leaf's own `status:` (`current` / `draft` / `superseded`) is the leaf's
  lifecycle, never the progress of the work it describes.
- Route by the category, not by where the fact currently sits.

## Trackers are pointers, not hosts

Open items and progress live in a **tracker**: either the IMP's own `status:`
and lifecycle, or a separate tracker file placed beside the leaves (the
`99_open-items.md` pattern — one file at a folder's tail listing open work).
Either way the tracker is a **pointer**:

- A tracker row names the item, its canonical home **by ID**, and its
  open/closed status — nothing else.
- The tracker never **absorbs** the content it points at: no restated facts, no
  dated event log, no progress narrative. If a row is carrying prose, that
  prose has a canonical home; the row points at it instead.
- Watch for the failure mode: a tracker collecting "on 2026-09-29, X happened"
  notes has become a second history; one that restates facts has become a
  second leaf. Both are duplication — cut the absorbed content back to a
  pointer row.

## Ownership and the Boundary Rule

- Route every addition through the boundary rule in the breakdown's top-level
  `README.md`: reason-to-exist → Intent; promised deliverable
  → Product; organizing design → Architecture; files/scripts/interfaces/configs
  → Implementation; proof/acceptance → Verification; routine build/release →
  Operation; future work or risk → Evolution.
- For cross-layer material, keep the canonical statement at the layer owning the
  primary concern and defer the secondary concern **by ID**; state carve-outs
  explicitly at the owning layer.

## Node Budget (AD-009)

Three size tiers per node, enforced by `scripts/pb node-size --strict`:

- **Index node** (one per folder/layer, `README.md`): goal ≤40 lines, warning
  50, strict 75; purpose, owns/excludes, a **generated** `## Contents` list
  (one `[title](leaf) — summary` row per direct child, rebuilt by
  `pb registers --sync-footers` from leaf front-matter), decisions pointer. No
  rationale or substantive detail. The generated list is excluded from the line
  count — the budget governs the hand-written part only.
- **Leaf node**: one concern; goal ≤50 lines, warning 75, strict 100, minimum
  ~10 lines of unique content. Carries the full leaf front-matter block
  (`id`/`type`/`title`/`summary`/`date`/`status` — the generated index reads it
  and shows the id); cites other nodes by ID, never by path link
  ([`templates/LEAF.md`](../templates/LEAF.md), [`frontmatter.md`](frontmatter.md)).
- At or under the goal → silent; over the goal → `info`; over the warning →
  `warn`; over the strict tier → `HARD`, which fails `node-size --strict`
  (exit 1).
- A node can exempt itself from the node budget by declaring `pb_exempt: true`
  in its front matter — the front-matter counterpart to the path-based
  `[nodes] exempt` config list. Reserve it for genuinely long reference
  material; the default remedy is trim → cite → split.
- Over strict → **trim** material owned elsewhere, **cite it by ID** instead of
  repeating it, then **split** along a concern seam. Keep exactly one canonical
  leaf per fact.
- Never split a decision record; tighten it or supersede it.
- A decision record leads with `Context`, `Decision` (dated, past tense), and
  `Rationale`; it never states current state. `Decision` target ≤4 lines (cap 6);
  `Rationale` and `Context` target ≤5 (cap 8). Enforced by
  `scripts/pb check --strict`.
- Name files by role; folder indexes are `README.md`.
- The writing form inside a node is governed by
  [readability-rules.md](readability-rules.md).

## Cite by ID, never by path

- Every live leaf carries a stable, unique `id` in its front-matter
  (`<PREFIX>-<NNN>`, e.g. `INFO-007`). The prefix encodes the **content type**
  (`info`, `eval`; decision records keep their per-layer prefixes), never the
  location, so a file can be moved or renamed without changing its identity.
  The checker guarantees ids are globally unique and that every registered
  `TYPE-NNN` citation in body text resolves to an existing node.
- Hand-written content (leaves and index prose) references other nodes by
  **ID** in backticks (``INFO-007``, ``AD-012``), never by a markdown link to a
  file path. A path appears only in record front-matter (`state:`, `artifacts:`)
  and in generated output (registers, leaf `## Decisions` footers, index
  `## Contents` lists — which show the id of every listed node).
- **Why:** ids are stable and location-free, so moving or renaming a leaf costs
  zero reference edits; `pb registers --sync-footers` re-resolves ids to
  locations on every run, and `pb check` flags any citation that no longer
  resolves.
- **Create / backfill:** `pb new <directory> "<Title>" --summary "..."` scaffolds
  a new leaf with id/type/title/summary/date/status; `pb check --fix` adds the
  missing identity keys to existing leaves while running the checks.
- Enforced by `scripts/pb check --strict`: a live leaf with a markdown link to
  a `.md` file, missing `title`/`summary`, or missing `id`/`type`/`date`/`status`
  is a violation.

## Routing Table

| Type of information | Home |
|---|---|
| Current scope / state / requirements / interfaces | owning layer index + leaves |
| One committed choice, as dated history | `decisions/<PREFIX>-NNN-<slug>.md` |
| Dated event / "on 2026-09-29, we did X" — history | `decisions/` record, never a leaf |
| Open item / progress status ("N of M done") | a tracker pointer, or the IMP's `status:` — never a leaf |
| Candidate / future change (not yet decided) | `06-evolution/selected/` as an IMP |
| Implemented IMP (historical) | `06-evolution/implemented/` — no longer tracked |
| Registry / changelog of decisions (generated) | `decisions/README.md`, `design-choice-log.md` |
| Leaf → decision → artifact links (generated) | `traceability-map.md` |
