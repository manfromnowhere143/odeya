#!/usr/bin/env python3
"""Offline semantic checks for the unissued HumanDecisionAssurance candidate.

The suite verifies an acyclic raw-byte construction:

    decision/material bytes -> core -> evidence -> seal -> later consumer

It deliberately does not perform a real WebAuthn ceremony, prove a natural
person, issue the candidate profile, migrate a consumer, satisfy an H slot,
accept Gate A, or authorize runtime or external effects.
"""

from __future__ import annotations

import base64
import copy
import functools
import hashlib
import json
import struct
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests/human-decision-assurance"
CASES = SUITE / "cases.json"

CORE_SCHEMA = ROOT / "schemas/human-decision-assurance-core.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/human-decision-assurance-evidence.schema.json"
SEAL_SCHEMA = ROOT / "schemas/human-decision-assurance-seal.schema.json"
CORE_FIXTURE = (
    ROOT / "tests/architecture-schema/fixtures/"
    "human-decision-assurance-core.valid.json"
)
EVIDENCE_FIXTURE = (
    ROOT / "tests/architecture-schema/fixtures/"
    "human-decision-assurance-evidence.valid.json"
)
SEAL_FIXTURE = (
    ROOT / "tests/architecture-schema/fixtures/"
    "human-decision-assurance-seal.valid.json"
)
KB001_FIXTURE = (
    ROOT / "tests/architecture-schema/fixtures/"
    "prq-013-kb-001.agent-accessible-key.known-bad.json"
)
CHALLENGE_FRAME = (
    ROOT / "architecture/human-decision-challenge-frame-v1-candidate.json"
)
CHALLENGE_FRAME_EVIDENCE = (
    ROOT
    / "architecture/human-decision-challenge-frame-v1-candidate-evidence.json"
)
INDIVIDUAL_ELIGIBILITY_RULESET = (
    ROOT
    / "architecture/"
    "human-decision-assurance-individual-eligibility-ruleset-v1-candidate.json"
)
DECISION_SOURCE = (
    ROOT
    / "tests/architecture-schema/fixtures/"
    "human-decision-assurance-decision-subject.valid.json"
)
CANDIDATE_SOURCE = (
    ROOT
    / "tests/architecture-review/fixtures/"
    "architecture-candidate-manifest.valid.json"
)
CONSUMER_CENSUS = (
    ROOT / "architecture/human-decision-assurance-consumer-census.json"
)
CANDIDATE_EVIDENCE = (
    ROOT / "architecture/human-decision-assurance-candidate-evidence.json"
)

CORE_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-core:0.1.0"
EVIDENCE_SCHEMA_ID = (
    "urn:odeya:schema:human-decision-assurance-evidence:0.1.0"
)
SEAL_SCHEMA_ID = "urn:odeya:schema:human-decision-assurance-seal:0.1.0"
SUPPORTED = "supported"
OBSERVATION_STATUSES = {
    "supported",
    "contradicted",
    "unknown",
    "not_applicable",
}
RECORDED_OUTCOME_DIAGNOSTICS = {
    "challenge_required_evidence_not_supported",
    "challenge_replay_or_consumption_invalid",
    "challenge_time_window_invalid",
    "decision_confirmation_stale_or_out_of_window",
    "challenge_assertion_or_consumption_time_invalid",
    "controlled_time_order_invalid",
    "decision_gesture_not_supported",
    "decision_gesture_not_human_initiated",
    "authenticator_gesture_reused_as_decision_gesture",
    "webauthn_cryptographic_evidence_not_supported",
    "authentication_intent_not_supported",
    "phishing_resistance_not_supported",
    "user_presence_not_supported",
    "user_verification_not_supported",
    "webauthn_context_binding_not_supported",
    "cross_origin_context_not_supported",
    "authenticator_backup_state_unknown",
    "signature_counter_risk_or_unknown",
    "identity_proofing_not_supported",
    "principal_authenticator_binding_not_supported",
    "authenticator_custody_not_supported",
    "private_key_nonexportability_not_supported",
    "agent_model_tool_signing_not_excluded",
    "unattended_invocation_not_excluded",
    "human_remote_initiation_not_supported",
    "exclusive_session_control_not_supported",
    "shared_authenticator_not_excluded",
    "sync_recovery_exposure_not_accounted",
    "shared_effective_control_not_distinct",
    "observed_objection_unresolved",
    "observed_conflict_undisposed",
    "controlled_time_not_supported",
    "independent_verifier_not_supported",
    "ordered_evidence_not_sanitized",
    "sanitization_verification_not_supported",
}
EXPECTED_CANDIDATE_EVIDENCE_BINDINGS = [
    (
        "docs/decisions/"
        "0092-bind-human-decisions-through-an-external-assurance-wrapper.md",
        "architecture_decision",
    ),
    (
        "schemas/human-decision-assurance-core.schema.json",
        "assurance_core_schema",
    ),
    (
        "schemas/human-decision-assurance-evidence.schema.json",
        "assurance_evidence_schema",
    ),
    (
        "schemas/human-decision-assurance-seal.schema.json",
        "assurance_seal_schema",
    ),
    (
        "tests/architecture-schema/fixtures/"
        "human-decision-assurance-core.valid.json",
        "synthetic_core_control",
    ),
    (
        "tests/architecture-schema/fixtures/"
        "human-decision-assurance-evidence.valid.json",
        "synthetic_evidence_control",
    ),
    (
        "tests/architecture-schema/fixtures/"
        "human-decision-assurance-seal.valid.json",
        "synthetic_seal_control",
    ),
    (
        "tests/architecture-schema/fixtures/"
        "human-decision-assurance-decision-subject.valid.json",
        "relationally_coherent_synthetic_source_decision",
    ),
    (
        "tests/architecture-review/fixtures/"
        "architecture-candidate-manifest.valid.json",
        "exact_synthetic_candidate_subject",
    ),
    (
        "tests/architecture-schema/fixtures/"
        "prq-013-kb-001.agent-accessible-key.known-bad.json",
        "agent_accessible_key_known_bad",
    ),
    (
        "architecture/human-decision-challenge-frame-v1-candidate.json",
        "challenge_frame_profile",
    ),
    (
        "architecture/"
        "human-decision-challenge-frame-v1-candidate-evidence.json",
        "challenge_frame_vector_evidence",
    ),
    (
        "architecture/human-decision-assurance-consumer-census.json",
        "consumer_census",
    ),
    (
        "architecture/"
        "human-decision-assurance-individual-eligibility-ruleset-v1-candidate.json",
        "individual_eligibility_ruleset_candidate",
    ),
    ("tests/human-decision-assurance/check.py", "semantic_checker"),
    ("tests/human-decision-assurance/cases.json", "semantic_case_corpus"),
    ("tests/human-decision-assurance/README.md", "suite_contract"),
]
EXPECTED_HUMAN_DECISION_FAMILY_IDS = [
    "constitutional_bootstrap_and_assignment",
    "gate_a_review_finding_and_operator_decision",
    "registry_key_method_and_validation_seal",
    "admit_defer_decline_mission",
    "freeze_confirmatory_protocol",
    "amend_or_fork_after_exposure",
    "acquire_or_process_d1_through_d3_data",
    "material_spend_or_paid_provider_beyond_ceiling",
    "r2_external_write",
    "r3_r4_or_physical_action",
    "assign_verifier",
    "settle_model_assisted_or_expert_verification",
    "settle_ambiguous_external_outcome",
    "authorize_private_or_restricted_release",
    "authorize_public_release",
    "correct_retract_or_withdraw",
    "promote_strategy_candidate",
    "break_glass",
]
EXPECTED_TRANSITIVE_CONSUMER_FAMILY_IDS = [
    "root_authority",
    "authority_assignment_and_grant",
    "protocol_decisions",
    "data_use",
    "architecture_review_and_operator_decision",
    "publication_and_correction",
    "strategy_promotion",
    "recovery",
    "key_method_validation_and_registry_seals",
]
EXPECTED_VALIDATOR_PATHS = [
    "scripts/validate_gate_a_prerequisites.py",
    "scripts/validate.py",
    "tests/architecture-schema/manifest.json",
    "tests/architecture-review/check.py",
    "tests/constitutional-construction/check.py",
    "tests/lifecycle-closure/check.py",
    "tests/canonical-profile-candidate/check.py",
    "tests/work-intent-identity-candidate/check.py",
    "tests/work-intent-reference-resolution/check.py",
    "tests/work-identity-successor-cohort/check.py",
    "scripts/validate_canonicalization_dispositions.py",
]
EXPECTED_CANDIDATE_SCHEMA_PATHS = [
    "schemas/human-decision-assurance-core.schema.json",
    "schemas/human-decision-assurance-evidence.schema.json",
    "schemas/human-decision-assurance-seal.schema.json",
]
EXPECTED_EVIDENCE_ROLES = [
    "sanitized_challenge_lifecycle_and_atomic_consumption_record",
    "exact_unmodified_client_data_json",
    "exact_unmodified_authenticator_data",
    "exact_unmodified_webauthn_signature",
    "exact_unmodified_credential_public_key",
    "sanitized_exact_material_presentation_and_decision_confirmation_receipt",
    "sanitized_custody_observation",
    "sanitized_identity_proofing_profile",
    "sanitized_principal_authenticator_binding",
    "sanitized_controlled_time_observation",
    "sanitized_verifier_observation",
    "sanitized_delegation_effective_control_observation",
]
EXACT_CRYPTOGRAPHIC_INPUT_ROLES = {
    "exact_unmodified_client_data_json",
    "exact_unmodified_authenticator_data",
    "exact_unmodified_webauthn_signature",
    "exact_unmodified_credential_public_key",
}
EXPECTED_OPERATOR_ACCEPTANCE_CONSUMERS = [
    (
        "schemas/canonical-work-lease-profile-bound-candidate.schema.json",
        ("/properties/operator_acceptance_ref",),
    ),
    (
        "schemas/canonicalization-profile-candidate-evidence.schema.json",
        (
            "/properties/acceptance_boundary/properties/"
            "operator_acceptance_ref",
        ),
    ),
    (
        "schemas/canonicalization-profile-core.schema.json",
        (
            "/properties/bootstrap_boundary/properties/"
            "operator_acceptance_ref",
        ),
    ),
    (
        "schemas/work-contract-profile-bound-candidate.schema.json",
        ("/properties/operator_acceptance_ref",),
    ),
    (
        "schemas/work-identity-successor-cohort-evidence.schema.json",
        (
            "/properties/acceptance_boundary/properties/"
            "operator_acceptance_ref",
        ),
    ),
    (
        "schemas/work-intent-exact-reference-candidate.schema.json",
        ("/properties/operator_acceptance_ref",),
    ),
    (
        "schemas/work-intent-identity-candidate-evidence.schema.json",
        (
            "/properties/identity_construction_boundary/properties/"
            "operator_acceptance_ref",
            "/properties/profile_candidate_binding/properties/"
            "operator_acceptance_ref",
        ),
    ),
    (
        "schemas/work-intent-profile-bound-candidate.schema.json",
        ("/properties/operator_acceptance_ref",),
    ),
    (
        "schemas/work-intent-reference-resolution-evidence.schema.json",
        (
            "/properties/acceptance_boundary/properties/"
            "operator_acceptance_ref",
        ),
    ),
]
EXPECTED_MISSING_NODES = [
    ("mission_admission_decision.record_schema", "decision_record_schema"),
    ("proposal.decide.typed_payload", "command_payload_schema"),
    ("protocol.freeze.typed_payload", "command_payload_schema"),
    ("protocol.amend.typed_payload", "command_payload_schema"),
    ("protocol.fork.typed_payload", "command_payload_schema"),
    ("protocol.supersede.typed_payload", "command_payload_schema"),
    ("material_spend_decision.record_schema", "decision_record_schema"),
    (
        "external_effect_human_decision.composite_record_schema",
        "decision_record_schema",
    ),
    (
        "physical_action_human_decision.composite_record_schema",
        "decision_record_schema",
    ),
    ("physical_interlock_attestation.contract", "attestation_contract"),
    (
        "verifier_assignment_decision.record_schema",
        "decision_record_schema",
    ),
    ("verification.assign.typed_payload", "command_payload_schema"),
    (
        "verification_settlement_decision.record_schema",
        "decision_record_schema",
    ),
    ("outcome_settlement_decision.record_schema", "decision_record_schema"),
    ("release.decide.typed_payload", "command_payload_schema"),
    ("publication.seal.typed_payload", "command_payload_schema"),
    ("claim_retract.typed_payload", "command_payload_schema"),
    ("publication_correct.typed_payload", "command_payload_schema"),
    ("publication_withdraw.typed_payload", "command_payload_schema"),
    ("strategy.decide_promotion.typed_payload", "command_payload_schema"),
    (
        "strategy.promotion_decided.exact_promotion_decision_reference",
        "typed_event_reference",
    ),
    ("break_glass_decision.record_schema", "decision_record_schema"),
    (
        "key_profile.approve.typed_payload_and_event",
        "command_and_event_contract",
    ),
    (
        "method_registry.seal.typed_payload_and_event",
        "command_and_event_contract",
    ),
    (
        "validation_rule_registry.seal.typed_payload_and_event",
        "command_and_event_contract",
    ),
    (
        "human_decision_assurance.consumer_dereference_rule",
        "semantic_rule",
    ),
    (
        "human_decision_assurance.subject_display_candidate_equality_rule",
        "semantic_rule",
    ),
    (
        "human_decision_assurance.single_use_replay_rule",
        "semantic_rule",
    ),
    (
        "human_decision_assurance.effective_control_quorum_rule",
        "semantic_rule",
    ),
    (
        "human_decision_assurance.assured_decision_wrapper_contract",
        "wrapper_contract",
    ),
    (
        "human_decision_assurance.currentness_authority_evaluation_rule",
        "semantic_rule",
    ),
    (
        "human_decision_assurance.h_slot_wrapper_input_rule",
        "semantic_rule",
    ),
    (
        "PRQ-013-KB-001.end_to_end_consuming_transition_fixture",
        "known_bad_fixture",
    ),
]
EXPECTED_CENSUS_TOP_LEVEL_KEYS = {
    "artifact_type",
    "artifact_id",
    "version",
    "status",
    "as_of_date",
    "subject",
    "scope_boundary",
    "pointer_discovery_profile",
    "class_definitions",
    "baseline_schema_partition",
    "candidate_mechanism_schemas",
    "command_type_partition",
    "event_type_partition",
    "human_decision_families",
    "transitive_consumer_families",
    "operator_acceptance_consumers",
    "validator_census",
    "missing_contract_nodes",
    "dynamic_completeness_rule",
    "coverage",
    "migration",
    "nonclaims",
}
EXPECTED_CENSUS_SUBJECT = {
    "baseline_git_commit": "56e8062334fb81bba955ba137be690e085d4c88e",
    "baseline_git_tree": "d90ed6dd8c54b91a1e503358f98ecaa08c766fa3",
    "baseline_schema_count": 112,
    "candidate_mechanism_schema_count": 3,
    "current_union_schema_count": 115,
    "authority_matrix_ref": "docs/AUTHORITY_MATRIX.md",
    "baseline_authority_matrix_raw_sha256": (
        "sha256:5c1ffc01e8cafd84b2d761c53fb598aa159ba585ac743184a9a83872cce0b6be"
    ),
    "baseline_authority_matrix_byte_count": 22533,
    "current_authority_matrix_raw_sha256": (
        "sha256:51609375def9c31048aedfc8c81774996ecdcaf040382efb588014f10d5cbd24"
    ),
    "current_authority_matrix_byte_count": 23107,
    "gate_a_prerequisite_ref": "architecture/gate-a-prerequisite-closure.json",
    "prq_id": "PRQ-013",
}
EXPECTED_CENSUS_SCOPE_BOUNDARY = {
    "baseline_rows_are_read_from_exact_git_tree": True,
    "candidate_mechanism_rows_are_side_by_side_worktree_candidates": True,
    "candidate_mechanism_rows_are_not_part_of_baseline_partition": True,
    "all_current_consumer_schemas_remain_byte_identical_to_baseline": True,
    "complete_means_complete_only_for_the_named_frozen_source_corpus": True,
    "future_schema_command_event_or_authority_matrix_change_requires_recomputation": True,
    "t0_scope_is_unissued_individual_assurance_foundation_only": True,
    "t1_t2_authority_currentness_quorum_and_consumer_dependencies_precede_wrapper_migration": True,
    "gate_a_scope_is_architecture_evidence_not_live_ceremony": True,
    "real_protected_ceremony_is_separately_authorized_gate_b_probe": True,
    "runtime_conformance_is_gate_c_exit_condition": True,
}
EXPECTED_CENSUS_SEMANTIC_SHA256 = {
    "pointer_discovery_profile": (
        "sha256:0c602b6a11762e19e6926a5e9f069ae0e67cf4e81c0427cbafbf448db5d75d20"
    ),
    "class_definitions": (
        "sha256:a243d9952f5e9c972533c298c880dd85ebe27859948418e63ae3417007988263"
    ),
    "command_type_partition": (
        "sha256:663c333c7e42a2c63cdc754130a4e15a0c88e20c75283958f7bee22ed1960cef"
    ),
    "event_type_partition": (
        "sha256:5bd0add2d81596ea519f105a6ab053f8850f883328799de4e99621db9e7f64e0"
    ),
    "baseline_judgment_projection": (
        "sha256:ae5200cf5ffc8944cb5bd2297fab1a6e26187eb397a3d7891c78a9432ec23bf1"
    ),
    "candidate_status_projection": (
        "sha256:816abcfb2c55e7055a219697a5c229f225ae8ac7ee4e7a34d86e3e525af45398"
    ),
    "human_decision_families": (
        "sha256:145ba5502980c358a0710df70fcd1289770fe539699080ce9fece3dc37f68681"
    ),
    "transitive_consumer_families": (
        "sha256:2e811603a95126002d7303a898bb772e91185c50b3a4e5d79aacc1d27a14e77f"
    ),
    "validator_census": (
        "sha256:1d5e2c179b6ef215d6d7004441e4f1ac270bc1bcf5e27cdaacfb7a278dfb7039"
    ),
    "missing_construction_boundary": (
        "sha256:4dadf5ed2c2dfa0925aca40a44fa792c40959491e6d87f7703c36ea35340be89"
    ),
    "dynamic_completeness_rule": (
        "sha256:6b7670ae0c0e499a866f1940cb6c38d28b8c54ca1ecb5fae87f8bed1eedd6138"
    ),
    "migration": (
        "sha256:cced163ea2617444cf3348c497ace7ea9ad9c956c8668162dc9af2c8ade826eb"
    ),
    "nonclaims": (
        "sha256:790f8e3dc25a487befe7e049e28b13c24b18f03e49ed5e4021b630f6f03ccbe8"
    ),
}


