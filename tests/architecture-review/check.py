#!/usr/bin/env python3
"""Run the isolated Gate A review-schema cases.

Passing these structural cases is not an independent review, Gate A acceptance,
an operator decision, or implementation authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests/architecture-review/cases.json"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def mutate(instance: object, mutations: list[dict[str, object]]) -> object:
    # JSON round-tripping gives the cases an independent deep copy without
    # importing the shared validator while its manifest is being assembled.
    result = json.loads(json.dumps(instance))
    for mutation in mutations:
        operation = mutation["op"]
        tokens = pointer_tokens(str(mutation["path"]))
        parent = result
        for token in tokens[:-1]:
            parent = parent[int(token)] if isinstance(parent, list) else parent[token]
        final = tokens[-1]
        if isinstance(parent, list):
            position = int(final)
            if operation == "add":
                parent.insert(position, mutation.get("value"))
            elif operation == "remove":
                del parent[position]
            elif operation == "replace":
                parent[position] = mutation["value"]
            else:
                raise ValueError(f"unsupported mutation operation: {operation!r}")
        elif isinstance(parent, dict):
            if operation == "add":
                if final in parent:
                    raise ValueError(f"add target already exists: {final!r}")
                parent[final] = mutation.get("value")
            elif operation == "remove":
                del parent[final]
            elif operation == "replace":
                if final not in parent:
                    raise KeyError(final)
                parent[final] = mutation["value"]
            else:
                raise ValueError(f"unsupported mutation operation: {operation!r}")
        else:
            raise TypeError("mutation parent is not a container")
    return result


def evaluate_case(case: dict) -> list[str]:
    failures: list[str] = []
    schema_path = ROOT / case["schema"]
    fixture_path = ROOT / case["fixture"]
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    instance = mutate(load_json(fixture_path), case.get("mutations", []))
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance)
    )
    actual = "invalid" if errors else "valid"
    if actual != case["expect"]:
        detail = errors[0].message if errors else "mutation was unexpectedly accepted"
        failures.append(f"{case['name']}: expected {case['expect']}, got {actual}: {detail}")
    if case["expect"] == "invalid":
        # Refusal for an incidental reason is not proof that the intended
        # constraint fires: a case corrupted in transit would still count
        # as refused while the rule it names is broken. Bind each known-bad
        # case to the exact instance location and keyword that must refuse
        # it. The keyword is null where a boolean false schema refuses,
        # because jsonschema reports no keyword for those.
        declared = case.get("expected_refusal")
        if not isinstance(declared, dict) or "pointer" not in declared or "keyword" not in declared:
            failures.append(
                f"{case['name']}: known-bad case does not declare the constraint that must refuse it"
            )
        elif not any(
            "/" + "/".join(str(part) for part in error.absolute_path) == declared["pointer"]
            and error.validator == declared["keyword"]
            for error in errors
        ):
            observed = [
                ("/" + "/".join(str(part) for part in error.absolute_path), error.validator)
                for error in errors
            ]
            failures.append(
                f"{case['name']}: refused, but not at its declared constraint "
                f"{declared['pointer']!r} by {declared['keyword']!r}; got {observed}"
            )
    return failures


def attribution_self_test(manifest: dict) -> list[str]:
    """Prove on every run that the binding check itself fires.

    A gate without a known-bad proof is prose (law 11). Two tampered copies
    of the first known-bad case must each be refused by the attribution
    check: one declaring a constraint that never fires, one declaring
    nothing at all. Fail closed if either sails through.
    """
    template = next((c for c in manifest["cases"] if c["expect"] == "invalid"), None)
    if template is None:
        return ["attribution self-test found no known-bad case to tamper with"]
    failures: list[str] = []
    misdeclared = json.loads(json.dumps(template))
    misdeclared["expected_refusal"] = {"pointer": "/odeya-self-test/never-fires", "keyword": "const"}
    if not any("refused, but not at its declared constraint" in f for f in evaluate_case(misdeclared)):
        failures.append("attribution self-test: a misdeclared constraint was not detected")
    undeclared = json.loads(json.dumps(template))
    undeclared.pop("expected_refusal", None)
    if not any("does not declare the constraint" in f for f in evaluate_case(undeclared)):
        failures.append("attribution self-test: a missing declaration was not detected")
    return failures


def main() -> int:
    manifest = load_json(CASES)
    failures: list[str] = attribution_self_test(manifest)
    for case in manifest["cases"]:
        failures.extend(evaluate_case(case))

    if failures:
        print("Architecture review schema cases failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        f"Architecture review schema cases passed: {len(manifest['cases'])} "
        "(structural evidence only; Gate A remains unaccepted)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
