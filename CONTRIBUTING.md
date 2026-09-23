# Contributing

This repo holds multiple methods. Each method is a **self-contained skill
bundle**: it must install and work on its own, with no dependency on another
method or on a specific consuming repository.

## Add a method

Create `methods/<name>/` with:

- `SKILL.md` — the opencode skill: YAML front-matter (`name` must equal the
  directory name, plus `description`) and the agent instructions.
- `guidelines/*.md` — the canonical rules; one concern per file. The skill
  references these by relative path.
- `templates/` — any config schema or file templates the method uses.
- `scripts/` — the method's tools, runnable from the bundle (`python3 scripts/<tool> …`).
  Keep them dependency-light: standard library, plus `tomli` on Python < 3.11.
- `tests/` — a `conftest.py` that adds `scripts/` to `sys.path`, plus the tests.

Then add a row to the methods table in the root `README.md`.

## Keep a bundle portable

- Resolve paths relative to the skill's base directory, never to a fixed repo.
- A method must not assume a consuming repo's layout; discover it (for example
  from a `pb.toml` or a `decisions/` folder) or accept a `--root` flag.
- Guideline links: reference sibling files relatively; refer to consuming-repo
  paths as code spans (for example `` `decisions/TEMPLATE.md` ``), never as links
  into a specific repo.

## Verify

```bash
python3 -m pytest methods/<name>/tests -q
python3 install.py --method <name> --into /tmp/skills-check
```

## Versioning

A consuming repo records the version it installed and pins it. The method's
`SKILL.md` and guidelines are the versioned surface.
