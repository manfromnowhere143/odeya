#!/usr/bin/env python3
"""Validate the retained, architecture-only HDA 0.2 successor chain.

The default path verifies retained bytes and replays the expectation-free
corpus with the exact Python 3.14.2 evaluator.  ``--recompute-all`` additionally
requires the pinned Node.js 24.18.0 and Temurin Java 21.0.9 toolchains, executes
the complete retained vector inventory in all three implementations, and
compares the complete raw projections.  This checker never performs a
ceremony, accesses a network, grants authority, or accepts Gate A.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import io
import json
import os
import platform
import re
import struct
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "tests/human-decision-assurance-successor"
FIXTURES = ROOT / "tests/architecture-schema/fixtures"

VECTORS_PATH = SUITE / "vectors.json"
CASES_PATH = SUITE / "cases.json"
CHAIN_CASES_PATH = SUITE / "chain-cases.json"
INPUT_MANIFEST_PATH = SUITE / "input-manifest.json"
NORMATIVE_INPUT_PATH = SUITE / "normative-input-safe-complete-eligible.json"
GENERATION_MANIFEST_PATH = SUITE / "generation-manifest.json"
GENERATOR_PATH = ROOT / "scripts/generate_human_decision_assurance_successor.py"
TOOLCHAIN_LOCK_PATH = ROOT / "tools/repository-release/toolchain.lock.json"
ARCHITECTURE_REQUIREMENTS_SOURCE_PATH = ROOT / "requirements-architecture.txt"
ARCHITECTURE_REQUIREMENTS_LOCK_PATH = (
    ROOT / "tools/repository-release/requirements-architecture.lock"
)
RULESET_PATH = (
    ROOT
    / "architecture/human-decision-assurance-individual-eligibility-ruleset-v2-candidate.json"
)
RESOLVER_PATH = (
    ROOT
    / "architecture/human-decision-assurance-content-address-resolver-profile-v1-candidate.json"
)
CORE_PATH = FIXTURES / "human-decision-assurance-core.valid.json"
DECISION_PATH = FIXTURES / "human-decision-assurance-decision-subject.valid.json"
CANDIDATE_MANIFEST_PATH = (
    ROOT / "tests/architecture-review/fixtures/architecture-candidate-manifest.valid.json"
)
CHALLENGE_PROFILE_PATH = (
    ROOT / "architecture/human-decision-challenge-frame-v2-candidate.json"
)
CHALLENGE_EVIDENCE_PATH = (
    ROOT / "architecture/human-decision-challenge-frame-v2-candidate-evidence.json"
)

EVIDENCE_PATH = FIXTURES / "human-decision-assurance-evidence-v0-2.valid.json"
BACKING_PATH = (
    FIXTURES
    / "human-decision-assurance-backing-byte-verification-receipt.valid.json"
)
COMPARISON_PATH = (
    FIXTURES
    / "human-decision-assurance-eligibility-comparison-receipt.valid.json"
)
SEAL_PATH = FIXTURES / "human-decision-assurance-seal-v0-2.valid.json"

SCHEMA_PATHS = {
    "evidence": ROOT / "schemas/human-decision-assurance-evidence-v0-2.schema.json",
    "backing": ROOT
    / "schemas/human-decision-assurance-backing-byte-verification-receipt.schema.json",
    "result": ROOT
    / "schemas/human-decision-assurance-eligibility-recomputation-result.schema.json",
    "comparison": ROOT
    / "schemas/human-decision-assurance-eligibility-comparison-receipt.schema.json",
    "seal": ROOT / "schemas/human-decision-assurance-seal-v0-2.schema.json",
}

ROLE_KEYS = ("python", "node", "java")
IMPLEMENTATION_ROLES = {
    "python": "python",
    "node": "nodejs_24_18_0",
    "java": "java_21_0_9",
}
TOOLCHAIN_NAMES = {"python": "python", "node": "nodejs", "java": "java"}
TOOLCHAIN_VERSIONS = {"python": "3.14.2", "node": "24.18.0", "java": "21.0.9"}
PYTHON_ISOLATION_FLAGS = ("-B", "-E", "-s")
RESULT_PATHS = {
    "python": FIXTURES
    / "human-decision-assurance-eligibility-recomputation-result-python.valid.json",
    "node": FIXTURES
    / "human-decision-assurance-eligibility-recomputation-result-nodejs-24-18-0.valid.json",
    "java": FIXTURES
    / "human-decision-assurance-eligibility-recomputation-result-java-21-0-9.valid.json",
}
PROJECTION_PATHS = {
    "python": SUITE / "results/python.projection.json",
    "node": SUITE / "results/nodejs-24-18-0.projection.json",
    "java": SUITE / "results/java-21-0-9.projection.json",
}
SOURCE_MANIFEST_PATHS = {
    role: SUITE / role / "source-manifest.json" for role in ROLE_KEYS
}
CONFIG_PATHS = {
    "python": SUITE / "python/config.json",
    "node": SUITE / "node/evaluator-config.json",
    "java": SUITE / "java/evaluator-config.json",
}
DEPENDENCY_LOCK_PATHS = {
    "python": SUITE / "python/requirements.lock",
    "node": SUITE / "node/package-lock.json",
    "java": SUITE / "java/dependency-lock.json",
}
ADAPTER_PATHS = {
    "python": SUITE / "python/input_adapter.py",
    "node": SUITE / "node/src/input-adapter.mjs",
    "java": SUITE / "java/src/odeya/hda/java21/InputAdapter.java",
}
RUNTIME_PROFILE_PATHS = {
    "python": SUITE / "runtime/python-3-14-2.profile.json",
    "node": SUITE / "runtime/nodejs-24-18-0.profile.json",
    "java": SUITE / "runtime/java-21-0-9.profile.json",
}
SOURCE_ROOTS = {role: SUITE / role for role in ROLE_KEYS}
IMPLEMENTATION_ARTIFACT_IDS = {
    "python": {
        "source_binding": "hda-evaluator-source-manifest.python.3_14_2.0001",
        "toolchain_profile_binding": "hda-runtime-profile.python.3_14_2.0001",
        "dependency_lock_binding": "hda-dependency-lock.python.0001",
        "configuration_binding": "hda-evaluator-configuration.python.0001",
        "input_adapter_binding": "hda-input-adapter.python.0001",
        "raw_projection_binding": "hda-eligibility-projection.python.synthetic.0002",
        "result_id": "hda-recomputation-result.python.synthetic.0002",
    },
    "node": {
        "source_binding": "hda-evaluator-source-manifest.nodejs_24_18_0.0001",
        "toolchain_profile_binding": "hda-runtime-profile.nodejs_24_18_0.0001",
        "dependency_lock_binding": "hda-dependency-lock.nodejs_24_18_0.0001",
        "configuration_binding": "hda-evaluator-configuration.nodejs_24_18_0.0001",
        "input_adapter_binding": "hda-input-adapter.nodejs_24_18_0.0001",
        "raw_projection_binding": "hda-eligibility-projection.nodejs_24_18_0.synthetic.0002",
        "result_id": "hda-recomputation-result.nodejs_24_18_0.synthetic.0002",
    },
    "java": {
        "source_binding": "hda-evaluator-source-manifest.java_21_0_9.0001",
        "toolchain_profile_binding": "hda-runtime-profile.java_21_0_9.0001",
        "dependency_lock_binding": "hda-dependency-lock.java_21_0_9.0001",
        "configuration_binding": "hda-evaluator-configuration.java_21_0_9.0001",
        "input_adapter_binding": "hda-input-adapter.java_21_0_9.0001",
        "raw_projection_binding": "hda-eligibility-projection.java_21_0_9.synthetic.0002",
        "result_id": "hda-recomputation-result.java_21_0_9.synthetic.0002",
    },
}

RESULT_SCHEMA_ID = (
    "urn:odeya:schema:human-decision-assurance-eligibility-recomputation-result:0.1.0"
)
EVIDENCE_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-evidence:0.2.0"
BACKING_SCHEMA_ID = (
    "urn:odeya:schema:human-decision-assurance-backing-byte-verification-receipt:0.1.0"
)
COMPARISON_SCHEMA_ID = (
    "urn:odeya:schema:human-decision-assurance-eligibility-comparison-receipt:0.1.0"
)
SEAL_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-seal:0.2.0"
RULESET_ID = "urn:odeya:human-decision-assurance-eligibility:0.2.0-candidate"
RESOLVER_ID = (
    "urn:odeya:human-decision-assurance:content-address-resolver:0.1.0-candidate"
)
VECTOR_CORPUS_ARTIFACT_ID = "hda-successor-vectors.0002"
NORMATIVE_INPUT_ARTIFACT_ID = (
    "hda-successor-normative-input.safe-complete-eligible.0002"
)
INPUT_MANIFEST_ARTIFACT_ID = "hda-successor-input-manifest.synthetic.0002"
BACKING_RECEIPT_ARTIFACT_ID = "hda-backing-byte-receipt.synthetic.0002"
COMPARISON_ARTIFACT_ID = "hda-comparison-receipt.synthetic.0002"
SEAL_ARTIFACT_ID = "hda-seal.synthetic.0003"
GENERATION_MANIFEST_ARTIFACT_ID = (
    "hda-successor-generation-manifest.synthetic.0005"
)
PREDECESSOR_SUBJECT = {
    "commit": "86c0f1ed8ba20d74324d64529bf5435a0524f4cd",
    "tree": "0465eac6adf3f49629e72b1c9e6dce6d4acd121c",
    "sole_parent": "34cad10a42027730a515614fc0a5bd664dd8933b",
    "generation_manifest_artifact_id": (
        "hda-successor-generation-manifest.synthetic.0001"
    ),
    "generation_manifest_raw_sha256": (
        "sha256:f401a95c52ccc49791872584971450c723d3c9d2632d66cbd3e9761fea26e247"
    ),
    "generation_manifest_byte_count": 16050,
    "vector_corpus_raw_sha256": (
        "sha256:c81d7d9636d5a4f79a545bbad0ef5454ab8a4bb171d896e0035f1096b2c9cc1a"
    ),
    "stale_authentication_challenge_id": (
        "sha256:1b19ecdf21c6a4d9644fe18757cbd11d1bd32b4a0059a23b2e66ff7363e23a05"
    ),
    "disposition": "invalid_stale_phase_two_authentication_challenge_binding",
    "retention": "exact_git_parent_object_and_context_review_evidence",
}
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
UTC_MICROSECOND_RE = re.compile(
    rb"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    rb"\.[0-9]{6}Z$"
)
CONFIRMATION_FRAME_MAGIC = b"ODEYA-HDA-CONFIRMATION-RECEIPT-V1"
CONFIRMATION_FRAME_FIELDS = (
    "presentation_challenge_id",
    "displayed_bytes_sha256",
    "displayed_byte_count",
    "rendering_profile_id",
    "confirmation_gesture_kind",
    "confirmation_gesture_at",
)
CHALLENGE_FRAME_MAGIC = "ODEYA-HDA-CHALLENGE-FRAME-V2"
PRESENTATION_CHALLENGE_FIELDS = (
    "core_schema_resource_id",
    "core_raw_sha256",
    "decision_schema_resource_id",
    "decision_raw_sha256",
    "candidate_schema_resource_id",
    "candidate_raw_sha256",
    "session_id",
    "issued_at",
    "expires_at",
    "relying_party_id",
    "expected_origin",
    "nonce",
)
AUTHENTICATION_CHALLENGE_FIELDS = (
    *PRESENTATION_CHALLENGE_FIELDS,
    "presentation_challenge_id",
    "confirmation_receipt_raw_sha256",
    "confirmation_receipt_profile_id",
)
OUTPUT_FIELD_ORDER = (
    "participant_id",
    "domain_results",
    "categorical_results",
    "categorical_failures",
    "final_disposition",
    "reason_codes",
)
OUTPUT_KEYS = frozenset(OUTPUT_FIELD_ORDER)
ANSWER_ONLY_KEYS = {
    "expected_disposition",
    "expected_reason_codes",
    "expected_errors",
    "intent_errors",
    "domain_results",
    "categorical_results",
    "categorical_failures",
    "final_disposition",
    "reason_codes",
    "agreed_projection",
}


class DuplicateMember(ValueError):
    """Raised before duplicate JSON object names can collapse."""


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateMember(key)
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def loads_json_object(raw: bytes, label: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: invalid strict UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}: expected one JSON object")
    return value


def load_json(path: Path) -> dict[str, Any]:
    return loads_json_object(path.read_bytes(), str(path.relative_to(ROOT)))


def raw_sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def path_binding(path: Path) -> tuple[str, int]:
    raw = path.read_bytes()
    return raw_sha256(raw), len(raw)


def add_error(errors: list[str], code: str, detail: str | None = None) -> None:
    errors.append(code if detail is None else f"{code}: {detail}")


def error_codes(errors: Iterable[str]) -> set[str]:
    return {item.split(":", 1)[0] for item in errors}


def sorted_unique_ascii(values: Any) -> bool:
    return (
        isinstance(values, list)
        and all(isinstance(value, str) and value.isascii() for value in values)
        and values == sorted(set(values), key=lambda value: value.encode("ascii"))
    )


def strict_json_document(raw: bytes) -> bool:
    """Check strict UTF-8 JSON without requiring an object at the root."""
    try:
        json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=_unique_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeError, ValueError, json.JSONDecodeError):
        return False
    return True


def _read_cbor_argument(raw: bytes, offset: int, additional: int) -> tuple[int, int]:
    if additional < 24:
        return additional, offset
    width = {24: 1, 25: 2, 26: 4, 27: 8}.get(additional)
    if width is None or offset + width > len(raw):
        raise ValueError("indefinite or truncated CBOR argument")
    value = int.from_bytes(raw[offset : offset + width], "big")
    if (
        (width == 1 and value < 24)
        or (width == 2 and value <= 0xFF)
        or (width == 4 and value <= 0xFFFF)
        or (width == 8 and value <= 0xFFFFFFFF)
    ):
        raise ValueError("non-shortest CBOR argument")
    return value, offset + width


def _read_cbor_item(raw: bytes, offset: int, depth: int = 0) -> int:
    if depth > 64 or offset >= len(raw):
        raise ValueError("truncated or over-nested CBOR")
    initial = raw[offset]
    offset += 1
    major = initial >> 5
    additional = initial & 31
    value, offset = _read_cbor_argument(raw, offset, additional)
    if major in {0, 1}:
        return offset
    if major in {2, 3}:
        end = offset + value
        if end > len(raw):
            raise ValueError("truncated CBOR string")
        if major == 3:
            raw[offset:end].decode("utf-8", errors="strict")
        return end
    if major == 4:
        for _ in range(value):
            offset = _read_cbor_item(raw, offset, depth + 1)
        return offset
    if major == 5:
        for _ in range(value * 2):
            offset = _read_cbor_item(raw, offset, depth + 1)
        return offset
    if major == 6:
        return _read_cbor_item(raw, offset, depth + 1)
    if major == 7 and additional < 28:
        return offset
    raise ValueError("unsupported CBOR item")


def strict_cbor_document(raw: bytes) -> bool:
    try:
        return _read_cbor_item(raw, 0) == len(raw)
    except (UnicodeError, ValueError):
        return False


def parse_confirmation_frame(raw: bytes) -> dict[str, bytes] | None:
    """Parse the exact receipt frame without normalizing or re-encoding it."""
    try:
        if not raw.startswith(CONFIRMATION_FRAME_MAGIC):
            return None
        offset = len(CONFIRMATION_FRAME_MAGIC)
        if offset + 2 > len(raw):
            return None
        field_count = struct.unpack_from(">H", raw, offset)[0]
        offset += 2
        if field_count != len(CONFIRMATION_FRAME_FIELDS):
            return None
        fields: dict[str, bytes] = {}
        for expected_name in CONFIRMATION_FRAME_FIELDS:
            if offset + 2 > len(raw):
                return None
            name_size = struct.unpack_from(">H", raw, offset)[0]
            offset += 2
            if offset + name_size + 4 > len(raw):
                return None
            name = raw[offset : offset + name_size].decode("ascii", errors="strict")
            offset += name_size
            value_size = struct.unpack_from(">I", raw, offset)[0]
            offset += 4
            if name != expected_name or offset + value_size > len(raw):
                return None
            fields[name] = raw[offset : offset + value_size]
            offset += value_size
        if offset != len(raw):
            return None
        if (
            len(fields["presentation_challenge_id"]) != 32
            or len(fields["displayed_bytes_sha256"]) != 32
            or len(fields["displayed_byte_count"]) != 4
            or not fields["rendering_profile_id"]
            or not fields["confirmation_gesture_kind"]
        ):
            return None
        fields["rendering_profile_id"].decode("ascii", errors="strict")
        fields["confirmation_gesture_kind"].decode("ascii", errors="strict")
        if UTC_MICROSECOND_RE.fullmatch(fields["confirmation_gesture_at"]) is None:
            return None
        return fields
    except (UnicodeError, struct.error):
        return None


def challenge_digest_octets(value: Any, label: str) -> bytes:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{label} is not one lowercase sha256 digest")
    return bytes.fromhex(value[7:])


def challenge_nonce_octets(value: Any, label: str) -> bytes:
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[0-9a-f]{64}", value) is None
    ):
        raise ValueError(f"{label} is not one 32-octet lowercase nonce")
    return bytes.fromhex(value)


def challenge_ascii(value: Any, label: str) -> bytes:
    if not isinstance(value, str) or not value or not value.isascii():
        raise ValueError(f"{label} is not nonempty ASCII")
    return value.encode("ascii")


def encode_profile_ordered_frame(
    magic: str, ordered_names: Sequence[str], values: Mapping[str, bytes]
) -> bytes:
    """Encode from the profile's order and a separately constructed value map."""
    output = bytearray(challenge_ascii(magic, "challenge frame magic"))
    output.extend(struct.pack(">H", len(ordered_names)))
    for name in ordered_names:
        name_raw = challenge_ascii(name, "challenge frame field name")
        value = values[name]
        output.extend(struct.pack(">H", len(name_raw)))
        output.extend(name_raw)
        output.extend(struct.pack(">I", len(value)))
        output.extend(value)
    return bytes(output)


