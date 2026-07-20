#!/usr/bin/env python3
"""Validate the architecture-only Gate A prerequisite closure inventory.

This checker proves cross-file inventory equality and nonrecursive dependency
intent only. A pass is not a frozen canonical profile, immutable registry,
constitutional admission, Gate A acceptance, or runtime authorization.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "architecture/gate-a-prerequisite-closure.json"
FIRST_SLICE = ROOT / "architecture/first-slice-admission-resolution-candidate.json"
CANONICAL_AUDIT = ROOT / "tests/canonicalization/SCHEMA_AUDIT.json"
CANONICAL_PROFILE_CORE = (
    ROOT / "architecture/canonicalization-profile-core-candidate.json"
)
CANONICAL_PROFILE_EVIDENCE = (
    ROOT / "architecture/canonicalization-profile-candidate-evidence.json"
)
EXPECTED_REFUSAL_KEYS = frozenset(
    {
        "gate_a_complete",
        "immutable_candidate_exists",
        "runtime_authorized",
        "deployment_authorized",
        "external_registration_authorized",
        "signature_or_witness_fabrication_authorized",
    }
)
EXPECTED_REPOSITORY_PUBLICATION = {
    "canonical_remote": "https://github.com/manfromnowhere143/odeya",
    "visibility": "public",
    "architecture_repository_authorized": True,
    "authority_decision_ref":
        "docs/decisions/0047-create-the-public-remote-and-publish.md",
    "reconciliation_decision_ref":
        "docs/decisions/0087-reconcile-public-repository-operational-contract.md",
    "ongoing_contract_ref": "docs/REPOSITORY_RELEASE.md",
    "runtime_authorized": False,
    "deployment_authorized": False,
    "gate_a_accepted": False,
}
EXPECTED_HUMAN_DECISION_ASSURANCE = {
    "status": "unresolved_blocking",
    "applies_to": "every_policy_defined_consequential_human_only_decision",
    "signature_assurance":
        "signature_validity_under_declared_public_key_algorithm_and_trust_profile_only",
    "signature_proves_human_decision_intent": False,
    "authentication_intent_satisfies_substantive_decision_intent": False,
    "protected_ceremony_proves_review_understanding_or_cognition": False,
    "declared_human_principal_satisfies_human_decision": False,
    "unattended_agent_accessible_signing_key_satisfies_human_decision": False,
    "timeout_or_silence_satisfies_human_decision": False,
    "missing_assurance_disposition": "blocked_or_indeterminate_never_approval",
    "candidate_schema_resource_identities_assigned": True,
    "candidate_schema_refs": [
        {
            "path": "schemas/human-decision-assurance-core.schema.json",
            "schema_id":
                "urn:odeya:schema:human-decision-assurance-core:0.1.0",
        },
        {
            "path": "schemas/human-decision-assurance-evidence.schema.json",
            "schema_id":
                "urn:odeya:schema:human-decision-assurance-evidence:0.1.0",
        },
        {
            "path": "schemas/human-decision-assurance-seal.schema.json",
            "schema_id":
                "urn:odeya:schema:human-decision-assurance-seal:0.1.0",
        },
    ],
    "candidate_schemas_issued": False,
    "admitted_assurance_record_identity_issued": False,
    "assured_decision_wrapper_identity_assigned": False,
    "individual_assurance_foundation_closes_prq_013": False,
    "assured_decision_dependency_stage":
        "after_t1_authority_assignment_and_t2_authority_currentness_quorum_"
        "consumer_contracts",
    "individual_eligibility_ruleset_ref":
        "architecture/human-decision-assurance-individual-eligibility-ruleset-v1-candidate.json",
    "individual_eligibility_ruleset_issued": False,
    "independent_eligibility_recomputation_retained": False,
    "material_presentation_receipt_verified_in_real_ceremony": False,
    # ADR 0093, adopted. True as a property of the two-phase frame
    # construction: the authentication challenge commits to the confirmation
    # receipt digest, so a signature covers what was displayed and confirmed.
    # It is not a claim that any ceremony occurred -- see
    # material_presentation_receipt_verified_in_real_ceremony, still False --
    # and it does not prevent a presentation surface that lies about its own
    # displayed bytes, only detect the disagreement.
    "confirmation_gesture_and_authenticator_actor_cryptographically_co_bound":
        True,
    "exact_cryptographic_input_bytes_dereferenced_and_verified": False,
    "complete_consumer_census_for_frozen_source_corpus": True,
    "consumer_census_ref":
        "architecture/human-decision-assurance-consumer-census.json",
    "consumer_census_binding": {
        "raw_sha256":
            "sha256:d761cdb4ebd8776935a90bc7c877da805f3e07bb17ce1333f24c01619b4f9a3a",
        "byte_count": 147738,
        "baseline_git_commit": "56e8062334fb81bba955ba137be690e085d4c88e",
        "baseline_git_tree": "d90ed6dd8c54b91a1e503358f98ecaa08c766fa3",
        "baseline_schema_count": 112,
        "candidate_mechanism_schema_count": 3,
        "current_union_schema_count": 115,
        "direct_or_policy_conditional_schema_count": 19,
        "pending_operator_acceptance_schema_count": 9,
    },
    "current_consumers_migrated": False,
    "migrated_consumer_count": 0,
    "end_to_end_consumer_refusal_proved": False,
    "real_human_ceremony_verified": False,
    "gate_a_requires_live_protected_ceremony": False,
    "real_protected_ceremony_stage":
        "gate_b_after_gate_a_only_with_separate_operator_authorization",
    "runtime_conformance_stage": "gate_c_exit_evidence",
    "accountable_review_complete": False,
    "minimum_affected_source_schema_ids": [
        "urn:odeya:schema:root-authority-manifest:0.4.0",
        "urn:odeya:schema:authority-assignment:0.3.0",
        "urn:odeya:schema:protocol-amendment:0.4.0",
        "urn:odeya:schema:data-use-decision:0.3.0",
        "urn:odeya:schema:review-determination:0.3.0",
        "urn:odeya:schema:operator-architecture-decision:0.4.0",
        "urn:odeya:schema:publication-decision:0.5.0",
        "urn:odeya:schema:promotion-decision:0.6.0",
        "urn:odeya:schema:recovery-decision:0.6.0",
    ],
    "required_evidence": [
        "exact_decision_and_candidate_internal_identity_version_and_raw_digest_relationship",
        "exact_preceremony_required_review_and_display_decision_and_candidate_raw_bindings_plus_later_evidence_observations",
        "explicit_later_ratification_not_original_authorship_or_source_timestamp_relation",
        "source_decision_schema_and_policy_remain_semantic_authority",
        "verifier_or_relying_party_generated_content_addressed_unpredictable_challenge_bound_to_subject_session_time_and_candidate_rp_origin_algorithm_policy",
        "content_addressed_material_presentation_and_human_confirmation_receipt_bound_to_exact_core_and_full_ceremony_context",
        "cycle_free_cryptographic_or_trusted_path_cobinding_of_confirmation_gesture_and_authenticator_actor",
        "authentication_intent_phishing_resistant_credential_user_presence_and_user_verification_evidence",
        "principal_identity_proofing_and_authenticator_binding_evidence",
        "signing_key_and_session_custody_observation",
        "agent_model_and_tool_signing_exclusion",
        "delegation_scope_depth_objections_and_effective_control_disclosure",
        "singleton_confirming_principal_and_independent_verifier_observation",
        "controlled_time_half_open_expiry_atomic_consumption_and_replay_protection",
        "exact_unmodified_cryptographic_inputs_and_sanitized_derived_observation_records_with_verified_byte_fidelity",
        "exact_byte_bound_total_individual_eligibility_ruleset_and_independent_recomputation",
        "later_assured_decision_aggregate_quorum_currentness_revocation_and_authority_evaluation",
    ],
    "forbidden_evidence": [
        "raw_private_reasoning",
        "reusable_secrets_or_signing_material",
        "unrestricted_prompt_or_model_output",
    ],
    "standards_comparisons": [
        {
            "publication": "NIST SP 800-63B-4",
            "official_url": "https://csrc.nist.gov/pubs/sp/800/63/b/4/final",
            "publication_status": "final",
            "comparison_scope":
                "authentication_intent_authenticator_binding_and_phishing_resistance_only",
        },
        {
            "publication":
                "Web Authentication: An API for accessing Public Key "
                "Credentials Level 3",
            "official_url":
                "https://www.w3.org/TR/2026/CR-webauthn-3-20260526/",
            "publication_status": "candidate_recommendation_snapshot",
            "comparison_scope":
                "challenge_origin_rp_user_presence_user_verification_and_signature_ceremony_only",
        },
    ],
    "candidate_evidence_ref":
        "architecture/human-decision-assurance-candidate-evidence.json",
    "challenge_frame_profile_ref":
        "architecture/human-decision-challenge-frame-v2-candidate.json",
    "challenge_frame_vector_evidence_ref":
        "architecture/human-decision-challenge-frame-v2-candidate-evidence.json",
    "source_evidence_ref":
        "docs/CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md",
    "antecedent_decision_ref":
        "docs/decisions/0089-a-valid-human-signature-is-not-a-human-decision.md",
    "decision_ref":
        "docs/decisions/0092-bind-human-decisions-through-an-external-assurance-wrapper.md",
    "closure_disposition":
        "freeze_unissued_individual_assurance_foundation_then_construct_t1_t2_"
        "dependencies_and_unissued_wrapper_successors_prove_transitive_"
        "migration_exact_backing_bytes_confirmation_actor_cobinding_"
        "independent_recomputation_end_to_end_refusal_and_accountable_gate_a_"
        "review_real_ceremony_deferred_to_separately_authorized_gate_b_probe",
}
EXPECTED_NEXT_DEPENDENCY_CONTAINED_TRANCHE = {
    "tranche_id": "T1.authority-assignment",
    "may_start_after": [
        "canonical_schema_identity_candidate_closure",
        "standalone_member_record_contracts",
        "prq_005_through_prq_010_candidate_corrections",
        "prq_013_individual_assurance_foundation_candidate_closure",
    ],
    "ordered_subjects": [
        "AuthorityAssignment state schema and member",
        "AuthorityAssignment reducer member",
        "authority.assignment_recorded event member",
        "authority.record_root_assignment payload and command member",
        "authority.record_assignment payload and command member",
    ],
    "may_bind_engine_contract_root": False,
}
EXPECTED_PRQ_009_CLOSURE_FRAGMENTS = {
    "corrected_candidate":
        "C5-WORK-LEASE-RELEASE-CLAIM-001 is corrected in unissued "
        "ResearchEvent 0.18.0",
    "aggregate_ownership":
        "work.lease_released terminates only WorkLease",
    "blocking_boundary":
        "PRQ-009 remains unresolved_blocking",
    "post_commit_derivation":
        "then derive a post-commit non-dispatch WorkContract",
}


class DuplicateKey(ValueError):
    """Raised when JSON would otherwise silently overwrite a member."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain one JSON object")
    return value


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def prq_009_boundary_errors(value: Any) -> list[str]:
    """Keep the corrected C5 defect separate from PRQ-009 closure."""

    if not isinstance(value, dict):
        return ["PRQ-009 boundary must be an object"]
    errors: list[str] = []
    if value.get("finding_id") != "PRQ-009":
        errors.append("PRQ-009 boundary has the wrong finding identity")
    if value.get("status") != "unresolved_blocking":
        errors.append("PRQ-009 boundary must remain unresolved_blocking")
    closure = value.get("closure")
    if not isinstance(closure, str):
        return [*errors, "PRQ-009 boundary closure must be text"]
    for label, fragment in EXPECTED_PRQ_009_CLOSURE_FRAGMENTS.items():
        if fragment not in closure:
            errors.append(f"PRQ-009 boundary lost {label}")
    return errors


