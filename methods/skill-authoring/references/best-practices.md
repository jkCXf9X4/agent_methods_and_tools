# Best practices for skill creators (agentskills.io/skill-creation/best-practices)

Load this when a skill draft feels generic, too verbose, or the agent's
execution wastes steps. It covers grounding in real expertise, context
budgeting, calibration, and instruction patterns.

## Start from real expertise

A common pitfall is asking an LLM to generate a skill without domain-specific
context, producing vague generic procedures instead of the specific API
patterns, edge cases, and conventions that make a skill valuable.

### Extract from a hands-on task

Complete a real task in conversation with an agent, providing context,
corrections, and preferences. Then extract the reusable pattern. Pay attention
to:

- **Steps that worked** — the sequence of actions that led to success
- **Corrections you made** — where you steered the agent's approach
- **Input/output formats** — what the data looked like going in and coming out
- **Context you provided** — project-specific facts, conventions, or constraints

### Synthesize from existing project artifacts

Feed a body of existing knowledge into the LLM to synthesize a skill.
Project-specific material (runbooks, schemas, failure modes, recovery
procedures) outperforms generic articles. Good source material:

- Internal documentation, runbooks, and style guides
- API specifications, schemas, and configuration files
- Code review comments and issue trackers
- Version control history, especially patches and fixes
- Real-world failure cases and their resolutions

## Refine with real execution

The first draft needs refinement. Run the skill against real tasks, then feed
the results (all of them, not just failures) back into the process. Ask: what
triggered false positives? What was missed? What could be cut?

Read agent execution traces, not just final outputs. If the agent wastes time,
common causes: instructions too vague (several approaches tried), instructions
that don't apply to the current task, or too many options without a clear
default.

## Spending context wisely

Once a skill activates, its full body loads into the context window alongside
conversation history and other active skills. Every token competes for
attention.

### Add what the agent lacks, omit what it knows

Focus on what the agent *wouldn't* know without your skill: project-specific
conventions, domain-specific procedures, non-obvious edge cases, particular
tools/APIs. Don't explain what a PDF is, how HTTP works, or what a migration
does. Ask per piece: "Would the agent get this wrong without this instruction?"
If no, cut it. If unsure, test it.

### Design coherent units

Like a function: encapsulate a coherent unit of work that composes well. Too
narrow → multiple skills load for one task (overhead, conflicting
instructions). Too broad → hard to activate precisely.

### Aim for moderate detail

Concise, stepwise guidance with a working example outperforms exhaustive
documentation. Covering every edge case makes the agent struggle to extract
what's relevant and pursue unproductive paths.

### Structure large skills with progressive disclosure

Keep `SKILL.md` under 500 lines / 5,000 tokens — just the core instructions
needed on every run. Move detail to `references/` or similar. Tell the agent
*when* to load each file: "Read `references/api-errors.md` if the API returns
a non-200 status code" beats "see references/ for details."

## Calibrating control

Match the specificity of instructions to the fragility of the task.

### Match specificity to fragility

**Give freedom** when multiple approaches are valid and the task tolerates
variation; explaining *why* helps the agent make context-dependent decisions.

**Be prescriptive** when operations are fragile, consistency matters, or a
specific sequence must be followed — exact commands, "do not modify this
command or add flags."

### Provide defaults, not menus

Pick a default and mention alternatives briefly rather than presenting them as
equal options. "Use pdfplumber; for scanned PDFs requiring OCR, use pdf2image
with pytesseract instead" — not a four-library menu.

### Favor procedures over declarations

Teach *how to approach* a class of problems, not *what to produce* for one
instance. The approach should generalize even when individual details are
specific. Output format templates, constraints like "never output PII," and
tool-specific instructions are all still valuable.

## Patterns for effective instructions

### Gotchas sections

Highest-value content: environment-specific facts that defy reasonable
assumptions. Concrete corrections to mistakes the agent will make without
being told. Example:

```markdown
## Gotchas

- The `users` table uses soft deletes. Queries must include
  `WHERE deleted_at IS NULL` or results will include deactivated accounts.
- The user ID is `user_id` in the database, `uid` in the auth service,
  and `accountId` in the billing API. All three refer to the same value.
- The `/health` endpoint returns 200 as long as the web server is running,
  even if the database connection is down. Use `/ready` to check full
  service health.
```

Keep gotchas in `SKILL.md` where the agent reads them before encountering the
situation. When an agent makes a mistake you correct, add the correction to
the gotchas — one of the most direct ways to improve a skill.

### Templates for output format

Provide a template rather than describing the format in prose. Short templates
inline; long or rare ones in `assets/` referenced from `SKILL.md`.

### Checklists for multi-step workflows

Explicit `- [ ]` checklists help the agent track progress and avoid skipping
steps, especially with dependencies or validation gates.

### Validation loops

Do the work, run a validator (script, reference checklist, or self-check), fix
issues, repeat until validation passes, then proceed.

### Plan-validate-execute

For batch or destructive operations: create an intermediate plan in a
structured format, validate it against a source of truth, then execute. The
validation script that checks the plan against the source of truth is the key
ingredient — its errors give the agent enough information to self-correct.

### Bundling reusable scripts

If the agent independently reinvents the same logic each run (charts, parsing,
validation), write a tested script once and bundle it in `scripts/`.

## Next steps

- **Evaluating skill output quality** — set up test cases, grade results,
  iterate systematically.
- **Optimizing skill descriptions** — test and improve the `description` so it
  triggers on the right prompts.