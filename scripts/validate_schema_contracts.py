#!/usr/bin/env python3
"""Run the exhaustive schema-contract partition as an independent CI gate."""

from __future__ import annotations

import json
import sys

import validate as foundation


EXPECTED_SCHEMAS = 112
EXPECTED_CASES = {"valid": 205, "invalid": 455}


def main() -> int:
    errors: list[str] = []
    schema_ready, fixture_ready = foundation.validate_jsonschema_dependencies(errors)
    schema_count, schemas = foundation.validate_schemas(errors, schema_ready)
    case_count = foundation.validate_schema_fixtures(errors, schemas, fixture_ready)

    manifest = json.loads(foundation.SCHEMA_TEST_MANIFEST.read_text(encoding="utf-8"))
    observed_cases = {"valid": 0, "invalid": 0}
    for case in manifest.get("cases", []):
        expectation = case.get("expect")
        if expectation in observed_cases:
            observed_cases[expectation] += 1

    if schema_count != EXPECTED_SCHEMAS:
        errors.append(
            f"schema inventory drifted: expected {EXPECTED_SCHEMAS}, got {schema_count}"
        )
    if case_count != sum(EXPECTED_CASES.values()):
        errors.append(
            f"schema case inventory drifted: expected {sum(EXPECTED_CASES.values())}, "
            f"got {case_count}"
        )
    if observed_cases != EXPECTED_CASES:
        errors.append(
            f"schema case partition drifted: expected {EXPECTED_CASES}, got {observed_cases}"
        )

    if errors:
        print("Odeya schema contracts FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Odeya schema contracts PASSED")
    print(f"- {schema_count} Draft 2020-12 schemas")
    print(f"- {EXPECTED_CASES['valid']} admitted fixtures")
    print(f"- {EXPECTED_CASES['invalid']} known-bad fixtures rejected")
    print("- complete local registry; network retrieval disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
