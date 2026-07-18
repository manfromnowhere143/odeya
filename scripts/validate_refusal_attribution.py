#!/usr/bin/env python3
"""Enforce the refusal-attribution standard by census, not by list.

ADR 0024 proved that a known-bad case refused for an incidental reason is
not evidence its named rule fires; ADRs 0055-0061 bound every negative case
in every suite to its intended constraint. Twice during that work the
frontier claim itself was wrong: counts were carried instead of re-measured,
and one whole suite was missing from the list. This gate makes both errors
structural rather than disciplinary:

- every registered suite's negative cases must carry that suite's declared
  attribution binding; and
- every case manifest under tests/ is swept, and a suite unknown to the
  registry that carries negative-looking cases fails the run — a new suite
  cannot ship unattributed negatives silently.

The standard deliberately keeps domain-exact spellings instead of one
cosmetic vocabulary (ADR 0062): a jsonschema refusal is bound by instance
pointer + keyword because those are library-stable, an authored-checker
refusal is bound by its message because the message is contract text, and
the three older spellings are retained where their harnesses already
enforce them. Re-spelling hundreds of proven bindings would churn evidence
without strengthening it.

This gate checks binding *presence and shape*; each suite's own harness
proves the binding fires, with its own fail-closed self-test. A
seventeen-line self-test here proves this gate refuses a stripped binding
and an unregistered negative suite, on every run.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"


def pointer_keyword(case: dict[str, Any]) -> bool:
    declared = case.get("expected_refusal")
    return (
        isinstance(declared, dict)
        and isinstance(declared.get("pointer"), str)
        and declared["pointer"].startswith("/")
        and "keyword" in declared
    )


def substring(field: str) -> Callable[[dict[str, Any]], bool]:
    def check(case: dict[str, Any]) -> bool:
        value = case.get(field)
        return isinstance(value, str) and bool(value)

    return check


def string_list(field: str) -> Callable[[dict[str, Any]], bool]:
    def check(case: dict[str, Any]) -> bool:
        value = case.get(field)
        return (
            isinstance(value, list)
            and bool(value)
            and all(isinstance(item, str) and item for item in value)
        )

    return check


def is_structural_negative(case: dict[str, Any]) -> bool:
    return (
        case.get("expect") in {"invalid", "reject"}
        or case.get("structural_expect") == "invalid"
        or case.get("kind") == "adversarial"
        or str(case.get("expected_status", "")).startswith("invalid_")
    )


def is_semantic_negative(case: dict[str, Any]) -> bool:
    return case.get("semantic_expect") == "invalid" and not (
        case.get("expect") == "invalid" or case.get("structural_expect") == "invalid"
    )


# suite -> (structural binding check | None, semantic binding check | None).
# None means the suite has no negative cases in that domain; a negative case
# appearing there anyway is reported, because absence must stay measured.
REGISTRY: dict[str, tuple[Callable[[dict[str, Any]], bool] | None, Callable[[dict[str, Any]], bool] | None]] = {
    "architecture-review": (pointer_keyword, None),
    "cognitive-contracts": (pointer_keyword, substring("expected_semantic_refusal_contains")),
    "mathematical-contracts": (pointer_keyword, substring("expected_semantic_refusal_contains")),
    "projection-contracts": (pointer_keyword, substring("expected_semantic_refusal_contains")),
    "physical-contracts": (pointer_keyword, substring("expected_semantic_refusal_contains")),
    "lifecycle-closure": (substring("expected_refusal_contains"), None),
    "first-slice-resolution": (substring("expected_refusal_contains"), None),
    "constitutional-construction": (substring("expected_refusal_contains"), None),
    "work-identity-successor-cohort": (string_list("expected_errors"), None),
    "work-intent-identity-candidate": (string_list("expected_errors"), None),
    "canonical-profile-candidate": (string_list("required_errors"), None),
    "command-identity-contracts": (string_list("expected_reasons"), None),
}


def audit_manifest(suite: str, cases: list[Any]) -> tuple[list[str], int]:
    errors: list[str] = []
    bound = 0
    spec = REGISTRY.get(suite)
    for case in cases:
        if not isinstance(case, dict):
            continue
        name = case.get("name", "<unnamed>")
        negative_domains = []
        if is_structural_negative(case):
            negative_domains.append(0)
        if is_semantic_negative(case):
            negative_domains.append(1)
        if not negative_domains:
            continue
        if spec is None:
            errors.append(
                f"{suite}: carries negative case {name!r} but is unknown to the "
                "attribution registry; register its binding spelling before retaining it"
            )
            continue
        for domain in negative_domains:
            check = spec[domain]
            kind = "structural" if domain == 0 else "semantic"
            if check is None:
                errors.append(
                    f"{suite}: {name}: has a {kind} negative but the registry declares "
                    "none for this suite; update the registry deliberately"
                )
            elif not check(case):
                errors.append(
                    f"{suite}: {name}: {kind} negative case lacks its declared "
                    "attribution binding"
                )
            else:
                bound += 1
    return errors, bound


def census() -> tuple[list[str], int, int]:
    errors: list[str] = []
    bound = 0
    suites = 0
    for manifest_path in sorted(TESTS.glob("*/cases.json")):
        suite = manifest_path.parent.name
        try:
            document = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{suite}: cases.json is not valid JSON: {exc}")
            continue
        cases = document.get("cases", [])
        if not isinstance(cases, list):
            errors.append(f"{suite}: cases must be an array")
            continue
        suite_errors, suite_bound = audit_manifest(suite, cases)
        errors.extend(suite_errors)
        bound += suite_bound
        suites += 1
    for suite in REGISTRY:
        if not (TESTS / suite / "cases.json").is_file():
            errors.append(f"{suite}: registered but its cases.json is absent")
    return errors, bound, suites


def self_test() -> list[str]:
    """The gate must refuse a stripped binding and an unregistered negative."""
    failures: list[str] = []
    stripped = [{"name": "x", "expect": "reject"}]
    errors, _ = audit_manifest("lifecycle-closure", stripped)
    if not any("lacks its declared attribution binding" in e for e in errors):
        failures.append("attribution gate self-test: a stripped binding was not refused")
    unknown = [{"name": "x", "expect": "invalid"}]
    errors, _ = audit_manifest("odeya-self-test-unregistered", unknown)
    if not any("unknown to the attribution registry" in e for e in errors):
        failures.append("attribution gate self-test: an unregistered negative suite was not refused")
    return failures


def main() -> int:
    errors = self_test()
    census_errors, bound, suites = census()
    errors.extend(census_errors)
    if errors:
        print("refusal attribution: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"refusal attribution checked by census: {bound} bound negative cases across "
        f"{suites} swept manifests; unknown suites with negatives fail closed; "
        "binding presence only — each suite's harness proves its bindings fire"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
