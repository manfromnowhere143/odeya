#!/usr/bin/env python3
"""Gate the retained lifecycle condition-coverage record.

The measurement is a mutation run over every removable condition and lives in
`scripts/audit_lifecycle_condition_coverage.py`. This is the cheap half: it
proves the retained record still describes the exact checker bytes it claims,
that its counts are internally consistent, and that every condition without
evidence stays explicitly enumerated.

What this gate cannot do, stated plainly, the same boundary its statement-
level sibling learned from independent review: it cannot detect a falsified
record. Flipping a condition to unproved, or deleting one by name with the
counts corrected, survives it. This gate enforces digest and arithmetic;
only re-measurement binds content to reality, and the exact-commit
fresh-clone rehearsal runs `--check` for exactly that reason.

This validates retained bytes. It does not prove the conditions enforce the
right rules, admit a member, supply an independently reproduced verdict, or
accept Gate A.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/lifecycle-condition-coverage.json"
AUDIT_TOOL = ROOT / "scripts/audit_lifecycle_condition_coverage.py"


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []

    if not AUDIT_TOOL.exists():
        add(errors, "the condition-coverage audit tool is absent; the record cannot be reproduced")
    if not RECORD.exists():
        print("lifecycle condition coverage: record is absent", file=sys.stderr)
        return 1

    try:
        document = json.loads(RECORD.read_text())
    except json.JSONDecodeError as exc:
        print(f"lifecycle condition coverage: record is not valid JSON: {exc}", file=sys.stderr)
        return 1

    if document.get("status") != "candidate_measurement_not_admitted":
        add(errors, "record status must remain candidate_measurement_not_admitted")
    if document.get("artifact_class") != "architecture_evidence":
        add(errors, "record must declare itself architecture evidence")

    subject_rel = document.get("subject")
    if not isinstance(subject_rel, str) or not subject_rel:
        add(errors, "record does not name its subject")
        subject_rel = None

    if subject_rel:
        subject = ROOT / subject_rel
        if not subject.exists():
            add(errors, f"record subject is absent: {subject_rel}")
        else:
            actual = "sha256:" + hashlib.sha256(subject.read_bytes()).hexdigest()
            declared = document.get("subject_sha256")
            if declared != actual:
                add(
                    errors,
                    "record does not describe the current checker bytes; re-run "
                    "scripts/audit_lifecycle_condition_coverage.py --write to re-measure "
                    f"(declared {declared}, actual {actual})",
                )

    models = document.get("models")
    if not isinstance(models, list) or not models:
        add(errors, "record enumerates no audited function")
        models = []

    total = 0
    proved = 0
    for model in models:
        conditions = model.get("conditions")
        if not isinstance(conditions, list):
            add(errors, f"{model.get('function')}: record enumerates no condition list")
            continue
        if model.get("condition_count") != len(conditions):
            add(errors, f"{model.get('function')}: condition_count disagrees with the enumeration")
        actual_proved = sum(1 for c in conditions if c.get("proved") is True)
        if model.get("proved_count") != actual_proved:
            add(errors, f"{model.get('function')}: proved_count disagrees with the enumeration")
        for condition in conditions:
            if not isinstance(condition.get("condition"), str) or not condition["condition"]:
                add(errors, f"{model.get('function')}: a condition is enumerated without its source")
            if condition.get("role") not in {"disjunct", "conjunct", "comprehension_filter"}:
                add(errors, f"{model.get('function')}: a condition lacks its boolean role")
            if condition.get("proved") is True and not condition.get("proved_by"):
                add(
                    errors,
                    f"{model.get('function')}: a condition claims a proof without naming "
                    "the failure that establishes it",
                )
            if condition.get("proved") is True and condition.get("detection") not in {"case_attributed", "crash"}:
                add(errors, f"{model.get('function')}: a proved condition does not declare its detection kind")
            if condition.get("proved") is False and condition.get("proved_by"):
                add(errors, f"{model.get('function')}: an unproved condition names a proof")
        total += len(conditions)
        proved += actual_proved

    summary = document.get("summary") or {}
    if summary.get("condition_count") != total:
        add(errors, "summary condition_count disagrees with the enumerated functions")
    if summary.get("proved") != proved:
        add(errors, "summary proved count disagrees with the enumerated functions")
    if summary.get("unproved") != total - proved:
        add(errors, "summary unproved count is not the exact remainder")

    # What is present but unaudited must be counted; a silent zero reads clean.
    not_audited = document.get("not_audited")
    if not isinstance(not_audited, dict) or not (
        isinstance(not_audited.get("single_condition_tests"), int)
        and isinstance(not_audited.get("nested_boolean_groups"), int)
        and isinstance(not_audited.get("ternary_selectors"), int)
    ):
        add(errors, "record does not explicitly count its unaudited constructs")

    if errors:
        print("lifecycle condition coverage: FAILED")
        for message in errors:
            print(f"- {message}")
        return 1

    print(
        f"lifecycle condition coverage record checked: {proved}/{total} conditions proved by "
        f"mutation, {total - proved} removable-with-suite-green retained explicitly; "
        "condition coverage is not correctness and Gate A acceptance remains separate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
