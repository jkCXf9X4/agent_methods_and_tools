# Host binding: Dynamic Harness

How this doctrine maps onto the Dynamic Harness runtime. Host-specific — other
harnesses apply the same doctrine through their own field names and wiring. See
[`SKILL.md`](../SKILL.md) for the host-agnostic doctrine.

## Mapping doctrine → Dynamic Harness today

The parent → child brief is built from the `delegate` tool's `description` +
`role` (+ optional `system_prompt`, `agent_type`, `metadata`). The system
prompt's BRIEF line compresses this to: *"description+role; specific
paths/functions/behavior; outcome not process; verification; disk artifact;
acceptance criteria; one task per delegation."*

| Doctrine element | Current analog | Status |
|---|---|---|
| Uppgift (mission) | `description` | Present |
| Syfte (purpose) | Only implicit inside `description` | Missing as a structure |
| Målbild (end state) | "Acceptance criteria" — prose advice in the BRIEF rule | Advice only, not a first-class field |
| Genomförandeidé (concept) | Nothing | Missing |
| Ramar (constraints) | `role` (soft scope); `delegate` result / `status` surface the child's runtime limits (token cap / wall-clock); hard enforcement remains in the safety system | Communicated to the parent; the child's own brief still lists them only if the parent writes them |
| Handlingsfrihet (freedom of action) | "Outcome not process" in the BRIEF rule | Implicit only — no explicit mandate to adapt |
| Authority to deviate | `escalate`/`fail` exist, but deviation is not framed as authorized | Missing |
| Trust → verify | "Never synthesize from assumed results"; verify by artifact | Tension with doctrine |

## Implemented wiring

Implemented status is noted per item (see `core/task.py`, `core/prompts.py`,
`core/tools/agents.py` for the live wiring).

1. **Structured intent block.** The `delegate` tool (and `Task`) carry a compact
   intent carrier — purpose, end state, constraints, and the license to adapt —
   rendered into the child's context. `Task` carries
   `intent`/`end_state`/`constraints`/`authority`; `delegate`'s
   `intent`/`end_state`/`constraints`/`authority` fields render as
   `[INTENT]` / `[END STATE]` / `[CONSTRAINTS]` / `[AUTHORITY]` blocks baked
   into the child's **system prompt steerage** (`Agent._build_steerage`) — the
   compression-surviving, cache-friendly layer, since `context.compress` keeps
   only the system message and erases the user message.
2. **Acceptance as contract, not advice.** "Done looks like X" is a stated
   field the child verifies against and the parent re-verifies against —
   mirroring the `plan` tool's `acceptance` parameter. Covered by `end_state`:
   the parent states the desired final condition explicitly, and the child
   steers toward it when the path changes.
3. **Mandate to adapt + report back.** Explicitly: *if the situation changes,
   deviate as needed to honor the intent; report the deviation and why in your
   report/escalate.* This turns the child's two bad exits (plow ahead / fail)
   into a third, aligned one. Implemented via the `authority` field.
4. **Communicate the ramar up front.** The child's own hard limits (token
   budget, timeouts, delegation caps) are surfaced as constraints in the brief,
   not as surprises the safety system reveals on violation. The `delegate`
   result and `status` snapshot carry the child's `limits` (token cap /
   wall-clock) for the parent; and the child's own system-prompt steerage states
   its wall-clock budget (`_build_steerage`) alongside the existing `[Budget]`
   token-cap block, so both sides see the real ramar up front.
5. **Verify against intent, not plan-adherence.** The parent's VERIFY step
   checks the artifact "matches the requirement"; the requirement is the *end
   state*, not whether the child followed the original plan. Prompt-level
   guidance (see the VERIFY rule): non-empty + satisfies the `end_state` you
   briefed.
6. **Observe brief completeness, don't just hope for it.** Prompt guidance
   alone lets a parent delegate WHAT without WHY. `core/policies/brief.py`
   (`BriefPolicy`) is a `ReactivePolicy` registered on every agent (default
   `safety.brief_nudge_attempts: 1`): it watches `delegate` calls in the
   post-turn observation and injects a budgeted notice naming the missing
   `intent`/`end_state` dimension(s). Host-agnostic — a plugin host can
   register/replace/rephrase it through the reactive-policy seam without
   touching the run loop.