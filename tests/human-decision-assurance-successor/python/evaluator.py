#!/usr/bin/env python3
"""Independent Python derivation of the HDA 0.2 eligibility projection."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import struct
from dataclasses import dataclass
from typing import Any


RULESET_ID = "urn:odeya:human-decision-assurance-eligibility:0.2.0-candidate"
RESOLVER_ID = "urn:odeya:human-decision-assurance:content-address-resolver:0.1.0-candidate"
DOMAIN_ORDER = (
    "exact_core_and_evidence_binding",
    "backing_byte_integrity",
    "challenge_and_replay",
    "decision_confirmation",
    "authentication",
    "identity_and_authenticator_binding",
    "custody",
    "delegation_objections_conflicts",
    "controlled_time",
    "verifier_independence",
    "sanitation",
)
CATEGORICAL_ORDER = (
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
)
OBSERVATION_DOMAINS = DOMAIN_ORDER[2:]
IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:[._:-][a-z0-9]+)+$")
CONTENT_ADDRESS = re.compile(r"^sha256:[0-9a-f]{64}$")
TIMESTAMP = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$")
FRAME_MAGIC = b"ODEYA-HDA-CONFIRMATION-RECEIPT-V1"
FRAME_FIELDS = (
    "presentation_challenge_id",
    "displayed_bytes_sha256",
    "displayed_byte_count",
    "rendering_profile_id",
    "confirmation_gesture_kind",
    "confirmation_gesture_at",
)


class EvaluationError(ValueError):
    """Raised for malformed evaluator inputs, never for an adverse finding."""


@dataclass(frozen=True)
class DomainProjection:
    domain: str
    count: int
    status: str
    reasons: tuple[str, ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "input_observation_count": self.count,
            "folded_status": self.status,
            "reason_codes": list(self.reasons),
        }


@dataclass(frozen=True)
class CategoricalProjection:
    condition_id: str
    status: str
    reasons: tuple[str, ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "status": self.status,
            "reason_codes": list(self.reasons),
        }


def _sorted_unique(values: list[str] | tuple[str, ...] | set[str]) -> tuple[str, ...]:
    if not all(isinstance(value, str) and value.isascii() for value in values):
        raise EvaluationError("reason codes must be ASCII strings")
    return tuple(sorted(set(values), key=lambda value: value.encode("ascii")))


def _strict_json_bytes(raw: bytes) -> bool:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate member")
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError(value)

    try:
        text = raw.decode("utf-8", errors="strict")
        json.loads(text, object_pairs_hook=unique, parse_constant=reject)
    except (UnicodeError, ValueError, json.JSONDecodeError):
        return False
    return True


def _read_cbor_argument(raw: bytes, offset: int, additional: int) -> tuple[int, int]:
    if additional < 24:
        return additional, offset
    widths = {24: 1, 25: 2, 26: 4, 27: 8}
    width = widths.get(additional)
    if width is None or offset + width > len(raw):
        raise EvaluationError("indefinite or truncated CBOR argument")
    value = int.from_bytes(raw[offset : offset + width], "big")
    if (width == 1 and value < 24) or (width == 2 and value <= 0xFF) or (width == 4 and value <= 0xFFFF) or (width == 8 and value <= 0xFFFFFFFF):
        raise EvaluationError("non-shortest CBOR argument")
    return value, offset + width


def _read_cbor_item(raw: bytes, offset: int, depth: int = 0) -> int:
    if depth > 64 or offset >= len(raw):
        raise EvaluationError("truncated or over-nested CBOR")
    initial = raw[offset]
    offset += 1
    major, additional = initial >> 5, initial & 31
    value, offset = _read_cbor_argument(raw, offset, additional)
    if major in {0, 1}:
        return offset
    if major in {2, 3}:
        end = offset + value
        if end > len(raw):
            raise EvaluationError("truncated CBOR string")
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
    raise EvaluationError("unsupported CBOR item")


def _strict_cbor(raw: bytes) -> bool:
    try:
        return _read_cbor_item(raw, 0) == len(raw)
    except (EvaluationError, UnicodeError):
        return False


def _parse_frame(raw: bytes) -> dict[str, bytes] | None:
    try:
        if not raw.startswith(FRAME_MAGIC):
            return None
        offset = len(FRAME_MAGIC)
        if offset + 2 > len(raw):
            return None
        count = struct.unpack_from(">H", raw, offset)[0]
        offset += 2
        if count != len(FRAME_FIELDS):
            return None
        fields: dict[str, bytes] = {}
        for expected in FRAME_FIELDS:
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
            if name != expected or offset + value_size > len(raw):
                return None
            fields[name] = raw[offset : offset + value_size]
            offset += value_size
        if offset != len(raw):
            return None
        if len(fields["presentation_challenge_id"]) != 32 or len(fields["displayed_bytes_sha256"]) != 32:
            return None
        if len(fields["displayed_byte_count"]) != 4:
            return None
        if not fields["rendering_profile_id"] or not fields["confirmation_gesture_kind"]:
            return None
        fields["rendering_profile_id"].decode("ascii", errors="strict")
        fields["confirmation_gesture_kind"].decode("ascii", errors="strict")
        timestamp = fields["confirmation_gesture_at"].decode("ascii", errors="strict")
        if TIMESTAMP.fullmatch(timestamp) is None:
            return None
        return fields
    except (UnicodeError, struct.error):
        return None


def _decode_base64(value: Any) -> bytes | None:
    if not isinstance(value, str) or not value.isascii():
        return None
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError):
        return None
    if base64.b64encode(raw).decode("ascii") != value:
        return None
    return raw


def _format_ok(role: str, media_type: str, raw: bytes) -> tuple[bool, dict[str, bytes] | None]:
    if media_type == "application/json":
        return _strict_json_bytes(raw), None
    if media_type == "application/cbor":
        return _strict_cbor(raw), None
    if role == "exact_unmodified_confirmation_receipt_frame":
        frame = _parse_frame(raw)
        return frame is not None, frame
    return media_type == "application/octet-stream" and bool(raw), None


def _positive_domain(domain: str) -> tuple[str, ...]:
    return (f"eligible.domain.{domain}.supported",)


def _domain_from_status(domain: str, statuses: list[str], missing: bool = False) -> DomainProjection:
    if missing or not statuses:
        return DomainProjection(domain, len(statuses), "unknown", (f"indeterminate.domain.{domain}.missing",))
    if any(status == "contradicted" for status in statuses):
        code = "invalid.sanitation.contradicted" if domain == "sanitation" else f"invalid.domain.{domain}.contradicted"
        return DomainProjection(domain, len(statuses), "contradicted", (code,))
    if any(status == "unknown" for status in statuses):
        return DomainProjection(domain, len(statuses), "unknown", (f"indeterminate.domain.{domain}.unknown",))
    if any(status == "not_applicable" for status in statuses):
        return DomainProjection(domain, len(statuses), "not_applicable", (f"indeterminate.domain.{domain}.not_applicable",))
    if statuses and all(status == "supported" for status in statuses):
        return DomainProjection(domain, len(statuses), "supported", _positive_domain(domain))
    return DomainProjection(domain, len(statuses), "contradicted", (f"invalid.domain.{domain}.contradicted",))


def _backing_projection(subject: dict[str, Any], resolver: dict[str, Any]) -> tuple[DomainProjection, dict[str, str]]:
    expected_inventory = resolver.get("closed_role_inventory")
    backing = subject.get("backing_byte_inputs")
    if not isinstance(expected_inventory, list) or not isinstance(backing, dict):
        raise EvaluationError("resolver inventory or backing_byte_inputs is malformed")
    expected_roles = [entry.get("role") for entry in expected_inventory if isinstance(entry, dict)]
    artifacts = backing.get("artifacts")
    if not isinstance(artifacts, list):
        artifacts = []
    present_row_count = sum(
        1
        for artifact in artifacts
        if isinstance(artifact, dict) and isinstance(artifact.get("verification_row"), dict)
    )
    actual_roles = [artifact.get("descriptor", {}).get("role") if isinstance(artifact, dict) else None for artifact in artifacts]
    if actual_roles != expected_roles:
        reason = "invalid.backing_byte.closed_role_inventory_mismatch"
        return DomainProjection("backing_byte_integrity", present_row_count, "contradicted", (reason,)), {}

    findings: set[str] = set()
    read_states: dict[str, str] = {}
    artifact_ids: set[str] = set()
    frame_fields: dict[str, bytes] | None = None
    frame_digest: str | None = None
    descriptors: dict[str, dict[str, Any]] = {}

    for expected, artifact in zip(expected_inventory, artifacts, strict=True):
        if not isinstance(artifact, dict):
            findings.add("invalid.backing_byte.closed_role_inventory_mismatch")
            continue
        descriptor = artifact.get("descriptor")
        if not isinstance(descriptor, dict):
            findings.add("invalid.backing_byte.closed_role_inventory_mismatch")
            continue
        role = descriptor.get("role")
        if not isinstance(role, str):
            findings.add("invalid.backing_byte.closed_role_inventory_mismatch")
            continue
        descriptors[role] = descriptor
        artifact_id = descriptor.get("artifact_id")
        if not isinstance(artifact_id, str) or artifact_id in artifact_ids:
            findings.add("invalid.backing_byte.closed_role_inventory_mismatch")
        else:
            artifact_ids.add(artifact_id)
        content_address = descriptor.get("content_address")
        digest_hex = content_address[7:] if isinstance(content_address, str) and CONTENT_ADDRESS.fullmatch(content_address) else None
        derived_path = f"architecture/evidence-blobs/sha256/{digest_hex[:2]}/{digest_hex[2:]}" if digest_hex else None
        descriptor_mismatch = (
            descriptor.get("media_type") != expected.get("required_media_type")
            or descriptor.get("byte_fidelity") != expected.get("required_byte_fidelity")
            or descriptor.get("repository_blob_path") != derived_path
            or not isinstance(descriptor.get("byte_count"), int)
            or isinstance(descriptor.get("byte_count"), bool)
            or descriptor.get("byte_count", 0) <= 0
        )

        preimage = artifact.get("preimage")
        raw = _decode_base64(preimage.get("raw_base64")) if isinstance(preimage, dict) else None
        row = artifact.get("verification_row")
        if raw is None:
            read_states[role] = "missing"
            findings.add(f"indeterminate.backing_byte.{role}.missing")
            if not isinstance(row, dict):
                findings.add("invalid.backing_byte.failed_row_omitted")
            elif row.get("read_disposition") == "readable_complete":
                if row.get("observed_byte_count") == 0:
                    findings.add("invalid.backing_byte.missing_recorded_as_zero_byte_match")
                else:
                    findings.add("invalid.backing_byte.missing_recorded_as_readable_match")
            continue

        read_states[role] = "readable_complete"
        observed = "sha256:" + hashlib.sha256(raw).hexdigest()
        format_ok, parsed_frame = _format_ok(role, str(expected.get("required_media_type")), raw)
        malformed = not format_ok
        if malformed:
            findings.add(f"invalid.backing_byte.{role}.malformed")
        if (
            descriptor_mismatch
            or observed != content_address
            or len(raw) != descriptor.get("byte_count")
            or not isinstance(preimage, dict)
            or preimage.get("repository_blob_path") != derived_path
            or malformed
        ):
            findings.add(f"invalid.backing_byte.{role}.mismatch")
        if not isinstance(row, dict):
            findings.add("invalid.backing_byte.failed_row_omitted")
        else:
            expected_row = {
                "role": role,
                "artifact_id": artifact_id,
                "expected_content_address": content_address,
                "expected_byte_count": descriptor.get("byte_count"),
                "expected_media_type": descriptor.get("media_type"),
                "expected_byte_fidelity": descriptor.get("byte_fidelity"),
                "repository_blob_path": derived_path,
                "read_disposition": "readable_complete",
                "observed_raw_sha256": observed,
                "observed_byte_count": len(raw),
                "format_disposition": "conformant" if format_ok else "malformed",
                "comparison_disposition": "match" if not descriptor_mismatch and observed == content_address and len(raw) == descriptor.get("byte_count") and format_ok and preimage.get("repository_blob_path") == derived_path else "mismatch",
                "integrity_observation": "supported" if not descriptor_mismatch and observed == content_address and len(raw) == descriptor.get("byte_count") and format_ok and preimage.get("repository_blob_path") == derived_path else "contradicted",
            }
            if row != expected_row:
                findings.add(f"invalid.backing_byte.{role}.mismatch")
        if role == "exact_unmodified_confirmation_receipt_frame":
            frame_fields = parsed_frame
            frame_digest = observed

    relation = backing.get("confirmation_receipt_frame_relation")
    displayed = descriptors.get("exact_unmodified_displayed_decision_bytes", {})
    relation_ok = isinstance(relation, dict) and frame_fields is not None and frame_digest is not None
    if relation_ok:
        assert isinstance(relation, dict) and frame_fields is not None and frame_digest is not None
        relation_ok = (
            relation.get("frame_role") == "exact_unmodified_confirmation_receipt_frame"
            and relation.get("expected_frame_content_address") == frame_digest
            and relation.get("observed_frame_raw_sha256") == frame_digest
            and relation.get("authentication_frame_committed_receipt_sha256") == frame_digest
            and relation.get("presentation_challenge_id") == "sha256:" + frame_fields["presentation_challenge_id"].hex()
            and displayed.get("content_address") == "sha256:" + frame_fields["displayed_bytes_sha256"].hex()
            and displayed.get("byte_count") == int.from_bytes(frame_fields["displayed_byte_count"], "big")
            and relation.get("binary_framing_disposition") == "supported"
            and relation.get("presentation_to_receipt_relation_disposition") == "supported"
            and relation.get("receipt_to_authentication_relation_disposition") == "supported"
        )
    if not relation_ok:
        findings.add("invalid.backing_byte.confirmation_receipt_relation_mismatch")

    ordered = _sorted_unique(findings)
    if any(code.startswith("invalid.") for code in ordered):
        status = "contradicted"
    elif any(code.startswith("indeterminate.") for code in ordered):
        status = "unknown"
    else:
        status = "supported"
        ordered = ("eligible.domain.backing_byte_integrity.supported",)
    return DomainProjection("backing_byte_integrity", present_row_count, status, ordered), read_states


def _exact_binding_projection(subject: dict[str, Any], ruleset: dict[str, Any]) -> DomainProjection:
    findings: set[str] = set()
    rule_input = subject.get("ruleset_input")
    participant = subject.get("participant_input")
    required = [entry.get("domain_id") for entry in ruleset.get("required_domains", []) if isinstance(entry, dict)]
    if not isinstance(rule_input, dict) or rule_input.get("required_domain_ids") != required:
        findings.add("invalid.integrity.required_domain_inventory_mismatch")
    if not isinstance(rule_input, dict) or rule_input.get("ruleset_id") != RULESET_ID or rule_input.get("ruleset_version") != "0.2.0":
        findings.add("invalid.integrity.resource_identity_version_mismatch")
    if isinstance(participant, dict) and set(participant) - {"principal_id", "domain_observation_sequences", "categorical_inputs"}:
        findings.add("invalid.integrity.undeclared_eligibility_domain")
    status = subject.get("exact_core_and_evidence_binding_observation")
    if status == "contradicted":
        findings.add("invalid.domain.exact_core_and_evidence_binding.contradicted")
    elif status in {"unknown", "not_applicable"}:
        findings.add(f"indeterminate.domain.exact_core_and_evidence_binding.{status}")
    elif status != "supported":
        findings.add("indeterminate.domain.exact_core_and_evidence_binding.missing")
    reasons = _sorted_unique(findings)
    if any(reason.startswith("invalid.") for reason in reasons):
        folded = "contradicted"
    elif reasons:
        folded = "unknown"
    else:
        folded = "supported"
        reasons = _positive_domain("exact_core_and_evidence_binding")
    return DomainProjection("exact_core_and_evidence_binding", 1, folded, reasons)


def _observation_projections(subject: dict[str, Any]) -> list[DomainProjection]:
    participant = subject.get("participant_input")
    sequences = participant.get("domain_observation_sequences") if isinstance(participant, dict) else None
    by_domain: dict[str, Any] = {}
    if isinstance(sequences, list):
        for sequence in sequences:
            if isinstance(sequence, dict) and isinstance(sequence.get("domain"), str):
                domain = sequence["domain"]
                if domain in by_domain:
                    by_domain[domain] = None
                else:
                    by_domain[domain] = sequence
    result: list[DomainProjection] = []
    for domain in OBSERVATION_DOMAINS:
        sequence = by_domain.get(domain)
        observations = sequence.get("observations") if isinstance(sequence, dict) else None
        statuses: list[str] = []
        if isinstance(observations, list):
            statuses = [item.get("status") for item in observations if isinstance(item, dict) and isinstance(item.get("status"), str)]
        projection = _domain_from_status(domain, statuses, missing=not isinstance(sequence, dict) or len(statuses) != len(observations or []))
        if domain == "sanitation":
            sanitation = subject.get("forbidden_content_and_sanitation")
            extra_statuses = sanitation.get("sanitization_verification_sequence") if isinstance(sanitation, dict) else None
            sanitation_statuses = [item.get("status") for item in extra_statuses if isinstance(item, dict) and isinstance(item.get("status"), str)] if isinstance(extra_statuses, list) else []
            combined = statuses + sanitation_statuses
            projection = _domain_from_status(domain, combined, missing=not combined)
            forbidden = sanitation.get("ordered_forbidden_content_observations") if isinstance(sanitation, dict) else None
            present = isinstance(forbidden, list) and any(isinstance(item, dict) and item.get("disposition") == "present" for item in forbidden)
            sanitation_count = len(combined) + (len(forbidden) if isinstance(forbidden, list) else 0)
            projection = DomainProjection(
                projection.domain,
                sanitation_count,
                projection.status,
                projection.reasons,
            )
            if present:
                reasons = set(projection.reasons)
                reasons.discard("eligible.domain.sanitation.supported")
                reasons.add("invalid.sanitation.forbidden_content")
                projection = DomainProjection(domain, sanitation_count, "contradicted", _sorted_unique(reasons))
        result.append(projection)
    return result


def _categorical(condition: str, status: str, specific: list[str] | None = None) -> CategoricalProjection:
    if specific is not None:
        reasons = _sorted_unique(specific)
    else:
        suffix = {"satisfied": "satisfied", "failed": "failed", "unknown": "unknown", "not_applicable": "not_applicable"}[status]
        prefix = {"satisfied": "eligible", "failed": "invalid", "unknown": "indeterminate", "not_applicable": "indeterminate"}[status]
        reasons = (f"{prefix}.categorical.{condition}.{suffix}",)
    return CategoricalProjection(condition, status, reasons)


def _present_value(values: dict[str, Any], name: str, satisfied: Any, unknown_values: set[Any]) -> str:
    if name not in values or values[name] is None or values[name] in unknown_values:
        return "unknown"
    return "satisfied" if values[name] == satisfied else "failed"


def _categorical_projections(subject: dict[str, Any], read_states: dict[str, str]) -> list[CategoricalProjection]:
    participant = subject.get("participant_input")
    values = participant.get("categorical_inputs") if isinstance(participant, dict) else None
    principal_id = participant.get("principal_id") if isinstance(participant, dict) else None
    if not isinstance(values, dict):
        values = {}
    projections: list[CategoricalProjection] = []
    projections.append(_categorical(CATEGORICAL_ORDER[0], _present_value(values, "challenge_consumption_state", "fresh_consumed_once", {"unknown"})))
    projections.append(_categorical(CATEGORICAL_ORDER[1], _present_value(values, "prior_consumption_count", 0, set())))
    projections.append(_categorical(CATEGORICAL_ORDER[2], _present_value(values, "result_consumption_count", 1, set())))

    acceptance = values.get("assertion_acceptance_atomic_action_id")
    consumption = values.get("consumption_atomic_action_id")
    atomic_reasons: list[str] = []
    invalid_atomic = False
    if acceptance is None:
        atomic_reasons.append("indeterminate.atomic_action.acceptance_id_missing")
    elif not isinstance(acceptance, str) or IDENTIFIER.fullmatch(acceptance) is None:
        atomic_reasons.append("invalid.atomic_action.acceptance_id_malformed")
        invalid_atomic = True
    if consumption is None:
        atomic_reasons.append("indeterminate.atomic_action.consumption_id_missing")
    elif not isinstance(consumption, str) or IDENTIFIER.fullmatch(consumption) is None:
        atomic_reasons.append("invalid.atomic_action.consumption_id_malformed")
        invalid_atomic = True
    if isinstance(acceptance, str) and IDENTIFIER.fullmatch(acceptance) and isinstance(consumption, str) and IDENTIFIER.fullmatch(consumption) and acceptance != consumption:
        atomic_reasons.append("invalid.atomic_action.identifiers_unequal")
        invalid_atomic = True
    required_role = "sanitized_challenge_lifecycle_and_atomic_consumption_record"
    record_role = values.get("atomic_action_record_role")
    if record_role is None:
        atomic_reasons.append("indeterminate.atomic_action.backing_record_missing")
    elif record_role != required_role:
        atomic_reasons.append("invalid.atomic_action.backing_record_malformed")
        invalid_atomic = True
    observation = values.get("atomic_action_record_observation")
    if observation == "contradicted":
        atomic_reasons.append("invalid.atomic_action.backing_record_contradicted")
        invalid_atomic = True
    elif observation in {"unknown", "not_applicable", None}:
        read = read_states.get("sanitized_challenge_lifecycle_and_atomic_consumption_record")
        atomic_reasons.append("indeterminate.atomic_action.backing_record_unreadable" if read == "unreadable" else "indeterminate.atomic_action.backing_record_missing")
    if invalid_atomic:
        atomic_status = "failed"
    elif atomic_reasons:
        atomic_status = "unknown"
    else:
        atomic_status = "satisfied"
        atomic_reasons = [f"eligible.categorical.{CATEGORICAL_ORDER[3]}.satisfied"]
    projections.append(_categorical(CATEGORICAL_ORDER[3], atomic_status, atomic_reasons))

    principal_value = values.get("decision_confirmation_principal_id")
    principal_status = "unknown" if principal_value is None else ("satisfied" if isinstance(principal_id, str) and principal_value == principal_id else "failed")
    projections.append(_categorical(CATEGORICAL_ORDER[4], principal_status))
    projections.append(_categorical(CATEGORICAL_ORDER[5], _present_value(values, "decision_confirmation_initiator_class", "human_initiated", {"unknown"})))
    projections.append(_categorical(CATEGORICAL_ORDER[6], _present_value(values, "decision_confirmation_separate_from_authenticator_gesture", True, set())))
    projections.append(_categorical(CATEGORICAL_ORDER[7], _present_value(values, "cross_origin_disposition", "same_origin_supported", {"unknown"})))
    projections.append(_categorical(CATEGORICAL_ORDER[8], _present_value(values, "signature_counter_disposition", "observed_no_clone_conclusion", {"unknown"})))
    shared = values.get("shared_effective_control_principal_ids")
    shared_status = "unknown" if shared is None else ("satisfied" if isinstance(shared, list) and not shared else "failed")
    projections.append(_categorical(CATEGORICAL_ORDER[9], shared_status))
    projections.append(_categorical(CATEGORICAL_ORDER[10], _present_value(values, "verifier_relation_to_decision_principal", "distinct_principal_and_effective_control", {"unknown"})))
    return projections


def evaluate(subject: dict[str, Any], ruleset: dict[str, Any], resolver: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(subject, dict) or not isinstance(ruleset, dict) or not isinstance(resolver, dict):
        raise EvaluationError("subject, ruleset, and resolver must be objects")
    if ruleset.get("ruleset_id") != RULESET_ID or resolver.get("profile_id") != RESOLVER_ID:
        raise EvaluationError("unexpected ruleset or resolver identity")
    actual_domains = tuple(entry.get("domain_id") for entry in ruleset.get("required_domains", []) if isinstance(entry, dict))
    actual_categories = tuple(ruleset.get("required_categorical_conditions", []))
    if actual_domains != DOMAIN_ORDER or actual_categories != CATEGORICAL_ORDER:
        raise EvaluationError("normative ordered inventory differs from evaluator contract")

    exact = _exact_binding_projection(subject, ruleset)
    backing, read_states = _backing_projection(subject, resolver)
    domains = [exact, backing, *_observation_projections(subject)]
    if tuple(item.domain for item in domains) != DOMAIN_ORDER:
        raise EvaluationError("computed domain order is incomplete")
    categoricals = _categorical_projections(subject, read_states)
    if tuple(item.condition_id for item in categoricals) != CATEGORICAL_ORDER:
        raise EvaluationError("computed categorical order is incomplete")

    negative: set[str] = set()
    for projection in domains:
        negative.update(reason for reason in projection.reasons if not reason.startswith("eligible."))
    for projection in categoricals:
        negative.update(reason for reason in projection.reasons if not reason.startswith("eligible."))
    ordered_negative = _sorted_unique(negative)
    if any(reason.startswith("invalid.") for reason in ordered_negative):
        disposition = "invalid"
        reasons = ordered_negative
    elif ordered_negative:
        disposition = "indeterminate"
        reasons = ordered_negative
    else:
        disposition = "eligible"
        reasons = ("eligible.all_required_inputs_supported",)

    participant = subject.get("participant_input")
    participant_id = participant.get("principal_id") if isinstance(participant, dict) else None
    if not isinstance(participant_id, str):
        raise EvaluationError("participant principal_id is missing")
    failures = sorted(
        (item.condition_id for item in categoricals if item.status == "failed"),
        key=lambda value: value.encode("ascii"),
    )
    return {
        "participant_id": participant_id,
        "domain_results": [item.as_json() for item in domains],
        "categorical_results": [item.as_json() for item in categoricals],
        "categorical_failures": failures,
        "final_disposition": disposition,
        "reason_codes": list(reasons),
    }
