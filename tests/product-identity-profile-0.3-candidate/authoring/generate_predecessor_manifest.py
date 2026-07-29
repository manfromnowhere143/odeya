#!/usr/bin/env python3
"""Freeze the exact 132-schema predecessor cohort from commit 617209ba."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "tests/product-identity-profile-0.3-candidate/predecessor-schemas.json"
SOURCE_COMMIT = "617209ba480b854a00c6a15cd99ac1d5a18e90ad"
SOURCE_TREE = "67c38b895276bf2c804fe192339ce90a8c75ea97"
EXPECTED_COUNT = 132


def git_bytes(*arguments: str) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            f"{result.stderr.decode('utf-8', 'replace')[:500]}"
        )
    return result.stdout


def strict_object(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(entries: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in entries:
            if key in result:
                raise ValueError(f"duplicate key {key!r} in {label}")
            result[key] = value
        return result

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError(f"schema root is not an object: {label}")
    return value


def build() -> dict[str, Any]:
    resolved = git_bytes("rev-parse", SOURCE_COMMIT).decode().strip()
    tree = git_bytes("rev-parse", f"{SOURCE_COMMIT}^{{tree}}").decode().strip()
    if resolved != SOURCE_COMMIT or tree != SOURCE_TREE:
        raise RuntimeError("frozen predecessor commit or tree is unavailable")
    paths = [
        line
        for line in git_bytes(
            "ls-tree", "-r", "--name-only", SOURCE_COMMIT, "--", "schemas"
        )
        .decode("utf-8")
        .splitlines()
        if line.endswith(".schema.json")
    ]
    if paths != sorted(paths) or len(paths) != EXPECTED_COUNT:
        raise RuntimeError(
            f"expected {EXPECTED_COUNT} sorted predecessor paths, got {len(paths)}"
        )
    rows: list[list[Any]] = []
    identities: set[str] = set()
    for path in paths:
        raw = git_bytes("show", f"{SOURCE_COMMIT}:{path}")
        document = strict_object(raw, path)
        schema_id = document.get("$id")
        if not isinstance(schema_id, str) or schema_id in identities:
            raise RuntimeError(f"missing or duplicate predecessor schema ID: {path}")
        identities.add(schema_id)
        rows.append(
            [
                path,
                schema_id,
                f"sha256:{hashlib.sha256(raw).hexdigest()}",
                len(raw),
            ]
        )
    corpus_preimage = (
        json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002e_frozen_predecessor_schema_manifest",
        "source_commit": SOURCE_COMMIT,
        "source_tree": SOURCE_TREE,
        "row_shape": ["path", "schema_id", "raw_digest", "byte_count"],
        "schema_path_count": EXPECTED_COUNT,
        "ordered_row_corpus_sha256": (
            f"sha256:{hashlib.sha256(corpus_preimage).hexdigest()}"
        ),
        "schemas": rows,
    }


def encoded(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = encoded(build())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
            raise SystemExit("frozen predecessor manifest is absent or stale")
        return 0
    OUTPUT.write_bytes(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
