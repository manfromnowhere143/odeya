#!/usr/bin/env python3
"""Generate the byte-bound HDA 0.2 synthetic architecture evidence chain.

This generator is deliberately downstream of three source-separated evaluator
implementations.  It executes their exact CLIs, retains stdout bytes without
reserializing them, compares the complete semantic projections, and only then
constructs the wrapper results, comparison receipt, and Seal fixture.

The generated records are synthetic architecture fixtures.  They are not an
issued profile, a real human ceremony, approval, Gate A acceptance, runtime
authority, or external-effect authority.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import platform
import re
import struct
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "tests/human-decision-assurance-successor"
FIXTURES = ROOT / "tests/architecture-schema/fixtures"
VECTOR_PATH = SUITE / "vectors.json"
CASES_PATH = SUITE / "cases.json"
CHAIN_CASES_PATH = SUITE / "chain-cases.json"
VALIDATOR_PATH = ROOT / "scripts/validate_human_decision_assurance_successor.py"
RULESET_PATH = ROOT / "architecture/human-decision-assurance-individual-eligibility-ruleset-v2-candidate.json"
RESOLVER_PATH = ROOT / "architecture/human-decision-assurance-content-address-resolver-profile-v1-candidate.json"
TOOLCHAIN_LOCK_PATH = ROOT / "tools/repository-release/toolchain.lock.json"
ARCHITECTURE_REQUIREMENTS_SOURCE_PATH = ROOT / "requirements-architecture.txt"
ARCHITECTURE_REQUIREMENTS_LOCK_PATH = (
    ROOT / "tools/repository-release/requirements-architecture.lock"
)
CORE_PATH = FIXTURES / "human-decision-assurance-core.valid.json"
DECISION_PATH = FIXTURES / "human-decision-assurance-decision-subject.valid.json"
CANDIDATE_MANIFEST_PATH = ROOT / "tests/architecture-review/fixtures/architecture-candidate-manifest.valid.json"
CHALLENGE_PROFILE_PATH = ROOT / "architecture/human-decision-challenge-frame-v2-candidate.json"
CHALLENGE_EVIDENCE_PATH = (
    ROOT / "architecture/human-decision-challenge-frame-v2-candidate-evidence.json"
)

EVIDENCE_PATH = FIXTURES / "human-decision-assurance-evidence-v0-2.valid.json"
BACKING_RECEIPT_PATH = FIXTURES / "human-decision-assurance-backing-byte-verification-receipt.valid.json"
NORMATIVE_INPUT_PATH = SUITE / "normative-input-safe-complete-eligible.json"
INPUT_MANIFEST_PATH = SUITE / "input-manifest.json"
COMPARISON_PATH = FIXTURES / "human-decision-assurance-eligibility-comparison-receipt.valid.json"
SEAL_PATH = FIXTURES / "human-decision-assurance-seal-v0-2.valid.json"
GENERATION_MANIFEST_PATH = SUITE / "generation-manifest.json"

ASSURANCE_ID = "hda.synthetic.0001"
VECTOR_ID = "safe-complete-eligible"
RULESET_ID = "urn:odeya:human-decision-assurance-eligibility:0.2.0-candidate"
RULESET_VERSION = "0.2.0"
RESOLVER_ID = "urn:odeya:human-decision-assurance:content-address-resolver:0.1.0-candidate"
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
# Deterministic fixture timestamps make regeneration byte-for-byte replayable.
# They are not observations of a ceremony, runtime execution, or external event.
FIXED_TIMES = {
    "evidence": "2026-07-21T00:00:00.000000Z",
    "backing": "2026-07-21T00:01:00.000000Z",
    "recomputation": "2026-07-21T00:02:00.000000Z",
    "comparison": "2026-07-21T00:03:00.000000Z",
    "seal": "2026-07-21T00:04:00.000000Z",
}

SCHEMA_PATHS = {
    "evidence": ROOT / "schemas/human-decision-assurance-evidence-v0-2.schema.json",
    "backing": ROOT / "schemas/human-decision-assurance-backing-byte-verification-receipt.schema.json",
    "result": ROOT / "schemas/human-decision-assurance-eligibility-recomputation-result.schema.json",
    "comparison": ROOT / "schemas/human-decision-assurance-eligibility-comparison-receipt.schema.json",
    "seal": ROOT / "schemas/human-decision-assurance-seal-v0-2.schema.json",
}

RESULT_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-eligibility-recomputation-result:0.1.0"
EVIDENCE_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-evidence:0.2.0"
BACKING_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-backing-byte-verification-receipt:0.1.0"
COMPARISON_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-eligibility-comparison-receipt:0.1.0"

ROLE_ORDER = ("python", "nodejs_24_18_0", "java_21_0_9")
COMPLETE_PROJECTION_FIELDS = (
    "participant_id",
    "domain_results",
    "categorical_results",
    "categorical_failures",
    "final_disposition",
    "reason_codes",
)
RESULT_PATHS = {
    "python": FIXTURES / "human-decision-assurance-eligibility-recomputation-result-python.valid.json",
    "nodejs_24_18_0": FIXTURES / "human-decision-assurance-eligibility-recomputation-result-nodejs-24-18-0.valid.json",
    "java_21_0_9": FIXTURES / "human-decision-assurance-eligibility-recomputation-result-java-21-0-9.valid.json",
}
PROJECTION_PATHS = {
    "python": SUITE / "results/python.projection.json",
    "nodejs_24_18_0": SUITE / "results/nodejs-24-18-0.projection.json",
    "java_21_0_9": SUITE / "results/java-21-0-9.projection.json",
}
SOURCE_MANIFEST_PATHS = {
    "python": SUITE / "python/source-manifest.json",
    "nodejs_24_18_0": SUITE / "node/source-manifest.json",
    "java_21_0_9": SUITE / "java/source-manifest.json",
}
RUNTIME_PROFILE_PATHS = {
    "python": SUITE / "runtime/python-3-14-2.profile.json",
    "nodejs_24_18_0": SUITE / "runtime/nodejs-24-18-0.profile.json",
    "java_21_0_9": SUITE / "runtime/java-21-0-9.profile.json",
}

IMPLEMENTATION_FILES = {
    "python": {
        "sources": (
            SUITE / "python/evaluator.py",
            SUITE / "python/input_adapter.py",
        ),
        "adapter": SUITE / "python/input_adapter.py",
        "configuration": SUITE / "python/config.json",
        "dependency_lock": SUITE / "python/requirements.lock",
    },
    "nodejs_24_18_0": {
        "sources": (
            SUITE / "node/src/evaluator.mjs",
            SUITE / "node/src/input-adapter.mjs",
            SUITE / "node/src/cli.mjs",
        ),
        "adapter": SUITE / "node/src/input-adapter.mjs",
        "configuration": SUITE / "node/evaluator-config.json",
        "dependency_lock": SUITE / "node/package-lock.json",
    },
    "java_21_0_9": {
        "sources": (
            SUITE / "java/src/odeya/hda/java21/StrictJson.java",
            SUITE / "java/src/odeya/hda/java21/JsonPatch.java",
            SUITE / "java/src/odeya/hda/java21/InputAdapter.java",
            SUITE / "java/src/odeya/hda/java21/HumanDecisionAssuranceEvaluator.java",
        ),
        "adapter": SUITE / "java/src/odeya/hda/java21/InputAdapter.java",
        "configuration": SUITE / "java/evaluator-config.json",
        "dependency_lock": SUITE / "java/dependency-lock.json",
    },
}

IMPLEMENTATION_METADATA = {
    "python": {
        "toolchain_name": "python",
        "toolchain_version": "3.14.2",
        "source_manifest_id": "hda-evaluator-source-manifest.python.3_14_2.0001",
        "runtime_profile_id": "hda-runtime-profile.python.3_14_2.0001",
        "projection_id": "hda-eligibility-projection.python.synthetic.0002",
        "result_id": "hda-recomputation-result.python.synthetic.0002",
    },
    "nodejs_24_18_0": {
        "toolchain_name": "nodejs",
        "toolchain_version": "24.18.0",
        "source_manifest_id": "hda-evaluator-source-manifest.nodejs_24_18_0.0001",
        "runtime_profile_id": "hda-runtime-profile.nodejs_24_18_0.0001",
        "projection_id": "hda-eligibility-projection.nodejs_24_18_0.synthetic.0002",
        "result_id": "hda-recomputation-result.nodejs_24_18_0.synthetic.0002",
    },
    "java_21_0_9": {
        "toolchain_name": "java",
        "toolchain_version": "21.0.9",
        "source_manifest_id": "hda-evaluator-source-manifest.java_21_0_9.0001",
        "runtime_profile_id": "hda-runtime-profile.java_21_0_9.0001",
        "projection_id": "hda-eligibility-projection.java_21_0_9.synthetic.0002",
        "result_id": "hda-recomputation-result.java_21_0_9.synthetic.0002",
    },
}


class GenerationError(RuntimeError):
    """Raised when exact generation or retained evidence verification fails."""


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def digest_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def strict_json_bytes(raw: bytes, label: str) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise GenerationError(f"{label}: duplicate JSON member {key!r}")
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise GenerationError(f"{label}: non-finite JSON number {value}")

    try:
        text = raw.decode("utf-8", errors="strict")
        return json.loads(text, object_pairs_hook=unique, parse_constant=reject)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GenerationError(f"{label}: invalid strict UTF-8 JSON: {exc}") from exc


def load_json(path: Path) -> Any:
    return strict_json_bytes(path.read_bytes(), relative(path))


def write_bytes(path: Path, raw: bytes) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise GenerationError(f"refusing to write outside repository: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json_bytes(value))


def raw_binding(artifact_id: str, path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if not raw:
        raise GenerationError(f"cannot bind empty artifact: {relative(path)}")
    return {
        "artifact_id": artifact_id,
        "raw_sha256": digest_bytes(raw),
        "byte_count": len(raw),
        "mutable_alias_used": False,
    }


def digest_octets(value: Any, label: str) -> bytes:
    if (
        not isinstance(value, str)
        or re.fullmatch(r"sha256:[0-9a-f]{64}", value) is None
    ):
        raise GenerationError(f"{label}: expected one sha256-prefixed digest")
    try:
        return bytes.fromhex(value[7:])
    except ValueError as exc:
        raise GenerationError(f"{label}: digest is not lowercase hexadecimal") from exc


def encode_named_binary_frame(
    magic: Any, fields: list[tuple[str, bytes]], label: str
) -> bytes:
    if not isinstance(magic, str) or not magic.isascii():
        raise GenerationError(f"{label}: frame magic must be ASCII")
    encoded = bytearray(magic.encode("ascii"))
    encoded.extend(struct.pack(">H", len(fields)))
    for name, value in fields:
        if not name.isascii():
            raise GenerationError(f"{label}: field name must be ASCII")
        name_bytes = name.encode("ascii")
        encoded.extend(struct.pack(">H", len(name_bytes)))
        encoded.extend(name_bytes)
        encoded.extend(struct.pack(">I", len(value)))
        encoded.extend(value)
    return bytes(encoded)


def challenge_shared_fields(shared: dict[str, Any]) -> list[tuple[str, bytes]]:
    def text(key: str) -> bytes:
        value = shared.get(key)
        if not isinstance(value, str) or not value.isascii():
            raise GenerationError(f"challenge shared input {key} must be ASCII")
        return value.encode("ascii")

    return [
        ("core_schema_resource_id", text("core_schema_resource_id")),
        (
            "core_raw_sha256",
            digest_octets(shared.get("core_raw_sha256"), "core_raw_sha256"),
        ),
        ("decision_schema_resource_id", text("decision_schema_resource_id")),
        (
            "decision_raw_sha256",
            digest_octets(
                shared.get("decision_raw_sha256"), "decision_raw_sha256"
            ),
        ),
        ("candidate_schema_resource_id", text("candidate_schema_resource_id")),
        (
            "candidate_raw_sha256",
            digest_octets(
                shared.get("candidate_raw_sha256"), "candidate_raw_sha256"
            ),
        ),
        ("session_id", text("session_id")),
    ]


def challenge_interval_fields(
    shared: dict[str, Any], phase: dict[str, Any]
) -> list[tuple[str, bytes]]:
    fields: list[tuple[str, bytes]] = []
    for name in ("issued_at", "expires_at"):
        value = phase.get(name)
        if not isinstance(value, str) or not value.isascii():
            raise GenerationError(f"challenge phase {name} must be ASCII")
        fields.append((name, value.encode("ascii")))
    for name in ("relying_party_id", "expected_origin"):
        value = shared.get(name)
        if not isinstance(value, str) or not value.isascii():
            raise GenerationError(f"challenge shared input {name} must be ASCII")
        fields.append((name, value.encode("ascii")))
    nonce = phase.get("nonce_hex")
    try:
        nonce_bytes = bytes.fromhex(nonce) if isinstance(nonce, str) else b""
    except ValueError as exc:
        raise GenerationError("challenge phase nonce is not hexadecimal") from exc
    if len(nonce_bytes) != 32:
        raise GenerationError("challenge phase nonce is not exactly 32 octets")
    fields.append(("nonce", nonce_bytes))
    return fields


def exact_receipt_preimage(base_input: dict[str, Any]) -> bytes:
    artifacts = base_input.get("backing_byte_inputs", {}).get("artifacts", [])
    matches = [
        item
        for item in artifacts
        if isinstance(item, dict)
        and item.get("descriptor", {}).get("role")
        == "exact_unmodified_confirmation_receipt_frame"
    ]
    if len(matches) != 1:
        raise GenerationError(
            "expected exactly one confirmation-receipt frame preimage"
        )
    raw_base64 = matches[0].get("preimage", {}).get("raw_base64")
    if not isinstance(raw_base64, str):
        raise GenerationError("confirmation-receipt frame preimage is absent")
    try:
        return base64.b64decode(raw_base64, validate=True)
    except ValueError as exc:
        raise GenerationError(
            "confirmation-receipt frame preimage is not strict Base64"
        ) from exc


def recompute_phase_two_challenge_relation(
    base_input: dict[str, Any],
    *,
    vector_raw_sha256: str,
) -> dict[str, Any]:
    """Recompute the successor receipt's phase-two challenge from source bytes.

    The published predecessor copied the ADR 0093 authentication challenge ID
    after replacing the confirmation-receipt bytes.  That left every local
    checker green because the old validator compared only the copied receipt
    digest.  Generation now fails unless the retained relation equals a fresh
    construction from the exact challenge profile, exact upstream vector
    inputs, and exact successor receipt preimage.
    """

    profile = load_json(CHALLENGE_PROFILE_PATH)
    evidence = load_json(CHALLENGE_EVIDENCE_PATH)
    profile_binding = evidence.get("profile_binding")
    profile_raw = CHALLENGE_PROFILE_PATH.read_bytes()
    if profile_binding != {
        "path": relative(CHALLENGE_PROFILE_PATH),
        "profile_id": profile.get("profile_id"),
        "profile_version": profile.get("profile_version"),
        "raw_sha256": digest_bytes(profile_raw),
        "byte_count": len(profile_raw),
    }:
        raise GenerationError("challenge-frame evidence profile binding is stale")
    source_vector = evidence.get("synthetic_test_vector")
    if not isinstance(source_vector, dict):
        raise GenerationError("challenge-frame evidence has no synthetic vector")
    shared = source_vector.get("shared_inputs")
    presentation = source_vector.get("presentation_phase")
    authentication = source_vector.get("authentication_phase")
    if not all(isinstance(value, dict) for value in (shared, presentation, authentication)):
        raise GenerationError("challenge-frame source vector is incomplete")

    magic = profile.get("binary_frame", {}).get("magic_ascii")
    presentation_fields = challenge_shared_fields(shared) + challenge_interval_fields(
        shared, presentation
    )
    expected_presentation_order = profile.get("binary_frame", {}).get(
        "presentation_phase_ordered_fields"
    )
    if [name for name, _ in presentation_fields] != expected_presentation_order:
        raise GenerationError("presentation frame field order differs from profile")
    presentation_frame = encode_named_binary_frame(
        magic, presentation_fields, "presentation challenge"
    )
    presentation_nonce = presentation_fields[-1][1]
    presentation_octets = presentation_nonce + hashlib.sha256(
        presentation_frame
    ).digest()
    presentation_id = digest_bytes(presentation_octets)
    presentation_base64url = base64.urlsafe_b64encode(presentation_octets).decode(
        "ascii"
    ).rstrip("=")
    if (
        len(presentation_frame) != presentation.get("frame_byte_count")
        or digest_bytes(presentation_frame) != presentation.get("frame_raw_sha256")
        or presentation_base64url != presentation.get("challenge_base64url")
        or presentation_id != presentation.get("presentation_challenge_id")
    ):
        raise GenerationError(
            "upstream presentation challenge does not independently recompute"
        )

    receipt_raw = exact_receipt_preimage(base_input)
    receipt_digest = digest_bytes(receipt_raw)
    receipt_profile_id = profile.get("confirmation_receipt", {}).get(
        "receipt_profile_id"
    )
    if not isinstance(receipt_profile_id, str) or not receipt_profile_id.isascii():
        raise GenerationError("confirmation-receipt profile identity is invalid")
    appended = [
        (
            "presentation_challenge_id",
            digest_octets(presentation_id, "presentation_challenge_id"),
        ),
        (
            "confirmation_receipt_raw_sha256",
            digest_octets(receipt_digest, "confirmation_receipt_raw_sha256"),
        ),
        ("confirmation_receipt_profile_id", receipt_profile_id.encode("ascii")),
    ]
    authentication_fields = (
        challenge_shared_fields(shared)
        + challenge_interval_fields(shared, authentication)
        + appended
    )
    expected_authentication_order = profile.get("binary_frame", {}).get(
        "authentication_phase_ordered_fields"
    )
    if [name for name, _ in authentication_fields] != expected_authentication_order:
        raise GenerationError("authentication frame field order differs from profile")
    authentication_frame = encode_named_binary_frame(
        magic, authentication_fields, "authentication challenge"
    )
    authentication_nonce_hex = authentication.get("nonce_hex")
    if (
        not isinstance(authentication_nonce_hex, str)
        or re.fullmatch(r"[0-9a-f]{64}", authentication_nonce_hex) is None
    ):
        raise GenerationError("authentication nonce is not 32 lowercase octets")
    authentication_nonce = bytes.fromhex(authentication_nonce_hex)
    authentication_octets = authentication_nonce + hashlib.sha256(
        authentication_frame
    ).digest()
    authentication_id = digest_bytes(authentication_octets)

    relation = base_input.get("backing_byte_inputs", {}).get(
        "confirmation_receipt_frame_relation"
    )
    expected_relation = {
        "frame_role": "exact_unmodified_confirmation_receipt_frame",
        "expected_frame_content_address": receipt_digest,
        "observed_frame_raw_sha256": receipt_digest,
        "presentation_challenge_id": presentation_id,
        "authentication_challenge_id": authentication_id,
        "authentication_frame_committed_receipt_sha256": receipt_digest,
        "binary_framing_disposition": "supported",
        "presentation_to_receipt_relation_disposition": "supported",
        "receipt_to_authentication_relation_disposition": "supported",
    }
    if relation != expected_relation:
        stale_predecessor_relation = copy.deepcopy(expected_relation)
        stale_predecessor_relation["authentication_challenge_id"] = (
            PREDECESSOR_SUBJECT["stale_authentication_challenge_id"]
        )
        if (
            relation != stale_predecessor_relation
            or vector_raw_sha256
            != PREDECESSOR_SUBJECT["vector_corpus_raw_sha256"]
        ):
            raise GenerationError(
                "confirmation-receipt relation is not the exact independently "
                "recomputed phase-two relation or the one exact retained "
                "predecessor defect"
            )
        relation.clear()
        relation.update(copy.deepcopy(expected_relation))

    return {
        "challenge_profile_binding": raw_binding(
            "hda-challenge-frame-profile.v2.0001", CHALLENGE_PROFILE_PATH
        ),
        "challenge_vector_evidence_binding": raw_binding(
            "hda-challenge-frame-v2-evidence.0001", CHALLENGE_EVIDENCE_PATH
        ),
        "presentation_frame_raw_sha256": digest_bytes(presentation_frame),
        "presentation_challenge_id": presentation_id,
        "confirmation_receipt_raw_sha256": receipt_digest,
        "authentication_frame_byte_count": len(authentication_frame),
        "authentication_frame_raw_sha256": digest_bytes(authentication_frame),
        "authentication_challenge_base64url": base64.urlsafe_b64encode(
            authentication_octets
        )
        .decode("ascii")
        .rstrip("="),
        "authentication_challenge_id": authentication_id,
        "retained_relation_exact_match": True,
    }


def schema_binding(artifact_id: str, schema_resource_id: str, path: Path) -> dict[str, Any]:
    return {
        **raw_binding(artifact_id, path),
        "schema_resource_id": schema_resource_id,
    }


def ruleset_binding() -> dict[str, Any]:
    raw = RULESET_PATH.read_bytes()
    return {
        "ruleset_id": RULESET_ID,
        "ruleset_version": RULESET_VERSION,
        "raw_sha256": digest_bytes(raw),
        "byte_count": len(raw),
        "mutable_alias_used": False,
    }


def manifest_entry(artifact_id: str, path: Path, kind: str) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "artifact_id": artifact_id,
        "artifact_kind": kind,
        "repository_path": relative(path),
        "raw_sha256": digest_bytes(raw),
        "byte_count": len(raw),
    }


def run(command: list[str], *, environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    process = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        rendered = " ".join(command)
        stderr = process.stderr.decode("utf-8", errors="replace")
        raise GenerationError(f"command failed ({process.returncode}): {rendered}\n{stderr}")
    return process


def closed_environment() -> dict[str, str]:
    environment = {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": os.defpath,
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }
    for name in ("SYSTEMROOT", "TMPDIR"):
        if name in os.environ:
            environment[name] = os.environ[name]
    return environment


def platform_key() -> str:
    mapping = {
        ("Darwin", "x86_64"): "darwin_amd64",
        ("Darwin", "arm64"): "darwin_arm64",
        ("Linux", "x86_64"): "linux_amd64",
        ("Linux", "aarch64"): "linux_arm64",
        ("Linux", "arm64"): "linux_arm64",
    }
    observed = (platform.system(), platform.machine())
    try:
        return mapping[observed]
    except KeyError as exc:
        raise GenerationError(
            f"unsupported exact-toolchain platform: {observed[0]}/{observed[1]}"
        ) from exc


def tool_cache_root() -> Path:
    configured = os.environ.get("ODEYA_TOOL_CACHE")
    return Path(
        configured
        if configured is not None
        else Path(tempfile.gettempdir()) / "odeya-release-tools"
    ).resolve()


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


def path_digest_and_count(path: Path) -> tuple[str, int]:
    with path.open("rb") as stream:
        return stream_digest_and_count(stream)


def attest_archive_member(
    *,
    selected_path: Path,
    expected_selected_path: Path,
    archive_path: Path,
    expected_archive_sha256: str,
    member_suffix: str,
    label: str,
) -> None:
    try:
        selected = selected_path.resolve(strict=True)
        expected_selected = expected_selected_path.resolve(strict=True)
    except OSError as exc:
        raise GenerationError(f"{label} selected executable is unavailable: {exc}") from exc
    if selected != expected_selected:
        raise GenerationError(
            f"{label} must be the canonical installer-cache executable"
        )
    if archive_path.is_symlink() or not archive_path.is_file():
        raise GenerationError(f"{label} pinned installer archive is unavailable")
    archive_digest, _ = path_digest_and_count(archive_path)
    if archive_digest != "sha256:" + expected_archive_sha256:
        raise GenerationError(f"{label} installer archive digest is not locked")
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            members = [
                member
                for member in archive.getmembers()
                if member.isfile() and member.name.endswith(member_suffix)
            ]
            if len(members) != 1:
                raise GenerationError(
                    f"{label} archive must contain one exact {member_suffix} member"
                )
            stream = archive.extractfile(members[0])
            if stream is None:
                raise GenerationError(f"{label} archive member is unreadable")
            with stream:
                archive_member = stream_digest_and_count(stream)
    except (OSError, tarfile.TarError) as exc:
        raise GenerationError(f"{label} installer archive is unreadable: {exc}") from exc
    if path_digest_and_count(selected) != archive_member:
        raise GenerationError(
            f"{label} selected executable bytes differ from the pinned archive member"
        )


def attest_generation_toolchains(
    python_executable: Path, node_executable: Path, java_bin: Path
) -> None:
    try:
        selected_python = python_executable.resolve(strict=True)
        generator_python = Path(sys.executable).resolve(strict=True)
    except OSError as exc:
        raise GenerationError(f"Python generator interpreter is unavailable: {exc}") from exc
    if selected_python != generator_python:
        raise GenerationError(
            "the Python evaluator must be the exact generator interpreter"
        )
    python_probe = run(
        [str(selected_python), "--version"], environment=closed_environment()
    )
    if python_probe.stdout + python_probe.stderr != b"Python 3.14.2\n":
        raise GenerationError("the generator interpreter is not Python 3.14.2")

    lock = load_json(TOOLCHAIN_LOCK_PATH)
    key = platform_key()
    cache = tool_cache_root()
    node_platform = {
        "darwin_amd64": "darwin-x64",
        "darwin_arm64": "darwin-arm64",
        "linux_amd64": "linux-x64",
        "linux_arm64": "linux-arm64",
    }[key]
    node_archive_name = f"node-v24.18.0-{node_platform}.tar.gz"
    node_archive_sha = lock.get("node", {}).get("archives", {}).get(key)
    if not isinstance(node_archive_sha, str):
        raise GenerationError(f"Node archive lock is missing for {key}")
    expected_node = cache / "node/v24.18.0" / key / "bin/node"
    attest_archive_member(
        selected_path=node_executable,
        expected_selected_path=expected_node,
        archive_path=cache / "node" / node_archive_name,
        expected_archive_sha256=node_archive_sha,
        member_suffix="/bin/node",
        label="Node.js 24.18.0",
    )

    java_lock = lock.get("java", {}).get("archives", {}).get(key)
    if not isinstance(java_lock, dict):
        raise GenerationError(f"Java archive lock is missing for {key}")
    java_archive_name = java_lock.get("name")
    java_archive_sha = java_lock.get("sha256")
    if not isinstance(java_archive_name, str) or not isinstance(
        java_archive_sha, str
    ):
        raise GenerationError(f"Java archive lock is malformed for {key}")
    java_home = cache / "java/jdk-21.0.9+10" / key
    if platform.system() == "Darwin":
        java_home = java_home / "Contents/Home"
    expected_java_bin = java_home / "bin"
    try:
        selected_java_bin = java_bin.resolve(strict=True)
        canonical_java_bin = expected_java_bin.resolve(strict=True)
    except OSError as exc:
        raise GenerationError(f"Java bin directory is unavailable: {exc}") from exc
    if selected_java_bin != canonical_java_bin:
        raise GenerationError("Java must use the canonical installer-cache bin directory")
    java_archive_path = cache / "java" / java_archive_name
    for executable_name in ("java", "javac"):
        attest_archive_member(
            selected_path=selected_java_bin / executable_name,
            expected_selected_path=expected_java_bin / executable_name,
            archive_path=java_archive_path,
            expected_archive_sha256=java_archive_sha,
            member_suffix=f"/bin/{executable_name}",
            label=f"Temurin {executable_name} 21.0.9+10",
        )


def create_source_manifests() -> dict[str, dict[str, Any]]:
    configs: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        paths = IMPLEMENTATION_FILES[role]
        config = load_json(paths["configuration"])
        configs[role] = config
        source_rows = []
        for index, path in enumerate(paths["sources"]):
            raw = path.read_bytes()
            source_rows.append(
                {
                    "sequence_index": index,
                    "repository_path": relative(path),
                    "raw_sha256": digest_bytes(raw),
                    "byte_count": len(raw),
                }
            )
        manifest = {
            "schema_version": "0.1.0",
            "artifact_class": "human_decision_assurance_evaluator_source_manifest",
            "artifact_id": IMPLEMENTATION_METADATA[role]["source_manifest_id"],
            "implementation_role": role,
            "implementation_id": config["implementation_id"],
            "source_files": source_rows,
            "source_file_count": len(source_rows),
            "shared_source_files_with_peer_implementations": [],
            "generated_source_consumed": False,
            "expected_result_fixture_consumed": False,
            "peer_implementation_source_consumed": False,
            "manifest_self_digest_forbidden": True,
        }
        write_json(SOURCE_MANIFEST_PATHS[role], manifest)
    digests = [digest_bytes(path.read_bytes()) for path in SOURCE_MANIFEST_PATHS.values()]
    if len(set(digests)) != len(digests):
        raise GenerationError("evaluator source-manifest digests are not pairwise distinct")
    return configs


def executable_observation(path: Path, function: str) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    raw = resolved.read_bytes()
    return {
        "function": function,
        "invocation_path": str(path),
        "resolved_path": str(resolved),
        "raw_sha256": digest_bytes(raw),
        "byte_count": len(raw),
    }


def create_runtime_profiles(python_executable: Path, node_executable: Path, java_bin: Path) -> None:
    environment = closed_environment()
    probes: dict[str, list[tuple[str, Path, subprocess.CompletedProcess[bytes], str]]] = {}

    python_probe = run([str(python_executable), "--version"], environment=environment)
    python_raw = python_probe.stdout if python_probe.stdout else python_probe.stderr
    if python_raw != b"Python 3.14.2\n":
        raise GenerationError(f"unexpected Python version probe: {python_raw!r}")
    python_probe_path = SUITE / "runtime/python-3-14-2.version.txt"
    write_bytes(python_probe_path, python_raw)
    probes["python"] = [("interpreter", python_executable, python_probe, relative(python_probe_path))]

    node_probe = run([str(node_executable), "--version"], environment=environment)
    if node_probe.stdout != b"v24.18.0\n" or node_probe.stderr:
        raise GenerationError(f"unexpected Node.js version probe: {node_probe.stdout!r} {node_probe.stderr!r}")
    node_probe_path = SUITE / "runtime/nodejs-24-18-0.version.txt"
    write_bytes(node_probe_path, node_probe.stdout)
    probes["nodejs_24_18_0"] = [("runtime", node_executable, node_probe, relative(node_probe_path))]

    java_executable = java_bin / "java"
    javac_executable = java_bin / "javac"
    java_probe = run([str(java_executable), "-version"], environment=environment)
    java_raw = java_probe.stdout + java_probe.stderr
    if b'openjdk version "21.0.9"' not in java_raw or b"Temurin-21.0.9+10" not in java_raw:
        raise GenerationError(f"unexpected Java version probe: {java_raw!r}")
    java_probe_path = SUITE / "runtime/java-21-0-9.version.txt"
    write_bytes(java_probe_path, java_raw)
    javac_probe = run([str(javac_executable), "-version"], environment=environment)
    javac_raw = javac_probe.stdout + javac_probe.stderr
    if javac_raw != b"javac 21.0.9\n":
        raise GenerationError(f"unexpected javac version probe: {javac_raw!r}")
    javac_probe_path = SUITE / "runtime/javac-21-0-9.version.txt"
    write_bytes(javac_probe_path, javac_raw)
    probes["java_21_0_9"] = [
        ("runtime", java_executable, java_probe, relative(java_probe_path)),
        ("compiler", javac_executable, javac_probe, relative(javac_probe_path)),
    ]

    toolchain_lock = manifest_entry("repository-release-toolchain-lock.0001", TOOLCHAIN_LOCK_PATH, "toolchain_lock")
    for role in ROLE_ORDER:
        observations = []
        for function, executable, process, probe_path in probes[role]:
            probe_file = ROOT / probe_path
            observations.append(
                {
                    **executable_observation(executable, function),
                    "version_probe": {
                        "repository_path": probe_path,
                        "raw_sha256": digest_bytes(probe_file.read_bytes()),
                        "byte_count": len(probe_file.read_bytes()),
                        "exit_code": process.returncode,
                    },
                }
            )
        profile = {
            "schema_version": "0.1.0",
            "artifact_class": "human_decision_assurance_exact_runtime_profile",
            "artifact_id": IMPLEMENTATION_METADATA[role]["runtime_profile_id"],
            "implementation_role": role,
            "toolchain_name": IMPLEMENTATION_METADATA[role]["toolchain_name"],
            "toolchain_version": IMPLEMENTATION_METADATA[role]["toolchain_version"],
            "host_observation": {
                "system": platform.system(),
                "machine": platform.machine(),
            },
            "repository_toolchain_lock": toolchain_lock,
            "executable_observations": observations,
            "network_access": False,
            "mutable_toolchain_alias_used": False,
            "profile_self_digest_forbidden": True,
        }
        write_json(RUNTIME_PROFILE_PATHS[role], profile)


def create_backing_blobs(base_input: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = base_input["backing_byte_inputs"]["artifacts"]
    generated: list[dict[str, Any]] = []
    for artifact in artifacts:
        descriptor = artifact["descriptor"]
        preimage = artifact["preimage"]
        if descriptor["repository_blob_path"] != preimage["repository_blob_path"]:
            raise GenerationError(f"descriptor/preimage path mismatch for {descriptor['artifact_id']}")
        try:
            raw = base64.b64decode(preimage["raw_base64"], validate=True)
        except ValueError as exc:
            raise GenerationError(f"invalid Base64 preimage for {descriptor['artifact_id']}") from exc
        if base64.b64encode(raw).decode("ascii") != preimage["raw_base64"]:
            raise GenerationError(f"non-canonical Base64 preimage for {descriptor['artifact_id']}")
        if digest_bytes(raw) != descriptor["content_address"]:
            raise GenerationError(f"preimage digest mismatch for {descriptor['artifact_id']}")
        if len(raw) != descriptor["byte_count"]:
            raise GenerationError(f"preimage byte count mismatch for {descriptor['artifact_id']}")
        path = ROOT / descriptor["repository_blob_path"]
        write_bytes(path, raw)
        generated.append(manifest_entry(descriptor["artifact_id"], path, "content_addressed_backing_preimage"))
    if len(generated) != 14:
        raise GenerationError(f"expected 14 backing blobs, generated {len(generated)}")
    return generated


def create_evidence(base_input: dict[str, Any]) -> dict[str, Any]:
    core = load_json(CORE_PATH)
    decision = load_json(DECISION_PATH)
    candidate_manifest = load_json(CANDIDATE_MANIFEST_PATH)
    challenge_profile = load_json(CHALLENGE_PROFILE_PATH)
    descriptors = [copy.deepcopy(item["descriptor"]) for item in base_input["backing_byte_inputs"]["artifacts"]]
    evidence = {
        "schema_version": "0.2.0",
        "artifact_class": "human_decision_assurance_evidence_candidate",
        "artifact_id": "hda-evidence.synthetic.0002",
        "assurance_id": ASSURANCE_ID,
        "version": 2,
        "candidate_status": "unissued_architecture_candidate_not_human_authority",
        "evidence_class": "synthetic_architecture_fixture",
        "assurance_scope": {
            "principal_act_cardinality": "exactly_one",
            "aggregate_quorum_evaluation": "deferred_to_assured_decision_wrapper",
            "currentness_evaluation": "deferred_to_assured_decision_wrapper",
            "authority_evaluation": "deferred_to_assured_decision_wrapper",
            "assured_decision_wrapper_identity_assigned": False,
        },
        "core_binding": schema_binding(core["artifact_id"], "urn:odeya:schema:human-decision-assurance-core:0.1.0", CORE_PATH),
        "decision_subject_binding": schema_binding(
            decision["decision_id"], "urn:odeya:schema:operator-architecture-decision:0.4.0", DECISION_PATH
        ),
        "candidate_manifest_binding": schema_binding(
            candidate_manifest["manifest_id"], "urn:odeya:schema:architecture-candidate-manifest:0.5.0", CANDIDATE_MANIFEST_PATH
        ),
        "challenge_profile_binding": {
            "profile_id": challenge_profile["profile_id"],
            "profile_version": challenge_profile["profile_version"],
            "raw_sha256": digest_bytes(CHALLENGE_PROFILE_PATH.read_bytes()),
            "byte_count": len(CHALLENGE_PROFILE_PATH.read_bytes()),
            "mutable_alias_used": False,
        },
        "participant_observations": [copy.deepcopy(base_input["participant_input"])],
        "ordered_artifact_ids": [item["artifact_id"] for item in descriptors],
        "ordered_artifact_inventory": descriptors,
        "forbidden_content_and_sanitation": copy.deepcopy(base_input["forbidden_content_and_sanitation"]),
        "proof_boundary": {
            "evidence_self_digest_forbidden": True,
            "profile_issued": False,
            "real_human_ceremony_verified": False,
            "signature_alone_proves_human_control": False,
            "user_presence_proves_review": False,
            "user_verification_proves_natural_person_identity": False,
            "ceremony_proves_cognition": False,
            "assignment_effective_control_mechanically_established": False,
            "original_decision_authorship_proven": False,
            "source_decided_at_proven": False,
            "aggregate_quorum_evaluated": False,
            "consumer_currentness_evaluated": False,
            "evidence_grants_authority": False,
            "gate_a_accepted": False,
            "runtime_authorized": False,
            "external_effects_authorized": False,
        },
        "collected_at": FIXED_TIMES["evidence"],
    }
    write_json(EVIDENCE_PATH, evidence)
    return evidence


def create_backing_receipt(base_input: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    resolver = load_json(RESOLVER_PATH)
    rows = [copy.deepcopy(item["verification_row"]) for item in base_input["backing_byte_inputs"]["artifacts"]]
    receipt = {
        "schema_version": "0.1.0",
        "artifact_class": "human_decision_assurance_backing_byte_verification_receipt_candidate",
        "artifact_id": BACKING_RECEIPT_ARTIFACT_ID,
        "assurance_id": ASSURANCE_ID,
        "version": 1,
        "candidate_status": "unissued_architecture_candidate_not_human_authority",
        "evidence_binding": schema_binding(evidence["artifact_id"], EVIDENCE_SCHEMA_ID, EVIDENCE_PATH),
        "resolver_profile_binding": {
            "profile_id": resolver["profile_id"],
            "profile_version": resolver["profile_version"],
            "raw_sha256": digest_bytes(RESOLVER_PATH.read_bytes()),
            "byte_count": len(RESOLVER_PATH.read_bytes()),
            "content_address_is_object_identity": True,
            "mutable_alias_used": False,
        },
        "expected_role_count": 14,
        "role_verifications": rows,
        "confirmation_receipt_frame_relation": copy.deepcopy(
            base_input["backing_byte_inputs"]["confirmation_receipt_frame_relation"]
        ),
        "verification_disposition": "supported",
        "reason_codes": ["supported.all_backing_bytes_verified"],
        "proof_boundary": {
            "receipt_self_digest_forbidden": True,
            "receipt_names_or_predicts_seal_identity": False,
            "profile_issued": False,
            "bytes_verified_by_filename_or_descriptor_only": False,
            "missing_bytes_represented_as_zero": False,
            "receipt_grants_authority": False,
            "gate_a_accepted": False,
            "runtime_authorized": False,
            "external_effects_authorized": False,
        },
        "verified_at": FIXED_TIMES["backing"],
    }
    write_json(BACKING_RECEIPT_PATH, receipt)
    return receipt


def create_normative_input_and_manifest(base_input: dict[str, Any], evidence: dict[str, Any], receipt: dict[str, Any]) -> None:
    write_json(NORMATIVE_INPUT_PATH, base_input)
    manifest = {
        "schema_version": "0.1.0",
        "artifact_class": "human_decision_assurance_successor_expectation_free_safe_input_manifest",
        "artifact_id": INPUT_MANIFEST_ARTIFACT_ID,
        "assurance_id": ASSURANCE_ID,
        "candidate_status": "synthetic_architecture_inputs_not_ceremony_evidence",
        "vector_id": VECTOR_ID,
        "upstream_bindings": {
            "evidence": schema_binding(evidence["artifact_id"], EVIDENCE_SCHEMA_ID, EVIDENCE_PATH),
            "backing_byte_verification_receipt": schema_binding(
                receipt["artifact_id"], BACKING_SCHEMA_ID, BACKING_RECEIPT_PATH
            ),
        },
        "process_read_set": {
            "expectation_free_vector_corpus": raw_binding(
                VECTOR_CORPUS_ARTIFACT_ID, VECTOR_PATH
            ),
            "eligibility_ruleset": ruleset_binding(),
            "content_address_resolver_profile": raw_binding("hda-content-address-resolver-profile.0001", RESOLVER_PATH),
        },
        "materialized_normative_input": raw_binding(
            NORMATIVE_INPUT_ARTIFACT_ID, NORMATIVE_INPUT_PATH
        ),
        "materialization_contract": {
            "base_input_source": "vectors.json#base_input",
            "selected_vector_id": VECTOR_ID,
            "selected_vector_mutation_count": 0,
            "materialized_input_equals_base_input": True,
        },
        "non_process_wrapper_context": [
            "evidence",
            "backing_byte_verification_receipt",
            "input_manifest",
            "materialized_normative_input",
        ],
        "forbidden_evaluator_inputs": [
            "cases.json",
            "expected outputs",
            "peer implementation source",
            "peer implementation output",
            "comparison receipt",
            "Seal",
        ],
        "expected_answer_values_present": False,
        "peer_output_values_present": False,
        "manifest_self_digest_forbidden": True,
    }
    write_json(INPUT_MANIFEST_PATH, manifest)


def evaluator_commands(
    python_executable: Path, node_executable: Path, java_bin: Path, java_classes: Path
) -> dict[str, list[str]]:
    common = [
        "--vectors",
        str(VECTOR_PATH),
        "--ruleset",
        str(RULESET_PATH),
        "--resolver",
        str(RESOLVER_PATH),
        "--vector-id",
        VECTOR_ID,
    ]
    return {
        "python": [str(python_executable), str(SUITE / "python/input_adapter.py"), *common],
        "nodejs_24_18_0": [
            str(node_executable),
            "--disable-proto=throw",
            str(SUITE / "node/src/cli.mjs"),
            *common,
        ],
        "java_21_0_9": [
            str(java_bin / "java"),
            "-cp",
            str(java_classes),
            "odeya.hda.java21.HumanDecisionAssuranceEvaluator",
            *common,
        ],
    }


def compile_java(java_bin: Path, output: Path) -> None:
    command = [
        str(java_bin / "javac"),
        "--release",
        "21",
        "-encoding",
        "UTF-8",
        "-Xlint:all",
        "-Werror",
        "-d",
        str(output),
        *(str(path) for path in IMPLEMENTATION_FILES["java_21_0_9"]["sources"]),
    ]
    process = run(command, environment=closed_environment())
    if process.stdout or process.stderr:
        raise GenerationError(f"javac emitted unexpected output: {process.stdout!r} {process.stderr!r}")


def execute_evaluators(
    python_executable: Path, node_executable: Path, java_bin: Path
) -> dict[str, dict[str, Any]]:
    outputs: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="odeya-hda-java-classes-") as temp_name:
        java_classes = Path(temp_name)
        compile_java(java_bin, java_classes)
        commands = evaluator_commands(python_executable, node_executable, java_bin, java_classes)
        for role in ROLE_ORDER:
            environment = closed_environment()
            if role == "python":
                environment["PYTHONPATH"] = str(SUITE / "python")
            process = run(commands[role], environment=environment)
            if process.stderr:
                raise GenerationError(f"{role} evaluator emitted stderr: {process.stderr!r}")
            if not process.stdout.endswith(b"\n"):
                raise GenerationError(f"{role} evaluator stdout lacks a trailing LF")
            projection = strict_json_bytes(process.stdout, f"{role} direct projection")
            if not isinstance(projection, dict):
                raise GenerationError(f"{role} evaluator projection is not an object")
            write_bytes(PROJECTION_PATHS[role], process.stdout)
            outputs[role] = projection
    baseline = outputs[ROLE_ORDER[0]]
    for role in ROLE_ORDER[1:]:
        if outputs[role] != baseline:
            raise GenerationError(f"complete safe-vector projection disagreement: python versus {role}")
    return outputs


def projection_for_comparison(result_projection: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in COMPLETE_PROJECTION_FIELDS if field not in result_projection]
    if missing:
        raise GenerationError(f"complete evaluator projection is missing fields: {missing}")
    return {field: copy.deepcopy(result_projection[field]) for field in COMPLETE_PROJECTION_FIELDS}


def common_input_bindings(evidence: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence": schema_binding(evidence["artifact_id"], EVIDENCE_SCHEMA_ID, EVIDENCE_PATH),
        "backing_byte_verification_receipt": schema_binding(
            receipt["artifact_id"], BACKING_SCHEMA_ID, BACKING_RECEIPT_PATH
        ),
        "eligibility_ruleset": ruleset_binding(),
        "input_manifest": raw_binding(
            INPUT_MANIFEST_ARTIFACT_ID, INPUT_MANIFEST_PATH
        ),
        "normative_input_vector": raw_binding(
            NORMATIVE_INPUT_ARTIFACT_ID, NORMATIVE_INPUT_PATH
        ),
    }


def create_results(
    configs: dict[str, dict[str, Any]],
    projections: dict[str, dict[str, Any]],
    evidence: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    inputs = common_input_bindings(evidence, receipt)
    for role in ROLE_ORDER:
        files = IMPLEMENTATION_FILES[role]
        metadata = IMPLEMENTATION_METADATA[role]
        configuration = configs[role]
        projection = projections[role]
        result = {
            "schema_version": "0.1.0",
            "artifact_class": "human_decision_assurance_eligibility_recomputation_result_candidate",
            "artifact_id": metadata["result_id"],
            "assurance_id": ASSURANCE_ID,
            "version": 1,
            "candidate_status": "unissued_architecture_candidate_not_human_authority",
            "implementation": {
                "implementation_role": role,
                "implementation_id": configuration["implementation_id"],
                "source_binding": raw_binding(metadata["source_manifest_id"], SOURCE_MANIFEST_PATHS[role]),
                "toolchain_name": metadata["toolchain_name"],
                "toolchain_version": metadata["toolchain_version"],
                "toolchain_profile_binding": raw_binding(metadata["runtime_profile_id"], RUNTIME_PROFILE_PATHS[role]),
                "dependency_lock_binding": raw_binding(
                    f"hda-dependency-lock.{role}.0001", files["dependency_lock"]
                ),
                "configuration_binding": raw_binding(f"hda-evaluator-configuration.{role}.0001", files["configuration"]),
                "input_adapter_binding": raw_binding(f"hda-input-adapter.{role}.0001", files["adapter"]),
                "network_access": False,
                "mutable_toolchain_alias_used": False,
            },
            "input_bindings": copy.deepcopy(inputs),
            "execution": {
                "exit_disposition": "completed",
                "exit_code": 0,
                "output_transport": "raw_projection_is_direct_output_and_result_record_binds_it",
                "raw_projection_binding": raw_binding(metadata["projection_id"], PROJECTION_PATHS[role]),
            },
            "participant_id": projection["participant_id"],
            "domain_results": copy.deepcopy(projection["domain_results"]),
            "categorical_results": copy.deepcopy(projection["categorical_results"]),
            "categorical_failures": copy.deepcopy(projection["categorical_failures"]),
            "final_disposition": projection["final_disposition"],
            "reason_codes": copy.deepcopy(projection["reason_codes"]),
            "proof_boundary": {
                "result_self_digest_forbidden": True,
                "result_names_or_predicts_seal_identity": False,
                "expected_result_fixture_consumed": False,
                "shared_evaluator_source_consumed": False,
                "generated_evaluator_code_consumed": False,
                "network_service_used": False,
                "ruleset_issued": False,
                "organizational_independence_proven": False,
                "eligibility_is_approval": False,
                "result_grants_authority": False,
                "gate_a_accepted": False,
                "runtime_authorized": False,
                "external_effects_authorized": False,
            },
            "recomputed_at": FIXED_TIMES["recomputation"],
        }
        write_json(RESULT_PATHS[role], result)
        results[role] = result
    return results


def create_comparison(
    configs: dict[str, dict[str, Any]],
    results: dict[str, dict[str, Any]],
    evidence: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    reason_contract = load_json(RULESET_PATH)["independent_recomputation_contract"][
        "comparison_receipt_reason_derivation"
    ]
    if reason_contract["complete_projection_field_order"] != list(COMPLETE_PROJECTION_FIELDS):
        raise GenerationError("generator complete projection inventory differs from ruleset")
    projections = {role: projection_for_comparison(results[role]) for role in ROLE_ORDER}
    baseline = projections["python"]
    if any(projections[role] != baseline for role in ROLE_ORDER[1:]):
        raise GenerationError("wrapper result projections do not agree exactly")
    ordered_bindings = []
    source_digests = []
    for role in ROLE_ORDER:
        source_digest = digest_bytes(SOURCE_MANIFEST_PATHS[role].read_bytes())
        source_digests.append(source_digest)
        ordered_bindings.append(
            {
                "implementation_role": role,
                "implementation_id": configs[role]["implementation_id"],
                "implementation_source_sha256": source_digest,
                "artifact_id": results[role]["artifact_id"],
                "schema_resource_id": RESULT_SCHEMA_ID,
                "read_disposition": "readable_complete",
                "raw_sha256": digest_bytes(RESULT_PATHS[role].read_bytes()),
                "byte_count": len(RESULT_PATHS[role].read_bytes()),
                "projection": copy.deepcopy(projections[role]),
            }
        )
    comparison = {
        "schema_version": "0.1.0",
        "artifact_class": "human_decision_assurance_eligibility_comparison_receipt_candidate",
        "artifact_id": COMPARISON_ARTIFACT_ID,
        "assurance_id": ASSURANCE_ID,
        "version": 1,
        "candidate_status": "unissued_architecture_candidate_not_human_authority",
        "common_input_bindings": common_input_bindings(evidence, receipt),
        "implementation_identity_inventory": [configs[role]["implementation_id"] for role in ROLE_ORDER],
        "implementation_source_digest_inventory": source_digests,
        "ordered_result_bindings": ordered_bindings,
        "field_comparisons": [
            {"field": field, "comparison_disposition": "agreement"}
            for field in COMPLETE_PROJECTION_FIELDS
        ],
        "comparison_disposition": "exact_agreement",
        "agreed_projection": copy.deepcopy(baseline),
        "reason_codes": copy.deepcopy(reason_contract["exact_agreement_reason_codes"]),
        "proof_boundary": {
            "receipt_self_digest_forbidden": True,
            "receipt_names_or_predicts_seal_identity": False,
            "one_result_substituted_for_multiple_implementations": False,
            "shared_evaluator_source_permitted": False,
            "final_disposition_only_comparison_permitted": False,
            "agreement_proves_normative_correctness": False,
            "agreement_is_approval": False,
            "comparison_grants_authority": False,
            "organizational_independence_proven": False,
            "gate_a_accepted": False,
            "runtime_authorized": False,
            "external_effects_authorized": False,
        },
        "compared_at": FIXED_TIMES["comparison"],
    }
    write_json(COMPARISON_PATH, comparison)
    return comparison


def create_seal(
    evidence: dict[str, Any], receipt: dict[str, Any], comparison: dict[str, Any]
) -> dict[str, Any]:
    core = load_json(CORE_PATH)
    agreed = comparison["agreed_projection"]
    seal = {
        "schema_version": "0.2.0",
        "artifact_class": "human_decision_assurance_seal_candidate",
        "artifact_id": SEAL_ARTIFACT_ID,
        "assurance_id": ASSURANCE_ID,
        "version": 2,
        "candidate_status": "unissued_architecture_candidate_not_human_authority",
        "evidence_class": "synthetic_architecture_fixture",
        "assurance_scope": {
            "principal_act_cardinality": "exactly_one",
            "aggregate_quorum_evaluation": "deferred_to_assured_decision_wrapper",
            "currentness_evaluation": "deferred_to_assured_decision_wrapper",
            "authority_evaluation": "deferred_to_assured_decision_wrapper",
            "assured_decision_wrapper_identity_assigned": False,
        },
        "input_bindings": {
            "core": schema_binding(core["artifact_id"], "urn:odeya:schema:human-decision-assurance-core:0.1.0", CORE_PATH),
            "evidence": schema_binding(evidence["artifact_id"], EVIDENCE_SCHEMA_ID, EVIDENCE_PATH),
            "eligibility_ruleset": ruleset_binding(),
            "backing_byte_verification_receipt": schema_binding(
                receipt["artifact_id"], BACKING_SCHEMA_ID, BACKING_RECEIPT_PATH
            ),
            "eligibility_comparison_receipt": schema_binding(
                comparison["artifact_id"], COMPARISON_SCHEMA_ID, COMPARISON_PATH
            ),
        },
        "receipt_dispositions": {
            "backing_byte_verification": receipt["verification_disposition"],
            "eligibility_comparison": comparison["comparison_disposition"],
            "agreed_recomputation_disposition": agreed["final_disposition"],
        },
        "copied_agreed_projection": copy.deepcopy(agreed),
        "assurance_disposition": agreed["final_disposition"],
        "reason_codes": copy.deepcopy(agreed["reason_codes"]),
        "decision_entry": {
            "policy_entry": "may_enter_assured_decision_assembly_only",
            "decision_value_copied_into_seal": False,
            "eligibility_is_approval": False,
            "consumer_authority_effective": False,
            "aggregate_quorum_effective": False,
            "currentness_evaluation": "deferred_to_consumer_policy_at_controlled_evaluation_time",
            "currentness_evaluated_at": None,
            "source_expiry_evaluated": False,
            "withdrawal_revocation_contradiction_evaluated": False,
        },
        "claim_boundary": {
            "seal_self_digest_forbidden": True,
            "profile_issued": False,
            "consumer_migration_complete": False,
            "accountable_review_complete": False,
            "real_human_ceremony_verified": False,
            "human_only_slot_satisfied": False,
            "aggregate_quorum_evaluated": False,
            "aggregate_quorum_authority_effective": False,
            "source_decision_semantics_interpreted": False,
            "currentness_evaluated": False,
            "organizational_independence_proven": False,
            "seal_is_approval": False,
            "seal_grants_authority": False,
            "gate_a_accepted": False,
            "runtime_authorized": False,
            "external_effects_authorized": False,
        },
        "sealed_at": FIXED_TIMES["seal"],
    }
    write_json(SEAL_PATH, seal)
    return seal


def validate_schema(instance: Any, schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        details = []
        for error in errors[:20]:
            pointer = "/" + "/".join(str(part) for part in error.absolute_path)
            details.append(f"{pointer}: {error.message}")
        raise GenerationError(f"{label} failed schema validation:\n" + "\n".join(details))


def validate_generated_chain(
    evidence: dict[str, Any],
    receipt: dict[str, Any],
    results: dict[str, dict[str, Any]],
    comparison: dict[str, Any],
    seal: dict[str, Any],
) -> None:
    validate_schema(evidence, SCHEMA_PATHS["evidence"], "Evidence 0.2")
    validate_schema(receipt, SCHEMA_PATHS["backing"], "backing-byte receipt")
    for role in ROLE_ORDER:
        validate_schema(results[role], SCHEMA_PATHS["result"], f"{role} recomputation result")
    validate_schema(comparison, SCHEMA_PATHS["comparison"], "comparison receipt")
    validate_schema(seal, SCHEMA_PATHS["seal"], "Seal 0.2")

    evidence_inventory = evidence["ordered_artifact_inventory"]
    receipt_rows = receipt["role_verifications"]
    if [row["artifact_id"] for row in receipt_rows] != evidence["ordered_artifact_ids"]:
        raise GenerationError("receipt artifact order differs from Evidence order")
    for descriptor, row in zip(evidence_inventory, receipt_rows, strict=True):
        path = ROOT / descriptor["repository_blob_path"]
        raw = path.read_bytes()
        if row["repository_blob_path"] != descriptor["repository_blob_path"]:
            raise GenerationError(f"receipt path differs for {descriptor['artifact_id']}")
        if digest_bytes(raw) != descriptor["content_address"] or len(raw) != descriptor["byte_count"]:
            raise GenerationError(f"retained blob differs from descriptor for {descriptor['artifact_id']}")
        if row["observed_raw_sha256"] != digest_bytes(raw) or row["observed_byte_count"] != len(raw):
            raise GenerationError(f"receipt observation differs from bytes for {descriptor['artifact_id']}")

    for role in ROLE_ORDER:
        direct = strict_json_bytes(PROJECTION_PATHS[role].read_bytes(), f"retained {role} projection")
        result = results[role]
        copied = {
            key: result[key]
            for key in (
                "participant_id",
                "domain_results",
                "categorical_results",
                "categorical_failures",
                "final_disposition",
                "reason_codes",
            )
        }
        if direct != copied:
            raise GenerationError(f"{role} result does not exactly copy its bound direct projection")
        raw_binding_value = result["execution"]["raw_projection_binding"]
        if raw_binding_value["raw_sha256"] != digest_bytes(PROJECTION_PATHS[role].read_bytes()):
            raise GenerationError(f"{role} result raw projection digest is stale")

    compared = [binding["projection"] for binding in comparison["ordered_result_bindings"]]
    if any(value != comparison["agreed_projection"] for value in compared):
        raise GenerationError("comparison receipt asserts agreement over unequal projections")
    expected_fields = list(COMPLETE_PROJECTION_FIELDS)
    if list(comparison["agreed_projection"]) != expected_fields:
        raise GenerationError("agreed projection is not the complete ordered direct evaluator output")
    for role, binding in zip(ROLE_ORDER, comparison["ordered_result_bindings"], strict=True):
        expected = projection_for_comparison(results[role])
        if binding["projection"] != expected:
            raise GenerationError(f"{role} comparison binding does not copy the complete result projection")
    if [entry["field"] for entry in comparison["field_comparisons"]] != expected_fields:
        raise GenerationError("comparison field inventory is not the exact complete projection inventory")
    if any(entry["comparison_disposition"] != "agreement" for entry in comparison["field_comparisons"]):
        raise GenerationError("exact-agreement comparison contains a non-agreement field")
    reason_contract = load_json(RULESET_PATH)["independent_recomputation_contract"][
        "comparison_receipt_reason_derivation"
    ]
    if reason_contract["complete_projection_field_order"] != expected_fields:
        raise GenerationError("retained ruleset complete projection inventory differs from generator")
    if comparison["reason_codes"] != reason_contract["exact_agreement_reason_codes"]:
        raise GenerationError("comparison exact-agreement reason set differs from ruleset derivation")
    if seal["copied_agreed_projection"] != comparison["agreed_projection"]:
        raise GenerationError("Seal does not exactly copy the agreed comparison projection")
    if seal["assurance_disposition"] != comparison["agreed_projection"]["final_disposition"]:
        raise GenerationError("Seal disposition differs from agreed recomputation disposition")


def create_generation_manifest(
    backing_blob_entries: list[dict[str, Any]],
    configs: dict[str, dict[str, Any]],
    evidence: dict[str, Any],
    receipt: dict[str, Any],
    results: dict[str, dict[str, Any]],
    comparison: dict[str, Any],
    seal: dict[str, Any],
    phase_two_recomputation: dict[str, Any],
) -> None:
    generated_entries = list(backing_blob_entries)
    generated_entries.extend(
        [
            manifest_entry(evidence["artifact_id"], EVIDENCE_PATH, "schema_valid_evidence_fixture"),
            manifest_entry(receipt["artifact_id"], BACKING_RECEIPT_PATH, "schema_valid_backing_receipt_fixture"),
            manifest_entry(
                NORMATIVE_INPUT_ARTIFACT_ID,
                NORMATIVE_INPUT_PATH,
                "materialized_expectation_free_input",
            ),
            manifest_entry(
                INPUT_MANIFEST_ARTIFACT_ID,
                INPUT_MANIFEST_PATH,
                "safe_input_manifest",
            ),
        ]
    )
    for role in ROLE_ORDER:
        generated_entries.extend(
            [
                manifest_entry(
                    IMPLEMENTATION_METADATA[role]["source_manifest_id"],
                    SOURCE_MANIFEST_PATHS[role],
                    "evaluator_source_manifest",
                ),
                manifest_entry(
                    IMPLEMENTATION_METADATA[role]["runtime_profile_id"],
                    RUNTIME_PROFILE_PATHS[role],
                    "exact_runtime_profile",
                ),
                manifest_entry(
                    IMPLEMENTATION_METADATA[role]["projection_id"],
                    PROJECTION_PATHS[role],
                    "direct_evaluator_stdout_projection",
                ),
                manifest_entry(results[role]["artifact_id"], RESULT_PATHS[role], "schema_valid_recomputation_result"),
            ]
        )
    for path in sorted((SUITE / "runtime").glob("*.version.txt")):
        generated_entries.append(
            manifest_entry(f"hda-runtime-version-observation.{path.stem}", path, "direct_runtime_version_probe")
        )
    generated_entries.extend(
        [
            manifest_entry(comparison["artifact_id"], COMPARISON_PATH, "schema_valid_comparison_receipt"),
            manifest_entry(seal["artifact_id"], SEAL_PATH, "schema_valid_seal_fixture"),
        ]
    )
    if len({entry["repository_path"] for entry in generated_entries}) != len(generated_entries):
        raise GenerationError("generation manifest contains duplicate repository paths")

    manifest = {
        "schema_version": "0.1.0",
        "artifact_class": "human_decision_assurance_successor_generation_manifest",
        "artifact_id": GENERATION_MANIFEST_ARTIFACT_ID,
        "assurance_id": ASSURANCE_ID,
        "candidate_status": "synthetic_architecture_evidence_not_ceremony_or_authority",
        "generator_source_binding": manifest_entry(
            "hda-successor-evidence-generator.python.0005",
            Path(__file__).resolve(),
            "retained_evidence_generator",
        ),
        "normative_schema_bindings": [
            manifest_entry(f"hda-schema.{name}.0001", path, "json_schema")
            for name, path in SCHEMA_PATHS.items()
        ],
        "predecessor_candidate": copy.deepcopy(PREDECESSOR_SUBJECT),
        "phase_two_challenge_recomputation": copy.deepcopy(
            phase_two_recomputation
        ),
        "bounded_technical_review_scope": {
            "scope_id": "hda-successor-t0-technical-review-scope.0005",
            "scope_semantics": (
                "the_exact_generation_manifest_and_every_direct_or_"
                "transitively_bound_t0_member_excluding_the_later_review_"
                "report_and_status_prose"
            ),
            "direct_input_bindings": [
                manifest_entry(
                    VECTOR_CORPUS_ARTIFACT_ID,
                    VECTOR_PATH,
                    "expectation_free_vector_corpus",
                ),
                manifest_entry(
                    "hda-successor-case-answers.0001",
                    CASES_PATH,
                    "private_conformance_answer_corpus",
                ),
                manifest_entry(
                    "hda-successor-chain-known-bads.0002",
                    CHAIN_CASES_PATH,
                    "downstream_chain_known_bad_corpus",
                ),
                manifest_entry(
                    "hda-successor-validator.python.0005",
                    VALIDATOR_PATH,
                    "separately_implemented_retained_chain_validator",
                ),
                manifest_entry(
                    "hda-individual-eligibility-ruleset.v2.0001",
                    RULESET_PATH,
                    "normative_eligibility_ruleset",
                ),
                manifest_entry(
                    "hda-content-address-resolver-profile.0001",
                    RESOLVER_PATH,
                    "content_address_resolver_profile",
                ),
                manifest_entry(
                    "hda-challenge-frame-profile.v2.0001",
                    CHALLENGE_PROFILE_PATH,
                    "challenge_frame_profile",
                ),
                manifest_entry(
                    "hda-challenge-frame-v2-evidence.0001",
                    CHALLENGE_EVIDENCE_PATH,
                    "challenge_frame_source_vector_evidence",
                ),
                manifest_entry(
                    "hda-core-fixture.synthetic.0001",
                    CORE_PATH,
                    "exact_core_fixture",
                ),
                manifest_entry(
                    "hda-decision-subject-fixture.synthetic.0001",
                    DECISION_PATH,
                    "exact_decision_subject_fixture",
                ),
                manifest_entry(
                    "hda-candidate-manifest-fixture.synthetic.0001",
                    CANDIDATE_MANIFEST_PATH,
                    "exact_candidate_manifest_fixture",
                ),
                manifest_entry(
                    "repository-release-toolchain-lock.0001",
                    TOOLCHAIN_LOCK_PATH,
                    "toolchain_lock",
                ),
                manifest_entry(
                    "architecture-python-requirements-source.0001",
                    ARCHITECTURE_REQUIREMENTS_SOURCE_PATH,
                    "python_requirements_source",
                ),
                manifest_entry(
                    "architecture-python-requirements-lock.0001",
                    ARCHITECTURE_REQUIREMENTS_LOCK_PATH,
                    "hash_locked_python_environment",
                ),
                *[
                    manifest_entry(
                        f"hda-evaluator-configuration.{role}.0001",
                        IMPLEMENTATION_FILES[role]["configuration"],
                        "evaluator_configuration",
                    )
                    for role in ROLE_ORDER
                ],
                *[
                    manifest_entry(
                        f"hda-dependency-lock.{role}.0001",
                        IMPLEMENTATION_FILES[role]["dependency_lock"],
                        "evaluator_dependency_lock",
                    )
                    for role in ROLE_ORDER
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
        },
        "generated_artifacts": generated_entries,
        "chain_order": [
            "Evidence 0.2 and fourteen content-addressed backing preimages",
            "backing-byte verification receipt",
            "expectation-free safe input manifest and materialized vector",
            "three pairwise-distinct evaluator source and exact runtime profiles",
            "three direct evaluator stdout projections",
            "three schema-valid wrapper recomputation results",
            "semantic full-projection comparison receipt",
            "Seal 0.2",
            "this downstream generation manifest excluding its own digest",
        ],
        "chain_edges": [
            {"from": evidence["artifact_id"], "to": receipt["artifact_id"]},
            {"from": receipt["artifact_id"], "to": INPUT_MANIFEST_ARTIFACT_ID},
            *[
                {
                    "from": INPUT_MANIFEST_ARTIFACT_ID,
                    "to": IMPLEMENTATION_METADATA[role]["projection_id"],
                }
                for role in ROLE_ORDER
            ],
            *[
                {
                    "from": IMPLEMENTATION_METADATA[role]["projection_id"],
                    "to": results[role]["artifact_id"],
                }
                for role in ROLE_ORDER
            ],
            *[
                {"from": results[role]["artifact_id"], "to": comparison["artifact_id"]}
                for role in ROLE_ORDER
            ],
            {"from": comparison["artifact_id"], "to": seal["artifact_id"]},
            {"from": seal["artifact_id"], "to": GENERATION_MANIFEST_ARTIFACT_ID},
        ],
        "implementation_identity_inventory": [configs[role]["implementation_id"] for role in ROLE_ORDER],
        "complete_projection_agreement": True,
        "schema_valid_fixture_count": 7,
        "content_addressed_backing_blob_count": 14,
        "fixture_timestamp_semantics": (
            "deterministic_fixture_values_not_observed_ceremony_runtime_or_"
            "external_event_times"
        ),
        "network_access": False,
        "real_human_ceremony_verified": False,
        "organizational_independence_proven": False,
        "gate_a_accepted": False,
        "runtime_authorized": False,
        "external_effects_authorized": False,
        "manifest_self_digest_forbidden": True,
    }
    write_json(GENERATION_MANIFEST_PATH, manifest)


def replace_exactly_one_identifier(
    raw: bytes, stale: bytes, corrected: bytes
) -> bytes:
    if len(stale) != len(corrected):
        raise GenerationError("predecessor migration identifiers differ in length")
    if raw.count(stale) != 1:
        raise GenerationError(
            "published predecessor vector does not contain exactly one stale id"
        )
    return raw.replace(stale, corrected)


def migrate_exact_predecessor_vector(
    predecessor_raw: bytes,
    corrected_authentication_challenge_id: str,
    corrected_semantic_value: dict[str, Any],
) -> bytes:
    if (
        digest_bytes(predecessor_raw)
        != PREDECESSOR_SUBJECT["vector_corpus_raw_sha256"]
    ):
        raise GenerationError("vector migration input is not the exact predecessor")
    if re.fullmatch(
        r"sha256:[0-9a-f]{64}", corrected_authentication_challenge_id
    ) is None:
        raise GenerationError("corrected authentication challenge id is invalid")
    stale = PREDECESSOR_SUBJECT["stale_authentication_challenge_id"].encode(
        "ascii"
    )
    corrected = corrected_authentication_challenge_id.encode("ascii")
    migrated_raw = replace_exactly_one_identifier(
        predecessor_raw, stale, corrected
    )
    migrated_value = strict_json_bytes(
        migrated_raw, "exact migrated predecessor vector"
    )
    if migrated_value != corrected_semantic_value:
        raise GenerationError(
            "byte-preserving predecessor migration changed unexpected semantics"
        )
    return migrated_raw


def local_git_object_directory(repository_root: Path) -> Path:
    """Resolve the worktree's shared object directory without consulting Git."""
    dot_git = repository_root / ".git"
    if dot_git.is_dir() and not dot_git.is_symlink():
        git_directory = dot_git.resolve(strict=True)
    elif dot_git.is_file() and not dot_git.is_symlink():
        pointer = dot_git.read_text(encoding="utf-8")
        if (
            len(pointer.encode("utf-8")) > 4096
            or not pointer.startswith("gitdir: ")
            or "\x00" in pointer
        ):
            raise GenerationError("Git worktree pointer is malformed")
        pointer_value = pointer.removeprefix("gitdir: ").strip()
        if not pointer_value:
            raise GenerationError("Git worktree pointer is empty")
        candidate = Path(pointer_value)
        if not candidate.is_absolute():
            candidate = repository_root / candidate
        git_directory = candidate.resolve(strict=True)
    else:
        raise GenerationError("repository has no regular Git directory")

    common_pointer = git_directory / "commondir"
    if common_pointer.exists():
        if not common_pointer.is_file() or common_pointer.is_symlink():
            raise GenerationError("Git common-directory pointer is not regular")
        common_value = common_pointer.read_text(encoding="utf-8")
        if (
            len(common_value.encode("utf-8")) > 4096
            or not common_value.strip()
            or "\x00" in common_value
        ):
            raise GenerationError("Git common-directory pointer is malformed")
        common_candidate = Path(common_value.strip())
        if not common_candidate.is_absolute():
            common_candidate = git_directory / common_candidate
        common_directory = common_candidate.resolve(strict=True)
    else:
        common_directory = git_directory
    object_directory = (common_directory / "objects").resolve(strict=True)
    if not object_directory.is_dir():
        raise GenerationError("Git object directory is absent")
    return object_directory