def recompute_successor_phase_two_challenge(
    retained: "Retained", receipt_digest: str | None, errors: list[str]
) -> dict[str, Any] | None:
    """Derive phase two from the exact profile, source vector, and receipt digest.

    This implementation is deliberately profile-order driven and does not call
    the generator.  The retained ADR 0093 evidence supplies only shared inputs,
    phase intervals, and nonces; its predecessor receipt digest and phase-two
    outputs are not consumed.
    """
    if receipt_digest is None:
        return None
    profile = retained.challenge_profile
    evidence = retained.challenge_evidence
    binary = profile.get("binary_frame")
    receipt_profile = profile.get("confirmation_receipt")
    if (
        not isinstance(binary, dict)
        or not isinstance(receipt_profile, dict)
        or binary.get("magic_ascii") != CHALLENGE_FRAME_MAGIC
        or tuple(binary.get("presentation_phase_ordered_fields", ()))
        != PRESENTATION_CHALLENGE_FIELDS
        or tuple(binary.get("authentication_phase_ordered_fields", ()))
        != AUTHENTICATION_CHALLENGE_FIELDS
        or binary.get("appended_authentication_fields_must_be_last") is not True
        or binary.get("field_reordering_allowed") is not False
        or receipt_profile.get("receipt_profile_id")
        != "odeya-human-decision-confirmation-receipt-v1-candidate"
    ):
        add_error(errors, "backing_challenge_profile_contract_mismatch")
        return None
    profile_digest, profile_count = path_binding(CHALLENGE_PROFILE_PATH)
    if evidence.get("profile_binding") != {
        "path": str(CHALLENGE_PROFILE_PATH.relative_to(ROOT)),
        "profile_id": profile.get("profile_id"),
        "profile_version": profile.get("profile_version"),
        "raw_sha256": profile_digest,
        "byte_count": profile_count,
    }:
        add_error(errors, "backing_challenge_evidence_profile_binding_mismatch")
        return None
    vector = evidence.get("synthetic_test_vector")
    if not isinstance(vector, dict):
        add_error(errors, "backing_challenge_source_vector_missing")
        return None
    shared = vector.get("shared_inputs")
    presentation = vector.get("presentation_phase")
    authentication = vector.get("authentication_phase")
    if not all(
        isinstance(value, dict)
        for value in (shared, presentation, authentication)
    ):
        add_error(errors, "backing_challenge_source_vector_incomplete")
        return None
    try:
        shared_values = {
            "core_schema_resource_id": challenge_ascii(
                shared.get("core_schema_resource_id"), "core schema resource id"
            ),
            "core_raw_sha256": challenge_digest_octets(
                shared.get("core_raw_sha256"), "core raw digest"
            ),
            "decision_schema_resource_id": challenge_ascii(
                shared.get("decision_schema_resource_id"),
                "decision schema resource id",
            ),
            "decision_raw_sha256": challenge_digest_octets(
                shared.get("decision_raw_sha256"), "decision raw digest"
            ),
            "candidate_schema_resource_id": challenge_ascii(
                shared.get("candidate_schema_resource_id"),
                "candidate schema resource id",
            ),
            "candidate_raw_sha256": challenge_digest_octets(
                shared.get("candidate_raw_sha256"), "candidate raw digest"
            ),
            "session_id": challenge_ascii(shared.get("session_id"), "session id"),
            "relying_party_id": challenge_ascii(
                shared.get("relying_party_id"), "relying-party id"
            ),
            "expected_origin": challenge_ascii(
                shared.get("expected_origin"), "expected origin"
            ),
        }

        def phase_values(phase: Mapping[str, Any], label: str) -> dict[str, bytes]:
            return {
                "issued_at": challenge_ascii(
                    phase.get("issued_at"), f"{label} issued_at"
                ),
                "expires_at": challenge_ascii(
                    phase.get("expires_at"), f"{label} expires_at"
                ),
                "nonce": challenge_nonce_octets(
                    phase.get("nonce_hex"), f"{label} nonce"
                ),
            }

        presentation_values = {**shared_values, **phase_values(presentation, "phase one")}
        presentation_frame = encode_profile_ordered_frame(
            CHALLENGE_FRAME_MAGIC,
            PRESENTATION_CHALLENGE_FIELDS,
            presentation_values,
        )
        presentation_octets = (
            presentation_values["nonce"] + hashlib.sha256(presentation_frame).digest()
        )
        presentation_id = raw_sha256(presentation_octets)
        presentation_base64url = base64.urlsafe_b64encode(
            presentation_octets
        ).decode("ascii").rstrip("=")
        if (
            presentation.get("frame_byte_count") != len(presentation_frame)
            or presentation.get("frame_raw_sha256") != raw_sha256(presentation_frame)
            or presentation.get("challenge_base64url") != presentation_base64url
            or presentation.get("presentation_challenge_id") != presentation_id
        ):
            add_error(
                errors,
                "backing_presentation_challenge_source_recomputation_mismatch",
            )

        authentication_values = {
            **shared_values,
            **phase_values(authentication, "phase two"),
            "presentation_challenge_id": challenge_digest_octets(
                presentation_id, "recomputed presentation challenge id"
            ),
            "confirmation_receipt_raw_sha256": challenge_digest_octets(
                receipt_digest, "successor confirmation receipt digest"
            ),
            "confirmation_receipt_profile_id": challenge_ascii(
                receipt_profile.get("receipt_profile_id"),
                "confirmation receipt profile id",
            ),
        }
        authentication_frame = encode_profile_ordered_frame(
            CHALLENGE_FRAME_MAGIC,
            AUTHENTICATION_CHALLENGE_FIELDS,
            authentication_values,
        )
        authentication_octets = (
            authentication_values["nonce"]
            + hashlib.sha256(authentication_frame).digest()
        )
    except (KeyError, TypeError, ValueError, struct.error) as exc:
        add_error(errors, "backing_challenge_recomputation_failed", str(exc))
        return None

    return {
        "challenge_profile_binding": {
            "artifact_id": "hda-challenge-frame-profile.v2.0001",
            "raw_sha256": profile_digest,
            "byte_count": profile_count,
            "mutable_alias_used": False,
        },
        "challenge_vector_evidence_binding": {
            "artifact_id": "hda-challenge-frame-v2-evidence.0001",
            "raw_sha256": path_binding(CHALLENGE_EVIDENCE_PATH)[0],
            "byte_count": path_binding(CHALLENGE_EVIDENCE_PATH)[1],
            "mutable_alias_used": False,
        },
        "presentation_frame_raw_sha256": raw_sha256(presentation_frame),
        "presentation_challenge_id": presentation_id,
        "confirmation_receipt_raw_sha256": receipt_digest,
        "authentication_frame_byte_count": len(authentication_frame),
        "authentication_frame_raw_sha256": raw_sha256(authentication_frame),
        "authentication_challenge_base64url": base64.urlsafe_b64encode(
            authentication_octets
        ).decode("ascii").rstrip("="),
        "authentication_challenge_id": raw_sha256(authentication_octets),
        "retained_relation_exact_match": True,
    }


def backing_format_conformant(
    role: str, required_media_type: str, raw: bytes
) -> tuple[bool, dict[str, bytes] | None]:
    if required_media_type == "application/json":
        return strict_json_document(raw), None
    if required_media_type == "application/cbor":
        return strict_cbor_document(raw), None
    if role == "exact_unmodified_confirmation_receipt_frame":
        parsed = parse_confirmation_frame(raw)
        return parsed is not None, parsed
    return required_media_type == "application/octet-stream" and bool(raw), None


def walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


@dataclass
class Retained:
    vectors: dict[str, Any]
    cases: dict[str, Any]
    chain_cases: dict[str, Any]
    ruleset: dict[str, Any]
    resolver: dict[str, Any]
    challenge_profile: dict[str, Any]
    challenge_evidence: dict[str, Any]
    evidence: dict[str, Any]
    backing: dict[str, Any]
    results: dict[str, dict[str, Any]]
    projections: dict[str, dict[str, Any]]
    comparison: dict[str, Any]
    seal: dict[str, Any]
    input_manifest: dict[str, Any]
    generation_manifest: dict[str, Any]
    source_manifests: dict[str, dict[str, Any]]
    schemas: dict[str, dict[str, Any]]


def required_paths() -> list[Path]:
    paths = [
        VECTORS_PATH,
        CASES_PATH,
        CHAIN_CASES_PATH,
        INPUT_MANIFEST_PATH,
        NORMATIVE_INPUT_PATH,
        GENERATION_MANIFEST_PATH,
        GENERATOR_PATH,
        TOOLCHAIN_LOCK_PATH,
        ARCHITECTURE_REQUIREMENTS_SOURCE_PATH,
        ARCHITECTURE_REQUIREMENTS_LOCK_PATH,
        RULESET_PATH,
        RESOLVER_PATH,
        CORE_PATH,
        DECISION_PATH,
        CANDIDATE_MANIFEST_PATH,
        CHALLENGE_PROFILE_PATH,
        CHALLENGE_EVIDENCE_PATH,
        EVIDENCE_PATH,
        BACKING_PATH,
        COMPARISON_PATH,
        SEAL_PATH,
        *SCHEMA_PATHS.values(),
        *RESULT_PATHS.values(),
        *PROJECTION_PATHS.values(),
        *SOURCE_MANIFEST_PATHS.values(),
        *CONFIG_PATHS.values(),
        *DEPENDENCY_LOCK_PATHS.values(),
        *ADAPTER_PATHS.values(),
        *RUNTIME_PROFILE_PATHS.values(),
    ]
    return paths


def load_retained(errors: list[str]) -> Retained | None:
    missing = [str(path.relative_to(ROOT)) for path in required_paths() if not path.is_file()]
    if missing:
        for path in missing:
            add_error(errors, "required_retained_artifact_missing", path)
        return None
    try:
        return Retained(
            vectors=load_json(VECTORS_PATH),
            cases=load_json(CASES_PATH),
            chain_cases=load_json(CHAIN_CASES_PATH),
            ruleset=load_json(RULESET_PATH),
            resolver=load_json(RESOLVER_PATH),
            challenge_profile=load_json(CHALLENGE_PROFILE_PATH),
            challenge_evidence=load_json(CHALLENGE_EVIDENCE_PATH),
            evidence=load_json(EVIDENCE_PATH),
            backing=load_json(BACKING_PATH),
            results={role: load_json(path) for role, path in RESULT_PATHS.items()},
            projections={
                role: load_json(path) for role, path in PROJECTION_PATHS.items()
            },
            comparison=load_json(COMPARISON_PATH),
            seal=load_json(SEAL_PATH),
            input_manifest=load_json(INPUT_MANIFEST_PATH),
            generation_manifest=load_json(GENERATION_MANIFEST_PATH),
            source_manifests={
                role: load_json(path) for role, path in SOURCE_MANIFEST_PATHS.items()
            },
            schemas={name: load_json(path) for name, path in SCHEMA_PATHS.items()},
        )
    except (OSError, ValueError) as exc:
        add_error(errors, "retained_json_unreadable", str(exc))
        return None


def validate_schema(
    schema: dict[str, Any], value: dict[str, Any], label: str, errors: list[str]
) -> None:
    try:
        Draft202012Validator.check_schema(schema)
        findings = sorted(
            Draft202012Validator(
                schema, format_checker=FormatChecker()
            ).iter_errors(value),
            key=lambda finding: tuple(str(part) for part in finding.absolute_path),
        )
    except Exception as exc:  # jsonschema deliberately has a broad error family
        add_error(errors, f"{label}_schema_unusable", str(exc))
        return
    for finding in findings:
        pointer = "/" + "/".join(str(part) for part in finding.absolute_path)
        add_error(errors, f"{label}_schema_rejected", f"{pointer}: {finding.message}")


def check_raw_binding(
    binding: Any,
    path: Path,
    label: str,
    errors: list[str],
    *,
    artifact_id: str | None = None,
    schema_id: str | None = None,
) -> None:
    if not isinstance(binding, dict):
        add_error(errors, f"{label}_binding_not_object")
        return
    try:
        digest, count = path_binding(path)
    except OSError as exc:
        add_error(errors, f"{label}_bound_file_unreadable", str(exc))
        return
    if binding.get("raw_sha256") != digest:
        add_error(errors, f"{label}_raw_sha256_mismatch")
    if binding.get("byte_count") != count:
        add_error(errors, f"{label}_byte_count_mismatch")
    if binding.get("mutable_alias_used") is not False:
        add_error(errors, f"{label}_mutable_alias_used")
    if artifact_id is not None and binding.get("artifact_id") != artifact_id:
        add_error(errors, f"{label}_artifact_id_mismatch")
    if schema_id is not None and binding.get("schema_resource_id") != schema_id:
        add_error(errors, f"{label}_schema_resource_id_mismatch")


def expected_manifest_entry(
    artifact_id: str, path: Path, artifact_kind: str
) -> dict[str, Any]:
    digest, count = path_binding(path)
    return {
        "artifact_id": artifact_id,
        "repository_path": str(path.relative_to(ROOT)),
        "raw_sha256": digest,
        "byte_count": count,
        "artifact_kind": artifact_kind,
    }


def check_ruleset_binding(binding: Any, label: str, errors: list[str]) -> None:
    if not isinstance(binding, dict):
        add_error(errors, f"{label}_binding_not_object")
        return
    digest, count = path_binding(RULESET_PATH)
    if binding != {
        "ruleset_id": RULESET_ID,
        "ruleset_version": "0.2.0",
        "raw_sha256": digest,
        "byte_count": count,
        "mutable_alias_used": False,
    }:
        add_error(errors, f"{label}_ruleset_binding_mismatch")


def validate_expectation_boundary(retained: Retained, errors: list[str]) -> None:
    vectors = retained.vectors
    cases = retained.cases
    expected_vector_keys = {
        "suite_version",
        "artifact_class",
        "candidate_status",
        "ruleset_id",
        "resolver_profile_id",
        "mutation_language",
        "base_input",
        "vectors",
    }
    if set(vectors) != expected_vector_keys:
        add_error(errors, "expectation_free_vector_top_level_shape_mismatch")
    if vectors.get("artifact_class") != (
        "human_decision_assurance_successor_expectation_free_evaluator_inputs"
    ):
        add_error(errors, "expectation_free_vector_artifact_class_mismatch")
    if vectors.get("ruleset_id") != RULESET_ID or vectors.get("resolver_profile_id") != RESOLVER_ID:
        add_error(errors, "expectation_free_vector_normative_identity_mismatch")
    forbidden = ANSWER_ONLY_KEYS.intersection(walk_keys(vectors))
    if forbidden:
        add_error(
            errors,
            "expected_answer_leaked_into_vector_corpus",
            ",".join(sorted(forbidden)),
        )
    entries = vectors.get("vectors")
    case_entries = cases.get("cases")
    if not isinstance(entries, list) or not entries:
        add_error(errors, "expectation_free_vector_inventory_empty_or_invalid")
        entries = []
    if not isinstance(case_entries, list) or not case_entries:
        add_error(errors, "private_answer_case_inventory_empty_or_invalid")
        case_entries = []
    if len(entries) != len(case_entries):
        add_error(errors, "expectation_free_vector_private_answer_count_mismatch")
    vector_ids: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or not set(entry) <= {
            "vector_id",
            "base_vector_id",
            "mutations",
        } or set(entry) < {"vector_id", "mutations"}:
            add_error(errors, "expectation_free_vector_entry_shape_mismatch")
            continue
        vector_id = entry.get("vector_id")
        if not isinstance(vector_id, str):
            add_error(errors, "expectation_free_vector_id_invalid")
        else:
            vector_ids.append(vector_id)
    case_ids = [
        entry.get("vector_id")
        for entry in case_entries
        if isinstance(entry, dict)
    ]
    if len(vector_ids) != len(set(vector_ids)):
        add_error(errors, "expectation_free_vector_id_duplicate")
    if vector_ids != case_ids:
        add_error(errors, "private_answers_not_one_to_one_in_vector_order")
    by_case = {
        entry.get("vector_id"): entry for entry in case_entries if isinstance(entry, dict)
    }
    for entry in case_entries:
        if not isinstance(entry, dict) or set(entry) != {
            "vector_id",
            "kind",
            "safe_control_vector_id",
            "expected_disposition",
            "expected_reason_codes",
            "expected_errors",
            "intent_errors",
        }:
            add_error(errors, "private_answer_case_shape_mismatch")
            continue
        if not sorted_unique_ascii(entry.get("expected_reason_codes")):
            add_error(errors, "private_answer_reason_codes_not_sorted_unique")
        if not sorted_unique_ascii(entry.get("expected_errors")):
            add_error(errors, "private_answer_errors_not_sorted_unique")
        if not sorted_unique_ascii(entry.get("intent_errors")):
            add_error(errors, "private_answer_intent_errors_not_sorted_unique")
        intent = entry.get("intent_errors", [])
        expected = entry.get("expected_errors", [])
        if not set(intent).issubset(expected):
            add_error(errors, "private_answer_intent_not_subset")
        if entry.get("kind") == "adversarial":
            control = by_case.get(entry.get("safe_control_vector_id"))
            if not intent or not isinstance(control, dict) or control.get("kind") != "safe_control":
                add_error(errors, "adversarial_case_safe_control_or_intent_missing")
        elif entry.get("kind") == "safe_control":
            if entry.get("safe_control_vector_id") is not None or expected or intent:
                add_error(errors, "safe_control_contains_refusal_answer")
        else:
            add_error(errors, "private_answer_case_kind_invalid")

    # Source trees may contain a literal cases.json only in an explicit refusal
    # guard; they may never consume the answer corpus or another implementation.
    python_evaluator = (SUITE / "python/evaluator.py").read_text(encoding="utf-8")
    if "cases.json" in python_evaluator:
        add_error(errors, "python_evaluator_mentions_answer_corpus")
    for role, root in SOURCE_ROOTS.items():
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".mjs", ".java"}:
                continue
            if path.is_symlink():
                add_error(errors, "implementation_source_symlink_forbidden", str(path.relative_to(ROOT)))
            text = path.read_text(encoding="utf-8")
            peers = set(ROLE_KEYS) - {role}
            for peer in peers:
                peer_markers = (f"/{peer}/", f"../{peer}", f"{peer}.projection", f"{peer}.result")
                if any(marker in text for marker in peer_markers):
                    add_error(errors, "peer_implementation_material_referenced", str(path.relative_to(ROOT)))


