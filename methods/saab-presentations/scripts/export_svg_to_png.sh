#!/usr/bin/env bash
# Export SVG figures to PNG for a Saab deck.
#
# Usage:
#   export_svg_to_png.sh [DIR] [--dpi N]
#
# Recursively converts every *.svg under DIR (default: current directory) to a
# sibling *.png, using Inkscape and falling back to ImageMagick `convert`.
# Keep the SVG source next to the PNG; the deck can reference either.
set -euo pipefail

DIR="."
DPI=300

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dpi) DPI="$2"; shift 2 ;;
    -h|--help) echo "Usage: export_svg_to_png.sh [DIR] [--dpi N]"; exit 0 ;;
    *) DIR="$1"; shift ;;
  esac
done

[[ -d "$DIR" ]] || { echo "error: not a directory: $DIR" >&2; exit 1; }

found=0
while IFS= read -r -d '' svg; do
  found=1
  out="${svg%.svg}.png"
  echo "Exporting $svg -> $out"
  if command -v inkscape >/dev/null 2>&1; then
    inkscape --export-type=png --export-dpi="$DPI" --export-filename="$out" "$svg" >/dev/null 2>&1
  else
    convert -background none -density "$DPI" "$svg" "$out"
  fi
done < <(find "$DIR" -type f -name '*.svg' -print0)

[[ $found -eq 1 ]] || echo "No SVG files found under $DIR"
