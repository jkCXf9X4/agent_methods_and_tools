# Example Modelica sources for FMU export

Two tiny example sources used to validate the `fmu_build` toolchain:

- `Hello.mo` — standalone `HelloWorld` model (single file, simplest case).
- `MyLib/package.mo` — package with two models (`MyLib.Bounce`, `MyLib.Springs`) to exercise package loading and multi-model builds.

## Build a single FMU

```bash
python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file Hello.mo --model HelloWorld --output-dir build/fmus
# -> build/fmus/HelloWorld.fmu
```

## Build two FMUs from a package in one invocation

```bash
python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file MyLib/package.mo --model MyLib.Bounce --model MyLib.Springs \
  --output-dir build/fmus
# -> build/fmus/MyLib_Bounce.fmu, build/fmus/MyLib_Springs.fmu
```

## Inspect before building (no omc run)

```bash
python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
  --load-file Hello.mo --model HelloWorld --output-dir build/fmus --dry-run
# writes build/fmus/HelloWorld.mos and prints nothing else
```

Requires `omc` (OpenModelica) on `PATH` for non dry-run builds.

Full flag reference: the skill's `references/build.md`.