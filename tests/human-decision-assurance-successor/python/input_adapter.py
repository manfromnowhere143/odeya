#!/usr/bin/env python3
"""Expectation-free input adapter for the Python HDA successor evaluator.

This module deliberately owns its JSON parsing and RFC 6902 subset. It never
opens the private answer corpus and never imports an adapter from another
implementation.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import evaluator


class InputError(ValueError):
    """Raised when evaluator input is not exact and closed."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise InputError(f"non-finite JSON number is forbidden: {value}")


def load_json(path: Path, expected_artifact_class: str | None = None) -> Any:
    if path.name == "cases.json":
        raise InputError("the private answer corpus is forbidden evaluator input")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InputError(f"cannot read strict UTF-8 JSON {path}: {exc}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, InputError) as exc:
        raise InputError(f"invalid strict JSON {path}: {exc}") from exc
    if expected_artifact_class is not None:
        if not isinstance(value, dict) or value.get("artifact_class") != expected_artifact_class:
            raise InputError(f"unexpected artifact_class in {path}")
    return value


def _tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise InputError(f"invalid JSON Pointer: {pointer}")
    result: list[str] = []
    for encoded in pointer[1:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if "~" in encoded.replace("~1", "").replace("~0", ""):
            raise InputError(f"invalid JSON Pointer escape: {pointer}")
        result.append(token)
    return result


def _array_index(token: str, length: int, allow_append: bool) -> int:
    if token == "-":
        if allow_append:
            return length
        raise InputError("'-' is valid only for array add")
    if not token or (len(token) > 1 and token.startswith("0")) or not token.isascii() or not token.isdigit():
        raise InputError(f"invalid array index: {token}")
    index = int(token)
    limit = length if allow_append else length - 1
    if index < 0 or index > limit:
        raise InputError(f"array index out of bounds: {token}")
    return index


def _resolve(document: Any, pointer: str) -> Any:
    current = document
    for token in _tokens(pointer):
        if isinstance(current, list):
            current = current[_array_index(token, len(current), False)]
        elif isinstance(current, dict):
            if token not in current:
                raise InputError(f"JSON Pointer member is absent: {pointer}")
            current = current[token]
        else:
            raise InputError(f"JSON Pointer traverses a scalar: {pointer}")
    return current


def _parent(document: Any, pointer: str) -> tuple[Any, str]:
    tokens = _tokens(pointer)
    if not tokens:
        raise InputError("root replacement is not permitted by this corpus")
    parent_pointer = "" if len(tokens) == 1 else "/" + "/".join(
        token.replace("~", "~0").replace("/", "~1") for token in tokens[:-1]
    )
    return _resolve(document, parent_pointer), tokens[-1]


def _add(document: Any, pointer: str, value: Any) -> None:
    parent, token = _parent(document, pointer)
    if isinstance(parent, list):
        parent.insert(_array_index(token, len(parent), True), value)
    elif isinstance(parent, dict):
        parent[token] = value
    else:
        raise InputError(f"add parent is a scalar: {pointer}")


def _remove(document: Any, pointer: str) -> Any:
    parent, token = _parent(document, pointer)
    if isinstance(parent, list):
        return parent.pop(_array_index(token, len(parent), False))
    if isinstance(parent, dict):
        if token not in parent:
            raise InputError(f"remove target is absent: {pointer}")
        return parent.pop(token)
    raise InputError(f"remove parent is a scalar: {pointer}")


def apply_patch(document: Any, operations: Any) -> Any:
    if not isinstance(operations, list):
        raise InputError("mutations must be an array")
    result = copy.deepcopy(document)
    for operation in operations:
        if not isinstance(operation, dict):
            raise InputError("each mutation must be an object")
        op = operation.get("op")
        path = operation.get("path")
        if op not in {"add", "copy", "move", "remove", "replace"} or not isinstance(path, str):
            raise InputError("unsupported or malformed mutation")
        if op == "add":
            if set(operation) != {"op", "path", "value"}:
                raise InputError("add mutation has unexpected members")
            _add(result, path, copy.deepcopy(operation["value"]))
        elif op == "remove":
            if set(operation) != {"op", "path"}:
                raise InputError("remove mutation has unexpected members")
            _remove(result, path)
        elif op == "replace":
            if set(operation) != {"op", "path", "value"}:
                raise InputError("replace mutation has unexpected members")
            _resolve(result, path)
            _remove(result, path)
            _add(result, path, copy.deepcopy(operation["value"]))
        else:
            if set(operation) != {"op", "from", "path"} or not isinstance(operation.get("from"), str):
                raise InputError(f"{op} mutation has unexpected members")
            value = copy.deepcopy(_resolve(result, operation["from"]))
            if op == "move":
                _remove(result, operation["from"])
            _add(result, path, value)
    return result


def materialize(vectors: dict[str, Any], vector_id: str) -> dict[str, Any]:
    base = vectors.get("base_input")
    entries = vectors.get("vectors")
    if not isinstance(base, dict) or not isinstance(entries, list):
        raise InputError("vector corpus lacks base_input or vectors")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("vector_id"), str):
            raise InputError("vector entry is malformed")
        if entry["vector_id"] in by_id:
            raise InputError(f"duplicate vector_id: {entry['vector_id']}")
        by_id[entry["vector_id"]] = entry

    def visit(current_id: str, stack: tuple[str, ...]) -> dict[str, Any]:
        if current_id in stack:
            raise InputError("vector inheritance cycle: " + " -> ".join((*stack, current_id)))
        entry = by_id.get(current_id)
        if entry is None:
            raise InputError(f"unknown vector_id: {current_id}")
        allowed = {"vector_id", "base_vector_id", "mutations"}
        if set(entry) - allowed:
            raise InputError(f"vector {current_id} has unexpected members")
        parent_id = entry.get("base_vector_id")
        subject = copy.deepcopy(base) if parent_id is None else visit(parent_id, (*stack, current_id))
        return apply_patch(subject, entry.get("mutations", []))

    return visit(vector_id, ())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vectors", type=Path, required=True)
    parser.add_argument("--ruleset", type=Path, required=True)
    parser.add_argument("--resolver", type=Path, required=True)
    parser.add_argument("--vector-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vectors = load_json(
        args.vectors,
        "human_decision_assurance_successor_expectation_free_evaluator_inputs",
    )
    ruleset = load_json(
        args.ruleset,
        "human_decision_assurance_individual_eligibility_ruleset_candidate",
    )
    resolver = load_json(
        args.resolver,
        "human_decision_assurance_content_address_resolver_profile_candidate",
    )
    subject = materialize(vectors, args.vector_id)
    result = evaluator.evaluate(subject, ruleset, resolver)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
