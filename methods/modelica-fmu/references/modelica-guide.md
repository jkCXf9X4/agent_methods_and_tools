# Modelica for FMU export: practical guide

Background for writing and configuring Modelica models so they export cleanly to
FMI 2.0 FMUs with the `fmu_build` toolchain. Scope: OpenModelica `omc` as the
compiler, and the default settings the toolchain ships with.

## Writing models that export cleanly

`buildModelFMU` accepts a fully qualified, **balanceable** model class. Rules of
thumb that avoid the most common `omc` failures:

- **Balanced equations.** Number of equations must equal number of unknowns in
  every connector/parameter/state. A common minimal skeleton:

  ```modelica
  model Bounce
    Real h(start = 1.0);
    Real v(start = 0.0);
  equation
    der(h) = v;
    der(v) = -9.81;
  end Bounce;
  ```

- **Expose parameters explicitly.** `parameter Real k = 2.0;` becomes an FMU
  scalar with `causality="parameter"` and `variability="fixed"` — tuneable
  before simulation starts in the importing tool.
- **Give states `start` values.** They surface as FMU initial values; without
  them omc may pick defaults you do not intend.
- **Inputs/outputs.** Declare `input Real u;` / `output Real y;` explicitly for
  co-simulation couplings; in `cs` FMUs these become the FMI input/output ports.
- **No `algorithm` sections needed** — plain `equation` sections are fine and
  most predictable for code generation.
- **Dependencies.** Load the whole package (`package.mo`) rather than individual
  member files so `extends`/`replaceable` and cross-references resolve.

## FMI choices

| Choice | Meaning | When |
| ------ | ------- | ---- |
| FMI version `2.0` | Default; the de-facto standard supported across tools | Stick with it |
| `fmuType=cs` (default) | Co-simulation: FMU carries its own solver; master couples step-wise | Coupling models to other tools/solvers |
| `fmuType=me` | Model exchange: FMU exports equations; **importing tool** integrates | Reusing the model in an external solver |
| `platforms={"static"}` (default) | FMU bundles runtime/solver libraries (self-contained archive) | Portable FMU, larger archive |
| platform = OS tag (e.g. `linux64`, `win64`, `darwin64`) | Dynamic linking against system libs | Lean archive for a known host |

`cs` FMUs in this repository are typically packaged into SSP containers
(`resources/*.ssd`) and driven by a co-simulation framework later, so keep the
I/O interface minimal and well-named — those names travel into the SSP.

## Solver and runtime flags

- `--fmi-flag s:cvode` is the default solver (CVODE, good stiff/default choice).
  Use `s:ls` for linear/linearized systems, or other omc solver codes.
- **Only the last `--fmi-flag` is effective.** The script emits one
  `setCommandLineOptions("--fmiFlags=...")` per flag, and omc stores a single
  `--fmiFlags` option — later calls overwrite earlier ones. If you need one
  solver, pass exactly one `--fmi-flag`. Verify the effective solver in the FMU:
  `unzip -p out/Model.fmu resources/*_flags.json` → e.g. `{"s":"ls"}`.
- `--fmuRuntimeDepends=all` (default) records the runtime library dependencies in
  the FMU so importers can pull them; `none`/empty omits the option entirely —
  useful when the target host guarantees the libraries.
- `--platform static` bundles `libsundials_*` and the C runtime into the FMU; the
  `{#platforms}` argument is forwarded verbatim to `buildModelFMU`.

## Validating an FMU

After an export, confirm the archive is structurally valid before consuming it:

```bash
unzip -l build/fmus/MyLib_Bounce.fmu
# must contain (at least):
#   modelDescription.xml
#   binaries/<platform>/...
#   resources/  (solver flags json for cs FMUs)
#   sources/    (OpenModelica always includes the generated sources)
```

In `modelDescription.xml` check `fmiVersion="2.0"`, `modelName`,
`generationTool="OpenModelica Compiler ..."`, the `ScalarVariable`s (parameter
visibility), and — for `cs` — the `CoSimulation` capabilities block.

## Multi-model and multi-platform builds

- Repeat `--model` to export several classes in one invocation; each gets its own
  `omc` run and `.mos` script. Targets are `output_dir/<Dotted.Name>.fmu`.
- Intermediates (logs, makefiles, `index.html`) accumulate in a shared output
  dir and are keyed by *short* class name — either use one output dir per model
  family or `--clean-output-dir` before rebuilds.
- `--output-name` is only allowed for a single `--model`.

## Downstream use

Co-simulation FMUs produced here are FMI 2.0 standard: importable by any FMI 2.0
master/co-simulation tool (e.g. PyFMI, FMPy, or the SSP tooling used elsewhere in
this repository). The FMU interface (parameters, inputs, outputs) is fixed at
export time — re-export and re-package the SSP when you change it.

## Environment

- Full stack is `python3` + `omc`; no pip dependencies. Prefer a local
  environment/venv if one is present in the repo (see `AGENTS.md`).
- `--dry-run` is the cheapest way to inspect exactly what omc will be asked to
  do; use it first when debugging a load or build error.