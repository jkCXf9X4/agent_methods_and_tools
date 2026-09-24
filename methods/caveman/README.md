# Method: caveman

An ultra-compressed communication mode that cuts output tokens while keeping
technical accuracy. Levels: lite, full, ultra.

Why: response style is a per-session preference, not a host capability. Keeping
it as a loadable skill lets any agent apply the compression rules on demand
without re-deriving them, and keeps the style from drifting into filler on long
sessions.

## Contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent entrypoint — compression rules, intensity levels, auto-clarity, boundaries |

## Adopt it

1. Install the skill bundle:
   ```bash
   python3 install.py --method caveman
   python3 install.py --method caveman --into ~/.config/opencode/skills
   ```
2. The skill is host-agnostic: it compresses style, never the language, and
   leaves code, technical terms, and error strings untouched. No host binding is
   required.