def validate_ruleset_and_resolver(retained: Retained, errors: list[str]) -> None:
    ruleset = retained.ruleset
    resolver = retained.resolver
    domains = [item.get("domain_id") for item in ruleset.get("required_domains", []) if isinstance(item, dict)]
    categorical = ruleset.get("required_categorical_conditions")
    roles = [item.get("role") for item in resolver.get("closed_role_inventory", []) if isinstance(item, dict)]
    if ruleset.get("ruleset_id") != RULESET_ID or ruleset.get("ruleset_version") != "0.2.0":
        add_error(errors, "ruleset_identity_mismatch")
    if resolver.get("profile_id") != RESOLVER_ID or resolver.get("profile_version") != "0.1.0":
        add_error(errors, "resolver_profile_identity_mismatch")
    if len(domains) != 11 or len(set(domains)) != 11:
        add_error(errors, "ruleset_required_domain_inventory_not_closed")
    if not isinstance(categorical, list) or len(categorical) != 11 or len(set(categorical)) != 11:
        add_error(errors, "ruleset_categorical_inventory_not_closed")
    if len(roles) != 14 or len(set(roles)) != 14:
        add_error(errors, "resolver_role_inventory_not_closed")
    independent = ruleset.get("independent_recomputation_contract", {})
    if independent.get("required_result_roles") != list(IMPLEMENTATION_ROLES.values()):
        add_error(errors, "ruleset_required_result_roles_mismatch")
    if independent.get("required_toolchain_versions") != {
        IMPLEMENTATION_ROLES[key]: TOOLCHAIN_VERSIONS[key] for key in ROLE_KEYS
    }:
        add_error(errors, "ruleset_toolchain_versions_mismatch")


def validate_evidence(retained: Retained, errors: list[str]) -> None:
    evidence = retained.evidence
    base = retained.vectors.get("base_input", {})
    validate_schema(retained.schemas["evidence"], evidence, "evidence", errors)
    if evidence.get("schema_version") != "0.2.0":
        add_error(errors, "evidence_resource_identity_version_mismatch")
    assurance_id = evidence.get("assurance_id")
    if not isinstance(assurance_id, str):
        add_error(errors, "evidence_assurance_id_invalid")
    check_raw_binding(
        evidence.get("core_binding"), CORE_PATH, "evidence_core", errors,
        schema_id="urn:odeya:schema:human-decision-assurance-core:0.1.0",
    )
    check_raw_binding(
        evidence.get("decision_subject_binding"), DECISION_PATH,
        "evidence_decision_subject", errors,
        schema_id="urn:odeya:schema:operator-architecture-decision:0.4.0",
    )
    check_raw_binding(
        evidence.get("candidate_manifest_binding"), CANDIDATE_MANIFEST_PATH,
        "evidence_candidate_manifest", errors,
        schema_id="urn:odeya:schema:architecture-candidate-manifest:0.5.0",
    )
    challenge = evidence.get("challenge_profile_binding")
    if not isinstance(challenge, dict):
        add_error(errors, "evidence_challenge_profile_binding_not_object")
    else:
        digest, count = path_binding(CHALLENGE_PROFILE_PATH)
        if challenge.get("raw_sha256") != digest or challenge.get("byte_count") != count:
            add_error(errors, "evidence_challenge_profile_raw_binding_mismatch")
    expected_participant = base.get("participant_input")
    if evidence.get("participant_observations") != [expected_participant]:
        add_error(errors, "evidence_participant_projection_mismatch")
    if evidence.get("forbidden_content_and_sanitation") != base.get(
        "forbidden_content_and_sanitation"
    ):
        add_error(errors, "evidence_sanitation_projection_mismatch")

    artifacts = base.get("backing_byte_inputs", {}).get("artifacts", [])
    descriptors = [item.get("descriptor") for item in artifacts if isinstance(item, dict)]
    inventory = evidence.get("ordered_artifact_inventory")
    if inventory != descriptors:
        add_error(errors, "evidence_descriptor_inventory_mismatch")
    expected_ids = [item.get("artifact_id") for item in descriptors if isinstance(item, dict)]
    if evidence.get("ordered_artifact_ids") != expected_ids:
        add_error(errors, "evidence_artifact_id_order_mismatch")
    resolver_roles = [
        item.get("role")
        for item in retained.resolver.get("closed_role_inventory", [])
        if isinstance(item, dict)
    ]
    observed_roles = [item.get("role") for item in inventory or [] if isinstance(item, dict)]
    if observed_roles != resolver_roles:
        add_error(errors, "evidence_role_order_mismatch")
    if len(expected_ids) != len(set(expected_ids)):
        add_error(errors, "evidence_artifact_id_duplicate")

    for index, descriptor in enumerate(inventory or []):
        if not isinstance(descriptor, dict):
            add_error(errors, "evidence_descriptor_not_object", str(index))
            continue
        content_address = descriptor.get("content_address")
        path_text = descriptor.get("repository_blob_path")
        if not isinstance(content_address, str) or SHA256_RE.fullmatch(content_address) is None:
            add_error(errors, "evidence_content_address_invalid", str(index))
            continue
        expected_path = (
            f"architecture/evidence-blobs/sha256/{content_address[7:9]}/"
            f"{content_address[9:]}"
        )
        if path_text != expected_path:
            add_error(errors, "evidence_blob_path_not_content_derived", str(index))
            continue
        blob_path = ROOT / expected_path
        try:
            if blob_path.is_symlink() or not blob_path.is_file():
                raise OSError("not a regular non-symlink file")
            raw = blob_path.read_bytes()
        except OSError as exc:
            add_error(errors, "evidence_blob_unreadable", f"{index}: {exc}")
            continue
        if raw_sha256(raw) != content_address:
            add_error(errors, "evidence_blob_digest_mismatch", str(index))
        if len(raw) != descriptor.get("byte_count"):
            add_error(errors, "evidence_blob_byte_count_mismatch", str(index))
        vector_preimage = artifacts[index].get("preimage", {}) if index < len(artifacts) else {}
        if vector_preimage.get("repository_blob_path") != expected_path:
            add_error(errors, "vector_preimage_path_mismatch", str(index))


def derive_backing_outcome(
    rows: Sequence[Mapping[str, Any]], relation: Mapping[str, Any]
) -> tuple[str, list[str]]:
    """Derive the receipt disposition and its exact reason set from observations."""
    findings: set[str] = set()
    for row in rows:
        role = row.get("role")
        if not isinstance(role, str):
            continue
        observation = row.get("integrity_observation")
        if observation == "unknown":
            read = row.get("read_disposition")
            suffix = "missing" if read == "missing" else "unreadable"
            findings.add(f"indeterminate.backing_byte.{role}.{suffix}")
        elif observation == "contradicted":
            findings.add(f"invalid.backing_byte.{role}.mismatch")
            if row.get("format_disposition") == "malformed":
                findings.add(f"invalid.backing_byte.{role}.malformed")
    relation_states = [
        relation.get("binary_framing_disposition"),
        relation.get("presentation_to_receipt_relation_disposition"),
        relation.get("receipt_to_authentication_relation_disposition"),
    ]
    if "contradicted" in relation_states:
        findings.add("invalid.backing_byte.confirmation_receipt_relation_mismatch")
    elif "unknown" in relation_states:
        findings.add("indeterminate.backing_byte.confirmation_receipt_relation.unknown")
    ordered = sorted(findings, key=lambda value: value.encode("ascii"))
    if any(code.startswith("invalid.") for code in ordered):
        return "invalid", ordered
    if ordered:
        return "indeterminate", ordered
    return "supported", ["supported.all_backing_bytes_verified"]


def recompute_backing_from_evidence(
    retained: Retained, errors: list[str]
) -> tuple[list[dict[str, Any]], dict[str, Any], str, list[str]]:
    """Resolve every role from Evidence bytes; never consume vector receipt rows."""
    descriptors = retained.evidence.get("ordered_artifact_inventory")
    resolver_rows = retained.resolver.get("closed_role_inventory")
    if not isinstance(descriptors, list) or not isinstance(resolver_rows, list):
        add_error(errors, "backing_recomputation_inventory_unavailable")
        return [], {}, "invalid", ["invalid.backing_byte.closed_role_inventory_mismatch"]
    expected_roles = [
        item.get("role") for item in resolver_rows if isinstance(item, dict)
    ]
    observed_roles = [
        item.get("role") for item in descriptors if isinstance(item, dict)
    ]
    if observed_roles != expected_roles or len(descriptors) != len(resolver_rows):
        add_error(errors, "backing_recomputation_closed_role_inventory_mismatch")
        return [], {}, "invalid", ["invalid.backing_byte.closed_role_inventory_mismatch"]

    rows: list[dict[str, Any]] = []
    parsed_frame: dict[str, bytes] | None = None
    frame_observed_digest: str | None = None
    displayed_observed_digest: str | None = None
    displayed_observed_count: int | None = None
    descriptors_by_role: dict[str, dict[str, Any]] = {}
    artifact_ids: set[str] = set()
    for index, (descriptor, required) in enumerate(
        zip(descriptors, resolver_rows, strict=True)
    ):
        if not isinstance(descriptor, dict) or not isinstance(required, dict):
            add_error(errors, "backing_recomputation_descriptor_invalid", str(index))
            continue
        role = required.get("role")
        content_address = descriptor.get("content_address")
        if not isinstance(role, str) or not isinstance(content_address, str):
            add_error(errors, "backing_recomputation_descriptor_invalid", str(index))
            continue
        if SHA256_RE.fullmatch(content_address) is None:
            add_error(errors, "backing_recomputation_content_address_invalid", role)
            continue
        derived_path = (
            f"architecture/evidence-blobs/sha256/{content_address[7:9]}/"
            f"{content_address[9:]}"
        )
        descriptors_by_role[role] = descriptor
        artifact_id = descriptor.get("artifact_id")
        artifact_id_valid = (
            isinstance(artifact_id, str)
            and bool(artifact_id)
            and artifact_id not in artifact_ids
        )
        if isinstance(artifact_id, str):
            artifact_ids.add(artifact_id)
        byte_count = descriptor.get("byte_count")
        descriptor_matches = (
            descriptor.get("role") == role
            and artifact_id_valid
            and isinstance(byte_count, int)
            and not isinstance(byte_count, bool)
            and byte_count > 0
            and descriptor.get("media_type") == required.get("required_media_type")
            and descriptor.get("byte_fidelity")
            == required.get("required_byte_fidelity")
            and descriptor.get("repository_blob_path") == derived_path
        )
        row: dict[str, Any] = {
            "role": role,
            "artifact_id": artifact_id,
            "expected_content_address": content_address,
            "expected_byte_count": byte_count,
            "expected_media_type": descriptor.get("media_type"),
            "expected_byte_fidelity": descriptor.get("byte_fidelity"),
            "repository_blob_path": derived_path,
        }
        blob_path = ROOT / derived_path
        if blob_path.is_symlink() or not blob_path.exists():
            row.update(
                {
                    "read_disposition": "missing",
                    "observed_raw_sha256": None,
                    "observed_byte_count": None,
                    "format_disposition": "not_evaluated_no_read",
                    "comparison_disposition": "not_compared_no_read",
                    "integrity_observation": "unknown",
                }
            )
            rows.append(row)
            continue
        try:
            if not blob_path.is_file():
                raise OSError("not a regular file")
            raw = blob_path.read_bytes()
        except OSError:
            row.update(
                {
                    "read_disposition": "unreadable",
                    "observed_raw_sha256": None,
                    "observed_byte_count": None,
                    "format_disposition": "not_evaluated_no_read",
                    "comparison_disposition": "not_compared_no_read",
                    "integrity_observation": "unknown",
                }
            )
            rows.append(row)
            continue
        observed_digest = raw_sha256(raw)
        format_ok, frame = backing_format_conformant(
            role, str(required.get("required_media_type")), raw
        )
        matches = (
            descriptor_matches
            and observed_digest == content_address
            and len(raw) == byte_count
            and format_ok
        )
        row.update(
            {
                "read_disposition": "readable_complete",
                "observed_raw_sha256": observed_digest,
                "observed_byte_count": len(raw),
                "format_disposition": "conformant" if format_ok else "malformed",
                "comparison_disposition": "match" if matches else "mismatch",
                "integrity_observation": "supported" if matches else "contradicted",
            }
        )
        rows.append(row)
        if role == "exact_unmodified_confirmation_receipt_frame":
            parsed_frame = frame
            frame_observed_digest = observed_digest
        elif role == "exact_unmodified_displayed_decision_bytes":
            displayed_observed_digest = observed_digest
            displayed_observed_count = len(raw)

    normative_relation = (
        retained.vectors.get("base_input", {})
        .get("backing_byte_inputs", {})
        .get("confirmation_receipt_frame_relation", {})
    )
    if not isinstance(normative_relation, dict):
        normative_relation = {}
    frame_descriptor = descriptors_by_role.get(
        "exact_unmodified_confirmation_receipt_frame", {}
    )
    expected_frame_digest = frame_descriptor.get("content_address")
    recorded_presentation_id = normative_relation.get("presentation_challenge_id")
    recorded_authentication_id = normative_relation.get(
        "authentication_challenge_id"
    )
    committed_digest = normative_relation.get(
        "authentication_frame_committed_receipt_sha256"
    )
    challenge_recomputation = recompute_successor_phase_two_challenge(
        retained, frame_observed_digest, errors
    )
    presentation_id = recorded_presentation_id
    authentication_id = recorded_authentication_id
    if challenge_recomputation is not None:
        presentation_id = challenge_recomputation["presentation_challenge_id"]
        authentication_id = challenge_recomputation["authentication_challenge_id"]
        if recorded_presentation_id != presentation_id:
            add_error(
                errors,
                "backing_confirmation_relation_presentation_challenge_id_mismatch",
            )
        if recorded_authentication_id != authentication_id:
            add_error(
                errors,
                "backing_confirmation_relation_authentication_challenge_id_mismatch",
            )
    binary_state = (
        "supported"
        if parsed_frame is not None
        else "unknown"
        if frame_observed_digest is None
        else "contradicted"
    )
    presentation_state = "unknown" if frame_observed_digest is None else "contradicted"
    authentication_state = "unknown" if frame_observed_digest is None else "contradicted"
    if parsed_frame is not None:
        frame_presentation = "sha256:" + parsed_frame["presentation_challenge_id"].hex()
        frame_displayed_digest = "sha256:" + parsed_frame["displayed_bytes_sha256"].hex()
        frame_displayed_count = int.from_bytes(
            parsed_frame["displayed_byte_count"], "big"
        )
        if (
            frame_presentation == presentation_id
            and frame_displayed_digest == displayed_observed_digest
            and frame_displayed_count == displayed_observed_count
        ):
            presentation_state = "supported"
        if (
            frame_observed_digest == committed_digest == expected_frame_digest
            and recorded_authentication_id == authentication_id
        ):
            authentication_state = "supported"
    expected_relation = {
        "frame_role": "exact_unmodified_confirmation_receipt_frame",
        "expected_frame_content_address": expected_frame_digest,
        "observed_frame_raw_sha256": frame_observed_digest,
        "presentation_challenge_id": presentation_id,
        "authentication_challenge_id": authentication_id,
        "authentication_frame_committed_receipt_sha256": committed_digest,
        "binary_framing_disposition": binary_state,
        "presentation_to_receipt_relation_disposition": presentation_state,
        "receipt_to_authentication_relation_disposition": authentication_state,
    }
    disposition, reason_codes = derive_backing_outcome(rows, expected_relation)
    return rows, expected_relation, disposition, reason_codes


def validate_backing(retained: Retained, errors: list[str]) -> None:
    backing = retained.backing
    validate_schema(retained.schemas["backing"], backing, "backing", errors)
    if (
        backing.get("artifact_id") != BACKING_RECEIPT_ARTIFACT_ID
        or backing.get("assurance_id") != retained.evidence.get("assurance_id")
    ):
        add_error(errors, "backing_identity_mismatch")
    check_raw_binding(
        backing.get("evidence_binding"), EVIDENCE_PATH, "backing_evidence", errors,
        artifact_id=retained.evidence.get("artifact_id"), schema_id=EVIDENCE_SCHEMA_ID,
    )
    resolver_binding = backing.get("resolver_profile_binding")
    if not isinstance(resolver_binding, dict):
        add_error(errors, "backing_resolver_binding_not_object")
    else:
        digest, count = path_binding(RESOLVER_PATH)
        if (
            resolver_binding.get("profile_id") != RESOLVER_ID
            or resolver_binding.get("profile_version") != "0.1.0"
            or resolver_binding.get("raw_sha256") != digest
            or resolver_binding.get("byte_count") != count
            or resolver_binding.get("content_address_is_object_identity") is not True
            or resolver_binding.get("mutable_alias_used") is not False
        ):
            add_error(errors, "backing_resolver_binding_mismatch")
    expected_rows, expected_relation, expected_disposition, expected_reasons = (
        recompute_backing_from_evidence(retained, errors)
    )
    if backing.get("role_verifications") != expected_rows:
        add_error(errors, "backing_role_rows_mismatch")
    if (
        backing.get("expected_role_count") != len(expected_rows)
        or len(expected_rows) != len(retained.resolver.get("closed_role_inventory", []))
    ):
        add_error(errors, "backing_role_count_mismatch")
    if backing.get("confirmation_receipt_frame_relation") != expected_relation:
        add_error(errors, "backing_confirmation_relation_mismatch")
    if backing.get("verification_disposition") != expected_disposition:
        add_error(errors, "backing_verification_disposition_mismatch")
    if backing.get("reason_codes") != expected_reasons:
        add_error(errors, "backing_reason_codes_mismatch")


def raw_projection_to_full(value: Mapping[str, Any]) -> dict[str, Any]:
    return {field: copy.deepcopy(value.get(field)) for field in OUTPUT_FIELD_ORDER}


