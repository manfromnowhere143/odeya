#!/usr/bin/env python3
"""Gate the retained suite guard-coverage record.

The measurement disables every refusal construct of twelve suites in turn
and lives in `scripts/audit_suite_guard_coverage.py`. This is the cheap
half: the record must describe the exact checker bytes it claims, cover
every declared suite, keep unproved guards enumerated by name, and agree
with its own arithmetic.

The boundary its siblings carry applies here too, and ADR 0077 sharpened
it: a retained record is regenerable by `--write`, so this gate cannot
detect a laundered weakening. Only re-measurement can, which the
exact-commit rehearsal runs.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/suite-guard-coverage.json"
AUDIT_TOOL = ROOT / "scripts/audit_suite_guard_coverage.py"
EXPECTED_SUMMARY = {"guard_count": 611, "proved": 203, "unproved": 408, "crash_detected": 0}


def main() -> int:
    errors: list[str] = []
    if not AUDIT_TOOL.exists():
        errors.append("the suite guard-coverage audit tool is absent")
    if not RECORD.exists():
        print("suite guard coverage: record is absent", file=sys.stderr)
        return 1

    document = json.loads(RECORD.read_text(encoding="utf-8"))
    if document.get("status") != "candidate_measurement_not_admitted":
        errors.append("record status must remain candidate_measurement_not_admitted")
    if document.get("artifact_class") != "architecture_evidence":
        errors.append("record must declare itself architecture evidence")

    total = proved = 0
    for suite in document.get("suites", []):
        guards = suite.get("guards")
        if not isinstance(guards, list):
            errors.append(f"{suite.get('suite')}: record enumerates no guards")
            continue
        if suite.get("control") != "passed":
            errors.append(f"{suite.get('suite')}: unmutated control did not pass; the audit is void")
        subject = ROOT / str(suite.get("subject", ""))
        if not subject.is_file():
            errors.append(f"{suite.get('suite')}: subject is absent")
        else:
            actual = "sha256:" + hashlib.sha256(subject.read_bytes()).hexdigest()
            if suite.get("subject_sha256") != actual:
                errors.append(
                    f"{suite.get('suite')}: record does not describe the current checker bytes; "
                    "re-run scripts/audit_suite_guard_coverage.py --write"
                )
        if suite.get("guard_count") != len(guards):
            errors.append(f"{suite.get('suite')}: guard_count disagrees with the enumeration")
        actual_proved = sum(1 for g in guards if g.get("proved") is True)
        if suite.get("proved_count") != actual_proved:
            errors.append(f"{suite.get('suite')}: proved_count disagrees with the enumeration")
        for guard in guards:
            if not isinstance(guard.get("guard"), str) or not guard["guard"]:
                errors.append(f"{suite.get('suite')}: a guard is enumerated without an identity")
            if guard.get("proved") is True and guard.get("detection") not in {"case_attributed", "crash"}:
                errors.append(f"{suite.get('suite')}: a proved guard does not declare its detection kind")
        total += len(guards)
        proved += actual_proved

    summary = document.get("summary") or {}
    if summary.get("guard_count") != total or summary.get("proved") != proved:
        errors.append("summary disagrees with the enumerated suites")
    for field, value in EXPECTED_SUMMARY.items():
        if summary.get(field) != value:
            errors.append(
                f"retained {field} is {summary.get(field)!r} but this gate pins {value!r}; "
                "re-measure and update the pin deliberately"
            )

    if errors:
        print("suite guard coverage: FAILED")
        for message in errors:
            print(f"- {message}")
        return 1

    print(
        f"suite guard-coverage record checked: {proved}/{total} guards proved by mutation across "
        f"{len(document.get('suites', []))} suites, {total - proved} with no known-bad proof "
        "retained explicitly; coverage is not correctness and Gate A acceptance remains separate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
