---
name: Modelica FMU
description: Export Modelica models to FMI 2.0 FMUs with OpenModelica (omc) using the common_article fmu_build toolchain (CLI + Python API, multi-model/multi-platform builds, cs/me types)
---

# Modelica FMU

Reusable instructions for **exporting Modelica models as FMUs** in this
repository. Source of truth is the `article_common_artifacts` submodule
(`3rd_party/article_common_artifacts/modelica/`), which ships a generic FMU
builder backed by OpenModelica's `omc` compiler:

- **CLI** — `build_fmu.py`, a thin wrapper: give it `.mo` files/packages to load
  and one or more fully qualified classes to export; it writes an `omc` script
  per model and invokes `buildModelFMU`.
- **Python API** — `fmu_build` package: `BuildRequest` / `BuildResult`
  dataclasses plus `build_mos_script`, `run_omc`, `build_fmus`, so export logic
  is embeddable in other tooling (e.g. paper build scripts).

## When to use

Use this skill when the task involves:

- Turning Modelica models into FMUs (FMI 2.0) for co-simulation or tool
  exchange — typically to feed SSP/co-simulation setups.
- Writing or preparing Modelica sources (`*.mo`, `package.mo`) for export.
- Choosing FMI/FMU parameters: FMI version, `cs`/`me` type, solver flags,
  target platforms, runtime dependencies.
- Debugging an `omc` run, a missing FMU, or an invalid FMU layout.

## Non-negotiables

1. **Export through the shared entrypoint** — the submodule CLI
   (`3rd_party/article_common_artifacts/modelica/build_fmu.py`) or this skill's
   runner `bash scripts/build_fmu.sh`. Do not hand-write ad-hoc `omc` invocations.
2. **`omc` (OpenModelica) must be installed** — on `PATH` or given via
   `--omc-path`. Without it every non dry-run build fails.
3. **Treat build errors as blockers.** Missing model, unbalanced equations,
   missing MSL package, omc failure — fix before moving on. `.mos` scripts and
   logs in the output dir are the first place to look.
4. **FMUs and intermediate artifacts are generated** — never commit `.fmu`
   archives; keep the `.mo` sources as the editable source of truth. Outputs go
   to `--output-dir` (default `build/fmus/`), which is already git-ignored.
5. **Know the append-with-default gotcha:** `--fmi-flag` and `--platform` append
   to built-in defaults (`s:cvode`, `static`) instead of replacing them, and of
   repeated `--fmi-flag` values **only the last one is effective** in omc.
   See *Solver & platform flags* below.
6. **Dry-run first when reasoning about scripts:** `--dry-run` writes the `.mos`
   files without invoking `omc` — cheap and safe.

## Toolchain

| Item | Value |
| ---- | ----- |
| Build entrypoint (repo) | `python3 3rd_party/article_common_artifacts/modelica/build_fmu.py` |
| Standalone runner (skill) | `bash scripts/build_fmu.sh` |
| Library | OpenModelica `omc` (`buildModelFMU`), verified against 1.26.x |
| Output dir | `--output-dir` (default `build/fmus`) |
| FMI version / type | default `2.0` / `cs` |
| Platforms | `--platform` (repeatable; default `static` = bundled runtime libs) |
| Solver flags | `--fmi-flag s:cvode` default; last provided flag wins |
| Requirements | `python3`, `omc` (OpenModelica); no pip dependencies |

Basic usage (run from the repository root):

```bash
python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file resources/modelica/Delay.mo --model Delay --output-dir build/fmus

python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file path/to/package.mo --model MyLibrary.Controller --model MyLibrary.Plant
```

### Standalone use (bundled resources)

The skill bundles everything needed to export FMUs without the submodule:

| Resource | Purpose |
| -------- | ------- |
| `scripts/build_fmu.py` | Copy of the CLI wrapper |
| `scripts/fmu_build/` | Copy of the toolchain package (builder + cli) |
| `scripts/build_fmu.sh` | Runner that prefers the repo submodule, falls back to the bundled copy |
| `templates/example/` | Minimal `.mo` sources (single model + package) for quick validation |

```bash
SKILL=.opencode/skills/modelica-fmu
bash "$SKILL/scripts/build_fmu.sh" \
  --load-file "$SKILL/templates/example/Hello.mo" \
  --model HelloWorld --output-dir build/fmus
```

## Workflow

1. **Prepare Modelica sources.** Balanced, exportable classes in `*.mo` files or
   `package.mo` packages. Declare parameters you want exposed as FMU tunables;
   give `start` values to states. Tips: `references/modelica-guide.md`.
2. **Decide FMU parameters.** FMI version (`2.0` default), type (`cs` default,
   `me` for tool exchange), platforms, solver flags, `--modelica-version` and
   runtime deps only if you need to change them.
3. **Export.** One or many `--model` flags; `--load-file` as many sources as the
   model needs (package before referenced classes). Verify the requested target
   path is printed, e.g. `Exporting MyLib.Bounce -> build/fmus/MyLib_Bounce.fmu`.
4. **Verify the FMU.** It must be a valid FMI 2.0 zip: `unzip -l out/Model.fmu`
   shows `modelDescription.xml`, `binaries/<platform>/`, `resources/`. See
   *Validating an FMU* in `references/build.md`.
5. **Feed downstream.** Co-simulation (`cs`) FMUs plug into FMI 2.0 master
   algorithms; in this repo they typically end up inside SSP containers
   (`resources/*.ssd`).

## Reference files

- `references/build.md` — CLI flags, Python API, generated `.mos` script anatomy, outputs and intermediates, error behaviour, troubleshooting, how to re-sync the bundled copy.
- `references/modelica-guide.md` — writing Modelica for export, FMI `cs` vs `me`, solver/platform flags, validating FMUs, downstream use.
- `scripts/build_fmu.sh` — standalone export runner (submodule first, bundled fallback).
- `scripts/build_fmu.py`, `scripts/fmu_build/` — bundled copies of the toolchain.
- `templates/example/` — minimal working `.mo` sources with build commands.