class DuplicateKey(ValueError):
    """Raised before duplicate JSON names can collapse into one mapping."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r}")


def loads_object(raw: bytes | str, label: str) -> dict[str, Any]:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    value = json.loads(
        raw,
        object_pairs_hook=strict_pairs,
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain one JSON object")
    return value


def load(path: Path) -> dict[str, Any]:
    return loads_object(path.read_bytes(), str(path.relative_to(ROOT)))


def render(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )


def raw_sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def semantic_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return raw_sha256(raw)


def raw_binding(value: dict[str, Any]) -> tuple[str, int]:
    raw = render(value)
    return raw_sha256(raw), len(raw)


def unique_errors(errors: list[str]) -> list[str]:
    return sorted(set(errors))


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


def pointer_get(subject: Any, pointer: str) -> Any:
    current = subject
    for token in pointer_tokens(pointer):
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def apply_mutation(subject: Any, mutation: dict[str, Any]) -> None:
    tokens = pointer_tokens(mutation["path"])
    parent = subject
    for token in tokens[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    final = tokens[-1]
    operation = mutation["op"]
    if isinstance(parent, list):
        index = int(final)
        if operation == "replace":
            parent[index] = mutation["value"]
        elif operation == "remove":
            del parent[index]
        elif operation == "add":
            parent.insert(index, mutation["value"])
        else:
            raise ValueError(f"unsupported operation {operation!r}")
    elif isinstance(parent, dict):
        if operation == "replace":
            if final not in parent:
                raise KeyError(final)
            parent[final] = mutation["value"]
        elif operation == "remove":
            del parent[final]
        elif operation == "add":
            if final in parent:
                raise ValueError(f"add target already exists: {final!r}")
            parent[final] = mutation["value"]
        elif operation == "merge":
            target = parent.get(final)
            value = mutation.get("value")
            if not isinstance(target, dict) or not isinstance(value, dict):
                raise TypeError("merge requires object target and value")
            target.update(copy.deepcopy(value))
        else:
            raise ValueError(f"unsupported operation {operation!r}")
    else:
        raise TypeError("mutation parent is not a container")


def schema_invalid(
    document: dict[str, Any], schema: dict[str, Any], label: str
) -> str | None:
    failures = list(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(document)
    )
    return f"{label}_schema_invalid" if failures else None


def get(value: Any, *parts: str) -> Any:
    current = value
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def all_false(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and bool(value)
        and all(item is False for item in value.values())
    )


def frame_value_bytes(name: str, value: str) -> bytes:
    if name == "nonce":
        return bytes.fromhex(value)
    if name.endswith("sha256"):
        prefix = "sha256:"
        if not value.startswith(prefix):
            raise ValueError(f"{name} is not a raw SHA-256 value")
        return bytes.fromhex(value[len(prefix) :])
    return value.encode("ascii")


def challenge_frame_fields(
    frame_profile: dict[str, Any], phase: str = "authentication"
) -> list[str]:
    """Resolve the ordered field list for one challenge phase.

    The v1 profile carries a single `ordered_fields` list because it has one
    phase. The ADR 0093 v2 profile carries a list per phase, and the caller
    must say which one it means rather than defaulting into whichever key
    happens to exist -- a silent fallback here would let a phase-two frame be
    built from phase-one fields and still verify.
    """
    binary = frame_profile["binary_frame"]
    if "ordered_fields" in binary:
        return binary["ordered_fields"]
    key = f"{phase}_phase_ordered_fields"
    if key not in binary:
        raise KeyError(f"frame profile declares no field list for phase {phase!r}")
    return binary[key]


def encode_challenge_frame(
    frame_profile: dict[str, Any],
    inputs: dict[str, str],
    phase: str = "authentication",
) -> bytes:
    binary = frame_profile["binary_frame"]
    fields = challenge_frame_fields(frame_profile, phase)
    result = bytearray(binary["magic_ascii"].encode("ascii"))
    result.extend(struct.pack(">H", len(fields)))
    for name in fields:
        input_name = "nonce_hex" if name == "nonce" else name
        name_raw = name.encode("ascii")
        value_raw = frame_value_bytes(name, inputs[input_name])
        result.extend(struct.pack(">H", len(name_raw)))
        result.extend(name_raw)
        result.extend(struct.pack(">I", len(value_raw)))
        result.extend(value_raw)
    return bytes(result)


def challenge_from_inputs(
    frame_profile: dict[str, Any],
    inputs: dict[str, str],
    phase: str = "authentication",
) -> tuple[str, bytes]:
    frame = encode_challenge_frame(frame_profile, inputs, phase)
    nonce = bytes.fromhex(inputs["nonce_hex"])
    challenge = nonce + hashlib.sha256(frame).digest()
    encoded = base64.urlsafe_b64encode(challenge).rstrip(b"=").decode("ascii")
    return encoded, frame


def challenge_nonce_hex(challenge_value: str) -> str:
    return challenge_octets(challenge_value)[:32].hex()


def challenge_octets(challenge_value: str) -> bytes:
    if not isinstance(challenge_value, str):
        raise ValueError("challenge value must be a base64url string")
    padded = challenge_value + ("=" * (-len(challenge_value) % 4))
    try:
        challenge = base64.b64decode(
            padded,
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, UnicodeError) as exc:
        raise ValueError("challenge value is not strict base64url") from exc
    if len(challenge) != 64:
        raise ValueError("challenge value must decode to 64 bytes")
    return challenge


def challenge_identifier(challenge_value: str) -> str:
    return raw_sha256(challenge_octets(challenge_value))


def chain_challenge_inputs(
    core: dict[str, Any],
    evidence: dict[str, Any],
    frame_profile: dict[str, Any],
    frame_evidence: dict[str, Any],
    observation: dict[str, Any],
    core_raw_sha256: str,
    nonce_hex: str | None = None,
) -> dict[str, str]:
    challenge = observation["challenge"]
    if nonce_hex is None:
        nonce_hex = challenge_nonce_hex(challenge["challenge_value"])
    return {
        "core_schema_resource_id": CORE_SCHEMA_ID,
        "core_raw_sha256": core_raw_sha256,
        "decision_schema_resource_id": core["decision_subject"][
            "schema_resource_id"
        ],
        "decision_raw_sha256": core["decision_subject"]["raw_sha256"],
        "candidate_schema_resource_id": core["candidate_subject"][
            "schema_resource_id"
        ],
        "candidate_raw_sha256": core["candidate_subject"]["raw_sha256"],
        "session_id": challenge["session_id"],
        "issued_at": challenge["issued_at"],
        "expires_at": challenge["expires_at"],
        "relying_party_id": challenge["relying_party_id"],
        "expected_origin": challenge["expected_origin"],
        "nonce_hex": nonce_hex,
    }


def evaluate_challenge_frame(
    frame_profile: dict[str, Any],
    frame_evidence: dict[str, Any],
    base_core: dict[str, Any],
    base_evidence: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    binary = frame_profile.get("binary_frame", {})
    construction = frame_profile.get("challenge_construction", {})
    relying_party_policy = frame_profile.get(
        "relying_party_origin_policy", {}
    )
    algorithm_policy = frame_profile.get("webauthn_algorithm_policy", {})
    vector = frame_evidence.get("synthetic_test_vector", {})
    proof = frame_profile.get("proof_boundary", {})
    evidence_proof = frame_evidence.get("proof_boundary", {})
    expected_fields = base_core.get("ceremony_request", {}).get(
        "challenge_commitment_fields"
    )
    if (
        frame_profile.get("schema_version") != "0.1.0"
        or frame_profile.get("artifact_class")
        != "human_decision_challenge_frame_candidate"
        or frame_profile.get("profile_id")
        != "odeya-human-decision-challenge-frame-v1-candidate"
        or frame_profile.get("profile_version") != "0.1.0"
        or frame_profile.get("candidate_status")
        != "unissued_architecture_candidate_not_a_real_ceremony"
        or frame_profile.get("issuance_disposition")
        != (
            "blocked_pending_cycle_free_confirmation_receipt_commitment_"
            "or_accepted_transaction_confirmation_trusted_path"
        )
        or frame_profile.get("purpose")
        != "nonrecursive_exact_byte_commitment_for_a_webauthn_authentication_challenge"
    ):
        errors.append("challenge_frame_profile_mismatch")
    if frame_evidence.get("schema_version") != "0.1.0" or (
        frame_evidence.get("artifact_class")
        != "human_decision_challenge_frame_candidate_evidence"
    ) or (
        frame_evidence.get("evidence_id")
        != "odeya.human-decision-challenge-frame-v1."
        "candidate-evidence.2026-07-19"
    ) or frame_evidence.get("version") != "0.1.0" or (
        frame_evidence.get("evidence_status")
        != "candidate_measurement_not_admitted"
    ):
        errors.append("challenge_frame_evidence_identity_or_status_mismatch")
    if (
        vector.get("fixture_class")
        != "deterministic_recomputation_vector_not_randomness_or_human_evidence"
    ):
        errors.append("challenge_frame_vector_classification_mismatch")
    if binary != {
        "magic_ascii": "ODEYA-HDA-CHALLENGE-FRAME-V1",
        "field_count_encoding": "unsigned_16_bit_big_endian",
        "field_entry_encoding": (
            "name_length_u16be_then_ascii_name_then_"
            "value_length_u32be_then_value"
        ),
        "text_value_encoding": "ascii_exact_bytes_no_normalization",
        "digest_value_encoding": (
            "32_raw_octets_decoded_from_lowercase_sha256_colon_hex"
        ),
        "nonce_value_encoding": "32_raw_octets_decoded_from_lowercase_hex",
        "ordered_fields": expected_fields,
    } or construction != {
        "minimum_fresh_random_bits": 256,
        "nonce_bytes": 32,
        "commitment_algorithm": "sha-256",
        "commitment_input": "exact_binary_frame",
        "challenge_octets": "nonce_32_octets_then_commitment_32_octets",
        "challenge_bytes": 64,
        "challenge_id": (
            "sha256_colon_lowercase_hex_of_exact_challenge_octets"
        ),
        "webauthn_encoding": "base64url_without_padding",
        "webauthn_encoded_length": 86,
        "generator": "independent_verifier_or_relying_party",
        "single_use_required": True,
        "maximum_lifetime_seconds": 300,
        "validity_interval": (
            "half_open_issued_at_inclusive_expires_at_exclusive"
        ),
        "client_generated_challenge_allowed": False,
    }:
        errors.append("challenge_frame_encoding_contract_mismatch")
    if relying_party_policy != {
        "policy_status": "candidate_unissued",
        "allowed_relying_party_id": "odeya.danielwahnich.dev",
        "allowed_origin": "https://odeya.danielwahnich.dev",
        "origin_host_must_equal_relying_party_id": True,
        "nondefault_port_allowed": False,
        "alternate_relying_party_or_origin_allowed": False,
    }:
        errors.append("challenge_frame_relying_party_origin_policy_mismatch")
    if algorithm_policy != {
        "policy_status": "candidate_unissued",
        "credential_public_key_algorithm": -7,
        "cose_algorithm_name": "ES256",
        "algorithm_substitution_allowed": False,
        "algorithm_match_must_be_independently_verified": True,
    }:
        errors.append("challenge_frame_algorithm_policy_mismatch")
    if any(
        "material" in field
        for field in binary.get("ordered_fields", [])
        if isinstance(field, str)
    ):
        errors.append("challenge_frame_material_digest_forbidden")
    disk_profile_raw = CHALLENGE_FRAME.read_bytes()
    disk_core_raw = CORE_FIXTURE.read_bytes()
    profile_raw = render(frame_profile)
    profile_binding = frame_evidence.get("profile_binding", {})
    core_binding = frame_evidence.get("core_fixture_binding", {})
    request_profile = get(
        base_core, "ceremony_request", "challenge_framing_profile"
    )
    if (
        profile_binding.get("path")
        != "architecture/human-decision-challenge-frame-v1-candidate.json"
        or profile_binding.get("profile_id") != frame_profile.get("profile_id")
        or profile_binding.get("profile_version")
        != frame_profile.get("profile_version")
        or profile_binding.get("raw_sha256") != raw_sha256(disk_profile_raw)
        or profile_binding.get("byte_count") != len(disk_profile_raw)
        or request_profile != {
            "profile_id": frame_profile.get("profile_id"),
            "profile_version": frame_profile.get("profile_version"),
            "raw_sha256": raw_sha256(disk_profile_raw),
            "byte_count": len(disk_profile_raw),
            "candidate_status": frame_profile.get("candidate_status"),
        }
    ):
        errors.append("challenge_frame_profile_raw_binding_mismatch")
    if profile_raw != disk_profile_raw:
        errors.append("challenge_frame_profile_document_bytes_mismatch")
    if (
        core_binding.get("path")
        != "tests/architecture-schema/fixtures/"
        "human-decision-assurance-core.valid.json"
        or core_binding.get("schema_resource_id") != CORE_SCHEMA_ID
        or core_binding.get("raw_sha256") != raw_sha256(disk_core_raw)
        or core_binding.get("byte_count") != len(disk_core_raw)
    ):
        errors.append("challenge_frame_core_raw_binding_mismatch")
    try:
        encoded, raw_frame = challenge_from_inputs(
            frame_profile, vector["inputs"]
        )
    except (KeyError, TypeError, ValueError, UnicodeError, struct.error):
        errors.append("challenge_frame_vector_unrecomputable")
    else:
        if (
            vector.get("frame_byte_count") != len(raw_frame)
            or vector.get("frame_raw_sha256") != raw_sha256(raw_frame)
            or vector.get("commitment_hex")
            != hashlib.sha256(raw_frame).hexdigest()
            or vector.get("challenge_base64url") != encoded
            or vector.get("challenge_id") != challenge_identifier(encoded)
        ):
            errors.append("challenge_frame_vector_mismatch")
        inputs = vector.get("inputs", {})
        challenge = get(base_evidence, "participant_observations")
        challenge = (
            challenge[0].get("challenge", {})
            if isinstance(challenge, list) and challenge
            else {}
        )
        expected_inputs = {
            "core_schema_resource_id": CORE_SCHEMA_ID,
            "core_raw_sha256": raw_sha256(disk_core_raw),
            "decision_schema_resource_id": get(
                base_core, "decision_subject", "schema_resource_id"
            ),
            "decision_raw_sha256": get(
                base_core, "decision_subject", "raw_sha256"
            ),
            "candidate_schema_resource_id": get(
                base_core, "candidate_subject", "schema_resource_id"
            ),
            "candidate_raw_sha256": get(
                base_core, "candidate_subject", "raw_sha256"
            ),
            "session_id": get(base_core, "ceremony_request", "session_id"),
            "issued_at": challenge.get("issued_at"),
            "expires_at": challenge.get("expires_at"),
            "relying_party_id": get(
                base_core, "ceremony_request", "relying_party_id"
            ),
            "expected_origin": get(
                base_core, "ceremony_request", "expected_origin"
            ),
            "nonce_hex": inputs.get("nonce_hex"),
        }
        if inputs != expected_inputs:
            errors.append("challenge_frame_vector_subject_mismatch")
        try:
            nonce = bytes.fromhex(inputs.get("nonce_hex", ""))
        except (TypeError, ValueError):
            nonce = b""
        issued = parse_time(inputs.get("issued_at"))
        expires = parse_time(inputs.get("expires_at"))
        if (
            len(nonce) != 32
            or issued is None
            or expires is None
            or expires <= issued
            or (expires - issued).total_seconds() > 300
        ):
            errors.append("challenge_frame_nonce_or_lifetime_invalid")
    if set(frame_profile) != {
        "schema_version",
        "artifact_class",
        "profile_id",
        "profile_version",
        "candidate_status",
        "issuance_disposition",
        "purpose",
        "binary_frame",
        "challenge_construction",
        "relying_party_origin_policy",
        "webauthn_algorithm_policy",
        "proof_boundary",
    } or set(frame_evidence) != {
        "schema_version",
        "artifact_class",
        "evidence_id",
        "version",
        "evidence_status",
        "profile_binding",
        "core_fixture_binding",
        "synthetic_test_vector",
        "proof_boundary",
    }:
        errors.append("challenge_frame_artifact_shape_mismatch")
    if (
        set(proof)
        != {
            "profile_issued",
            "relying_party_origin_policy_issued",
            "webauthn_algorithm_policy_issued",
            "confirmation_receipt_digest_committed",
            (
                "confirmation_gesture_and_authenticator_actor_"
                "cryptographically_co_bound"
            ),
            "challenge_proves_review_or_comprehension",
            "challenge_grants_authority",
            "gate_a_accepted",
            "runtime_authorized",
        }
        or set(evidence_proof)
        != {
            "profile_issued",
            "relying_party_origin_policy_issued",
            "webauthn_algorithm_policy_issued",
            "test_vector_proves_fresh_randomness",
            "test_vector_is_authentication_evidence",
            "test_vector_is_human_decision_evidence",
            "challenge_proves_review_or_comprehension",
            "challenge_grants_authority",
            "gate_a_accepted",
            "runtime_authorized",
        }
        or not all_false(proof)
        or not all_false(evidence_proof)
    ):
        errors.append("challenge_frame_claim_boundary_escalated")
    return unique_errors(errors)


def rebind_chain(
    candidates: dict[str, dict[str, Any]],
    mode: str,
    sync: str,
    nonce_hex: str | None = None,
) -> None:
    core = candidates["core"]
    evidence = candidates["evidence"]
    seal = candidates["seal"]
    frame_profile = candidates["frame"]
    frame_evidence = candidates["frame_evidence"]
    if mode not in {
        "none",
        "all",
        "evidence_to_seal",
        "fail_closed",
        "bindings_only",
    }:
        raise ValueError(f"unknown rebind mode {mode!r}")
    if sync not in {"none", "fresh_confirmation"}:
        raise ValueError(f"unknown synchronization mode {sync!r}")
    if mode == "all":
        core_digest, core_bytes = raw_binding(core)
        evidence_binding = evidence["core_binding"]
        evidence_binding["raw_sha256"] = core_digest
        evidence_binding["byte_count"] = core_bytes
        seal_binding = seal["core_binding"]
        seal_binding["raw_sha256"] = core_digest
        seal_binding["byte_count"] = core_bytes
        for observation in evidence["participant_observations"]:
            challenge = observation["challenge"]
            challenge["bound_core_schema_resource_id"] = CORE_SCHEMA_ID
            challenge["bound_core_raw_sha256"] = core_digest
            challenge["bound_decision_schema_resource_id"] = core[
                "decision_subject"
            ]["schema_resource_id"]
            challenge["bound_decision_raw_sha256"] = core["decision_subject"][
                "raw_sha256"
            ]
            challenge["bound_candidate_schema_resource_id"] = core[
                "candidate_subject"
            ]["schema_resource_id"]
            challenge["bound_candidate_raw_sha256"] = core[
                "candidate_subject"
            ]["raw_sha256"]
            challenge_value = challenge_from_inputs(
                frame_profile,
                chain_challenge_inputs(
                    core,
                    evidence,
                    frame_profile,
                    frame_evidence,
                    observation,
                    core_digest,
                    nonce_hex,
                ),
            )[0]
            challenge["challenge_value"] = challenge_value
            challenge["challenge_id"] = challenge_identifier(challenge_value)
            controlled_time = observation["controlled_time"]
            controlled_time["bound_challenge_id"] = challenge["challenge_id"]
            controlled_time["observed_challenge_consumed_at"] = challenge[
                "consumed_at"
            ]
    if sync == "fresh_confirmation":
        if mode != "all":
            raise ValueError(
                "fresh_confirmation requires a complete chain rebind"
            )
        for observation in evidence["participant_observations"]:
            challenge = observation["challenge"]
            confirmation = observation["decision_confirmation"]
            confirmation["assurance_id"] = core["assurance_id"]
            confirmation["bound_core_raw_sha256"] = raw_binding(core)[0]
            confirmation["session_id"] = challenge["session_id"]
            confirmation["challenge_request_id"] = challenge[
                "challenge_request_id"
            ]
            confirmation["bound_challenge_id"] = challenge["challenge_id"]
            confirmation["relying_party_id"] = challenge["relying_party_id"]
            confirmation["expected_origin"] = challenge["expected_origin"]
            confirmation["bound_decision_raw_sha256"] = core[
                "decision_subject"
            ]["raw_sha256"]
            confirmation["bound_candidate_raw_sha256"] = core[
                "candidate_subject"
            ]["raw_sha256"]
            confirmation_refs = confirmation.get("evidence_refs", [])
            artifact_by_id = {
                item.get("artifact_id"): item
                for item in evidence.get("ordered_evidence_set", [])
                if isinstance(item, dict)
            }
            if len(confirmation_refs) == 1:
                artifact = artifact_by_id.get(confirmation_refs[0], {})
                if artifact.get("role") == (
                    "sanitized_exact_material_presentation_and_"
                    "decision_confirmation_receipt"
                ):
                    confirmation["gesture_id"] = artifact.get("raw_sha256")
    if mode in {
        "all",
        "evidence_to_seal",
        "fail_closed",
        "bindings_only",
    }:
        evidence_digest, evidence_bytes = raw_binding(evidence)
        binding = seal["ordered_evidence_bindings"][0]
        binding["raw_sha256"] = evidence_digest
        binding["byte_count"] = evidence_bytes
    if mode == "all":
        seal["quorum_evaluation"]["required_principal_count"] = get(
            core, "authority_context", "quorum_rule", "required_principal_count"
        )
    if mode in {"all", "evidence_to_seal", "fail_closed"}:
        recompute_fail_closed_seal(evidence, seal)


def combine_statuses(values: list[Any]) -> str:
    if any(value == "contradicted" for value in values):
        return "contradicted"
    if any(value not in {SUPPORTED} for value in values):
        return "unknown"
    return SUPPORTED


def derive_participant_eligibility(
    observation: dict[str, Any], sanitation: str
) -> dict[str, Any]:
    """Derive domains, categorical failures, and disposition exactly once."""
    challenge = observation.get("challenge", {})
    confirmation = observation.get("decision_confirmation", {})
    authentication = observation.get("authentication", {})
    identity = observation.get("identity_and_authenticator_binding", {})
    custody = observation.get("custody", {})
    delegation = observation.get("delegation_and_effective_control", {})
    controlled_time = observation.get("controlled_time", {})
    verifier = observation.get("verification_observer", {})
    challenge_status = combine_statuses(
        [
            challenge.get(field)
            for field in (
                "generation",
                "fresh_randomness",
                "framing",
                "core_binding",
                "decision_binding",
                "candidate_binding",
                "decision_artifact_presentation",
                "candidate_artifact_presentation",
                "assertion_match",
                "consumption_time_observation",
                "atomic_assertion_acceptance_and_consumption",
            )
        ]
    )
    categorical_failures: list[str] = []
    if challenge.get("consumption_state") == "replayed":
        categorical_failures.append(
            "challenge_consumption_state_fresh_consumed_once"
        )
        challenge_status = "contradicted"
    elif challenge.get("consumption_state") != "fresh_consumed_once":
        challenge_status = "unknown"
    if challenge.get("prior_consumption_count") != 0:
        categorical_failures.append("challenge_not_previously_consumed")
        challenge_status = "contradicted"
    if challenge.get("result_consumption_count") != 1:
        categorical_failures.append("challenge_consumed_exactly_once")
        challenge_status = "contradicted"
    if (
        challenge.get("assertion_acceptance_atomic_action_id")
        != challenge.get("consumption_atomic_action_id")
    ):
        categorical_failures.append(
            "assertion_acceptance_and_consumption_atomic_action_equal"
        )
        challenge_status = "contradicted"
    confirmation_status = combine_statuses(
        [
            confirmation.get("gesture_status"),
            confirmation.get(
                "exact_decision_and_candidate_bindings_presented"
            ),
        ]
    )
    confirmation_invalid = False
    if confirmation.get("initiator_class") == "agent_model_or_tool_initiated":
        categorical_failures.append(
            "decision_confirmation_human_initiated"
        )
        confirmation_invalid = True
    if (
        confirmation.get("initiated_by_principal_id")
        != observation.get("principal_id")
    ):
        categorical_failures.append(
            "decision_confirmation_principal_matches_observation"
        )
        confirmation_invalid = True
    if confirmation.get("separate_from_authenticator_gesture") is False:
        categorical_failures.append(
            "decision_confirmation_separate_from_authenticator_gesture"
        )
        confirmation_invalid = True
    if confirmation_invalid:
        confirmation_status = "contradicted"
    elif (
        confirmation.get("initiator_class") != "human_initiated"
        or confirmation.get("separate_from_authenticator_gesture") is not True
    ):
        confirmation_status = "unknown"
    authentication_status = combine_statuses(
        [
            authentication.get(field)
            for field in (
                "client_data_type_match",
                "credential_public_key_binding",
                "algorithm_profile_match",
                "signature_verification",
                "authentication_intent",
                "phishing_resistance",
                "user_presence",
                "user_verification",
                "challenge_match",
                "origin_match",
                "relying_party_id_hash_match",
                "top_origin_match",
            )
        ]
    )
    cross_origin = authentication.get("cross_origin_disposition")
    top_origin = authentication.get("top_origin_match")
    if cross_origin in {
        "approved_cross_origin_profile_supported",
        "contradicted",
    }:
        categorical_failures.append(
            "same_origin_candidate_context_supported"
        )
        authentication_status = "contradicted"
    elif cross_origin == "same_origin_supported" and top_origin != SUPPORTED:
        authentication_status = "unknown"
    elif cross_origin not in {"same_origin_supported", "unknown", None}:
        categorical_failures.append(
            "same_origin_candidate_context_supported"
        )
        authentication_status = "contradicted"
    elif (
        cross_origin == "unknown"
        or authentication.get("backup_eligibility") == "unknown"
        or authentication.get("backup_state") == "unknown"
        or authentication.get("signature_counter_disposition")
        in {"unsupported", "unknown", None}
    ):
        authentication_status = "unknown"
    if (
        authentication.get("signature_counter_disposition")
        == "clone_risk_signal"
    ):
        categorical_failures.append(
            "no_authenticator_clone_risk_signal"
        )
        authentication_status = "contradicted"
    identity_status = combine_statuses(
        [
            identity.get("identity_proofing"),
            identity.get("principal_authenticator_binding"),
        ]
    )
    custody_status = combine_statuses(
        [
            custody.get(field)
            for field in (
                "authenticator_custody",
                "private_key_nonexportability",
                "agent_model_tool_signing_exclusion",
                "unattended_invocation_exclusion",
                "human_initiated_remote_operation",
                "exclusive_session_control",
                "shared_authenticator_absence",
                "sync_and_recovery_exposure_accounted",
            )
        ]
    )
    delegation_status = combine_statuses(
        [delegation.get("observation_status")]
    )
    if delegation.get("shared_control_principal_ids"):
        categorical_failures.append(
            "no_shared_effective_control_principals"
        )
        delegation_status = "contradicted"
    verifier_status = combine_statuses([verifier.get("observation_status")])
    if verifier.get("relation_to_decision_principal") in {
        "same_principal",
        "author_correlated",
    }:
        categorical_failures.append(
            "verifier_distinct_principal_and_effective_control"
        )
        verifier_status = "contradicted"
    elif (
        verifier.get("relation_to_decision_principal")
        != "distinct_principal_and_effective_control"
    ):
        verifier_status = "unknown"
    domains = {
        "exact_core_and_evidence_binding": SUPPORTED,
        "challenge_and_replay": challenge_status,
        "decision_confirmation": confirmation_status,
        "authentication": authentication_status,
        "identity_and_authenticator_binding": identity_status,
        "custody": custody_status,
        "delegation_objections_conflicts": delegation_status,
        "controlled_time": combine_statuses(
            [
                controlled_time.get("time_observation"),
                controlled_time.get(
                    "challenge_consumption_time_observation"
                ),
            ]
        ),
        "sanitation": sanitation,
        "_verifier": verifier_status,
    }
    required_domain_values = [
        value for key, value in domains.items() if key != "_verifier"
    ]
    if (
        categorical_failures
        or "contradicted" in required_domain_values
        or verifier_status == "contradicted"
    ):
        disposition = "invalid"
    elif (
        any(value != SUPPORTED for value in required_domain_values)
        or verifier_status != SUPPORTED
    ):
        disposition = "indeterminate"
    else:
        disposition = "eligible"
    return {
        "domains": domains,
        "categorical_failures": sorted(set(categorical_failures)),
        "disposition": disposition,
    }
def recompute_fail_closed_seal(
    evidence: dict[str, Any], seal: dict[str, Any]
) -> None:
    sanitation = (
        SUPPORTED
        if all(
            item.get("sanitization_status") == SUPPORTED
            for item in evidence.get("ordered_evidence_set", [])
        )
        and evidence.get("forbidden_content", {}).get(
            "sanitization_verification"
        )
        == SUPPORTED
        else "unknown"
    )
    determinations = {
        item.get("principal_id"): item
        for item in seal.get("participant_determinations", [])
    }
    dispositions: list[str] = []
    for observation in evidence.get("participant_observations", []):
        principal_id = observation.get("principal_id")
        determination = determinations.get(principal_id)
        if not isinstance(determination, dict):
            continue
        evaluation = derive_participant_eligibility(
            observation, sanitation
        )
        domains = evaluation["domains"]
        for field, value in domains.items():
            if field != "_verifier":
                determination[field] = value
        relation = get(
            observation,
            "verification_observer",
            "relation_to_decision_principal",
        )
        determination["verifier_relation"] = relation
        observed = evaluation["disposition"]
        determination["disposition"] = observed
        dispositions.append(observed)
    eligible = [
        item
        for item in seal.get("participant_determinations", [])
        if item.get("disposition") == "eligible"
    ]
    quorum = seal["quorum_evaluation"]
    quorum["eligible_principal_ids"] = [
        item["principal_id"] for item in eligible
    ]
    quorum["eligible_effective_control_group_ids"] = [
        item["effective_control_group_id"] for item in eligible
    ]
    quorum["eligible_authenticator_binding_refs"] = [
        item["authenticator_binding_ref"] for item in eligible
    ]
    if any(item in {"invalid", "contradicted"} for item in dispositions):
        result = "invalid"
    elif len(eligible) < quorum.get("required_principal_count", 1):
        result = "indeterminate"
    else:
        result = "supported"
    quorum["result"] = result
    entry = seal["decision_entry"]
    assurance = "eligible" if result == "supported" else result
    entry["assurance_disposition"] = assurance
    allowed = assurance == "eligible"
    entry["policy_entry"] = (
        "may_enter_assured_decision_assembly_only" if allowed else "blocked"
    )
    entry["candidate_policy_evaluation_result"] = (
        "not_evaluated" if allowed else "blocked"
    )


def evaluate_chain(
    core: dict[str, Any],
    evidence: dict[str, Any],
    seal: dict[str, Any],
    frame_profile: dict[str, Any],
    frame_evidence: dict[str, Any],
    base_core: dict[str, Any],
    base_evidence: dict[str, Any],
    *,
    core_raw: bytes,
    evidence_raw: bytes,
    ruleset_candidate: dict[str, Any],
    ruleset_raw: bytes,
    accept_recorded_negative_outcome: bool = False,
) -> list[str]:
    """Evaluate the exact singleton chain without inventing human authority."""
    errors: list[str] = []
    try:
        parsed_core = loads_object(core_raw, "supplied HumanDecisionAssuranceCore")
    except (DuplicateKey, UnicodeError, ValueError, json.JSONDecodeError):
        parsed_core = None
    if parsed_core != core:
        errors.append("core_raw_bytes_do_not_parse_to_supplied_object")
    try:
        parsed_evidence = loads_object(
            evidence_raw, "supplied HumanDecisionAssuranceEvidence"
        )
    except (DuplicateKey, UnicodeError, ValueError, json.JSONDecodeError):
        parsed_evidence = None
    if parsed_evidence != evidence:
        errors.append("evidence_raw_bytes_do_not_parse_to_supplied_object")
    try:
        parsed_ruleset = loads_object(
            ruleset_raw, "supplied individual eligibility ruleset candidate"
        )
    except (DuplicateKey, UnicodeError, ValueError, json.JSONDecodeError):
        parsed_ruleset = None
    if parsed_ruleset != ruleset_candidate:
        errors.append("ruleset_raw_bytes_do_not_parse_to_supplied_object")
    for code in (
        schema_invalid(core, load(CORE_SCHEMA), "core"),
        schema_invalid(evidence, load(EVIDENCE_SCHEMA), "evidence"),
        schema_invalid(seal, load(SEAL_SCHEMA), "seal"),
    ):
        if code:
            errors.append(code)
    errors.extend(
        evaluate_challenge_frame(
            frame_profile, frame_evidence, base_core, base_evidence
        )
    )

    if (
        core.get("assurance_id") != evidence.get("assurance_id")
        or core.get("assurance_id") != seal.get("assurance_id")
        or core.get("version") != evidence.get("version")
        or core.get("version") != seal.get("version")
    ):
        errors.append("assurance_identity_mismatch")
    assurance_artifact_ids = [
        core.get("artifact_id"),
        evidence.get("artifact_id"),
        seal.get("artifact_id"),
    ]
    if (
        any(not isinstance(item, str) for item in assurance_artifact_ids)
        or len(set(assurance_artifact_ids)) != 3
    ):
        errors.append("assurance_artifact_id_alias")
    if (
        core.get("candidate_status")
        != "unissued_candidate_not_human_authority"
        or evidence.get("candidate_status")
        != "unissued_candidate_not_human_authority"
        or seal.get("candidate_status")
        != "unissued_candidate_not_human_authority"
    ):
        errors.append("candidate_status_escalated")
    if evidence.get("evidence_class") != seal.get("evidence_class"):
        errors.append("evidence_class_mismatch")
    profile = core.get("profile_binding", {})
    if (
        profile.get("profile_status") != "candidate_unissued"
        or profile.get("canonical_profile_issued") is not False
        or profile.get("raw_byte_bootstrap_only") is not True
    ):
        errors.append("profile_issuance_or_bootstrap_boundary_escalated")

    singleton_scope = {
        "principal_act_cardinality": "exactly_one",
        "aggregate_quorum_evaluation": (
            "deferred_to_assured_decision_wrapper"
        ),
        "assured_decision_wrapper_identity_assigned": False,
    }
    authority = core.get("authority_context", {})
    if any(
        item != singleton_scope
        for item in (
            authority.get("assurance_scope"),
            evidence.get("assurance_scope"),
            seal.get("assurance_scope"),
        )
    ):
        errors.append("individual_assurance_scope_invalid")

    forbidden_core = {
        "self_digest",
        "canonical_digest",
        "assurance_ref",
        "evidence",
        "seal",
        "external_attestation",
    }
    if forbidden_core & set(core):
        errors.append("recursive_core_content_forbidden")

    decision_raw = DECISION_SOURCE.read_bytes()
    candidate_raw = CANDIDATE_SOURCE.read_bytes()
    decision_source = loads_object(decision_raw, str(DECISION_SOURCE))
    candidate_source = loads_object(candidate_raw, str(CANDIDATE_SOURCE))
    decision_subject = core.get("decision_subject", {})
    candidate_subject = core.get("candidate_subject", {})
    expected_decision_subject = {
        "artifact_id": decision_source.get("decision_id"),
        "schema_resource_id": (
            "urn:odeya:schema:operator-architecture-decision:0.4.0"
        ),
        "raw_sha256": raw_sha256(decision_raw),
        "byte_count": len(decision_raw),
        "media_type": "application/json",
        "decision_value_pointer": "/decision",
        "canonical_digest": None,
    }
    expected_candidate_subject = {
        "artifact_id": candidate_source.get("manifest_id"),
        "schema_resource_id": (
            "urn:odeya:schema:architecture-candidate-manifest:0.5.0"
        ),
        "raw_sha256": raw_sha256(candidate_raw),
        "byte_count": len(candidate_raw),
        "media_type": "application/json",
    }
    if decision_subject != expected_decision_subject:
        errors.append("decision_leaf_raw_binding_or_semantics_mismatch")
    if candidate_subject != expected_candidate_subject:
        errors.append("candidate_leaf_raw_binding_mismatch")
    try:
        pointer_value = pointer_get(
            decision_source,
            decision_subject.get("decision_value_pointer", "/missing"),
        )
    except (KeyError, IndexError, TypeError, ValueError):
        pointer_value = None
    if pointer_value != decision_source.get("decision"):
        errors.append("decision_value_pointer_resolution_mismatch")

    decision_candidate = decision_source.get("candidate", {})
    relationship = core.get("subject_relationship", {})
    expected_relationship = {
        "decision_candidate_manifest_id": decision_candidate.get(
            "manifest_id"
        ),
        "decision_candidate_version": decision_candidate.get("version"),
        "decision_candidate_manifest_raw_sha256": decision_candidate.get(
            "manifest_digest"
        ),
        "candidate_manifest_id": candidate_source.get("manifest_id"),
        "candidate_version": candidate_source.get("version"),
        "candidate_raw_sha256": raw_sha256(candidate_raw),
        "exact_id_version_and_raw_digest_match_required": True,
        "source_decision_schema_remains_semantic_authority": True,
    }
    if relationship != expected_relationship or (
        relationship.get("decision_candidate_manifest_id")
        != relationship.get("candidate_manifest_id")
        or relationship.get("decision_candidate_version")
        != relationship.get("candidate_version")
        or relationship.get("decision_candidate_manifest_raw_sha256")
        != relationship.get("candidate_raw_sha256")
    ):
        errors.append("decision_candidate_relationship_mismatch")

    materials = core.get("material_bindings", {})
    reviewed_decision = materials.get(
        "required_review_decision_artifact", {}
    )
    displayed_decision = materials.get(
        "required_display_decision_artifact", {}
    )
    reviewed_candidate = materials.get(
        "required_review_candidate_artifact", {}
    )
    displayed_candidate = materials.get(
        "required_display_candidate_artifact", {}
    )
    if (
        set(materials)
        != {
            "binding_kind",
            "required_review_decision_artifact",
            "required_display_decision_artifact",
            "required_review_candidate_artifact",
            "required_display_candidate_artifact",
            "required_display_and_review_exact_bindings_must_match",
        }
        or materials.get("binding_kind")
        != "ceremony_material_requirement_not_observation"
    ):
        errors.append("core_pre_ceremony_boundary_invalid")
    if (
        reviewed_decision != displayed_decision
        or reviewed_candidate != displayed_candidate
        or materials.get(
            "required_display_and_review_exact_bindings_must_match"
        )
        is not True
    ):
        errors.append("displayed_reviewed_material_mismatch")
    if (
        reviewed_decision != expected_decision_subject
        or displayed_decision != expected_decision_subject
        or reviewed_candidate != expected_candidate_subject
        or displayed_candidate != expected_candidate_subject
    ):
        errors.append("material_leaf_raw_binding_mismatch")

    principals = authority.get("decision_principals", [])
    verifier_ids = authority.get("verifier_principal_ids", [])
    if len(principals) != 1:
        errors.append("individual_assurance_principal_cardinality_invalid")
    if len(verifier_ids) != 1:
        errors.append("individual_assurance_verifier_cardinality_invalid")
    principal_ids = [
        item.get("principal_id")
        for item in principals
        if isinstance(item, dict)
    ]
    proposer = authority.get("proposer_principal_id")
    if len(principal_ids) != len(set(principal_ids)):
        errors.append("duplicate_decision_principal")
    if proposer in principal_ids:
        errors.append("proposer_decision_principal_collapse")
    if set(principal_ids) & set(verifier_ids):
        errors.append("decision_principal_verifier_collapse")
    if proposer in verifier_ids:
        errors.append("proposer_verifier_collapse")

    source_principal = get(decision_source, "operator", "principal_id")
    confirming_principal = principal_ids[0] if len(principal_ids) == 1 else None
    assurance_relation = core.get("assurance_relation", {})
    expected_principal_relation = (
        "same_declared_principal"
        if source_principal == confirming_principal
        else "distinct_declared_principals"
    )
    if assurance_relation != {
        "requested_relation_kind": (
            "later_ratification_of_exact_artifacts_not_original_authorship"
        ),
        "source_operator_principal_id": source_principal,
        "confirming_principal_id": confirming_principal,
        "source_and_confirming_principal_relationship": (
            expected_principal_relation
        ),
        "source_declared_decided_at": decision_source.get("decided_at"),
        "exact_decision_artifact_confirmation_required": True,
        "exact_candidate_artifact_confirmation_required": True,
        "source_decision_semantic_authority_transferred_to_core": False,
        "original_decision_authorship_assured": False,
        "original_decision_timestamp_assured": False,
        "confirmation_timestamp_must_be_assurance_timestamp": True,
        "consumer_currentness_must_be_recomputed": True,
    }:
        errors.append(
            "assurance_relation_authorship_or_semantics_boundary_invalid"
        )
    declared_source_decided = parse_time(
        assurance_relation.get("source_declared_decided_at")
    )
    core_created = parse_time(core.get("created_at"))
    if (
        declared_source_decided is None
        or core_created is None
        or declared_source_decided > core_created
    ):
        errors.append("declared_source_decision_time_order_invalid")

    quorum_rule = authority.get("quorum_rule", {})
    eligible_core = quorum_rule.get("eligible_principal_ids", [])
    if set(eligible_core) != set(principal_ids):
        errors.append("core_quorum_principal_membership_mismatch")
    if (
        quorum_rule.get("required_principal_count") != 1
        or eligible_core != principal_ids
    ):
        errors.append("core_quorum_count_unsatisfiable")
    for principal in principals:
        delegation = principal.get("delegation", {})
        if delegation.get("delegated") is False and (
            delegation.get("delegation_source_ref") is not None
            or delegation.get("depth") != 0
        ):
            errors.append("undeclared_delegation_context")
        if delegation.get("delegated") is True and (
            delegation.get("delegation_source_ref") is None
            or not isinstance(delegation.get("depth"), int)
            or delegation.get("depth") < 1
        ):
            errors.append("delegation_source_or_depth_missing")
        if principal.get("objections"):
            errors.append("unresolved_objection")
        if principal.get("conflicts"):
            errors.append("undisposed_conflict")

    request = core.get("ceremony_request", {})
    frame_raw = CHALLENGE_FRAME.read_bytes()
    if request.get("challenge_framing_profile") != {
        "profile_id": frame_profile.get("profile_id"),
        "profile_version": frame_profile.get("profile_version"),
        "raw_sha256": raw_sha256(frame_raw),
        "byte_count": len(frame_raw),
        "candidate_status": frame_profile.get("candidate_status"),
    }:
        errors.append("challenge_frame_profile_raw_binding_mismatch")
    if (
        request.get("client_generated_challenge_allowed") is not False
        or request.get("minimum_fresh_random_bits") != 256
        or request.get("single_use_required") is not True
        or request.get("separate_human_decision_gesture_required") is not True
        or request.get("challenge_validity_interval")
        != "half_open_issued_at_inclusive_expires_at_exclusive"
    ):
        errors.append("ceremony_request_weakened")
    if (
        request.get("relying_party_id")
        != get(
            frame_profile,
            "relying_party_origin_policy",
            "allowed_relying_party_id",
        )
        or request.get("expected_origin")
        != get(
            frame_profile,
            "relying_party_origin_policy",
            "allowed_origin",
        )
    ):
        errors.append("ceremony_request_relying_party_origin_policy_mismatch")
    if request.get("webauthn_algorithm_policy") != {
        "credential_public_key_algorithm": -7,
        "cose_algorithm_name": "ES256",
        "algorithm_substitution_allowed": False,
    }:
        errors.append("ceremony_request_algorithm_policy_mismatch")
    request_fields = request.get("challenge_commitment_fields", [])
    if (
        request_fields
        != get(frame_profile, "binary_frame", "ordered_fields")
        or any(
            "material" in field
            for field in request_fields
            if isinstance(field, str)
        )
    ):
        errors.append("ceremony_request_challenge_field_contract_mismatch")

    core_digest, core_bytes = raw_sha256(core_raw), len(core_raw)
    for binding in (
        evidence.get("core_binding", {}),
        seal.get("core_binding", {}),
    ):
        if (
            binding.get("schema_resource_id") != CORE_SCHEMA_ID
            or binding.get("raw_sha256") != core_digest
            or binding.get("byte_count") != core_bytes
            or binding.get("canonical_digest") is not None
        ):
            errors.append("core_raw_byte_binding_mismatch")
        if binding.get("artifact_id") != core.get("artifact_id"):
            errors.append("core_artifact_id_binding_mismatch")
    if (
        evidence.get("core_binding", {}).get("binding_is_external_to_core")
        is not True
    ):
        errors.append("core_external_binding_boundary_invalid")

    evidence_digest, evidence_bytes = raw_sha256(evidence_raw), len(evidence_raw)
    evidence_bindings = seal.get("ordered_evidence_bindings", [])
    if len(evidence_bindings) != 1:
        errors.append("individual_assurance_evidence_binding_cardinality_invalid")
    if len(evidence_bindings) != 1 or any(
        binding.get("schema_resource_id") != EVIDENCE_SCHEMA_ID
        or binding.get("raw_sha256") != evidence_digest
        or binding.get("byte_count") != evidence_bytes
        or binding.get("canonical_digest") is not None
        for binding in evidence_bindings
        if isinstance(binding, dict)
    ):
        errors.append("evidence_raw_byte_binding_mismatch")
    if any(
        binding.get("artifact_id") != evidence.get("artifact_id")
        for binding in evidence_bindings
        if isinstance(binding, dict)
    ):
        errors.append("evidence_artifact_id_binding_mismatch")

    if not all_false(
        {
            key: value
            for key, value in core.get("claim_boundary", {}).items()
            if key != "permitted_claim"
        }
    ):
        errors.append("core_claim_boundary_escalated")
    expected_evidence_proof_boundary = {
        "signature_alone_proves_human_control": False,
        "authentication_intent_is_decision_intent": False,
        "user_presence_proves_review": False,
        "user_verification_proves_natural_person_identity": False,
        "ceremony_proves_cognition": False,
        (
            "confirmation_gesture_and_authenticator_actor_"
            "cryptographically_co_bound"
        ): False,
        "backing_evidence_artifact_bytes_dereferenced": False,
        (
            "assignment_effective_control_or_verifier_independence_"
            "mechanically_established"
        ): False,
        "original_decision_authorship_proven": False,
        "source_decided_at_proven": False,
        "evidence_grants_authority": False,
    }
    if evidence.get("proof_boundary") != expected_evidence_proof_boundary:
        errors.append("evidence_claim_boundary_escalated")

    ruleset = seal.get("eligibility_ruleset", {})
    required_domains = [
        "exact_core_and_evidence_binding",
        "challenge_and_replay",
        "decision_confirmation",
        "authentication",
        "identity_and_authenticator_binding",
        "custody",
        "delegation_objections_conflicts",
        "controlled_time",
        "sanitation",
    ]
    required_categorical_conditions = [
        "challenge_consumption_state_fresh_consumed_once",
        "challenge_not_previously_consumed",
        "challenge_consumed_exactly_once",
        "assertion_acceptance_and_consumption_atomic_action_equal",
        "decision_confirmation_principal_matches_observation",
        "decision_confirmation_human_initiated",
        "decision_confirmation_separate_from_authenticator_gesture",
        "same_origin_candidate_context_supported",
        "no_authenticator_clone_risk_signal",
        "no_shared_effective_control_principals",
        "verifier_distinct_principal_and_effective_control",
    ]
    if ruleset_candidate != {
        "schema_version": "0.1.0",
        "artifact_class": (
            "human_decision_assurance_individual_eligibility_"
            "ruleset_candidate"
        ),
        "ruleset_id": (
            "urn:odeya:human-decision-assurance-eligibility:"
            "0.1.0-candidate"
        ),
        "ruleset_version": "0.1.0",
        "candidate_status": (
            "unissued_architecture_candidate_not_policy_authority"
        ),
        "scope": {
            "principal_act_cardinality": "exactly_one",
            "aggregate_quorum_evaluation": (
                "deferred_to_assured_decision_wrapper"
            ),
            "currentness_evaluation": (
                "deferred_to_assured_decision_wrapper"
            ),
            "authority_evaluation": (
                "deferred_to_assured_decision_wrapper"
            ),
        },
        "required_supported_domains": required_domains,
        "required_categorical_conditions": required_categorical_conditions,
        "disposition_law": {
            "integrity_precondition": (
                "schema_raw_binding_and_cross_record_identity_integrity_"
                "must_pass_before_embedded_disposition_evaluation"
            ),
            "integrity_precondition_failure": (
                "externally_invalid_chain_refused_before_embedded_"
                "disposition_evaluation"
            ),
            "required_observation_status_domain": [
                "supported",
                "contradicted",
                "unknown",
                "not_applicable",
            ],
            "required_categorical_condition_scope": (
                "evidence_internal_eligibility_conditions_after_"
                "integrity_precondition_passes"
            ),
            "required_categorical_condition_failure": "invalid",
            "contradicted_required_observation": "invalid",
            "missing_unknown_or_not_applicable_required_observation": (
                "indeterminate"
            ),
            "all_required_observations_supported_and_all_required_"
            "categorical_conditions_satisfied": "eligible",
            "precedence": [
                "invalid_if_any_required_observation_is_contradicted_"
                "or_any_required_categorical_condition_fails",
                "indeterminate_if_no_invalid_condition_exists_and_any_"
                "required_observation_is_missing_unknown_or_not_applicable",
                "eligible_only_if_every_required_observation_is_"
                "supported_and_every_required_categorical_condition_"
                "is_satisfied",
            ],
            "profile_authorized_not_applicable_domains": [],
            "eligible_compiles_to_approval": False,
            "eligible_satisfies_human_only_slot": False,
            "eligible_establishes_aggregate_quorum": False,
            "eligible_establishes_currentness": False,
            "eligible_grants_authority": False,
        },
        "proof_boundary": {
            "ruleset_issued": False,
            "independent_implementation_retained": False,
            "real_ceremony_verified": False,
            "consumer_migration_complete": False,
            "gate_a_accepted": False,
            "runtime_authorized": False,
        },
    }:
        errors.append("eligibility_ruleset_candidate_mismatch")
    if (
        ruleset.get("ruleset_id") != ruleset_candidate.get("ruleset_id")
        or ruleset.get("ruleset_version")
        != ruleset_candidate.get("ruleset_version")
        or ruleset.get("ruleset_path")
        != (
            "architecture/human-decision-assurance-individual-"
            "eligibility-ruleset-v1-candidate.json"
        )
        or ruleset.get("ruleset_raw_sha256") != raw_sha256(ruleset_raw)
        or ruleset.get("ruleset_byte_count") != len(ruleset_raw)
        or ruleset.get("status") != "candidate_unissued"
        or ruleset.get("missing_observation_disposition")
        != "indeterminate"
        or ruleset.get("contradicted_observation_disposition") != "invalid"
        or ruleset.get("eligibility_compiles_to_approval") is not False
    ):
        errors.append("eligibility_ruleset_binding_or_boundary_invalid")
    if any(
        determination.get("reason_codes")
        != ["synthetic_positive_control_all_candidate_requirements_supported"]
        or determination.get("limitations")
        != ["synthetic_fixture_not_a_human_decision"]
        for determination in seal.get("participant_determinations", [])
        if isinstance(determination, dict)
    ) or get(seal, "quorum_evaluation", "reason_codes") != [
        "synthetic_single_principal_individual_eligibility_supported"
    ] or get(seal, "decision_entry", "reason_codes") != [
        "synthetic_candidate_eligibility_only"
    ] or get(seal, "decision_entry", "limitations") != [
        "profile_unissued",
        "consumer_migration_incomplete",
        "no_real_human_ceremony",
        "aggregate_quorum_not_evaluated",
        "currentness_not_evaluated",
        "no_authority",
    ]:
        errors.append("seal_annotation_boundary_mismatch")

    observations = evidence.get("participant_observations", [])
    if len(observations) != 1:
        errors.append("individual_assurance_observation_cardinality_invalid")
    observation_ids = [
        item.get("principal_id")
        for item in observations
        if isinstance(item, dict)
    ]
    if (
        len(observation_ids) != len(set(observation_ids))
        or set(observation_ids) != set(principal_ids)
    ):
        errors.append("participant_observation_set_mismatch")

    artifact_rows = evidence.get("ordered_evidence_set", [])
    if len(artifact_rows) != len(EXPECTED_EVIDENCE_ROLES):
        errors.append("individual_assurance_evidence_role_cardinality_invalid")
    artifact_ids = [
        item.get("artifact_id")
        for item in artifact_rows
        if isinstance(item, dict)
    ]
    artifact_digests = [
        item.get("raw_sha256")
        for item in artifact_rows
        if isinstance(item, dict)
    ]
    artifact_roles = [
        item.get("role")
        for item in artifact_rows
        if isinstance(item, dict)
    ]
    artifact_by_id = {
        item.get("artifact_id"): item
        for item in artifact_rows
        if isinstance(item, dict)
    }
    if (
        len(artifact_ids) != len(set(artifact_ids))
        or len(artifact_digests) != len(set(artifact_digests))
    ):
        errors.append("ordered_evidence_set_not_unique")
    if artifact_roles != EXPECTED_EVIDENCE_ROLES:
        errors.append("referenced_evidence_artifact_role_mismatch")
    if any(
        item.get("byte_fidelity")
        != (
            "exact_unmodified_cryptographic_input"
            if item.get("role") in EXACT_CRYPTOGRAPHIC_INPUT_ROLES
            else "sanitized_derived_observation_record"
        )
        for item in artifact_rows
        if isinstance(item, dict)
    ):
        errors.append("ordered_evidence_byte_fidelity_mismatch")
    artifact_sanitation_supported = (
        len(artifact_rows) == len(EXPECTED_EVIDENCE_ROLES)
        and all(
            isinstance(item, dict)
            and item.get("sanitization_status") == SUPPORTED
            for item in artifact_rows
        )
    )
    if not artifact_sanitation_supported:
        errors.append("ordered_evidence_not_sanitized")
    root_sanitation_supported = (
        evidence.get("forbidden_content", {}).get(
            "sanitization_verification"
        )
        == SUPPORTED
    )
    sanitation_status = (
        SUPPORTED
        if artifact_sanitation_supported and root_sanitation_supported
        else "unknown"
    )

    expected_participant_dispositions: dict[str, str] = {}
    expected_participant_domains: dict[str, dict[str, str]] = {}
    categorical_failures_by_principal: dict[str, list[str]] = {}
    challenge_ids: list[Any] = []
    challenge_values: list[Any] = []
    for observation in observations:
        if not isinstance(observation, dict):
            continue
        principal_id = observation.get("principal_id")
        principal = next(
            (
                item
                for item in principals
                if isinstance(item, dict)
                and item.get("principal_id") == principal_id
            ),
            {},
        )
        challenge = observation.get("challenge", {})
        confirmation = observation.get("decision_confirmation", {})
        authentication = observation.get("authentication", {})
        identity = observation.get(
            "identity_and_authenticator_binding", {}
        )
        custody = observation.get("custody", {})
        delegation = observation.get(
            "delegation_and_effective_control", {}
        )
        controlled_time = observation.get("controlled_time", {})
        verifier = observation.get("verification_observer", {})
        challenge_ids.append(challenge.get("challenge_id"))
        challenge_values.append(challenge.get("challenge_value"))

        if (
            challenge.get("challenge_request_id")
            != request.get("challenge_request_id")
            or challenge.get("session_id") != request.get("session_id")
        ):
            errors.append("challenge_request_or_session_mismatch")
        if challenge.get("relying_party_id") != request.get(
            "relying_party_id"
        ):
            errors.append("relying_party_id_mismatch")
        if challenge.get("expected_origin") != request.get("expected_origin"):
            errors.append("expected_origin_mismatch")
        if (
            challenge.get("generator_role")
            != request.get("challenge_generator_role")
            or challenge.get("generator_principal_id") not in verifier_ids
            or challenge.get("generator_principal_id") in principal_ids
            or challenge.get("generator_principal_id") == proposer
        ):
            errors.append("challenge_generator_not_independent")
        if (
            challenge.get("framing_profile")
            != get(request, "challenge_framing_profile", "profile_id")
            or challenge.get("minimum_fresh_random_bits")
            != request.get("minimum_fresh_random_bits")
        ):
            errors.append("challenge_profile_or_entropy_mismatch")

        expected_challenge = None
        try:
            expected_challenge = challenge_from_inputs(
                frame_profile,
                chain_challenge_inputs(
                    core,
                    evidence,
                    frame_profile,
                    frame_evidence,
                    observation,
                    core_digest,
                ),
            )[0]
        except (
            KeyError,
            TypeError,
            ValueError,
            UnicodeError,
            struct.error,
        ):
            pass
        if challenge.get("challenge_value") != expected_challenge:
            errors.append("challenge_frame_commitment_mismatch")
        try:
            observed_challenge_id = challenge_identifier(
                challenge.get("challenge_value")
            )
        except (TypeError, ValueError, UnicodeError):
            observed_challenge_id = None
        if challenge.get("challenge_id") != observed_challenge_id:
            errors.append("challenge_identifier_mismatch")
        if (
            challenge.get("bound_core_schema_resource_id") != CORE_SCHEMA_ID
            or challenge.get("bound_core_raw_sha256") != core_digest
        ):
            errors.append("challenge_core_binding_mismatch")
        if (
            challenge.get("bound_decision_schema_resource_id")
            != decision_subject.get("schema_resource_id")
            or challenge.get("bound_decision_raw_sha256")
            != decision_subject.get("raw_sha256")
        ):
            errors.append("challenge_decision_binding_mismatch")
        if (
            challenge.get("bound_candidate_schema_resource_id")
            != candidate_subject.get("schema_resource_id")
            or challenge.get("bound_candidate_raw_sha256")
            != candidate_subject.get("raw_sha256")
        ):
            errors.append("challenge_candidate_binding_mismatch")
        if any(
            challenge.get(field) != SUPPORTED
            for field in (
                "generation",
                "fresh_randomness",
                "framing",
                "core_binding",
                "decision_binding",
                "candidate_binding",
                "decision_artifact_presentation",
                "candidate_artifact_presentation",
                "assertion_match",
                "consumption_time_observation",
                "atomic_assertion_acceptance_and_consumption",
            )
        ):
            errors.append("challenge_required_evidence_not_supported")
        if (
            challenge.get("consumption_state") != "fresh_consumed_once"
            or challenge.get("prior_consumption_count") != 0
            or challenge.get("result_consumption_count") != 1
        ):
            errors.append("challenge_replay_or_consumption_invalid")

        created = parse_time(core.get("created_at"))
        issued = parse_time(challenge.get("issued_at"))
        confirmed = parse_time(confirmation.get("confirmed_at"))
        assertion_received = parse_time(
            challenge.get("assertion_received_at")
        )
        consumed = parse_time(challenge.get("consumed_at"))
        expires = parse_time(challenge.get("expires_at"))
        observed_consumed = parse_time(
            controlled_time.get("observed_challenge_consumed_at")
        )
        observed = parse_time(controlled_time.get("observed_at"))
        collected = parse_time(evidence.get("collected_at"))
        sealed = parse_time(seal.get("sealed_at"))
        max_lifetime = request.get("maximum_challenge_lifetime_seconds")
        if created is None or issued is None or created > issued:
            errors.append("core_created_after_challenge_issue")
        if (
            issued is None
            or expires is None
            or expires <= issued
            or not isinstance(max_lifetime, int)
            or (expires - issued).total_seconds() > max_lifetime
        ):
            errors.append("challenge_time_window_invalid")
        if (
            issued is None
            or confirmed is None
            or expires is None
            or not (issued <= confirmed < expires)
        ):
            errors.append("decision_confirmation_stale_or_out_of_window")
        if (
            confirmed is None
            or assertion_received is None
            or consumed is None
            or expires is None
            or not (
                confirmed
                <= assertion_received
                <= consumed
                < expires
            )
        ):
            errors.append(
                "challenge_assertion_or_consumption_time_invalid"
            )
        if (
            controlled_time.get("bound_challenge_id")
            != challenge.get("challenge_id")
            or observed_consumed != consumed
            or controlled_time.get(
                "challenge_consumption_time_observation"
            )
            != SUPPORTED
        ):
            errors.append("controlled_time_challenge_binding_mismatch")
        if (
            consumed is None
            or observed is None
            or collected is None
            or sealed is None
            or not (consumed <= observed <= collected <= sealed)
        ):
            errors.append("controlled_time_order_invalid")

        if confirmation.get("gesture_status") != SUPPORTED:
            errors.append("decision_gesture_not_supported")
        if (
            confirmation.get("initiated_by_principal_id") != principal_id
            or confirmation.get("initiator_class") != "human_initiated"
        ):
            errors.append("decision_gesture_not_human_initiated")
        if (
            confirmation.get("separate_from_authenticator_gesture")
            is not True
        ):
            errors.append(
                "authenticator_gesture_reused_as_decision_gesture"
            )
        if (
            confirmation.get("confirmation_relation")
            != (
                "later_ratification_of_exact_artifacts_not_"
                "original_authorship"
            )
            or confirmation.get("exact_core_bytes_confirmed") is not True
            or confirmation.get(
                "exact_decision_and_candidate_bindings_presented"
            )
            != SUPPORTED
        ):
            errors.append("decision_confirmation_relation_invalid")
        if (
            confirmation.get("assurance_id") != core.get("assurance_id")
            or confirmation.get("bound_core_raw_sha256") != core_digest
            or confirmation.get("session_id") != challenge.get("session_id")
            or confirmation.get("challenge_request_id")
            != challenge.get("challenge_request_id")
            or confirmation.get("bound_challenge_id")
            != challenge.get("challenge_id")
            or confirmation.get("relying_party_id")
            != challenge.get("relying_party_id")
            or confirmation.get("expected_origin")
            != challenge.get("expected_origin")
            or confirmation.get("bound_decision_raw_sha256")
            != decision_subject.get("raw_sha256")
            or confirmation.get("bound_candidate_raw_sha256")
            != candidate_subject.get("raw_sha256")
        ):
            errors.append("decision_confirmation_context_binding_mismatch")
        confirmation_refs = confirmation.get("evidence_refs", [])
        if len(confirmation_refs) != 1:
            errors.append("decision_confirmation_evidence_missing")
        confirmation_artifact = (
            artifact_by_id.get(confirmation_refs[0], {})
            if len(confirmation_refs) == 1
            else {}
        )
        if (
            confirmation_artifact.get("role")
            != (
                "sanitized_exact_material_presentation_and_"
                "decision_confirmation_receipt"
            )
            or confirmation.get("gesture_id")
            != confirmation_artifact.get("raw_sha256")
        ):
            errors.append("decision_gesture_artifact_digest_mismatch")
        if (
            len(confirmation_refs) != 1
            or challenge.get("material_presentation_artifact_id")
            != confirmation_refs[0]
            or confirmation_artifact.get("role")
            != (
                "sanitized_exact_material_presentation_and_"
                "decision_confirmation_receipt"
            )
        ):
            errors.append(
                "material_presentation_confirmation_receipt_binding_mismatch"
            )

        algorithm_policy = request.get("webauthn_algorithm_policy", {})
        if (
            authentication.get("webauthn_operation")
            != request.get("webauthn_operation")
            or authentication.get("credential_binding_ref")
            != principal.get("authenticator_binding_ref")
        ):
            errors.append(
                "webauthn_operation_or_credential_binding_mismatch"
            )
        if (
            authentication.get("credential_public_key_algorithm")
            != algorithm_policy.get("credential_public_key_algorithm")
            or authentication.get("algorithm_policy_profile_id")
            != get(request, "challenge_framing_profile", "profile_id")
        ):
            errors.append("webauthn_algorithm_policy_mismatch")
        if any(
            authentication.get(field) != SUPPORTED
            for field in (
                "client_data_type_match",
                "credential_public_key_binding",
                "algorithm_profile_match",
                "signature_verification",
            )
        ):
            errors.append(
                "webauthn_cryptographic_evidence_not_supported"
            )
        if authentication.get("authentication_intent") != SUPPORTED:
            errors.append("authentication_intent_not_supported")
        if authentication.get("phishing_resistance") != SUPPORTED:
            errors.append("phishing_resistance_not_supported")
        if authentication.get("user_presence") != SUPPORTED:
            errors.append("user_presence_not_supported")
        if authentication.get("user_verification") != SUPPORTED:
            errors.append("user_verification_not_supported")
        if any(
            authentication.get(field) != SUPPORTED
            for field in (
                "challenge_match",
                "origin_match",
                "relying_party_id_hash_match",
            )
        ):
            errors.append("webauthn_context_binding_not_supported")
        cross_origin = authentication.get("cross_origin_disposition")
        top_origin = authentication.get("top_origin_match")
        if (
            cross_origin != "same_origin_supported"
            or top_origin != SUPPORTED
        ):
            errors.append("cross_origin_context_not_supported")
        if (
            authentication.get("backup_eligibility") == "unknown"
            or authentication.get("backup_state") == "unknown"
        ):
            errors.append("authenticator_backup_state_unknown")
        if authentication.get("signature_counter_disposition") in {
            "clone_risk_signal",
            "unsupported",
            "unknown",
            None,
        }:
            errors.append("signature_counter_risk_or_unknown")

        if (
            identity.get("identity_proofing_profile_ref")
            != principal.get("identity_proofing_profile_ref")
            or identity.get("identity_proofing") != SUPPORTED
        ):
            errors.append("identity_proofing_not_supported")
        if (
            identity.get("principal_authenticator_binding_ref")
            != principal.get("authenticator_binding_ref")
            or identity.get("principal_authenticator_binding") != SUPPORTED
        ):
            errors.append("principal_authenticator_binding_not_supported")
        if (
            identity.get("account_identifier_equals_natural_person")
            is not False
        ):
            errors.append(
                "account_identifier_promoted_to_natural_person"
            )

        if custody.get("authenticator_custody") != SUPPORTED:
            errors.append("authenticator_custody_not_supported")
        if custody.get("private_key_nonexportability") != SUPPORTED:
            errors.append("private_key_nonexportability_not_supported")
        if custody.get("agent_model_tool_signing_exclusion") != SUPPORTED:
            errors.append("agent_model_tool_signing_not_excluded")
        if custody.get("unattended_invocation_exclusion") != SUPPORTED:
            errors.append("unattended_invocation_not_excluded")
        if custody.get("human_initiated_remote_operation") != SUPPORTED:
            errors.append("human_remote_initiation_not_supported")
        if custody.get("exclusive_session_control") != SUPPORTED:
            errors.append("exclusive_session_control_not_supported")
        if custody.get("shared_authenticator_absence") != SUPPORTED:
            errors.append("shared_authenticator_not_excluded")
        if custody.get("sync_and_recovery_exposure_accounted") != SUPPORTED:
            errors.append("sync_recovery_exposure_not_accounted")

        expected_delegation = principal.get("delegation", {})
        if (
            delegation.get("delegation_source_ref")
            != expected_delegation.get("delegation_source_ref")
            or delegation.get("delegation_depth_observed")
            != expected_delegation.get("depth")
            or delegation.get("delegation_scope_codes_observed")
            != expected_delegation.get("scope_codes")
            or delegation.get("objections_observed")
            != principal.get("objections")
            or delegation.get("conflicts_observed")
            != principal.get("conflicts")
            or delegation.get("effective_control_group_id")
            != principal.get("effective_control_group_id")
            or delegation.get("observation_status") != SUPPORTED
        ):
            errors.append(
                "delegation_effective_control_context_mismatch"
            )
        if not delegation.get("evidence_refs"):
            errors.append(
                "delegation_effective_control_evidence_missing"
            )
        if delegation.get("shared_control_principal_ids"):
            errors.append("shared_effective_control_not_distinct")
        if delegation.get("objections_observed"):
            errors.append("observed_objection_unresolved")
        if delegation.get("conflicts_observed"):
            errors.append("observed_conflict_undisposed")

        if (
            controlled_time.get("time_observation") != SUPPORTED
            or controlled_time.get(
                "challenge_consumption_time_observation"
            )
            != SUPPORTED
        ):
            errors.append("controlled_time_not_supported")
        if (
            verifier.get("principal_id") not in verifier_ids
            or verifier.get("principal_id") == principal_id
            or verifier.get("principal_id") == proposer
            or verifier.get("relation_to_decision_principal")
            != "distinct_principal_and_effective_control"
            or verifier.get("observation_status") != SUPPORTED
        ):
            errors.append("independent_verifier_not_supported")

        required_artifact_ids = {
            challenge.get("challenge_lifecycle_artifact_id"),
            challenge.get("material_presentation_artifact_id"),
            authentication.get("client_data_json_artifact_id"),
            authentication.get("authenticator_data_artifact_id"),
            authentication.get("signature_artifact_id"),
            authentication.get("credential_public_key_artifact_id"),
            identity.get("identity_proofing_profile_ref"),
            identity.get("principal_authenticator_binding_ref"),
            controlled_time.get("controlled_time_source_ref"),
            *confirmation_refs,
            *delegation.get("evidence_refs", []),
            *custody.get("observation_refs", []),
            *verifier.get("evidence_refs", []),
        }
        if (
            None in required_artifact_ids
            or not required_artifact_ids.issubset(set(artifact_ids))
        ):
            errors.append("referenced_evidence_artifact_missing")
        expected_reference_roles = [
            (
                challenge.get("challenge_lifecycle_artifact_id"),
                "sanitized_challenge_lifecycle_and_atomic_consumption_record",
            ),
            (
                challenge.get("material_presentation_artifact_id"),
                "sanitized_exact_material_presentation_and_"
                "decision_confirmation_receipt",
            ),
            (
                authentication.get("client_data_json_artifact_id"),
                "exact_unmodified_client_data_json",
            ),
            (
                authentication.get("authenticator_data_artifact_id"),
                "exact_unmodified_authenticator_data",
            ),
            (
                authentication.get("signature_artifact_id"),
                "exact_unmodified_webauthn_signature",
            ),
            (
                authentication.get("credential_public_key_artifact_id"),
                "exact_unmodified_credential_public_key",
            ),
            (
                identity.get("identity_proofing_profile_ref"),
                "sanitized_identity_proofing_profile",
            ),
            (
                identity.get("principal_authenticator_binding_ref"),
                "sanitized_principal_authenticator_binding",
            ),
            (
                controlled_time.get("controlled_time_source_ref"),
                "sanitized_controlled_time_observation",
            ),
            *[
                (
                    reference,
                    "sanitized_exact_material_presentation_and_"
                    "decision_confirmation_receipt",
                )
                for reference in confirmation_refs
            ],
            *[
                (
                    reference,
                    "sanitized_delegation_effective_control_observation",
                )
                for reference in delegation.get("evidence_refs", [])
            ],
            *[
                (reference, "sanitized_custody_observation")
                for reference in custody.get("observation_refs", [])
            ],
            *[
                (reference, "sanitized_verifier_observation")
                for reference in verifier.get("evidence_refs", [])
            ],
        ]
        if any(
            reference in artifact_by_id
            and artifact_by_id[reference].get("role") != expected_role
            for reference, expected_role in expected_reference_roles
        ):
            errors.append("referenced_evidence_artifact_role_mismatch")
        lifecycle_artifact = artifact_by_id.get(
            challenge.get("challenge_lifecycle_artifact_id"), {}
        )
        if (
            lifecycle_artifact.get("role")
            != (
                "sanitized_challenge_lifecycle_and_"
                "atomic_consumption_record"
            )
        ):
            errors.append(
                "challenge_lifecycle_provenance_missing_or_wrong_role"
            )

        eligibility = derive_participant_eligibility(
            observation, sanitation_status
        )
        expected_participant_dispositions[principal_id] = eligibility[
            "disposition"
        ]
        expected_participant_domains[principal_id] = eligibility["domains"]
        categorical_failures_by_principal[principal_id] = eligibility[
            "categorical_failures"
        ]

    if (
        len(challenge_ids) != len(set(challenge_ids))
        or len(challenge_values) != len(set(challenge_values))
    ):
        errors.append("challenge_reuse_across_participants")

    forbidden = evidence.get("forbidden_content", {})
    forbidden_flags = {
        key: value
        for key, value in forbidden.items()
        if key != "sanitization_verification"
    }
    if not all_false(forbidden_flags):
        errors.append("forbidden_sensitive_content_retained")
    if forbidden.get("sanitization_verification") != SUPPORTED:
        errors.append("sanitization_verification_not_supported")

    determinations = seal.get("participant_determinations", [])
    if len(determinations) != 1:
        errors.append(
            "individual_assurance_determination_cardinality_invalid"
        )
    determination_ids = [
        item.get("principal_id")
        for item in determinations
        if isinstance(item, dict)
    ]
    if (
        len(determination_ids) != len(set(determination_ids))
        or set(determination_ids) != set(observation_ids)
    ):
        errors.append("participant_determination_set_mismatch")

    eligible_ids: list[str] = []
    eligible_controls: list[str] = []
    eligible_authenticators: list[str] = []
    any_invalid = False
    any_indeterminate = False
    for determination in determinations:
        if not isinstance(determination, dict):
            continue
        principal_id = determination.get("principal_id")
        principal = next(
            (
                item
                for item in principals
                if isinstance(item, dict)
                and item.get("principal_id") == principal_id
            ),
            {},
        )
        observation = next(
            (
                item
                for item in observations
                if isinstance(item, dict)
                and item.get("principal_id") == principal_id
            ),
            {},
        )
        expected = expected_participant_dispositions.get(
            principal_id, "indeterminate"
        )
        actual = determination.get("disposition")
        if expected == "invalid":
            any_invalid = True
            if actual not in {"invalid", "contradicted"}:
                if categorical_failures_by_principal.get(principal_id):
                    errors.append(
                        "categorical_failure_not_sealed_invalid"
                    )
                else:
                    errors.append("contradiction_not_sealed_invalid")
        elif expected == "indeterminate":
            any_indeterminate = True
            if actual != "indeterminate":
                errors.append("missing_evidence_not_sealed_indeterminate")
        elif actual != "eligible":
            errors.append("supported_evidence_not_sealed_eligible")
        domains = (
            "exact_core_and_evidence_binding",
            "challenge_and_replay",
            "decision_confirmation",
            "authentication",
            "identity_and_authenticator_binding",
            "custody",
            "delegation_objections_conflicts",
            "controlled_time",
            "sanitation",
        )
        expected_domains = expected_participant_domains.get(
            principal_id, {}
        )
        if any(
            determination.get(field) != expected_domains.get(field)
            for field in domains
        ):
            errors.append("participant_domain_derivation_mismatch")
        if actual == "eligible" and any(
            determination.get(field) != SUPPORTED for field in domains
        ):
            errors.append(
                "eligible_participant_has_non_supported_domain"
            )
        if (
            determination.get("effective_control_group_id")
            != principal.get("effective_control_group_id")
            or determination.get("authenticator_binding_ref")
            != principal.get("authenticator_binding_ref")
            or determination.get("verifier_principal_id")
            != get(observation, "verification_observer", "principal_id")
            or determination.get("verifier_relation")
            != get(
                observation,
                "verification_observer",
                "relation_to_decision_principal",
            )
        ):
            errors.append(
                "participant_determination_identity_mismatch"
            )
        if expected == "eligible" and actual == "eligible":
            eligible_ids.append(principal_id)
            eligible_controls.append(
                principal.get("effective_control_group_id")
            )
            eligible_authenticators.append(
                principal.get("authenticator_binding_ref")
            )

    quorum = seal.get("quorum_evaluation", {})
    if (
        quorum.get("evaluation_scope")
        != "single_individual_assurance_not_aggregate_quorum"
        or quorum.get("required_principal_count") != 1
        or quorum_rule.get("required_principal_count") != 1
    ):
        errors.append("aggregate_quorum_must_be_deferred_to_wrapper")
    if (
        set(quorum.get("eligible_principal_ids", []))
        != set(eligible_ids)
        or set(quorum.get("eligible_effective_control_group_ids", []))
        != set(eligible_controls)
        or set(quorum.get("eligible_authenticator_binding_refs", []))
        != set(eligible_authenticators)
    ):
        errors.append("quorum_eligible_set_mismatch")
    expected_result = (
        "invalid"
        if any_invalid
        else "indeterminate"
        if any_indeterminate or eligible_ids != principal_ids
        else "supported"
    )
    if quorum.get("result") != expected_result:
        errors.append("quorum_result_mismatch")
    if quorum.get("result") == "supported" and (
        quorum.get("eligible_principal_ids") != principal_ids
        or any(
            quorum.get(field) != SUPPORTED
            for field in (
                "distinct_principal_evaluation",
                "distinct_effective_control_evaluation",
                "distinct_authenticator_evaluation",
                "objection_disposition",
                "conflict_disposition",
            )
        )
    ):
        errors.append("supported_quorum_has_missing_prerequisite")

    decision_entry = seal.get("decision_entry", {})
    expected_assurance = (
        "eligible" if expected_result == "supported" else expected_result
    )
    if decision_entry.get("assurance_disposition") != expected_assurance:
        errors.append("decision_assurance_disposition_mismatch")
    if (
        decision_entry.get("policy_entry")
        != (
            "may_enter_assured_decision_assembly_only"
            if expected_assurance == "eligible"
            else "blocked"
        )
        or decision_entry.get("candidate_policy_evaluation_result")
        != (
            "not_evaluated"
            if expected_assurance == "eligible"
            else "blocked"
        )
    ):
        errors.append("candidate_policy_entry_fail_closed_mismatch")
    if (
        decision_entry.get("currentness_evaluation")
        != "deferred_to_consumer_policy_at_controlled_evaluation_time"
        or decision_entry.get("currentness_evaluated_at") is not None
        or decision_entry.get("source_expiry_evaluated") is not False
        or decision_entry.get(
            "withdrawal_revocation_contradiction_evaluated"
        )
        is not False
    ):
        errors.append("seal_currentness_or_policy_boundary_invalid")
    if (
        decision_entry.get("decision_value_copied_into_seal") is not False
        or decision_entry.get("decision_value_resolution")
        != (
            "resolve_exact_decision_subject_using_its_bound_json_pointer"
        )
        or decision_entry.get("eligibility_is_approval") is not False
        or decision_entry.get("consumer_authority_effective") is not False
    ):
        errors.append("eligibility_or_seal_promoted_to_authority")

    if "self_digest" in seal or "external_attestation" in seal:
        errors.append("recursive_seal_content_forbidden")
    seal_boundary = seal.get("claim_boundary", {})
    expected_seal_boundary = {
        "seal_self_digest_forbidden": True,
        "seal_contains_external_attestation": False,
        "profile_issued": False,
        "consumer_migration_complete": False,
        "accountable_review_complete": False,
        "real_human_ceremony_verified": False,
        (
            "confirmation_gesture_and_authenticator_actor_"
            "cryptographically_co_bound"
        ): False,
        "human_only_slot_satisfied": False,
        "aggregate_quorum_evaluated": False,
        "aggregate_quorum_authority_effective": False,
        "source_decision_semantics_interpreted": False,
        "currentness_evaluated": False,
        "independent_eligibility_recomputation_retained": False,
        "gate_a_accepted": False,
        "runtime_authorized": False,
        "external_effects_authorized": False,
    }
    if seal_boundary != expected_seal_boundary:
        errors.append("seal_claim_boundary_escalated")
    if (
        seal_boundary.get("aggregate_quorum_evaluated") is not False
        or seal_boundary.get("aggregate_quorum_authority_effective")
        is not False
    ):
        errors.append("aggregate_quorum_must_be_deferred_to_wrapper")
    outcome_consistency_errors = {
        "categorical_failure_not_sealed_invalid",
        "contradiction_not_sealed_invalid",
        "missing_evidence_not_sealed_indeterminate",
        "supported_evidence_not_sealed_eligible",
        "participant_domain_derivation_mismatch",
        "eligible_participant_has_non_supported_domain",
        "quorum_eligible_set_mismatch",
        "quorum_result_mismatch",
        "decision_assurance_disposition_mismatch",
        "candidate_policy_entry_fail_closed_mismatch",
    }
    if (
        accept_recorded_negative_outcome
        and expected_result in {"invalid", "indeterminate"}
        and not (set(errors) & outcome_consistency_errors)
    ):
        errors = [
            error
            for error in errors
            if error not in RECORDED_OUTCOME_DIAGNOSTICS
        ]
    return unique_errors(errors)


@functools.lru_cache(maxsize=None)
def git_bytes(*args: str) -> bytes:
    """Read immutable Git-addressed evidence once per checker process."""
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.decode("utf-8", errors="replace").strip()
        )
    return result.stdout


def pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def discovered_schema_pointers(
    document: dict[str, Any], markers: set[str]
) -> list[str]:
    found: set[str] = set()

    def visit(value: Any, tokens: list[str]) -> None:
        if isinstance(value, dict):
            properties = value.get("properties")
            if isinstance(properties, dict):
                for name, declaration in properties.items():
                    pointer = "/" + "/".join(
                        pointer_escape(item)
                        for item in [*tokens, "properties", name]
                    )
                    if name in markers:
                        found.add(pointer)
                    if (
                        name == "principal_type"
                        and isinstance(declaration, dict)
                        and (
                            declaration.get("const") == "human"
                            or (
                                isinstance(declaration.get("enum"), list)
                                and "human" in declaration["enum"]
                            )
                        )
                    ):
                        found.add(pointer)
            for key, item in value.items():
                visit(item, [*tokens, key])
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, [*tokens, str(index)])

    visit(document, [])
    return sorted(found)


def catalog_partition_errors(
    catalog: list[str], partition: dict[str, Any], groups: tuple[str, ...], label: str
) -> list[str]:
    errors: list[str] = []
    expected_contract = (
        {
            "catalog_path": "schemas/command-envelope.schema.json",
            "catalog_pointer": "/$defs/command_type/enum",
            "expected_count": 121,
            "classification_basis": (
                "conservative first-slice applicability partition; a "
                "policy-conditional producer still requires a runtime "
                "applicability rule before any H slot can be evaluated"
            ),
            "disjoint_union_complete": True,
        }
        if label == "command"
        else {
            "catalog_path": "schemas/research-event.schema.json",
            "catalog_pointer": "/properties/event_type/enum",
            "expected_count": 135,
            "classification_basis": (
                "persisted-fact counterpart of the conservative command "
                "applicability partition"
            ),
            "disjoint_union_complete": True,
        }
    )
    if set(partition) != {
        *expected_contract,
        *groups,
        "partition_counts",
    } or any(
        partition.get(key) != value
        for key, value in expected_contract.items()
    ) or (
        semantic_sha256(partition)
        != EXPECTED_CENSUS_SEMANTIC_SHA256[
            f"{label}_type_partition"
        ]
    ):
        errors.append(f"{label}_partition_contract_mismatch")
    lists = [partition.get(group, []) for group in groups]
    flattened = [item for group in lists for item in group]
    if (
        partition.get("expected_count") != len(catalog)
        or len(flattened) != len(catalog)
        or set(flattened) != set(catalog)
        or len(flattened) != len(set(flattened))
    ):
        errors.append(f"{label}_partition_not_exact_disjoint_union")
    for group in lists:
        if group != [item for item in catalog if item in set(group)]:
            errors.append(f"{label}_partition_source_order_mismatch")
    counts = partition.get("partition_counts", {})
    if set(counts) != set(groups) or any(
        counts.get(name) != len(partition.get(name, [])) for name in groups
    ):
        errors.append(f"{label}_partition_count_mismatch")
    return errors


def evaluate_census(
    census: dict[str, Any],
    current_schema_overrides: dict[str, bytes] | None = None,
    extra_current_schema_paths: list[str] | None = None,
    current_authority_matrix_override: bytes | None = None,
) -> list[str]:
    errors: list[str] = []
    current_schema_overrides = current_schema_overrides or {}
    extra_current_schema_paths = extra_current_schema_paths or []
    if set(census) != EXPECTED_CENSUS_TOP_LEVEL_KEYS:
        errors.append("census_identity_or_shape_mismatch")
    if (
        census.get("artifact_type") != "HumanDecisionAssuranceConsumerCensus"
        or census.get("artifact_id")
        != "urn:odeya:architecture:"
        "human-decision-assurance-consumer-census:2026-07-19:1"
        or census.get("version") != 1
        or census.get("status")
        != "candidate_complete_for_frozen_source_corpus_not_migrated"
        or census.get("as_of_date") != "2026-07-19"
    ):
        errors.append("census_identity_or_status_mismatch")
    subject = census.get("subject", {})
    if subject != EXPECTED_CENSUS_SUBJECT:
        errors.append("census_subject_binding_mismatch")
    if census.get("scope_boundary") != EXPECTED_CENSUS_SCOPE_BOUNDARY:
        errors.append("census_scope_boundary_mismatch")
    commit = subject.get("baseline_git_commit")
    tree = subject.get("baseline_git_tree")
    try:
        resolved_commit = git_bytes(
            "rev-parse", "--verify", f"{commit}^{{commit}}"
        ).decode("ascii").strip()
        resolved_tree = git_bytes(
            "rev-parse", "--verify", f"{commit}^{{tree}}"
        ).decode("ascii").strip()
        baseline_paths = [
            line
            for line in git_bytes(
                "ls-tree", "-r", "--name-only", commit, "schemas"
            )
            .decode("utf-8")
            .splitlines()
            if line.endswith(".schema.json")
        ]
        baseline_authority_matrix_raw = git_bytes(
            "show", f"{commit}:{subject.get('authority_matrix_ref')}"
        )
    except (RuntimeError, UnicodeError, AttributeError):
        errors.append("census_baseline_checkpoint_unresolvable")
        return unique_errors(errors)
    if resolved_commit != commit or resolved_tree != tree:
        errors.append("census_baseline_checkpoint_mismatch")
    if (
        raw_sha256(baseline_authority_matrix_raw)
        != subject.get("baseline_authority_matrix_raw_sha256")
        or len(baseline_authority_matrix_raw)
        != subject.get("baseline_authority_matrix_byte_count")
    ):
        errors.append("census_subject_binding_mismatch")
    try:
        current_authority_matrix_raw = (
            current_authority_matrix_override
            if current_authority_matrix_override is not None
            else (ROOT / subject.get("authority_matrix_ref")).read_bytes()
        )
    except (OSError, TypeError):
        current_authority_matrix_raw = b""
    if (
        raw_sha256(current_authority_matrix_raw)
        != subject.get("current_authority_matrix_raw_sha256")
        or len(current_authority_matrix_raw)
        != subject.get("current_authority_matrix_byte_count")
    ):
        errors.append("census_current_authority_matrix_drift")
    current_schema_paths = sorted(
        [
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "schemas").rglob("*.schema.json")
        ]
        + extra_current_schema_paths
    )
    if current_schema_paths != sorted(
        [*baseline_paths, *EXPECTED_CANDIDATE_SCHEMA_PATHS]
    ):
        errors.append("census_current_schema_union_or_baseline_drift")

    profile = census.get("pointer_discovery_profile", {})
    markers = profile.get("exact_property_markers", [])
    profile_shape_invalid = (
        not isinstance(markers, list)
        or len(markers) != len(set(markers))
        or profile.get("traversal")
        != "depth_first_over_every_json_object_and_array"
        or profile.get("json_pointer_escaping") != "RFC6901"
        or profile.get("deduplication") != "lexicographically_sorted_unique"
    )
    if profile_shape_invalid:
        errors.append("census_pointer_marker_profile_invalid")
        markers = []
    elif (
        semantic_sha256(profile)
        != EXPECTED_CENSUS_SEMANTIC_SHA256["pointer_discovery_profile"]
    ):
        errors.append("census_pointer_marker_profile_invalid")
    if (
        semantic_sha256(census.get("class_definitions"))
        != EXPECTED_CENSUS_SEMANTIC_SHA256["class_definitions"]
    ):
        errors.append("census_classification_profile_mismatch")
    marker_set = set(markers)
    baseline = census.get("baseline_schema_partition", {})
    rows = baseline.get("rows", [])
    expected_baseline_row_keys = {
        "path",
        "schema_id",
        "raw_sha256",
        "byte_length",
        "primary_class",
        "roles",
        "matching_pointers",
        "applicability",
        "migration_disposition",
        "current_assurance_ref_pointers",
        "consumer_migrated",
    }
    if (
        set(baseline)
        != {
            "expected_count",
            "partition_counts",
            "paths_unique",
            "schema_ids_are_bound_as_observed_not_asserted_globally_unique",
            "rows",
        }
        or baseline.get("paths_unique") is not True
        or baseline.get(
            "schema_ids_are_bound_as_observed_not_asserted_globally_unique"
        )
        is not True
        or not isinstance(rows, list)
        or any(
            not isinstance(row, dict)
            or set(row) != expected_baseline_row_keys
            for row in rows
        )
    ):
        errors.append("census_baseline_partition_mismatch")
        if not isinstance(rows, list):
            rows = []
    baseline_judgment_projection = [
        {
            key: get(row, key)
            for key in (
                "path",
                "primary_class",
                "roles",
                "applicability",
                "migration_disposition",
            )
        }
        for row in rows
    ]
    if (
        semantic_sha256(baseline_judgment_projection)
        != EXPECTED_CENSUS_SEMANTIC_SHA256[
            "baseline_judgment_projection"
        ]
    ):
        errors.append("census_baseline_classification_inventory_mismatch")
    paths = [row.get("path") for row in rows if isinstance(row, dict)]
    if (
        len(baseline_paths) != 112
        or baseline.get("expected_count") != 112
        or paths != baseline_paths
        or len(paths) != len(set(paths))
    ):
        errors.append("census_baseline_partition_mismatch")
    observed_classes: Counter[str] = Counter()
    baseline_documents: dict[str, dict[str, Any]] = {}
    for row in rows:
        path = row.get("path")
        try:
            raw = git_bytes("show", f"{commit}:{path}")
            document = loads_object(raw, f"{commit}:{path}")
            current_raw = current_schema_overrides.get(
                path, (ROOT / path).read_bytes()
            )
        except (RuntimeError, UnicodeError, ValueError, DuplicateKey, KeyError):
            errors.append("census_baseline_row_unrecomputable")
            continue
        except OSError:
            errors.append("census_current_schema_union_or_baseline_drift")
            continue
        if current_raw != raw:
            errors.append("census_current_schema_union_or_baseline_drift")
        baseline_documents[path] = document
        if (
            row.get("schema_id") != document.get("$id")
            or row.get("raw_sha256") != raw_sha256(raw)
            or row.get("byte_length") != len(raw)
        ):
            errors.append("census_baseline_row_binding_mismatch")
        if row.get("matching_pointers") != discovered_schema_pointers(
            document, marker_set
        ):
            errors.append("census_pointer_discovery_mismatch")
        if row.get("current_assurance_ref_pointers") != []:
            errors.append("census_existing_assurance_reference_fabricated")
        if row.get("consumer_migrated") is not False:
            errors.append("census_consumer_migration_fabricated")
        observed_classes[row.get("primary_class")] += 1
    expected_classes = {
        "direct_or_policy_conditional_assurance_subject": 19,
        "pending_operator_acceptance_consumer": 9,
        "transitive_or_transport_surface": 53,
        "non_authority_human_or_integrity_metadata": 17,
        "no_human_decision_assurance_surface": 14,
    }
    if (
        dict(observed_classes) != expected_classes
        or baseline.get("partition_counts") != expected_classes
    ):
        errors.append("census_primary_class_partition_mismatch")

    candidate = census.get("candidate_mechanism_schemas", {})
    candidate_rows = candidate.get("rows", [])
    candidate_paths = [row.get("path") for row in candidate_rows]
    expected_candidate_row_keys = {
        "path",
        "schema_id",
        "raw_sha256",
        "byte_length",
        "primary_class",
        "roles",
        "matching_pointers",
        "applicability",
        "migration_disposition",
        "consumer_migrated",
    }
    candidate_status_projection = [
        {
            key: get(row, key)
            for key in (
                "path",
                "primary_class",
                "roles",
                "applicability",
                "migration_disposition",
                "consumer_migrated",
            )
        }
        for row in candidate_rows
        if isinstance(row, dict)
    ]
    if (
        set(candidate)
        != {"expected_count", "all_unissued", "all_non_authoritative", "rows"}
        or candidate.get("expected_count") != 3
        or candidate.get("all_unissued") is not True
        or candidate.get("all_non_authoritative") is not True
        or not isinstance(candidate_rows, list)
        or any(
            not isinstance(row, dict)
            or set(row) != expected_candidate_row_keys
            for row in candidate_rows
        )
        or candidate_paths != EXPECTED_CANDIDATE_SCHEMA_PATHS
        or set(candidate_paths) & set(paths)
    ):
        errors.append("census_candidate_partition_mismatch")
    if (
        semantic_sha256(candidate_status_projection)
        != EXPECTED_CENSUS_SEMANTIC_SHA256["candidate_status_projection"]
    ):
        errors.append("census_candidate_status_escalated")
    for row in candidate_rows:
        path = row.get("path")
        try:
            raw = (ROOT / path).read_bytes()
            document = loads_object(raw, path)
        except (OSError, UnicodeError, ValueError, DuplicateKey, KeyError):
            errors.append("census_candidate_row_unrecomputable")
            continue
        if (
            row.get("schema_id") != document.get("$id")
            or row.get("raw_sha256") != raw_sha256(raw)
            or row.get("byte_length") != len(raw)
            or row.get("matching_pointers")
            != discovered_schema_pointers(document, marker_set)
        ):
            errors.append("census_candidate_row_binding_mismatch")
        if (
            row.get("primary_class")
            != "candidate_mechanism_not_baseline_consumer"
            or row.get("consumer_migrated") is not False
        ):
            errors.append("census_candidate_status_escalated")

    try:
        command_schema = baseline_documents[
            census["command_type_partition"]["catalog_path"]
        ]
        command_catalog = pointer_get(
            command_schema, census["command_type_partition"]["catalog_pointer"]
        )
        event_schema = baseline_documents[
            census["event_type_partition"]["catalog_path"]
        ]
        event_catalog = pointer_get(
            event_schema, census["event_type_partition"]["catalog_pointer"]
        )
    except (KeyError, TypeError, IndexError, ValueError):
        errors.append("census_command_event_catalog_unresolvable")
    else:
        errors.extend(
            catalog_partition_errors(
                command_catalog,
                census["command_type_partition"],
                (
                    "assurance_subject_or_policy_conditional_producers",
                    "prior_or_same_transaction_assurance_consumers",
                    "not_direct_human_decision_in_frozen_profile",
                ),
                "command",
            )
        )
        errors.extend(
            catalog_partition_errors(
                event_catalog,
                census["event_type_partition"],
                (
                    "human_decision_or_policy_conditional_facts",
                    "assurance_dependent_transitive_facts",
                    "not_direct_human_decision_in_frozen_profile",
                ),
                "event",
            )
        )

    missing_nodes = get(
        census, "missing_contract_nodes", "hda_specific_explicit_nodes"
    )
    missing_contract_nodes = census.get("missing_contract_nodes", {})
    missing_construction_boundary = (
        {
            key: value
            for key, value in missing_contract_nodes.items()
            if key != "hda_specific_explicit_nodes"
        }
        if isinstance(missing_contract_nodes, dict)
        else None
    )
    if (
        not isinstance(missing_contract_nodes, dict)
        or set(missing_contract_nodes)
        != {
            "source_ref",
            "construction_inventory_at_start",
            "hda_specific_explicit_nodes",
            "full_missing_inventory_member_identities_retained",
            "rule",
        }
        or semantic_sha256(missing_construction_boundary)
        != EXPECTED_CENSUS_SEMANTIC_SHA256[
            "missing_construction_boundary"
        ]
    ):
        errors.append("census_construction_boundary_escalated")
    if not isinstance(missing_nodes, list):
        errors.append("census_explicit_missing_node_inventory_mismatch")
        missing_nodes = []
    elif (
        any(
            not isinstance(row, dict)
            or set(row) != {"node_id", "node_kind", "status"}
            for row in missing_nodes
        )
        or [
            (get(row, "node_id"), get(row, "node_kind"))
            for row in missing_nodes
        ]
        != EXPECTED_MISSING_NODES
        or any(get(row, "status") != "missing" for row in missing_nodes)
    ):
        errors.append("census_explicit_missing_node_inventory_mismatch")
    operator_consumers = census.get("operator_acceptance_consumers", [])
    if not isinstance(operator_consumers, list):
        errors.append("census_operator_acceptance_inventory_mismatch")
        operator_consumers = []
    elif (
        any(
            not isinstance(row, dict)
            or set(row)
            != {
                "path",
                "pointers",
                "current_value_rule",
                "consumer_migrated",
            }
            for row in operator_consumers
        )
        or [
            (
                get(row, "path"),
                tuple(get(row, "pointers") or ()),
            )
            for row in operator_consumers
        ]
        != EXPECTED_OPERATOR_ACCEPTANCE_CONSUMERS
        or any(
            get(row, "consumer_migrated") is not False
            or get(row, "current_value_rule") != "must_remain_null"
            for row in operator_consumers
        )
    ):
        errors.append("census_operator_acceptance_inventory_mismatch")
    human_families = census.get("human_decision_families", [])
    if not isinstance(human_families, list):
        errors.append("census_decision_family_inventory_mismatch")
        human_families = []
    elif (
        [get(family, "family_id") for family in human_families]
        != EXPECTED_HUMAN_DECISION_FAMILY_IDS
        or semantic_sha256(human_families)
        != EXPECTED_CENSUS_SEMANTIC_SHA256[
            "human_decision_families"
        ]
    ):
        errors.append("census_decision_family_inventory_mismatch")
    validators = census.get("validator_census", [])
    if not isinstance(validators, list):
        errors.append("census_validator_inventory_mismatch")
        validators = []
    elif (
        [get(validator, "path") for validator in validators]
        != EXPECTED_VALIDATOR_PATHS
        or semantic_sha256(validators)
        != EXPECTED_CENSUS_SEMANTIC_SHA256["validator_census"]
        or any(
            get(validator, "assurance_consumer_enforced") is not False
            for validator in validators
        )
    ):
        errors.append("census_validator_inventory_mismatch")
    transitive_families = census.get("transitive_consumer_families", [])
    if not isinstance(transitive_families, list):
        errors.append("census_transitive_family_inventory_mismatch")
        transitive_families = []
    elif (
        [get(family, "family_id") for family in transitive_families]
        != EXPECTED_TRANSITIVE_CONSUMER_FAMILY_IDS
        or semantic_sha256(transitive_families)
        != EXPECTED_CENSUS_SEMANTIC_SHA256[
            "transitive_consumer_families"
        ]
    ):
        errors.append("census_transitive_family_inventory_mismatch")
    if any(
        get(family, "migration_complete") is not False
        for family in human_families
    ) or any(
        get(family, "consumer_migration_complete") is not False
        for family in transitive_families
    ):
        errors.append("census_family_migration_fabricated")
    additional_family_ids = set(EXPECTED_HUMAN_DECISION_FAMILY_IDS[:3])
    observed_family_ids = {
        get(family, "family_id") for family in human_families
    }
    additional_family_count = len(
        observed_family_ids & additional_family_ids
    )
    expected_coverage = {
        "baseline_schema_rows": len(rows),
        "candidate_mechanism_rows": len(candidate_rows),
        "current_union_rows": len(rows) + len(candidate_rows),
        "baseline_primary_class_counts_sum_to_112": (
            sum(expected_classes.values()) == len(rows) == 112
        ),
        "all_baseline_paths_partitioned_exactly_once": (
            paths == baseline_paths and len(paths) == len(set(paths))
        ),
        "all_baseline_rows_bound_to_path_id_raw_sha256_and_byte_length": True,
        "all_discovered_matching_pointers_recorded_under_declared_profile": True,
        "all_current_assurance_ref_pointer_arrays_empty": True,
        "all_baseline_consumers_migrated_false": True,
        "command_type_count": 121,
        "command_partition_disjoint_union_complete": True,
        "event_type_count": 135,
        "event_partition_disjoint_union_complete": True,
        "founding_h_action_rows_mapped": (
            len(human_families) - additional_family_count
        ),
        "additional_constitutional_review_and_registry_families_mapped": (
            additional_family_count
        ),
        "operator_acceptance_consumer_count": len(operator_consumers),
        "validator_entries": len(validators),
        "hda_specific_explicit_missing_nodes": len(missing_nodes),
        "suppression_count": 0,
        "complete_only_for_frozen_source_corpus": True,
        "consumer_migration_complete": False,
    }
    if census.get("coverage") != expected_coverage:
        errors.append("census_coverage_reconciliation_mismatch")
    if (
        semantic_sha256(census.get("dynamic_completeness_rule"))
        != EXPECTED_CENSUS_SEMANTIC_SHA256["dynamic_completeness_rule"]
    ):
        errors.append("census_dynamic_completeness_boundary_escalated")
    migration = census.get("migration", {})
    if (
        migration.get("current_consumers_migrated") is not False
        or migration.get("consumer_schema_reissue_complete") is not False
        or migration.get("command_contract_reissue_complete") is not False
        or migration.get("event_contract_reissue_complete") is not False
        or migration.get("assurance_dereference_rules_implemented") is not False
        or migration.get("known_bad_end_to_end_consumer_refusal_proved")
        is not False
        or semantic_sha256(migration)
        != EXPECTED_CENSUS_SEMANTIC_SHA256["migration"]
    ):
        errors.append("census_migration_boundary_escalated")
    if (
        not all_false(census.get("nonclaims"))
        or semantic_sha256(census.get("nonclaims"))
        != EXPECTED_CENSUS_SEMANTIC_SHA256["nonclaims"]
    ):
        errors.append("census_nonclaim_boundary_escalated")
    return unique_errors(errors)


def evaluate_candidate_evidence(
    candidate_evidence: dict[str, Any],
    cases_document: dict[str, Any],
    census: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    expected_top_level = {
        "schema_version",
        "artifact_class",
        "evidence_id",
        "version",
        "evidence_status",
        "ordered_artifact_bindings",
        "suite_summary",
        "census_summary",
        "open_boundaries",
        "proof_boundary",
    }
    if (
        set(candidate_evidence) != expected_top_level
        or candidate_evidence.get("schema_version") != "0.1.0"
        or candidate_evidence.get("artifact_class")
        != "human_decision_assurance_candidate_evidence"
        or candidate_evidence.get("version") != "0.1.0"
        or candidate_evidence.get("evidence_status")
        != "candidate_measurement_not_admitted"
        or not isinstance(candidate_evidence.get("evidence_id"), str)
        or not candidate_evidence["evidence_id"].startswith(
            "odeya.human-decision-assurance.candidate-evidence."
        )
    ):
        errors.append("candidate_evidence_identity_or_shape_mismatch")
    bindings = candidate_evidence.get("ordered_artifact_bindings", [])
    observed_path_roles = [
        (item.get("path"), item.get("role"))
        for item in bindings
        if isinstance(item, dict)
    ]
    if (
        observed_path_roles != EXPECTED_CANDIDATE_EVIDENCE_BINDINGS
        or len(observed_path_roles) != len(set(observed_path_roles))
    ):
        errors.append("candidate_evidence_artifact_inventory_mismatch")
    for item in bindings:
        if not isinstance(item, dict) or set(item) != {
            "path",
            "role",
            "raw_sha256",
            "byte_count",
        }:
            errors.append("candidate_evidence_artifact_binding_shape_mismatch")
            continue
        path = item.get("path")
        try:
            raw = (ROOT / path).read_bytes()
        except (OSError, TypeError):
            errors.append("candidate_evidence_artifact_unresolvable")
            continue
        if (
            item.get("raw_sha256") != raw_sha256(raw)
            or item.get("byte_count") != len(raw)
        ):
            errors.append("candidate_evidence_artifact_binding_mismatch")
    cases = cases_document.get("cases", [])
    expected_suite_summary = {
        "safe_controls": sum(
            case.get("kind") == "safe" for case in cases if isinstance(case, dict)
        ),
        "adversarial_one_mutation_cases": sum(
            case.get("kind") == "adversarial"
            for case in cases
            if isinstance(case, dict)
        ),
        "intent_bound_refusal_rules": len(
            {
                code
                for case in cases
                if isinstance(case, dict)
                for code in case.get("intent_errors", [])
                if isinstance(code, str)
            }
        ),
        "exact_error_inventory_enforced": True,
        "harness_self_tested": True,
    }
    if candidate_evidence.get("suite_summary") != expected_suite_summary:
        errors.append("candidate_evidence_suite_summary_mismatch")
    expected_census_summary = {
        "baseline_schema_rows": len(
            get(census, "baseline_schema_partition", "rows") or []
        ),
        "candidate_mechanism_rows": len(
            get(census, "candidate_mechanism_schemas", "rows") or []
        ),
        "command_types": get(
            census, "command_type_partition", "expected_count"
        ),
        "event_types": get(census, "event_type_partition", "expected_count"),
        "operator_acceptance_consumers": len(
            census.get("operator_acceptance_consumers", [])
        ),
        "decision_families": len(census.get("human_decision_families", [])),
        "validator_entries": len(census.get("validator_census", [])),
        "explicit_missing_nodes": len(
            get(
                census,
                "missing_contract_nodes",
                "hda_specific_explicit_nodes",
            )
            or []
        ),
        "current_consumers_migrated": False,
    }
    if candidate_evidence.get("census_summary") != expected_census_summary:
        errors.append("candidate_evidence_census_summary_mismatch")
    expected_open_keys = {
        "profile_issued",
        "individual_eligibility_ruleset_issued",
        "independent_eligibility_recomputation_retained",
        "material_presentation_receipt_verified_in_real_ceremony",
        "exact_cryptographic_input_bytes_dereferenced_and_verified",
        "assured_decision_wrapper_identity_assigned",
        "aggregate_quorum_evaluated",
        "currentness_evaluated",
        "consumer_migration_complete",
        "real_human_ceremony_verified",
        "accountable_review_complete",
        "gate_a_accepted",
        "runtime_authorized",
        "deployment_authorized",
        "external_effects_authorized",
        "publication_authorized",
    }
    open_boundaries = candidate_evidence.get("open_boundaries")
    if (
        not isinstance(open_boundaries, dict)
        or set(open_boundaries) != expected_open_keys
        or not all_false(open_boundaries)
    ):
        errors.append("candidate_evidence_open_boundary_escalated")
    expected_proof_keys = {
        "proves_natural_person_control",
        "proves_cognition_or_comprehension",
        "proves_substantive_approval",
        "proves_original_decision_authorship",
        "proves_source_decision_time",
        (
            "confirmation_gesture_and_authenticator_actor_"
            "cryptographically_co_bound"
        ),
        "backing_evidence_artifact_bytes_dereferenced",
        "exact_cryptographic_input_bytes_dereferenced_and_verified",
        "material_presentation_receipt_verified_in_real_ceremony",
        "individual_eligibility_ruleset_issued",
        "independent_eligibility_recomputation_retained",
        "proves_assignment_effective_control_or_verifier_independence",
        "human_only_slot_satisfied",
        "aggregate_quorum_evaluated",
        "currentness_evaluated",
        "quorum_authority_effective",
        "profile_issued",
        "consumer_migration_complete",
        "real_human_ceremony_verified",
        "accountable_review_complete",
        "gate_a_accepted",
        "runtime_authorized",
        "deployment_authorized",
        "external_effects_authorized",
        "publication_authorized",
    }
    proof = candidate_evidence.get("proof_boundary")
    if (
        not isinstance(proof, dict)
        or set(proof) != expected_proof_keys
        or not all_false(proof)
    ):
        errors.append("candidate_evidence_proof_boundary_escalated")
    return unique_errors(errors)


def evaluate_kb001(kb: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if kb.get("fixture_id") != "PRQ-013-KB-001":
        errors.append("prq_013_kb_001_identity_mismatch")
    if (
        kb.get("signature_verification") == SUPPORTED
        and kb.get("unattended_agent_can_invoke_key") == SUPPORTED
        and kb.get("human_initiated_remote_operation") == "contradicted"
    ):
        if (
            kb.get("expected_assurance_disposition") != "invalid"
            or kb.get("may_satisfy_human_only_slot") is not False
            or kb.get("may_count_toward_quorum") is not False
        ):
            errors.append("agent_accessible_key_not_sealed_invalid")
        errors.append("agent_accessible_key_cannot_establish_human_control")
    else:
        errors.append("prq_013_kb_001_attack_preconditions_missing")
    if not all_false(kb.get("proof_boundary")):
        errors.append("prq_013_kb_001_proof_boundary_escalated")
    return unique_errors(errors)


def consumer_reference() -> dict[str, Any]:
    return {
        "assurance_ref": "hda-seal.synthetic.0001",
        "human_slot_input_kind": "individual_hda_seal",
        "assured_decision_wrapper": None,
        "assurance_disposition": "eligible",
        "policy_entry": "may_enter_candidate_policy_evaluation_only",
        "candidate_policy_evaluation_result": "eligible_to_enter",
        "decision_observation": "explicit_decision",
        "bare_signature_accepted": False,
        "human_only_slot_satisfied": False,
        "quorum_counted": False,
        "approval_effective": False,
        "authority_effective": False,
    }


def evaluate_consumer(consumer: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not consumer.get("assurance_ref"):
        errors.append("consumer_bypasses_assurance")
    observation = consumer.get("decision_observation")
    if observation in {"timeout", "silence", "missing"}:
        errors.append("timeout_silence_or_missing_is_not_a_decision")
    if consumer.get("bare_signature_accepted") is not False:
        errors.append("bare_signature_accepted_as_human_control")
    eligible = consumer.get("assurance_disposition") == "eligible"
    if not eligible and (
        consumer.get("policy_entry")
        == "may_enter_candidate_policy_evaluation_only"
        or consumer.get("candidate_policy_evaluation_result")
        == "eligible_to_enter"
    ):
        errors.append("missing_or_indeterminate_assurance_promoted")
    input_kind = consumer.get("human_slot_input_kind")
    wrapper = consumer.get("assured_decision_wrapper")
    claims_h_or_quorum = (
        consumer.get("human_only_slot_satisfied") is True
        or consumer.get("quorum_counted") is True
    )
    if claims_h_or_quorum and input_kind != "assured_decision_wrapper":
        errors.append("candidate_assurance_counted_as_h_or_quorum")
        errors.append(
            "individual_core_evidence_or_seal_cannot_satisfy_h_slot"
        )
    if input_kind == "assured_decision_wrapper":
        errors.append(
            "assured_decision_wrapper_contract_not_yet_admitted"
        )
        if wrapper is None:
            errors.append(
                "human_only_slot_requires_admitted_current_assured_"
                "decision_wrapper"
            )
    elif wrapper is not None:
        errors.append("assured_decision_wrapper_input_kind_mismatch")
    if (
        consumer.get("approval_effective") is not False
        or consumer.get("authority_effective") is not False
    ):
        errors.append("eligibility_compiled_to_approval_or_authority")
    return unique_errors(errors)


def evaluate_raw_parser(raw: str) -> list[str]:
    errors: list[str] = []
    try:
        loads_object(raw, "synthetic duplicate-key probe")
    except DuplicateKey:
        errors.append("duplicate_json_key_rejected_before_mapping")
    except (json.JSONDecodeError, UnicodeError, ValueError):
        errors.append("raw_json_probe_unexpected_parse_failure")
    return unique_errors(errors)


def evaluate_raw_chain_probe(
    probe: dict[str, Any],
    candidates: dict[str, Any],
    references: dict[str, Any],
) -> list[str]:
    core_raw = references["core_raw"] + str(
        probe.get("core_suffix", "")
    ).encode("ascii")
    evidence_raw = references["evidence_raw"] + str(
        probe.get("evidence_suffix", "")
    ).encode("ascii")
    return evaluate_chain(
        candidates["core"],
        candidates["evidence"],
        candidates["seal"],
        candidates["frame"],
        candidates["frame_evidence"],
        references["core"],
        references["evidence"],
        core_raw=core_raw,
        evidence_raw=evidence_raw,
        ruleset_candidate=candidates["ruleset_candidate"],
        ruleset_raw=references["ruleset_raw"],
    )


def evaluate_rebound_raw_chain_probe(
    probe: dict[str, Any],
    candidates: dict[str, Any],
    references: dict[str, Any],
) -> list[str]:
    core_suffix = str(probe.get("core_suffix", "")).encode("ascii")
    evidence_suffix = str(
        probe.get("evidence_suffix", "")
    ).encode("ascii")
    core_raw = references["core_raw"] + core_suffix
    core_digest = raw_sha256(core_raw)
    core_bytes = len(core_raw)
    core = candidates["core"]
    evidence = candidates["evidence"]
    seal = candidates["seal"]
    for binding in (evidence["core_binding"], seal["core_binding"]):
        binding["raw_sha256"] = core_digest
        binding["byte_count"] = core_bytes
    for observation in evidence["participant_observations"]:
        challenge = observation["challenge"]
        challenge["bound_core_raw_sha256"] = core_digest
        challenge_value = challenge_from_inputs(
            candidates["frame"],
            chain_challenge_inputs(
                core,
                evidence,
                candidates["frame"],
                candidates["frame_evidence"],
                observation,
                core_digest,
            ),
        )[0]
        challenge["challenge_value"] = challenge_value
        challenge["challenge_id"] = challenge_identifier(challenge_value)
        controlled_time = observation["controlled_time"]
        controlled_time["bound_challenge_id"] = challenge["challenge_id"]
        confirmation = observation["decision_confirmation"]
        confirmation["bound_core_raw_sha256"] = core_digest
        confirmation["bound_challenge_id"] = challenge["challenge_id"]
    evidence_mapping_changed = evidence != references["evidence"]
    evidence_raw = (
        render(evidence)
        if evidence_mapping_changed
        else references["evidence_raw"]
    ) + evidence_suffix
    evidence_binding = seal["ordered_evidence_bindings"][0]
    evidence_binding["raw_sha256"] = raw_sha256(evidence_raw)
    evidence_binding["byte_count"] = len(evidence_raw)
    recompute_fail_closed_seal(evidence, seal)
    return evaluate_chain(
        core,
        evidence,
        seal,
        candidates["frame"],
        candidates["frame_evidence"],
        references["core"],
        references["evidence"],
        core_raw=core_raw,
        evidence_raw=evidence_raw,
        ruleset_candidate=candidates["ruleset_candidate"],
        ruleset_raw=references["ruleset_raw"],
    )


def evaluate_harness_probe(probe: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    observed = {"synthetic_guard"}
    declared = set(probe.get("expected_errors", []))
    if observed != declared:
        errors.append("harness_exact_error_inventory_guard_fired")
    return unique_errors(errors)


def reference_documents() -> dict[str, Any]:
    return {
        "core": load(CORE_FIXTURE),
        "core_raw": CORE_FIXTURE.read_bytes(),
        "evidence": load(EVIDENCE_FIXTURE),
        "evidence_raw": EVIDENCE_FIXTURE.read_bytes(),
        "seal": load(SEAL_FIXTURE),
        "frame": load(CHALLENGE_FRAME),
        "frame_evidence": load(CHALLENGE_FRAME_EVIDENCE),
        "census": load(CONSUMER_CENSUS),
        "census_current_probe": {
            "path": "schemas/admission-evidence-bundle.schema.json",
            "suffix": "",
            "extra_current_schema_paths": [],
            "authority_matrix_suffix": "",
        },
        "candidate_evidence": load(CANDIDATE_EVIDENCE),
        "cases_document": load(CASES),
        "ruleset_candidate": load(INDIVIDUAL_ELIGIBILITY_RULESET),
        "ruleset_raw": INDIVIDUAL_ELIGIBILITY_RULESET.read_bytes(),
        "kb001": load(KB001_FIXTURE),
        "consumer": consumer_reference(),
        "probe": {"expected_errors": ["synthetic_guard"]},
        "raw_chain_probe": {"core_suffix": "", "evidence_suffix": ""},
        "rebound_raw_chain_probe": {
            "core_suffix": "",
            "evidence_suffix": "",
        },
        "ruleset_raw_probe": {"raw_override": None},
    }


def evaluate_case(
    case: dict[str, Any], references: dict[str, Any]
) -> list[str]:
    model = case.get("model")
    candidates = copy.deepcopy(references)
    mutation = case.get("mutation")
    if mutation is not None:
        target = mutation.get("target")
        if target == "raw_json":
            if mutation.get("op") != "inject_duplicate_key":
                raise ValueError("raw_json supports only inject_duplicate_key")
            candidates["raw_json"] = (
                '{"probe":"first","probe":'
                + json.dumps(mutation.get("value"))
                + "}"
            )
        else:
            if target not in candidates:
                raise ValueError(f"unknown mutation target {target!r}")
            apply_mutation(candidates[target], mutation)
    if model in {"chain", "record_chain"}:
        rebind_chain(
            candidates,
            case.get("rebind", "none"),
            case.get("sync", "none"),
            case.get("challenge_nonce_hex"),
        )
        core_raw = (
            references["core_raw"]
            if candidates["core"] == references["core"]
            else render(candidates["core"])
        )
        evidence_raw = (
            references["evidence_raw"]
            if candidates["evidence"] == references["evidence"]
            else render(candidates["evidence"])
        )
        errors = evaluate_chain(
            candidates["core"],
            candidates["evidence"],
            candidates["seal"],
            candidates["frame"],
            candidates["frame_evidence"],
            references["core"],
            references["evidence"],
            core_raw=core_raw,
            evidence_raw=evidence_raw,
            ruleset_candidate=candidates["ruleset_candidate"],
            ruleset_raw=references["ruleset_raw"],
            accept_recorded_negative_outcome=(model == "record_chain"),
        )
        return unique_errors(errors)
    if model == "ruleset_candidate":
        ruleset_raw = render(candidates["ruleset_candidate"])
        seal_ruleset = candidates["seal"]["eligibility_ruleset"]
        seal_ruleset["ruleset_raw_sha256"] = raw_sha256(ruleset_raw)
        seal_ruleset["ruleset_byte_count"] = len(ruleset_raw)
        return evaluate_chain(
            candidates["core"],
            candidates["evidence"],
            candidates["seal"],
            candidates["frame"],
            candidates["frame_evidence"],
            references["core"],
            references["evidence"],
            core_raw=references["core_raw"],
            evidence_raw=references["evidence_raw"],
            ruleset_candidate=candidates["ruleset_candidate"],
            ruleset_raw=ruleset_raw,
        )
    if model == "census":
        return evaluate_census(candidates["census"])
    if model == "candidate_evidence":
        return evaluate_candidate_evidence(
            candidates["candidate_evidence"],
            candidates["cases_document"],
            candidates["census"],
        )
    if model == "census_current":
        probe = candidates["census_current_probe"]
        path = probe.get("path")
        suffix = probe.get("suffix")
        if not isinstance(path, str) or not isinstance(suffix, str):
            raise ValueError("census current-byte probe is malformed")
        current_raw = (ROOT / path).read_bytes() + suffix.encode("utf-8")
        authority_suffix = probe.get("authority_matrix_suffix")
        if not isinstance(authority_suffix, str):
            raise ValueError("census authority-matrix probe is malformed")
        current_authority_matrix_raw = (
            ROOT / EXPECTED_CENSUS_SUBJECT["authority_matrix_ref"]
        ).read_bytes() + authority_suffix.encode("utf-8")
        return evaluate_census(
            candidates["census"],
            current_schema_overrides={path: current_raw},
            extra_current_schema_paths=probe.get(
                "extra_current_schema_paths", []
            ),
            current_authority_matrix_override=current_authority_matrix_raw,
        )
    if model == "kb001":
        return evaluate_kb001(candidates["kb001"])
    if model == "consumer":
        return evaluate_consumer(candidates["consumer"])
    if model == "raw_json":
        return evaluate_raw_parser(candidates.get("raw_json", '{"probe":"ok"}'))
    if model == "raw_chain":
        return evaluate_raw_chain_probe(
            candidates["raw_chain_probe"], candidates, references
        )
    if model == "rebound_raw_chain":
        return evaluate_rebound_raw_chain_probe(
            candidates["rebound_raw_chain_probe"],
            candidates,
            references,
        )
    if model == "raw_ruleset":
        raw_override = candidates["ruleset_raw_probe"].get("raw_override")
        if not isinstance(raw_override, str):
            raise ValueError("raw ruleset probe requires a string override")
        ruleset_raw = raw_override.encode("utf-8")
        seal_ruleset = candidates["seal"]["eligibility_ruleset"]
        seal_ruleset["ruleset_raw_sha256"] = raw_sha256(ruleset_raw)
        seal_ruleset["ruleset_byte_count"] = len(ruleset_raw)
        return evaluate_chain(
            candidates["core"],
            candidates["evidence"],
            candidates["seal"],
            candidates["frame"],
            candidates["frame_evidence"],
            references["core"],
            references["evidence"],
            core_raw=references["core_raw"],
            evidence_raw=references["evidence_raw"],
            ruleset_candidate=candidates["ruleset_candidate"],
            ruleset_raw=ruleset_raw,
        )
    if model == "harness_probe":
        return evaluate_harness_probe(candidates["probe"])
    raise ValueError(f"unknown model {model!r}")


def evaluate_cases(
    cases: list[Any], references: dict[str, dict[str, Any]]
) -> tuple[list[str], int, int]:
    failures: list[str] = []
    names: set[str] = set()
    safe_count = 0
    adversarial_count = 0
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            failures.append(f"case {index} is not an object")
            continue
        name = case.get("name")
        kind = case.get("kind")
        if not isinstance(name, str) or not name or name in names:
            failures.append(f"case {index} has a missing or duplicate name")
            continue
        names.add(name)
        mutation = case.get("mutation")
        try:
            observed = set(evaluate_case(case, references))
        except (
            KeyError,
            TypeError,
            ValueError,
            IndexError,
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            DuplicateKey,
        ) as exc:
            failures.append(f"{name}: case execution failed: {exc}")
            continue
        expected = set(case.get("expected_errors", []))
        if kind == "safe":
            safe_count += 1
            if observed:
                failures.append(f"{name}: safe case failed with {sorted(observed)!r}")
        elif kind == "adversarial":
            adversarial_count += 1
            intent = set(case.get("intent_errors", []))
            if not isinstance(mutation, dict):
                failures.append(f"{name}: adversarial case has no mutation")
            if not intent:
                failures.append(f"{name}: adversarial case declares no intent error")
            elif intent - observed:
                failures.append(
                    f"{name}: intent {sorted(intent - observed)!r} did not fire; "
                    f"observed={sorted(observed)!r}"
                )
            if not observed:
                failures.append(f"{name}: known-bad mutation was accepted")
            elif observed != expected:
                failures.append(
                    f"{name}: declared {sorted(expected)!r} but "
                    f"observed {sorted(observed)!r}"
                )
        else:
            failures.append(f"{name}: unknown kind {kind!r}")
    return failures, safe_count, adversarial_count


def coverage_failures(
    safe_count: int, adversarial_count: int, cases_document: dict[str, Any]
) -> list[str]:
    failures: list[str] = []
    if safe_count < 3:
        failures.append(f"expected at least 3 safe cases, found {safe_count}")
    if adversarial_count < 50:
        failures.append(
            f"expected at least 50 adversarial cases, found {adversarial_count}"
        )
    required = set(cases_document.get("required_adversarial_tags", []))
    observed = {
        case.get("adversarial_tag")
        for case in cases_document.get("cases", [])
        if case.get("kind") == "adversarial"
    }
    if None in observed or observed != required:
        failures.append(
            "adversarial tag inventory mismatch: "
            f"required={sorted(required)!r}, observed={sorted(observed)!r}"
        )
    return failures


def harness_self_test(
    references: dict[str, dict[str, Any]], evaluator: Any = None
) -> list[str]:
    """Exercise every retained-case hygiene refusal with synthetic probes."""
    failures: list[str] = []
    run = evaluator or evaluate_cases
    bad = {
        "name": "hda-self-test",
        "kind": "adversarial",
        "model": "consumer",
        "mutation": {
            "target": "consumer",
            "op": "replace",
            "path": "/authority_effective",
            "value": True,
        },
        "expected_errors": ["eligibility_compiled_to_approval_or_authority"],
        "intent_errors": ["eligibility_compiled_to_approval_or_authority"],
    }

    def refuses(case: Any, text: str, label: str) -> None:
        observed, _, _ = run([case], references)
        if not any(text in failure for failure in observed):
            failures.append(
                f"harness self-test: {label} was not refused; got {observed}"
            )

    refuses("not-an-object", "is not an object", "a non-object case")
    missing_name = copy.deepcopy(bad)
    missing_name.pop("name")
    refuses(missing_name, "missing or duplicate name", "a missing name")
    broken_target = copy.deepcopy(bad)
    broken_target["name"] = "hda-self-test-target"
    broken_target["mutation"]["target"] = "no-such-target"
    refuses(broken_target, "case execution failed", "an unknown mutation target")
    no_mutation = copy.deepcopy(bad)
    no_mutation["name"] = "hda-self-test-no-mutation"
    no_mutation["mutation"] = None
    refuses(no_mutation, "has no mutation", "an adversarial case without mutation")
    no_intent = copy.deepcopy(bad)
    no_intent["name"] = "hda-self-test-no-intent"
    no_intent["intent_errors"] = []
    refuses(no_intent, "declares no intent", "a missing intent inventory")
    wrong_intent = copy.deepcopy(bad)
    wrong_intent["name"] = "hda-self-test-wrong-intent"
    wrong_intent["intent_errors"] = ["never_fires"]
    refuses(wrong_intent, "did not fire", "a non-firing intent")
    wrong_expected = copy.deepcopy(bad)
    wrong_expected["name"] = "hda-self-test-wrong-errors"
    wrong_expected["expected_errors"] = ["not_observed"]
    refuses(wrong_expected, "declared", "a non-exact error inventory")
    unknown_kind = copy.deepcopy(bad)
    unknown_kind["name"] = "hda-self-test-kind"
    unknown_kind["kind"] = "unknown"
    refuses(unknown_kind, "unknown kind", "an unknown case kind")
    return failures


def harness_meta_self_test(references: dict[str, dict[str, Any]]) -> list[str]:
    blind = lambda cases, refs: ([], 0, 0)  # noqa: E731
    failures = harness_self_test(references, evaluator=blind)
    if len(set(failures)) != 8:
        return [
            "harness meta self-test: blinding the evaluator did not expose "
            "exactly 8 distinct load-bearing hygiene refusals"
        ]
    return []


def candidate_evidence_self_test(
    references: dict[str, dict[str, Any]],
    cases_document: dict[str, Any],
) -> list[str]:
    mutated = copy.deepcopy(references["candidate_evidence"])
    mutated["ordered_artifact_bindings"][0]["raw_sha256"] = (
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )
    observed = evaluate_candidate_evidence(
        mutated, cases_document, references["census"]
    )
    if "candidate_evidence_artifact_binding_mismatch" not in observed:
        return [
            "candidate evidence self-test: a substituted raw binding was "
            f"not refused; observed={observed!r}"
        ]
    return []


def main() -> int:
    try:
        references = reference_documents()
        cases_document = load(CASES)
        cases = cases_document.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError("cases.json must contain a non-empty cases array")
    except (
        OSError,
        ValueError,
        UnicodeError,
        json.JSONDecodeError,
        DuplicateKey,
    ) as exc:
        print(
            f"HumanDecisionAssurance: invalid suite input: {exc}",
            file=sys.stderr,
        )
        return 1

    failures, safe_count, adversarial_count = evaluate_cases(cases, references)
    base_census_errors = evaluate_census(references["census"])
    if base_census_errors:
        failures.append(
            f"base consumer census rejected: {base_census_errors!r}"
        )
    base_candidate_evidence_errors = evaluate_candidate_evidence(
        references["candidate_evidence"],
        cases_document,
        references["census"],
    )
    if base_candidate_evidence_errors:
        failures.append(
            "base candidate evidence rejected: "
            f"{base_candidate_evidence_errors!r}"
        )
    failures.extend(
        coverage_failures(safe_count, adversarial_count, cases_document)
    )
    failures.extend(harness_self_test(references))
    failures.extend(harness_meta_self_test(references))
    failures.extend(candidate_evidence_self_test(references, cases_document))
    if failures:
        print("HumanDecisionAssurance: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    rule_codes = {
        item
        for case in cases
        for item in case.get("intent_errors", [])
        if isinstance(item, str)
    }
    print(
        "HumanDecisionAssurance: PASS — "
        f"{safe_count} safe controls, {adversarial_count} one-mutation, "
        f"intent-bound known-bads, {len(rule_codes)} refusal rules; "
        "candidate-only, synthetic, unissued, no H slot, no quorum authority, "
        "Gate A blocked, runtime unauthorized."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
