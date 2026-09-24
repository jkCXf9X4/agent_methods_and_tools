# Host binding: Dynamic Harness

Tool-vocabulary map for the portable tool motivations. The
[`SKILL.md`](../SKILL.md) speaks in behaviors and categories; this file names the
Dynamic Harness tools that realize each.

## Behavior → tool map

| Behavior in SKILL.md | Dynamic Harness tool |
|---|---|
| Enumerate files | `glob` |
| Search file contents | `grep` (`include` filters by extension) |
| Consume a known file | `read` (`token_limit`/`token_offset` page large files) |
| Persist a finding | `write` |
| Surgical in-place replacement (first match) | `edit` |
| Run commands / builds / tests / git | `bash` (raw executor — no pipes/redirects/`&&`) |
| Fetch external content | `webfetch` (no localhost/private ranges) |
| Spawn a sub-agent | `delegate` |
| Push an existing worker forward | `converse` |
| Read live status / partial progress | `status` (outcome, summary, plan done/pending, `partial_data`) |
| Abort a worker | `kill` (`recursive=true` for a subtree; result embeds `salvage`) |
| Read a stored record by id | `read_artifact` (headline → summary → technical) |
| Persist mid-run findings durably | `archive` (or attach ids at `report`) |
| Self-monitor context/budget | `usage` |
| Compress context | `compress` (advised past ~50 messages) |
| Drop stale turns | `prune` |
| Restore a dropped turn | `restore` |
| Report / escalate / fail | `report`, `escalate`, `fail` (all terminal) |

## Choosing rules → concrete pairs

| Rule in SKILL.md | Dynamic Harness pair |
|---|---|
| search vs consume | `grep` vs `read` |
| enumerate vs search | `glob` vs `grep` |
| surgical edit vs full write | `edit` vs `write` |
| delegate vs do-it-yourself | `delegate` vs in-context work (0–1 calls on a known target) |
| verify vs trust | verify the artifact on disk (`read_artifact`) over the return summary |
| push vs re-spawn | `converse` (same child) vs `kill` + re-`delegate` (fresh worker) |
| status vs record read | `status` (how the run went) vs `read_artifact` (the content it produced) |
| archive vs write | `archive` (durable, id-addressed, provenance-linked) vs `write` (scratch/cursor) |

## Notes on this harness

- `bash` is a raw command executor, not a shell: no pipes, redirects, or `&&`.
  Run one command per call; use `result_bash` to pipe a cached result to a
  command's stdin instead of re-running the producing tool.
- `kill` is parent-side only: it cancels a child's in-flight run (authored
  artifacts/commits are preserved) and marks it failed. Killed agents are
  excluded from self-heal — never resurrected on their own.
- `status` returns the child's `limits` (token cap / wall-clock) alongside the
  outcome snapshot, so the parent knows the real constraints without re-reading
  the brief.
- The `[Storage]` line in the `[Environment]` block names the scratch and
  artifact roots; scratch files belong under the scratch root and are deleted
  after archiving.
- The runtime only auto-creates an artifact at `report()`; `archive` is how
  mid-run findings stay discoverable before then.