def validate_prq_009_boundary_known_bads(errors: list[str]) -> int:
    """Prove each corrected-versus-blocked boundary guard can fire."""

    safe_closure = "; ".join(EXPECTED_PRQ_009_CLOSURE_FRAGMENTS.values())
    safe = {
        "finding_id": "PRQ-009",
        "status": "unresolved_blocking",
        "closure": safe_closure,
    }
    safe_errors = prq_009_boundary_errors(safe)
    if safe_errors:
        errors.append(
            "PRQ-009 boundary safe self-test was rejected: "
            + " | ".join(safe_errors)
        )

    mutations = (
        (
            "wrong-finding",
            {"finding_id": "PRQ-008"},
            "PRQ-009 boundary has the wrong finding identity",
        ),
        (
            "premature-closure",
            {"status": "corrected"},
            "PRQ-009 boundary must remain unresolved_blocking",
        ),
        (
            "stale-candidate",
            {
                "closure": safe_closure.replace(
                    "ResearchEvent 0.18.0",
                    "ResearchEvent 0.17.0",
                )
            },
            "PRQ-009 boundary lost corrected_candidate",
        ),
        (
            "lease-settles-resource",
            {
                "closure": safe_closure.replace(
                    "work.lease_released terminates only WorkLease",
                    "work.lease_released settles ResourceLedger",
                )
            },
            "PRQ-009 boundary lost aggregate_ownership",
        ),
        (
            "blocking-caveat-removed",
            {
                "closure": safe_closure.replace(
                    "PRQ-009 remains unresolved_blocking",
                    "PRQ-009 is resolved",
                )
            },
            "PRQ-009 boundary lost blocking_boundary",
        ),
        (
            "pre-commit-contract",
            {
                "closure": safe_closure.replace(
                    "then derive a post-commit non-dispatch WorkContract",
                    "then derive a pre-commit dispatch WorkContract",
                )
            },
            "PRQ-009 boundary lost post_commit_derivation",
        ),
    )
    passed = 0
    for case_id, replacement, expected_reason in mutations:
        candidate = json.loads(json.dumps(safe))
        candidate.update(replacement)
        observed = prq_009_boundary_errors(candidate)
        if expected_reason in observed:
            passed += 1
        else:
            errors.append(
                f"PRQ-009 boundary known-bad {case_id} did not fire its "
                f"intended reason; got {observed!r}"
            )
    return passed


