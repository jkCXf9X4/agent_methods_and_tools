#!/usr/bin/env python3
"""Install a method's skill bundle into a skills directory.

    python3 install.py --method product-breakdown
    python3 install.py --method product-breakdown --into ~/.config/opencode/skills
    python3 install.py --method product-breakdown --dry-run --force

The default target is project-local: ``.agents/skills/<method>/`` under the
current working directory. Pass ``--into`` to install elsewhere, for example a
global ``~/.config/opencode/skills``.

Installation is scoped to the named method's directory only; other skills in
the target directory are never touched.

The installed bundle records a provenance manifest (``.install.json``) listing
each file's checksum, the source commit, and the install time. On reinstall the
script compares the installed tree against that manifest:

- clean   -> replaced without asking (a safe upgrade);
- modified -> locally edited; backed up, then replaced only with ``--force``;
- foreign  -> no manifest, so not from this repo; left alone unless ``--force``.

Use ``--dry-run`` to see what would happen without changing anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_INTO = Path(".agents") / "skills"
MANIFEST = ".install.json"
MANIFEST_ATTRS = ("method", "source", "source_commit", "installed_at", "files")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_checksums(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): sha256_file(p)
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name != MANIFEST
    }


def source_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "unknown"
    if result.returncode == 0:
        return result.stdout.strip()
    return "unknown"


def read_manifest(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not set(MANIFEST_ATTRS).issubset(data):
        return None
    return data


def analyze(dest: Path, src_checksums: dict[str, str]) -> tuple[str, list[str], dict | None]:
    """Return (status, modified_files, manifest).

    status: "absent" | "clean" | "modified" | "foreign"
    """
    if not dest.exists():
        return "absent", [], None

    manifest = read_manifest(dest / MANIFEST)
    if manifest is None:
        return "foreign", [], None

    current = tree_checksums(dest)
    recorded = manifest.get("files", {})
    changed = [rel for rel, ch in current.items() if recorded.get(rel) != ch]
    changed += [rel for rel in recorded if rel not in current]
    changed = sorted(set(changed))
    return ("modified" if changed else "clean"), changed, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", required=True, help="method name under methods/")
    parser.add_argument(
        "--into",
        default=str(DEFAULT_INTO),
        help="skills directory to install into (default: ./.agents/skills)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite a locally modified or foreign bundle",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would happen without changing anything",
    )
    args = parser.parse_args()

    source = ROOT / "methods" / args.method
    if not (source / "SKILL.md").is_file():
        print(f"no skill bundle at {source}")
        return 1

    into = Path(args.into).expanduser()
    if not into.is_absolute():
        into = Path.cwd() / into
    dest = into.resolve() / args.method

    src_checksums = tree_checksums(source)
    status, modified, _ = analyze(dest, src_checksums)

    if status == "absent":
        action = "install"
    elif status == "clean":
        action = "upgrade"
    else:
        action = "overwrite" if args.force else "skip"

    verb = "would" if args.dry_run else "will"
    if status == "absent":
        print(f"{verb} install {args.method} -> {dest}")
    elif status == "clean":
        print(f"{verb} upgrade {args.method} -> {dest} (no local changes)")
    elif status == "modified":
        print(f"{dest} is locally modified ({len(modified)} files):")
        for rel in modified:
            print(f"  {rel}")
        if action == "skip":
            print("not installed; use --force to back up and overwrite")
        else:
            print(f"{verb} back up the existing bundle and overwrite")
    elif status == "foreign":
        print(f"{dest} has no install manifest; not from this repo")
        if action == "skip":
            print("not installed; use --force to back up and overwrite")
        else:
            print(f"{verb} back up the existing directory and overwrite")

    if args.dry_run:
        return 0
    if action == "skip":
        return 1

    if status in ("modified", "foreign"):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = into / f"{args.method}.backup-{stamp}"
        shutil.copytree(dest, backup)
        print(f"backed up -> {backup}")

    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

    manifest_data = {
        "method": args.method,
        "source": ROOT.name,
        "source_commit": source_commit(),
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "files": src_checksums,
    }
    (dest / MANIFEST).write_text(json.dumps(manifest_data, indent=2) + "\n")
    print(f"installed {args.method} -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())