def check_reason_array(
    value: Any, label: str, errors: list[str]
) -> list[str] | None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.isascii() for item in value
    ):
        add_error(errors, f"{label}_reason_codes_invalid")
        return None
    if len(value) != len(set(value)):
        add_error(errors, f"{label}_duplicate_reason_code")
    if value != sorted(value, key=lambda item: item.encode("ascii")):
        add_error(errors, f"{label}_reason_codes_unsorted")
    grammar = re.compile(
        r"^(eligible|indeterminate|invalid)\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$"
    )
    if any(grammar.fullmatch(item) is None for item in value):
        add_error(errors, f"{label}_reason_code_grammar_mismatch")
    return value


def expected_domain_reason_codes(
    domain: str, status: str, count: int, observed: list[str]
) -> list[str] | None:
    if status == "supported":
        return [f"eligible.domain.{domain}.supported"]
    if domain == "backing_byte_integrity":
        role_finding = re.compile(
            r"^(?:indeterminate\.backing_byte\.[a-z0-9_]+\.(?:missing|unreadable)"
            r"|invalid\.backing_byte\.[a-z0-9_]+\.(?:malformed|mismatch)"
            r"|invalid\.backing_byte\.(?:closed_role_inventory_mismatch"
            r"|confirmation_receipt_relation_mismatch|failed_row_omitted"
            r"|missing_recorded_as_readable_match|missing_recorded_as_zero_byte_match)"
            r"|indeterminate\.backing_byte\.confirmation_receipt_relation\.unknown)$"
        )
        valid = bool(observed) and all(
            role_finding.fullmatch(reason) is not None for reason in observed
        )
        if status == "contradicted":
            valid = valid and any(reason.startswith("invalid.") for reason in observed)
        elif status == "unknown":
            valid = valid and all(
                reason.startswith("indeterminate.") for reason in observed
            )
        else:
            valid = False
        return (
            sorted(set(observed), key=lambda item: item.encode("ascii"))
            if valid
            else []
        )
    if domain == "sanitation" and status == "contradicted":
        allowed = {
            "invalid.sanitation.contradicted",
            "invalid.sanitation.forbidden_content",
        }
        if observed and set(observed).issubset(allowed):
            return sorted(set(observed), key=lambda item: item.encode("ascii"))
        return []
    if domain == "exact_core_and_evidence_binding" and status == "contradicted":
        allowed = {
            "invalid.domain.exact_core_and_evidence_binding.contradicted",
            "invalid.integrity.required_domain_inventory_mismatch",
            "invalid.integrity.resource_identity_version_mismatch",
            "invalid.integrity.undeclared_eligibility_domain",
        }
        if observed and set(observed).issubset(allowed):
            return sorted(set(observed), key=lambda item: item.encode("ascii"))
        return []
    if domain == "exact_core_and_evidence_binding" and status in {
        "unknown",
        "not_applicable",
    }:
        allowed = {
            "indeterminate.domain.exact_core_and_evidence_binding.missing",
            "indeterminate.domain.exact_core_and_evidence_binding.not_applicable",
            "indeterminate.domain.exact_core_and_evidence_binding.unknown",
        }
        if len(observed) == 1 and observed[0] in allowed:
            return observed
        return []
    if status == "contradicted":
        return [f"invalid.domain.{domain}.contradicted"]
    if status == "not_applicable":
        return [f"indeterminate.domain.{domain}.not_applicable"]
    if status == "unknown":
        suffix = "missing" if count == 0 else "unknown"
        return [f"indeterminate.domain.{domain}.{suffix}"]
    return []


def expected_categorical_reason_codes(
    condition: str, status: str, observed: list[str]
) -> list[str]:
    if condition == "assertion_acceptance_and_consumption_atomic_action_equal":
        if status == "satisfied":
            return [f"eligible.categorical.{condition}.satisfied"]
        allowed = {
            "indeterminate.atomic_action.acceptance_id_missing",
            "indeterminate.atomic_action.backing_record_missing",
            "indeterminate.atomic_action.backing_record_unreadable",
            "indeterminate.atomic_action.consumption_id_missing",
            "invalid.atomic_action.acceptance_id_malformed",
            "invalid.atomic_action.backing_record_contradicted",
            "invalid.atomic_action.backing_record_malformed",
            "invalid.atomic_action.consumption_id_malformed",
            "invalid.atomic_action.identifiers_unequal",
        }
        valid = bool(observed) and set(observed).issubset(allowed)
        if status == "failed":
            valid = valid and any(item.startswith("invalid.") for item in observed)
        elif status == "unknown":
            valid = valid and all(
                item.startswith("indeterminate.") for item in observed
            )
        else:
            valid = False
        if valid:
            return sorted(set(observed), key=lambda item: item.encode("ascii"))
        return []
    prefix = {
        "satisfied": "eligible",
        "failed": "invalid",
        "unknown": "indeterminate",
        "not_applicable": "indeterminate",
    }.get(status)
    suffix = {
        "satisfied": "satisfied",
        "failed": "failed",
        "unknown": "unknown",
        "not_applicable": "not_applicable",
    }.get(status)
    if prefix is None or suffix is None:
        return []
    return [f"{prefix}.categorical.{condition}.{suffix}"]


def validate_raw_projection(
    projection: dict[str, Any], retained: Retained, label: str, errors: list[str]
) -> None:
    if set(projection) != OUTPUT_KEYS:
        add_error(errors, f"{label}_raw_projection_shape_mismatch")
    domain_order = [
        item.get("domain_id")
        for item in retained.ruleset.get("required_domains", [])
        if isinstance(item, dict)
    ]
    categorical_order = retained.ruleset.get("required_categorical_conditions", [])
    domain_results = projection.get("domain_results")
    categorical_results = projection.get("categorical_results")
    if not isinstance(domain_results, list) or [
        item.get("domain") for item in domain_results if isinstance(item, dict)
    ] != domain_order:
        add_error(errors, f"{label}_domain_order_mismatch")
    if not isinstance(categorical_results, list) or [
        item.get("condition_id") for item in categorical_results if isinstance(item, dict)
    ] != categorical_order:
        add_error(errors, f"{label}_categorical_order_mismatch")
    if not isinstance(projection.get("participant_id"), str):
        add_error(errors, f"{label}_participant_id_invalid")
    local_negative: set[str] = set()
    if isinstance(domain_results, list):
        for index, item in enumerate(domain_results):
            if not isinstance(item, dict) or set(item) != {
                "domain",
                "input_observation_count",
                "folded_status",
                "reason_codes",
            }:
                add_error(errors, f"{label}_domain_result_shape_mismatch", str(index))
                continue
            count = item.get("input_observation_count")
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                add_error(errors, f"{label}_domain_observation_count_invalid", str(index))
                count = 0
            reasons = check_reason_array(
                item.get("reason_codes"), f"{label}_domain_{index}", errors
            )
            if reasons is None:
                continue
            expected_local = expected_domain_reason_codes(
                str(item.get("domain")), str(item.get("folded_status")), count, reasons
            )
            if expected_local is not None and reasons != expected_local:
                add_error(errors, f"{label}_domain_reason_set_mismatch", str(index))
            local_negative.update(
                reason for reason in reasons if not reason.startswith("eligible.")
            )
    if isinstance(categorical_results, list):
        for index, item in enumerate(categorical_results):
            if not isinstance(item, dict) or set(item) != {
                "condition_id",
                "status",
                "reason_codes",
            }:
                add_error(
                    errors, f"{label}_categorical_result_shape_mismatch", str(index)
                )
                continue
            reasons = check_reason_array(
                item.get("reason_codes"), f"{label}_categorical_{index}", errors
            )
            if reasons is None:
                continue
            expected_local = expected_categorical_reason_codes(
                str(item.get("condition_id")), str(item.get("status")), reasons
            )
            if reasons != expected_local:
                add_error(
                    errors, f"{label}_categorical_reason_set_mismatch", str(index)
                )
            local_negative.update(
                reason for reason in reasons if not reason.startswith("eligible.")
            )
    failures = projection.get("categorical_failures")
    expected_failures = sorted(
        [
            item.get("condition_id")
            for item in categorical_results or []
            if isinstance(item, dict) and item.get("status") == "failed"
        ],
        key=lambda value: value.encode("ascii") if isinstance(value, str) else b"",
    )
    if failures != expected_failures:
        add_error(errors, f"{label}_categorical_failures_mismatch")
    reasons = check_reason_array(projection.get("reason_codes"), label, errors)
    has_invalid = any(
        isinstance(item, dict) and item.get("folded_status") == "contradicted"
        for item in domain_results or []
    ) or any(
        isinstance(item, dict) and item.get("status") == "failed"
        for item in categorical_results or []
    )
    has_unknown = any(
        isinstance(item, dict) and item.get("folded_status") in {"unknown", "not_applicable"}
        for item in domain_results or []
    ) or any(
        isinstance(item, dict) and item.get("status") in {"unknown", "not_applicable"}
        for item in categorical_results or []
    )
    expected_final = "invalid" if has_invalid else "indeterminate" if has_unknown else "eligible"
    if projection.get("final_disposition") != expected_final:
        add_error(errors, f"{label}_final_disposition_precedence_mismatch")
    expected_global = (
        ["eligible.all_required_inputs_supported"]
        if not local_negative
        else sorted(local_negative, key=lambda item: item.encode("ascii"))
    )
    if reasons is not None and reasons != expected_global:
        add_error(errors, f"{label}_reason_code_set_mismatch")
    if expected_final == "eligible":
        if reasons != ["eligible.all_required_inputs_supported"]:
            add_error(errors, f"{label}_eligible_reason_set_mismatch")
        if reasons is not None and any(code.startswith(("invalid.", "indeterminate.")) for code in reasons):
            add_error(errors, f"{label}_negative_reason_on_eligible_result")
    elif reasons is not None and any(code.startswith("eligible.") for code in reasons):
        add_error(errors, f"{label}_positive_reason_on_negative_result")


def candidate_binding_paths(role: str, field: str) -> list[Path]:
    if field == "source_binding":
        return [SOURCE_MANIFEST_PATHS[role]]
    if field == "configuration_binding":
        return [CONFIG_PATHS[role]]
    if field == "dependency_lock_binding":
        return [DEPENDENCY_LOCK_PATHS[role]]
    if field == "input_adapter_binding":
        return [ADAPTER_PATHS[role]]
    if field == "toolchain_profile_binding":
        return [RUNTIME_PROFILE_PATHS[role]]
    raise KeyError(field)


def binding_matches_any_path(
    binding: Any, paths: Sequence[Path], expected_artifact_id: str
) -> bool:
    if not isinstance(binding, dict):
        return False
    if (
        binding.get("artifact_id") != expected_artifact_id
        or binding.get("mutable_alias_used") is not False
    ):
        return False
    for path in paths:
        if not path.is_file():
            continue
        digest, count = path_binding(path)
        if binding.get("raw_sha256") == digest and binding.get("byte_count") == count:
            return True
    return False


def validate_result(role: str, retained: Retained, errors: list[str]) -> None:
    result = retained.results[role]
    projection = retained.projections[role]
    validate_schema(retained.schemas["result"], result, f"{role}_result", errors)
    validate_raw_projection(projection, retained, f"{role}_projection", errors)
    if (
        result.get("artifact_id")
        != IMPLEMENTATION_ARTIFACT_IDS[role]["result_id"]
        or result.get("assurance_id") != retained.evidence.get("assurance_id")
    ):
        add_error(errors, f"{role}_result_identity_mismatch")
    implementation = result.get("implementation", {})
    if (
        implementation.get("implementation_role") != IMPLEMENTATION_ROLES[role]
        or implementation.get("toolchain_name") != TOOLCHAIN_NAMES[role]
        or implementation.get("toolchain_version") != TOOLCHAIN_VERSIONS[role]
        or implementation.get("network_access") is not False
        or implementation.get("mutable_toolchain_alias_used") is not False
    ):
        add_error(errors, f"{role}_implementation_identity_mismatch")
    for field in (
        "source_binding",
        "toolchain_profile_binding",
        "dependency_lock_binding",
        "configuration_binding",
        "input_adapter_binding",
    ):
        if not binding_matches_any_path(
            implementation.get(field),
            candidate_binding_paths(role, field),
            IMPLEMENTATION_ARTIFACT_IDS[role][field],
        ):
            add_error(errors, f"{role}_{field}_raw_binding_mismatch")
    bindings = result.get("input_bindings", {})
    check_raw_binding(
        bindings.get("evidence"), EVIDENCE_PATH, f"{role}_result_evidence", errors,
        artifact_id=retained.evidence.get("artifact_id"), schema_id=EVIDENCE_SCHEMA_ID,
    )
    check_raw_binding(
        bindings.get("backing_byte_verification_receipt"), BACKING_PATH,
        f"{role}_result_backing", errors,
        artifact_id=retained.backing.get("artifact_id"), schema_id=BACKING_SCHEMA_ID,
    )
    check_ruleset_binding(bindings.get("eligibility_ruleset"), f"{role}_result", errors)
    check_raw_binding(
        bindings.get("input_manifest"), INPUT_MANIFEST_PATH,
        f"{role}_result_input_manifest", errors,
        artifact_id=retained.input_manifest.get("artifact_id"),
    )
    check_raw_binding(
        bindings.get("normative_input_vector"), NORMATIVE_INPUT_PATH,
        f"{role}_result_normative_vector", errors,
        artifact_id=NORMATIVE_INPUT_ARTIFACT_ID,
    )
    execution = result.get("execution", {})
    check_raw_binding(
        execution.get("raw_projection_binding"), PROJECTION_PATHS[role],
        f"{role}_result_projection", errors,
        artifact_id=IMPLEMENTATION_ARTIFACT_IDS[role]["raw_projection_binding"],
    )
    for field in OUTPUT_KEYS:
        if result.get(field) != projection.get(field):
            add_error(errors, f"{role}_result_projection_{field}_mismatch")
    proof = result.get("proof_boundary", {})
    for field in (
        "expected_result_fixture_consumed",
        "shared_evaluator_source_consumed",
        "generated_evaluator_code_consumed",
        "network_service_used",
    ):
        if proof.get(field) is not False:
            add_error(errors, f"{role}_result_nonsharing_boundary_escalated")


def manifest_source_paths(value: Any) -> list[str]:
    """Extract retained paths from a source manifest without trusting one shape."""
    result: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if key in {"path", "source_path", "repository_path"} and isinstance(child, str):
                    result.append(child)
                else:
                    visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    return result


def runtime_profile_errors(
    profile: Any, role: str, lock_digest: str, lock_count: int
) -> list[str]:
    errors: list[str] = []
    if not isinstance(profile, dict):
        return [f"{role}_runtime_profile_must_be_object"]
    if (
        profile.get("artifact_class")
        != "human_decision_assurance_exact_runtime_profile"
        or profile.get("artifact_id")
        != IMPLEMENTATION_ARTIFACT_IDS[role]["toolchain_profile_binding"]
        or profile.get("implementation_role") != IMPLEMENTATION_ROLES[role]
        or profile.get("toolchain_name") != TOOLCHAIN_NAMES[role]
        or profile.get("toolchain_version") != TOOLCHAIN_VERSIONS[role]
        or profile.get("mutable_toolchain_alias_used") is not False
        or profile.get("network_access") is not False
        or profile.get("profile_self_digest_forbidden") is not True
    ):
        add_error(errors, f"{role}_runtime_profile_identity_mismatch")
    lock = profile.get("repository_toolchain_lock", {})
    if (
        lock.get("repository_path")
        != "tools/repository-release/toolchain.lock.json"
        or lock.get("raw_sha256") != lock_digest
        or lock.get("byte_count") != lock_count
    ):
        add_error(errors, f"{role}_runtime_profile_toolchain_lock_mismatch")
    host = profile.get("host_observation")
    if (
        not isinstance(host, dict)
        or set(host) != {"machine", "system"}
        or (host.get("system"), host.get("machine"))
        not in {
            ("Darwin", "arm64"),
            ("Darwin", "x86_64"),
            ("Linux", "aarch64"),
            ("Linux", "arm64"),
            ("Linux", "x86_64"),
        }
    ):
        add_error(errors, f"{role}_runtime_profile_host_observation_invalid")
    observations = profile.get("executable_observations")
    if not isinstance(observations, list) or len(observations) != (
        2 if role == "java" else 1
    ):
        add_error(errors, f"{role}_runtime_profile_observation_count_mismatch")
        observations = []
    expected_functions = {
        "python": ["interpreter"],
        "node": ["runtime"],
        "java": ["runtime", "compiler"],
    }[role]
    if [
        item.get("function") for item in observations if isinstance(item, dict)
    ] != expected_functions:
        add_error(errors, f"{role}_runtime_profile_function_inventory_mismatch")
    for observation in observations:
        if (
            not isinstance(observation, dict)
            or set(observation)
            != {
                "byte_count",
                "function",
                "invocation_path",
                "raw_sha256",
                "resolved_path",
                "version_probe",
            }
            or not isinstance(observation.get("invocation_path"), str)
            or not observation.get("invocation_path")
            or not isinstance(observation.get("resolved_path"), str)
            or not observation.get("resolved_path")
            or not isinstance(observation.get("raw_sha256"), str)
            or SHA256_RE.fullmatch(observation["raw_sha256"]) is None
            or isinstance(observation.get("byte_count"), bool)
            or not isinstance(observation.get("byte_count"), int)
            or observation["byte_count"] <= 0
        ):
            add_error(errors, f"{role}_runtime_profile_observation_shape_invalid")
        probe = (
            observation.get("version_probe", {})
            if isinstance(observation, dict)
            else {}
        )
        probe_path_text = probe.get("repository_path")
        if not isinstance(probe_path_text, str):
            add_error(errors, f"{role}_runtime_version_probe_path_invalid")
            continue
        probe_path = ROOT / probe_path_text
        if not probe_path.is_file():
            add_error(errors, f"{role}_runtime_version_probe_missing")
            continue
        digest, count = path_binding(probe_path)
        if (
            probe.get("exit_code") != 0
            or isinstance(probe.get("exit_code"), bool)
            or probe.get("raw_sha256") != digest
            or probe.get("byte_count") != count
            or isinstance(probe.get("byte_count"), bool)
        ):
            add_error(errors, f"{role}_runtime_version_probe_binding_mismatch")
    return errors


