# Build: the fmu_build toolchain

The FMU builder is a Python package in the `article_common_artifacts` submodule
under `3rd_party/article_common_artifacts/modelica/fmu_build/`, exposed through
the wrapper `3rd_party/article_common_artifacts/modelica/build_fmu.py`. It never
calls `omc` directly from user code — it generates an `omc` script (`.mos`) per
model and runs `omc <script.mos>` in a working directory.

```bash
# single model
python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file resources/modelica/Delay.mo --model Delay --output-dir build/fmus

# multiple models, one invocation
python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file path/to/package.mo --model MyLib.Controller --model MyLib.Plant

# inspect generated omc scripts without running omc
python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file Hello.mo --model HelloWorld --dry-run

# standalone runner (submodule first, bundled fallback)
bash .opencode/skills/modelica-fmu/scripts/build_fmu.sh \
  --load-file Hello.mo --model HelloWorld --output-dir build/fmus
```

## CLI flags

| Flag | Default | Effect |
| ---- | ------- | ------ |
| `--model NAME` (repeat, required) | — | Fully qualified Modelica class to export; one FMU per model |
| `--load-file PATH` (repeat) | — | `.mo` file or `package.mo` to `loadFile` before building |
| `--output-dir DIR` | `build/fmus` | Where FMUs (and intermediates) are written |
| `--output-name NAME` | — | Explicit FMU filename; **only valid with a single `--model`** |
| `--omc-path CMD` | `omc` | Path to the OpenModelica `omc` executable |
| `--working-dir DIR` | cwd | Working directory `omc` is launched in |
| `--fmi-version V` | `2.0` | FMI version passed to `buildModelFMU` |
| `--fmu-type {cs,me}` | `cs` | Co-simulation (`cs`) or model exchange (`me`) |
| `--platform TAG` (repeat) | `["static"]` | Target platforms; **appends to the default** |
| `--fmi-flag FLAG` (repeat) | `["s:cvode"]` | `--fmiFlags` values; **appends to the default, last wins** |
| `--runtime-depends V` | `all` | `--fmuRuntimeDepends`; `none`/empty strips the option |
| `--modelica-version V` | `4.0.0` | Emits `installPackage(Modelica, V, exactMatch=false)` first |
| `--clean-output-dir` | off | Remove the output dir (once, deduplicated) before building |
| `--dry-run` | off | Write `.mos` scripts only; never invoke `omc` |

Pre-flight validation: `--output-name` with more than one `--model` aborts with
`--output-name can only be used when building a single model.`

## Generated omc script (anatomy)

For `HelloWorld` with defaults, `build/fmus/HelloWorld.mos` is:

```
installPackage(Modelica, "4.0.0", exactMatch=false);
loadFile("/abs/path/Hello.mo");
cd("/abs/path/build/fmus");
setCommandLineOptions("--fmiFlags=s:cvode");
setCommandLineOptions("--fmuRuntimeDepends=all");
filename := OpenModelica.Scripting.buildModelFMU(HelloWorld, version="2.0", fmuType="cs", platforms={"static"});
filename;
getErrorString();
```

Order of statements:

1. `installPackage(Modelica, "<version>", exactMatch=false)` — only when
   `--modelica-version` is set (default). `exactMatch=false` lets omc use the
   bundled MSL version closest to the requested one.
2. `loadFile("...")` per `--load-file` (paths are resolved to absolute).
3. `cd("<output-dir>")` — omc changes into the output directory.
4. `setCommandLineOptions("--fmiFlags=<flag>")` per `--fmi-flag`.
5. `setCommandLineOptions("--fmuRuntimeDepends=<value>")` unless `none`/empty.
6. `buildModelFMU(<model>, version=..., fmuType=..., platforms={...})`.
7. `filename;` and `getErrorString();` so stdout reports the emitted FMU path.

## Outputs and intermediates

For each model the output dir receives the FMU **plus** omc's build
intermediates. Example after exporting `MyLib.Bounce`:

```
build/fmus/MyLib_Bounce.fmu     # final FMU (dotted name -> underscores)
build/fmus/MyLib_Bounce.mos     # generated omc script (kept!)
build/fmus/Bounce.log           # omc transcript
build/fmus/Bounce_info.json     # build meta
build/fmus/Bounce_FMU.makefile  # compiler driver
build/fmus/Bounce_FMU.libs      # linker response file
build/fmus/Bounce_FMU.log       # compile output
build/fmus/index.html           # omc status page
```

