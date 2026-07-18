#!/usr/bin/env python3
"""Prove each declared cross-field rule case actually isolates its rule.

Independent review established the finding this tool answers: 210 of 286
root-level if/then cross-field rules could be deleted with the entire
adversarial corpus still green, mostly because no case exercised them at
all (ADR 0070). Binding a case to a constraint says nothing about whether
any case would notice the constraint disappearing.

A case declaring `ablation_verified_rule` claims to isolate exactly one
rule. This tool checks that claim the only way it can be checked: delete
the rule from an in-memory copy of the schema and re-validate. The case
must be refused with the rule present and accepted without it. A case that
stays refused after deletion is not isolating that rule, whatever it
declares.

The measurement is retained as `architecture/schema-rule-ablation.json`.
The cheap gate in the default validator binds the record's arithmetic and
the exact case set; only re-measurement binds it to reality, which the
exact-commit fresh-clone rehearsal runs.

This is architecture evidence about retained bytes. It is not a runtime,
an admitted member, an independently reproduced verdict, or Gate A
acceptance.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/schema-rule-ablation.json"
MANIFEST = ROOT / "tests/architecture-schema/manifest.json"

sys.path.insert(0, str(ROOT / "scripts"))


def measure() -> dict:
    import validate as foundation
    from jsonschema import Draft202012Validator, FormatChecker

    errors: list[str] = []
    _, schemas = foundation.validate_schemas(errors, True)
    registry = foundation.build_preloaded_schema_registry(schemas, errors)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    results = []
    for case in manifest.get("cases", []):
        declared = case.get("ablation_verified_rule")
        if not declared:
            continue
        schema = schemas[case["schema"]]
        instance = foundation.apply_mutations(
            json.loads((ROOT / case["fixture"]).read_text(encoding="utf-8")),
            case.get("mutations"),
            errors,
            case["name"],
        )
        index = int(declared.rsplit("/", 1)[1])
        ablated = deepcopy(schema)
        del ablated["allOf"][index]
        refused_with = bool(
            list(Draft202012Validator(schema, registry=registry,
                                      format_checker=FormatChecker()).iter_errors(instance))
        )
        refused_without = bool(
            list(Draft202012Validator(ablated, registry=registry,
                                      format_checker=FormatChecker()).iter_errors(instance))
        )
        results.append({
            "case": case["name"],
            "schema": case["schema"],
            "rule": declared,
            "isolates": refused_with and not refused_without,
        })

    isolating = sum(1 for r in results if r["isolates"])
    return {
        "schema_version": "0.1.0",
        "artifact_class": "architecture_evidence",
        "inventory_id": "odeya.schema-rule-ablation",
        "version": "0.1.0",
        "status": "candidate_measurement_not_admitted",
        "method": (
            "each case declaring ablation_verified_rule is validated against its "
            "schema with the rule present and with the rule deleted; the case "
            "isolates the rule only when it is refused with and accepted without"
        ),
        "cases": sorted(results, key=lambda r: r["case"]),
        "summary": {"declared": len(results), "isolating": isolating,
                    "not_isolating": len(results) - isolating},
        "boundary": (
            "proves each declared case notices its rule disappearing; it does not "
            "prove the corpus covers every rule, and unexercised rules remain "
            "counted in ADR 0070"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    document = measure()
    summary = document["summary"]
    for entry in document["cases"]:
        if not entry["isolates"]:
            print(f"NOT ISOLATING  {entry['case']} -> {entry['rule']}")
    print(f"{summary['isolating']}/{summary['declared']} declared cases isolate their rule")
    if summary["not_isolating"]:
        print("a case that does not isolate its declared rule is not evidence for it",
              file=sys.stderr)
        return 1

    serialized = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        RECORD.write_text(serialized)
        print(f"retained {RECORD.relative_to(ROOT)}")
        return 0
    if args.check:
        if not RECORD.exists():
            print("schema-rule ablation record is absent", file=sys.stderr)
            return 1
        if RECORD.read_text() != serialized:
            print("schema-rule ablation record does not reproduce", file=sys.stderr)
            return 1
        print("schema-rule ablation record reproduces exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