def validate_source_independence(retained: Retained, errors: list[str]) -> None:
    implementation_ids = [
        retained.results[role].get("implementation", {}).get("implementation_id")
        for role in ROLE_KEYS
    ]
    source_digests = [
        retained.results[role].get("implementation", {})
        .get("source_binding", {})
        .get("raw_sha256")
        for role in ROLE_KEYS
    ]
    adapter_digests = [path_binding(ADAPTER_PATHS[role])[0] for role in ROLE_KEYS]
    lock_digests = [path_binding(DEPENDENCY_LOCK_PATHS[role])[0] for role in ROLE_KEYS]
    if len(set(implementation_ids)) != 3 or None in implementation_ids:
        add_error(errors, "implementation_identity_not_unique")
    if len(set(source_digests)) != 3 or None in source_digests:
        add_error(errors, "implementation_source_digest_not_unique")
    if len(set(adapter_digests)) != 3:
        add_error(errors, "implementation_adapter_bytes_shared")
    if len(set(lock_digests)) != 3:
        add_error(errors, "implementation_dependency_lock_bytes_shared")
    path_sets: dict[str, set[str]] = {}
    source_digest_sets: dict[str, set[str]] = {}
    expected_source_paths = {
        "python": [
            "tests/human-decision-assurance-successor/python/evaluator.py",
            "tests/human-decision-assurance-successor/python/input_adapter.py",
        ],
        "node": [
            "tests/human-decision-assurance-successor/node/src/evaluator.mjs",
            "tests/human-decision-assurance-successor/node/src/input-adapter.mjs",
            "tests/human-decision-assurance-successor/node/src/cli.mjs",
        ],
        "java": [str(path.relative_to(ROOT)) for path in JAVA_SOURCES],
    }
    for role in ROLE_KEYS:
        manifest = retained.source_manifests[role]
        expected_implementation_id = retained.results[role].get("implementation", {}).get(
            "implementation_id"
        )
        if (
            manifest.get("artifact_class")
            != "human_decision_assurance_evaluator_source_manifest"
            or manifest.get("artifact_id")
            != IMPLEMENTATION_ARTIFACT_IDS[role]["source_binding"]
            or manifest.get("implementation_id") != expected_implementation_id
            or manifest.get("implementation_role") != IMPLEMENTATION_ROLES[role]
            or manifest.get("manifest_self_digest_forbidden") is not True
            or manifest.get("expected_result_fixture_consumed") is not False
            or manifest.get("generated_source_consumed") is not False
            or manifest.get("peer_implementation_source_consumed") is not False
            or manifest.get("shared_source_files_with_peer_implementations") != []
        ):
            add_error(errors, f"{role}_source_manifest_boundary_mismatch")
        rows = manifest.get("source_files")
        if not isinstance(rows, list) or manifest.get("source_file_count") != len(rows):
            add_error(errors, f"{role}_source_manifest_count_mismatch")
            rows = []
        row_paths = [
            row.get("repository_path") for row in rows if isinstance(row, dict)
        ]
        if row_paths != expected_source_paths[role]:
            add_error(errors, f"{role}_source_manifest_inventory_mismatch")
        actual_source_digests: set[str] = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict) or row.get("sequence_index") != index:
                add_error(errors, f"{role}_source_manifest_sequence_mismatch")
                continue
            path_text = row.get("repository_path")
            if not isinstance(path_text, str):
                add_error(errors, f"{role}_source_manifest_path_invalid")
                continue
            source_path = ROOT / path_text
            if source_path.is_symlink() or not source_path.is_file():
                add_error(errors, f"{role}_source_manifest_file_unreadable", path_text)
                continue
            digest, count = path_binding(source_path)
            actual_source_digests.add(digest)
            if row.get("raw_sha256") != digest or row.get("byte_count") != count:
                add_error(errors, f"{role}_source_manifest_file_binding_mismatch", path_text)
        source_digest_sets[role] = actual_source_digests
        paths = manifest_source_paths(manifest)
        if not paths:
            add_error(errors, f"{role}_source_manifest_has_no_paths")
            path_sets[role] = set()
            continue
        normalized: set[str] = set()
        expected_prefix = f"tests/human-decision-assurance-successor/{role}/"
        for path_text in paths:
            if path_text in normalized:
                add_error(errors, f"{role}_source_manifest_duplicate_path")
            normalized.add(path_text)
            if not path_text.startswith(expected_prefix) or ".." in Path(path_text).parts:
                add_error(errors, f"{role}_source_manifest_cross_boundary_path", path_text)
        path_sets[role] = normalized
    for index, left in enumerate(ROLE_KEYS):
        for right in ROLE_KEYS[index + 1 :]:
            if path_sets[left].intersection(path_sets[right]):
                add_error(errors, "implementation_source_path_shared", f"{left}/{right}")
            if source_digest_sets.get(left, set()).intersection(
                source_digest_sets.get(right, set())
            ):
                add_error(errors, "implementation_source_file_bytes_shared", f"{left}/{right}")

    generated_paths = {
        row.get("repository_path")
        for row in retained.generation_manifest.get("generated_artifacts", [])
        if isinstance(row, dict) and isinstance(row.get("repository_path"), str)
    }
    all_source_paths = set().union(*path_sets.values()) if path_sets else set()
    generated_source_overlap = generated_paths.intersection(all_source_paths)
    if generated_source_overlap:
        add_error(
            errors,
            "evaluator_source_listed_as_generated_artifact",
            ",".join(sorted(generated_source_overlap)),
        )

    configurations = {role: load_json(CONFIG_PATHS[role]) for role in ROLE_KEYS}
    for role, configuration in configurations.items():
        implementation_id = retained.results[role]["implementation"]["implementation_id"]
        if configuration.get("implementation_id") != implementation_id:
            add_error(errors, f"{role}_configuration_implementation_id_mismatch")
    python_config = configurations["python"]
    if (
        python_config.get("expected_answer_input_allowed") is not False
        or python_config.get("peer_implementation_input_allowed") is not False
        or python_config.get("network_access") is not False
    ):
        add_error(errors, "python_configuration_nonsharing_boundary_escalated")
    node_contract = configurations["node"].get("input_contract", {})
    if (
        node_contract.get("expected_answers_permitted") is not False
        or node_contract.get("other_implementation_outputs_permitted") is not False
        or configurations["node"].get("runtime", {}).get("network_access") is not False
        or configurations["node"].get("runtime", {}).get("third_party_runtime_dependencies") != []
    ):
        add_error(errors, "node_configuration_nonsharing_boundary_escalated")
    java_contract = configurations["java"].get("input_contract", {})
    if (
        java_contract.get("expected_result_fixture_access") is not False
        or java_contract.get("another_implementation_output_access") is not False
        or configurations["java"].get("execution", {}).get("network_access") is not False
    ):
        add_error(errors, "java_configuration_nonsharing_boundary_escalated")

    toolchain_lock = ROOT / "tools/repository-release/toolchain.lock.json"
    lock_digest, lock_count = path_binding(toolchain_lock)
    for role, profile_path in RUNTIME_PROFILE_PATHS.items():
        profile = load_json(profile_path)
        errors.extend(
            runtime_profile_errors(profile, role, lock_digest, lock_count)
        )


def validate_common_input_manifest(retained: Retained, errors: list[str]) -> None:
    # The manifest is an architecture record, never evaluator input.  It must
    # not expose answers or downstream identities and all result records must
    # bind its same exact bytes.
    forbidden = ANSWER_ONLY_KEYS.intersection(walk_keys(retained.input_manifest))
    if forbidden:
        add_error(errors, "input_manifest_contains_expected_or_output_material")
    manifest = retained.input_manifest
    if (
        manifest.get("artifact_class")
        != "human_decision_assurance_successor_expectation_free_safe_input_manifest"
        or manifest.get("artifact_id") != INPUT_MANIFEST_ARTIFACT_ID
        or manifest.get("assurance_id") != retained.evidence.get("assurance_id")
        or manifest.get("expected_answer_values_present") is not False
        or manifest.get("peer_output_values_present") is not False
        or manifest.get("manifest_self_digest_forbidden") is not True
        or manifest.get("vector_id") != "safe-complete-eligible"
    ):
        add_error(errors, "input_manifest_identity_or_boundary_mismatch")
    normative = load_json(NORMATIVE_INPUT_PATH)
    if normative != retained.vectors.get("base_input"):
        add_error(errors, "materialized_normative_input_not_exact_base_vector")
    check_raw_binding(
        manifest.get("materialized_normative_input"),
        NORMATIVE_INPUT_PATH,
        "input_manifest_materialized_vector",
        errors,
        artifact_id=NORMATIVE_INPUT_ARTIFACT_ID,
    )
    materialization = manifest.get("materialization_contract", {})
    if materialization != {
        "base_input_source": "vectors.json#base_input",
        "materialized_input_equals_base_input": True,
        "selected_vector_id": "safe-complete-eligible",
        "selected_vector_mutation_count": 0,
    }:
        add_error(errors, "input_manifest_materialization_contract_mismatch")
    process = manifest.get("process_read_set", {})
    check_raw_binding(
        process.get("expectation_free_vector_corpus"),
        VECTORS_PATH,
        "input_manifest_vector_corpus",
        errors,
        artifact_id=VECTOR_CORPUS_ARTIFACT_ID,
    )
    check_ruleset_binding(process.get("eligibility_ruleset"), "input_manifest", errors)
    resolver_binding = process.get("content_address_resolver_profile", {})
    resolver_digest, resolver_count = path_binding(RESOLVER_PATH)
    if (
        resolver_binding.get("artifact_id")
        != "hda-content-address-resolver-profile.0001"
        or resolver_binding.get("raw_sha256") != resolver_digest
        or resolver_binding.get("byte_count") != resolver_count
        or resolver_binding.get("mutable_alias_used") is not False
    ):
        add_error(errors, "input_manifest_resolver_binding_mismatch")
    upstream = manifest.get("upstream_bindings", {})
    check_raw_binding(
        upstream.get("evidence"),
        EVIDENCE_PATH,
        "input_manifest_evidence",
        errors,
        artifact_id=retained.evidence.get("artifact_id"),
        schema_id=EVIDENCE_SCHEMA_ID,
    )
    check_raw_binding(
        upstream.get("backing_byte_verification_receipt"),
        BACKING_PATH,
        "input_manifest_backing",
        errors,
        artifact_id=retained.backing.get("artifact_id"),
        schema_id=BACKING_SCHEMA_ID,
    )
    process_strings = set(
        walk_strings(retained.input_manifest.get("process_read_set", {}))
    )
    process_strings.update(
        walk_strings(retained.input_manifest.get("materialized_normative_input", {}))
    )
    if "cases.json" in process_strings or str(CASES_PATH.relative_to(ROOT)) in process_strings:
        add_error(errors, "input_manifest_names_private_answer_corpus")
    strings = set(walk_strings(retained.input_manifest))
    for path in (*RESULT_PATHS.values(), *PROJECTION_PATHS.values(), COMPARISON_PATH, SEAL_PATH):
        if str(path.relative_to(ROOT)) in strings:
            add_error(errors, "input_manifest_names_downstream_output")
    bindings = [retained.results[role].get("input_bindings") for role in ROLE_KEYS]
    if not all(binding == bindings[0] for binding in bindings[1:]):
        add_error(errors, "result_common_input_bindings_disagree")
    if bindings and isinstance(bindings[0], dict):
        expected_common = {
            "evidence": upstream.get("evidence"),
            "backing_byte_verification_receipt": upstream.get(
                "backing_byte_verification_receipt"
            ),
            "eligibility_ruleset": process.get("eligibility_ruleset"),
            "input_manifest": {
                "artifact_id": manifest.get("artifact_id"),
                "raw_sha256": path_binding(INPUT_MANIFEST_PATH)[0],
                "byte_count": path_binding(INPUT_MANIFEST_PATH)[1],
                "mutable_alias_used": False,
            },
            "normative_input_vector": manifest.get("materialized_normative_input"),
        }
        if bindings[0] != expected_common:
            add_error(errors, "result_common_input_bindings_not_exact_manifest_projection")


def validate_comparison(retained: Retained, errors: list[str]) -> None:
    comparison = retained.comparison
    validate_schema(retained.schemas["comparison"], comparison, "comparison", errors)
    if (
        comparison.get("artifact_id") != COMPARISON_ARTIFACT_ID
        or comparison.get("assurance_id") != retained.evidence.get("assurance_id")
    ):
        add_error(errors, "comparison_identity_mismatch")
    common = comparison.get("common_input_bindings")
    if common != retained.results["python"].get("input_bindings"):
        add_error(errors, "comparison_common_input_bindings_mismatch")
    identities: list[Any] = []
    sources: list[Any] = []
    readable: list[dict[str, Any]] = []
    unavailable: list[tuple[str, str]] = []
    result_bindings = comparison.get("ordered_result_bindings", [])
    if not isinstance(result_bindings, list) or len(result_bindings) != 3:
        add_error(errors, "comparison_result_binding_count_mismatch")
        if not isinstance(result_bindings, list):
            result_bindings = []
    readable_result_digests: list[str] = []
    readable_result_ids: list[str] = []
    for index, role in enumerate(ROLE_KEYS):
        result = retained.results[role]
        implementation = result.get("implementation", {})
        identities.append(implementation.get("implementation_id"))
        source_digest = implementation.get("source_binding", {}).get("raw_sha256")
        sources.append(source_digest)
        projection = raw_projection_to_full(retained.projections[role])
        if index >= len(result_bindings) or not isinstance(result_bindings[index], dict):
            unavailable.append((IMPLEMENTATION_ROLES[role], "missing"))
            continue
        binding = result_bindings[index]
        read_disposition = binding.get("read_disposition")
        if read_disposition != "readable_complete":
            unavailable.append(
                (
                    IMPLEMENTATION_ROLES[role],
                    "missing" if read_disposition == "missing" else "unreadable",
                )
            )
        else:
            readable.append(projection)
            if isinstance(binding.get("raw_sha256"), str):
                readable_result_digests.append(binding["raw_sha256"])
            if isinstance(binding.get("artifact_id"), str):
                readable_result_ids.append(binding["artifact_id"])
        digest, count = path_binding(RESULT_PATHS[role])
        expected = {
            "implementation_role": IMPLEMENTATION_ROLES[role],
            "implementation_id": implementation.get("implementation_id"),
            "implementation_source_sha256": source_digest,
            "artifact_id": result.get("artifact_id"),
            "schema_resource_id": RESULT_SCHEMA_ID,
            "read_disposition": read_disposition,
            "raw_sha256": digest if read_disposition == "readable_complete" else None,
            "byte_count": count if read_disposition == "readable_complete" else None,
            "projection": projection if read_disposition == "readable_complete" else None,
        }
        if binding != expected:
            add_error(errors, f"comparison_{role}_result_binding_mismatch")
    if len(readable_result_digests) != len(set(readable_result_digests)) or len(
        readable_result_ids
    ) != len(set(readable_result_ids)):
        add_error(errors, "comparison_result_bytes_reused")
    if comparison.get("implementation_identity_inventory") != identities:
        add_error(errors, "comparison_implementation_identity_inventory_mismatch")
    if comparison.get("implementation_source_digest_inventory") != sources:
        add_error(errors, "comparison_source_digest_inventory_mismatch")

    expected_fields = []
    disagreement_fields: list[str] = []
    for field in OUTPUT_FIELD_ORDER:
        disagreement = len(readable) >= 2 and any(
            item.get(field) != readable[0].get(field) for item in readable[1:]
        )
        if disagreement:
            field_disposition = "disagreement"
            disagreement_fields.append(field)
        elif unavailable:
            field_disposition = "missing_or_unreadable"
        else:
            field_disposition = "agreement"
        expected_fields.append(
            {"field": field, "comparison_disposition": field_disposition}
        )
    if comparison.get("field_comparisons") != expected_fields:
        add_error(errors, "comparison_field_comparisons_not_semantically_recomputed")
    if disagreement_fields:
        expected_disposition = "invalid_disagreement"
    elif unavailable:
        expected_disposition = "indeterminate_missing_or_unreadable"
    else:
        expected_disposition = "exact_agreement"
    if comparison.get("comparison_disposition") != expected_disposition:
        add_error(errors, "comparison_disposition_mismatch")
    expected_projection = readable[0] if expected_disposition == "exact_agreement" else None
    if comparison.get("agreed_projection") != expected_projection:
        add_error(errors, "comparison_agreed_projection_mismatch")
    if expected_disposition == "exact_agreement":
        expected_reasons = [
            "eligible.comparison.exact_three_way_full_projection_agreement"
        ]
    else:
        reason_set = {
            f"indeterminate.comparison.{role}.result_{state}"
            for role, state in unavailable
        }
        reason_set.update(
            f"invalid.comparison.{field}.disagreement"
            for field in disagreement_fields
        )
        expected_reasons = sorted(reason_set, key=lambda value: value.encode("ascii"))
    if comparison.get("reason_codes") != expected_reasons:
        add_error(errors, "comparison_reason_codes_mismatch")


def expected_seal_disposition(backing: str, comparison: str, agreed: Any) -> str:
    if backing == "invalid" or comparison == "invalid_disagreement" or agreed == "invalid":
        return "invalid"
    if backing != "supported" or comparison != "exact_agreement" or agreed != "eligible":
        return "indeterminate"
    return "eligible"


