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


def main() -> int:
    manifest = load_json(CASES)
    failures: list[str] = []
    for case in manifest["cases"]:
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
