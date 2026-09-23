# Host binding: Dynamic Harness

Tool-vocabulary map for the portable delegation guidelines. The
[`SKILL.md`](../SKILL.md) speaks in behaviors; this file names the Dynamic
Harness tools that realize each behavior.

## Behavior → tool map

| Behavior in SKILL.md | Dynamic Harness tool(s) |
|---|---|---|
| Spawn a sub-agent | `delegate` (with `role`, optional `system_prompt`/`agent_type`) |
| Ask the user | `ask` |
| Read the child's durable-record summary | `read_artifact` (`level="summary"`); see also `status` for the outcome snapshot |
| Push the same child forward | `converse` |
| Abort a stuck/looping child | `kill` (`recursive=true` for a subtree) |
| Read child outcome / partial progress | `status <agent_id>` |
| Read a stored durable record by id | `read_artifact` |
| Persist mid-run findings durably | `archive` (or attach ids at `report`) |
| Self-monitor context/budget | `usage` |
| Drop stale turns / compress context | `prune`, `compress`, `restore` |
| Report / escalate / fail | `report`, `escalate`, `fail` (all terminal) |
| Verify a result on disk | `read` / `bash` (run the repo's own checks) |
| Step decomposition | `plan`; milestone note via `checkpoint` |

## Brief dimensions → fields

The portable brief dimensions map onto first-class fields, not prose:

| Dimension in SKILL.md | Dynamic Harness field |
|---|---|
| scope marker | `role` |
| intent | `delegate(..., intent=...)` / `Task.intent` |
| end state | `delegate(..., end_state=...)` / `Task.end_state` |
| constraints | `delegate(..., constraints=...)` / `Task.constraints` |
| authority | `delegate(..., authority=...)` / `Task.authority` |

The intent fields render as `[INTENT]` / `[END STATE]` / `[CONSTRAINTS]` /
`[AUTHORITY]` blocks baked into the child's system-prompt steerage (the
compression-surviving layer — `context.compress` keeps only the system message).
`end_state` doubles as the acceptance criteria, mirroring the `plan` tool's
`acceptance` parameter.

## Salvage snapshot fields

The abort result / `status` snapshot returns the child's state as concrete
fields: `outcome` (terminal verdict), `summary` (failure reason / result),
`plan` steps marked `done` vs `pending`, and `partial_data` (a bounded tail of
what it was working on). Fold these into the retry brief rather than re-deriving
them.

## Notes on this harness

- The `delegate` result and `status` snapshot surface the child's runtime
  `limits` (token cap / wall-clock) to the parent; the child's own
  system-prompt steerage states its wall-clock budget alongside the `[Budget]`
  token-cap block. Keep those out of the brief's `constraints` — they are
  auto-injected.
- The `[Storage]` line in the `[Environment]` block names the scratch and
  artifact roots; the scratch root is where the eval ledger /
  `progress_report.md` belongs.
- Killed agents are excluded from self-heal — an aborted child is never
  resurrected on its own; the parent decides via `resume`/re-delegation.
- "Compress when the context grows large" maps to DH's concrete triggers:
  `compress` is advised past ~50 messages; `prune` drops stale completed turns.
- The goal-aligned roadmap lives at `product-breakdown/06-evolution/roadmap.md`
  in this project's structure.