Naming notices:

- **Target name** `request.target_path` = `output_dir / (output_name or
  model_name.replace('.', '_') + ".fmu")` — so `MyLib.Bounce` becomes
  `MyLib_Bounce.fmu`.
- omc itself emits the **short-class-name** FMU (`Bounce.fmu`) into the output
  dir first; the builder then renames it to the target (removing a stale target
  if present). Intermediates stay keyed to the short name.
- Intermediate logs/makefiles are never cleaned; a shared output dir across
  models accumulates files keyed by short class name. Use per-project output
  dirs if you want clean separation, or `--clean-output-dir` before a rebuild.

## Error behaviour (blockers)

- `omc executable not found...` — OpenModelica missing; install it or pass
  `--omc-path`.
- `CalledProcessError` payload — omc failed; the message is omc's stderr/stdout.
- `Could not locate FMU emitted for <model>...` — omc completed but no `*.fmu`
  appeared in stdout; check the `.mos` and `<Model>.log` for the real cause
  (wrong model name, unbalanced model, missing class).
- `FMU file <path> missing after omc run...` — locate step succeeded but the
  archive is absent; same investigation applies.

All of these exit non-zero; treat them as blockers.

## Python API (embedding in scripts)

```python
from pathlib import Path
from fmu_build import BuildRequest, build_fmus, build_mos_script, run_omc

req = BuildRequest(
    model_name="MyLib.Bounce",
    output_dir=Path("build/fmus"),
    load_files=(Path("path/to/package.mo"),),
    fmi_flags=("s:cvode",),
)
mos = build_mos_script(req)                 # -> str (no I/O)
stdout, stderr = run_omc("omc", mos, req.mos_path, req.working_dir)
results = build_fmus([req], clean_output_dir=True)  # full pipeline
```

- `BuildRequest` is frozen; `target_path`/`mos_path` are derived properties.
- `build_fmus` runs one `omc` invocation per request, renames short-name FMUs to
  targets, and returns `BuildResult` (request, built_path, target_path, stdout,
  stderr). `dry_run=True` skips omc.
- `clean_output_dir` removes each output dir once across all requests.

## Troubleshooting

- **omc missing** — `which omc`; OpenModelica (≥1.20 works, 1.26.x verified).
  No pip dependencies; plain `python3` + `omc` is the whole stack.
- **Model not found** — check the fully qualified name matches the `model ...`
  inside a loaded `package.mo`; load the package file, not just member files.
- **`installPackage` needs network** — omc falls back to its bundled MSL with
  `exactMatch=false`; if you want to skip MSL entirely, pass an empty
  `--modelica-version`.
- **Wrong solver in the FMU** — remember only the **last** `--fmi-flag` is
  effective; verify with `unzip -p out/Model.fmu resources/*_flags.json` (e.g.
  `{"s":"ls"}`).
- **Stale FMU with old behaviour** — delete the output dir (or pass
  `--clean-output-dir`) and rebuild; intermediates are never auto-removed.
- **More than one platform/flag than expected** — `--platform`/`--fmi-flag`
  *append* to their defaults; duplicates of the same value are harmless.
- **Prefer the local environment** — if a venv/toolchain is present, use it
  (see `AGENTS.md`); the toolchain itself has no pip deps.

## Keeping the bundled copy in sync

The skill bundles a copy so exports work outside the repository. It is a
verbatim copy of `3rd_party/article_common_artifacts/modelica/` (wrapper +
package). Re-sync whenever the submodule version changes:

```bash
SRC=3rd_party/article_common_artifacts/modelica
SKILL=.opencode/skills/modelica-fmu/scripts
cp "$SRC/build_fmu.py"         "$SKILL/build_fmu.py"
rm -rf "$SKILL/fmu_build"
cp -r "$SRC/fmu_build"         "$SKILL/fmu_build"
```

`scripts/build_fmu.sh` uses the repository submodule when it exists and only
falls back to the bundled copy — so in this repo the submodule is always the
authority.