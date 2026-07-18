#!/usr/bin/env python3
"""Gate the retained lifecycle guard-coverage record.

The measurement itself is a mutation run over every guard and is too expensive
for the default validator, so it lives in
`scripts/audit_lifecycle_guard_coverage.py`. This is the cheap half: it proves
the retained record still describes the exact checker bytes it claims to
describe, that its counts are internally consistent, and that every guard
without a known-bad proof stays explicitly enumerated.

Changing the checker changes its digest, which invalidates the record and forces
the guards to be re-proved. Leaving the checker alone costs one hash.

What this gate cannot do, stated plainly because an earlier version of this file
implied otherwise. It cannot detect a falsified record. Flipping a guard to
unproved, or deleting an unproved guard by name, survives it as long as the
counts are corrected to match — an independent reviewer demonstrated both. This
gate enforces the checker digest and the record's internal arithmetic; nothing
here binds the record's content to an actual measurement, and nothing can
without re-measuring. `scripts/audit_lifecycle_guard_coverage.py --check` is the
only real check, and the exact-commit fresh-clone rehearsal runs it.

Negative evidence is still retained by name rather than summarized, so a reader
can see which guards are unproved without re-running the audit. That is for
review, not for enforcement; the count is not self-defending.

This validates retained bytes. It does not prove the guards are correct, admit
a member, supply an independently reproduced verdict, or accept Gate A.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/lifecycle-guard-coverage.json"
EXPECTED_SUMMARY = {"branch_count": 185, "proved": 178, "unproved": 7, "crash_detected": 0}
AUDIT_TOOL = ROOT / "scripts/audit_lifecycle_guard_coverage.py"


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []

    if not AUDIT_TOOL.exists():
        add(errors, "the guard-coverage audit tool is absent; the record cannot be reproduced")
    if not RECORD.exists():
        print("lifecycle guard coverage: record is absent", file=sys.stderr)
        return 1

    try:
        document = json.loads(RECORD.read_text())
    except json.JSONDecodeError as exc:
        print(f"lifecycle guard coverage: record is not valid JSON: {exc}", file=sys.stderr)
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
                    "scripts/audit_lifecycle_guard_coverage.py --write to re-prove the guards "
                    f"(declared {declared}, actual {actual})",
                )

    models = document.get("models")
    if not isinstance(models, list) or not models:
        add(errors, "record enumerates no lifecycle model")
        models = []

    total = 0
    proved = 0
    for model in models:
        branches = model.get("branches")
        if not isinstance(branches, list) or not branches:
            add(errors, f"{model.get('function')}: record enumerates no guard")
            continue
        declared_count = model.get("branch_count")
        declared_proved = model.get("proved_count")
        if declared_count != len(branches):
            add(errors, f"{model.get('function')}: branch_count disagrees with the enumerated guards")
        actual_proved = sum(1 for b in branches if b.get("proved") is True)
        if declared_proved != actual_proved:
            add(errors, f"{model.get('function')}: proved_count disagrees with the enumerated guards")
        for branch in branches:
            if not isinstance(branch.get("guard"), str) or not branch["guard"]:
                add(errors, f"{model.get('function')}: a guard is enumerated without an identity")
            if branch.get("proved") is True and not branch.get("proved_by"):
                add(
                    errors,
                    f"{model.get('function')}: a guard claims a proof without naming the "
                    "known-bad case that establishes it",
                )
            if branch.get("proved") is True and branch.get("detection") not in {"case_attributed", "crash"}:
                add(errors, f"{model.get('function')}: a proved guard does not declare its detection kind")
            if branch.get("proved") is False and branch.get("proved_by"):
                add(errors, f"{model.get('function')}: an unproved guard names a proof")
        total += len(branches)
        proved += actual_proved

    # A retained record is regenerable: `--write` reproduces it from whatever
    # the checker currently says, so an author can launder a weakening by
    # re-measuring (independent review, ADR 0077). Pinning the measured totals
    # here does not stop that, but it converts a silent regeneration into a
    # deliberate, reviewable edit of this file.
    if EXPECTED_SUMMARY is not None:
        for field, value in EXPECTED_SUMMARY.items():
            if (document.get("summary") or {}).get(field) != value:
                add(errors, f"retained {field} is {(document.get('summary') or {}).get(field)!r}, "
                            f"but this gate pins {value!r}; re-measure and update the pin deliberately")
    summary = document.get("summary") or {}
    if summary.get("branch_count") != total:
        add(errors, "summary branch_count disagrees with the enumerated models")
    if summary.get("proved") != proved:
        add(errors, "summary proved count disagrees with the enumerated models")
    if summary.get("unproved") != total - proved:
        add(errors, "summary unproved count is not the exact remainder")

    # A model that cannot be measured must say so. A silent zero reads as clean.
    for entry in document.get("not_auditable", []):
        if not entry.get("reason"):
            add(errors, f"{entry.get('function')}: declared unauditable without a reason")

    if errors:
        print("lifecycle guard coverage: FAILED")
        for message in errors:
            print(f"- {message}")
        return 1

    unmeasured = len(document.get("not_auditable", []))
    print(
        f"lifecycle guard coverage record checked: {proved}/{total} guards proved by mutation, "
        f"{total - proved} with no known-bad proof retained explicitly, {unmeasured} model unmeasured; "
        "coverage is not correctness and Gate A acceptance remains separate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
