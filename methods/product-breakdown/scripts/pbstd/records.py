"""Shared parsing for decision records and markdown sections."""
from __future__ import annotations

import re
from pathlib import Path


def parse_front_matter(text: str) -> tuple[dict | None, str]:
    """Return ``(front_matter, body)``; front matter is ``None`` if absent."""
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, text
    data: dict = {}
    key = None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        head = re.match(r"^([A-Za-z_]+):\s*(.*)$", raw)
        if head:
            key = head.group(1)
            val = head.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                data[key] = [x.strip() for x in inner.split(",") if x.strip()]
            elif val:
                data[key] = val
            else:
                data[key] = []
        else:
            item = re.match(r"^\s*-\s+(.*)$", raw)
            if item and key:
                if not isinstance(data.get(key), list):
                    data[key] = []
                data[key].append(item.group(1).strip())
    return data, "\n".join(lines[end + 1:])


def as_list(value) -> list[str]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def section_body(text: str, name: str) -> list[str] | None:
    match = re.search(r"^## " + re.escape(name) + r"\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if match is None:
        return None
    return [line for line in match.group(1).strip().splitlines() if line.strip()]


def headings(text: str) -> list[str]:
    return re.findall(r"^## (.+?)\s*$", text, re.M)


def read_first_line(path: Path) -> str:
    with path.open(encoding="utf-8") as handle:
        return handle.readline()
