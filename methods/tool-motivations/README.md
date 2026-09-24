# Method: tool-motivations

What each tool category is for and why, and how to choose between them.

Why: the optimized system prompt lists tools with terse guidance. When the
motivation behind a tool — or when to prefer it over a sibling — is compressed
away, this bundle recovers the full reasoning.

## Contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent entrypoint — portable tool doctrine, tool-agnostic |
| [`guidelines/host-dynamic-harness.md`](guidelines/host-dynamic-harness.md) | Behavior → tool map for the Dynamic Harness host |

## Adopt it

1. Install the skill bundle:
   ```bash
   python3 install.py --method tool-motivations
   python3 install.py --method tool-motivations --into ~/.config/opencode/skills
   ```
2. For a non-Dynamic-Harness host, add a `guidelines/host-<your-harness>.md`
   mapping the portable behaviors to that host's tools (or skip it and let the
   model resolve the behaviors against its own toolset).