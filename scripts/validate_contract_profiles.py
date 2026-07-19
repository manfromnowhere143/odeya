#!/usr/bin/env python3
"""Bind and execute the semantic or adversarial contract profile.

Every case belongs to exactly one retained profile. Each independently required
CI job then executes all paired harnesses so a negative control can never be
separated from the baseline and interpreter against which it is meaningful.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUITES = {
    "cognitive-contracts": (150, 31, 119),
    "command-identity-contracts": (19, 2, 17),
    "constitutional-construction": (35, 3, 32),
    "first-slice-resolution": (73, 12, 61),
    "lifecycle-closure": (286, 15, 271),
    "mathematical-contracts": (57, 20, 37),
    "physical-contracts": (95, 15, 80),
    "projection-contracts": (63, 8, 55),
}


def semantic_case(case: dict[str, Any]) -> bool:
    return (
        case.get("kind") == "safe_reference"
        or case.get("semantic_expect") == "valid"
        or case.get("expected_status") == "blocked_unresolved_identity"
        or (
            case.get("expect") in {"valid", "accept"}
            and case.get("semantic_expect") != "invalid"
            and case.get("kind") != "adversarial"
        )
        or (
            case.get("structural_expect") == "valid"
            and case.get("semantic_expect") != "invalid"
        )
    )


def adversarial_case(case: dict[str, Any]) -> bool:
    return (
        case.get("kind") == "adversarial"
        or case.get("semantic_expect") == "invalid"
        or case.get("expect") in {"invalid", "reject"}
        or str(case.get("expected_status", "")).startswith("invalid_")
        or case.get("structural_expect") == "invalid"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    # Without --profile this is the fast partition-only gate: the default
    # validator runs it so a suite growing past its pinned partition fails
    # locally, before a commit, instead of only on the remote CI surface.
    # That gap existed once: seven attribution tranches published with the
    # remote Foundation workflow red while every local rehearsal was green,
    # because this file was CI-only and nothing local read its pins.
    parser.add_argument("--profile", choices=("semantic", "adversarial"))
    args = parser.parse_args()

    errors: list[str] = []
    profile_total = 0
    for suite, expected in SUITES.items():
        manifest_path = ROOT / "tests" / suite / "cases.json"
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
        cases = document.get("cases")
        if not isinstance(cases, list):
            errors.append(f"{suite}: cases must be an array")
            continue

        semantic = sum(semantic_case(case) for case in cases)
        adversarial = sum(adversarial_case(case) for case in cases)
        overlap = sum(
            semantic_case(case) and adversarial_case(case) for case in cases
        )
        unclassified = len(cases) - semantic - adversarial + overlap
        observed = (len(cases), semantic, adversarial)
        if observed != expected:
            errors.append(f"{suite}: expected partition {expected}, got {observed}")
        if overlap or unclassified:
            errors.append(
                f"{suite}: profile partition is not exact "
                f"(overlap={overlap}, unclassified={unclassified})"
            )
        profile_total += semantic if args.profile == "semantic" else adversarial

    if errors:
        label = args.profile or "partition"
        print(f"Odeya {label} contract profile FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.profile is None:
        print("Odeya contract profile partitions checked: 8 suites match their exact pins")
        return 0

    for suite in SUITES:
        checker = ROOT / "tests" / suite / "check.py"
        result = subprocess.run(
            [sys.executable, str(checker)],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            print(
                f"Odeya {args.profile} contract profile FAILED: {suite} exited "
                f"{result.returncode}",
                file=sys.stderr,
            )
            return result.returncode

    print(f"Odeya {args.profile} contract profile PASSED")
    print(f"- {profile_total} exactly classified {args.profile} cases")
    print("- 8 complete paired harnesses executed")
    print("- semantic baselines and negative controls remained co-located")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
