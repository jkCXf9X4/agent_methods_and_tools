---
name: skill-authoring
description: >
  Creates well-scoped, calibrated Agent Skills (SKILL.md bundles) for opencode
  and other clients, per the agentskills.io specification. Use when the user
  asks to "create a skill", "write a skill", "make a skill", "add a method",
  "SKILL.md", or to draft skill instructions, scripts, references, or
  frontmatter. Covers naming/description rules, progressive disclosure,
  instruction patterns, and spec validation.
---

# Skill Authoring

Create or improve an Agent Skill: a directory containing `SKILL.md` plus any
`scripts/`, `references/`, and `assets/`. Follow the agentskills.io
specification, then calibrate the content to the task.

Source documents (summarized here, full detail in `references/`):

- Specification and SKILL.md format: `references/spec.md`
- Best practices for skill creators: `references/best-practices.md`
- How clients load skills (progressive disclosure): `references/client-implementation.md`

## Workflow

### 1. Gather real expertise first

Do not draft from general knowledge. Ground the skill in domain-specific
material the agent would not already know. Ask the user, or extract from:

- A real hands-on task just completed (steps that worked, corrections the user
  made, input/output formats, context the user had to supply).
- Existing project artifacts: runbooks, schemas, API specs, config files, code
  review comments, incident postmortems, git history patches.

Synthesized from the user's own material beats generic "best practices"
prose every time. If the user only gives a topic, ask them what their
conventions, tools, and failure modes actually are.

### 2. Scope to a coherent unit

A skill should encapsulate one coherent unit of work that composes with other
skills. Too narrow: several skills load for one task, risking conflicts. Too
broad: hard to activate precisely. If the unit needs more content than fits in
SKILL.md, keep the core in SKILL.md and push detail to `references/`.

### 3. Create the directory and frontmatter

```
skill-name/
├── SKILL.md          # required: frontmatter + instructions
├── scripts/          # executable code the agent runs
├── references/       # documentation loaded on demand
├── assets/           # templates, schemas, static resources
```

`SKILL.md` = YAML frontmatter (between `---` delimiters) + Markdown body.

Non-negotiable frontmatter rules:

| Field         | Required | Rules                                                                                          |
| ------------- | -------- | ---------------------------------------------------------------------------------------------- |
| `name`        | Yes      | 1-64 chars, lowercase `a-z0-9` and hyphens only, no leading/trailing/consecutive hyphens, MUST equal the parent directory name |
| `description` | Yes      | 1-1024 chars, non-empty. Say what the skill does AND when to use it, third person, front-load trigger keywords |
| `license`     | No       | Short license name or path to a bundled license file                                            |
| `compatibility` | No     | 1-500 chars, only if the skill has environment requirements (tools, packages, network)          |
| `metadata`    | No       | String-to-string map; make keys reasonably unique                                              |
| `allowed-tools` | No     | Space-separated pre-approved tools, e.g. `Bash(git:*) Read` (experimental)                      |

Write `description` to gate the skill precisely: "Use when handling PDFs" is
better than "Helps with PDFs." If the skill must stay quiet on adjacent
topics, start with "Use ONLY when...".

### 4. Write the body for what the agent lacks

Cut anything the agent already knows. For each sentence ask: *"Would the agent
get this wrong without this instruction?"* If no, cut it. Focus on:

- Project/domain conventions, non-obvious edge cases, exact API/tool choices.
- Concrete commands and code, not descriptions of them.

Good:

```
Use pdfplumber for text extraction. For scanned documents, fall back to
pdf2image with pytesseract.
```

Bad (agent already knows this):

```
PDF (Portable Document Format) files are a common format... use a library.
```

### 5. Structure with progressive disclosure

Keep `SKILL.md` under 500 lines / ~5000 tokens. Move detail to separate files
and tell the agent **when** to load each one:

- "Read `references/api-errors.md` if the API returns a non-200 status code."
- "Run `scripts/extract.py` to pull the text."

Never write "see references/ for details" without a trigger. Use relative
paths from the skill root, one level deep.

### 6. Calibrate control per section

Match specificity to fragility:

- **Flexible** (multiple valid approaches): explain why; give the agent freedom.
- **Fragile** (order matters, consistency required): prescriptive, exact
  commands, "do not modify this command."

When several tools could work, pick one default and mention alternatives
briefly. No menus of equal options.

### 7. Teach procedures, not instances

The body should generalize to a class of tasks. 1) Read the schema; 2) join on
the `_id` convention; 3) apply filters from the request — not a specific
query. Specific output templates, constraints, and tool instructions are fine;
the *approach* must generalize.

### 8. Use proven instruction patterns

- **Gotchas**: concrete, environment-specific corrections the agent will get
  wrong without being told (soft deletes, ID naming inconsistencies, health
  endpoints that lie). Highest-value content in most skills.
- **Templates**: show output format as a concrete template; agents pattern-match
  better than against prose. Long templates → `assets/`.
- **Checklists**: for multi-step workflows with dependencies, give a `- [ ]`
  progress checklist.
- **Validation loops**: do the work, run a validator, fix, re-run, proceed only
  when it passes.
- **Plan-validate-execute**: for batch/destructive work, have the agent produce
  an intermediate structured plan, validate it against a source of truth, then
  execute.

### 9. Validate

```bash
python3 scripts/validate_skill.py <skill-dir>
```

Fix errors until it exits 0. The validator checks frontmatter parseability,
name constraints, required fields, and type limits. For full compliance also
try the upstream `skills-ref validate` (see references/spec.md).

### 10. Refine with real execution

Run the skill on a real task. Then feed the results — successes and failures —
back into the process:

- Read execution traces, not just outputs. Wasted steps usually mean
  instructions too vague, non-applicable instructions the agent follows anyway,
  or too many options with no default.
- When you had to correct a mistake, add it to the Gotchas section.
- If the agent re-invents the same logic each run (parsing a format, building a
  chart), bundle it once as a tested `scripts/` file.
- Repeat until it triggers only when relevant and misses nothing important.

## Output checklist

- [ ] `SKILL.md` at the skill root, name matches the directory
- [ ] `description` says what AND when, front-loads trigger keywords
- [ ] Under 500 lines; detail pushed to `references/` with load triggers
- [ ] Paths are relative to the skill root, one level deep
- [ ] Scripts are self-contained, with helpful error messages and edge-case handling
- [ ] Gotchas captured from real corrections
- [ ] `python3 scripts/validate_skill.py <skill-dir>` exits 0

## Gotchas

- `name` must match the parent directory exactly, or clients may warn or skip
  the skill. Check the directory name before editing SKILL.md.
- A skill without a `description` is silently filtered out by opencode and
  never surfaced to the model. Missing description is a hard skip, not a warning.
- Do not rely on an LLM's general knowledge to fill a skill — it produces
  vague, generic procedures. Real material is the whole value.
- `description: Use this skill when: the user asks about X` is technically
  invalid YAML (bare colon). Quote it or use a block scalar (`>`).
- Keep `scripts/` dependency-light: standard library only unless the skill
  explicitly needs more (see this repo's CONTRIBUTING.md).
- Skill content is loaded into the agent's context window. Every token
  competes with the conversation; bloat degrades performance.