#!/usr/bin/env python3
"""Independently re-derive the ADR 0093 two-phase challenge construction.

This suite does not trust the retained evidence digests. It re-implements the
frame and receipt encoders from the profile's declared rules, recomputes every
digest, and refuses any disagreement. It additionally reproduces the retained
v1 vector, so an encoder that silently changed would be caught against a
frozen predecessor rather than only against itself.

Structural and bounded-semantic architecture-time evidence only. No real
authenticator participates, no person confirms anything, no signature is
produced or verified, and nothing here is Gate A acceptance.
"""

from __future__ import annotations

import base64
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests/challenge-frame/cases.json"
PROFILE = ROOT / "architecture/human-decision-challenge-frame-v2-candidate.json"
EVIDENCE = ROOT / "architecture/human-decision-challenge-frame-v2-candidate-evidence.json"

V1_FRAME_BYTES = 720
V1_COMMITMENT = "0885968caa3ea2e1b83ae77023d77e7189655e710e41f67416201a0907eb9493"
V1_CHALLENGE_ID = "sha256:9cda614e474dd1cc6e644a557c22596467f51d2e711092d7853d6bda32d0f5f6"
RECEIPT_MAGIC = "ODEYA-HDA-CONFIRMATION-RECEIPT-V1"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest_octets(value: str) -> bytes:
    if not value.startswith("sha256:"):
        raise ValueError("digest value is not sha256-prefixed")
    return bytes.fromhex(value.split(":", 1)[1])


def encode_frame(magic: str, fields: list[tuple[str, bytes]]) -> bytes:
    out = magic.encode("ascii") + struct.pack(">H", len(fields))
    for name, value in fields:
        name_bytes = name.encode("ascii")
        out += struct.pack(">H", len(name_bytes)) + name_bytes
        out += struct.pack(">I", len(value)) + value
    return out


def challenge_octets(nonce_hex: str, frame: bytes) -> bytes:
    return bytes.fromhex(nonce_hex) + hashlib.sha256(frame).digest()


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def shared_fields(shared: dict) -> list[tuple[str, bytes]]:
    text = lambda s: s.encode("ascii")  # noqa: E731
    return [
        ("core_schema_resource_id", text(shared["core_schema_resource_id"])),
        ("core_raw_sha256", digest_octets(shared["core_raw_sha256"])),
        ("decision_schema_resource_id", text(shared["decision_schema_resource_id"])),
        ("decision_raw_sha256", digest_octets(shared["decision_raw_sha256"])),
        ("candidate_schema_resource_id", text(shared["candidate_schema_resource_id"])),
        ("candidate_raw_sha256", digest_octets(shared["candidate_raw_sha256"])),
        ("session_id", text(shared["session_id"])),
    ]


def interval_fields(shared: dict, phase: dict) -> list[tuple[str, bytes]]:
    text = lambda s: s.encode("ascii")  # noqa: E731
    return [
        ("issued_at", text(phase["issued_at"])),
        ("expires_at", text(phase["expires_at"])),
        ("relying_party_id", text(shared["relying_party_id"])),
        ("expected_origin", text(shared["expected_origin"])),
        ("nonce", bytes.fromhex(phase["nonce_hex"])),
    ]


def build_receipt_frame(receipt: dict, presentation_challenge_id: str) -> bytes:
    text = lambda s: s.encode("ascii")  # noqa: E731
    return encode_frame(
        RECEIPT_MAGIC,
        [
            ("presentation_challenge_id", digest_octets(presentation_challenge_id)),
            ("displayed_bytes_sha256", digest_octets(receipt["displayed_bytes_sha256"])),
            ("displayed_byte_count", struct.pack(">I", receipt["displayed_byte_count"])),
            ("rendering_profile_id", text(receipt["rendering_profile_id"])),
            ("confirmation_gesture_kind", text(receipt["confirmation_gesture_kind"])),
            ("confirmation_gesture_at", text(receipt["confirmation_gesture_at"])),
        ],
    )


def v1_reproduction_errors() -> list[str]:
    """Reproduce the frozen predecessor vector before trusting this encoder."""
    text = lambda s: s.encode("ascii")  # noqa: E731
    fields = [
        ("core_schema_resource_id", text("urn:odeya:schema:human-decision-assurance-core:0.1.0")),
        ("core_raw_sha256", digest_octets("sha256:48cafa2fa014605d92d263bc81dbb5940badcd60abd2f3e7375d68bb06a49084")),
        ("decision_schema_resource_id", text("urn:odeya:schema:operator-architecture-decision:0.4.0")),
        ("decision_raw_sha256", digest_octets("sha256:22c0bc954ef601bc9a00b6a6316d64691c36198d6d9a2559d3d0460aa876fa2f")),
        ("candidate_schema_resource_id", text("urn:odeya:schema:architecture-candidate-manifest:0.5.0")),
        ("candidate_raw_sha256", digest_octets("sha256:e0b0ec414439c2a327c0003eb40c2580a83e49a32e70f0acc0b5e38b2abbbcd1")),
        ("session_id", text("hda-session.synthetic.0001")),
        ("issued_at", text("2026-07-19T06:00:00.000000Z")),
        ("expires_at", text("2026-07-19T06:05:00.000000Z")),
        ("relying_party_id", text("odeya.danielwahnich.dev")),
        ("expected_origin", text("https://odeya.danielwahnich.dev")),
        ("nonce", bytes.fromhex("bb977208e93b4cf16a04acc2e6b2a72b6db005d4244b288b2931c2f6eb9f6ab6")),
    ]
    frame = encode_frame("ODEYA-HDA-CHALLENGE-FRAME-V1", fields)
    errors: list[str] = []
    if len(frame) != V1_FRAME_BYTES:
        errors.append("v1_predecessor_frame_length_drift")
    if sha_hex(frame) != V1_COMMITMENT:
        errors.append("v1_predecessor_commitment_drift")
    octets = challenge_octets(
        "bb977208e93b4cf16a04acc2e6b2a72b6db005d4244b288b2931c2f6eb9f6ab6", frame
    )
    if "sha256:" + sha_hex(octets) != V1_CHALLENGE_ID:
        errors.append("v1_predecessor_challenge_id_drift")
    return errors


