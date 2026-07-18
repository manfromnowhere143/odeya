#!/usr/bin/env python3
"""Gate the retained schema-rule ablation record.

The measurement re-validates every declared case with and without its rule
and lives in `scripts/audit_schema_rule_ablation.py`. This is the cheap
half: the record must cover exactly the cases that declare a rule, every
one must isolate, and the arithmetic must agree.

What this gate cannot do, the same boundary its siblings carry: it cannot
detect a falsified record. Only re-measurement binds content to reality,
and the exact-commit fresh-clone rehearsal runs `--check` for that.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/schema-rule-ablation.json"
MANIFEST = ROOT / "tests/architecture-schema/manifest.json"
AUDIT_TOOL = ROOT / "scripts/audit_schema_rule_ablation.py"


def main() -> int:
    errors: list[str] = []
    if not AUDIT_TOOL.exists():
        errors.append("the ablation audit tool is absent; the record cannot be reproduced")
    if not RECORD.exists():
        print("schema-rule ablation: record is absent", file=sys.stderr)
        return 1

    document = json.loads(RECORD.read_text(encoding="utf-8"))
    if document.get("status") != "candidate_measurement_not_admitted":
        errors.append("record status must remain candidate_measurement_not_admitted")
    if document.get("artifact_class") != "architecture_evidence":
        errors.append("record must declare itself architecture evidence")

    entries = document.get("cases")
    if not isinstance(entries, list):
        print("schema-rule ablation: record enumerates no cases", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    declared = {
        case["name"]
        for case in manifest.get("cases", [])
        if isinstance(case, dict) and case.get("ablation_verified_rule")
    }
    recorded = {entry.get("case") for entry in entries}
    if declared != recorded:
        errors.append(
            f"record does not cover the declaring cases exactly: "
            f"missing={sorted(declared - recorded)} extra={sorted(recorded - declared)}"
        )
    for entry in entries:
        if entry.get("isolates") is not True:
            errors.append(f"{entry.get('case')}: retained as not isolating its declared rule")

    summary = document.get("summary") or {}
    if summary.get("declared") != len(entries):
        errors.append("summary declared count disagrees with the enumeration")
    isolating = sum(1 for entry in entries if entry.get("isolates") is True)
    if summary.get("isolating") != isolating:
        errors.append("summary isolating count disagrees with the enumeration")
    if summary.get("not_isolating") != len(entries) - isolating:
        errors.append("summary not_isolating count is not the exact remainder")

    if errors:
        print("schema-rule ablation: FAILED")
        for message in errors:
            print(f"- {message}")
        return 1

    print(
        f"schema-rule ablation record checked: {isolating} cases each proven to notice "
        "their cross-field rule disappearing; coverage of unexercised rules remains open"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
