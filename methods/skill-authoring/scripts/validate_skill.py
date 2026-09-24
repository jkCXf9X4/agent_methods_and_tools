#!/usr/bin/env python3
"""Validate Agent Skills against the agentskills.io specification.

    python3 scripts/validate_skill.py <skill-dir> [<skill-dir> ...]
    python3 scripts/validate_skill.py --lenient <skills-root>

Each path may be a skill directory (contains SKILL.md) or a directory that
contains skill subdirectories (e.g. an installed ``skills/`` tree). Exit code
is 0 when the skill(s) are valid.

Errors violate the specification. Warnings are lenient-compatibility issues
(see client-implementation: some clients warn and load anyway). With
``--lenient`` only errors block a clean exit.

Uses PyYAML when available; otherwise a dependency-light frontmatter parser
that handles ``key: value`` pairs, quoted values, and ``>``/``|`` block
scalars.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
SKILL_FILE = "SKILL.md"

try:
    import yaml  # type: ignore

    def _parse_frontmatter(text: str) -> dict:
        try:
            data = yaml.safe_load(text)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

except ImportError:
    yaml = None

    def _unquote(value: str) -> str:
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            return value[1:-1]
        return value

    def _parse_frontmatter(text: str) -> dict:
        """Minimal YAML-subset parser: flat keys, quoted values, block scalars,
        and a single nested map (for ``metadata``)."""
        entries: dict = {}
        current_key: str | None = None
        mode: str | None = None  # None | block | map
        accumulator: list[str] | None = None
        block_folded = False

        def finalize() -> None:
            nonlocal mode, current_key, accumulator
            if mode == "block" and current_key is not None and accumulator is not None:
                joined = (
                    " ".join(accumulator) if block_folded else "\n".join(accumulator)
                )
                entries[current_key] = joined.strip()
            mode = None
            current_key = None
            accumulator = None

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            if indent == 0:
                finalize()
                if ":" not in line:
                    continue
                key, _, rest = line.partition(":")
                key, rest = key.strip(), rest.strip()
                if rest in (">", "|"):
                    mode = "block"
                    block_folded = rest == ">"
                    current_key = key
                    accumulator = []
                elif rest == "":
                    mode = "map"
                    current_key = key
                    entries[key] = {}
                else:
                    entries[key] = _unquote(rest)
            elif mode == "block" and accumulator is not None:
                accumulator.append(line[indent:])
            elif mode == "map" and current_key is not None and isinstance(
                entries.get(current_key), dict
            ):
                if ":" in line:
                    k, _, v = line.partition(":")
                    entries[current_key][k.strip()] = _unquote(v.strip())
        finalize()
        return entries


def _split_frontmatter(raw: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Empty dict means missing/unparseable."""
    if not raw.startswith("---"):
        return {}, ""
    rest = raw[3:]
    if not rest.startswith("\n"):
        return {}, ""
    rest = rest[1:]
    end = rest.find("\n---")
    if end == -1:
        return {}, ""
    fm_text = rest[:end]
    body = rest[end + 4:]
    if body.startswith("\n"):
        body = body[1:]
    return _parse_frontmatter(fm_text), body


def _is_str(value) -> bool:
    return isinstance(value, str)


def validate_skill(skill_dir: Path, problems: list[tuple[str, str]]) -> None:
    """Append ('error'|'warning', message) tuples to ``problems``."""
    sk_file = skill_dir / SKILL_FILE
    if not sk_file.is_file():
        problems.append(("error", f"{skill_dir}: no {SKILL_FILE}"))
        return

    raw = sk_file.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(raw)

    if not fm:
        problems.append(("error", f"{sk_file}: missing or unparseable YAML frontmatter"))
        return

    name = fm.get("name")
    if not _is_str(name) or name == "":
        problems.append(("error", f"{sk_file}: 'name' is required"))
    else:
        if len(name) > MAX_NAME:
            problems.append(("error", f"{sk_file}: 'name' exceeds {MAX_NAME} chars"))
        if not NAME_RE.match(name):
            problems.append(
                (
                    "error",
                    f"{sk_file}: 'name' must be lowercase a-z0-9 with single hyphens "
                    f"(no leading/trailing/consecutive); got {name!r}",
                )
            )
        if name != skill_dir.name:
            problems.append(
                (
                    "warning",
                    f"{sk_file}: 'name' {name!r} does not match directory "
                    f"{skill_dir.name!r} (clients may warn and still load it)",
                )
            )

    description = fm.get("description")
    if not _is_str(description) or description.strip() == "":
        problems.append(
            (
                "error",
                f"{sk_file}: 'description' is required — skills without one are "
                f"filtered out and never surfaced",
            )
        )
    elif len(description) > MAX_DESCRIPTION:
        problems.append(
            ("error", f"{sk_file}: 'description' exceeds {MAX_DESCRIPTION} chars")
        )

    for field in ("license", "allowed-tools"):
        if field in fm and not _is_str(fm[field]):
            problems.append(("error", f"{sk_file}: '{field}' must be a string"))

    compatibility = fm.get("compatibility")
    if compatibility is not None and (
        not _is_str(compatibility) or len(compatibility) > MAX_COMPATIBILITY
    ):
        problems.append(
            (
                "error",
                f"{sk_file}: 'compatibility' must be a string of at most "
                f"{MAX_COMPATIBILITY} chars",
            )
        )

    metadata = fm.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            problems.append(("error", f"{sk_file}: 'metadata' must be a map"))
        else:
            bad = [
                (k, v) for k, v in metadata.items() if not _is_str(k) or not _is_str(v)
            ]
            if bad:
                problems.append(
                    (
                        "error",
                        f"{sk_file}: 'metadata' values must be strings (got {bad!r})",
                    )
                )

    if body.strip() == "":
        problems.append(
            ("warning", f"{sk_file}: body is empty — a skill should contain instructions")
        )


def discover(path: Path) -> list[Path]:
    if (path / SKILL_FILE).is_file():
        return [path]
    if not path.is_dir():
        return []
    return [d for d in sorted(path.iterdir()) if (d / SKILL_FILE).is_file()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="+", type=Path, help="skill dirs or dirs of skills")
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="exit 0 when only warnings are present (errors still block)",
    )
    args = parser.parse_args(argv)

    problems: list[tuple[str, str]] = []
    seen: set[Path] = set()
    for path in args.paths:
        if not path.exists():
            problems.append(("error", f"{path}: not found"))
            continue
        for skill_dir in discover(path):
            if skill_dir in seen:
                continue
            seen.add(skill_dir)
            validate_skill(skill_dir, problems)

    if not seen:
        problems.append(("error", "no skill directories (containing SKILL.md) found"))

    errors = [m for sev, m in problems if sev == "error"]
    warnings = [m for sev, m in problems if sev == "warning"]

    for message in problems:
        print(f"[{message[0]}] {message[1]}")

    print(f"{len(seen)} skill(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        return 1
    if warnings and not args.lenient:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())