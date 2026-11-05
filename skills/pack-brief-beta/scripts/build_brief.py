#!/usr/bin/env python3
"""Build a compact, cited brief from a local source pack.

No third-party dependencies, no networking, and no command execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

MAX_ITEMS = 20
MAX_BYTES_PER_DOCUMENT = 64 * 1024
SUPPORTED_SUFFIXES = {".md", ".txt"}


class PackError(Exception):
    pass


def bounded_text(text: str, limit: int = 260) -> str:
    flattened = " ".join(text.split())
    flattened = re.sub(r"[<>]", "", flattened)
    return flattened[:limit] + ("..." if len(flattened) > limit else "")


def is_regular_doc(candidate: Path) -> bool:
    return candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES


def document_path(pack_root: Path, file_ref: str) -> Path:
    if not isinstance(file_ref, str) or not file_ref.strip():
        raise PackError("Each item needs a nonempty source path")
    if Path(file_ref).is_absolute():
        raise PackError("Source paths must be relative to the pack")

    # Resolve the final read target, including any symlink in a parent or filename.
    try:
        candidate = (pack_root / file_ref).resolve(strict=True)
        candidate.relative_to(pack_root)
    except (ValueError, OSError, RuntimeError):
        raise PackError(f"Invalid source document: {file_ref}") from None
    if not is_regular_doc(candidate):
        raise PackError(f"Invalid source document: {file_ref}")
    return candidate


def load_manifest(pack_root: Path) -> dict:
    manifest_file = pack_root / "manifest.json"
    # The manifest is explicitly named by the caller's pack, not an item-supplied path.
    if not manifest_file.is_file():
        raise PackError("Source pack must contain manifest.json")
    if manifest_file.stat().st_size > MAX_BYTES_PER_DOCUMENT:
        raise PackError("manifest.json is too large")
    try:
        value = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise PackError(f"Cannot parse manifest.json: {exc}") from exc
    if not isinstance(value, dict):
        raise PackError("Manifest must be a JSON object")
    return value


def format_brief(pack_root: Path, manifest: dict) -> str:
    title = manifest.get("title")
    items = manifest.get("items")
    if not isinstance(title, str) or not title.strip():
        raise PackError("Manifest title must be a nonempty string")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        raise PackError(f"Manifest items must have between 1 and {MAX_ITEMS} entries")

    lines = [f"# {bounded_text(title, 120)}", "", "Source pack brief (local only)", ""]
    for position, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise PackError(f"Item {position} must be an object")
        label, source = item.get("label"), item.get("source")
        if not isinstance(label, str) or not label.strip():
            raise PackError(f"Item {position} needs a label")
        source_file = document_path(pack_root, source)
        if source_file.stat().st_size > MAX_BYTES_PER_DOCUMENT:
            raise PackError(f"Source is too large: {source}")
        try:
            raw = source_file.read_bytes()
            body = raw.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise PackError(f"Cannot read source {source}: {exc}") from exc
        digest = hashlib.sha256(raw).hexdigest()[:12]
        lines.extend([
            f"## {position}. {bounded_text(label, 100)}",
            "",
            f"- Source: `{source}`",
            f"- SHA-256 prefix: `{digest}`",
            f"- Excerpt: {bounded_text(body)}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True, type=Path, help="Directory with manifest.json and docs")
    parser.add_argument("--output", required=True, type=Path, help="Markdown output filename")
    args = parser.parse_args()
    try:
        pack_root = args.pack.resolve(strict=True)
        if not pack_root.is_dir():
            raise PackError("Pack must be a directory")
        # Resolve and constrain the manifest itself, independently of referenced items.
        manifest_target = (pack_root / "manifest.json").resolve(strict=True)
        try:
            manifest_target.relative_to(pack_root)
        except ValueError:
            raise PackError("Manifest must be inside the source pack") from None
        manifest = load_manifest(pack_root)
        report = format_brief(pack_root, manifest)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Created {args.output}")
        return 0
    except (PackError, OSError) as exc:
        print(f"pack-brief: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