def repository_publication_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["repository_publication must be an object"]
    errors: list[str] = []
    if set(value) != set(EXPECTED_REPOSITORY_PUBLICATION):
        errors.append("repository_publication members must be closed and exact")
    for key, expected_value in EXPECTED_REPOSITORY_PUBLICATION.items():
        if value.get(key) != expected_value:
            errors.append(
                f"repository_publication.{key} must equal {expected_value!r}"
            )
    for key in (
        "authority_decision_ref",
        "reconciliation_decision_ref",
        "ongoing_contract_ref",
    ):
        relative = value.get(key)
        if isinstance(relative, str) and not (ROOT / relative).is_file():
            errors.append(
                f"repository_publication.{key} does not resolve to a retained file"
            )
    return errors


def validate_repository_publication_known_bads(errors: list[str]) -> int:
    safe = dict(EXPECTED_REPOSITORY_PUBLICATION)
    safe_errors = repository_publication_errors(safe)
    if safe_errors:
        errors.append(
            "repository publication safe self-test was rejected: "
            + " | ".join(safe_errors)
        )
    mutations = (
        (
            "private-remote-fiction",
            "visibility",
            "private",
            "repository_publication.visibility must equal 'public'",
        ),
        (
            "wrong-public-identity",
            "canonical_remote",
            "https://example.invalid/odeya",
            "repository_publication.canonical_remote must equal "
            "'https://github.com/manfromnowhere143/odeya'",
        ),
        (
            "runtime-authority-escalation",
            "runtime_authorized",
            True,
            "repository_publication.runtime_authorized must equal False",
        ),
        (
            "gate-a-self-acceptance",
            "gate_a_accepted",
            True,
            "repository_publication.gate_a_accepted must equal False",
        ),
    )
    passed = 0
    for case_id, key, replacement, expected_reason in mutations:
        candidate = dict(safe)
        candidate[key] = replacement
        observed = repository_publication_errors(candidate)
        if expected_reason in observed:
            passed += 1
        else:
            errors.append(
                f"repository publication known-bad {case_id} did not fire its "
                f"intended reason; got {observed!r}"
            )
    return passed


def refusal_boundary_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["refusal must be an object"]
    errors: list[str] = []
    if set(value) != EXPECTED_REFUSAL_KEYS:
        errors.append("refusal members must be closed and exact")
    for key in EXPECTED_REFUSAL_KEYS:
        if value.get(key) is not False:
            errors.append(f"refusal.{key} must be false")
    return errors


def validate_refusal_boundary_known_bads(errors: list[str]) -> int:
    safe = {key: False for key in EXPECTED_REFUSAL_KEYS}
    safe_errors = refusal_boundary_errors(safe)
    if safe_errors:
        errors.append(
            "refusal boundary safe self-test was rejected: "
            + " | ".join(safe_errors)
        )
    mutations = (
        ("empty-refusal-object", {}, "refusal members must be closed and exact"),
        (
            "invented-refusal-member",
            {"invented": False},
            "refusal members must be closed and exact",
        ),
        (
            "runtime-authority-escalation",
            {**safe, "runtime_authorized": True},
            "refusal.runtime_authorized must be false",
        ),
    )
    passed = 0
    for case_id, candidate, expected_reason in mutations:
        observed = refusal_boundary_errors(candidate)
        if expected_reason in observed:
            passed += 1
        else:
            errors.append(
                f"refusal boundary known-bad {case_id} did not fire its "
                f"intended reason; got {observed!r}"
            )
    return passed