def evaluate_vector(profile: dict, vector: dict) -> list[str]:
    """Recompute the whole two-phase construction and refuse disagreement."""
    errors: list[str] = []
    shared = vector["shared_inputs"]
    presentation = vector["presentation_phase"]
    receipt = vector["confirmation_receipt"]
    authentication = vector["authentication_phase"]

    # Phase one.
    p1_fields = shared_fields(shared) + interval_fields(shared, presentation)
    declared_p1 = profile["binary_frame"]["presentation_phase_ordered_fields"]
    if [name for name, _ in p1_fields] != declared_p1:
        errors.append("presentation_frame_field_order_mismatch")
    p1_frame = encode_frame(profile["binary_frame"]["magic_ascii"], p1_fields)
    if len(p1_frame) != presentation["frame_byte_count"]:
        errors.append("presentation_frame_byte_count_mismatch")
    if "sha256:" + sha_hex(p1_frame) != presentation["frame_raw_sha256"]:
        errors.append("presentation_frame_digest_mismatch")
    p1_octets = challenge_octets(presentation["nonce_hex"], p1_frame)
    if b64u(p1_octets) != presentation["challenge_base64url"]:
        errors.append("presentation_challenge_encoding_mismatch")
    recomputed_p1_id = "sha256:" + sha_hex(p1_octets)
    if recomputed_p1_id != presentation["presentation_challenge_id"]:
        errors.append("presentation_challenge_id_mismatch")

    # Receipt. It must commit to the phase-one challenge that *actually*
    # resulted from the shared inputs, not to whatever id the vector claims.
    # Building this from the recorded id would let a session, origin, or
    # decision-subject substitution slide: the real challenge would change
    # while the receipt kept validating against a stale identity, which is
    # precisely the presentation substitution this construction must refuse.
    receipt_frame = build_receipt_frame(receipt, recomputed_p1_id)
    if len(receipt_frame) != receipt["receipt_frame_byte_count"]:
        errors.append("receipt_frame_byte_count_mismatch")
    if "sha256:" + sha_hex(receipt_frame) != receipt["confirmation_receipt_raw_sha256"]:
        errors.append("receipt_digest_mismatch")
    bound_id = receipt.get("bound_presentation_challenge_id")
    if bound_id is not None and bound_id != presentation["presentation_challenge_id"]:
        errors.append("receipt_presentation_challenge_id_mismatch")
    if receipt.get("displayed_bytes_source") == "reserialized_decision_object":
        errors.append("reserialized_object_digest_used_instead_of_displayed_bytes")
    if profile["confirmation_receipt"]["reserialized_object_digest_allowed"] is not False:
        errors.append("profile_admits_reserialized_object_digest")

    # Ordering. The gesture happens after phase one opens and before phase two.
    if not (
        presentation["issued_at"]
        <= receipt["confirmation_gesture_at"]
        <= authentication["issued_at"]
    ):
        errors.append("receipt_gesture_outside_phase_order")

    # Phase two interval containment.
    if not (
        presentation["issued_at"] <= authentication["issued_at"]
        and authentication["expires_at"] <= presentation["expires_at"]
    ):
        errors.append("authentication_interval_not_contained_in_presentation_interval")

    # Nonce separation.
    if presentation["nonce_hex"] == authentication["nonce_hex"]:
        errors.append("phase_nonce_reused")

    # Phase two frame: shared + interval + the three appended bindings, last.
    text = lambda s: s.encode("ascii")  # noqa: E731
    appended = [
        ("presentation_challenge_id", digest_octets(presentation["presentation_challenge_id"])),
        ("confirmation_receipt_raw_sha256", digest_octets(receipt["confirmation_receipt_raw_sha256"])),
        ("confirmation_receipt_profile_id", text(receipt["confirmation_receipt_profile_id"])),
    ]
    omitted = set(vector.get("omit_authentication_fields", []))
    if omitted:
        appended = [item for item in appended if item[0] not in omitted]
        errors.append("authentication_frame_missing_appended_field")
    p2_fields = shared_fields(shared) + interval_fields(shared, authentication) + appended
    declared_p2 = profile["binary_frame"]["authentication_phase_ordered_fields"]
    if not omitted and [name for name, _ in p2_fields] != declared_p2:
        errors.append("authentication_frame_field_order_mismatch")
    p2_frame = encode_frame(profile["binary_frame"]["magic_ascii"], p2_fields)
    if not omitted:
        if len(p2_frame) != authentication["frame_byte_count"]:
            errors.append("authentication_frame_byte_count_mismatch")
        if "sha256:" + sha_hex(p2_frame) != authentication["frame_raw_sha256"]:
            errors.append("authentication_frame_digest_mismatch")
        p2_octets = challenge_octets(authentication["nonce_hex"], p2_frame)
        if b64u(p2_octets) != authentication["challenge_base64url"]:
            errors.append("authentication_challenge_encoding_mismatch")
        if "sha256:" + sha_hex(p2_octets) != authentication["authentication_challenge_id"]:
            errors.append("authentication_challenge_id_mismatch")

    # Acyclicity is structural, not incidental.
    if "authentication_challenge_id" in receipt:
        errors.append("receipt_references_authentication_challenge")
    if any(key.startswith("confirmation_receipt") for key in presentation):
        errors.append("presentation_frame_references_receipt")

    return sorted(set(errors))