def validate_seal(retained: Retained, errors: list[str]) -> None:
    seal = retained.seal
    comparison = retained.comparison
    validate_schema(retained.schemas["seal"], seal, "seal", errors)
    if (
        seal.get("schema_version") != "0.2.0"
        or seal.get("artifact_id") != SEAL_ARTIFACT_ID
    ):
        add_error(errors, "seal_resource_identity_version_mismatch")
    if seal.get("assurance_id") != retained.evidence.get("assurance_id"):
        add_error(errors, "seal_assurance_id_mismatch")
    bindings = seal.get("input_bindings", {})
    if not isinstance(bindings, dict):
        bindings = {}
    if "backing_byte_verification_receipt" not in bindings:
        add_error(errors, "seal_backing_receipt_binding_missing")
    if "eligibility_comparison_receipt" not in bindings:
        add_error(errors, "seal_comparison_receipt_binding_missing")
    check_raw_binding(
        bindings.get("core"), CORE_PATH, "seal_core", errors,
        schema_id="urn:odeya:schema:human-decision-assurance-core:0.1.0",
    )
    check_raw_binding(
        bindings.get("evidence"), EVIDENCE_PATH, "seal_evidence", errors,
        artifact_id=retained.evidence.get("artifact_id"), schema_id=EVIDENCE_SCHEMA_ID,
    )
    check_ruleset_binding(bindings.get("eligibility_ruleset"), "seal", errors)
    check_raw_binding(
        bindings.get("backing_byte_verification_receipt"), BACKING_PATH,
        "seal_backing", errors, artifact_id=retained.backing.get("artifact_id"),
        schema_id=BACKING_SCHEMA_ID,
    )
    check_raw_binding(
        bindings.get("eligibility_comparison_receipt"), COMPARISON_PATH,
        "seal_comparison", errors, artifact_id=comparison.get("artifact_id"),
        schema_id=COMPARISON_SCHEMA_ID,
    )
    receipt = seal.get("receipt_dispositions", {})
    expected_receipt = {
        "backing_byte_verification": retained.backing.get("verification_disposition"),
        "eligibility_comparison": comparison.get("comparison_disposition"),
        "agreed_recomputation_disposition": (
            comparison.get("agreed_projection", {}).get("final_disposition")
            if isinstance(comparison.get("agreed_projection"), dict)
            else None
        ),
    }
    if receipt != expected_receipt:
        add_error(errors, "seal_receipt_dispositions_not_copied")
    if seal.get("copied_agreed_projection") != comparison.get("agreed_projection"):
        add_error(errors, "seal_agreed_projection_not_exact_copy")
    expected_disposition = expected_seal_disposition(
        expected_receipt["backing_byte_verification"],
        expected_receipt["eligibility_comparison"],
        expected_receipt["agreed_recomputation_disposition"],
    )
    if seal.get("assurance_disposition") != expected_disposition:
        add_error(errors, "seal_precedence_disposition_mismatch")
    expected_policy = (
        "may_enter_assured_decision_assembly_only"
        if expected_disposition == "eligible"
        else "blocked"
    )
    if seal.get("decision_entry", {}).get("policy_entry") != expected_policy:
        add_error(errors, "seal_policy_entry_mismatch")
    if expected_disposition == "eligible":
        agreed = comparison.get("agreed_projection", {})
        expected_reasons = (
            agreed.get("reason_codes", []) if isinstance(agreed, dict) else []
        )
    else:
        reason_set: set[str] = set()
        if expected_receipt["backing_byte_verification"] != "supported":
            reason_set.update(
                code
                for code in retained.backing.get("reason_codes", [])
                if isinstance(code, str) and not code.startswith("supported.")
            )
        if expected_receipt["eligibility_comparison"] != "exact_agreement":
            reason_set.update(
                code
                for code in comparison.get("reason_codes", [])
                if isinstance(code, str) and not code.startswith("eligible.")
            )
        elif isinstance(comparison.get("agreed_projection"), dict):
            reason_set.update(
                code
                for code in comparison["agreed_projection"].get("reason_codes", [])
                if isinstance(code, str) and not code.startswith("eligible.")
            )
        expected_reasons = sorted(reason_set, key=lambda value: value.encode("ascii"))
    if seal.get("reason_codes") != expected_reasons:
        add_error(errors, "seal_reason_codes_mismatch")
    if expected_disposition != "eligible" and any(
        isinstance(code, str) and code.startswith("eligible.")
        for code in seal.get("reason_codes", [])
    ):
        add_error(errors, "seal_positive_reason_on_negative_disposition")


def validate_generation_manifest(retained: Retained, errors: list[str]) -> None:
    manifest = retained.generation_manifest
    manifest_id = GENERATION_MANIFEST_ARTIFACT_ID
    if (
        manifest.get("artifact_class")
        != "human_decision_assurance_successor_generation_manifest"
        or manifest.get("artifact_id") != manifest_id
        or manifest.get("assurance_id") != retained.evidence.get("assurance_id")
        or manifest.get("manifest_self_digest_forbidden") is not True
        or manifest.get("complete_projection_agreement") is not True
        or manifest.get("content_addressed_backing_blob_count") != 14
        or manifest.get("schema_valid_fixture_count") != 7
        or manifest.get("fixture_timestamp_semantics")
        != (
            "deterministic_fixture_values_not_observed_ceremony_runtime_or_"
            "external_event_times"
        )
        or manifest.get("network_access") is not False
        or manifest.get("real_human_ceremony_verified") is not False
        or manifest.get("organizational_independence_proven") is not False
        or manifest.get("gate_a_accepted") is not False
        or manifest.get("runtime_authorized") is not False
        or manifest.get("external_effects_authorized") is not False
    ):
        add_error(errors, "generation_manifest_identity_or_boundary_mismatch")
    if manifest.get("generator_source_binding") != expected_manifest_entry(
        "hda-successor-evidence-generator.python.0005",
        GENERATOR_PATH,
        "retained_evidence_generator",
    ):
        add_error(errors, "generation_manifest_generator_binding_mismatch")
    if manifest.get("predecessor_candidate") != PREDECESSOR_SUBJECT:
        add_error(errors, "generation_manifest_predecessor_binding_mismatch")
    relation = retained.backing.get("confirmation_receipt_frame_relation", {})
    relation_receipt_digest = (
        relation.get("observed_frame_raw_sha256")
        if isinstance(relation, dict)
        else None
    )
    expected_challenge_recomputation = recompute_successor_phase_two_challenge(
        retained, relation_receipt_digest, errors
    )
    if (
        expected_challenge_recomputation is None
        or manifest.get("phase_two_challenge_recomputation")
        != expected_challenge_recomputation
    ):
        add_error(errors, "generation_manifest_phase_two_recomputation_mismatch")
    expected_review_scope = {
        "scope_id": "hda-successor-t0-technical-review-scope.0005",
        "scope_semantics": (
            "the_exact_generation_manifest_and_every_direct_or_transitively_"
            "bound_t0_member_excluding_the_later_review_report_and_status_prose"
        ),
        "direct_input_bindings": [
            expected_manifest_entry(
                VECTOR_CORPUS_ARTIFACT_ID,
                VECTORS_PATH,
                "expectation_free_vector_corpus",
            ),
            expected_manifest_entry(
                "hda-successor-case-answers.0001",
                CASES_PATH,
                "private_conformance_answer_corpus",
            ),
            expected_manifest_entry(
                "hda-successor-chain-known-bads.0002",
                CHAIN_CASES_PATH,
                "downstream_chain_known_bad_corpus",
            ),
            expected_manifest_entry(
                "hda-successor-validator.python.0005",
                Path(__file__).resolve(),
                "separately_implemented_retained_chain_validator",
            ),
            expected_manifest_entry(
                "hda-individual-eligibility-ruleset.v2.0001",
                RULESET_PATH,
                "normative_eligibility_ruleset",
            ),
            expected_manifest_entry(
                "hda-content-address-resolver-profile.0001",
                RESOLVER_PATH,
                "content_address_resolver_profile",
            ),
            expected_manifest_entry(
                "hda-challenge-frame-profile.v2.0001",
                CHALLENGE_PROFILE_PATH,
                "challenge_frame_profile",
            ),
            expected_manifest_entry(
                "hda-challenge-frame-v2-evidence.0001",
                CHALLENGE_EVIDENCE_PATH,
                "challenge_frame_source_vector_evidence",
            ),
            expected_manifest_entry(
                "hda-core-fixture.synthetic.0001",
                CORE_PATH,
                "exact_core_fixture",
            ),
            expected_manifest_entry(
                "hda-decision-subject-fixture.synthetic.0001",
                DECISION_PATH,
                "exact_decision_subject_fixture",
            ),
            expected_manifest_entry(
                "hda-candidate-manifest-fixture.synthetic.0001",
                CANDIDATE_MANIFEST_PATH,
                "exact_candidate_manifest_fixture",
            ),
            expected_manifest_entry(
                "repository-release-toolchain-lock.0001",
                TOOLCHAIN_LOCK_PATH,
                "toolchain_lock",
            ),
            expected_manifest_entry(
                "architecture-python-requirements-source.0001",
                ARCHITECTURE_REQUIREMENTS_SOURCE_PATH,
                "python_requirements_source",
            ),
            expected_manifest_entry(
                "architecture-python-requirements-lock.0001",
                ARCHITECTURE_REQUIREMENTS_LOCK_PATH,
                "hash_locked_python_environment",
            ),
            *[
                expected_manifest_entry(
                    f"hda-evaluator-configuration.{IMPLEMENTATION_ROLES[role]}.0001",
                    CONFIG_PATHS[role],
                    "evaluator_configuration",
                )
                for role in ROLE_KEYS
            ],
            *[
                expected_manifest_entry(
                    f"hda-dependency-lock.{IMPLEMENTATION_ROLES[role]}.0001",
                    DEPENDENCY_LOCK_PATHS[role],
                    "evaluator_dependency_lock",
                )
                for role in ROLE_KEYS
            ],
        ],
        "transitive_binding_roots": [
            "generator_source_binding",
            "normative_schema_bindings",
            "generated_artifacts",
        ],
        "generation_manifest_self_digest_forbidden": True,
        "any_bound_member_byte_change_invalidates_review": True,
        "review_report_is_out_of_scope_to_avoid_self_reference": True,
    }
    if manifest.get("bounded_technical_review_scope") != expected_review_scope:
        add_error(errors, "generation_manifest_technical_review_scope_mismatch")

    inventory = retained.evidence.get("ordered_artifact_inventory", [])
    expected_paths = {
        item.get("repository_blob_path")
        for item in inventory
        if isinstance(item, dict)
    }
    expected_paths.update(
        str(path.relative_to(ROOT))
        for path in (
            EVIDENCE_PATH,
            BACKING_PATH,
            NORMATIVE_INPUT_PATH,
            INPUT_MANIFEST_PATH,
            *SOURCE_MANIFEST_PATHS.values(),
            *RUNTIME_PROFILE_PATHS.values(),
            *PROJECTION_PATHS.values(),
            *RESULT_PATHS.values(),
            SUITE / "runtime/python-3-14-2.version.txt",
            SUITE / "runtime/nodejs-24-18-0.version.txt",
            SUITE / "runtime/java-21-0-9.version.txt",
            SUITE / "runtime/javac-21-0-9.version.txt",
            COMPARISON_PATH,
            SEAL_PATH,
        )
    )
    rows = manifest.get("generated_artifacts")
    if not isinstance(rows, list):
        add_error(errors, "generation_manifest_artifacts_not_array")
        rows = []
    observed_paths: list[str] = []
    observed_ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "artifact_id",
            "artifact_kind",
            "byte_count",
            "raw_sha256",
            "repository_path",
        }:
            add_error(errors, "generation_manifest_artifact_row_shape_mismatch")
            continue
        path_text = row.get("repository_path")
        artifact_id = row.get("artifact_id")
        if not isinstance(path_text, str) or Path(path_text).is_absolute() or ".." in Path(path_text).parts:
            add_error(errors, "generation_manifest_artifact_path_invalid")
            continue
        observed_paths.append(path_text)
        if isinstance(artifact_id, str):
            observed_ids.append(artifact_id)
        artifact_path = ROOT / path_text
        if artifact_path.is_symlink() or not artifact_path.is_file():
            add_error(errors, "generation_manifest_artifact_unreadable", path_text)
            continue
        digest, count = path_binding(artifact_path)
        if row.get("raw_sha256") != digest or row.get("byte_count") != count:
            add_error(errors, "generation_manifest_artifact_binding_mismatch", path_text)
    if set(observed_paths) != expected_paths or len(observed_paths) != len(expected_paths):
        add_error(errors, "generation_manifest_artifact_inventory_not_exact")
    if len(observed_paths) != len(set(observed_paths)):
        add_error(errors, "generation_manifest_artifact_path_duplicate")
    if len(observed_ids) != len(set(observed_ids)):
        add_error(errors, "generation_manifest_artifact_id_duplicate")

    schema_rows = manifest.get("normative_schema_bindings")
    if not isinstance(schema_rows, list):
        add_error(errors, "generation_manifest_schema_bindings_not_array")
        schema_rows = []
    expected_schema_paths = [str(path.relative_to(ROOT)) for path in SCHEMA_PATHS.values()]
    if [row.get("repository_path") for row in schema_rows if isinstance(row, dict)] != expected_schema_paths:
        add_error(errors, "generation_manifest_schema_inventory_not_exact")
    for row, path in zip(schema_rows, SCHEMA_PATHS.values(), strict=False):
        if not isinstance(row, dict):
            continue
        digest, count = path_binding(path)
        if (
            row.get("artifact_kind") != "json_schema"
            or row.get("raw_sha256") != digest
            or row.get("byte_count") != count
        ):
            add_error(errors, "generation_manifest_schema_binding_mismatch", str(path.relative_to(ROOT)))

    expected_edges = [
        {"from": retained.evidence.get("artifact_id"), "to": retained.backing.get("artifact_id")},
        {"from": retained.backing.get("artifact_id"), "to": retained.input_manifest.get("artifact_id")},
        *[
            {
                "from": retained.input_manifest.get("artifact_id"),
                "to": IMPLEMENTATION_ARTIFACT_IDS[role]["raw_projection_binding"],
            }
            for role in ROLE_KEYS
        ],
        *[
            {
                "from": IMPLEMENTATION_ARTIFACT_IDS[role]["raw_projection_binding"],
                "to": retained.results[role].get("artifact_id"),
            }
            for role in ROLE_KEYS
        ],
        *[
            {
                "from": retained.results[role].get("artifact_id"),
                "to": retained.comparison.get("artifact_id"),
            }
            for role in ROLE_KEYS
        ],
        {"from": retained.comparison.get("artifact_id"), "to": retained.seal.get("artifact_id")},
        {"from": retained.seal.get("artifact_id"), "to": manifest_id},
    ]
    edges = manifest.get("chain_edges")
    if edges != expected_edges:
        add_error(errors, "generation_manifest_chain_edges_mismatch")
    graph: dict[str, set[str]] = {}
    for edge in edges if isinstance(edges, list) else []:
        if not isinstance(edge, dict) or set(edge) != {"from", "to"}:
            add_error(errors, "generation_manifest_chain_edge_shape_mismatch")
            continue
        source, target = edge.get("from"), edge.get("to")
        if not isinstance(source, str) or not isinstance(target, str):
            add_error(errors, "generation_manifest_chain_edge_identity_invalid")
            continue
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set())
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        visiting.add(node)
        if not all(visit(child) for child in graph.get(node, set())):
            return False
        visiting.remove(node)
        visited.add(node)
        return True

    if not all(visit(node) for node in graph):
        add_error(errors, "generation_manifest_chain_cycle")
    manifest_digest = raw_sha256(GENERATION_MANIFEST_PATH.read_bytes())
    if manifest_digest in set(walk_strings(manifest)):
        add_error(errors, "generation_manifest_contains_self_digest")
    if any(row.get("repository_path") == str(GENERATION_MANIFEST_PATH.relative_to(ROOT)) for row in rows if isinstance(row, dict)):
        add_error(errors, "generation_manifest_includes_itself_in_artifact_inventory")


def forbidden_downstream_key(key: str) -> bool:
    lowered = key.lower()
    return (
        lowered in {"seal", "seal_id", "seal_digest", "seal_sha256", "seal_binding"}
        or lowered.startswith("seal_")
        or lowered.endswith("_seal_binding")
    )