def git_object_bytes(
    commit: str,
    repository_path: str,
    *,
    repository_root: Path = ROOT,
) -> bytes:
    """Read one literal local blob without repository config, refs, or fetch."""
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise GenerationError("predecessor commit is not an exact object id")
    components = repository_path.split("/")
    if (
        not repository_path
        or repository_path.startswith("/")
        or any(component in {"", ".", ".."} for component in components)
        or "\x00" in repository_path
    ):
        raise GenerationError("predecessor repository path is not normalized")
    object_directory = local_git_object_directory(repository_root)
    with tempfile.TemporaryDirectory(prefix="odeya-hda-object-reader-") as raw_root:
        isolated_git_directory = Path(raw_root) / "isolated.git"
        (isolated_git_directory / "objects").mkdir(parents=True)
        (isolated_git_directory / "refs").mkdir()
        (isolated_git_directory / "HEAD").write_bytes(
            b"ref: refs/heads/unused\n"
        )
        environment = closed_environment()
        environment.update(
            {
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_DIR": str(isolated_git_directory),
                "GIT_LITERAL_PATHSPECS": "1",
                "GIT_NO_LAZY_FETCH": "1",
                "GIT_NO_REPLACE_OBJECTS": "1",
                "GIT_OBJECT_DIRECTORY": str(object_directory),
                "GIT_OPTIONAL_LOCKS": "0",
                "GIT_TERMINAL_PROMPT": "0",
            }
        )
        completed = subprocess.run(
            [
                "git",
                "--no-replace-objects",
                "--literal-pathspecs",
                "cat-file",
                "blob",
                f"{commit}:{repository_path}",
            ],
            cwd=repository_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    if completed.returncode != 0:
        raise GenerationError("local predecessor Git object is unavailable")
    return completed.stdout


def self_test_predecessor_migration() -> None:
    repository_path = relative(VECTOR_PATH)
    predecessor_raw = git_object_bytes(
        PREDECESSOR_SUBJECT["commit"], repository_path
    )
    predecessor_value = strict_json_bytes(
        predecessor_raw, "published predecessor vector"
    )
    recomputation = recompute_phase_two_challenge_relation(
        predecessor_value["base_input"],
        vector_raw_sha256=digest_bytes(predecessor_raw),
    )
    migrated_raw = migrate_exact_predecessor_vector(
        predecessor_raw,
        recomputation["authentication_challenge_id"],
        predecessor_value,
    )
    if migrated_raw != VECTOR_PATH.read_bytes():
        raise GenerationError(
            "exact predecessor migration does not reproduce the retained vector"
        )

    near_miss = predecessor_raw.replace(
        b'  "suite_version": "0.1.0",',
        b'  "suite_version": "0.1.1",',
        1,
    )
    if near_miss == predecessor_raw or len(near_miss) != len(predecessor_raw):
        raise GenerationError("same-length migration near-miss setup failed")
    try:
        migrate_exact_predecessor_vector(
            near_miss,
            recomputation["authentication_challenge_id"],
            predecessor_value,
        )
    except GenerationError as exc:
        if str(exc) != "vector migration input is not the exact predecessor":
            raise
    else:
        raise GenerationError("same-length migration near-miss was accepted")

    stale = PREDECESSOR_SUBJECT["stale_authentication_challenge_id"].encode(
        "ascii"
    )
    corrected = recomputation["authentication_challenge_id"].encode("ascii")
    for label, candidate in (
        ("zero-stale", predecessor_raw.replace(stale, corrected)),
        ("multiple-stale", predecessor_raw + stale),
    ):
        try:
            replace_exactly_one_identifier(candidate, stale, corrected)
        except GenerationError as exc:
            if "exactly one stale id" not in str(exc):
                raise
        else:
            raise GenerationError(f"{label} predecessor migration was accepted")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test-predecessor-migration",
        action="store_true",
        help=(
            "replay the one-time migration from the exact published Git object "
            "and run its refusal controls without generating artifacts"
        ),
    )
    parser.add_argument(
        "--python-executable",
        type=Path,
        default=Path(sys.executable),
        help="Exact Python 3.14.2 executable; defaults to the generator interpreter.",
    )
    parser.add_argument(
        "--node-executable",
        type=Path,
        help="Canonical installer-cache Node.js 24.18.0 executable.",
    )
    parser.add_argument(
        "--java-bin",
        type=Path,
        help=(
            "canonical installer-cache bin directory containing Temurin java "
            "and javac 21.0.9+10"
        ),
    )
    args = parser.parse_args()
    if not args.self_test_predecessor_migration and (
        args.node_executable is None or args.java_bin is None
    ):
        parser.error("--node-executable and --java-bin are required for generation")
    return args


