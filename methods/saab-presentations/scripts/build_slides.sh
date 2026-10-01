#!/usr/bin/env bash
# Standalone Marp build for Saab decks using this skill's bundled theme.
#
# Usage:
#   build_slides.sh <deck.md | deck-dir> [--pdf | --pptx | --both]
#                   [--theme FILE] [--out FILE]
#
# The deck path may be a Markdown file or a directory containing
# `slides.marp.md` or `slides.md`. By default a PDF is written next to the
# source deck. The bundled theme at assets/theme/saab-theme.css is self-contained
# (logo and cover inlined as data URIs), so no sibling `themes/` directory or
# submodule is required.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

THEME="$SKILL_DIR/assets/theme/saab-theme.css"
MODE="pdf"
OUT=""
DECK=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pdf)   MODE="pdf"; shift ;;
    --pptx)  MODE="pptx"; shift ;;
    --both)  MODE="both"; shift ;;
    --theme) THEME="$2"; shift 2 ;;
    --out)   OUT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "error: unknown option $1" >&2; exit 1 ;;
    *) DECK="$1"; shift ;;
  esac
done

if [[ -z "$DECK" ]]; then
  echo "error: no deck given (see --help)" >&2
  exit 1
fi

# Resolve a directory to its deck file.
if [[ -d "$DECK" ]]; then
  if   [[ -f "$DECK/slides.marp.md" ]]; then DECK="$DECK/slides.marp.md"
  elif [[ -f "$DECK/slides.md" ]];      then DECK="$DECK/slides.md"
  else echo "error: no slides.marp.md or slides.md in $DECK" >&2; exit 1
  fi
fi

[[ -f "$DECK" ]] || { echo "error: deck not found: $DECK" >&2; exit 1; }
[[ -f "$THEME" ]] || { echo "error: theme not found: $THEME" >&2; exit 1; }

command -v marp >/dev/null || { echo "error: marp CLI not found (https://marp.app)" >&2; exit 1; }

DECK_DIR="$(cd "$(dirname "$DECK")" && pwd)"
DECK_BASE="$(basename "$DECK")"
DECK_BASE="${DECK_BASE%.*}"

run() {  # run <pdf|pptx> <outfile>
  local fmt="$1" out="$2"
  echo "Building ${fmt^^} ($DECK)…"
  marp "$DECK" --theme "$THEME" --allow-local-files --"$fmt" -o "$out"
  echo "  wrote $out"
}

case "$MODE" in
  pdf)  run pdf  "${OUT:-$DECK_DIR/$DECK_BASE.pdf}" ;;
  pptx) run pptx "${OUT:-$DECK_DIR/$DECK_BASE.pptx}" ;;
  both)
    run pdf  "${OUT:-$DECK_DIR/$DECK_BASE.pdf}"
    run pptx "${OUT:-$DECK_DIR/$DECK_BASE.pptx}"
    ;;
esac
