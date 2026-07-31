"""Deterministically regenerate the PRQ-002G suite metadata files.

Emits both source manifests, the Python dependency lock, and the
zero-dependency Node package pair from current repository bytes. `--check`
verifies every generated file equals its retained bytes without writing.
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
SUITE_ID = "prq-002g-jcs-serialization-conformance.0001"


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
    python_lock = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002g_jcs_conformance_dependency_lock",
        "suite_id": SUITE_ID,
        "implementation_id": "python-stdlib-jcs-serializer.0001",
        "runtime": {"family": "CPython", "version": "3.14.2"},
        "third_party_distribution_count_decimal": "0",
        "third_party_distributions": [],
        "standard_library_only": True,
    }
    package_manifest = {
        "name": "prq-002g-jcs-node-runner",
        "version": "0.1.0",
        "private": True,
        "description": (
            "Zero-dependency source-separated Node.js runner for the PRQ-002G "
            "profile-bounded JCS serialization conformance suite. Architecture "
            "evidence only; no identity, issuance, or publication authority."
        ),
        "type": "module",
        "engines": {"node": "24.18.0"},
        "dependencies": {},
    }
    package_lock = {
        "name": "prq-002g-jcs-node-runner",
        "version": "0.1.0",
        "lockfileVersion": 3,
        "requires": True,
        "packages": {
            "": {
                "name": "prq-002g-jcs-node-runner",
                "version": "0.1.0",
                "engines": {"node": "24.18.0"},
            }
        },
    }
    files: dict[str, bytes] = {
        "python/dependency-lock.json": encode(python_lock),
        "node/package.json": encode(package_manifest),
        "node/package-lock.json": encode(package_lock),
    }
    for relative, raw in files.items():
        target = SUITE / relative
        if not target.exists() or target.read_bytes() != raw:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)

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
                "artifact_class": "prq_002g_jcs_conformance_source_manifest",
                "suite_id": SUITE_ID,
                "role": role,
                "implementation_id": implementation_id,
                "language": language,
                "runtime_version": runtime_version,
                "parser_strategy": parser_strategy,
                "member_ordering_strategy": (
                    "explicit_utf16_be_byte_comparison"
                    if role == "python"
                    else "native_utf16_code_unit_string_comparison"
                ),
                "source_file_count_decimal": str(len(sources)),
                "source_files": [
                    {"role": source_role, **binding(relative)}
                    for source_role, relative in sources
                ],
                "allowed_input_roles": ["vectors", "source_manifest"],
                "private_expectation_consumption_allowed": False,
                "peer_source_consumption_allowed": False,
                "peer_result_consumption_allowed": False,
                "network_access_requested": False,
                "filesystem_isolation_proven": False,
            }
        )

    files["python/source-manifest.json"] = source_manifest(
        "python",
        "python-stdlib-jcs-serializer.0001",
        "Python",
        "3.14.2",
        "stdlib_raw_decode_with_lexeme_hooks",
        [
            ("runner", "tests/profile-0-3-jcs-conformance/python/runner.py"),
            (
                "dependency_lock",
                "tests/profile-0-3-jcs-conformance/python/dependency-lock.json",
            ),
        ],
    )
    files["node/source-manifest.json"] = source_manifest(
        "node",
        "nodejs-native-jcs-serializer.0001",
        "JavaScript",
        "24.18.0",
        "native_recursive_descent_without_json_parse",
        [
            ("runner", "tests/profile-0-3-jcs-conformance/node/runner.mjs"),
            (
                "package_manifest",
                "tests/profile-0-3-jcs-conformance/node/package.json",
            ),
            (
                "package_lock",
                "tests/profile-0-3-jcs-conformance/node/package-lock.json",
            ),
        ],
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
            "PRQ-002G suite metadata differs from deterministic regeneration: "
            + ", ".join(sorted(failures))
        )
        return 1
    print(
        ("verified" if arguments.check else "generated")
        + f" {len(files)} deterministic PRQ-002G metadata files"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
