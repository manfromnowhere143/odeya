"""Deterministically regenerate the PRQ-002F suite metadata files.

Emits the answer-free input manifest, both source manifests, the Python
dependency lock, and the zero-dependency Node package pair from current
repository bytes. Rerunning after any runner byte change refreshes the
bindings; `--check` verifies that every generated file equals its retained
bytes without writing.

This authoring step retains no expectations and reads no private answers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent
ROOT = SUITE.parent.parent
SUITE_ID = "prq-002f-numeric-trace-conformance.0001"

SUBJECT_ROLES = (
    ("schema_resource_record_schema", "schemas/schema-resource-record-v0-2.schema.json"),
    (
        "aggregate_state_subject_record_schema",
        "schemas/aggregate-state-subject-record-v0-2.schema.json",
    ),
    ("reducer_contract_record_schema", "schemas/reducer-contract-record-v0-2.schema.json"),
    ("event_contract_record_schema", "schemas/event-contract-record-v0-2.schema.json"),
    (
        "ordered_member_map_commitment_schema",
        "schemas/ordered-member-map-commitment-v0-2.schema.json",
    ),
    ("schema_registry_schema", "schemas/schema-registry-v0-9.schema.json"),
    (
        "aggregate_state_subject_registry_schema",
        "schemas/aggregate-state-subject-registry-v0-8.schema.json",
    ),
    ("reducer_registry_schema", "schemas/reducer-registry-v0-8.schema.json"),
    ("event_contract_registry_schema", "schemas/event-contract-registry-v0-8.schema.json"),
    ("profile_core_schema", "schemas/canonicalization-profile-core-v0-7.schema.json"),
    (
        "profile_evidence_schema",
        "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json",
    ),
    ("profile_migration_schema", "schemas/canonicalization-profile-migration-v0-2.schema.json"),
    ("profile_core", "architecture/canonicalization-profile-core-0.3-candidate.json"),
    ("profile_evidence", "architecture/canonicalization-profile-0.3-candidate-evidence.json"),
    (
        "profile_migration",
        "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json",
    ),
)


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def binding(relative: str) -> dict[str, str]:
    raw = (ROOT / relative).read_bytes()
    return {
        "repository_path": relative,
        "raw_sha256": sha256(raw),
        "byte_count_decimal": str(len(raw)),
    }


def encode(document: dict) -> bytes:
    return (
        json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    ).encode("utf-8")


def generated_files() -> dict[str, bytes]:
    input_manifest = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002f_numeric_trace_input_manifest",
        "suite_id": SUITE_ID,
        "manifest_id": "prq-002f-numeric-trace-inputs.0001",
        "answer_free": True,
        "expected_outcomes_included": False,
        "peer_results_included": False,
        "subject_count_decimal": "15",
        "subjects": [
            {"role": role, "repository_path": relative}
            for role, relative in SUBJECT_ROLES
        ],
        "contract_path": (
            "architecture/prq-002f-numeric-trace-conformance-contract-v1-candidate.json"
        ),
        "network_access_allowed": False,
        "environment_path_discovery_allowed": False,
        "expectation_manifest_may_be_passed_to_runner": False,
        "peer_source_may_be_passed_to_runner": False,
        "peer_result_may_be_passed_to_runner": False,
        "product_identity_computation_allowed": False,
        "authority_claim_allowed": False,
    }
    python_sources = [
        (
            "runner",
            "tests/profile-0-3-numeric-trace-conformance/python/runner.py",
        ),
        (
            "dependency_lock",
            "tests/profile-0-3-numeric-trace-conformance/python/dependency-lock.json",
        ),
    ]
    node_sources = [
        (
            "runner",
            "tests/profile-0-3-numeric-trace-conformance/node/runner.mjs",
        ),
        (
            "package_manifest",
            "tests/profile-0-3-numeric-trace-conformance/node/package.json",
        ),
        (
            "package_lock",
            "tests/profile-0-3-numeric-trace-conformance/node/package-lock.json",
        ),
    ]
    python_lock = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002f_numeric_trace_dependency_lock",
        "suite_id": SUITE_ID,
        "implementation_id": "python-stdlib-numeric-trace.0001",
        "runtime": {"family": "CPython", "version": "3.14.2"},
        "third_party_distribution_count_decimal": "0",
        "third_party_distributions": [],
        "standard_library_only": True,
    }
    package_manifest = {
        "name": "prq-002f-numeric-trace-node-runner",
        "version": "0.1.0",
        "private": True,
        "description": (
            "Zero-dependency source-separated Node.js runner for the PRQ-002F "
            "raw-aware numeric trace conformance suite. Architecture evidence "
            "only; no runtime, identity, issuance, or publication authority."
        ),
        "type": "module",
        "engines": {"node": "24.18.0"},
        "dependencies": {},
    }
    package_lock = {
        "name": "prq-002f-numeric-trace-node-runner",
        "version": "0.1.0",
        "lockfileVersion": 3,
        "requires": True,
        "packages": {
            "": {
                "name": "prq-002f-numeric-trace-node-runner",
                "version": "0.1.0",
                "engines": {"node": "24.18.0"},
            }
        },
    }
    files: dict[str, bytes] = {
        "input-manifest.json": encode(input_manifest),
        "python/dependency-lock.json": encode(python_lock),
        "node/package.json": encode(package_manifest),
        "node/package-lock.json": encode(package_lock),
    }

    def source_manifest(
        role: str,
        implementation_id: str,
        language: str,
        runtime_version: str,
        parser_strategy: str,
        sources: list[tuple[str, str]],
    ) -> bytes:
        return encode(
            {
                "schema_version": "0.1.0",
                "artifact_class": "prq_002f_numeric_trace_source_manifest",
                "suite_id": SUITE_ID,
                "role": role,
                "implementation_id": implementation_id,
                "language": language,
                "runtime_version": runtime_version,
                "parser_strategy": parser_strategy,
                "source_file_count_decimal": str(len(sources)),
                "source_files": [
                    {"role": source_role, **binding(relative)}
                    for source_role, relative in sources
                ],
                "allowed_input_roles": [
                    "repository_subjects",
                    "contract",
                    "source_manifest",
                ],
                "subject_rows_hard_coded": True,
                "private_expectation_consumption_allowed": False,
                "peer_source_consumption_allowed": False,
                "peer_result_consumption_allowed": False,
                "network_access_requested": False,
                "filesystem_isolation_proven": False,
            }
        )

    # The Python dependency lock and Node package pair are generated above and
    # bound below, so their bytes must be produced before the manifests bind
    # them. Write-order inside this dict is not retention order; the retainer
    # stages and installs atomically.
    staged_root = {
        "python/dependency-lock.json": files["python/dependency-lock.json"],
        "node/package.json": files["node/package.json"],
        "node/package-lock.json": files["node/package-lock.json"],
    }
    for relative, raw in staged_root.items():
        target = SUITE / relative
        if not target.exists() or target.read_bytes() != raw:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    files["python/source-manifest.json"] = source_manifest(
        "python",
        "python-stdlib-numeric-trace.0001",
        "Python",
        "3.14.2",
        "stdlib_strict_pairs_with_raw_octet_scan_reconciliation",
        python_sources,
    )
    files["node/source-manifest.json"] = source_manifest(
        "node",
        "nodejs-native-numeric-trace.0001",
        "JavaScript",
        "24.18.0",
        "native_recursive_descent_without_json_parse",
        node_sources,
    )
    return files


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    files = generated_files()
    failures: list[str] = []
    for relative, raw in files.items():
        target = SUITE / relative
        if arguments.check:
            if not target.is_file() or target.read_bytes() != raw:
                failures.append(relative)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    if arguments.check and failures:
        print(
            "PRQ-002F suite metadata differs from deterministic regeneration: "
            + ", ".join(sorted(failures))
        )
        return 1
    print(
        ("verified" if arguments.check else "generated")
        + f" {len(files)} deterministic PRQ-002F metadata files"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