def main() -> int:
    args = parse_args()
    if args.self_test_predecessor_migration:
        self_test_predecessor_migration()
        print(
            "exact predecessor migration replayed; same-length, zero-stale, "
            "and multiple-stale controls refused"
        )
        return 0
    assert args.node_executable is not None and args.java_bin is not None
    attest_generation_toolchains(
        args.python_executable, args.node_executable, args.java_bin
    )
    vector_raw_before = VECTOR_PATH.read_bytes()
    vectors = strict_json_bytes(vector_raw_before, relative(VECTOR_PATH))
    if vectors.get("artifact_class") != "human_decision_assurance_successor_expectation_free_evaluator_inputs":
        raise GenerationError("unexpected vector corpus artifact class")
    safe_entries = [entry for entry in vectors["vectors"] if entry.get("vector_id") == VECTOR_ID]
    if len(safe_entries) != 1 or safe_entries[0].get("mutations") != []:
        raise GenerationError("safe-complete-eligible must be the unique zero-mutation retained vector")
    base_input = vectors["base_input"]
    phase_two_recomputation = recompute_phase_two_challenge_relation(
        base_input, vector_raw_sha256=digest_bytes(vector_raw_before)
    )
    # This is a one-predecessor correction, not a generic refresh: the helper
    # accepts only the exact published vector digest and exact stale value.
    # Once corrected, every later invocation must already match recomputation.
    if digest_bytes(vector_raw_before) == PREDECESSOR_SUBJECT["vector_corpus_raw_sha256"]:
        migrated_raw = migrate_exact_predecessor_vector(
            vector_raw_before,
            phase_two_recomputation["authentication_challenge_id"],
            vectors,
        )
        write_bytes(VECTOR_PATH, migrated_raw)

    backing_blob_entries = create_backing_blobs(base_input)
    configs = create_source_manifests()
    create_runtime_profiles(args.python_executable, args.node_executable, args.java_bin)
    evidence = create_evidence(base_input)
    receipt = create_backing_receipt(base_input, evidence)
    create_normative_input_and_manifest(base_input, evidence, receipt)
    projections = execute_evaluators(args.python_executable, args.node_executable, args.java_bin)
    results = create_results(configs, projections, evidence, receipt)
    comparison = create_comparison(configs, results, evidence, receipt)
    seal = create_seal(evidence, receipt, comparison)
    validate_generated_chain(evidence, receipt, results, comparison, seal)
    create_generation_manifest(
        backing_blob_entries,
        configs,
        evidence,
        receipt,
        results,
        comparison,
        seal,
        phase_two_recomputation,
    )
    print(
        "generated HDA successor chain: 14 backing blobs, 3 direct projections, "
        "7 schema-valid fixtures, and 1 downstream generation manifest"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
