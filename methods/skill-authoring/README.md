# Method: skill-authoring

Creates well-scoped, calibrated Agent Skills (SKILL.md bundles) per the
agentskills.io specification and best practices.

Why: skill quality is decided at authoring time. A skill built from real,
domain-specific material, scoped to one coherent unit, and kept under ~500
lines beats a generic one every time — and the validator enforces the spec
rules that otherwise silently break loading (missing description, invalid
name, frontmatter parse failures).

## Contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent entrypoint — the authoring workflow and rules |
| [`references/spec.md`](references/spec.md) | The agentskills.io specification (frontmatter fields, structure, progressive disclosure) |
| [`references/best-practices.md`](references/best-practices.md) | Best practices for skill creators (expertise, context budget, calibration, patterns) |
| [`references/client-implementation.md`](references/client-implementation.md) | How clients discover, disclose, and activate skills |
| [`scripts/validate_skill.py`](scripts/validate_skill.py) | Spec validator — checks frontmatter and naming rules (stdlib-only) |
| [`tests/`](tests/) | Tests for the validator |

## Adopt it

1. Install the skill bundle:
   ```bash
   python3 install.py --method skill-authoring
   python3 install.py --method skill-authoring --into ~/.config/opencode/skills
   ```
2. Ask the agent to "create a skill" for your topic; supply real material
   (runbooks, schemas, corrections from prior sessions) for grounding.
3. Validate every draft before finishing:
   ```bash
   python3 <skills-dir>/skill-authoring/scripts/validate_skill.py <new-skill-dir>
   ```