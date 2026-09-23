# Method: mission-command

Why parent agents brief delegated children with intent, end state, constraints,
and freedom of action (uppdragstaktik / mission command).

Why: a mission without intent is exactly the case where a subordinate cannot
make correct autonomous decisions. This bundle is the durable rationale for the
intent dimension of a delegation brief, kept separate from the optimized prompt.

## Contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent entrypoint — portable doctrine, tool-agnostic |
| [`guidelines/host-dynamic-harness.md`](guidelines/host-dynamic-harness.md) | Doctrine → field/prompt/policy wiring for the Dynamic Harness host |

## Adopt it

1. Install the skill bundle:
   ```bash
   python3 install.py --method mission-command
   python3 install.py --method mission-command --into ~/.config/opencode/skills
   ```
2. For a non-Dynamic-Harness host, apply the doctrine through your own
   delegation fields (or add a `guidelines/host-<your-harness>.md` mapping).
3. The sibling `delegation-guidelines` method turns this rationale into
   executable brief-composition rules; install it alongside.