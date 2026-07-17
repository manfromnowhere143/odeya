#!/usr/bin/env python3
"""Execute wave tranche D2a: pin every unprofiled datetime path outside
ResearchEvent to the frozen UTC microsecond lexical profile.

The accepted D2 disposition pins each `format: date-time` node to the exact
pattern the canonicalization profile freezes. Every schema whose bytes change
is reissued at the same path with a bumped minor version under the ledger's
precedent, its predecessor retained as a git object, and every consumer of the
retired identity repointed in the same tranche.

ResearchEvent's 20 paths are deferred to D2b: its identity is load-bearing in
the 60-event identity map, the lifecycle suite's hardcoded constants, and the
event fixtures, and that web deserves its own recorded tranche.

Idempotent: running against an already-pinned tree changes nothing.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME_PATTERN = (
    "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    "[0-9]{2}\\.[0-9]{6}Z$"
)
DEFERRED = {"schemas/research-event.schema.json"}
URN = re.compile(r"^(urn:odeya:schema:[a-z0-9-]+:)(\d+)\.(\d+)\.(\d+)$")


def sha(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def pin_datetimes(schema: dict) -> int:
    """Set the frozen pattern on every format:date-time node lacking it.

    Works on resolved shape: a $ref node's target def receives the pattern, so
    every reference through it is pinned at once.
    """

    def resolve(node):
        ref = node.get("$ref") if isinstance(node, dict) else None
        if isinstance(ref, str) and ref.startswith("#/"):
            cur = schema
            try:
                for seg in ref[2:].split("/"):
                    cur = cur[seg.replace("~1", "/").replace("~0", "~")]
            except (KeyError, TypeError):
                return node
            return cur
        return node

    pinned = 0
    seen: set[int] = set()

    def walk(node):
        nonlocal pinned
        if isinstance(node, dict):
            target = resolve(node)
            if (
                isinstance(target, dict)
                and target.get("format") == "date-time"
                and target.get("pattern") != FIXED_TIME_PATTERN
                and id(target) not in seen
            ):
                target["pattern"] = FIXED_TIME_PATTERN
                seen.add(id(target))
                pinned += 1
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(schema)
    return pinned


def main() -> int:
    audit = json.loads((ROOT / "tests/canonicalization/SCHEMA_AUDIT.json").read_text())
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()

    reissues = []
    renames: dict[str, str] = {}
    for record in audit["schemas"]:
        if not record.get("unprofiled_datetime_paths") or record["path"] in DEFERRED:
            continue
        path = ROOT / record["path"]
        schema = json.loads(path.read_text())
        old_id = schema["$id"]
        m = URN.match(old_id)
        if not m:
            raise SystemExit(f"unversioned $id: {old_id}")
        # never bump onto a taken identity: side-by-side successors already
        # occupy versions above some legacy resources (work-intent 0.2/0.3,
        # work-contract 0.3), and a collision here forged a duplicate $id on
        # the first run of this tranche
        taken = {
            json.loads(candidate.read_text())["$id"]
            for candidate in (ROOT / "schemas").glob("*.schema.json")
        }
        minor = int(m.group(3)) + 1
        while f"{m.group(1)}{m.group(2)}.{minor}.0" in taken:
            minor += 1
        new_id = f"{m.group(1)}{m.group(2)}.{minor}.0"

        pinned = pin_datetimes(schema)
        if not pinned:
            continue
        schema["$id"] = new_id
        # bump a schema_version const if the resource declares one for itself
        sv = schema.get("properties", {}).get("schema_version", {})
        if isinstance(sv, dict) and sv.get("const") == f"{m.group(2)}.{m.group(3)}.{m.group(4)}":
            sv["const"] = f"{m.group(2)}.{int(m.group(3)) + 1}.0"

        blob = subprocess.run(
            ["git", "rev-parse", f"HEAD:{record['path']}"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        old_bytes = subprocess.run(
            ["git", "show", f"HEAD:{record['path']}"],
            cwd=ROOT, capture_output=True, check=True,
        ).stdout
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
        renames[old_id] = new_id
        reissues.append({
            "path": record["path"],
            "predecessor": {
                "schema_id": old_id,
                "source_commit": head,
                "git_blob": blob,
                "raw_sha256": "sha256:" + hashlib.sha256(old_bytes).hexdigest(),
                "byte_count": len(old_bytes),
                "retention_mode": "git_object_only_architecture_checkpoint_blocking",
            },
            "current_candidate": {
                "schema_id": new_id,
                "raw_sha256": sha(path),
                "byte_count": len(path.read_bytes()),
            },
        })
        print(f"reissued {record['path'].split('/')[-1]:44s} {pinned:2d} pins  {old_id.rsplit(':',1)[1]} -> {new_id.rsplit(':',1)[1]}")

    if not renames:
        print("nothing to do")
        return 0

    # repoint every retired identity across schemas, fixtures, and records
    repointed = 0
    for scope in ("schemas", "architecture", "tests"):
        for p in sorted((ROOT / scope).rglob("*.json")):
            s = p.read_text()
            out = s
            for old_id, new_id in renames.items():
                out = out.replace(old_id, new_id)
            if out != s:
                p.write_text(out)
                repointed += 1
    print(f"consumers repointed: {repointed} files")

    # ledger: append the reissue rows
    lp = ROOT / "architecture/schema-resource-reissue-ledger.json"
    ledger = json.loads(lp.read_text())
    known = {r["path"] for r in ledger["reissues"]}
    appended = 0
    for row in reissues:
        if row["path"] not in known:
            ledger["reissues"].append(row)
            appended += 1
        else:
            for existing in ledger["reissues"]:
                if existing["path"] == row["path"]:
                    existing["current_candidate"] = row["current_candidate"]
    lp.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    print(f"ledger: {appended} reissue rows appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
