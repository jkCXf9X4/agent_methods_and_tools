# Client implementation: adding skills support (agentskills.io/client-implementation/adding-skills-support)

Load this when the task is about how a client/harness *loads* skills — 
discovery, disclosure, activation, context management — or when a skill
fails to load/trigger and you need to reason about the client's behavior.

The core integration is identical regardless of agent architecture; details
vary by where skills live and how the model accesses content.

## The core principle: progressive disclosure

Every skills-compatible agent follows a three-tier loading strategy:

| Tier            | What's loaded               | When                                 | Token cost                  |
| --------------- | --------------------------- | ------------------------------------ | --------------------------- |
| 1. Catalog      | Name + description          | Session start                        | ~50-100 tokens per skill    |
| 2. Instructions | Full `SKILL.md` body        | When the skill is activated          | <5000 tokens (recommended)  |
| 3. Resources    | Scripts, references, assets | When the instructions reference them | Varies                      |

The model sees the catalog from the start. On activation it loads the full
instructions; supporting files load individually as needed. An agent with 20
skills doesn't pay the token cost of all 20 instruction sets upfront.

## Step 1: Discover skills

### Where to scan

Local agents usually scan at least project-level and user-level. Within each
scope, scan both a client-specific directory and the `.agents/skills/`
cross-client convention:

| Scope   | Path                               | Purpose                       |
| ------- | ---------------------------------- | ----------------------------- |
| Project | `<project>/.<your-client>/skills/` | Client's native location      |
| Project | `<project>/.agents/skills/`        | Cross-client interoperability |
| User    | `~/.<your-client>/skills/`         | Client's native location      |
| User    | `~/.agents/skills/`                | Cross-client interoperability |

The spec does not mandate where skill directories live (only what goes inside
them). Some implementations also scan `.claude/skills/`, ancestor directories
up to the git root, XDG config dirs, and user-configured paths.

### What to scan for

Subdirectories containing a file named exactly `SKILL.md`. Skip `.git/`,
`node_modules/`; optionally respect `.gitignore`; set bounds (max depth 4-6,
max ~2000 directories).

### Name collisions

Deterministic precedence: **project-level skills override user-level skills.**
Within the same scope pick first-found or last-found consistently and log a
warning when a skill is shadowed.

### Trust considerations

Project-level skills come from the repo being worked on, which may be
untrusted. Consider gating project-level skill loading on a trust check so
untrusted repos can't silently inject instructions into context.

### Cloud/sandboxed agents

No local filesystem: project-level skills travel with the cloned repo;
user/org-level skills must be provisioned (config repo, skill URLs/packages,
web UI upload); built-in skills ship as static assets.

## Step 2: Parse `SKILL.md`

Find the opening `---` at file start and the closing `---`; parse the YAML
between; the trimmed remainder is the body.

Handle malformed YAML from other clients — most common issue is unquoted
values containing colons:

```yaml
description: Use this skill when: the user asks about PDFs
```

Fallback: wrap such values in quotes or convert to YAML block scalars before
retrying.

### Lenient validation

Warn on issues but load anyway: name doesn't match directory, name > 64 chars.
Hard skip: missing/empty description (essential for disclosure), completely
unparseable YAML. Record diagnostics for surfacing but don't block loading on
cosmetic issues.

### What to store

Per skill: `name`, `description`, `location` (absolute path to `SKILL.md`),
keyed by name in an in-memory map. Store body at discovery time (faster
activation) or read at activation time (less memory, picks up edits). Derive
the base directory (parent of `SKILL.md`) for resolving relative paths and
bundled resources.

## Step 3: Disclose available skills to the model

Tier 1. Include `name`, `description`, and optionally `location` in a
structured format. `location` enables file-read activation and gives the model
a base path for resolving relative references.

### Where to place the catalog

- **System prompt section**: labeled section preceded by brief usage
  instructions. Simplest; works with any model that can read files.
- **Tool description**: embedded in a dedicated activation tool's description.
  Keeps the system prompt clean; couples discovery with activation.

### Behavioral instructions

If the model activates by reading files:

```
The following skills provide specialized instructions for specific tasks.
When a task matches a skill's description, use your file-read tool to load
the SKILL.md at the listed location before proceeding.
When a skill references relative paths, resolve them against the skill's
directory (the parent of SKILL.md) and use absolute paths in tool calls.
```

If via a dedicated tool: "call the activate_skill tool with the skill's name
to load its full instructions."

### Filtering

Hide filtered skills (disabled, permission-denied, opted out) **entirely**
from the catalog rather than listing them and blocking at activation.

### When no skills are available

Omit the catalog and behavioral instructions entirely. Don't show an empty
`<available_skills/>` block or register a skill tool with no options.

## Step 4: Activate skills

Tier 2. Two model-driven patterns:

- **File-read activation**: model calls its standard file-read tool with the
  `SKILL.md` path from the catalog. Simplest when the model has file access.
- **Dedicated tool activation**: `activate_skill(name)` returns the content.
  Required when the model can't read files; useful even when it can. Advantages:
  control returned content (strip frontmatter), wrap in structured tags, list
  bundled resources, enforce permissions, track analytics. Constrain `name` to
  valid skill names (enum) to prevent hallucination; don't register the tool at
  all when no skills exist.

**User-explicit activation**: slash command or mention (`/skill-name`,
`$skill-name`) that the harness intercepts, plus an autocomplete widget.

### What the model receives

- **Full file**: entire `SKILL.md` including frontmatter (frontmatter may carry
  `compatibility` info useful at activation).
- **Body only**: frontmatter stripped after extracting name/description. Most
  common among dedicated-tool implementations.

### Structured wrapping

Wrap skill content in identifying tags (`<skill_content name="...">`), include
the skill directory, note that relative paths are relative to it, and list
bundled resources without eagerly reading them. Benefits: distinguishes skill
content, enables identification during context compaction, surfaces resources.

### Permission allowlisting

If the agent gates file access, allowlist skill directories so bundled
scripts/references load without a permission prompt per file.

## Step 5: Manage skill context over time

- **Protect skill content from context compaction**: exempt skill content from
  pruning/truncation (flag tool outputs as protected, or use structured tags).
  Losing skill instructions mid-conversation silently degrades performance.
- **Deduplicate activations**: skip re-injecting a skill already in context.
- **Subagent delegation** (optional, advanced): run the skill in a separate
  subagent session that returns a summary — good for complex workflows needing
  a focused session.