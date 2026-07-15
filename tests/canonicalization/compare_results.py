#!/usr/bin/env python3
"""Fail-closed comparison for the two Odeya canonicalization evidence paths."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SUITE = Path(__file__).resolve().parent
ROOT = SUITE.parents[1]
DEFAULT_RESULTS = (
    SUITE / "results/python-rfc8785-0.1.4.json",
    SUITE / "results/node-canonicalize-3.0.0.json",
)


class DuplicateKey(ValueError):
    pass


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text("utf-8"), object_pairs_hook=strict_pairs)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case_projection(case: dict[str, Any]) -> dict[str, Any]:
    common = {
        "id": case["id"],
        "input_length": case["input_length"],
        "input_sha256": case["input_sha256"],
        "outcome": case["outcome"],
    }
    if case["outcome"] == "accepted":
        common.update(
            {
                "canonical_length": case["canonical_length"],
                "canonical_hex": case["canonical_hex"],
                "canonical_sha256": case["canonical_sha256"],
            }
        )
    elif case["outcome"] == "refused":
        common["code"] = case["code"]
    else:
        common["error_type"] = case.get("error_type")
    return common


def index_unique(items: list[dict[str, Any]], label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{label} contains an item without an ID")
            continue
        if identifier in indexed:
            errors.append(f"{label} contains duplicate ID {identifier}")
        indexed[identifier] = item
    return indexed


def check_relation(
    relation: dict[str, Any], cases: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    members = relation["members"]
    try:
        selected = [cases[identifier] for identifier in members]
    except KeyError as exc:
        errors.append(f"metamorphic relation {relation['id']} has unknown member {exc.args[0]}")
        return
    if any(case.get("outcome") != "accepted" for case in selected):
        errors.append(f"metamorphic relation {relation['id']} includes a non-accepted case")
        return
    kind = relation["relation"]
    if kind == "same_digest":
        values = {case["canonical_sha256"] for case in selected}
        passed = len(values) == 1
    elif kind == "different_digest":
        values = [case["canonical_sha256"] for case in selected]
        passed = len(values) == len(set(values))
    elif kind == "different_canonical_bytes":
        values = [case["canonical_hex"] for case in selected]
        passed = len(values) == len(set(values))
    else:
        errors.append(f"metamorphic relation {relation['id']} has unknown relation {kind}")
        return
    if not passed:
        errors.append(f"metamorphic relation failed: {relation['id']}")


def validate(result_paths: tuple[Path, Path]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    manifest_path = SUITE / "manifest.json"
    source_lock_path = SUITE / "source-lock.json"
    upstream_path = SUITE / "official/cyberphone/vectors.json"
    manifest = load(manifest_path)
    source_lock = load(source_lock_path)
    upstream = load(upstream_path)

    expectations_path = ROOT / manifest["expectations_path"]
    if digest(expectations_path) != manifest["expectations_sha256"]:
        errors.append("expectations file digest does not match manifest")
    expectations = load(expectations_path)
    expected_cases = index_unique(expectations["cases"], "expectations", errors)
    vectors = index_unique(manifest["vectors"], "manifest vectors", errors)
    if set(expected_cases) != set(vectors):
        errors.append("expectation/vector ID sets differ")

    for identifier in sorted(set(expected_cases) & set(vectors)):
        contract = vectors[identifier]["expect"]
        expected = expected_cases[identifier]
        if contract["outcome"] != expected["outcome"]:
            errors.append(f"manifest/expectation outcome differs for {identifier}")
        if contract["outcome"] == "refused" and contract["code"] != expected.get("code"):
            errors.append(f"manifest/expectation refusal code differs for {identifier}")

    upstream_index = {item["name"]: item for item in upstream["vectors"]}
    for vector in manifest["vectors"]:
        if "upstream_vector" not in vector:
            continue
        retained = upstream_index.get(vector["upstream_vector"])
        expected = expected_cases.get(vector["id"])
        if retained is None or expected is None:
            errors.append(f"missing retained upstream evidence for {vector['id']}")
            continue
        if expected.get("input_sha256") != retained["input_sha256"]:
            errors.append(f"upstream input digest differs for {vector['id']}")
        if expected.get("canonical_hex") != retained["output_hex"]:
            errors.append(f"upstream canonical bytes differ for {vector['id']}")
        if expected.get("canonical_sha256") != retained["output_sha256"]:
            errors.append(f"upstream canonical digest differs for {vector['id']}")

    for entry in manifest["schema_registry"]:
        path = ROOT / entry["path"]
        if not path.is_file() or digest(path) != entry["byte_sha256"]:
            errors.append(f"schema-registry byte drift: {entry['path']}")
    for entry in source_lock["upstream_vectors"]["files"]:
        path = ROOT / entry["path"]
        if not path.is_file() or digest(path) != entry["byte_sha256"]:
            errors.append(f"retained upstream byte drift: {entry['path']}")
    for entry in source_lock["suite_artifacts"]:
        path = ROOT / entry["path"]
        if not path.is_file() or digest(path) != entry["byte_sha256"]:
            errors.append(f"suite artifact byte drift: {entry['path']}")

    results = [load(path) for path in result_paths]
    manifest_sha = digest(manifest_path)
    source_lock_sha = digest(source_lock_path)
    upstream_sha = digest(upstream_path)
    implementation_lock = {
        item["runner"]: item for item in source_lock["implementations"]
    }
    runner_contract = {
        "python": {
            "package": "rfc8785",
            "package_version": "0.1.4",
            "runtime": "CPython",
            "runtime_version": "3.14.2",
            "runner_sha256": digest(SUITE / "runner_python.py"),
            "package_code_sha256": implementation_lock["python"][
                "observed_package_code_sha256"
            ],
        },
        "node": {
            "package": "canonicalize",
            "package_version": "3.0.0",
            "runtime": "Node.js",
            "runtime_version": "20.18.3",
            "runner_sha256": digest(SUITE / "runner_node.mjs"),
            "package_code_sha256": implementation_lock["node"][
                "observed_package_code_sha256"
            ],
        },
    }
    normalized_results: list[dict[str, dict[str, Any]]] = []
    observed_runners: list[str] = []
    for path, result in zip(result_paths, results, strict=True):
        implementation = result.get("implementation", {})
        runner = implementation.get("runner")
        if runner not in runner_contract:
            errors.append(f"unknown result implementation in {path}")
            continue
        observed_runners.append(runner)
        for key, expected_value in runner_contract[runner].items():
            if implementation.get(key) != expected_value:
                errors.append(f"{runner} {key} drift in {path}")
        for key, expected_value in {
            "suite_id": manifest["suite_id"],
            "profile_id": manifest["profile_id"],
            "evidence_label": manifest["evidence_label"],
            "manifest_sha256": manifest_sha,
            "source_lock_sha256": source_lock_sha,
            "upstream_vectors_sha256": upstream_sha,
            "limits": manifest["limits"],
        }.items():
            if result.get(key) != expected_value:
                errors.append(f"{runner} result field drift: {key}")
        observed = index_unique(result.get("cases", []), f"{runner} result cases", errors)
        normalized_results.append(observed)
        if set(observed) != set(expected_cases):
            errors.append(f"{runner} result/expectation ID sets differ")
        for identifier in sorted(set(observed) & set(expected_cases)):
            if case_projection(observed[identifier]) != expected_cases[identifier]:
                errors.append(f"{runner} result differs from exact expectation: {identifier}")
        actual_summary = {
            "total": len(observed),
            "accepted": sum(case.get("outcome") == "accepted" for case in observed.values()),
            "refused": sum(case.get("outcome") == "refused" for case in observed.values()),
            "errors": sum(case.get("outcome") == "error" for case in observed.values()),
        }
        if result.get("summary") != actual_summary:
            errors.append(f"{runner} summary is not a fold of its cases")

    if sorted(observed_runners) != ["node", "python"]:
        errors.append(
            "result pair must contain exactly one python implementation and one node implementation"
        )

    if len(normalized_results) == 2:
        left, right = normalized_results
        if set(left) == set(right):
            for identifier in sorted(left):
                if case_projection(left[identifier]) != case_projection(right[identifier]):
                    errors.append(f"implementation disagreement: {identifier}")
        for relation in manifest["metamorphic_relations"]:
            check_relation(relation, left, errors)
            check_relation(relation, right, errors)
        environments = [result.get("implementation", {}).get("environment") for result in results]
        if not all(isinstance(environment, dict) for environment in environments):
            errors.append("one or both result environments are missing")
        else:
            python_environment, node_environment = environments
            for field in ("operating_system", "operating_system_release", "byte_order"):
                if python_environment.get(field) != node_environment.get(field):
                    errors.append(f"result host environment disagreement: {field}")
            if not python_environment.get("architecture") or not node_environment.get("architecture"):
                errors.append("result host architecture identity is missing")

    receipt = {
        "receipt_version": "0.1.0",
        "status": "pass" if not errors else "fail",
        "suite_id": manifest["suite_id"],
        "profile_id": manifest["profile_id"],
        "case_count": len(expected_cases),
        "accepted_count": sum(item["outcome"] == "accepted" for item in expected_cases.values()),
        "refused_count": sum(item["outcome"] == "refused" for item in expected_cases.values()),
        "metamorphic_relation_count": len(manifest["metamorphic_relations"]),
        "implementation_agreement": not any(
            error.startswith("implementation disagreement") for error in errors
        ),
        "errors": errors,
    }
    return errors, receipt


def main() -> int:
    paths = tuple(Path(value).resolve() for value in sys.argv[1:])
    if not paths:
        paths = DEFAULT_RESULTS
    if len(paths) != 2:
        print("usage: compare_results.py [PYTHON_RESULT NODE_RESULT]", file=sys.stderr)
        return 2
    try:
        errors, receipt = validate(paths)  # type: ignore[arg-type]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "fail", "errors": [f"suite control failure: {type(exc).__name__}"]}, indent=2))
        return 1
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
