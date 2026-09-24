# Agent Skills specification (agentskills.io/specification)

Full reference for the skill format. Load this when you need exact
constraints on frontmatter fields, directory structure, or validation, beyond
what is stated in SKILL.md.

## Directory structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## SKILL.md format

YAML frontmatter followed by Markdown content.

### Frontmatter fields

| Field           | Required | Constraints                                                                                                       |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.             |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                 |
| `license`       | No       | License name or reference to a bundled license file.                                                              |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata (a map from string keys to string values).                    |
| `allowed-tools` | No       | Space-separated string of pre-approved tools the skill may use. (Experimental)                                    |

Minimal example:

```markdown
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

Example with optional fields:

```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

### `name` field

- Must be 1-64 characters
- May only contain unicode lowercase alphanumeric characters (`a-z`, `0-9`) and
  hyphens (`-`)
- Must not start or end with a hyphen (`-`)
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

Valid: `pdf-processing`, `data-analysis`, `code-review`.
Invalid: `PDF-Processing` (uppercase), `-pdf` (leading hyphen),
`pdf--processing` (consecutive hyphens).

### `description` field

- Must be 1-1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks

Good: "Extracts text and tables from PDF files, fills PDF forms, and merges
multiple PDFs. Use when working with PDF documents or when the user mentions
PDFs, forms, or document extraction."
Poor: "Helps with PDFs."

### `license` field

Optional. Keep short: name of a license or name of a bundled license file.

Example: `license: Proprietary. LICENSE.txt has complete terms`

### `compatibility` field

Optional, 1-500 chars if provided. Only include if the skill has specific
environment requirements.

Examples:
- `compatibility: Designed for Claude Code (or similar products)`
- `compatibility: Requires git, docker, jq, and access to the internet`
- `compatibility: Requires Python 3.14+ and uv`

Most skills do not need this field.

### `metadata` field

Optional map from string keys to string values. Clients can use it for
additional properties not defined by the spec. Make key names reasonably
unique to avoid conflicts.

### `allowed-tools` field

Optional, space-separated string of tools pre-approved to run. Experimental;
support varies between agent implementations.

Example: `allowed-tools: Bash(git:*) Bash(jq:*) Read`

## Body content

The Markdown body after the frontmatter contains the skill instructions. No
format restrictions. Recommended sections: step-by-step instructions, examples
of inputs and outputs, common edge cases.

The agent loads the entire file once the skill is activated. Consider splitting
longer content into referenced files.

## Optional directories

### `scripts/`

Executable code the agent can run. Should be self-contained or document
dependencies, include helpful error messages, and handle edge cases. Supported
languages depend on the agent implementation (commonly Python, Bash,
JavaScript).

### `references/`

Additional documentation read on demand: `REFERENCE.md` for detailed technical
reference, `FORMS.md` for form templates/structured data formats, or
domain-specific files (`finance.md`, `legal.md`). Keep individual files
focused — smaller files cost less context when loaded.

### `assets/`

Static resources: templates, images, data files (lookup tables, schemas).

## Progressive disclosure

Agents load skills progressively:

1. **Metadata** (~100 tokens): `name` and `description` loaded at startup for
   all skills.
2. **Instructions** (< 5000 tokens recommended): the full `SKILL.md` body loaded
   when the skill is activated.
3. **Resources** (as needed): files in `scripts/`, `references/`, or `assets/`
   loaded only when required.

Keep the main `SKILL.md` under 500 lines. Move detailed reference material to
separate files.

## File references

Use relative paths from the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested
reference chains.

## Validation

The upstream reference implementation validates skills:

```bash
skills-ref validate ./my-skill
```

Source: https://github.com/agentskills/agentskills/tree/main/skills-ref
Checks that `SKILL.md` frontmatter is valid and follows all naming conventions.