def human_decision_assurance_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["human_decision_assurance must be an object"]
    errors: list[str] = []
    if set(value) != set(EXPECTED_HUMAN_DECISION_ASSURANCE):
        errors.append("human_decision_assurance members must be closed and exact")
    for key, expected_value in EXPECTED_HUMAN_DECISION_ASSURANCE.items():
        if value.get(key) != expected_value:
            errors.append(
                f"human_decision_assurance.{key} must equal {expected_value!r}"
            )
    # The co-binding claim is only true while the construction is actually
    # adopted. Pinning it as a constant would let the Core revert to the v1
    # frame while this record kept asserting a property the bytes no longer
    # provide, so it is re-derived from the Core and the Evidence fixture on
    # every run rather than trusted.
    if value.get(
        "confirmation_gesture_and_authenticator_actor_cryptographically_co_bound"
    ) is True:
        try:
            core = json.loads(
                (
                    ROOT
                    / "tests/architecture-schema/fixtures/"
                    "human-decision-assurance-core.valid.json"
                ).read_text(encoding="utf-8")
            )
            evidence = json.loads(
                (
                    ROOT
                    / "tests/architecture-schema/fixtures/"
                    "human-decision-assurance-evidence.valid.json"
                ).read_text(encoding="utf-8")
            )
        except (OSError, ValueError, UnicodeError):
            errors.append(
                "co-binding is claimed but the Core or Evidence fixture is unreadable"
            )
        else:
            request = core.get("ceremony_request", {})
            if (
                request.get("challenge_framing_profile", {}).get("profile_id")
                != "odeya-human-decision-challenge-frame-v2-candidate"
                or request.get("two_phase_challenge_required") is not True
            ):
                errors.append(
                    "co-binding is claimed but the Core does not pin the "
                    "two-phase v2 challenge-framing profile"
                )
            observations = evidence.get("participant_observations", [])
            if not observations or any(
                not isinstance(observation, dict)
                or "confirmation_receipt"
                not in observation.get("challenge", {})
                or "presentation_challenge"
                not in observation.get("challenge", {})
                for observation in observations
            ):
                errors.append(
                    "co-binding is claimed but a participant observation "
                    "carries no presentation challenge and confirmation receipt"
                )
    for key in (
        "consumer_census_ref",
        "individual_eligibility_ruleset_ref",
        "candidate_evidence_ref",
        "challenge_frame_profile_ref",
        "challenge_frame_vector_evidence_ref",
        "source_evidence_ref",
        "antecedent_decision_ref",
        "decision_ref",
    ):
        relative = value.get(key)
        if isinstance(relative, str) and not (ROOT / relative).is_file():
            errors.append(
                f"human_decision_assurance.{key} does not resolve to a retained file"
            )

    schema_refs = value.get("candidate_schema_refs")
    if isinstance(schema_refs, list):
        for index, schema_ref in enumerate(schema_refs):
            if not isinstance(schema_ref, dict):
                errors.append(
                    "human_decision_assurance.candidate_schema_refs"
                    f"[{index}] must be an object"
                )
                continue
            path = schema_ref.get("path")
            schema_id = schema_ref.get("schema_id")
            if not isinstance(path, str) or not isinstance(schema_id, str):
                errors.append(
                    "human_decision_assurance.candidate_schema_refs"
                    f"[{index}] must bind path and schema_id strings"
                )
                continue
            try:
                schema = load(ROOT / path)
            except (
                OSError,
                json.JSONDecodeError,
                DuplicateKey,
                ValueError,
            ) as exc:
                errors.append(
                    "human_decision_assurance.candidate_schema_refs"
                    f"[{index}] does not resolve to strict schema bytes: {exc}"
                )
                continue
            if schema.get("$id") != schema_id:
                errors.append(
                    "human_decision_assurance.candidate_schema_refs"
                    f"[{index}] schema_id does not equal the retained $id"
                )

    census_ref = value.get("consumer_census_ref")
    census_binding = value.get("consumer_census_binding")
    if isinstance(census_ref, str) and isinstance(census_binding, dict):
        census_path = ROOT / census_ref
        try:
            census_raw = census_path.read_bytes()
            census = load(census_path)
        except (
            OSError,
            json.JSONDecodeError,
            DuplicateKey,
            ValueError,
        ) as exc:
            errors.append(
                "human_decision_assurance consumer census is not strict "
                f"retained evidence: {exc}"
            )
        else:
            observed_digest = "sha256:" + hashlib.sha256(census_raw).hexdigest()
            if census_binding.get("raw_sha256") != observed_digest:
                errors.append(
                    "human_decision_assurance.consumer_census_binding.raw_sha256 "
                    "does not match retained census bytes"
                )
            if census_binding.get("byte_count") != len(census_raw):
                errors.append(
                    "human_decision_assurance.consumer_census_binding.byte_count "
                    "does not match retained census bytes"
                )
            subject = census.get("subject")
            partition = census.get("baseline_schema_partition")
            coverage = census.get("coverage")
            migration = census.get("migration")
            if not all(
                isinstance(item, dict)
                for item in (subject, partition, coverage, migration)
            ):
                errors.append(
                    "human_decision_assurance consumer census lacks required "
                    "subject, partition, coverage, or migration objects"
                )
            else:
                census_facts = {
                    "baseline_git_commit": subject.get("baseline_git_commit"),
                    "baseline_git_tree": subject.get("baseline_git_tree"),
                    "baseline_schema_count": subject.get(
                        "baseline_schema_count"
                    ),
                    "candidate_mechanism_schema_count": subject.get(
                        "candidate_mechanism_schema_count"
                    ),
                    "current_union_schema_count": subject.get(
                        "current_union_schema_count"
                    ),
                    "direct_or_policy_conditional_schema_count":
                        partition.get("partition_counts", {}).get(
                            "direct_or_policy_conditional_assurance_subject"
                        ),
                    "pending_operator_acceptance_schema_count":
                        partition.get("partition_counts", {}).get(
                            "pending_operator_acceptance_consumer"
                        ),
                }
                for key, observed in census_facts.items():
                    if census_binding.get(key) != observed:
                        errors.append(
                            "human_decision_assurance.consumer_census_binding."
                            f"{key} does not match the retained census"
                        )
                if (
                    coverage.get("complete_only_for_frozen_source_corpus")
                    is not True
                    or migration.get(
                        "complete_consumer_census_for_frozen_source_corpus"
                    )
                    is not True
                ):
                    errors.append(
                        "human_decision_assurance census does not prove "
                        "completeness for its exact frozen source corpus"
                    )
                if (
                    coverage.get("all_baseline_consumers_migrated_false")
                    is not True
                    or coverage.get("consumer_migration_complete") is not False
                    or migration.get("current_consumers_migrated") is not False
                ):
                    errors.append(
                        "human_decision_assurance census does not retain the "
                        "zero-migration boundary"
                    )
    return errors