def validate_acyclicity(retained: Retained, errors: list[str]) -> None:
    seal_raw = SEAL_PATH.read_bytes()
    seal_digest = raw_sha256(seal_raw)
    seal_id = retained.seal.get("artifact_id")
    forbidden_values = {SEAL_SCHEMA_ID, seal_digest}
    if isinstance(seal_id, str):
        forbidden_values.add(seal_id)
    upstream: dict[str, dict[str, Any]] = {
        "backing": retained.backing,
        **{f"{role}_result": retained.results[role] for role in ROLE_KEYS},
        "comparison": retained.comparison,
    }
    for label, value in upstream.items():
        if forbidden_values.intersection(walk_strings(value)):
            add_error(errors, f"{label}_names_or_hashes_downstream_seal")
        suspicious = [key for key in walk_keys(value) if forbidden_downstream_key(key)]
        # The schemas deliberately carry one false proof-boundary assertion.
        suspicious = [
            key
            for key in suspicious
            if key not in {"receipt_names_or_predicts_seal_identity", "result_names_or_predicts_seal_identity"}
        ]
        if suspicious:
            add_error(errors, f"{label}_contains_downstream_seal_binding_key")
        path = BACKING_PATH if label == "backing" else COMPARISON_PATH if label == "comparison" else RESULT_PATHS[label.removesuffix("_result")]
        if raw_sha256(path.read_bytes()) in set(walk_strings(value)):
            add_error(errors, f"{label}_contains_forbidden_self_digest")

    levels: list[list[tuple[str, dict[str, Any], Path]]] = [
        [("evidence", retained.evidence, EVIDENCE_PATH)],
        [("backing", retained.backing, BACKING_PATH)],
        [("input_manifest", retained.input_manifest, INPUT_MANIFEST_PATH)],
        [
            (f"{role}_result", retained.results[role], RESULT_PATHS[role])
            for role in ROLE_KEYS
        ],
        [("comparison", retained.comparison, COMPARISON_PATH)],
        [("seal", retained.seal, SEAL_PATH)],
        [("generation_manifest", retained.generation_manifest, GENERATION_MANIFEST_PATH)],
    ]
    identities: list[list[tuple[str, str]]] = []
    for level in levels:
        current: list[tuple[str, str]] = []
        for _, value, path in level:
            artifact_id = value.get("artifact_id")
            if isinstance(artifact_id, str):
                current.append((artifact_id, raw_sha256(path.read_bytes())))
        identities.append(current)
    for level_index, level in enumerate(levels[:-1]):
        later = {
            identity
            for later_level in identities[level_index + 1 :]
            for pair in later_level
            for identity in pair
        }
        for label, value, _ in level:
            if later.intersection(walk_strings(value)):
                add_error(errors, f"{label}_contains_forward_downstream_identity")
    result_identities = {
        identity
        for pair in identities[3]
        for identity in pair
    }
    for label, value, path in levels[3]:
        own = {value.get("artifact_id"), raw_sha256(path.read_bytes())}
        peer_identities = result_identities - own
        if peer_identities.intersection(walk_strings(value)):
            add_error(errors, f"{label}_contains_peer_result_identity")

    for level in levels:
        for label, value, path in level:
            if raw_sha256(path.read_bytes()) in set(walk_strings(value)):
                add_error(errors, f"{label}_contains_forbidden_self_digest")

    # Explicit dependency graph: edges point from a derived record to its
    # already-existing inputs.  A DFS makes the no-cycle claim executable.
    graph = {
        "evidence": {"core"},
        "backing": {"evidence"},
        "python_result": {"evidence", "backing"},
        "node_result": {"evidence", "backing"},
        "java_result": {"evidence", "backing"},
        "comparison": {"evidence", "backing", "python_result", "node_result", "java_result"},
        "seal": {"core", "evidence", "backing", "comparison"},
        "core": set(),
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        visiting.add(node)
        if not all(visit(child) for child in graph[node]):
            return False
        visiting.remove(node)
        visited.add(node)
        return True

    if not all(visit(node) for node in graph):
        add_error(errors, "assurance_dependency_cycle")


TOOLCHAIN_OVERRIDE_NAMES = (
    "ODEYA_HDA_PYTHON",
    "ODEYA_HDA_NODE",
    "ODEYA_HDA_JAVA",
    "ODEYA_HDA_JAVAC",
)


def reject_toolchain_overrides(environment: Mapping[str, str]) -> None:
    present = [name for name in TOOLCHAIN_OVERRIDE_NAMES if name in environment]
    if present:
        raise RuntimeError(
            "HDA executable overrides are forbidden: " + ", ".join(present)
        )


def evaluator_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    observed = os.environ if source is None else source
    environment = {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": os.defpath,
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }
    for name in ("SYSTEMROOT", "TMPDIR"):
        if name in observed:
            environment[name] = observed[name]
    return environment


def stream_digest_and_count(stream: Any) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        count += len(chunk)
    return "sha256:" + digest.hexdigest(), count


def streamed_path_binding(path: Path) -> tuple[str, int]:
    with path.open("rb") as stream:
        return stream_digest_and_count(stream)


def tool_cache_root() -> Path:
    configured = os.environ.get("ODEYA_TOOL_CACHE")
    return Path(
        configured
        if configured is not None
        else Path(tempfile.gettempdir()) / "odeya-release-tools"
    ).resolve()


def archive_member_binding(
    archive_path: Path,
    expected_archive_sha256: str,
    member_suffix: str,
    label: str,
) -> tuple[str, int]:
    if archive_path.is_symlink() or not archive_path.is_file():
        raise RuntimeError(f"{label} pinned installer archive is unavailable")
    archive_binding = streamed_path_binding(archive_path)
    if archive_binding[0] != "sha256:" + expected_archive_sha256:
        raise RuntimeError(f"{label} installer archive digest is not locked")
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            members = [
                member
                for member in archive.getmembers()
                if member.isfile() and member.name.endswith(member_suffix)
            ]
            if len(members) != 1:
                raise RuntimeError(
                    f"{label} archive must contain one exact {member_suffix} member"
                )
            stream = archive.extractfile(members[0])
            if stream is None:
                raise RuntimeError(f"{label} archive member is unreadable")
            with stream:
                return stream_digest_and_count(stream)
    except (OSError, tarfile.TarError) as exc:
        raise RuntimeError(f"{label} installer archive is unreadable: {exc}") from exc


def require_installed_archive_member(
    *,
    selected_path: Path,
    expected_selected_path: Path,
    archive_path: Path,
    expected_archive_sha256: str,
    member_suffix: str,
    label: str,
) -> Path:
    try:
        selected = selected_path.resolve(strict=True)
        expected_selected = expected_selected_path.resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(f"{label} selected executable is unavailable: {exc}") from exc
    if selected != expected_selected:
        raise RuntimeError(f"{label} is not the canonical installer-cache executable")
    archive_binding = archive_member_binding(
        archive_path,
        expected_archive_sha256,
        member_suffix,
        label,
    )
    if streamed_path_binding(selected) != archive_binding:
        raise RuntimeError(
            f"{label} selected executable bytes differ from the pinned archive member"
        )
    return selected


def exact_python() -> Path:
    reject_toolchain_overrides(os.environ)
    try:
        candidate = Path(sys.executable).resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(f"the verifier interpreter is unavailable: {exc}") from exc
    completed = subprocess.run(
        [str(candidate), "--version"],
        env=evaluator_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    observed = (completed.stdout + completed.stderr).strip()
    if completed.returncode != 0 or observed != "Python 3.14.2":
        raise RuntimeError("the current verifier interpreter must be Python 3.14.2")
    return candidate


def platform_key() -> str:
    system = platform.system()
    machine = platform.machine()
    mapping = {
        ("Darwin", "x86_64"): "darwin_amd64",
        ("Darwin", "arm64"): "darwin_arm64",
        ("Linux", "x86_64"): "linux_amd64",
        ("Linux", "aarch64"): "linux_arm64",
        ("Linux", "arm64"): "linux_arm64",
    }
    try:
        return mapping[(system, machine)]
    except KeyError as exc:
        raise RuntimeError(f"unsupported exact-toolchain platform: {system}/{machine}") from exc


def exact_node() -> Path:
    reject_toolchain_overrides(os.environ)
    key = platform_key()
    cache = tool_cache_root()
    lock = load_json(TOOLCHAIN_LOCK_PATH)
    expected_archive_sha256 = lock.get("node", {}).get("archives", {}).get(key)
    if not isinstance(expected_archive_sha256, str):
        raise RuntimeError(f"Node archive lock is missing for {key}")
    archive_platform = {
        "darwin_amd64": "darwin-x64",
        "darwin_arm64": "darwin-arm64",
        "linux_amd64": "linux-x64",
        "linux_arm64": "linux-arm64",
    }[key]
    candidate = cache / "node/v24.18.0" / key / "bin/node"
    selected = require_installed_archive_member(
        selected_path=candidate,
        expected_selected_path=candidate,
        archive_path=(
            cache / "node" / f"node-v24.18.0-{archive_platform}.tar.gz"
        ),
        expected_archive_sha256=expected_archive_sha256,
        member_suffix="/bin/node",
        label="Node.js 24.18.0",
    )
    completed = subprocess.run(
        [str(selected), "--version"],
        env=evaluator_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 or completed.stdout.strip() != "v24.18.0":
        raise RuntimeError("pinned Node.js archive member is not version 24.18.0")
    return selected


def exact_java_bins() -> tuple[Path, Path]:
    reject_toolchain_overrides(os.environ)
    key = platform_key()
    cache = tool_cache_root()
    install = cache / "java/jdk-21.0.9+10" / key
    if platform.system() == "Darwin":
        install = install / "Contents/Home"
    lock = load_json(TOOLCHAIN_LOCK_PATH)
    archive_lock = lock.get("java", {}).get("archives", {}).get(key)
    if not isinstance(archive_lock, dict):
        raise RuntimeError(f"Java archive lock is missing for {key}")
    archive_name = archive_lock.get("name")
    expected_archive_sha256 = archive_lock.get("sha256")
    if not isinstance(archive_name, str) or not isinstance(
        expected_archive_sha256, str
    ):
        raise RuntimeError(f"Java archive lock is malformed for {key}")
    archive_path = cache / "java" / archive_name
    java = require_installed_archive_member(
        selected_path=install / "bin/java",
        expected_selected_path=install / "bin/java",
        archive_path=archive_path,
        expected_archive_sha256=expected_archive_sha256,
        member_suffix="/bin/java",
        label="Temurin Java 21.0.9+10",
    )
    javac = require_installed_archive_member(
        selected_path=install / "bin/javac",
        expected_selected_path=install / "bin/javac",
        archive_path=archive_path,
        expected_archive_sha256=expected_archive_sha256,
        member_suffix="/bin/javac",
        label="Temurin javac 21.0.9+10",
    )
    runtime = subprocess.run(
        [str(java), "-XshowSettings:properties", "-version"],
        env=evaluator_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    compiler = subprocess.run(
        [str(javac), "-version"],
        env=evaluator_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    if (
        runtime.returncode != 0
        or "java.runtime.version = 21.0.9+10-LTS" not in runtime.stderr
        or compiler.returncode != 0
        or compiler.stdout.strip() != "javac 21.0.9"
    ):
        raise RuntimeError("Java toolchain is not exact Temurin/Javac 21.0.9+10")
    return java, javac


def matching_host_profile_binding_errors(
    profile: dict[str, Any],
    selected: Mapping[str, Path],
    *,
    observed_host: tuple[str, str] | None = None,
) -> list[str]:
    role = str(profile.get("implementation_role", "unknown"))
    host = profile.get("host_observation", {})
    actual_host = (
        (platform.system(), platform.machine())
        if observed_host is None
        else observed_host
    )
    if (host.get("system"), host.get("machine")) != actual_host:
        return []
    errors: list[str] = []
    observations = profile.get("executable_observations", [])
    for observation in observations if isinstance(observations, list) else []:
        function = observation.get("function") if isinstance(observation, dict) else None
        executable = selected.get(function) if isinstance(function, str) else None
        if executable is None:
            errors.append(f"{role}_matching_host_selected_function_missing")
            continue
        try:
            binding = streamed_path_binding(executable.resolve(strict=True))
        except OSError:
            errors.append(f"{role}_matching_host_selected_executable_unreadable")
            continue
        if binding != (
            observation.get("raw_sha256"),
            observation.get("byte_count"),
        ):
            errors.append(f"{role}_matching_host_executable_binding_mismatch")
    return errors


def validate_selected_executable_profiles(
    python: Path,
    node: Path | None,
    java_bins: tuple[Path, Path] | None,
    errors: list[str],
) -> None:
    selected_by_role: dict[str, dict[str, Path]] = {
        "python": {"interpreter": python},
    }
    if node is not None:
        selected_by_role["node"] = {"runtime": node}
    if java_bins is not None:
        selected_by_role["java"] = {
            "runtime": java_bins[0],
            "compiler": java_bins[1],
        }
    for role, selected in selected_by_role.items():
        profile = load_json(RUNTIME_PROFILE_PATHS[role])
        errors.extend(matching_host_profile_binding_errors(profile, selected))


def expect_runtime_refusal(
    label: str,
    operation: Any,
    expected_fragment: str,
    errors: list[str],
) -> bool:
    try:
        operation()
    except RuntimeError as exc:
        if expected_fragment in str(exc):
            return True
        add_error(
            errors,
            "runtime_boundary_known_bad_wrong_reason",
            f"{label}: {exc}",
        )
        return False
    add_error(errors, "runtime_boundary_known_bad_not_refused", label)
    return False


def run_runtime_boundary_known_bads(errors: list[str]) -> int:
    passed = 0
    for name in TOOLCHAIN_OVERRIDE_NAMES:
        if expect_runtime_refusal(
            f"override-{name}",
            lambda name=name: reject_toolchain_overrides({name: "/tmp/wrapper"}),
            name,
            errors,
        ):
            passed += 1

    injected = {
        "NODE_OPTIONS": "--require=/tmp/injected.js",
        "JAVA_TOOL_OPTIONS": "-javaagent:/tmp/injected.jar",
        "JDK_JAVA_OPTIONS": "-javaagent:/tmp/injected.jar",
        "LD_PRELOAD": "/tmp/injected.so",
        "DYLD_INSERT_LIBRARIES": "/tmp/injected.dylib",
        "PATH": "/tmp/injected-bin",
    }
    closed = evaluator_environment(injected)
    forbidden_environment = set(injected) - {"PATH"}
    if (
        not forbidden_environment.intersection(closed)
        and closed.get("PATH") == os.defpath
    ):
        passed += 1
    else:
        add_error(errors, "runtime_boundary_injected_environment_survived")

    with tempfile.TemporaryDirectory(prefix="odeya-hda-toolchain-self-test-") as temporary:
        root = Path(temporary)
        archive_path = root / "safe.tar.gz"
        member_raw = b"pinned-executable-member\n"
        with tarfile.open(archive_path, mode="w:gz") as archive:
            info = tarfile.TarInfo("package/bin/node")
            info.size = len(member_raw)
            archive.addfile(info, io.BytesIO(member_raw))
        archive_sha = streamed_path_binding(archive_path)[0][7:]
        selected = root / "install/bin/node"
        selected.parent.mkdir(parents=True)
        selected.write_bytes(member_raw)
        safe = require_installed_archive_member(
            selected_path=selected,
            expected_selected_path=selected,
            archive_path=archive_path,
            expected_archive_sha256=archive_sha,
            member_suffix="/bin/node",
            label="self-test runtime",
        )
        if safe == selected.resolve():
            passed += 1
        else:
            add_error(errors, "runtime_boundary_archive_safe_control_failed")

        if expect_runtime_refusal(
            "wrong-archive-digest",
            lambda: archive_member_binding(
                archive_path, "0" * 64, "/bin/node", "self-test runtime"
            ),
            "archive digest is not locked",
            errors,
        ):
            passed += 1
        if expect_runtime_refusal(
            "missing-archive",
            lambda: archive_member_binding(
                root / "missing.tar.gz",
                archive_sha,
                "/bin/node",
                "self-test runtime",
            ),
            "archive is unavailable",
            errors,
        ):
            passed += 1

        selected.write_bytes(b"v24.18.0\n")
        if expect_runtime_refusal(
            "installed-member-mismatch",
            lambda: require_installed_archive_member(
                selected_path=selected,
                expected_selected_path=selected,
                archive_path=archive_path,
                expected_archive_sha256=archive_sha,
                member_suffix="/bin/node",
                label="self-test runtime",
            ),
            "bytes differ from the pinned archive member",
            errors,
        ):
            passed += 1

        duplicate_archive = root / "duplicate.tar.gz"
        with tarfile.open(duplicate_archive, mode="w:gz") as archive:
            for prefix in ("first", "second"):
                info = tarfile.TarInfo(f"{prefix}/bin/node")
                info.size = len(member_raw)
                archive.addfile(info, io.BytesIO(member_raw))
        duplicate_sha = streamed_path_binding(duplicate_archive)[0][7:]
        if expect_runtime_refusal(
            "duplicate-archive-member",
            lambda: archive_member_binding(
                duplicate_archive,
                duplicate_sha,
                "/bin/node",
                "self-test runtime",
            ),
            "must contain one exact",
            errors,
        ):
            passed += 1

    with tempfile.TemporaryDirectory(
        prefix="odeya-hda-profile-self-test-"
    ) as temporary:
        selected_python = Path(temporary) / "python"
        selected_python.write_bytes(b"synthetic-profile-executable\n")
        binding = streamed_path_binding(selected_python)
        profile = load_json(RUNTIME_PROFILE_PATHS["python"])
        profile["executable_observations"][0]["raw_sha256"] = binding[0]
        profile["executable_observations"][0]["byte_count"] = binding[1]
        observed_host = (
            profile["host_observation"]["system"],
            profile["host_observation"]["machine"],
        )
        safe_profile_errors = matching_host_profile_binding_errors(
            profile,
            {"interpreter": selected_python},
            observed_host=observed_host,
        )
        if safe_profile_errors:
            add_error(
                errors,
                "runtime_boundary_profile_safe_control_failed",
                repr(safe_profile_errors),
            )
        for field, replacement in (
            ("raw_sha256", "sha256:" + ("0" * 64)),
            ("byte_count", 1),
        ):
            candidate = copy.deepcopy(profile)
            candidate["executable_observations"][0][field] = replacement
            observed = matching_host_profile_binding_errors(
                candidate,
                {"interpreter": selected_python},
                observed_host=observed_host,
            )
            if "python_matching_host_executable_binding_mismatch" in observed:
                passed += 1
            else:
                add_error(
                    errors,
                    "runtime_boundary_profile_known_bad_not_refused",
                    field,
                )
    return passed


def validate_predecessor_migration_self_test(
    python: Path, errors: list[str]
) -> bool:
    completed = subprocess.run(
        [
            str(python),
            *PYTHON_ISOLATION_FLAGS,
            str(GENERATOR_PATH),
            "--self-test-predecessor-migration",
        ],
        cwd=ROOT,
        env=evaluator_environment(),
        capture_output=True,
        check=False,
    )
    expected = (
        b"exact predecessor migration replayed; same-length, zero-stale, "
        b"and multiple-stale controls refused\n"
    )
    if completed.returncode != 0 or completed.stdout != expected or completed.stderr:
        add_error(
            errors,
            "predecessor_migration_self_test_failed",
            (completed.stdout + completed.stderr).decode(
                "utf-8", errors="replace"
            ).strip(),
        )
        return False
    return True


def validate_python_bytecode_isolation(python: Path, errors: list[str]) -> None:
    """Prove that evaluator isolation cannot dirty its immutable source tree."""

    try:
        with tempfile.TemporaryDirectory(prefix="odeya-hda-python-isolation-") as temporary:
            root = Path(temporary)
            (root / "probe_module.py").write_text(
                "VALUE = 'bytecode-isolation-probe'\n",
                encoding="utf-8",
            )
            runner = root / "probe_runner.py"
            runner.write_text(
                "import probe_module\n"
                "assert probe_module.VALUE == 'bytecode-isolation-probe'\n",
                encoding="utf-8",
            )
            env = evaluator_environment()
            # -E deliberately ignores this variable. The safe command must
            # therefore carry -B as an interpreter-level invariant.
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            safe = subprocess.run(
                [str(python), *PYTHON_ISOLATION_FLAGS, str(runner)],
                cwd=root,
                env=env,
                capture_output=True,
                check=False,
            )
            if safe.returncode != 0 or safe.stderr:
                add_error(
                    errors,
                    "python_bytecode_isolation_control_failed",
                    safe.stderr.decode("utf-8", errors="replace").strip(),
                )
                return
            if any(root.rglob("*.pyc")):
                add_error(errors, "python_bytecode_isolation_wrote_bytecode")
                return

            known_bad = subprocess.run(
                [str(python), "-E", "-s", str(runner)],
                cwd=root,
                env=env,
                capture_output=True,
                check=False,
            )
            if known_bad.returncode != 0 or known_bad.stderr:
                add_error(
                    errors,
                    "python_bytecode_isolation_known_bad_failed_to_execute",
                    known_bad.stderr.decode("utf-8", errors="replace").strip(),
                )
                return
            if not any(root.rglob("*.pyc")):
                add_error(
                    errors,
                    "python_bytecode_isolation_environment_only_known_bad_was_accepted",
                )
    except OSError as exc:
        add_error(errors, "python_bytecode_isolation_self_test_failed", str(exc))


def parse_process_projection(completed: subprocess.CompletedProcess[bytes], label: str) -> dict[str, Any]:
    if completed.returncode != 0:
        raise RuntimeError(
            f"{label} exited {completed.returncode}: {completed.stderr.decode('utf-8', errors='replace').strip()}"
        )
    if completed.stderr:
        raise RuntimeError(
            f"{label} wrote unexpected stderr: {completed.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return loads_json_object(completed.stdout, label)


def run_python_vector(python: Path, vector_id: str) -> tuple[dict[str, Any], bytes]:
    command = [
        str(python),
        *PYTHON_ISOLATION_FLAGS,
        str(SUITE / "python/input_adapter.py"),
        "--vectors",
        str(VECTORS_PATH),
        "--ruleset",
        str(RULESET_PATH),
        "--resolver",
        str(RESOLVER_PATH),
        "--vector-id",
        vector_id,
    ]
    completed = subprocess.run(
        command, cwd=ROOT, env=evaluator_environment(), capture_output=True, check=False
    )
    return parse_process_projection(completed, f"python:{vector_id}"), completed.stdout


def run_node_vector(node: Path, vector_id: str) -> tuple[dict[str, Any], bytes]:
    command = [
        str(node),
        "--disable-proto=throw",
        str(SUITE / "node/src/cli.mjs"),
        "--vectors",
        str(VECTORS_PATH),
        "--ruleset",
        str(RULESET_PATH),
        "--resolver",
        str(RESOLVER_PATH),
        "--vector-id",
        vector_id,
    ]
    completed = subprocess.run(
        command, cwd=ROOT, env=evaluator_environment(), capture_output=True, check=False
    )
    return parse_process_projection(completed, f"node:{vector_id}"), completed.stdout


JAVA_SOURCES = [
    SUITE / "java/src/odeya/hda/java21/StrictJson.java",
    SUITE / "java/src/odeya/hda/java21/JsonPatch.java",
    SUITE / "java/src/odeya/hda/java21/InputAdapter.java",
    SUITE / "java/src/odeya/hda/java21/HumanDecisionAssuranceEvaluator.java",
]


def compile_java(javac: Path, classes: Path) -> None:
    command = [
        str(javac),
        "--release",
        "21",
        "-encoding",
        "UTF-8",
        "-Xlint:all",
        "-Werror",
        "-d",
        str(classes),
        *(str(path) for path in JAVA_SOURCES),
    ]
    completed = subprocess.run(
        command, cwd=ROOT, env=evaluator_environment(), capture_output=True, check=False
    )
    if completed.returncode != 0 or completed.stderr:
        raise RuntimeError(
            "exact Java compilation failed or emitted diagnostics: "
            + completed.stderr.decode("utf-8", errors="replace")
        )


def run_java_vector(java: Path, classes: Path, vector_id: str) -> tuple[dict[str, Any], bytes]:
    command = [
        str(java),
        "-cp",
        str(classes),
        "odeya.hda.java21.HumanDecisionAssuranceEvaluator",
        "--vectors",
        str(VECTORS_PATH),
        "--ruleset",
        str(RULESET_PATH),
        "--resolver",
        str(RESOLVER_PATH),
        "--vector-id",
        vector_id,
    ]
    completed = subprocess.run(
        command, cwd=ROOT, env=evaluator_environment(), capture_output=True, check=False
    )
    return parse_process_projection(completed, f"java:{vector_id}"), completed.stdout


def validate_case_answer(case: dict[str, Any], projection: dict[str, Any], errors: list[str], label: str) -> None:
    if projection.get("final_disposition") != case.get("expected_disposition"):
        add_error(errors, "evaluator_case_disposition_mismatch", label)
    if projection.get("reason_codes") != case.get("expected_reason_codes"):
        add_error(errors, "evaluator_case_reason_codes_mismatch", label)
    observed_errors = projection.get("reason_codes", []) if case.get("kind") == "adversarial" else []
    if observed_errors != case.get("expected_errors"):
        add_error(errors, "evaluator_case_refusal_errors_mismatch", label)
    if not set(case.get("intent_errors", [])).issubset(observed_errors):
        add_error(errors, "evaluator_case_intent_not_observed", label)


def run_recomputations(retained: Retained, recompute_all: bool, errors: list[str]) -> int:
    try:
        python = exact_python()
        node = exact_node() if recompute_all else None
        java_bins = exact_java_bins() if recompute_all else None
    except RuntimeError as exc:
        add_error(errors, "exact_recomputation_toolchain_unavailable", str(exc))
        return 0
    validate_selected_executable_profiles(python, node, java_bins, errors)
    validate_predecessor_migration_self_test(python, errors)
    validate_python_bytecode_isolation(python, errors)
    cases = retained.cases.get("cases", [])
    count = 0
    try:
        with tempfile.TemporaryDirectory(prefix="odeya-hda-java-") as temporary:
            classes = Path(temporary) / "classes"
            classes.mkdir()
            if recompute_all and java_bins is not None:
                compile_java(java_bins[1], classes)
            for case in cases:
                vector_id = case.get("vector_id")
                python_projection, python_raw = run_python_vector(python, vector_id)
                validate_raw_projection(python_projection, retained, f"python_recomputed_{vector_id}", errors)
                validate_case_answer(case, python_projection, errors, f"python:{vector_id}")
                count += 1
                if vector_id == "safe-complete-eligible":
                    if python_projection != retained.projections["python"]:
                        add_error(errors, "python_retained_projection_semantic_mismatch")
                    if python_raw != PROJECTION_PATHS["python"].read_bytes():
                        add_error(errors, "python_retained_projection_raw_bytes_mismatch")
                if not recompute_all:
                    continue
                assert node is not None and java_bins is not None
                node_projection, node_raw = run_node_vector(node, vector_id)
                java_projection, java_raw = run_java_vector(java_bins[0], classes, vector_id)
                validate_raw_projection(node_projection, retained, f"node_recomputed_{vector_id}", errors)
                validate_raw_projection(java_projection, retained, f"java_recomputed_{vector_id}", errors)
                validate_case_answer(case, node_projection, errors, f"node:{vector_id}")
                validate_case_answer(case, java_projection, errors, f"java:{vector_id}")
                if node_projection != python_projection:
                    add_error(errors, "node_python_full_projection_disagreement", vector_id)
                if java_projection != python_projection:
                    add_error(errors, "java_python_full_projection_disagreement", vector_id)
                if vector_id == "safe-complete-eligible":
                    if node_projection != retained.projections["node"]:
                        add_error(errors, "node_retained_projection_semantic_mismatch")
                    if java_projection != retained.projections["java"]:
                        add_error(errors, "java_retained_projection_semantic_mismatch")
                    if node_raw != PROJECTION_PATHS["node"].read_bytes():
                        add_error(errors, "node_retained_projection_raw_bytes_mismatch")
                    if java_raw != PROJECTION_PATHS["java"].read_bytes():
                        add_error(errors, "java_retained_projection_raw_bytes_mismatch")
                count += 2
    except (OSError, RuntimeError, TypeError) as exc:
        add_error(errors, "evaluator_recomputation_failed", str(exc))
    return count


def retained_pointer_root(retained: Retained, name: str) -> Any:
    allowed = {
        "backing",
        "cases",
        "comparison",
        "evidence",
        "generation_manifest",
        "input_manifest",
        "projections",
        "results",
        "seal",
        "source_manifests",
        "vectors",
    }
    if name not in allowed:
        raise ValueError(f"unknown retained mutation root: {name}")
    return getattr(retained, name)


def pointer_parts(pointer: Any) -> list[str]:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("mutation path must be an absolute JSON pointer")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def resolve_pointer(retained: Retained, pointer: str) -> Any:
    parts = pointer_parts(pointer)
    if not parts:
        raise ValueError("mutation may not target the Retained container")
    current = retained_pointer_root(retained, parts[0])
    for part in parts[1:]:
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise ValueError(f"pointer traverses a scalar at {part}")
    return current


def mutation_value(retained: Retained, mutation: Mapping[str, Any]) -> Any:
    if "special_value" in mutation:
        special = mutation["special_value"]
        if special == "seal_artifact_id":
            return retained.seal.get("artifact_id")
        if special == "seal_raw_sha256":
            return raw_sha256(SEAL_PATH.read_bytes())
        raise ValueError(f"unknown special mutation value: {special}")
    if mutation.get("op") == "copy":
        return copy.deepcopy(resolve_pointer(retained, str(mutation.get("from"))))
    if "value" not in mutation:
        raise ValueError("add/replace mutation lacks value")
    return copy.deepcopy(mutation["value"])


def apply_retained_mutation(retained: Retained, mutation: Mapping[str, Any]) -> None:
    operation = mutation.get("op")
    if operation not in {"add", "copy", "remove", "replace"}:
        raise ValueError(f"unsupported mutation operation: {operation}")
    parts = pointer_parts(mutation.get("path"))
    if len(parts) < 2:
        raise ValueError("mutation must target a member below a retained root")
    parent: Any = retained_pointer_root(retained, parts[0])
    for part in parts[1:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    final = parts[-1]
    if operation == "remove":
        if isinstance(parent, list):
            parent.pop(int(final))
        else:
            del parent[final]
        return
    value = mutation_value(retained, mutation)
    if isinstance(parent, list):
        if operation == "add" and final == "-":
            parent.append(value)
        elif operation == "add":
            parent.insert(int(final), value)
        else:
            parent[int(final)] = value
    else:
        if operation == "replace" and final not in parent:
            raise ValueError(f"replace target does not exist: {mutation.get('path')}")
        parent[final] = value


def materialize_chain_safe_control(
    retained: Retained, control: Mapping[str, Any]
) -> Retained:
    candidate = copy.deepcopy(retained)
    setup = control.get("setup")
    if not isinstance(setup, list):
        raise ValueError("safe control setup must be an array")
    for mutation in setup:
        if not isinstance(mutation, dict):
            raise ValueError("safe control setup mutation must be an object")
        apply_retained_mutation(candidate, mutation)
    derive = control.get("derive")
    if derive is not None:
        if derive != "backing_receipt_from_evidence":
            raise ValueError(f"unknown safe-control derivation: {derive}")
        derivation_errors: list[str] = []
        rows, relation, disposition, reasons = recompute_backing_from_evidence(
            candidate, derivation_errors
        )
        if derivation_errors:
            raise ValueError(
                "backing safe-control derivation failed: "
                + ",".join(sorted(error_codes(derivation_errors)))
            )
        candidate.backing["role_verifications"] = rows
        candidate.backing["expected_role_count"] = len(rows)
        candidate.backing["confirmation_receipt_frame_relation"] = relation
        candidate.backing["verification_disposition"] = disposition
        candidate.backing["reason_codes"] = reasons
    return candidate


def run_chain_checker(name: str, retained: Retained, errors: list[str]) -> None:
    if name == "expectation":
        validate_expectation_boundary(retained, errors)
    elif name == "evidence":
        validate_evidence(retained, errors)
    elif name == "backing":
        validate_backing(retained, errors)
    elif name == "python_projection":
        validate_raw_projection(
            retained.projections["python"], retained, "python_projection", errors
        )
    elif name == "python_result":
        validate_result("python", retained, errors)
    elif name == "independence":
        validate_source_independence(retained, errors)
    elif name == "comparison":
        validate_comparison(retained, errors)
    elif name == "seal":
        validate_seal(retained, errors)
    elif name == "acyclicity":
        validate_acyclicity(retained, errors)
    else:
        raise ValueError(f"unknown chain-case checker: {name}")


def run_known_bad_self_tests(retained: Retained, errors: list[str]) -> int:
    """Load and prove every declarative one-mutation downstream chain refusal."""
    corpus = retained.chain_cases
    expected_top = {
        "adr_0095_obligations",
        "case_id",
        "checker",
        "expected_errors",
        "intent_errors",
        "kind",
        "mutations",
        "safe_control",
    }
    if (
        corpus.get("artifact_class")
        != "human_decision_assurance_successor_downstream_chain_known_bad_cases"
        or corpus.get("decision_ref")
        != "docs/decisions/0095-reissue-human-decision-assurance-as-a-byte-bound-independently-recomputed-chain.md"
        or corpus.get("mutation_cardinality_per_case") != 1
    ):
        add_error(errors, "chain_case_corpus_identity_mismatch")
    catalog = corpus.get("obligation_catalog")
    controls = corpus.get("safe_controls")
    cases = corpus.get("cases")
    if not isinstance(catalog, dict) or not catalog:
        add_error(errors, "chain_case_obligation_catalog_invalid")
        catalog = {}
    if not isinstance(controls, dict) or not controls:
        add_error(errors, "chain_case_safe_controls_invalid")
        controls = {}
    if not isinstance(cases, list) or not cases:
        add_error(errors, "chain_case_inventory_invalid")
        return 0
    case_ids: list[str] = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != expected_top:
            add_error(errors, "chain_case_shape_mismatch")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            add_error(errors, "chain_case_id_invalid")
            continue
        case_ids.append(case_id)
        obligations = case.get("adr_0095_obligations")
        if (
            not sorted_unique_ascii(obligations)
            or not obligations
            or any(item not in catalog for item in obligations)
        ):
            add_error(errors, "chain_case_adr_obligation_invalid", case_id)
        if case.get("kind") != "known_bad":
            add_error(errors, "chain_case_kind_not_known_bad", case_id)
        expected = case.get("expected_errors")
        intent = case.get("intent_errors")
        if not sorted_unique_ascii(expected) or not expected:
            add_error(errors, "chain_case_expected_errors_invalid", case_id)
        if (
            not sorted_unique_ascii(intent)
            or not intent
            or not set(intent).issubset(expected if isinstance(expected, list) else [])
        ):
            add_error(errors, "chain_case_intent_errors_invalid", case_id)
        mutations = case.get("mutations")
        if not isinstance(mutations, list) or len(mutations) != 1:
            add_error(errors, "chain_case_mutation_cardinality_mismatch", case_id)
            continue
        control = controls.get(case.get("safe_control"))
        if not isinstance(control, dict):
            add_error(errors, "chain_case_safe_control_missing", case_id)
            continue
        try:
            safe = materialize_chain_safe_control(retained, control)
            safe_findings: list[str] = []
            run_chain_checker(str(case.get("checker")), safe, safe_findings)
            if safe_findings:
                add_error(
                    errors,
                    "chain_case_safe_control_failed",
                    f"{case_id}: {sorted(error_codes(safe_findings))}",
                )
                continue
            candidate = copy.deepcopy(safe)
            mutation = mutations[0]
            if not isinstance(mutation, dict):
                raise ValueError("known-bad mutation must be an object")
            apply_retained_mutation(candidate, mutation)
            found: list[str] = []
            run_chain_checker(str(case.get("checker")), candidate, found)
        except (IndexError, KeyError, OSError, TypeError, ValueError) as exc:
            add_error(errors, "chain_case_execution_failed", f"{case_id}: {exc}")
            continue
        observed = sorted(error_codes(found))
        if observed != expected:
            add_error(
                errors,
                "chain_case_expected_error_set_mismatch",
                f"{case_id}: expected {expected}; got {observed}",
            )
        if not set(intent).issubset(observed):
            add_error(
                errors,
                "chain_case_intended_guard_not_observed",
                f"{case_id}: intended {intent}; got {observed}",
            )
    if len(case_ids) != len(set(case_ids)):
        add_error(errors, "chain_case_id_duplicate")
    return len(cases)


def validate_all(
    retained: Retained, recompute_all: bool, errors: list[str]
) -> tuple[int, int, int]:
    validate_expectation_boundary(retained, errors)
    validate_ruleset_and_resolver(retained, errors)
    validate_evidence(retained, errors)
    validate_backing(retained, errors)
    for role in ROLE_KEYS:
        validate_result(role, retained, errors)
    validate_source_independence(retained, errors)
    validate_common_input_manifest(retained, errors)
    validate_comparison(retained, errors)
    validate_seal(retained, errors)
    validate_generation_manifest(retained, errors)
    validate_acyclicity(retained, errors)
    known_bads = run_known_bad_self_tests(retained, errors)
    runtime_known_bads = run_runtime_boundary_known_bads(errors)
    recomputations = run_recomputations(retained, recompute_all, errors)
    return known_bads, runtime_known_bads, recomputations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--recompute-all",
        action="store_true",
        help="require exact Node/Java toolchains and compare the complete retained three-way vector inventory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    retained = load_retained(errors)
    known_bads = 0
    runtime_known_bads = 0
    recomputations = 0
    if retained is not None:
        known_bads, runtime_known_bads, recomputations = validate_all(
            retained, args.recompute_all, errors
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"human-decision-assurance successor validation failed with {len(errors)} finding(s)",
            file=sys.stderr,
        )
        return 1
    mode = "Python/Node.js/Java" if args.recompute_all else "Python"
    print(
        "human-decision-assurance successor checked: "
        "5-schema byte-bound retained chain; 14 content-addressed preimages; "
        "3 source-separated result records; exact full-field comparison and Seal copy/precedence; "
        f"{known_bads} in-memory known-bad semantic mutations refused; "
        f"{runtime_known_bads} toolchain-boundary controls passed; "
        "exact predecessor migration self-test passed; "
        f"{recomputations} {mode} vector recomputations matched"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