def pointer_set(instance: dict, pointer: str, value: object, op: str) -> None:
    """Apply one mutation.

    ``replace`` refuses to create a key: a case whose path was mistyped would
    otherwise mutate nothing and be credited as a refusal it never caused.
    ``add`` is the explicit opposite and exists only for injection cases that
    must introduce a field the honest vector does not carry -- a receipt that
    names the authentication challenge, for instance.
    """
    parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer.split("/")[1:]]
    node = instance
    for part in parts[:-1]:
        node = node[part]
    if op == "replace":
        if parts[-1] not in node:
            raise KeyError(parts[-1])
    elif op == "add":
        if parts[-1] in node:
            raise ValueError(f"add mutation targets an existing key: {pointer}")
    else:
        raise ValueError(f"unsupported mutation op: {op!r}")
    node[parts[-1]] = value


def evaluate_case(profile: dict, base_vector: dict, case: dict) -> list[str]:
    vector = json.loads(json.dumps(base_vector))
    for mutation in case.get("mutations", []):
        pointer_set(
            vector, mutation["path"], mutation["value"], mutation.get("op", "replace")
        )
    observed = evaluate_vector(profile, vector)
    declared = sorted(case.get("expected_errors", []))
    if case["kind"] == "safe":
        if observed:
            return [f"{case['name']}: expected accept, got {observed}"]
        return []
    if not declared:
        return [f"{case['name']}: known-bad case declares no expected error"]
    if observed != declared:
        return [f"{case['name']}: declared {declared} but observed {observed}"]
    return []


def harness_self_test(profile: dict, base_vector: dict) -> list[str]:
    """Prove the comparison itself fires before trusting any case result."""
    failures: list[str] = []
    tampered = json.loads(json.dumps(base_vector))
    tampered["presentation_phase"]["nonce_hex"] = "00" * 32
    if not evaluate_vector(profile, tampered):
        failures.append("harness self-test: a mutated presentation nonce was accepted")
    undeclared = {"name": "self-test", "kind": "adversarial", "expected_errors": []}
    if not evaluate_case(profile, base_vector, undeclared):
        failures.append("harness self-test: a known-bad declaring no error was accepted")
    misdeclared = {
        "name": "self-test",
        "kind": "adversarial",
        "expected_errors": ["odeya_self_test_never_fires"],
        "mutations": [{"path": "/presentation_phase/nonce_hex", "value": "11" * 32}],
    }
    if not evaluate_case(profile, base_vector, misdeclared):
        failures.append("harness self-test: a misdeclared expectation was accepted")
    return failures


def main() -> int:
    profile = load(PROFILE)
    evidence = load(EVIDENCE)
    manifest = load(CASES)
    base_vector = evidence["synthetic_test_vector"]

    failures: list[str] = []
    failures.extend(f"v1 predecessor reproduction: {e}" for e in v1_reproduction_errors())
    failures.extend(harness_self_test(profile, base_vector))
    for case in manifest["cases"]:
        failures.extend(evaluate_case(profile, base_vector, case))

    if profile["proof_boundary"]["profile_issued"] is not False:
        failures.append("profile claims issuance while Gate A is blocked")
    if evidence["proof_boundary"]["no_real_authenticator_participated"] is not True:
        failures.append("evidence claims a real authenticator participated")

    if failures:
        print("ChallengeFrameV2: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    safe = sum(c["kind"] == "safe" for c in manifest["cases"])
    bad = sum(c["kind"] == "adversarial" for c in manifest["cases"])
    print(
        f"ChallengeFrameV2: {safe} safe controls and {bad} one-mutation known-bads passed; "
        "the v1 predecessor vector reproduced exactly. Deterministic recomputation only: "
        "no ceremony, no signature, no issuance, and Gate A remains unaccepted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
