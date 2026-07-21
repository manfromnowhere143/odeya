#!/usr/bin/env python3
"""Enforce the refusal-attribution standard by census, not by list.

ADR 0024 proved that a known-bad case refused for an incidental reason is
not evidence its named rule fires; ADRs 0055-0061 bound every negative case
in the isolated suites to its intended constraint. The first version of
this gate was then refuted by independent review (ADR 0063) on three
fronts: its sweep missed the repository's largest adversarial corpus, its
negative-detectors were a closed spelling vocabulary that five realistic
variants passed silently, and it certified a binding field one harness
enforces vacuously. This version answers each refutation structurally:

- the registry is TOTAL over direct case-bearing suite JSON: every
  tests/*/*.json whose case list is non-empty must be registered as attributed
  (with its binding shape) or as known-unattributed (with a reason) — an
  unconventional filename therefore cannot hide a second negative corpus;
- known-unattributed corpora are counted and printed, never implied covered;
- binding checks may read the whole manifest, so a suite whose exactness
  lives at manifest level (command-identity's exact_mismatch_reason_sets)
  is certified on the field its harness actually enforces exactly.

This gate checks binding presence and shape; each suite's harness proves
its bindings fire. Binding SEMANTICS vary by suite by design: pointer plus
keyword where the refusing engine is the pinned validator, message
substring where the checker is authored here, and declared intent plus an
equality-enforced observed inventory in the three suites whose subset
checks independent review defeated (ADR 0067).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

POSITIVE_MARKERS = {"valid", "accept", "safe", "safe_reference"}


def pointer_keyword(case: dict[str, Any], _: dict[str, Any]) -> bool:
    declared = case.get("expected_refusal")
    return (
        isinstance(declared, dict)
        and isinstance(declared.get("pointer"), str)
        and declared["pointer"].startswith("/")
        and "keyword" in declared
    )


def substring(field: str) -> Callable[[dict[str, Any], dict[str, Any]], bool]:
    def check(case: dict[str, Any], _: dict[str, Any]) -> bool:
        value = case.get(field)
        return isinstance(value, str) and bool(value)

    return check


def intent_and_inventory(field: str) -> Callable[[dict[str, Any], dict[str, Any]], bool]:
    """Declared intent plus the exact observed inventory (ADR 0067).

    The inventory is enforced by equality in these harnesses, so the intent
    code cannot be dropped from the declaration while it still fires — the
    incidental-rebinding attack independent review demonstrated.
    """
    inventory = string_list(field)
    intent = string_list("intent_errors")

    def check(case: dict[str, Any], document: dict[str, Any]) -> bool:
        return inventory(case, document) and intent(case, document)

    return check


def string_list(field: str) -> Callable[[dict[str, Any], dict[str, Any]], bool]:
    def check(case: dict[str, Any], _: dict[str, Any]) -> bool:
        value = case.get(field)
        return (
            isinstance(value, list)
            and bool(value)
            and all(isinstance(item, str) and item for item in value)
        )

    return check


def exact_reason_set(case: dict[str, Any], document: dict[str, Any]) -> bool:
    """command-identity's exactness lives at manifest level, per case name.

    The per-case expected_reasons field is subset-enforced and satisfiable
    by an unconditional reason (refuted by review); the harness's exact
    equality check reads exact_mismatch_reason_sets instead, so that is
    what this census certifies.
    """
    sets = document.get("exact_mismatch_reason_sets")
    return isinstance(sets, dict) and isinstance(sets.get(case.get("name")), list)


def is_structural_negative(case: dict[str, Any]) -> bool:
    return (
        case.get("expect") in {"invalid", "reject"}
        or case.get("structural_expect") == "invalid"
        or case.get("kind") in {"adversarial", "known_bad"}
        or (isinstance(case.get("expected_status"), str) and case["expected_status"].startswith("invalid_"))
    )


def is_semantic_negative(case: dict[str, Any]) -> bool:
    return case.get("semantic_expect") == "invalid" and not (
        case.get("expect") == "invalid" or case.get("structural_expect") == "invalid"
    )


# suite -> (manifest filename, structural binding check | None, semantic
# binding check | None). None means the suite has no negatives in that
# domain; a negative appearing there anyway is reported.
REGISTRY: dict[str, tuple[str, Any, Any]] = {
    "architecture-review": ("cases.json", pointer_keyword, None),
    "cognitive-contracts": ("cases.json", pointer_keyword, substring("expected_semantic_refusal_contains")),
    "mathematical-contracts": ("cases.json", pointer_keyword, substring("expected_semantic_refusal_contains")),
    "projection-contracts": ("cases.json", pointer_keyword, substring("expected_semantic_refusal_contains")),
    "physical-contracts": ("cases.json", pointer_keyword, substring("expected_semantic_refusal_contains")),
    "lifecycle-closure": ("cases.json", substring("expected_refusal_contains"), None),
    "first-slice-resolution": ("cases.json", substring("expected_refusal_contains"), None),
    "human-decision-assurance": (
        "cases.json",
        intent_and_inventory("expected_errors"),
        None,
    ),
    "human-decision-assurance-successor": (
        "cases.json",
        intent_and_inventory("expected_errors"),
        None,
    ),
    "constitutional-construction": ("cases.json", substring("expected_refusal_contains"), None),
    "work-identity-successor-cohort": ("cases.json", intent_and_inventory("expected_errors"), None),
    "work-intent-identity-candidate": ("cases.json", intent_and_inventory("expected_errors"), None),
    "prq-009-assignment-order": (
        "cases.json",
        substring("expected_refusal_contains"),
        None,
    ),
    "canonical-profile-candidate": ("cases.json", intent_and_inventory("required_errors"), None),
    "challenge-frame": ("cases.json", intent_and_inventory("expected_errors"), None),
    "command-identity-contracts": ("cases.json", exact_reason_set, None),
    # The repository's largest adversarial corpus, attributed by ADR 0068.
    "architecture-schema": ("manifest.json", pointer_keyword, None),
}

# Additional deliberately named case manifests must be enumerated explicitly;
# otherwise a second corpus beside a suite's conventional cases.json could
# evade this census while still looking like retained negative evidence.
ADDITIONAL_REGISTRY: dict[str, tuple[Any, Any]] = {
    "human-decision-assurance-successor/chain-cases.json": (
        intent_and_inventory("expected_errors"),
        None,
    ),
}

# Case-bearing manifests whose negatives are NOT attributed, held visible by
# count instead of silently uncovered. Attributing them is open work (ADR
# 0063); removing an entry here requires attributing the suite, because the
# census fails closed on any unregistered case-bearing manifest.
KNOWN_UNATTRIBUTED: dict[str, str] = {
    "canonicalization/expectations.json": (
        "canonical-identity vectors; refusals are code-bound in expectations.json"
    ),
}


def count_negatives(cases: list[Any]) -> int:
    count = 0
    for case in cases:
        if isinstance(case, dict) and (is_structural_negative(case) or is_semantic_negative(case)):
            count += 1
    return count


def audit_registered(
    suite: str,
    cases: list[Any],
    document: dict[str, Any],
    checks: tuple[Any, Any] | None = None,
) -> tuple[list[str], int]:
    errors: list[str] = []
    bound = 0
    if checks is None:
        _, structural_check, semantic_check = REGISTRY[suite]
    else:
        structural_check, semantic_check = checks
    for case in cases:
        if not isinstance(case, dict):
            errors.append(f"{suite}: a case is not an object")
            continue
        name = case.get("name", "<unnamed>")
        for negative, check, kind in (
            (is_structural_negative(case), structural_check, "structural"),
            (is_semantic_negative(case), semantic_check, "semantic"),
        ):
            if not negative:
                continue
            if check is None:
                errors.append(
                    f"{suite}: {name}: has a {kind} negative but the registry declares "
                    "none for this suite; update the registry deliberately"
                )
            elif not check(case, document):
                errors.append(
                    f"{suite}: {name}: {kind} negative case lacks its declared attribution binding"
                )
            else:
                bound += 1
    return errors, bound


def census() -> tuple[list[str], int, int, int]:
    errors: list[str] = []
    bound = 0
    swept = 0
    unattributed = 0
    for manifest_path in sorted(TESTS.glob("*/*.json")):
        relative = f"{manifest_path.parent.name}/{manifest_path.name}"
        additional_registration = ADDITIONAL_REGISTRY.get(relative)
        try:
            document = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: not valid JSON: {exc}")
            continue
        if not isinstance(document, dict):
            continue
        cases = document.get("cases")
        if not isinstance(cases, list) or not cases:
            continue
        swept += 1
        suite = manifest_path.parent.name
        registered = REGISTRY.get(suite)
        if additional_registration is not None:
            suite_errors, suite_bound = audit_registered(
                relative,
                cases,
                document,
                additional_registration,
            )
            errors.extend(suite_errors)
            bound += suite_bound
        elif registered is not None and registered[0] == manifest_path.name:
            suite_errors, suite_bound = audit_registered(suite, cases, document)
            errors.extend(suite_errors)
            bound += suite_bound
        elif relative in KNOWN_UNATTRIBUTED:
            unattributed += count_negatives(cases)
        else:
            errors.append(
                f"{relative}: carries {len(cases)} cases but is neither registered for "
                "attribution nor recorded as known-unattributed; the census fails closed "
                "on unknown case-bearing manifests"
            )
    for suite, (manifest_name, _, _) in REGISTRY.items():
        if not (TESTS / suite / manifest_name).is_file():
            errors.append(f"{suite}: registered but {manifest_name} is absent")
    for relative in KNOWN_UNATTRIBUTED:
        if not (TESTS / relative).is_file():
            errors.append(f"{relative}: recorded as known-unattributed but absent")
    for relative in ADDITIONAL_REGISTRY:
        if not (TESTS / relative).is_file():
            errors.append(f"{relative}: registered additional case manifest is absent")
    return errors, bound, swept, unattributed


def self_test() -> list[str]:
    """The gate must refuse a stripped binding, an unregistered case-bearing
    manifest, and a vacuous command-identity binding."""
    failures: list[str] = []
    stripped = [{"name": "x", "expect": "reject"}]
    errors, _ = audit_registered("lifecycle-closure", stripped, {})
    if not any("lacks its declared attribution binding" in e for e in errors):
        failures.append("attribution gate self-test: a stripped binding was not refused")
    no_exact_set = [{"name": "x", "expected_status": "invalid_x", "expected_reasons": ["always-fires"]}]
    errors, _ = audit_registered("command-identity-contracts", no_exact_set, {"exact_mismatch_reason_sets": {}})
    if not any("lacks its declared attribution binding" in e for e in errors):
        failures.append("attribution gate self-test: a missing exact reason set was not refused")
    original = REGISTRY.pop("lifecycle-closure")
    try:
        errors, _, _, _ = census()
    finally:
        REGISTRY["lifecycle-closure"] = original
    if not any("fails closed on unknown case-bearing manifests" in e for e in errors):
        failures.append("attribution gate self-test: an unregistered case-bearing manifest was not refused")
    return failures


def main() -> int:
    errors = self_test()
    census_errors, bound, swept, unattributed = census()
    errors.extend(census_errors)
    if errors:
        print("refusal attribution: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"refusal attribution checked by census: {bound} bound negative cases across "
        f"{swept} case-bearing manifests; {unattributed} negatives remain explicitly "
        "unattributed in registered corpora (ADR 0063); unknown case-bearing manifests "
        "fail closed; binding presence only, and binding semantics vary by suite "
        "(pointer+keyword, message substring, or intent+exact inventory)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
