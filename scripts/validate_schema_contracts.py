#!/usr/bin/env python3
"""Run the exhaustive schema-contract partition as an independent CI gate.

With --pins-only this is the fast local reader of the pins below: it counts
the schema inventory and the manifest's valid/invalid partition without
executing the validation itself, which the default validator already runs.
The pins were CI-only once — the same failure class as the contract-profile
incident, found live by independent review (ADR 0063): a schema or
fixture-classification change passed every local gate including the full
rehearsal and failed only the remote Schema contracts job, because the
valid/invalid split was bound by no other artifact anywhere.
"""

from __future__ import annotations

import argparse
import json
import sys

import validate as foundation


EXPECTED_SCHEMAS = 115
EXPECTED_CASES = {"valid": 213, "invalid": 635}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pins-only", action="store_true", help="check the pinned counts without revalidating")
    args = parser.parse_args()

    errors: list[str] = []
    if args.pins_only:
        schema_count = sum(1 for _ in (foundation.ROOT / "schemas").glob("*.schema.json"))
        manifest = json.loads(foundation.SCHEMA_TEST_MANIFEST.read_text(encoding="utf-8"))
        case_count = len(manifest.get("cases", []))
    else:
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

    if args.pins_only:
        print(
            f"schema-contract pins checked: {schema_count} schemas, "
            f"{observed_cases['valid']} valid / {observed_cases['invalid']} invalid cases match the CI pins"
        )
        return 0

    print("Odeya schema contracts PASSED")
    print(f"- {schema_count} Draft 2020-12 schemas")
    print(f"- {EXPECTED_CASES['valid']} admitted fixtures")
    print(f"- {EXPECTED_CASES['invalid']} known-bad fixtures rejected")
    print("- complete local registry; network retrieval disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
