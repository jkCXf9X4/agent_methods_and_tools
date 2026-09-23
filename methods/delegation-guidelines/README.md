# Method: delegation-guidelines

Behavioral guidelines for running a tree of delegated agents: when to delegate,
verify, and stop; brief composition with intent / end_state / constraints /
authority; salvage-and-retry; stopping conditions; cross-run continuity.

Why: the system prompt is optimized for tokens, so a guideline's nuance gets
compressed away. This bundle is the recoverable, canonical statement of the
reasoning the prompt is optimized from.

## Contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent entrypoint — portable doctrine, tool-agnostic |
| [`guidelines/host-dynamic-harness.md`](guidelines/host-dynamic-harness.md) | Behavior → tool map for the Dynamic Harness host |

## Adopt it

1. Install the skill bundle:
   ```bash
   python3 install.py --method delegation-guidelines
   python3 install.py --method delegation-guidelines --into ~/.config/opencode/skills
   ```
2. For a non-Dynamic-Harness host, add a `guidelines/host-<your-harness>.md`
   mapping the portable behaviors to that host's tools (or skip it and let the
   model resolve the behaviors against its own toolset).
3. The sibling `mission-command` method explains *why* the intent fields exist;
   install it alongside if brief composition matters to your workload.