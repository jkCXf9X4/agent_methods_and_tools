#!/usr/bin/env bash
# Standalone Modelica -> FMU export using this skill's bundled fmu_build
# toolchain (prefers the repository submodule when present).
#
#   bash scripts/build_fmu.sh --load-file Hello.mo --model HelloWorld
#   bash scripts/build_fmu.sh --load-file src/package.mo --model MyLib.Controller \
#                             --model MyLib.Plant --output-dir build/fmus
#   bash scripts/build_fmu.sh --load-file src/Delay.mo --model Delay \
#                             --output-name Delay_cs \
#                             --fmu-type cs --fmi-flag s:cvode --dry-run
#
# It delegates to `build_fmu.py` (the fmu_build CLI wrapper): the repository
# submodule copy wins, the bundled copy is the fallback. All flags are passed
# through unchanged; see `references/build.md` for the full flag list.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
SUBMODULE_MODELICA="$REPO_ROOT/3rd_party/article_common_artifacts/modelica"
BUNDLED_WRAPPER="$SKILL_DIR/scripts/build_fmu.py"

if [[ -f "$SUBMODULE_MODELICA/build_fmu.py" && -d "$SUBMODULE_MODELICA/fmu_build" ]]; then
  WRAPPER="$SUBMODULE_MODELICA/build_fmu.py"
  : # repo submodule in use
elif [[ -f "$BUNDLED_WRAPPER" && -d "$SKILL_DIR/scripts/fmu_build" ]]; then
  WRAPPER="$BUNDLED_WRAPPER"
  : # bundled copy in use
else
  echo "error: fmu_build toolchain not found (submodule nor bundled copy)" >&2
  echo "  looked in: $SUBMODULE_MODELICA" >&2
  echo "  and in:    $SKILL_DIR/scripts" >&2
  exit 1
fi

# `build_fmu.py` puts its own directory on sys.path so `fmu_build` resolves
# next to it, no PYTHONPATH fiddling needed.
python3 "$WRAPPER" "$@"