#!/usr/bin/env python3
"""Observe exact PRQ-002E artifact bytes without deciding conformance.

This observer is deliberately smaller than a canonicalization implementation.
It independently inventories retained bytes, strict JSON parseability, raw
number lexemes, declared identities, and literal ``type: number`` assertions.
The parent comparator owns expectations and authority nonclaims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Any


SUITE_ID = "prq-002e-profile-0.3-construction.0001"
OBSERVER_ID = "python-stdlib-construction-observer.0001"
CHALLENGE_RE = re.compile(r"^challenge-v1:[0-9a-f]{64}$")
NUMBER_RE = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
)
INTEGER_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
DOMAIN_RE = re.compile(r"^odeya-[a-z0-9-]+-v[0-9]+$")
PROFILE_RE = re.compile(r"^urn:odeya:canonicalization:[a-z0-9.-]+$")
MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
EXPECTED_ARTIFACTS = [
    (
        "schema_resource_record_schema",
        "schemas/schema-resource-record-v0-2.schema.json",
    ),
    (
        "aggregate_state_subject_record_schema",
        "schemas/aggregate-state-subject-record-v0-2.schema.json",
    ),
    (
        "reducer_contract_record_schema",
        "schemas/reducer-contract-record-v0-2.schema.json",
    ),
    (
        "event_contract_record_schema",
        "schemas/event-contract-record-v0-2.schema.json",
    ),
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
    (
        "event_contract_registry_schema",
        "schemas/event-contract-registry-v0-8.schema.json",
    ),
    (
        "profile_core_schema",
        "schemas/canonicalization-profile-core-v0-7.schema.json",
    ),
    (
        "profile_evidence_schema",
        "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json",
    ),
    (
        "profile_migration_schema",
        "schemas/canonicalization-profile-migration-v0-2.schema.json",
    ),
    (
        "profile_core",
        "architecture/canonicalization-profile-core-0.3-candidate.json",
    ),
    (
        "profile_evidence",
        "architecture/canonicalization-profile-0.3-candidate-evidence.json",
    ),
    (
        "profile_migration",
        "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json",
    ),
]
EXPECTED_MANIFEST_KEYS = {
    "schema_version",
    "artifact_class",
    "suite_id",
    "manifest_id",
    "answer_free",
    "expected_outcomes_included",
    "peer_results_included",
    "artifact_count",
    "artifacts",
    "network_access_allowed",
    "environment_path_discovery_allowed",
    "expectation_manifest_may_be_passed_to_observer",
    "peer_source_may_be_passed_to_observer",
    "peer_result_may_be_passed_to_observer",
    "product_identity_computation_allowed",
    "authority_claim_allowed",
}


class DuplicateKeyError(ValueError):
    """Raised before an object mapping can erase a duplicate decoded key."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate object member: {key!r}")
        result[key] = value
    return result


def reject_nonfinite_constant(token: str) -> Any:
    raise ValueError(f"non-finite JSON constant is forbidden: {token}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_lexical(raw: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def strict_repository_file(root: Path, relative: str) -> tuple[Path, bytes]:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe repository path: {relative}")
    lexical = root / candidate
    mode = lexical.lstat().st_mode
    if not stat.S_ISREG(mode) or lexical.is_symlink():
        raise ValueError(f"artifact is not a non-symlink regular file: {relative}")
    resolved = lexical.resolve(strict=True)
    resolved.relative_to(root)
    return resolved, resolved.read_bytes()


def number_tokens(raw_text: str) -> list[str]:
    """Return JSON number lexemes while ignoring all string contents."""

    tokens: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(raw_text):
        character = raw_text[index]
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            index += 1
            continue
        if character == "-" or character.isdigit():
            match = NUMBER_RE.match(raw_text, index)
            if match is None:
                raise ValueError(f"unclassified numeric-looking byte at offset {index}")
            tokens.append(match.group(0))
            index = match.end()
            continue
        index += 1
    if in_string or escaped:
        raise ValueError("unterminated JSON string")
    return tokens


def negative_zero(token: str) -> bool:
    if not token.startswith("-"):
        return False
    significand = re.split(r"[eE]", token[1:], maxsplit=1)[0].replace(".", "")
    return bool(significand) and set(significand) == {"0"}


def walk_strings(value: Any) -> tuple[list[str], list[str]]:
    domains: set[str] = set()
    profiles: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, str):
            if DOMAIN_RE.fullmatch(node):
                domains.add(node)
            if PROFILE_RE.fullmatch(node):
                profiles.add(node)

    walk(value)
    return sorted(domains), sorted(profiles)


def count_literal_type_number_occurrences(value: Any) -> int:
    count = 0

    def walk(node: Any) -> None:
        nonlocal count
        if isinstance(node, dict):
            declared_type = node.get("type")
            if declared_type == "number" or (
                isinstance(declared_type, list) and "number" in declared_type
            ):
                count += 1
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return count


