#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Write and verify a SHA-256 manifest for tracked repo material."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = Path("docs/MATERIALS.sha256")
EXCLUDED = {DEFAULT_MANIFEST.as_posix()}


def git_files() -> list[str]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    )
    files = [item.decode("utf-8") for item in output.split(b"\0") if item]
    return sorted(path for path in files if path not in EXCLUDED and (ROOT / path).is_file())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel in git_files():
        rows.append(f"{sha256_file(ROOT / rel)}  {rel}\n")
    path.write_text("".join(rows), encoding="utf-8")
    print(f"wrote {len(rows)} hashes to {path}")
    return 0


def read_manifest(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        try:
            expected, rel = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"{path}:{line_no}: expected '<sha256>  <path>'") from exc
        rows.append((expected, rel))
    return rows


def verify_manifest(path: Path) -> int:
    failures = 0
    rows = read_manifest(path)
    for expected, rel in rows:
        file_path = ROOT / rel
        if not file_path.is_file():
            print(f"missing  {rel}", file=sys.stderr)
            failures += 1
            continue
        actual = sha256_file(file_path)
        if actual != expected:
            print(f"changed  {rel}", file=sys.stderr)
            failures += 1
    if failures:
        print(f"{failures} manifest entries failed", file=sys.stderr)
        return 1
    print(f"verified {len(rows)} hashes from {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["write", "verify"], nargs="?", default="verify")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST.as_posix())
    args = parser.parse_args()

    manifest = ROOT / args.manifest
    if args.command == "write":
        return write_manifest(manifest)
    if not manifest.is_file():
        print(f"manifest not found: {manifest}", file=sys.stderr)
        return 1
    return verify_manifest(manifest)


if __name__ == "__main__":
    raise SystemExit(main())
