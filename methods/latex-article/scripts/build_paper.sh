#!/usr/bin/env bash
# Standalone LaTeX article build using this skill's bundled common_article
# toolchain (falls back to the repository submodule when present).
#
#   bash scripts/build_paper.sh                     # build ./main.tex
#   bash scripts/build_paper.sh --tex paper/main.tex
#   bash scripts/build_paper.sh --tex main.tex --release
#   bash scripts/build_paper.sh --tex main.tex --release-tag v2
#
# It mirrors the repository's top-level `build.py`: put the latex_build package
# on PYTHONPATH and delegate to `latex_build.cli`.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Locate the toolchain: repository submodule wins; bundled copy is the fallback.
REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
SUBMODULE_SCRIPTS="$REPO_ROOT/3rd_party/article_common_artifacts/latex/scripts"
BUNDLED_SCRIPTS="$SKILL_DIR/scripts"

if [[ -d "$SUBMODULE_SCRIPTS/latex_build" ]]; then
  SCRIPTS_DIR="$SUBMODULE_SCRIPTS"
  : # repo submodule in use
elif [[ -d "$BUNDLED_SCRIPTS/latex_build" ]]; then
  SCRIPTS_DIR="$BUNDLED_SCRIPTS"
  : # bundled copy in use
else
  echo "error: latex_build toolchain not found (submodule nor bundled copy)" >&2
  echo "  looked in: $SUBMODULE_SCRIPTS" >&2
  echo "  and in:    $BUNDLED_SCRIPTS" >&2
  exit 1
fi

PYTHONPATH="$SCRIPTS_DIR${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -m latex_build.cli "$@"