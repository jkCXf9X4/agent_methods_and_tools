# agent_methods_and_tools

A shared, versioned home for agent **methods**. Each method is a self-contained
**skill bundle**: an agent skill, its guidelines, its templates, and the scripts
that enforce them. Installing a bundle makes the method available in any repo.

Base repository: <https://github.com/jkCXf9X4/agent_methods_and_tools>.

## Layout

```
methods/<name>/          a self-contained skill bundle
  SKILL.md               agent entrypoint
  guidelines/*.md        canonical operating rules
  templates/             config schema and file templates
  scripts/               the method's tools (e.g. `pb`)
  tests/                 tests for the scripts
install.py               installs a method's bundle into a skills directory
```

## Methods

| Method | What it covers |
|---|---|---|
| [product-breakdown](methods/product-breakdown/README.md) | Systems-engineering record: a seven-layer current-state hierarchy plus one flat, dated decision stream, with generated registers |
| [delegation-guidelines](methods/delegation-guidelines/README.md) | Behavioral guidelines — when to delegate, verify, and stop; brief composition with intent/end_state/constraints/authority; salvage-and-retry; stopping conditions; cross-run continuity |
| [mission-command](methods/mission-command/README.md) | Why parent agents brief children with intent, end state, constraints, and freedom of action (uppdragstaktik / mission command) |

## Install

Project-local (the default), into `./.agents/skills/` of the current directory:

```bash
python3 install.py --method product-breakdown
```

Global (available in every repo):

```bash
python3 install.py --method product-breakdown --into ~/.config/opencode/skills
```

Then the agent loads the skill on demand. The method's tool runs from the
installed bundle, for example `python3 <skills-dir>/product-breakdown/scripts/pb check --strict`.

## Add a method

See [CONTRIBUTING.md](CONTRIBUTING.md).
