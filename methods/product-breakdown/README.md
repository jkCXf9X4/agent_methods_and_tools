# Method: product-breakdown

A systems-engineering record that separates **current state** from **history**:

- **Current state** — a seven-layer hierarchy (`00-intent` … `06-evolution`) of
  small leaves, present tense.
- **History** — one flat, dated, immutable decision record per committed choice
  at `decisions/<ID>-<slug>.md`, naming its `state:` leaf.
- **Generated** — the index, changelog, traceability map, leaf footers, and
  each index's `## Contents` list are produced from record/leaf front-matter,
  never hand-edited.

Why: a reader or agent can act on the design without reconstructing a decision
thread, there is exactly one current truth, and hand-maintained registers cannot
drift. Full reasoning: [`guidelines/workflow-rationale.md`](guidelines/workflow-rationale.md).

## Contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent entrypoint |
| [`guidelines/`](guidelines/) | Canonical rules: storage, readability, pipeline, traceability, checklist, deprecation, rationale |
| [`templates/pb.toml`](templates/pb.toml) | Config schema; only needed to override defaults |
| [`templates/TEMPLATE.md`](templates/TEMPLATE.md) | Decision-record template |
| [`templates/LEAF.md`](templates/LEAF.md) | Leaf template: full front-matter block (`id`/`type`/`title`/`summary`/`date`/`status`) + the cite-by-ID rule |
| [`guidelines/frontmatter.md`](guidelines/frontmatter.md) | Front-matter structure: how IDs are displayed and used |
| [`scripts/pb`](scripts/pb) | The tool: `check`, `node-size`, `registers`, `new`, `doctor` |
| [`tests/`](tests/) | Tests for the tool |

## Adopt it

1. Install the skill bundle:
   ```bash
   python3 install.py --method product-breakdown                                  # -> ./.agents/skills/
   python3 install.py --method product-breakdown --into ~/.config/opencode/skills # global
   ```
2. Add a `pb.toml` at the breakdown root **only if** the repo differs from the
   defaults (layers, prefixes, budgets, register paths); otherwise nothing is
   needed — the tool discovers the root from `decisions/`.
3. Wire CI to:
   ```bash
   python3 <skills-dir>/product-breakdown/scripts/pb check --strict
   python3 <skills-dir>/product-breakdown/scripts/pb node-size --strict
   python3 <skills-dir>/product-breakdown/scripts/pb registers --sync-footers   # must produce no diff
   ```
4. Record the adopted version in a decision record.

## Migrate from the older per-layer model

The older model used per-layer `decisions/` folders and hand-maintained
`decision-log.md` / `traceability-map.md`. To migrate:

1. Move every record into `decisions/`, keeping the `<PREFIX>-<NNN>-<slug>`
   filename and adding front-matter (`state:`, `layers:`, `date:`).
2. Point each record's `state:` at the leaf holding its current state, and delete
   the record's `Current Choice` / `Status` / `Layer` sections.
3. Give every leaf the full front-matter block — `id`/`type`/`title`/`summary`/
   `date`/`status`
   ([`templates/LEAF.md`](templates/LEAF.md)); the generated index `## Contents`
   lists and the leaf checks depend on it. `pb check --fix` backfills the
   identity keys (`id`, `type`, `date`, `status`) onto existing leaves; `pb new`
   scaffolds new ones.
4. Replace hand-written path links in leaf bodies with ID citations, and move
   each index's old link table under a `## Contents` heading — the next
   `registers --sync-footers` rebuilds it from front-matter.
5. Delete the hand-maintained registers; regenerate them.
6. Run `check --strict` and `node-size --strict` until clean.
