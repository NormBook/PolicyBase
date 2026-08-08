#!/usr/bin/env python3
"""Verify PolicyBase seed volume content lint."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER_FIELDS = ("状态", "分卷编号", "主题", "重构日期", "仓库")
FORBIDDEN_FRONTMATTER_FIELDS = ("适用 generation",)
LEGACY_PB_CITATION_RE = re.compile(r"(?:见\s*|来源于\s*)PB\d{2}(?:\s*§|\.md\b|\b)")
TODO_MARKER_RE = re.compile(r"\b(?:TODO|FIXME)\b\s*:|<TBD>|\bXXX\b")
POLICYBASE_REF_RE = re.compile(r"PolicyBase_(\d{2})")
VOLUME_FILE_RE = re.compile(r"^PolicyBase_(\d{2})\.md$")


def fail(message: str) -> None:
    print(f"ERROR seed_set_invalid: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def discover_volumes(seeds_dir: Path) -> dict[str, Path]:
    volumes: dict[str, Path] = {}
    for fpath in sorted(seeds_dir.glob("PolicyBase_*.md")):
        m = VOLUME_FILE_RE.match(fpath.name)
        if m:
            key = f"PolicyBase_{m.group(1)}"
            volumes[key] = fpath
    require(len(volumes) > 0, "no PolicyBase_*.md files found in seeds/")
    return volumes


def verify_volume_content(path: Path, key: str, valid_keys: set[str]) -> None:
    text = path.read_text(encoding="utf-8")
    head = text[:1200]
    for field in REQUIRED_FRONTMATTER_FIELDS:
        require(field in head, f"{key} frontmatter missing field: {field}")
    for field in FORBIDDEN_FRONTMATTER_FIELDS:
        require(field not in head, f"{key} forbidden frontmatter field: {field}")
    identity = re.search(r"分卷编号[：:]\s*(PolicyBase_\d{2})", head)
    require(identity is not None and identity.group(1) == key, f"{key} frontmatter 分卷编号 mismatch")
    fence_count = text.count("```")
    require(fence_count % 2 == 0, f"{key} unpaired code fence (count={fence_count})")
    without_fences = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    h2 = re.findall(r"^##\s+(.+?)\s*$", without_fences, flags=re.MULTILINE)
    dupes = sorted({heading for heading in h2 if h2.count(heading) > 1})
    require(not dupes, f"{key} duplicate H2 headings: {dupes}")
    legacy = LEGACY_PB_CITATION_RE.search(text)
    if legacy is not None:
        fail(f"{key} legacy PB citation: {legacy.group(0)!r}")
    todo = TODO_MARKER_RE.search(text)
    if todo is not None:
        fail(f"{key} TODO/placeholder marker: {todo.group(0)!r}")
    for ref in POLICYBASE_REF_RE.findall(text):
        require(f"PolicyBase_{ref}" in valid_keys, f"{key} dangling PolicyBase_{ref} reference")


def main() -> int:
    seeds_dir = Path(__file__).resolve().parent
    volumes = discover_volumes(seeds_dir)
    valid_keys = set(volumes)

    for key, path in sorted(volumes.items()):
        verify_volume_content(path, key, valid_keys)

    print(f"OK seed_set_verified: {len(volumes)} volumes verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