def declared_identity(document: dict[str, Any]) -> str | None:
    for key in ("$id", "profile_id", "migration_id"):
        value = document.get(key)
        if isinstance(value, str):
            return value
    return None


def observe_row(
    root: Path,
    sequence_index: int,
    entry: dict[str, Any],
) -> dict[str, Any]:
    role = entry.get("role")
    relative = entry.get("repository_path")
    if not isinstance(role, str) or not isinstance(relative, str):
        raise ValueError("input manifest entry requires string role and repository_path")
    _path, raw = strict_repository_file(root, relative)
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"BOM is forbidden: {relative}")
    text = raw.decode("utf-8", errors="strict")
    document = json.loads(
        text,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_nonfinite_constant,
    )
    if not isinstance(document, dict):
        raise ValueError(f"artifact root must be an object: {relative}")
    tokens = number_tokens(text)
    integer_tokens = [token for token in tokens if INTEGER_RE.fullmatch(token)]
    fraction_or_exponent = [
        token for token in tokens if not INTEGER_RE.fullmatch(token)
    ]
    out_of_domain = [
        token
        for token in integer_tokens
        if not MIN_SAFE_INTEGER <= int(token) <= MAX_SAFE_INTEGER
    ]
    domains, profiles = walk_strings(document)
    return {
        "sequence_index": sequence_index,
        "role": role,
        "repository_path": relative,
        "raw_sha256": sha256_lexical(raw),
        "byte_count": len(raw),
        "declared_identity": declared_identity(document),
        "schema_version": document.get("schema_version"),
        "raw_number_token_count": len(tokens),
        "integer_token_count": len(integer_tokens),
        "fraction_or_exponent_token_count": len(fraction_or_exponent),
        "negative_zero_token_count": sum(negative_zero(token) for token in tokens),
        "overlong_number_token_count": sum(
            len(token.encode("ascii")) > 128 for token in tokens
        ),
        "out_of_safe_integer_domain_token_count": len(out_of_domain),
        "ordered_number_token_sha256": sha256_lexical(canonical_bytes(tokens)),
        "literal_type_number_occurrence_count": (
            count_literal_type_number_occurrences(document)
        ),
        "domain_literals": domains,
        "profile_literals": profiles,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--challenge", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if CHALLENGE_RE.fullmatch(args.challenge) is None:
        raise ValueError("challenge does not match the closed lexical contract")
    root = Path(args.root).resolve(strict=True)
    manifest_path = Path(args.manifest).resolve(strict=True)
    manifest_path.relative_to(root)
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_nonfinite_constant,
    )
    if not isinstance(manifest, dict):
        raise ValueError("input manifest root must be an object")
    if set(manifest) != EXPECTED_MANIFEST_KEYS:
        raise ValueError("input manifest member inventory drifted")
    expected_scalars = {
        "schema_version": "0.1.0",
        "artifact_class": "profile_0_3_construction_observer_input_manifest",
        "suite_id": SUITE_ID,
        "manifest_id": "prq-002e-profile-0.3-construction-inputs.0001",
        "answer_free": True,
        "expected_outcomes_included": False,
        "peer_results_included": False,
        "artifact_count": len(EXPECTED_ARTIFACTS),
        "network_access_allowed": False,
        "environment_path_discovery_allowed": False,
        "expectation_manifest_may_be_passed_to_observer": False,
        "peer_source_may_be_passed_to_observer": False,
        "peer_result_may_be_passed_to_observer": False,
        "product_identity_computation_allowed": False,
        "authority_claim_allowed": False,
    }
    if any(
        type(manifest.get(key)) is not type(expected)
        or manifest.get(key) != expected
        for key, expected in expected_scalars.items()
    ):
        raise ValueError("input manifest identity, count, or nonclaim drifted")
    entries = manifest.get("artifacts")
    if not isinstance(entries, list):
        raise ValueError("input manifest artifacts must be an array")
    observed_inventory = [
        (entry.get("role"), entry.get("repository_path"))
        if isinstance(entry, dict) and set(entry) == {"role", "repository_path"}
        else None
        for entry in entries
    ]
    if observed_inventory != EXPECTED_ARTIFACTS:
        raise ValueError("input manifest exact ordered artifact inventory drifted")
    rows = [
        observe_row(root, sequence_index, entry)
        for sequence_index, entry in enumerate(entries, start=1)
    ]
    projection = {
        "schema_version": "0.1.0",
        "artifact_class": "profile_0_3_construction_observation",
        "suite_id": SUITE_ID,
        "observer_id": OBSERVER_ID,
        "challenge": args.challenge,
        "artifact_count": len(rows),
        "artifacts": rows,
        "network_access_requested": False,
        "expectations_received": False,
        "peer_source_received": False,
        "peer_result_received": False,
        "canonicalization_conformance_claimed": False,
        "product_identity_computed": False,
        "authority_claimed": False,
    }
    print(canonical_bytes(projection).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