def validate_human_decision_assurance_known_bads(errors: list[str]) -> int:
    safe = json.loads(json.dumps(EXPECTED_HUMAN_DECISION_ASSURANCE))
    safe_errors = human_decision_assurance_errors(safe)
    if safe_errors:
        errors.append(
            "human decision-assurance safe self-test was rejected: "
            + " | ".join(safe_errors)
        )
    mutations = (
        (
            "signature-validity-promoted-to-key-control",
            "signature_assurance",
            "key_possession_under_declared_trust_root_only",
        ),
        (
            "signature-promoted-to-intent",
            "signature_proves_human_decision_intent",
            True,
        ),
        (
            "authentication-intent-promoted-to-decision-intent",
            "authentication_intent_satisfies_substantive_decision_intent",
            True,
        ),
        (
            "ceremony-promoted-to-cognition",
            "protected_ceremony_proves_review_understanding_or_cognition",
            True,
        ),
        (
            "declared-human-type-promoted-to-decision",
            "declared_human_principal_satisfies_human_decision",
            True,
        ),
        (
            "agent-accessible-key-promoted-to-human-decision",
            "unattended_agent_accessible_signing_key_satisfies_human_decision",
            True,
        ),
        (
            "silence-promoted-to-human-decision",
            "timeout_or_silence_satisfies_human_decision",
            True,
        ),
        (
            "missing-assurance-promoted-to-approval",
            "missing_assurance_disposition",
            "approved",
        ),
        (
            "approval-basis-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "source_decision_schema_and_policy_remain_semantic_authority"
            ],
        ),
        (
            "human-confirmation-gesture-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "content_addressed_material_presentation_and_human_confirmation_receipt_bound_to_exact_core_and_full_ceremony_context"
            ],
        ),
        (
            "confirmation-authenticator-cobinding-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "cycle_free_cryptographic_or_trusted_path_cobinding_of_confirmation_gesture_and_authenticator_actor"
            ],
        ),
        (
            "eligibility-ruleset-and-independent-recomputation-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "exact_byte_bound_total_individual_eligibility_ruleset_and_independent_recomputation"
            ],
        ),
        (
            "user-presence-and-verification-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "authentication_intent_phishing_resistant_credential_user_presence_and_user_verification_evidence"
            ],
        ),
        (
            "principal-authenticator-binding-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "principal_identity_proofing_and_authenticator_binding_evidence"
            ],
        ),
        (
            "delegation-and-objections-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "delegation_scope_depth_objections_and_effective_control_disclosure"
            ],
        ),
        (
            "singleton-principal-and-verifier-separation-omitted",
            "required_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["required_evidence"]
                if item
                != "singleton_confirming_principal_and_independent_verifier_observation"
            ],
        ),
        (
            "private-reasoning-retained-as-evidence",
            "forbidden_evidence",
            [
                item
                for item in EXPECTED_HUMAN_DECISION_ASSURANCE["forbidden_evidence"]
                if item != "raw_private_reasoning"
            ],
        ),
        (
            "prerequisite-self-closed",
            "status",
            "candidate_clear",
        ),
        (
            "candidate-schema-identities-erased",
            "candidate_schema_resource_identities_assigned",
            False,
        ),
        (
            "unissued-schemas-promoted-to-issued",
            "candidate_schemas_issued",
            True,
        ),
        (
            "admitted-record-identity-fabricated",
            "admitted_assurance_record_identity_issued",
            True,
        ),
        (
            "wrapper-identity-fabricated",
            "assured_decision_wrapper_identity_assigned",
            True,
        ),
        (
            "unissued-eligibility-ruleset-promoted-to-issued",
            "individual_eligibility_ruleset_issued",
            True,
        ),
        (
            "independent-eligibility-recomputation-fabricated",
            "independent_eligibility_recomputation_retained",
            True,
        ),
        # The construction now exists, so the escalation to refuse is no longer
        # claiming it -- it is silently dropping it while the profile still
        # carries it.
        (
            "same-actor-cryptographic-cobinding-dropped",
            "confirmation_gesture_and_authenticator_actor_cryptographically_co_bound",
            False,
        ),
        (
            "exact-crypto-input-dereference-fabricated",
            "exact_cryptographic_input_bytes_dereferenced_and_verified",
            True,
        ),
        (
            "frozen-corpus-census-erased",
            "complete_consumer_census_for_frozen_source_corpus",
            False,
        ),
        (
            "consumer-migration-promoted-to-complete",
            "current_consumers_migrated",
            True,
        ),
        (
            "migrated-consumer-count-fabricated",
            "migrated_consumer_count",
            1,
        ),
        (
            "end-to-end-refusal-fabricated",
            "end_to_end_consumer_refusal_proved",
            True,
        ),
        (
            "foundation-promoted-to-full-prq-013-closure",
            "individual_assurance_foundation_closes_prq_013",
            True,
        ),
        (
            "real-ceremony-fabricated",
            "real_human_ceremony_verified",
            True,
        ),
        (
            "live-ceremony-moved-into-gate-a",
            "gate_a_requires_live_protected_ceremony",
            True,
        ),
        (
            "live-ceremony-moved-outside-separate-gate-b-authorization",
            "real_protected_ceremony_stage",
            "gate_a_prerequisite",
        ),
        (
            "runtime-conformance-moved-out-of-gate-c",
            "runtime_conformance_stage",
            "gate_a_architecture_evidence",
        ),
        (
            "accountable-review-fabricated",
            "accountable_review_complete",
            True,
        ),
        (
            "consumer-census-binding-swapped",
            "consumer_census_binding",
            {
                **EXPECTED_HUMAN_DECISION_ASSURANCE[
                    "consumer_census_binding"
                ],
                "raw_sha256": "sha256:" + ("0" * 64),
            },
        ),
    )
    passed = 0
    for case_id, key, replacement in mutations:
        candidate = json.loads(json.dumps(safe))
        candidate[key] = replacement
        expected_reason = (
            f"human_decision_assurance.{key} must equal "
            f"{EXPECTED_HUMAN_DECISION_ASSURANCE[key]!r}"
        )
        observed = human_decision_assurance_errors(candidate)
        if expected_reason in observed:
            passed += 1
        else:
            errors.append(
                f"human decision-assurance known-bad {case_id} did not fire "
                f"its intended reason; got {observed!r}"
            )
    return passed


def next_dependency_contained_tranche_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["next_dependency_contained_tranche must be an object"]
    errors: list[str] = []
    if set(value) != set(EXPECTED_NEXT_DEPENDENCY_CONTAINED_TRANCHE):
        errors.append(
            "next_dependency_contained_tranche members must be closed and exact"
        )
    for key, expected_value in EXPECTED_NEXT_DEPENDENCY_CONTAINED_TRANCHE.items():
        if value.get(key) != expected_value:
            errors.append(
                f"next_dependency_contained_tranche.{key} must equal "
                f"{expected_value!r}"
            )
    return errors


def validate_next_tranche_known_bad(errors: list[str]) -> int:
    candidate = json.loads(
        json.dumps(EXPECTED_NEXT_DEPENDENCY_CONTAINED_TRANCHE)
    )
    candidate["may_start_after"].remove(
        "prq_013_individual_assurance_foundation_candidate_closure"
    )
    expected_reason = (
        "next_dependency_contained_tranche.may_start_after must equal "
        f"{EXPECTED_NEXT_DEPENDENCY_CONTAINED_TRANCHE['may_start_after']!r}"
    )
    observed = next_dependency_contained_tranche_errors(candidate)
    if expected_reason not in observed:
        errors.append(
            "next-tranche known-bad removed PRQ-013 without firing its "
            f"intended reason; got {observed!r}"
        )
        return 0
    return 1


def main() -> int:
    errors: list[str] = []
    try:
        inventory = load(INVENTORY)
        first_slice = load(FIRST_SLICE)
        canonical_audit = load(CANONICAL_AUDIT)
        canonical_profile_core = load(CANONICAL_PROFILE_CORE)
        canonical_profile_evidence = load(CANONICAL_PROFILE_EVIDENCE)
    except (OSError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        print(f"Gate A prerequisite closure: invalid evidence: {exc}", file=sys.stderr)
        return 1

    require(
        inventory.get("status") == "candidate_correction_in_progress_not_admitted",
        "inventory status must remain candidate_correction_in_progress_not_admitted",
        errors,
    )
    require(
        first_slice.get("schema_version") == "0.2.0"
        and first_slice.get("version") == "0.2.0"
        and first_slice.get("status")
        == "bounded_scope_candidate_c5_blocked_not_admitted",
        "first-slice source must be the honest 0.2 C5-blocked candidate",
        errors,
    )
    first_slice_verdict = first_slice.get("scope_verdict")
    require(
        isinstance(first_slice_verdict, dict)
        and first_slice_verdict.get("c1_through_c8_choices_resolved") is False
        and first_slice_verdict.get("may_construct_verification_assignment_member")
        is False,
        "first-slice source must keep C5/PRQ-009 unresolved and nonconstructible",
        errors,
    )
    conflict_rows = first_slice.get("resolved_conflicts")
    c5_rows = [
        row
        for row in conflict_rows
        if isinstance(row, dict) and row.get("conflict_id") == "C5"
    ] if isinstance(conflict_rows, list) else []
    require(
        len(c5_rows) == 1 and c5_rows[0].get("disposition") == "unresolved_blocking",
        "first-slice source must contain one unresolved_blocking C5 row",
        errors,
    )

    scope = inventory.get("exact_scope")
    counts = first_slice.get("counts")
    if not isinstance(scope, dict) or not isinstance(counts, dict):
        errors.append("exact_scope and first-slice counts must be objects")
    else:
        expected_scope = {
            "required_command_types": counts.get("required_commands_exact"),
            "outside_command_types": counts.get("outside_commands_exact"),
            "required_event_types": counts.get("required_event_types_exact"),
            "aggregate_state_reducer_families": counts.get(
                "aggregate_state_reducer_families_exact"
            ),
            "owner_modules": counts.get("owner_modules_exact"),
            "external_constitutional_prerequisites": counts.get(
                "external_constitutional_prerequisites_exact"
            ),
        }
        for key, expected in expected_scope.items():
            require(
                scope.get(key) == expected,
                f"exact_scope.{key} must equal first-slice count {expected!r}",
                errors,
            )
        require(
            scope.get("scope_change_requires_new_adversarial_review") is True,
            "scope changes must require a new adversarial review",
            errors,
        )

    expected_content_order = [
        "schema_resource_closure",
        "aggregate_state_member",
        "reducer_member",
        "event_member",
        "command_member",
        "pure_registry_snapshot",
        "engine_contract_root_core",
        "engine_contract_root_seal",
        "c0_core",
        "c0_seal",
    ]
    require(
        inventory.get("content_identity_order") == expected_content_order,
        "content identity order drifted",
        errors,
    )

    expected_constitutional_order = [
        "sealed_engine_root_and_c0",
        "signed_history_checkpoint",
        "inclusion_and_consistency_evidence",
        "independent_witness_observations",
        "witness_quorum_evaluation",
        "recovery_frontier_core",
        "recovery_frontier_verification",
        "p0_core",
        "p0_admission_seal",
        "handler_equality_evidence",
        "registry_activation_core",
        "registry_activation_seal",
        "later_command_admission",
    ]
    require(
        inventory.get("constitutional_evidence_order")
        == expected_constitutional_order,
        "constitutional evidence order drifted",
        errors,
    )

    integration = inventory.get("prospective_constitutional_profile_integration")
    require(
        isinstance(integration, dict)
        and integration.get("source_candidate_schema_bytes_conform") is False
        and integration.get("replacement_schema_identities_assigned") is False
        and integration.get("complete_transitive_consumer_migration") is False
        and integration.get("candidate_profile_parameters_frozen_for_review")
        is True
        and integration.get("candidate_digest_input_framing_frozen_for_review")
        is True
        and integration.get("candidate_profile_reference_shape_frozen_for_review")
        is True
        and integration.get("canonicalization_profile_frozen") is False
        and integration.get("digest_input_framing_frozen") is False
        and integration.get("replacement_digest_contract_shapes_frozen") is False
        and integration.get("disposition") == "blocking",
        "prospective constitutional profile must remain explicitly unintegrated and blocking",
        errors,
    )

    laws = inventory.get("identity_laws")
    if not isinstance(laws, dict):
        errors.append("identity_laws must be an object")
    else:
        required_false = [
            "member_embeds_parent_registry",
            "member_embeds_membership_proof",
            "member_embeds_checkpoint_or_activation",
            "p0_embeds_parent_activation",
            "evidence_enters_attested_core_preimage",
            "external_attestations_enter_seal_preimage",
            "re_signing_changes_core_identity",
            "currentness_is_content_identity",
            "historical_replay_uses_latest_root",
        ]
        for key in required_false:
            require(laws.get(key) is False, f"identity_laws.{key} must be false", errors)
        require(
            laws.get("activation_binds_exact_p0") is True,
            "activation must bind exact P0",
            errors,
        )
        require(
            laws.get("reverse_member_digest_edges") == "forbidden",
            "reverse member-digest edges must be forbidden",
            errors,
        )

    split = inventory.get("snapshot_history_split")
    if not isinstance(split, dict):
        errors.append("snapshot_history_split must be an object")
    else:
        snapshot = split.get("registry_snapshot")
        history = split.get("transparency_history")
        require(
            isinstance(snapshot, dict)
            and snapshot.get("temporal_append_only_claim") is False,
            "registry snapshot cannot claim temporal append-only ordering",
            errors,
        )
        require(
            isinstance(history, dict)
            and history.get("ordering") == "insertion_order"
            and history.get("sorted_by_member_key") is False,
            "transparency history must remain insertion ordered and unsorted",
            errors,
        )
        for key in (
            "membership_receipts_are_external",
            "history_checkpoints_are_external_to_registry_identity",
            "witness_cosignatures_are_external_to_checkpoint_identity",
        ):
            require(split.get(key) is True, f"{key} must remain true", errors)

    axes = inventory.get("explicit_version_axes")
    profile_axes = canonical_profile_core.get("version_axes")
    profile_axis_ids = [
        item.get("axis_id")
        for item in profile_axes
        if isinstance(item, dict)
    ] if isinstance(profile_axes, list) else []
    require(
        isinstance(axes, list)
        and len(axes) == 8
        and len(set(axes)) == len(axes)
        and profile_axis_ids == axes,
        "eight unique explicit version axes must equal the profile core",
        errors,
    )
    require(
        inventory.get("implicit_version_equality") == "forbidden"
        and inventory.get("implicit_upcast") == "forbidden",
        "implicit version equality and upcast must be forbidden",
        errors,
    )

    profile_candidate = inventory.get("canonical_profile_candidate")
    profile_binding = canonical_profile_evidence.get("profile_core_binding")
    migration_snapshot = canonical_profile_evidence.get("migration_snapshot")
    require(
        isinstance(profile_candidate, dict)
        and isinstance(profile_binding, dict)
        and isinstance(migration_snapshot, dict)
        and profile_candidate.get("profile_id")
        == "urn:odeya:canonicalization:odeya-jcs-0.1"
        == canonical_profile_core.get("profile_id")
        == profile_binding.get("profile_id")
        and profile_candidate.get("profile_version") == "0.1.0"
        == canonical_profile_core.get("profile_version")
        == profile_binding.get("profile_version")
        and profile_candidate.get("profile_core_ref")
        == "architecture/canonicalization-profile-core-candidate.json"
        and profile_candidate.get("profile_evidence_ref")
        == "architecture/canonicalization-profile-candidate-evidence.json"
        and profile_candidate.get("profile_core_schema_id")
        == "urn:odeya:schema:canonicalization-profile-core:0.5.0"
        and profile_candidate.get("parameter_status")
        == "candidate_parameters_frozen_for_review_profile_unissued"
        == canonical_profile_core.get("candidate_status")
        and profile_candidate.get("canonical_identity_issued") is False
        and profile_candidate.get("current_consumer_migration_complete") is False
        and migration_snapshot.get("current_consumer_migration_complete") is False
        and profile_candidate.get("operator_acceptance_ref") is None
        and profile_candidate.get("gate_a_disposition") == "blocked",
        "canonical profile candidate must bind the exact unissued core/evidence boundary",
        errors,
    )

    findings = inventory.get("findings")
    expected_ids = [f"PRQ-{index:03d}" for index in range(1, 14)]
    if not isinstance(findings, list):
        errors.append("findings must be an array")
    else:
        finding_ids = [
            item.get("finding_id") if isinstance(item, dict) else None
            for item in findings
        ]
        require(finding_ids == expected_ids, "findings must be exactly PRQ-001..013", errors)
        for item in findings:
            if isinstance(item, dict):
                require(
                    item.get("status")
                    in {
                        "blocking",
                        "unresolved_blocking",
                        "candidate_correction_in_progress",
                        "candidate_contract_in_progress",
                        "candidate_checker_in_progress",
                    },
                    f"{item.get('finding_id')} has an unrecognized status",
                    errors,
                )
                require(
                    isinstance(item.get("closure"), str) and bool(item["closure"]),
                    f"{item.get('finding_id')} needs a closure condition",
                    errors,
                )
        prq009 = findings[8] if len(findings) > 8 and isinstance(findings[8], dict) else {}
        prq008 = findings[7] if len(findings) > 7 and isinstance(findings[7], dict) else {}
        prq001 = findings[0] if findings and isinstance(findings[0], dict) else {}
        prq013 = findings[12] if len(findings) > 12 and isinstance(findings[12], dict) else {}
        require(
            prq001.get("finding_id") == "PRQ-001"
            and prq001.get("status") == "candidate_correction_in_progress"
            and "nonrecursive core" in prq001.get("closure", "")
            and "remain open" in prq001.get("closure", ""),
            "PRQ-001 must expose the frozen-for-review but unissued profile boundary",
            errors,
        )
        require(
            prq008.get("finding_id") == "PRQ-008"
            and prq008.get("status") == "unresolved_blocking"
            and "urn:odeya:schema:canonical-work-lease:0.8.0" in prq008.get("closure", "")
            and "present_unissued_candidate" in prq008.get("closure", ""),
            "PRQ-008 must expose the present-but-unadmitted canonical WorkLease resource as unresolved_blocking",
            errors,
        )
        errors.extend(prq_009_boundary_errors(prq009))
        require(
            prq013.get("finding_id") == "PRQ-013"
            and prq013.get("status") == "unresolved_blocking"
            and "three unissued HumanDecisionAssurance" in prq013.get(
                "closure", ""
            )
            and "zero current consumers are migrated" in prq013.get(
                "closure", ""
            )
            and "T0 individual-assurance foundation candidate"
            in prq013.get("closure", "")
            and "T1 AuthorityAssignment" in prq013.get("closure", "")
            and "required T2 command, event, state, reducer, currentness, quorum"
            in prq013.get("closure", "")
            and "same-actor confirmation/authenticator cryptographic co-binding"
            in prq013.get("closure", "")
            and "Gate A neither requires nor authorizes a live protected ceremony"
            in prq013.get("closure", "")
            and "separately authorized bounded Gate B probe"
            in prq013.get("closure", ""),
            "PRQ-013 must retain the blocking human decision-assurance boundary",
            errors,
        )
        first_slice_unresolved = first_slice.get("unresolved_prerequisites", [])
        require(
            isinstance(first_slice_unresolved, list)
            and len(first_slice_unresolved) == 1
            and first_slice_unresolved[0].get("prerequisite_id") == "PRQ-009"
            and first_slice_unresolved[0].get("status") == "unresolved_blocking",
            "Gate A PRQ-009 status must equal the first-slice blocking boundary",
            errors,
        )

    canonical_expected = {
        "CANON-SCHEMA-TIME-001": ("unprofiled_datetime_paths", 118),
        "CANON-SCHEMA-NUMBER-001": ("number_or_decimal_findings", 62),
        "CANON-SCHEMA-DIGEST-001": ("unscoped_digest_fields", 675),
        "CANON-SCHEMA-DEFS-001": ("divergent_common_definition_names", 56),
        "CANON-SCHEMA-PROFILE-001": ("unpinned_profile_bindings", 11),
        "CANON-FIXTURE-TIME-001": ("nonconformant_fixture_timestamps", 233),
    }
    canonical_start = inventory.get("canonical_profile_blockers_at_start")
    canonical_current = inventory.get("canonical_profile_current_audit")
    audit_findings = canonical_audit.get("blocking_findings")
    if (
        not isinstance(canonical_start, dict)
        or not isinstance(canonical_current, dict)
        or not isinstance(audit_findings, list)
    ):
        errors.append("canonical blocker evidence must be present")
    else:
        actual_by_id = {
            item.get("finding_id"): item.get("count")
            for item in audit_findings
            if isinstance(item, dict)
        }
        for finding_id, (inventory_key, frozen_start_count) in canonical_expected.items():
            require(
                canonical_start.get(inventory_key) == frozen_start_count,
                f"{inventory_key} must retain the tranche-start count {frozen_start_count}",
                errors,
            )
            # A resolved class vanishes from blocking_findings -- the audit
            # emits a finding only while its count is nonzero. Reading absence
            # as a mismatch made this a gate that could not observe success:
            # the accepted D1 disposition drove fixture timestamps to zero and
            # this check refused the truth. Absence is exactly count zero.
            require(
                actual_by_id.get(finding_id, 0) == canonical_current.get(inventory_key),
                f"{finding_id} current inventory count must match SCHEMA_AUDIT.json",
                errors,
            )
        require(
            canonical_start.get("source_checkpoint")
            == "f4429ce5ca71e58ebb5d65776a45ebb6a2a18889"
            and canonical_start.get("audit_raw_sha256")
            == "sha256:14e05ba802b032617c5567541c334d7a2e6f64397638ff6981394baec214688e",
            "canonical tranche-start checkpoint/audit identity drifted",
            errors,
        )
        current_audit_digest = "sha256:" + hashlib.sha256(
            CANONICAL_AUDIT.read_bytes()
        ).hexdigest()
        require(
            canonical_current.get("audit_raw_sha256") == current_audit_digest,
            "canonical current audit raw digest must match SCHEMA_AUDIT.json",
            errors,
        )
        # the tranche start is history and stays blocked; the current state
        # follows the measured audit disposition. Reaching zero once exposed a
        # gate that could not observe success (ADR 0038); this pairing can see
        # both worlds while keeping the profile unissued in each.
        measured_disposition = canonical_audit.get("gate_a_disposition")
        consistent_current = {
            "blocked": "blocked",
            "candidate_clear": "candidate_clear_unissued_pending_gate_a",
        }.get(measured_disposition)
        require(
            canonical_start.get("profile_status") == "blocked"
            and consistent_current is not None
            and canonical_current.get("profile_status") == consistent_current,
            "canonical profile status must match the measured audit disposition "
            "while remaining unissued",
            errors,
        )
        require(
            canonical_current.get("schema_count")
            == canonical_audit.get("schema_count")
            == migration_snapshot.get("schema_count")
            and canonical_current.get("fixture_count")
            == canonical_audit.get("fixture_count")
            == migration_snapshot.get("fixture_count"),
            "canonical current audit corpus counts must equal profile evidence",
            errors,
        )

    construction = inventory.get("construction_inventory_at_start")
    if not isinstance(construction, dict) or not isinstance(counts, dict):
        errors.append("construction inventory must be present")
    else:
        count_map = {
            "closed_command_payload_candidates_not_admitted":
                "closed_required_payload_candidates_not_admitted",
            "missing_command_payload_schemas": "missing_required_payload_contracts",
            "missing_command_contract_records": "missing_command_contract_records",
            "missing_event_contract_records": "missing_event_contract_records",
            "missing_aggregate_state_records": "missing_state_subject_records",
            "missing_reducer_contract_records": "missing_reducer_contract_records",
        }
        for inventory_key, first_slice_key in count_map.items():
            require(
                construction.get(inventory_key) == counts.get(first_slice_key),
                f"construction_inventory_at_start.{inventory_key} must match first slice",
                errors,
            )
        for key in (
            "real_engine_contract_root",
            "real_c0_bundle",
            "real_witnessed_checkpoint",
            "real_recovery_frontier",
            "real_p0",
            "real_handler_equality_report",
            "real_registry_activation",
        ):
            require(construction.get(key) is False, f"{key} must remain false", errors)

    external = first_slice.get("external_prerequisites")
    if not isinstance(external, list) or len(external) != 1 or not isinstance(external[0], dict):
        errors.append("first slice must contain one exact external prerequisite")
    else:
        bindings = external[0].get("required_bindings")
        require(isinstance(bindings, list), "P0 required_bindings must be an array", errors)
        if isinstance(bindings, list):
            require(
                "registry_activation_identity_sequence_and_digest" not in bindings,
                "P0 required bindings cannot bind the parent activation",
                errors,
            )
            require(
                "activation_independent_subject_excluding_activation_identity_sequence_reference_and_digest"
                in bindings,
                "P0 must explicitly exclude activation identity, sequence, reference, and digest",
                errors,
            )
        require(
            external[0].get("current_instance_status") == "missing",
            "no real P0 instance may be claimed",
            errors,
        )

    for decision_ref in inventory.get("decision_refs", []):
        require(
            isinstance(decision_ref, str) and (ROOT / decision_ref).is_file(),
            f"missing decision record {decision_ref!r}",
            errors,
        )
    require(
        (ROOT / str(inventory.get("plan_ref", ""))).is_file(),
        "prerequisite closure plan is missing",
        errors,
    )

    standards_refs = inventory.get("standards_comparison_refs")
    require(
        isinstance(standards_refs, list)
        and len(standards_refs) >= 10
        and len(standards_refs) == len(set(standards_refs))
        and all(isinstance(ref, str) and ref.startswith("https://") for ref in standards_refs),
        "standards comparison refs must be unique HTTPS primary references",
        errors,
    )

    publication_errors = repository_publication_errors(
        inventory.get("repository_publication")
    )
    errors.extend(publication_errors)
    repository_publication_known_bads = (
        validate_repository_publication_known_bads(errors)
    )

    errors.extend(refusal_boundary_errors(inventory.get("refusal")))
    refusal_boundary_known_bads = validate_refusal_boundary_known_bads(errors)

    errors.extend(
        human_decision_assurance_errors(
            inventory.get("human_decision_assurance")
        )
    )
    human_decision_assurance_known_bads = (
        validate_human_decision_assurance_known_bads(errors)
    )
    errors.extend(
        next_dependency_contained_tranche_errors(
            inventory.get("next_dependency_contained_tranche")
        )
    )
    next_tranche_known_bads = validate_next_tranche_known_bad(errors)
    prq_009_boundary_known_bads = validate_prq_009_boundary_known_bads(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"Gate A prerequisite closure: FAIL ({len(errors)} error(s)); "
            "candidate remains blocked",
            file=sys.stderr,
        )
        return 1

    print(
        "Gate A prerequisite closure: PASS; "
        "13 findings tracked; exact scope 43 commands / 60 events / "
        "25 families / 11 owners; "
        f"{repository_publication_known_bads} repository-publication "
        f"and {refusal_boundary_known_bads} refusal-boundary known-bads "
        f"and {human_decision_assurance_known_bads} "
        "human-decision-assurance known-bads "
        f"and {prq_009_boundary_known_bads} PRQ-009 boundary known-bads "
        f"and {next_tranche_known_bads} next-tranche known-bad "
        "rejected; candidate remains blocked and inactive"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
