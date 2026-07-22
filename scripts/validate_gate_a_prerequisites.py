#!/usr/bin/env python3
"""Validate the architecture-only Gate A prerequisite closure inventory.

This checker proves cross-file inventory equality and nonrecursive dependency
intent only. A pass is not a frozen canonical profile, immutable registry,
constitutional admission, Gate A acceptance, or runtime authorization.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
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
HDA_CONTEXT_REVIEW = (
    ROOT / "architecture/human-decision-assurance-context-isolated-technical-review.json"
)
HDA_CONTEXT_CLOSURE_OBSERVATION = (
    ROOT
    / "architecture/human-decision-assurance-context-review-closure-observation.json"
)
HDA_CONTEXT_PYTHON_INSTALL_OBSERVATION = (
    ROOT
    / "architecture/human-decision-assurance-context-review-python-install-observation.json"
)
HDA_CONTEXT_PYTHON_INSTALL_REPORT = (
    ROOT
    / "architecture/human-decision-assurance-context-review-python-install-pip-report.json"
)
HDA_CONTEXT_PYTHON_INSTALL_REPORT_RUN_02 = (
    ROOT
    / "architecture/human-decision-assurance-context-review-python-install-pip-report-run-02.json"
)
HDA_CONTEXT_PYTHON_INSTALL_GENERATOR = (
    ROOT
    / "scripts/generate_human_decision_assurance_context_review_python_install.py"
)
HDA_GENERATION_MANIFEST = (
    ROOT / "tests/human-decision-assurance-successor/generation-manifest.json"
)
HDA_SUCCESSOR_GENERATOR = (
    ROOT / "scripts/generate_human_decision_assurance_successor.py"
)
# path, governed heading, end heading, unit kind, unique marker, ordinal,
# SHA-256 of the normalized exact unit, then its complete governed section.
CURRENT_ASSURANCE_UNITS = (
    (
        "docs/HUMAN_DECISION_ASSURANCE.md", "## Retained nonclaims", None,
        "bullet", "The application confirmation receipt and authenticator actor", 3,
        "22d92e1a3afd115ef693ab611315b84f27c740f893063e3de68b5d4187220e4c",
        "33926437af749d17ff4810c4226ba17cdb711018fe7fd6532d890e43d74d7410",
    ),
    (
        "tests/human-decision-assurance/README.md", "## Exact-byte, challenge, and confirmation checks", None,
        "paragraph", "The adopted v2 construction co-binds the two acts", 3,
        "4047524fdc329dbaf89ddcfa4c42fac4e08098a0a08eda5eb5214b05f1d84bb7",
        "ddb3b51909c3904709156bf707b8c00af6064bad415fe4c8ccf547941afef29b",
    ),
    (
        "docs/THREAT_MODEL.md", "## Abuse-case register", None, "table_row", "| T29 |", None,
        "9ff1f0d40db48d6f85e0211a6c801bb0c668139dbb266203b83bbd45b7218574",
        "3bf778d024e5a0d90cca8a65bc142ec23a85f063590a263a62de12aad26a4ce7",
    ),
    (
        "docs/THREAT_MODEL.md", "## Abuse-case register", None, "paragraph", "The positive synthetic chain is not a counterexample", 3,
        "31bc358eaa531e5e37889fa1a548d74b9f286e9562e08c34775771bf4c1cb643",
        "3bf778d024e5a0d90cca8a65bc142ec23a85f063590a263a62de12aad26a4ce7",
    ),
    (
        "docs/ARCHITECTURE_STATUS.md", "## Readiness by Gate A area", None, "table_row", "| G3 security/authority |", None,
        "0f6604e35890637bb7c14a990f53468bc0a2274fa4a4a139e94dd3bb459ba8ed",
        "538465127b1fc753c62fb6c505caecd192ce105595761c8a97d4ff68ac982881",
    ),
    (
        "docs/ARCHITECTURE_STATUS.md", "## Critical blockers", None, "table_row", "| A-016 |", None,
        "c35e7cf3acee32233ab9216f4f317c48761465b490b9a0a36c56f5609931e11b",
        "3f26ef69b2d2fb5d4fe510bf5c893a671758f42ddb99a8af5be32c7346117caa",
    ),
    (
        "docs/SESSION_HANDOFF.md", "## What this lane established, and where to put pressure next", None,
        "bullet", "**PRQ-013 now has retained byte-bound/recomputation candidate evidence, not closure.**", 1,
        "995d7d3975047f8d64f41d137059b316e932202ab3d20e23b28b5b48af6bbc28",
        "dd32bdd71a39c0b97f5bfdd4b1ee51bb60706c76ba9c31790afa144a725d76c7",
    ),
    (
        "docs/SESSION_HANDOFF.md", "## Active PRQ-013 candidate — resolve release status from Git", None,
        "paragraph", "Those are structural and bounded-semantic candidate measurements", 7,
        "e0e4fd58d204a82cbcc698f436818e390225733fd52474dd96f9f449d986852c",
        "d0c98fbd69cc4784c4fd03bd56ecdedd5bd7a2e6e2936a6acba849706bd51759",
    ),
    (
        "docs/decisions/0092-bind-human-decisions-through-an-external-assurance-wrapper.md",
        "# ADR 0092: Bind human decisions through an external assurance wrapper", "## Context", "section", "", None,
        "176d0c8bddd27ff718f78617f0248f2a566a51729a942752cf3212efb0c5fd51",
        "176d0c8bddd27ff718f78617f0248f2a566a51729a942752cf3212efb0c5fd51",
    ),
    (
        "docs/decisions/0094-bind-current-status-surfaces-to-retained-machine-evidence.md",
        "## Decision", None, "section", "", None, "01aaf2f2943af931689598888ff9d709b750863360f02505d575242eaa8f7273",
        "01aaf2f2943af931689598888ff9d709b750863360f02505d575242eaa8f7273",
    ),
)

RECOVERY_HANDOFF = "docs/SESSION_HANDOFF.md"
RECOVERY_HEADING = "## Current repository recovery identity"
PUBLISHED_BASELINE = "05c2c3b18a3987c337a8c76d8db55ea4eb72bfa9"
PUBLISHED_BASELINE_TREE = "35f3622e8c3b883f33b0e5761686f6972ec1f67e"
RECOVERY_INVARIANT_SHA256 = "37b25307a3691eb275d6d457e2643e7400aa09d700b1fdb37ac63170bcb3cf2a"
# SHA-256 of the normalized 51-line recovery program. Its separately named
# cardinality line keeps the single-parent invariant reviewable.
EXPECTED_RECOVERY_PROGRAM_SHA256 = "0025c657f0676eb7ba995bd84ce2f581311d4a60ca8d29d372f4e35c5b095c6b"
PARENT_CARDINALITY_LINE = 'test "$(git rev-list --parents -n 1 "$HEAD_COMMIT" | awk \'{print NF}\')" = 2'
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
            "path": (
                "schemas/human-decision-assurance-backing-byte-"
                "verification-receipt.schema.json"
            ),
            "schema_id": (
                "urn:odeya:schema:human-decision-assurance-backing-byte-"
                "verification-receipt:0.1.0"
            ),
        },
        {
            "path": (
                "schemas/human-decision-assurance-eligibility-comparison-"
                "receipt.schema.json"
            ),
            "schema_id": (
                "urn:odeya:schema:human-decision-assurance-eligibility-"
                "comparison-receipt:0.1.0"
            ),
        },
        {
            "path": (
                "schemas/human-decision-assurance-eligibility-"
                "recomputation-result.schema.json"
            ),
            "schema_id": (
                "urn:odeya:schema:human-decision-assurance-eligibility-"
                "recomputation-result:0.1.0"
            ),
        },
        {
            "path": "schemas/human-decision-assurance-evidence-v0-2.schema.json",
            "schema_id":
                "urn:odeya:schema:human-decision-assurance-evidence:0.2.0",
        },
        {
            "path": "schemas/human-decision-assurance-evidence.schema.json",
            "schema_id":
                "urn:odeya:schema:human-decision-assurance-evidence:0.1.0",
        },
        {
            "path": "schemas/human-decision-assurance-seal-v0-2.schema.json",
            "schema_id":
                "urn:odeya:schema:human-decision-assurance-seal:0.2.0",
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
        "architecture/human-decision-assurance-individual-eligibility-ruleset-v2-candidate.json",
    "individual_eligibility_ruleset_issued": False,
    "independent_eligibility_recomputation_retained": True,
    "independent_recomputation_scope": (
        "three_source_separated_nonsharing_language_implementations_not_"
        "organizational_independence"
    ),
    "organizational_independence_proven": False,
    "successor_generation_manifest_ref": (
        "tests/human-decision-assurance-successor/generation-manifest.json"
    ),
    "successor_generation_manifest_binding": {
        "artifact_id": "hda-successor-generation-manifest.synthetic.0005",
        "raw_sha256": (
            "sha256:97062b38a14d5bdccf5ad87c547c62388e7cd82256a445f631856aecee54e1d9"
        ),
        "byte_count": 24530,
    },
    "synthetic_conformance_backing_bytes_dereferenced_and_verified": True,
    "synthetic_content_addressed_backing_preimage_count": 14,
    "successor_expectation_free_vector_count": 44,
    "successor_chain_known_bad_count": 49,
    "context_isolated_technical_review_ref": (
        "architecture/human-decision-assurance-context-isolated-technical-review.json"
    ),
    # The report cannot bind a validator that embeds the report's own digest.
    # These two values are therefore derived from the strict report bytes in
    # human_decision_assurance_errors rather than copied into validator source.
    "context_isolated_technical_review_binding": None,
    "context_isolated_technical_review_retained": True,
    "context_isolated_technical_review_bounded_result": None,
    "context_isolated_technical_review_is_accountable": False,
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
            "sha256:f3214129e18f9db38a6c00a517712190cf257b62b51f42a032cd5af033820e98",
        "byte_count": 151958,
        "baseline_git_commit": "56e8062334fb81bba955ba137be690e085d4c88e",
        "baseline_git_tree": "d90ed6dd8c54b91a1e503358f98ecaa08c766fa3",
        "baseline_schema_count": 112,
        "candidate_mechanism_schema_count": 8,
        "current_union_schema_count": 120,
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
    "co_binding_decision_ref":
        "docs/decisions/0093-co-bind-the-confirmation-gesture-through-a-two-phase-challenge.md",
    "phase_two_reconstruction_decision_ref":
        "docs/decisions/0096-reconstruct-the-successor-phase-two-binding-before-technical-review.md",
    "closure_disposition":
        "retain_unissued_t0_byte_bound_and_source_separated_recomputation_"
        "candidate_evidence_with_eleven_round_context_isolated_correlated_"
        "nonaccountable_review_no_grounded_refutation_observed_within_declared_"
        "attacks_not_correct_or_approved_then_"
        "construct_t1_t2_dependencies_and_unissued_wrapper_successors_prove_"
        "transitive_migration_end_to_end_refusal_and_accountable_gate_a_review_"
        "real_ceremony_deferred_to_separately_authorized_gate_b_probe",
}


def normalize_prose(value: str) -> str:
    return " ".join(value.split())


def blank_non_newlines(value: str) -> str:
    return "".join("\n" if character == "\n" else " " for character in value)


def mask_html_comments(value: str) -> str:
    return re.sub(
        r"<!--.*?(?:-->|$)",
        lambda match: blank_non_newlines(match.group()),
        value,
        flags=re.DOTALL,
    )


def visible_markdown(value: str) -> str:
    lines = mask_html_comments(value).splitlines(keepends=True)
    fence: str | None = None
    for index, line in enumerate(lines):
        opening = re.match(r"^[ \t]*(`{3,}|~{3,})", line)
        if fence is None and opening is not None:
            fence = opening.group(1)
            lines[index] = blank_non_newlines(line)
        elif fence is None and re.match(r"^(?: {4}|\t)", line):
            lines[index] = blank_non_newlines(line)
        elif fence is not None:
            lines[index] = blank_non_newlines(line)
            if re.match(
                rf"^[ \t]*{re.escape(fence[0])}{{{len(fence)},}}[ \t]*(?:\r?\n)?$",
                line,
            ):
                fence = None
    return "".join(lines)


def heading_parts(line: str) -> tuple[int, str] | None:
    match = re.fullmatch(r"[ \t]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*", line)
    if match is None:
        return None
    title = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(2)).strip()
    return len(match.group(1)), normalize_prose(title)


def governed_section(raw: str, heading: str, until_heading: str | None = None) -> tuple[str | None, str | None, str | None]:
    visible = visible_markdown(raw)
    headings: list[tuple[int, int, int, str]] = []
    for match in re.finditer(r"(?m)^.*$", visible):
        parts = heading_parts(match.group())
        if parts is not None:
            headings.append((match.start(), match.end(), *parts))
    target = heading_parts(heading)
    assert target is not None
    matches = [item for item in headings if item[3] == target[1]]
    if len(matches) != 1 or matches[0][2] != target[0]:
        return None, None, (
            f"governed heading {target[1]!r} must occur exactly once at "
            f"level {target[0]}"
        )
    current = matches[0]
    if until_heading is not None:
        endpoint = heading_parts(until_heading)
        assert endpoint is not None
        ends = [item for item in headings if item[3] == endpoint[1]]
        if len(ends) != 1 or ends[0][2] != endpoint[0] or ends[0][0] <= current[1]:
            return None, None, (
                f"governed end heading {endpoint[1]!r} must occur exactly once "
                f"at level {endpoint[0]} after {target[1]!r}"
            )
        end = ends[0][0]
    else:
        end = next(
            (
                item[0]
                for item in headings
                if item[0] > current[1] and item[2] <= target[0]
            ),
            len(raw),
        )
    return raw[current[1]:end], visible[current[1]:end], None


def current_file_text(relative_path: str, overrides: dict[str, str | None] | None) -> str | None:
    if overrides is not None and relative_path in overrides:
        return overrides[relative_path]
    try:
        return (ROOT / relative_path).read_text(encoding="utf-8")
    except OSError:
        return None


def units_of_kind(section: str, kind: str) -> list[str]:
    if kind == "section":
        return [normalize_prose(section)]
    if kind == "paragraph":
        return [
            normalize_prose(item)
            for item in re.split(r"\n[ \t]*\n", section)
            if normalize_prose(item)
        ]
    if kind == "table_row":
        lines = section.splitlines()
        separators = [
            index
            for index, line in enumerate(lines)
            if re.fullmatch(r"[ \t]*\|(?:[ \t]*:?-+:?[ \t]*\|)+[ \t]*", line)
        ]
        if len(separators) != 1 or separators[0] == 0:
            return []
        start, end = separators[0] - 1, separators[0] + 1
        while end < len(lines) and re.fullmatch(r"[ \t]*\|.*\|[ \t]*", lines[end]):
            end += 1
        return [
            normalize_prose(line)
            for line in lines[start:end]
            if re.fullmatch(r"[ \t]*\|.*\|[ \t]*", line)
        ]
    lines = section.splitlines()
    starts = [
        index
        for index, line in enumerate(lines)
        if re.match(r"^[-*+][ \t]+", line)
    ]
    return [
        normalize_prose("\n".join(lines[start:end]))
        for start, end in zip(starts, [*starts[1:], len(lines)], strict=True)
    ]


def exact_unit_errors(
    prefix: str,
    section: str,
    kind: str,
    marker: str,
    ordinal: int | None,
    expected_digest: str,
) -> list[str]:
    units = units_of_kind(section, kind)
    matches = units if kind == "section" else [unit for unit in units if marker in unit]
    label = marker or "complete section"
    if kind != "section" and normalize_prose(section).count(marker) != 1:
        matches = []
    if len(matches) != 1:
        return [
            f"{prefix}: governed {kind} marker {label!r} must occur exactly once; "
            f"observed {len(matches)}"
        ]
    unit = matches[0]
    failures: list[str] = []
    if ordinal is not None and units.index(unit) != ordinal:
        failures.append(f"{prefix}: governed {kind} {label!r} moved from ordinal {ordinal}")
    if hashlib.sha256(unit.encode()).hexdigest() != expected_digest:
        failures.append(f"{prefix}: governed {kind} {label!r} does not match its pinned exact unit")
    return failures


def assurance_truth_surface_errors(
    overrides: dict[str, str | None] | None = None,
) -> list[str]:
    failures: list[str] = []
    cache: dict[tuple[str, str, str | None], str | None] = {}
    for (
        path, heading, endpoint, kind, marker, ordinal, digest, section_digest,
    ) in CURRENT_ASSURANCE_UNITS:
        prefix = f"{path} [{heading}]"
        raw = current_file_text(path, overrides)
        if raw is None:
            failures.append(f"{path}: required current truth-surface file is missing")
            continue
        key = (path, heading, endpoint)
        if key not in cache:
            _, section, section_error = governed_section(raw, heading, endpoint)
            if section_error is not None:
                failures.append(f"{prefix}: {section_error}")
                cache[key] = None
            else:
                assert section is not None
                cache[key] = section
                if (
                    hashlib.sha256(normalize_prose(section).encode()).hexdigest()
                    != section_digest
                ):
                    failures.append(
                        f"{prefix}: governed section does not match its pinned "
                        "complete current structure"
                    )
        section = cache[key]
        if section is not None:
            failures.extend(
                exact_unit_errors(prefix, section, kind, marker, ordinal, digest)
            )
    return failures


def replace_once(raw: str, old: str, new: str, label: str, errors: list[str]) -> str:
    if raw.count(old) != 1:
        errors.append(f"cannot construct truth-surface self-test {label!r}")
        return raw
    return raw.replace(old, new, 1)


def expect_self_test(label: str, observed: list[str], expected: str, errors: list[str]) -> int:
    if expected in observed:
        return 1
    errors.append(
        f"truth-surface self-test {label!r} missed intended error "
        f"{expected!r}; observed {observed!r}"
    )
    return 0


def assurance_truth_surface_known_bad_self_tests(errors: list[str]) -> int:
    hda_path = "docs/HUMAN_DECISION_ASSURANCE.md"
    status_path = "docs/ARCHITECTURE_STATUS.md"
    threat_path = "docs/THREAT_MODEL.md"
    adr_path = CURRENT_ASSURANCE_UNITS[-1][0]
    hda = (ROOT / hda_path).read_text(encoding="utf-8")
    status = (ROOT / status_path).read_text(encoding="utf-8")
    threat = (ROOT / threat_path).read_text(encoding="utf-8")
    if safe := assurance_truth_surface_errors():
        errors.append(f"assurance truth-surface safe control failed: {safe!r}")
    marker = "The application confirmation receipt and authenticator actor"
    prefix = f"{hda_path} [## Retained nonclaims]"
    missing = f"{prefix}: governed bullet marker {marker!r} must occur exactly once; observed 0"
    hidden = replace_once(hda, marker, f"<!-- {marker} -->", "hidden", errors)
    start = hda.find("- The application confirmation receipt")
    end = hda.find("\n- The exact singleton ruleset", start)
    if start < 0 or end < 0:
        errors.append("cannot construct truth-surface self-test 'fenced-current-unit'")
        fenced = hda
    else:
        fenced = hda[:start] + "```text\n" + hda[start:end] + "\n```" + hda[end:]
    wrapped = replace_once(
        hda, "## Retained nonclaims",
        "## Retained nonclaims\n\nThe signed\nchallenge does not commit to the confirmation-receipt digest.",
        "wrapped-stale", errors,
    )
    omitted_receipt = replace_once(
        hda,
        "## Retained nonclaims",
        "## Retained nonclaims\n\n"
        "Current authentication omits all confirmation-receipt material.",
        "omitted-receipt-paragraph",
        errors,
    )
    nested = replace_once(
        hda, "## Retained nonclaims",
        "## Retained nonclaims\n\n### Retained nonclaims ###",
        "nested-closing-heading", errors,
    )
    suffix = hda[:end] + " This assertion is false." + hda[end:] if end >= 0 else hda
    a016_rows = [line for line in status.splitlines() if line.startswith("| A-016 |")]
    a016_cells = (
        [cell.strip() for cell in a016_rows[0][1:-1].split("|")]
        if len(a016_rows) == 1
        else []
    )
    if len(a016_cells) != 4:
        errors.append("cannot construct truth-surface self-test 'row-move'")
        moved = status
    else:
        current_blocker = a016_cells[2]
        moved = replace_once(
            status, current_blocker, "The A-016 boundary was moved.", "row-move", errors,
        )
        if moved != status:
            moved = replace_once(
                moved,
                "| A-015 | Critical |",
                f"| A-015 | Critical | {current_blocker}. ",
                "row-move-target",
                errors,
            )
    a017 = replace_once(
        status,
        "\n\n## Machine-family maturity",
        "\n| A-017 | Critical | The confirmation receipt is excluded from "
        "authentication. | Refuse the contradictory status claim |\n\n"
        "## Machine-family maturity",
        "A-017-receipt-exclusion",
        errors,
    )
    t30 = replace_once(
        threat,
        "\n\nEvery row needs at least one known-bad architecture fixture before Gate A.",
        "\n| T30 | Current authentication omits all confirmation-receipt material. | "
        "Contradicts the current construction | Blocked |\n\n"
        "Every row needs at least one known-bad architecture fixture before Gate A.",
        "T30-receipt-omission",
        errors,
    )
    complete = "governed section does not match its pinned complete current structure"
    mutants = (
        ("hidden-current-unit", {hda_path: hidden}, missing),
        ("fenced-current-unit", {hda_path: fenced}, missing),
        ("wrapped-stale-plus-correct", {hda_path: wrapped}, f"{prefix}: {complete}"),
        ("omitted-receipt-paragraph", {hda_path: omitted_receipt}, f"{prefix}: {complete}"),
        ("nested-closing-heading", {hda_path: nested}, f"{prefix}: governed heading 'Retained nonclaims' must occur exactly once at level 2"),
        ("unit-suffix-contradiction", {hda_path: suffix}, f"{prefix}: governed bullet {marker!r} does not match its pinned exact unit"),
        ("A-016-assertion-moved-to-A-015", {status_path: moved}, f"{status_path} [## Critical blockers]: governed table_row '| A-016 |' does not match its pinned exact unit"),
        ("A-017-receipt-exclusion", {status_path: a017}, f"{status_path} [## Critical blockers]: {complete}"),
        ("T30-receipt-omission", {threat_path: t30}, f"{threat_path} [## Abuse-case register]: {complete}"),
        ("missing-ADR-0094", {adr_path: None}, f"{adr_path}: required current truth-surface file is missing"),
    )
    return sum(
        expect_self_test(label, assurance_truth_surface_errors(override), expected, errors)
        for label, override, expected in mutants
    )


def fenced_blocks(value: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    fence: str | None = None
    info = ""
    body: list[str] = []
    for line in mask_html_comments(value).splitlines():
        marker = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", line)
        if fence is None and marker is not None:
            fence, info, body = marker.group(1), marker.group(2).strip(), []
        elif fence is not None and re.fullmatch(
            rf"[ \t]*{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line
        ):
            blocks.append((info, "\n".join(body)))
            fence = None
        elif fence is not None:
            body.append(line)
    return blocks


def recovery_truth_surface_errors(
    overrides: dict[str, str | None] | None = None,
) -> list[str]:
    prefix = f"{RECOVERY_HANDOFF} [{RECOVERY_HEADING}]"
    raw = current_file_text(RECOVERY_HANDOFF, overrides)
    if raw is None:
        return [f"{RECOVERY_HANDOFF}: required recovery handoff is missing"]
    raw_section, section, section_error = governed_section(raw, RECOVERY_HEADING)
    if section_error is not None:
        return [f"{prefix}: {section_error}"]
    assert raw_section is not None and section is not None
    failures: list[str] = []
    labels = (
        (
            "baseline", PUBLISHED_BASELINE,
            r"(?m)^- Exact published baseline observed at recovery:[ \t]*\n"
            r"[ \t]+`([0-9a-f]{40})`[ \t]*$",
        ),
        (
            "tree", PUBLISHED_BASELINE_TREE,
            r"(?m)^- Exact published-baseline tree:[ \t]*\n"
            r"[ \t]+`([0-9a-f]{40})`[ \t]*$",
        ),
    )
    for label, expected, pattern in labels:
        observed = re.findall(pattern, section)
        literal = "Exact published baseline observed at recovery:" if label == "baseline" else "Exact published-baseline tree:"
        if observed != [expected] or section.count(literal) != 1:
            failures.append(
                f"{prefix}: recovery {label} label must occur exactly once and "
                f"equal {expected}"
            )
    unexpected = sorted(
        set(re.findall(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", section))
        - {PUBLISHED_BASELINE, PUBLISHED_BASELINE_TREE}
    )
    if unexpected:
        failures.append(f"{prefix}: unexpected full Git identities {unexpected!r}")
    blocks = fenced_blocks(raw_section)
    if len(blocks) != 1 or blocks[0][0] != "bash":
        failures.append(f"{prefix}: recovery program must be exactly one bash fence")
    else:
        program = "\n".join(line.rstrip() for line in blocks[0][1].strip().splitlines())
        if hashlib.sha256(program.encode()).hexdigest() != EXPECTED_RECOVERY_PROGRAM_SHA256:
            failures.append(f"{prefix}: recovery program does not equal pinned expected program")
        if program.count(PARENT_CARDINALITY_LINE) != 1:
            failures.append(f"{prefix}: recovery program lost its one-parent cardinality guard")
    if section.count("Expected invariants:") != 1:
        failures.append(f"{prefix}: Expected invariants marker must occur exactly once")
    else:
        invariant_section = section.split("Expected invariants:", 1)[1]
        marker = "the active `HEAD` is either that already-published baseline"
        invariant_errors = exact_unit_errors(
            prefix,
            invariant_section,
            "bullet",
            marker,
            3,
            RECOVERY_INVARIANT_SHA256,
        )
        failures.extend(invariant_errors)
    return failures


def recovery_truth_surface_known_bad_self_tests(errors: list[str]) -> int:
    raw = (ROOT / RECOVERY_HANDOFF).read_text(encoding="utf-8")
    if safe := recovery_truth_surface_errors({RECOVERY_HANDOFF: raw}):
        errors.append(f"recovery truth-surface safe control failed: {safe!r}")
    prefix = f"{RECOVERY_HANDOFF} [{RECOVERY_HEADING}]"
    program_error = f"{prefix}: recovery program does not equal pinned expected program"
    mutations = (
        (
            "inverted-remote-main", program_error,
            'test "$REMOTE_MAIN" = "$PUBLISHED_BASELINE" || test "$REMOTE_MAIN" = "$HEAD_COMMIT"',
            'test "$REMOTE_MAIN" != "$PUBLISHED_BASELINE" || test "$REMOTE_MAIN" != "$HEAD_COMMIT"',
        ),
        (
            "two-commit-range", program_error,
            'test "$(git rev-list --count "$PUBLISHED_BASELINE..$HEAD_COMMIT")" = 1',
            'test "$(git rev-list --count "$PUBLISHED_BASELINE..$HEAD_COMMIT")" = 2',
        ),
        (
            "merge-parent-guard-removed",
            f"{prefix}: recovery program lost its one-parent cardinality guard",
            '  test "$(git rev-list --parents -n 1 "$HEAD_COMMIT" | awk \'{print NF}\')" = 2\n',
            "",
        ),
    )
    count = 0
    for label, expected, old, new in mutations:
        mutant = replace_once(raw, old, new, label, errors)
        count += expect_self_test(
            label, recovery_truth_surface_errors({RECOVERY_HANDOFF: mutant}),
            expected, errors,
        )
    baseline = f"- Exact published baseline observed at recovery:\n  `{PUBLISHED_BASELINE}`"
    duplicate = baseline + f"\n- Exact published baseline observed at recovery:\n  `{PUBLISHED_BASELINE_TREE}`"
    mutant = replace_once(raw, baseline, duplicate, "duplicate-baseline-label", errors)
    count += expect_self_test(
        "duplicate-baseline-label", recovery_truth_surface_errors({RECOVERY_HANDOFF: mutant}),
        f"{prefix}: recovery baseline label must occur exactly once and equal {PUBLISHED_BASELINE}",
        errors,
    )
    invariant = "multi-commit range fails recovery;"
    mutant = replace_once(
        raw, invariant, invariant + " this statement is false;",
        "recovery-invariant-suffix", errors,
    )
    count += expect_self_test(
        "recovery-invariant-suffix", recovery_truth_surface_errors({RECOVERY_HANDOFF: mutant}),
        (
            f"{prefix}: governed bullet 'the active `HEAD` is either that "
            "already-published baseline' does not match its pinned exact unit"
        ),
        errors,
    )
    return count


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


def canonical_observation_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def raw_file_binding(path: Path) -> tuple[str, int]:
    raw = path.read_bytes()
    return "sha256:" + hashlib.sha256(raw).hexdigest(), len(raw)


def valid_repository_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return (
        not path.is_absolute()
        and ".." not in path.parts
        and "." not in path.parts
        and path.as_posix() == value
    )


def json_pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


CONTEXT_REVIEW_BINDING_IDENTITY_KEYS = (
    "artifact_id",
    "profile_id",
    "ruleset_id",
    "schema_resource_id",
)


def context_review_binding_identity(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        key: value[key]
        for key in CONTEXT_REVIEW_BINDING_IDENTITY_KEYS
        if isinstance(value.get(key), str) and value[key]
    }


def context_review_blob_descriptor(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("repository_blob_path"), str)
        and isinstance(value.get("content_address"), str)
        and "byte_count" in value
    )


def context_review_executable_observation(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("function"), str)
        and isinstance(value.get("invocation_path"), str)
        and isinstance(value.get("resolved_path"), str)
        and isinstance(value.get("raw_sha256"), str)
        and "byte_count" in value
        and isinstance(value.get("version_probe"), dict)
    )


def derive_context_review_closure_observation() -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    root_path = str(HDA_GENERATION_MANIFEST.relative_to(ROOT))
    queue = [root_path]
    visited: set[str] = set()
    parsed_json_count = 0
    binding_rows: list[dict[str, Any]] = []
    pathless_binding_rows: list[dict[str, Any]] = []
    descriptor_rows: list[dict[str, Any]] = []
    executable_rows: list[dict[str, Any]] = []

    def walk(
        value: Any,
        source_path: str,
        pointer: str,
        host: dict[str, Any] | None,
    ) -> None:
        if isinstance(value, dict):
            identity = context_review_binding_identity(value)
            is_blob_descriptor = context_review_blob_descriptor(value)
            is_executable_observation = context_review_executable_observation(value)
            if (
                isinstance(value.get("repository_path"), str)
                and isinstance(value.get("raw_sha256"), str)
                and "byte_count" in value
            ):
                binding_rows.append(
                    {
                        "artifact_kind": value.get("artifact_kind"),
                        "declared_byte_count": value.get("byte_count"),
                        "declared_raw_sha256": value.get("raw_sha256"),
                        "identity": identity,
                        "source_json_pointer": pointer,
                        "source_repository_path": source_path,
                        "target_repository_path": value.get("repository_path"),
                    }
                )
            elif (
                identity
                and isinstance(value.get("raw_sha256"), str)
                and "byte_count" in value
                and not is_blob_descriptor
                and not is_executable_observation
            ):
                pathless_binding_rows.append(
                    {
                        "declared_byte_count": value.get("byte_count"),
                        "declared_raw_sha256": value.get("raw_sha256"),
                        "identity": identity,
                        "source_json_pointer": pointer,
                        "source_repository_path": source_path,
                    }
                )
            if is_blob_descriptor:
                descriptor_rows.append(
                    {
                        "artifact_id": value.get("artifact_id"),
                        "byte_count": value.get("byte_count"),
                        "content_address": value.get("content_address"),
                        "required_media_type": value.get("required_media_type"),
                        "role": value.get("role"),
                        "source_json_pointer": pointer,
                        "source_repository_path": source_path,
                        "target_repository_path": value.get(
                            "repository_blob_path"
                        ),
                    }
                )
            if is_executable_observation:
                executable_rows.append(
                    {
                        "byte_count": value.get("byte_count"),
                        "function": value.get("function"),
                        "host_machine": host.get("machine") if host else None,
                        "host_system": host.get("system") if host else None,
                        "invocation_path": value.get("invocation_path"),
                        "raw_sha256": value.get("raw_sha256"),
                        "resolved_path": value.get("resolved_path"),
                        "source_json_pointer": pointer,
                        "source_repository_path": source_path,
                        "version_probe_repository_path": value.get(
                            "version_probe", {}
                        ).get("repository_path"),
                    }
                )
            for key, child in value.items():
                walk(
                    child,
                    source_path,
                    pointer + "/" + json_pointer_token(key),
                    host,
                )
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, source_path, pointer + f"/{index}", host)

    while queue:
        source_path = queue.pop(0)
        if source_path in visited:
            continue
        visited.add(source_path)
        if not valid_repository_path(source_path):
            errors.append(
                "context_review.closure_source_repository_path_invalid"
            )
            continue
        path = ROOT / source_path
        if path.is_symlink() or not path.is_file():
            errors.append(
                "context_review.closure_source_repository_member_unreadable"
            )
            continue
        try:
            value = json.loads(
                path.read_text("utf-8"), object_pairs_hook=strict_pairs
            )
        except (DuplicateKey, OSError, UnicodeError, json.JSONDecodeError):
            if path.suffix == ".json":
                errors.append(
                    "context_review.closure_json_repository_member_unreadable"
                )
            continue
        parsed_json_count += 1
        if not isinstance(value, (dict, list)):
            errors.append("context_review.closure_json_root_invalid")
            continue
        host = (
            value.get("host_observation")
            if isinstance(value, dict)
            and isinstance(value.get("host_observation"), dict)
            else None
        )
        before = len(binding_rows)
        walk(value, source_path, "", host)
        for row in binding_rows[before:]:
            target = row["target_repository_path"]
            if (
                valid_repository_path(target)
                and Path(target).suffix == ".json"
                and target not in visited
                and target not in queue
            ):
                queue.append(target)

    member_paths = {root_path}
    member_paths.update(
        row["target_repository_path"]
        for row in binding_rows
        if valid_repository_path(row["target_repository_path"])
    )
    member_paths.update(
        row["target_repository_path"]
        for row in descriptor_rows
        if valid_repository_path(row["target_repository_path"])
    )
    member_rows: list[dict[str, Any]] = []
    for row in binding_rows:
        if (
            not valid_repository_path(row["target_repository_path"])
            or re.fullmatch(r"sha256:[0-9a-f]{64}", row["declared_raw_sha256"])
            is None
            or isinstance(row["declared_byte_count"], bool)
            or not isinstance(row["declared_byte_count"], int)
            or row["declared_byte_count"] < 0
        ):
            errors.append("context_review.closure_repository_binding_invalid")
            continue
        target_path = ROOT / row["target_repository_path"]
        if target_path.is_symlink() or not target_path.is_file():
            errors.append("context_review.closure_bound_repository_member_unreadable")
            continue
        if raw_file_binding(target_path) != (
            row["declared_raw_sha256"],
            row["declared_byte_count"],
        ):
            errors.append("context_review.closure_repository_binding_mismatch")
    for row in descriptor_rows:
        if (
            not valid_repository_path(row["target_repository_path"])
            or re.fullmatch(r"sha256:[0-9a-f]{64}", row["content_address"])
            is None
            or isinstance(row["byte_count"], bool)
            or not isinstance(row["byte_count"], int)
            or row["byte_count"] < 0
        ):
            errors.append("context_review.closure_blob_descriptor_invalid")
            continue
        target_path = ROOT / row["target_repository_path"]
        if target_path.is_symlink() or not target_path.is_file():
            errors.append("context_review.closure_blob_member_unreadable")
            continue
        if raw_file_binding(target_path) != (
            row["content_address"],
            row["byte_count"],
        ):
            errors.append("context_review.closure_blob_descriptor_mismatch")
    for row in pathless_binding_rows:
        if (
            not isinstance(row.get("identity"), dict)
            or not row["identity"]
            or set(row["identity"]) - set(CONTEXT_REVIEW_BINDING_IDENTITY_KEYS)
            or any(
                not isinstance(item, str) or not item
                for item in row["identity"].values()
            )
            or re.fullmatch(
                r"sha256:[0-9a-f]{64}", row["declared_raw_sha256"]
            )
            is None
            or isinstance(row["declared_byte_count"], bool)
            or not isinstance(row["declared_byte_count"], int)
            or row["declared_byte_count"] <= 0
        ):
            errors.append("context_review.closure_pathless_binding_invalid")
            continue
        exact_identity_targets = {
            candidate["target_repository_path"]
            for candidate in binding_rows
            if all(
                candidate["identity"].get(key) == item
                for key, item in row["identity"].items()
            )
            and candidate["declared_raw_sha256"] == row["declared_raw_sha256"]
            and candidate["declared_byte_count"] == row["declared_byte_count"]
        }
        digest_targets = {
            candidate["target_repository_path"]
            for candidate in binding_rows
            if candidate["declared_raw_sha256"] == row["declared_raw_sha256"]
            and candidate["declared_byte_count"] == row["declared_byte_count"]
        }
        targets = exact_identity_targets if exact_identity_targets else digest_targets
        if len(targets) != 1:
            errors.append(
                "context_review.closure_pathless_binding_resolution_not_unique"
            )
            continue
        row["resolution_method"] = (
            "closed_identity_digest_count"
            if exact_identity_targets
            else "unique_digest_count"
        )
        row["resolved_target_repository_path"] = next(iter(targets))
    for row in executable_rows:
        if (
            row["host_system"] not in {"Darwin", "Linux"}
            or row["host_machine"] not in {"aarch64", "arm64", "x86_64"}
            or re.fullmatch(r"sha256:[0-9a-f]{64}", row["raw_sha256"])
            is None
            or isinstance(row["byte_count"], bool)
            or not isinstance(row["byte_count"], int)
            or row["byte_count"] <= 0
        ):
            errors.append("context_review.closure_executable_observation_invalid")

    for member_path in sorted(member_paths):
        path = ROOT / member_path
        if path.is_symlink() or not path.is_file():
            errors.append("context_review.closure_repository_member_unreadable")
            continue
        digest, count = raw_file_binding(path)
        member_rows.append(
            {
                "byte_count": count,
                "raw_sha256": digest,
                "repository_path": member_path,
            }
        )

    sort_key = lambda row: canonical_observation_bytes(row)
    binding_rows.sort(key=sort_key)
    pathless_binding_rows.sort(key=sort_key)
    descriptor_rows.sort(key=sort_key)
    executable_rows.sort(key=sort_key)
    try:
        manifest = load(HDA_GENERATION_MANIFEST)
    except (DuplicateKey, OSError, UnicodeError, ValueError, json.JSONDecodeError):
        manifest = {}
        errors.append("context_review.closure_generation_manifest_unreadable")
    manifest_digest, manifest_count = raw_file_binding(HDA_GENERATION_MANIFEST)
    preimage = {
        "blob_descriptor_observations": descriptor_rows,
        "executable_observations": executable_rows,
        "pathless_binding_resolutions": pathless_binding_rows,
        "repository_binding_occurrences": binding_rows,
        "repository_members": member_rows,
        "subject_generation_manifest_binding": {
            "artifact_id": manifest.get("artifact_id"),
            "byte_count": manifest_count,
            "raw_sha256": manifest_digest,
            "repository_path": root_path,
        },
    }
    return {
        "observation_preimage": preimage,
        "parsed_json_repository_member_count": parsed_json_count,
        "unique_repository_member_byte_count": sum(
            row["byte_count"] for row in member_rows
        ),
        "observational_closure_digest": (
            "sha256:"
            + hashlib.sha256(canonical_observation_bytes(preimage)).hexdigest()
        ),
    }, errors


def context_review_closure_observation_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["context_review.closure_observation_must_be_object"]
    derived, errors = derive_context_review_closure_observation()
    preimage = derived["observation_preimage"]
    summary = value.get("summary")
    expected_summary = {
        "blob_descriptor_observation_count": len(
            preimage["blob_descriptor_observations"]
        ),
        "executable_observation_count": len(preimage["executable_observations"]),
        "observational_closure_digest": derived["observational_closure_digest"],
        "pathless_binding_resolution_count": len(
            preimage["pathless_binding_resolutions"]
        ),
        "parsed_json_repository_member_count": derived[
            "parsed_json_repository_member_count"
        ],
        "repository_binding_occurrence_count": len(
            preimage["repository_binding_occurrences"]
        ),
        "unique_repository_member_byte_count": derived[
            "unique_repository_member_byte_count"
        ],
        "unique_repository_member_count": len(preimage["repository_members"]),
    }
    expected_top = {
        "artifact_class",
        "authority_boundary",
        "derivation_contract",
        "observation_id",
        "observation_preimage",
        "schema_version",
        "subject_scope_id",
        "summary",
    }
    if set(value) != expected_top:
        errors.append("context_review.closure_observation_top_level_not_closed")
    if (
        value.get("schema_version") != "0.1.0"
        or value.get("artifact_class")
        != "human_decision_assurance_context_review_closure_observation"
        or value.get("observation_id")
        != "hda-context-review-closure-observation.2026-07-21.0003"
        or value.get("subject_scope_id")
        != "hda-successor-t0-technical-review-scope.0005"
    ):
        errors.append("context_review.closure_observation_identity_mismatch")
    if value.get("derivation_contract") != {
        "blob_descriptor_predicate": (
            "object_with_string_repository_blob_path_content_address_and_"
            "integer_byte_count"
        ),
        "canonical_digest_preimage": "observation_preimage",
        "canonicalization": (
            "utf8_ascii_escaped_json_sorted_keys_compact_separators_with_lf"
        ),
        "executable_observation_predicate": (
            "object_with_function_invocation_path_resolved_path_raw_sha256_"
            "byte_count_and_version_probe"
        ),
        "pathless_binding_resolution": (
            "resolve_each_pathless_raw_sha256_byte_count_object_with_one_or_more_"
            "closed_identity_keys_artifact_id_profile_id_ruleset_id_or_schema_"
            "resource_id_to_one_exact_path_bearing_scope_binding"
        ),
        "repository_binding_predicate": (
            "object_with_string_repository_path_raw_sha256_and_integer_byte_count"
        ),
        "traversal": (
            "breadth_first_from_generation_manifest_expand_each_distinct_"
            "dot_json_target_once_retain_every_json_pointer_occurrence"
        ),
    }:
        errors.append("context_review.closure_derivation_contract_mismatch")
    if value.get("observation_preimage") != preimage:
        errors.append("context_review.closure_observation_preimage_mismatch")
    if summary != expected_summary:
        errors.append("context_review.closure_observation_summary_mismatch")
    authority = value.get("authority_boundary")
    if (
        not isinstance(authority, dict)
        or set(authority)
        != {
            "accountable_review_completed",
            "gate_a_accepted",
            "organizational_independence_proven",
            "runtime_authorized",
        }
        or any(item is not False for item in authority.values())
    ):
        errors.append("context_review.closure_observation_authority_escalated")
    return errors


RAW_GIT_OBJECT_ENVIRONMENT = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_NO_LAZY_FETCH": "1",
    "GIT_NO_REPLACE_OBJECTS": "1",
    "GIT_LITERAL_PATHSPECS": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": os.defpath,
}


def run_raw_git_object_command(
    repository_root: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[bytes]:
    """Read only the local object database, without repository config or refs."""
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
            raise ValueError("Git worktree pointer is malformed")
        pointer_value = pointer.removeprefix("gitdir: ").strip()
        if not pointer_value:
            raise ValueError("Git worktree pointer is empty")
        candidate = Path(pointer_value)
        if not candidate.is_absolute():
            candidate = repository_root / candidate
        git_directory = candidate.resolve(strict=True)
    else:
        raise ValueError("repository has no regular Git directory or worktree pointer")
    common_pointer = git_directory / "commondir"
    if common_pointer.exists():
        if not common_pointer.is_file() or common_pointer.is_symlink():
            raise ValueError("Git common-directory pointer is not a regular file")
        common_value = common_pointer.read_text(encoding="utf-8")
        if (
            len(common_value.encode("utf-8")) > 4096
            or not common_value.strip()
            or "\x00" in common_value
        ):
            raise ValueError("Git common-directory pointer is malformed")
        common_candidate = Path(common_value.strip())
        if not common_candidate.is_absolute():
            common_candidate = git_directory / common_candidate
        common_directory = common_candidate.resolve(strict=True)
    else:
        common_directory = git_directory
    object_directory = (common_directory / "objects").resolve(strict=True)
    if not object_directory.is_dir():
        raise ValueError("Git object directory is absent")

    with tempfile.TemporaryDirectory(prefix="odeya-hda-object-reader-") as raw_root:
        isolated_git_directory = Path(raw_root) / "isolated.git"
        (isolated_git_directory / "objects").mkdir(parents=True)
        (isolated_git_directory / "refs").mkdir()
        (isolated_git_directory / "HEAD").write_bytes(
            b"ref: refs/heads/unused\n"
        )
        environment = dict(RAW_GIT_OBJECT_ENVIRONMENT)
        environment.update(
            {
                "GIT_DIR": str(isolated_git_directory),
                "GIT_OBJECT_DIRECTORY": str(object_directory),
            }
        )
        return subprocess.run(
            ["git", "--no-replace-objects", "--literal-pathspecs", *arguments],
            cwd=repository_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )


def parse_raw_git_commit_lineage(raw: bytes) -> tuple[str, tuple[str, ...]]:
    """Return the literal tree and ordered parents encoded in a commit object."""
    header, separator, _message = raw.partition(b"\n\n")
    if not separator:
        raise ValueError("raw Git commit has no header/message separator")
    lines = header.split(b"\n")
    if not lines or not lines[0].startswith(b"tree "):
        raise ValueError("raw Git commit must begin with its tree header")
    tree_value = lines[0][5:]
    if re.fullmatch(rb"[0-9a-f]{40}", tree_value) is None:
        raise ValueError("raw Git commit tree is not a SHA-1 object ID")
    parent_fields: list[str] = []
    lineage_end = 1
    for line in lines[1:]:
        if line.startswith(b"parent "):
            value = line[7:]
            if re.fullmatch(rb"[0-9a-f]{40}", value) is None:
                raise ValueError("raw Git commit parent is not a SHA-1 object ID")
            parent_fields.append(value.decode("ascii"))
            lineage_end += 1
        else:
            break
    if any(
        line.startswith((b"tree ", b"parent ")) for line in lines[lineage_end:]
    ):
        raise ValueError("raw Git commit has a duplicate or misordered lineage header")
    return tree_value.decode("ascii"), tuple(parent_fields)


def raw_git_commit_lineage(
    repository_root: Path,
    commit: str,
) -> tuple[str, tuple[str, ...]]:
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("Git commit object ID is invalid")
    observed = run_raw_git_object_command(repository_root, "cat-file", "commit", commit)
    if observed.returncode != 0:
        raise ValueError(
            "Git commit object cannot be read literally: "
            + observed.stderr.decode("utf-8", errors="replace").strip()
        )
    return parse_raw_git_commit_lineage(observed.stdout)


def raw_git_blob_at_tree(
    repository_root: Path,
    tree: str,
    repository_path: str,
) -> bytes:
    """Read one regular blob from a literal tree without commit revision semantics."""
    if re.fullmatch(r"[0-9a-f]{40}", tree) is None:
        raise ValueError("Git tree object ID is invalid")
    if not valid_repository_path(repository_path):
        raise ValueError("repository path is invalid")
    object_type = run_raw_git_object_command(repository_root, "cat-file", "-t", tree)
    if object_type.returncode != 0 or object_type.stdout != b"tree\n":
        raise ValueError("literal Git tree object is absent or has the wrong type")
    listed = run_raw_git_object_command(
        repository_root,
        "ls-tree",
        "--full-tree",
        "-z",
        tree,
        "--",
        repository_path,
    )
    if listed.returncode != 0:
        raise ValueError(
            "Git tree entry cannot be read literally: "
            + listed.stderr.decode("utf-8", errors="replace").strip()
        )
    records = [record for record in listed.stdout.split(b"\0") if record]
    if len(records) != 1:
        raise ValueError("Git tree path must resolve to exactly one entry")
    metadata, separator, path_bytes = records[0].partition(b"\t")
    fields = metadata.split(b" ")
    if (
        not separator
        or len(fields) != 3
        or fields[0] not in {b"100644", b"100755"}
        or fields[1] != b"blob"
        or re.fullmatch(rb"[0-9a-f]{40}", fields[2]) is None
        or path_bytes != repository_path.encode("utf-8")
    ):
        raise ValueError("Git tree path is not the exact requested regular blob")
    observed = run_raw_git_object_command(
        repository_root,
        "cat-file",
        "blob",
        fields[2].decode("ascii"),
    )
    if observed.returncode != 0:
        raise ValueError(
            "Git blob object cannot be read literally: "
            + observed.stderr.decode("utf-8", errors="replace").strip()
        )
    return observed.stdout


def git_predecessor_subject_errors(
    subject: Any,
    repository_root: Path = ROOT,
) -> list[str]:
    if not isinstance(subject, dict):
        return ["context_review.predecessor_git_subject_must_be_object"]
    errors: list[str] = []
    commit = subject.get("commit")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        return ["context_review.predecessor_git_commit_invalid"]
    try:
        tree, parents = raw_git_commit_lineage(repository_root, commit)
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"context_review.predecessor_git_lineage_unreadable:{exc}")
        return errors
    generation_binding = subject.get("generation_manifest_binding")
    vector_binding = subject.get("vector_corpus_binding")
    generation_path = (
        generation_binding.get("repository_path")
        if isinstance(generation_binding, dict)
        else None
    )
    vector_path = (
        vector_binding.get("repository_path")
        if isinstance(vector_binding, dict)
        else None
    )
    if (
        tree != subject.get("tree")
    ):
        errors.append("context_review.predecessor_git_lineage_mismatch")
    if len(parents) != 1 or parents[0] != subject.get("sole_parent"):
        errors.append("context_review.predecessor_git_parent_mismatch")
    for label, path_text, binding in (
        (
            "generation_manifest",
            generation_path,
            generation_binding,
        ),
        ("vector_corpus", vector_path, vector_binding),
    ):
        expected_binding_keys = {"repository_path", "raw_sha256", "byte_count"}
        if label == "generation_manifest":
            expected_binding_keys.add("artifact_id")
        if (
            not isinstance(binding, dict)
            or set(binding) != expected_binding_keys
            or not valid_repository_path(path_text)
            or not isinstance(binding.get("raw_sha256"), str)
            or re.fullmatch(r"sha256:[0-9a-f]{64}", binding["raw_sha256"])
            is None
            or type(binding.get("byte_count")) is not int
            or binding["byte_count"] < 0
            or (
                label == "generation_manifest"
                and (
                    not isinstance(binding.get("artifact_id"), str)
                    or not binding["artifact_id"]
                )
            )
        ):
            errors.append(f"context_review.predecessor_{label}_binding_shape_invalid")
            continue
        try:
            observed = raw_git_blob_at_tree(repository_root, tree, path_text)
        except (OSError, UnicodeError, ValueError):
            errors.append(f"context_review.predecessor_{label}_git_object_missing")
            continue
        expected = (
            "sha256:" + hashlib.sha256(observed).hexdigest(),
            len(observed),
        )
        if expected != (binding.get("raw_sha256"), binding.get("byte_count")):
            errors.append(f"context_review.predecessor_{label}_binding_mismatch")
    return errors


def validate_raw_git_object_attack_controls(errors: list[str]) -> int:
    """Prove Gate and generator object reads ignore ambient repository controls."""
    passed = 0
    with tempfile.TemporaryDirectory(prefix="odeya-hda-raw-git-") as raw_root:
        repository_root = Path(raw_root)
        test_environment = dict(RAW_GIT_OBJECT_ENVIRONMENT)
        test_environment.update(
            {
                "GIT_AUTHOR_DATE": "2001-01-01T00:00:00+0000",
                "GIT_COMMITTER_DATE": "2001-01-01T00:00:00+0000",
            }
        )

        def git(
            *arguments: str,
            replacement_refs_disabled: bool = True,
        ) -> subprocess.CompletedProcess[bytes]:
            environment = dict(test_environment)
            if not replacement_refs_disabled:
                environment.pop("GIT_NO_REPLACE_OBJECTS", None)
            return subprocess.run(
                ["git", *arguments],
                cwd=repository_root,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        def require_success(label: str, observed: subprocess.CompletedProcess[bytes]) -> None:
            if observed.returncode != 0:
                raise ValueError(
                    f"{label} failed: "
                    + observed.stderr.decode("utf-8", errors="replace").strip()
                )

        try:
            require_success("git init", git("init", "--quiet"))
            subject_path = repository_root / "subject.json"
            subject_path.write_bytes(b'{"state":"parent"}\n')
            require_success("git add parent", git("add", "--", "subject.json"))
            require_success(
                "git commit parent",
                git(
                    "-c",
                    "user.name=Odeya raw-object self-test",
                    "-c",
                    "user.email=raw-object-self-test@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "parent",
                ),
            )
            parent = git("rev-parse", "HEAD")
            require_success("resolve parent", parent)
            parent_id = parent.stdout.decode("ascii").strip()
            subject_path.write_bytes(b'{"state":"child"}\n')
            require_success("git add child", git("add", "--", "subject.json"))
            require_success(
                "git commit child",
                git(
                    "-c",
                    "user.name=Odeya raw-object self-test",
                    "-c",
                    "user.email=raw-object-self-test@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "child",
                ),
            )
            child = git("rev-parse", "HEAD")
            require_success("resolve child", child)
            child_id = child.stdout.decode("ascii").strip()
            expected_tree, expected_parents = raw_git_commit_lineage(
                repository_root,
                child_id,
            )
            expected_blob = raw_git_blob_at_tree(
                repository_root,
                expected_tree,
                "subject.json",
            )
            if expected_parents != (parent_id,) or expected_blob != b'{"state":"child"}\n':
                raise ValueError("raw-object safe control did not resolve the child commit")
            parent_tree, _parent_parents = raw_git_commit_lineage(
                repository_root,
                parent_id,
            )
            parent_blob_result = git("rev-parse", f"{parent_id}:subject.json")
            child_blob_result = git("rev-parse", f"{child_id}:subject.json")
            require_success("resolve parent blob", parent_blob_result)
            require_success("resolve child blob", child_blob_result)
            parent_blob_id = parent_blob_result.stdout.decode("ascii").strip()
            child_blob_id = child_blob_result.stdout.decode("ascii").strip()
            parent_blob = raw_git_blob_at_tree(
                repository_root,
                parent_tree,
                "subject.json",
            )
            forged_commit_result = git(
                "-c",
                "user.name=Odeya raw-object self-test",
                "-c",
                "user.email=raw-object-self-test@example.invalid",
                "commit-tree",
                parent_tree,
                "-p",
                parent_id,
                "-m",
                "forged replacement commit",
            )
            require_success("construct forged commit", forged_commit_result)
            forged_commit_id = forged_commit_result.stdout.decode("ascii").strip()
            expected_binding = {
                "repository_path": "subject.json",
                "raw_sha256": "sha256:" + hashlib.sha256(expected_blob).hexdigest(),
                "byte_count": len(expected_blob),
            }
            forged_binding = {
                "repository_path": "subject.json",
                "raw_sha256": "sha256:" + hashlib.sha256(parent_blob).hexdigest(),
                "byte_count": len(parent_blob),
            }
            exact_subject = {
                "commit": child_id,
                "tree": expected_tree,
                "sole_parent": parent_id,
                "generation_manifest_binding": {
                    "artifact_id": "raw-git-object-self-test",
                    **expected_binding,
                },
                "vector_corpus_binding": dict(expected_binding),
            }

            graft_path = repository_root / ".git/info/grafts"
            graft_path.write_text(
                f"{child_id} {forged_commit_id}\n",
                encoding="ascii",
            )
            grafted_walk = git(
                "--no-replace-objects",
                "rev-list",
                "--parents",
                "-n",
                "1",
                child_id,
            )
            require_success("grafted revision walk", grafted_walk)
            graft_effect_observed = (
                grafted_walk.stdout.decode("ascii").strip()
                == f"{child_id} {forged_commit_id}"
            )
            spoofed_graft_subject = json.loads(json.dumps(exact_subject))
            spoofed_graft_subject["sole_parent"] = forged_commit_id
            spoofed_graft_errors = git_predecessor_subject_errors(
                spoofed_graft_subject,
                repository_root,
            )
            graft_raw_tree, graft_raw_parents = raw_git_commit_lineage(
                repository_root,
                child_id,
            )
            graft_raw_blob = raw_git_blob_at_tree(
                repository_root,
                graft_raw_tree,
                "subject.json",
            )
            if (
                graft_effect_observed
                and (graft_raw_tree, graft_raw_parents)
                == (expected_tree, expected_parents)
                and graft_raw_blob == expected_blob
                and not git_predecessor_subject_errors(
                    exact_subject,
                    repository_root,
                )
                and "context_review.predecessor_git_parent_mismatch"
                in spoofed_graft_errors
            ):
                passed += 1
            else:
                errors.append(
                    "context review raw Git graft attack control did not prove "
                    "literal commit/tree/blob immunity"
                )

            graft_path.unlink()
            replacement = git(
                "replace",
                child_id,
                forged_commit_id,
                replacement_refs_disabled=False,
            )
            require_success("install commit replacement ref", replacement)
            require_success(
                "install tree replacement ref",
                git(
                    "replace",
                    expected_tree,
                    parent_tree,
                    replacement_refs_disabled=False,
                ),
            )
            require_success(
                "install blob replacement ref",
                git(
                    "replace",
                    child_blob_id,
                    parent_blob_id,
                    replacement_refs_disabled=False,
                ),
            )
            replaced_tree = git(
                "rev-parse",
                f"{child_id}^{{tree}}",
                replacement_refs_disabled=False,
            )
            require_success("replacement-aware tree read", replaced_tree)
            replaced_tree_entry = git(
                "ls-tree",
                "-z",
                expected_tree,
                "--",
                "subject.json",
                replacement_refs_disabled=False,
            )
            require_success("replacement-aware tree entry read", replaced_tree_entry)
            replaced_blob = git(
                "cat-file",
                "blob",
                child_blob_id,
                replacement_refs_disabled=False,
            )
            require_success("replacement-aware blob read", replaced_blob)
            replace_effect_observed = (
                replaced_tree.stdout.decode("ascii").strip() == parent_tree
                and parent_blob_id.encode("ascii") in replaced_tree_entry.stdout
                and replaced_blob.stdout == b'{"state":"parent"}\n'
            )
            replace_raw_tree, replace_raw_parents = raw_git_commit_lineage(
                repository_root,
                child_id,
            )
            replace_raw_blob = raw_git_blob_at_tree(
                repository_root,
                replace_raw_tree,
                "subject.json",
            )
            spoofed_replace_subject = {
                "commit": child_id,
                "tree": parent_tree,
                "sole_parent": parent_id,
                "generation_manifest_binding": {
                    "artifact_id": "raw-git-object-spoof",
                    **forged_binding,
                },
                "vector_corpus_binding": dict(forged_binding),
            }
            spoofed_replace_errors = git_predecessor_subject_errors(
                spoofed_replace_subject,
                repository_root,
            )
            if (
                replace_effect_observed
                and (replace_raw_tree, replace_raw_parents)
                == (expected_tree, expected_parents)
                and replace_raw_blob == expected_blob
                and not git_predecessor_subject_errors(
                    exact_subject,
                    repository_root,
                )
                and "context_review.predecessor_git_lineage_mismatch"
                in spoofed_replace_errors
                and "context_review.predecessor_generation_manifest_binding_mismatch"
                in spoofed_replace_errors
                and "context_review.predecessor_vector_corpus_binding_mismatch"
                in spoofed_replace_errors
            ):
                passed += 1
            else:
                errors.append(
                    "context review raw Git replacement-ref attack control did not "
                    "prove literal commit/tree/blob immunity"
                )

            sentinel = repository_root / "promisor-helper-invoked"
            for key, value in (
                ("core.repositoryformatversion", "1"),
                ("extensions.partialClone", "origin"),
                ("remote.origin.promisor", "true"),
                ("remote.origin.partialclonefilter", "blob:none"),
                ("remote.origin.url", f"ext::/usr/bin/touch {sentinel}"),
                ("protocol.ext.allow", "always"),
            ):
                require_success(
                    f"configure promisor attack {key}",
                    git("config", key, value),
                )
            git("cat-file", "blob", "1" * 40)
            if sentinel.exists():
                sentinel.unlink()
            isolated_missing = run_raw_git_object_command(
                repository_root,
                "cat-file",
                "blob",
                "1" * 40,
            )
            isolated_existing = raw_git_blob_at_tree(
                repository_root,
                expected_tree,
                "subject.json",
            )
            if (
                isolated_missing.returncode != 0
                and not sentinel.exists()
                and isolated_existing == expected_blob
            ):
                passed += 1
            else:
                errors.append(
                    "context review raw Git promisor attack control did not prove "
                    "local-only object reads"
                )

            module_spec = importlib.util.spec_from_file_location(
                "_odeya_hda_successor_generator_control",
                HDA_SUCCESSOR_GENERATOR,
            )
            if module_spec is None or module_spec.loader is None:
                raise ImportError("cannot load the HDA successor generator")
            generator = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(generator)
            generator_missing_refused = False
            try:
                generator.git_object_bytes(
                    "1" * 40,
                    "missing.json",
                    repository_root=repository_root,
                )
            except generator.GenerationError as exc:
                generator_missing_refused = (
                    str(exc) == "local predecessor Git object is unavailable"
                )
            generator_existing = generator.git_object_bytes(
                child_id,
                "subject.json",
                repository_root=repository_root,
            )
            if (
                generator_missing_refused
                and not sentinel.exists()
                and generator_existing == expected_blob
            ):
                passed += 1
            else:
                errors.append(
                    "context review generator Git-object control did not prove "
                    "that the live migration reader is configless and local-only"
                )
        except (ImportError, OSError, UnicodeError, ValueError) as exc:
            errors.append(f"context review raw Git attack controls failed: {exc}")
    return passed


def validate_context_review_closure_observation_known_bads(
    errors: list[str],
) -> int:
    try:
        safe = load(HDA_CONTEXT_CLOSURE_OBSERVATION)
    except (DuplicateKey, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"context review closure safe control is unreadable: {exc}")
        return 0
    safe_errors = context_review_closure_observation_errors(safe)
    if safe_errors:
        errors.append(
            f"context review closure safe control failed: {safe_errors!r}"
        )
        return 0
    mutations: list[tuple[str, Any, str]] = []

    omitted_member = json.loads(json.dumps(safe))
    omitted_member["observation_preimage"]["repository_members"].pop()
    mutations.append(
        (
            "omitted-member",
            omitted_member,
            "context_review.closure_observation_preimage_mismatch",
        )
    )
    collapsed_occurrence = json.loads(json.dumps(safe))
    collapsed_occurrence["observation_preimage"][
        "repository_binding_occurrences"
    ].pop()
    mutations.append(
        (
            "collapsed-repeated-occurrence",
            collapsed_occurrence,
            "context_review.closure_observation_preimage_mismatch",
        )
    )
    altered_pointer = json.loads(json.dumps(safe))
    altered_pointer["observation_preimage"]["repository_binding_occurrences"][0][
        "source_json_pointer"
    ] += "/shifted"
    mutations.append(
        (
            "altered-pointer",
            altered_pointer,
            "context_review.closure_observation_preimage_mismatch",
        )
    )
    omitted_pathless = json.loads(json.dumps(safe))
    omitted_pathless["observation_preimage"][
        "pathless_binding_resolutions"
    ].pop()
    mutations.append(
        (
            "omitted-pathless-binding-resolution",
            omitted_pathless,
            "context_review.closure_observation_preimage_mismatch",
        )
    )
    omitted_non_artifact_identity = json.loads(json.dumps(safe))
    pathless_rows = omitted_non_artifact_identity["observation_preimage"][
        "pathless_binding_resolutions"
    ]
    non_artifact_index = next(
        (
            index
            for index, row in enumerate(pathless_rows)
            if isinstance(row, dict)
            and isinstance(row.get("identity"), dict)
            and "artifact_id" not in row["identity"]
            and set(row["identity"]) & {"profile_id", "ruleset_id", "schema_resource_id"}
        ),
        None,
    )
    if non_artifact_index is None:
        errors.append(
            "context review closure safe control lacks a non-artifact identity binding"
        )
    else:
        pathless_rows.pop(non_artifact_index)
        mutations.append(
            (
                "omitted-non-artifact-identity-binding",
                omitted_non_artifact_identity,
                "context_review.closure_observation_preimage_mismatch",
            )
        )
    altered_non_artifact_identity = json.loads(json.dumps(safe))
    altered_rows = altered_non_artifact_identity["observation_preimage"][
        "pathless_binding_resolutions"
    ]
    altered_row = next(
        (
            row
            for row in altered_rows
            if isinstance(row, dict)
            and isinstance(row.get("identity"), dict)
            and "ruleset_id" in row["identity"]
        ),
        None,
    )
    if altered_row is None:
        errors.append(
            "context review closure safe control lacks a ruleset identity binding"
        )
    else:
        altered_row["identity"]["ruleset_id"] += ".substituted"
        mutations.append(
            (
                "altered-non-artifact-identity",
                altered_non_artifact_identity,
                "context_review.closure_observation_preimage_mismatch",
            )
        )
    altered_blob = json.loads(json.dumps(safe))
    altered_blob["observation_preimage"]["blob_descriptor_observations"][0][
        "content_address"
    ] = "sha256:" + ("0" * 64)
    mutations.append(
        (
            "altered-blob-address",
            altered_blob,
            "context_review.closure_observation_preimage_mismatch",
        )
    )
    swapped_executable = json.loads(json.dumps(safe))
    swapped_executable["observation_preimage"]["executable_observations"][0][
        "raw_sha256"
    ] = "sha256:" + ("0" * 64)
    mutations.append(
        (
            "swapped-executable-observation",
            swapped_executable,
            "context_review.closure_observation_preimage_mismatch",
        )
    )
    substituted_digest = json.loads(json.dumps(safe))
    substituted_digest["summary"]["observational_closure_digest"] = (
        "sha256:" + ("0" * 64)
    )
    mutations.append(
        (
            "substituted-projection-digest",
            substituted_digest,
            "context_review.closure_observation_summary_mismatch",
        )
    )
    boolean_count = json.loads(json.dumps(safe))
    boolean_count["summary"]["unique_repository_member_count"] = True
    mutations.append(
        (
            "boolean-for-member-count",
            boolean_count,
            "context_review.closure_observation_summary_mismatch",
        )
    )
    self_reference = json.loads(json.dumps(safe))
    self_reference["observation_preimage"]["repository_members"].append(
        {
            "byte_count": 0,
            "raw_sha256": "sha256:" + ("0" * 64),
            "repository_path": str(
                HDA_CONTEXT_CLOSURE_OBSERVATION.relative_to(ROOT)
            ),
        }
    )
    mutations.append(
        (
            "observation-self-reference",
            self_reference,
            "context_review.closure_observation_preimage_mismatch",
        )
    )
    authority = json.loads(json.dumps(safe))
    authority["authority_boundary"]["gate_a_accepted"] = True
    mutations.append(
        (
            "authority-promotion",
            authority,
            "context_review.closure_observation_authority_escalated",
        )
    )

    passed = 0
    for case_id, candidate, expected in mutations:
        observed = context_review_closure_observation_errors(candidate)
        if expected in observed:
            passed += 1
        else:
            errors.append(
                f"context review closure known-bad {case_id} missed "
                f"{expected}; observed {observed!r}"
            )
    return passed


def normalized_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def architecture_requirements_lock_inventory() -> dict[str, dict[str, Any]]:
    raw = (
        ROOT / "tools/repository-release/requirements-architecture.lock"
    ).read_text("utf-8")
    inventory: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for line in raw.splitlines():
        package = re.match(r"^([A-Za-z0-9_.-]+)==([^ \\]+)(?: \\)?$", line)
        if package is not None:
            name = normalized_distribution_name(package.group(1))
            if name in inventory:
                raise ValueError(f"duplicate locked distribution {name}")
            inventory[name] = {
                "hashes": set(),
                "version": package.group(2),
            }
            current = name
            continue
        digest = re.search(r"--hash=sha256:([0-9a-f]{64})", line)
        if digest is not None and current is not None:
            inventory[current]["hashes"].add(digest.group(1))
    if not inventory or any(not item["hashes"] for item in inventory.values()):
        raise ValueError("architecture requirements lock inventory is incomplete")
    return inventory


def context_review_artifact_binding(path: Path, artifact_id: str) -> dict[str, Any]:
    digest, count = raw_file_binding(path)
    return {
        "artifact_id": artifact_id,
        "byte_count": count,
        "raw_sha256": digest,
        "repository_path": str(path.relative_to(ROOT)),
    }


def context_review_command_observation_matches(
    candidate: Any,
    argv: list[str],
    *,
    phase: str | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
) -> bool:
    expected_keys = {"argv", "exit_code", "stderr", "stdout"}
    if phase is not None:
        expected_keys.add("phase")
    return (
        isinstance(candidate, dict)
        and set(candidate) == expected_keys
        and candidate.get("argv") == argv
        and (phase is None or candidate.get("phase") == phase)
        and type(candidate.get("exit_code")) is int
        and candidate.get("exit_code") == 0
        and isinstance(candidate.get("stdout"), str)
        and isinstance(candidate.get("stderr"), str)
        and (stdout is None or candidate.get("stdout") == stdout)
        and (stderr is None or candidate.get("stderr") == stderr)
    )


def context_review_pip_report_rows(
    report: Any,
    locked: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(report, dict) or set(report) != {
        "environment",
        "install",
        "pip_version",
        "version",
    }:
        errors.append("context_review.python_install_report_top_level_not_closed")
        report = report if isinstance(report, dict) else {}
    environment = report.get("environment")
    if (
        report.get("version") != "1"
        or not isinstance(report.get("pip_version"), str)
        or not report.get("pip_version")
        or not isinstance(environment, dict)
    ):
        errors.append("context_review.python_install_report_identity_mismatch")
        environment = environment if isinstance(environment, dict) else {}

    rows: list[dict[str, Any]] = []
    installs = report.get("install")
    if not isinstance(installs, list):
        errors.append("context_review.python_install_report_inventory_invalid")
        installs = []
    for item in installs:
        metadata = item.get("metadata") if isinstance(item, dict) else None
        download = item.get("download_info") if isinstance(item, dict) else None
        archive = download.get("archive_info") if isinstance(download, dict) else None
        hashes = archive.get("hashes") if isinstance(archive, dict) else None
        name = metadata.get("name") if isinstance(metadata, dict) else None
        version = metadata.get("version") if isinstance(metadata, dict) else None
        url = download.get("url") if isinstance(download, dict) else None
        digest = hashes.get("sha256") if isinstance(hashes, dict) else None
        if not (
            isinstance(item, dict)
            and set(item)
            == {"download_info", "is_direct", "is_yanked", "metadata", "requested"}
            and item.get("is_direct") is False
            and item.get("is_yanked") is False
            and item.get("requested") is True
            and isinstance(name, str)
            and isinstance(version, str)
            and isinstance(url, str)
            and url.startswith("https://files.pythonhosted.org/")
            and isinstance(archive, dict)
            and isinstance(hashes, dict)
            and set(hashes) == {"sha256"}
            and re.fullmatch(r"[0-9a-f]{64}", digest or "") is not None
            and archive.get("hash") == f"sha256={digest}"
        ):
            errors.append("context_review.python_install_report_row_invalid")
            continue
        assert isinstance(name, str)
        assert isinstance(version, str)
        assert isinstance(url, str)
        assert isinstance(digest, str)
        normalized = normalized_distribution_name(name)
        locked_row = locked.get(normalized)
        if (
            locked_row is None
            or version != locked_row["version"]
            or digest not in locked_row["hashes"]
        ):
            errors.append(
                "context_review.python_install_report_distribution_not_locked"
            )
        rows.append(
            {
                "normalized_name": normalized,
                "requested": True,
                "selected_archive_sha256": digest,
                "source_url": url,
                "version": version,
            }
        )
    rows.sort(key=lambda row: row["normalized_name"])
    names = [row["normalized_name"] for row in rows]
    if names != sorted(set(names)) or set(names) != set(locked):
        errors.append(
            "context_review.python_install_report_distribution_set_mismatch"
        )
    return environment, rows


def python_install_observation_errors(
    value: Any,
    *,
    report_overrides: list[Any] | None = None,
) -> list[str]:
    if not isinstance(value, dict):
        return ["context_review.python_install_observation_must_be_object"]
    errors: list[str] = []
    expected_top = {
        "artifact_class",
        "authority_boundary",
        "candidate_status",
        "closed_subprocess_environment",
        "fresh_environment",
        "generator_source_binding",
        "host_observation",
        "observation_id",
        "pip_report_projection",
        "python_observation",
        "raw_report_byte_identity",
        "requirements_lock_binding",
        "requirements_source_binding",
        "runs",
        "schema_version",
        "selected_distributions",
        "subject_scope_id",
        "summary",
    }
    if set(value) != expected_top:
        errors.append("context_review.python_install_top_level_not_closed")
    if (
        value.get("schema_version") != "0.1.0"
        or value.get("artifact_class")
        != "human_decision_assurance_context_review_python_install_observation"
        or value.get("observation_id")
        != "hda-context-review-python-install-observation.2026-07-21.0004"
        or value.get("subject_scope_id")
        != "hda-successor-t0-technical-review-scope.0005"
        or value.get("candidate_status")
        != (
            "host_bound_two_fresh_install_execution_observation_not_complete_"
            "environment_identity"
        )
    ):
        errors.append("context_review.python_install_identity_mismatch")

    expected_bindings = (
        (
            "requirements_source_binding",
            ROOT / "requirements-architecture.txt",
            "architecture-python-requirements-source.0001",
            "source",
        ),
        (
            "requirements_lock_binding",
            ROOT / "tools/repository-release/requirements-architecture.lock",
            "architecture-python-requirements-lock.0001",
            "lock",
        ),
        (
            "generator_source_binding",
            HDA_CONTEXT_PYTHON_INSTALL_GENERATOR,
            "hda-context-review-python-install-observation-generator.0003",
            "generator",
        ),
    )
    for member, path, artifact_id, label in expected_bindings:
        if value.get(member) != context_review_artifact_binding(path, artifact_id):
            errors.append(
                f"context_review.python_install_{label}_binding_mismatch"
            )

    report_paths = (
        HDA_CONTEXT_PYTHON_INSTALL_REPORT,
        HDA_CONTEXT_PYTHON_INSTALL_REPORT_RUN_02,
    )
    report_artifact_ids = (
        "hda-context-review-python-install-pip-report.run-01.0002",
        "hda-context-review-python-install-pip-report.run-02.0002",
    )
    try:
        reports = (
            [load(path) for path in report_paths]
            if report_overrides is None
            else report_overrides
        )
        report_raws = [path.read_bytes() for path in report_paths]
    except (DuplicateKey, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"context_review.python_install_report_unreadable:{exc}")
        reports = [{}, {}]
        report_raws = [b"", b""]
    if not isinstance(reports, list) or len(reports) != 2:
        errors.append("context_review.python_install_report_inventory_invalid")
        reports = [{}, {}]

    try:
        locked = architecture_requirements_lock_inventory()
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"context_review.python_install_lock_unreadable:{exc}")
        locked = {}
    parsed_reports = [
        context_review_pip_report_rows(report, locked, errors) for report in reports
    ]
    environments = [item[0] for item in parsed_reports]
    report_rows = [item[1] for item in parsed_reports]
    if (
        report_raws[0] != report_raws[1]
        or reports[0] != reports[1]
        or report_rows[0] != report_rows[1]
    ):
        errors.append("context_review.python_install_reports_not_byte_identical")
    common_environment = environments[0]
    common_rows = report_rows[0]
    if value.get("pip_report_projection") != {
        "environment": common_environment,
        "selected_distributions": common_rows,
    }:
        errors.append("context_review.python_install_report_projection_mismatch")

    host = value.get("host_observation")
    if (
        not isinstance(host, dict)
        or set(host) != {"machine", "system"}
        or host.get("system") != common_environment.get("platform_system")
        or host.get("machine") != common_environment.get("platform_machine")
        or common_environment.get("implementation_name") != "cpython"
        or common_environment.get("implementation_version") != "3.14.2"
        or common_environment.get("python_full_version") != "3.14.2"
        or common_environment.get("platform_python_implementation") != "CPython"
    ):
        errors.append("context_review.python_install_host_or_python_mismatch")

    expected_environment = {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": os.defpath,
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_COLOR": "1",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }
    if value.get("closed_subprocess_environment") != expected_environment:
        errors.append("context_review.python_install_closed_environment_mismatch")
    if value.get("fresh_environment") != {
        "distinct_fresh_temporary_environment_count": 2,
        "existing_project_environment_reused": False,
        "temporary_absolute_paths_retained": False,
    }:
        errors.append("context_review.python_install_fresh_environment_mismatch")

    python_observation = value.get("python_observation")
    version_probe = (
        python_observation.get("version_probe")
        if isinstance(python_observation, dict)
        else None
    )
    source_python = (
        version_probe.get("argv", [None])[0]
        if isinstance(version_probe, dict)
        and isinstance(version_probe.get("argv"), list)
        and version_probe["argv"]
        else None
    )
    if (
        not isinstance(source_python, str)
        or not Path(source_python).is_absolute()
        or not isinstance(python_observation, dict)
        or set(python_observation)
        != {"implementation_name", "implementation_version", "version_probe"}
        or python_observation.get("implementation_name") != "cpython"
        or python_observation.get("implementation_version") != "3.14.2"
        or not context_review_command_observation_matches(
            version_probe,
            [source_python, "--version"],
            stdout="Python 3.14.2\n",
            stderr="",
        )
    ):
        errors.append("context_review.python_install_python_mismatch")

    runs = value.get("runs")
    if (
        not isinstance(runs, list)
        or len(runs) != 2
        or [run.get("run_id") for run in runs if isinstance(run, dict)]
        != ["fresh-install.run-01", "fresh-install.run-02"]
    ):
        errors.append("context_review.python_install_run_inventory_mismatch")
        runs = runs if isinstance(runs, list) else []
    lock_digest, lock_count = raw_file_binding(
        ROOT / "tools/repository-release/requirements-architecture.lock"
    )
    expected_fresh_python = (
        "venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python"
    )
    expected_phase_commands = (
        ("venv_create", [source_python, "-m", "venv", "venv"], "", ""),
        (
            "preinstall",
            [expected_fresh_python, "-m", "pip", "list", "--format=json"],
            None,
            "",
        ),
        (
            "install",
            [
                expected_fresh_python,
                "-m",
                "pip",
                "install",
                "--isolated",
                "--disable-pip-version-check",
                "--no-input",
                "--require-hashes",
                "--only-binary=:all:",
                "--no-cache-dir",
                "--quiet",
                "--progress-bar=off",
                "--report",
                "pip-report.json",
                "--requirement=requirements-architecture.lock",
            ],
            "",
            "",
        ),
        (
            "pip_check",
            [expected_fresh_python, "-m", "pip", "check"],
            "No broken requirements found.\n",
            "",
        ),
    )
    for index, run in enumerate(runs[:2]):
        if not isinstance(run, dict) or set(run) != {
            "execution_sequence",
            "installer_metadata",
            "preinstall_locked_distribution_count",
            "preinstall_packages",
            "report_target_relation",
            "requirements_lock_copy_binding",
            "run_id",
            "working_directory",
        }:
            errors.append("context_review.python_install_run_members_not_closed")
            continue
        if run.get("working_directory") != {
            "absolute_path_retained": False,
            "distinct_fresh_directory": True,
            "semantics": "new_os_temporary_directory_removed_after_run",
        }:
            errors.append("context_review.python_install_working_directory_mismatch")
        if run.get("requirements_lock_copy_binding") != {
            "byte_count": lock_count,
            "execution_target": "requirements-architecture.lock",
            "raw_sha256": lock_digest,
        }:
            errors.append("context_review.python_install_lock_copy_mismatch")

        sequence = run.get("execution_sequence")
        if not isinstance(sequence, list) or len(sequence) != 4:
            errors.append("context_review.python_install_execution_sequence_mismatch")
            sequence = []
        for phase_index, (phase, argv, stdout, stderr) in enumerate(
            expected_phase_commands
        ):
            observed = sequence[phase_index] if len(sequence) > phase_index else None
            if not context_review_command_observation_matches(
                observed,
                argv,
                phase=phase,
                stdout=stdout,
                stderr=stderr,
            ):
                errors.append(
                    "context_review.python_install_execution_sequence_mismatch"
                )

        preinstall = sequence[1] if len(sequence) > 1 else None
        parsed_preinstall: Any = None
        if isinstance(preinstall, dict) and isinstance(preinstall.get("stdout"), str):
            try:
                parsed_preinstall = json.loads(
                    preinstall["stdout"], object_pairs_hook=strict_pairs
                )
            except (DuplicateKey, UnicodeError, ValueError, json.JSONDecodeError):
                pass
        normalized_preinstall = (
            sorted(
                (
                    {
                        "normalized_name": normalized_distribution_name(item["name"]),
                        "version": item["version"],
                    }
                    for item in parsed_preinstall
                    if isinstance(item, dict)
                    and isinstance(item.get("name"), str)
                    and isinstance(item.get("version"), str)
                ),
                key=lambda row: row["normalized_name"],
            )
            if isinstance(parsed_preinstall, list)
            else None
        )
        preinstall_packages = run.get("preinstall_packages")
        if (
            type(run.get("preinstall_locked_distribution_count")) is not int
            or run.get("preinstall_locked_distribution_count") != 0
            or normalized_preinstall != preinstall_packages
            or not isinstance(preinstall_packages, list)
            or any(row.get("normalized_name") in locked for row in preinstall_packages)
        ):
            errors.append("context_review.python_install_preinstall_mismatch")

        report = reports[index] if len(reports) > index else {}
        installer_metadata = run.get("installer_metadata")
        if (
            not isinstance(installer_metadata, dict)
            or installer_metadata
            != {
                "network_resolution_required": True,
                "pip_report_format_version": (
                    report.get("version") if isinstance(report, dict) else None
                ),
                "pip_version": (
                    report.get("pip_version") if isinstance(report, dict) else None
                ),
                "pip_version_bound_by_reviewed_subject": False,
            }
        ):
            errors.append("context_review.python_install_installer_boundary_mismatch")

        report_digest = "sha256:" + hashlib.sha256(report_raws[index]).hexdigest()
        report_count = len(report_raws[index])
        expected_retained = context_review_artifact_binding(
            report_paths[index], report_artifact_ids[index]
        )
        relation = run.get("report_target_relation")
        if (
            not isinstance(relation, dict)
            or relation
            != {
                "flag_argv_index": 12,
                "produced_bytes_binding": {
                    "byte_count": report_count,
                    "raw_sha256": report_digest,
                },
                "resolution_base": "ephemeral_run_working_directory",
                "retained_artifact_binding": expected_retained,
                "target_argv_index": 13,
                "target_argv_value": "pip-report.json",
            }
        ):
            errors.append("context_review.python_install_report_target_mismatch")

    report_bindings = [
        run.get("report_target_relation", {}).get("retained_artifact_binding")
        for run in runs[:2]
        if isinstance(run, dict)
    ]
    if (
        len(report_bindings) != 2
        or report_bindings[0].get("artifact_id")
        == report_bindings[1].get("artifact_id")
        or report_bindings[0].get("repository_path")
        == report_bindings[1].get("repository_path")
    ):
        errors.append("context_review.python_install_report_bindings_not_distinct")

    common_digest = "sha256:" + hashlib.sha256(report_raws[0]).hexdigest()
    common_count = len(report_raws[0])
    if value.get("raw_report_byte_identity") != {
        "byte_identical": True,
        "common_byte_count": common_count,
        "common_raw_sha256": common_digest,
        "comparison_method": "direct_raw_byte_equality_then_post_write_reread",
        "distinct_artifact_ids_and_repository_paths": True,
        "ordered_run_ids": ["fresh-install.run-01", "fresh-install.run-02"],
    }:
        errors.append("context_review.python_install_repeatability_mismatch")

    expected_distributions = [
        {
            "normalized_name": row["normalized_name"],
            "selected_archive_sha256": row["selected_archive_sha256"],
            "version": row["version"],
        }
        for row in common_rows
    ]
    if value.get("selected_distributions") != expected_distributions:
        errors.append(
            "context_review.python_install_distribution_inventory_mismatch"
        )
    expected_count = len(locked)
    if value.get("summary") != {
        "all_selected_archive_hashes_present_in_lock": True,
        "locked_distribution_set_exact_match": True,
        "pip_check_passed_for_both_runs": True,
        "raw_pip_reports_retained": 2,
        "selected_distribution_count": expected_count,
        "two_fresh_install_reports_byte_identical": True,
    } or len(common_rows) != expected_count:
        errors.append("context_review.python_install_summary_mismatch")
    authority = value.get("authority_boundary")
    if (
        not isinstance(authority, dict)
        or set(authority)
        != {
            "accountable_review_completed",
            "complete_environment_identity_proven",
            "cross_host_reproducibility_proven",
            "external_effects_authorized",
            "gate_a_accepted",
            "organizational_independence_proven",
            "runtime_authorized",
        }
        or any(item is not False for item in authority.values())
    ):
        errors.append("context_review.python_install_authority_escalated")
    return errors


def validate_python_install_observation_known_bads(errors: list[str]) -> int:
    try:
        safe = load(HDA_CONTEXT_PYTHON_INSTALL_OBSERVATION)
    except (DuplicateKey, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Python install observation safe control is unreadable: {exc}")
        return 0
    safe_errors = python_install_observation_errors(safe)
    if safe_errors:
        errors.append(f"Python install observation safe control failed: {safe_errors!r}")
        return 0
    mutations: list[tuple[str, dict[str, Any], str, list[Any] | None]] = []

    def add(
        case_id: str,
        candidate: dict[str, Any],
        expected: str,
        report_overrides: list[Any] | None = None,
    ) -> None:
        mutations.append((case_id, candidate, expected, report_overrides))

    candidate = json.loads(json.dumps(safe))
    candidate["runs"].pop()
    add("missing-run", candidate, "context_review.python_install_run_inventory_mismatch")
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][1]["run_id"] = candidate["runs"][0]["run_id"]
    add("duplicate-run-id", candidate, "context_review.python_install_run_inventory_mismatch")
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["execution_sequence"][0], candidate["runs"][0][
        "execution_sequence"
    ][1] = (
        candidate["runs"][0]["execution_sequence"][1],
        candidate["runs"][0]["execution_sequence"][0],
    )
    add(
        "reordered-phases",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["execution_sequence"][2]["argv"][0] = "$FRESH_PYTHON"
    add(
        "claimed-template-not-argv",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["execution_sequence"].pop(0)
    add(
        "venv-create-omitted",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["execution_sequence"][2]["exit_code"] = False
    add(
        "boolean-install-exit",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["execution_sequence"][2]["stderr"] = "hidden"
    add(
        "install-stderr-omitted",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["preinstall_locked_distribution_count"] = 1
    add(
        "locked-preinstall",
        candidate,
        "context_review.python_install_preinstall_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["execution_sequence"][2]["argv"].remove("--report")
    add(
        "missing-report-flag",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["report_target_relation"]["target_argv_index"] = 14
    add(
        "wrong-report-target-index",
        candidate,
        "context_review.python_install_report_target_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["report_target_relation"]["produced_bytes_binding"][
        "byte_count"
    ] += 1
    add(
        "produced-report-binding-swapped",
        candidate,
        "context_review.python_install_report_target_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][1]["report_target_relation"]["retained_artifact_binding"] = (
        candidate["runs"][0]["report_target_relation"]["retained_artifact_binding"]
    )
    add(
        "duplicate-retained-report-binding",
        candidate,
        "context_review.python_install_report_target_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["raw_report_byte_identity"]["byte_identical"] = False
    add(
        "repeatability-denied",
        candidate,
        "context_review.python_install_repeatability_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["execution_sequence"][2]["argv"].remove("--require-hashes")
    add(
        "missing-require-hashes",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][1]["execution_sequence"][3]["exit_code"] = 1
    add(
        "pip-check-failed",
        candidate,
        "context_review.python_install_execution_sequence_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["generator_source_binding"]["byte_count"] += 1
    add(
        "generator-binding-swapped",
        candidate,
        "context_review.python_install_generator_binding_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["requirements_lock_binding"]["raw_sha256"] = "sha256:" + ("0" * 64)
    add(
        "lock-binding-swapped",
        candidate,
        "context_review.python_install_lock_binding_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["closed_subprocess_environment"]["PYTHONPATH"] = "inherited"
    add(
        "environment-widened",
        candidate,
        "context_review.python_install_closed_environment_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["installer_metadata"]["network_resolution_required"] = False
    add(
        "network-resolution-suppressed",
        candidate,
        "context_review.python_install_installer_boundary_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["runs"][0]["installer_metadata"][
        "pip_version_bound_by_reviewed_subject"
    ] = True
    add(
        "pip-version-falsely-bound",
        candidate,
        "context_review.python_install_installer_boundary_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["selected_distributions"].pop()
    add(
        "missing-distribution",
        candidate,
        "context_review.python_install_distribution_inventory_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["pip_report_projection"]["selected_distributions"].pop()
    add(
        "projection-omitted",
        candidate,
        "context_review.python_install_report_projection_mismatch",
    )
    report_overrides = [
        load(HDA_CONTEXT_PYTHON_INSTALL_REPORT),
        load(HDA_CONTEXT_PYTHON_INSTALL_REPORT_RUN_02),
    ]
    report_overrides[1]["install"][0]["download_info"]["archive_info"]["hashes"][
        "sha256"
    ] = "0" * 64
    report_overrides[1]["install"][0]["download_info"]["archive_info"]["hash"] = (
        "sha256=" + ("0" * 64)
    )
    add(
        "run-two-unlocked-wheel",
        json.loads(json.dumps(safe)),
        "context_review.python_install_report_distribution_not_locked",
        report_overrides,
    )
    candidate = json.loads(json.dumps(safe))
    candidate["authority_boundary"]["runtime_authorized"] = True
    add(
        "runtime-authority",
        candidate,
        "context_review.python_install_authority_escalated",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["summary"]["raw_pip_reports_retained"] = True
    add(
        "boolean-report-count",
        candidate,
        "context_review.python_install_summary_mismatch",
    )
    candidate = json.loads(json.dumps(safe))
    candidate["python_observation"]["implementation_version"] = "3.14.3"
    add(
        "python-version-substituted",
        candidate,
        "context_review.python_install_python_mismatch",
    )

    passed = 0
    for case_id, candidate, expected, report_overrides in mutations:
        observed = python_install_observation_errors(
            candidate,
            report_overrides=report_overrides,
        )
        if expected in observed:
            passed += 1
        else:
            errors.append(
                f"Python install observation known-bad {case_id} missed {expected}; "
                f"observed {observed!r}"
            )
    return passed


def context_review_round_errors(
    value: Any,
    *,
    expected_round_id: str,
    expected_review_class: str,
    expected_subject: dict[str, Any],
    expected_result: str,
    expected_finding_refs: list[str],
    expected_attacks: list[tuple[str, str]],
    code: str,
) -> list[str]:
    errors: list[str] = []
    if (
        not isinstance(value, dict)
        or set(value)
        != {"round_id", "review_class", "subject", "attacks", "result", "finding_refs"}
        or value.get("round_id") != expected_round_id
        or value.get("review_class") != expected_review_class
        or value.get("subject") != expected_subject
        or value.get("result") != expected_result
        or value.get("finding_refs") != expected_finding_refs
    ):
        errors.append(f"context_review.{code}_round_mismatch")
    attacks = value.get("attacks") if isinstance(value, dict) else None
    observed: list[tuple[str, str]] = []
    attacks_valid = isinstance(attacks, list)
    for attack in attacks if isinstance(attacks, list) else []:
        allowed_keys = {
            "attack_id",
            "anti_contamination_control",
            "method",
            "observed_result",
            "verdict",
        }
        if isinstance(attack, dict) and "command" in attack:
            allowed_keys.add("command")
        if (
            not isinstance(attack, dict)
            or set(attack) != allowed_keys
            or any(
                not isinstance(attack.get(member), str) or not attack[member]
                for member in (
                    "attack_id",
                    "anti_contamination_control",
                    "method",
                    "observed_result",
                    "verdict",
                )
            )
            or (
                "command" in attack
                and (
                    not isinstance(attack.get("command"), str)
                    or not attack["command"]
                )
            )
        ):
            attacks_valid = False
            continue
        observed.append((attack["attack_id"], attack["verdict"]))
    if not attacks_valid or observed != expected_attacks:
        errors.append(f"context_review.{code}_attack_inventory_mismatch")
    return errors


def context_isolated_technical_review_errors(value: Any) -> list[str]:
    """Validate bounded model-review evidence without converting it to authority."""
    if not isinstance(value, dict):
        return ["context_review.must_be_object"]
    errors: list[str] = []
    expected_top = {
        "artifact_class",
        "authority_boundary",
        "bounded_result",
        "bounded_result_semantics",
        "candidate_status",
        "correction_evidence_bindings",
        "current_consumers_migrated",
        "decision_refs",
        "finding_ledger",
        "invalidation",
        "mandate",
        "report_id",
        "review_rounds",
        "reviewer_provenance",
        "schema_version",
        "version",
    }
    if set(value) != expected_top:
        errors.append("context_review.top_level_members_not_closed")
    rounds = value.get("review_rounds")
    round_count = len(rounds) if isinstance(rounds, list) else -1
    version = value.get("version")
    if (
        value.get("schema_version") != "0.1.0"
        or value.get("artifact_class")
        != (
            "human_decision_assurance_context_isolated_correlated_"
            "non_accountable_technical_review_evidence"
        )
        or value.get("report_id")
        != "hda-context-isolated-technical-review.2026-07-21.0001"
        or type(version) is not int
        or (round_count, version) not in {(8, 7), (9, 8), (10, 9), (11, 10)}
        or value.get("candidate_status")
        != (
            "retained_model_generated_technical_review_evidence_not_a_"
            "review_determination_or_authority"
        )
    ):
        errors.append("context_review.identity_or_status_mismatch")
    decision_refs = value.get("decision_refs")
    expected_decisions = [
        "docs/decisions/0095-reissue-human-decision-assurance-as-a-byte-bound-independently-recomputed-chain.md",
        "docs/decisions/0096-reconstruct-the-successor-phase-two-binding-before-technical-review.md",
    ]
    if (
        decision_refs != expected_decisions
        or any(not (ROOT / item).is_file() for item in expected_decisions)
    ):
        errors.append("context_review.decision_refs_mismatch")

    mandate = value.get("mandate")
    if (
        not isinstance(mandate, dict)
        or set(mandate)
        != {
            "adr_0095_adoption_item",
            "allowed_attack_verdicts",
            "allowed_bounded_results",
            "excluded_claims",
            "objective",
        }
        or type(mandate.get("adr_0095_adoption_item")) is not int
        or mandate.get("adr_0095_adoption_item") != 7
        or mandate.get("allowed_attack_verdicts")
        != ["refuted", "survived_this_attack", "unable_to_determine"]
        or mandate.get("allowed_bounded_results")
        != [
            "refuted",
            "no_grounded_refutation_observed_within_declared_attacks",
            "unable_to_determine",
        ]
        or not isinstance(mandate.get("objective"), str)
        or not mandate.get("objective")
        or mandate.get("excluded_claims")
        != [
            "accountable_review",
            "correctness_beyond_declared_attacks",
            "human_decision_or_ceremony_observation",
            "organizational_independence",
            "profile_or_schema_issuance",
            "prq_013_closure",
            "ruleset_approval",
            "runtime_or_external_effect_authority",
        ]
    ):
        errors.append("context_review.mandate_boundary_mismatch")

    provenance = value.get("reviewer_provenance")
    expected_provenance_keys = {
        "accountable_reviewer",
        "context_isolated",
        "exact_model_snapshot",
        "harness_family",
        "human_principal",
        "incentive_relation",
        "independence_conclusion_permitted",
        "model_family_declared_by_execution_environment",
        "organization",
        "organizational_independence_proven",
        "principal_type",
        "producer_private_reasoning_received",
        "prompt_family",
        "provider_declared_by_execution_environment",
        "shared_correlation_axes",
        "source_corpus",
        "training_data_lineage",
        "unknown_correlation_axes",
        "unrestricted_prompt_or_model_output_retained",
        "weights_lineage",
    }
    shared_axes = (
        provenance.get("shared_correlation_axes")
        if isinstance(provenance, dict)
        else None
    )
    unknown_axes = (
        provenance.get("unknown_correlation_axes")
        if isinstance(provenance, dict)
        else None
    )
    if (
        not isinstance(provenance, dict)
        or set(provenance) != expected_provenance_keys
        or provenance.get("principal_type") != "model_worker"
        or provenance.get("context_isolated") is not True
        or provenance.get("producer_private_reasoning_received") is not False
        or provenance.get("unrestricted_prompt_or_model_output_retained") is not False
        or provenance.get("accountable_reviewer") is not False
        or provenance.get("organizational_independence_proven") is not False
        or provenance.get("independence_conclusion_permitted") is not False
        or provenance.get("provider_declared_by_execution_environment") != "OpenAI"
        or provenance.get("model_family_declared_by_execution_environment") != "GPT-5"
        or not isinstance(shared_axes, list)
        or shared_axes != sorted(set(shared_axes))
        or not isinstance(unknown_axes, list)
        or unknown_axes != sorted(set(unknown_axes))
    ):
        errors.append("context_review.provenance_boundary_mismatch")

    if (
        not isinstance(rounds, list)
        or len(rounds) not in {8, 9, 10, 11}
        or not all(isinstance(item, dict) for item in rounds)
    ):
        errors.append("context_review.round_inventory_mismatch")
        rounds = []
    first_subject = {
        "subject_kind": "exact_published_git_candidate",
        "repository": "https://github.com/manfromnowhere143/odeya",
        "commit": "86c0f1ed8ba20d74324d64529bf5435a0524f4cd",
        "tree": "0465eac6adf3f49629e72b1c9e6dce6d4acd121c",
        "sole_parent": "34cad10a42027730a515614fc0a5bd664dd8933b",
        "generation_manifest_binding": {
            "artifact_id": "hda-successor-generation-manifest.synthetic.0001",
            "repository_path": "tests/human-decision-assurance-successor/generation-manifest.json",
            "raw_sha256": "sha256:f401a95c52ccc49791872584971450c723d3c9d2632d66cbd3e9761fea26e247",
            "byte_count": 16050,
        },
        "vector_corpus_binding": {
            "repository_path": "tests/human-decision-assurance-successor/vectors.json",
            "raw_sha256": "sha256:c81d7d9636d5a4f79a545bbad0ef5454ab8a4bb171d896e0035f1096b2c9cc1a",
            "byte_count": 42211,
        },
    }
    expected_rounds: list[dict[str, Any]] = [
        {
            "round_id": "hda-context-review.predecessor-refutation.0001",
            "review_class": "context_isolated_correlated_non_accountable_model_refutation",
            "subject": first_subject,
            "result": "refuted",
            "findings": ["HDA-CTX-001"],
            "attacks": [
                ("predecessor-retained-validator-replay", "survived_this_attack"),
                ("predecessor-independent-phase-two-reconstruction", "refuted"),
                ("predecessor-arbitrary-authentication-id-probe", "refuted"),
            ],
            "code": "predecessor",
        },
        {
            "round_id": "hda-context-review.corrected-bounded-scope.0002",
            "review_class": "fresh_context_correlated_non_accountable_model_refutation",
            "subject": {
                "subject_kind": "exact_bounded_t0_byte_scope_excluding_later_review_report_and_status_prose",
                "generation_manifest_binding": {
                    "artifact_id": "hda-successor-generation-manifest.synthetic.0002",
                    "repository_path": "tests/human-decision-assurance-successor/generation-manifest.json",
                    "raw_sha256": "sha256:4558c4ac0e9e4729f14ca3d69ec5218dc85886a86432161e33f669930d369767",
                    "byte_count": 22136,
                },
                "scope_id": "hda-successor-t0-technical-review-scope.0002",
                "direct_input_binding_count": 12,
                "verified_unique_repository_member_count": 70,
                "verified_nested_repository_binding_count": 69,
                "verified_blob_descriptor_count": 42,
                "verified_local_executable_observation_count": 4,
                "observational_sorted_closure_digest": "sha256:abe4ca3e44fa6fe3bf8d18dd04dd3cdeccfc07c57a22de84be11f5c40f6080d8",
                "observational_closure_digest_is_canonical_subject_identity": False,
                "any_bound_member_byte_change_invalidates_review": True,
            },
            "result": "survived_this_attack",
            "findings": [],
            "attacks": [
                ("corrected-byte-closure", "survived_this_attack"),
                ("corrected-independent-phase-two-reconstruction", "survived_this_attack"),
                ("corrected-stale-id-known-bad", "survived_this_attack"),
                ("corrected-migration-narrowness", "survived_this_attack"),
                ("corrected-three-toolchain-recomputation", "survived_this_attack"),
                ("corrected-disposable-regeneration", "survived_this_attack"),
                ("corrected-authority-boundary", "survived_this_attack"),
            ],
            "code": "round_two",
        },
        {
            "round_id": "hda-context-review.extended-root-and-evidence-refutation.0003",
            "review_class": "extended_context_correlated_non_accountable_model_refutation",
            "subject": {
                "subject_kind": "superseded_uncommitted_bounded_t0_byte_scope",
                "generation_manifest_binding": {
                    "artifact_id": "hda-successor-generation-manifest.synthetic.0002",
                    "repository_path": "tests/human-decision-assurance-successor/generation-manifest.json",
                    "raw_sha256": "sha256:4558c4ac0e9e4729f14ca3d69ec5218dc85886a86432161e33f669930d369767",
                    "byte_count": 22136,
                },
                "scope_id": "hda-successor-t0-technical-review-scope.0002",
                "historical_round_retained_without_claiming_current_repository_reconstruction": True,
            },
            "result": "refuted",
            "findings": ["HDA-CTX-002", "HDA-CTX-003", "HDA-CTX-004", "HDA-CTX-005"],
            "attacks": [
                ("extended-python-dependency-closure", "refuted"),
                ("extended-closure-observation-replay", "refuted"),
                ("extended-migration-branch-replay", "refuted"),
                ("extended-toolchain-selector-spoof", "refuted"),
                ("extended-generator-root-location", "refuted"),
                ("extended-predecessor-git-lineage", "refuted"),
            ],
            "code": "round_three",
        },
        {
            "round_id": "hda-context-review.fresh-root-0003-refutation.0004",
            "review_class": "fresh_context_correlated_non_accountable_model_refutation",
            "subject": {
                "subject_kind": "superseded_uncommitted_bounded_t0_byte_scope",
                "generation_manifest_binding": {
                    "artifact_id": "hda-successor-generation-manifest.synthetic.0003",
                    "repository_path": "tests/human-decision-assurance-successor/generation-manifest.json",
                    "raw_sha256": "sha256:3353389782d1795523cb89f8b73c79f51c9d7c962b31fb458ea53bc7afd326e8",
                    "byte_count": 22784,
                },
                "scope_id": "hda-successor-t0-technical-review-scope.0003",
                "direct_input_binding_count": 14,
                "declared_path_bearing_repository_binding_occurrence_count": 72,
                "declared_unique_repository_member_count": 66,
                "omitted_pathless_transitive_member_count": 6,
                "historical_round_retained_without_claiming_current_repository_reconstruction": True,
            },
            "result": "refuted",
            "findings": ["HDA-CTX-006", "HDA-CTX-007"],
            "attacks": [
                ("root-0003-declared-byte-closure-and-replay", "survived_this_attack"),
                ("root-0003-pathless-transitive-input-attack", "refuted"),
                ("root-0003-git-lineage-enforcement-attack", "refuted"),
                ("root-0003-fresh-lock-install-and-toolchain-identity", "survived_this_attack"),
                ("root-0003-authority-boundary", "survived_this_attack"),
            ],
            "code": "round_four",
        },
        {
            "round_id": "hda-context-review.takeover-install-observation-refutation.0005",
            "review_class": "takeover_context_correlated_non_accountable_model_refutation",
            "subject": {
                "subject_kind": "superseded_host_bound_correction_evidence_observation",
                "python_install_observation_binding": {
                    "observation_id": "hda-context-review-python-install-observation.2026-07-21.0001",
                    "repository_path": "architecture/human-decision-assurance-context-review-python-install-observation.json",
                    "raw_sha256": "sha256:1d03cc9faa6eca5e75fd4b05d4481e601d122543dd614e0462bde31f9935d2aa",
                    "byte_count": 5220,
                },
                "reviewed_root_binding": {
                    "artifact_id": "hda-successor-generation-manifest.synthetic.0004",
                    "repository_path": "tests/human-decision-assurance-successor/generation-manifest.json",
                    "raw_sha256": "sha256:110a28257eaa1ad822ea5634106a219f67be6c6cace22fea1221c92be8da7886",
                    "byte_count": 24530,
                },
                "historical_round_retained_without_claiming_current_repository_reconstruction": True,
            },
            "result": "refuted",
            "findings": ["HDA-CTX-008"],
            "attacks": [("takeover-fresh-install-execution-binding", "refuted")],
            "code": "round_five",
        },
        {
            "round_id": "hda-context-review.fresh-root-0004-refutation.0006",
            "review_class": "fresh_context_correlated_non_accountable_model_refutation",
            "subject": {
                "subject_kind": (
                    "exact_bounded_t0_byte_scope_with_superseded_correction_"
                    "observations"
                ),
                "generation_manifest_binding": {
                    "artifact_id": "hda-successor-generation-manifest.synthetic.0004",
                    "repository_path": (
                        "tests/human-decision-assurance-successor/"
                        "generation-manifest.json"
                    ),
                    "raw_sha256": (
                        "sha256:110a28257eaa1ad822ea5634106a219f67be6c6cace22fea"
                        "1221c92be8da7886"
                    ),
                    "byte_count": 24530,
                },
                "scope_id": "hda-successor-t0-technical-review-scope.0004",
                "closure_observation_binding": {
                    "observation_id": (
                        "hda-context-review-closure-observation.2026-07-21.0001"
                    ),
                    "repository_path": (
                        "architecture/human-decision-assurance-context-review-"
                        "closure-observation.json"
                    ),
                    "raw_sha256": (
                        "sha256:71afa0d8a0f839e7e80016c3a6cbcb6804245b6e0d821097"
                        "9b8942507fb52b01"
                    ),
                    "byte_count": 129111,
                },
                "python_install_observation_binding": {
                    "observation_id": (
                        "hda-context-review-python-install-observation."
                        "2026-07-21.0002"
                    ),
                    "repository_path": (
                        "architecture/human-decision-assurance-context-review-"
                        "python-install-observation.json"
                    ),
                    "raw_sha256": (
                        "sha256:c496df25f0f4d2071f48e6b220c11450c983f2601e269e058"
                        "b47ae1265d2657d"
                    ),
                    "byte_count": 11659,
                },
                "historical_round_retained_without_claiming_current_repository_reconstruction": True,
            },
            "result": "refuted",
            "findings": ["HDA-CTX-009", "HDA-CTX-010"],
            "attacks": [
                ("root-0004-declared-closure-replay", "survived_this_attack"),
                ("root-0004-complete-pathless-identity-attack", "refuted"),
                (
                    "root-0004-replacement-immune-git-lineage-attack",
                    "survived_this_attack",
                ),
                (
                    "root-0004-phase-two-and-migration-replay",
                    "survived_this_attack",
                ),
                ("root-0004-fresh-install-executed-argv-attack", "refuted"),
                ("root-0004-semantic-and-toolchain-replay", "unable_to_determine"),
                ("root-0004-disposable-regeneration", "unable_to_determine"),
                ("root-0004-authority-boundary", "survived_this_attack"),
            ],
            "code": "round_six",
        },
        {
            "round_id": (
                "hda-context-review.reissued-observations-integration-"
                "refutation.0007"
            ),
            "review_class": (
                "fresh_context_correlated_non_accountable_model_refutation"
            ),
            "subject": {
                "subject_kind": (
                    "exact_bounded_t0_byte_scope_with_reissued_correction_"
                    "observations_and_pre_correction_integration_surfaces"
                ),
                "generation_manifest_binding": {
                    "artifact_id": (
                        "hda-successor-generation-manifest.synthetic.0004"
                    ),
                    "repository_path": (
                        "tests/human-decision-assurance-successor/"
                        "generation-manifest.json"
                    ),
                    "raw_sha256": (
                        "sha256:110a28257eaa1ad822ea5634106a219f67be6c6cace22fea"
                        "1221c92be8da7886"
                    ),
                    "byte_count": 24530,
                },
                "closure_observation_binding": {
                    "observation_id": (
                        "hda-context-review-closure-observation.2026-07-21.0002"
                    ),
                    "repository_path": (
                        "architecture/human-decision-assurance-context-review-"
                        "closure-observation.json"
                    ),
                    "raw_sha256": (
                        "sha256:00368e4094e289fbbbc3de5d30a3eb7f79b709c261b929bf"
                        "f1bb863c5ee19594"
                    ),
                    "byte_count": 119866,
                },
                "python_install_observation_binding": {
                    "observation_id": (
                        "hda-context-review-python-install-observation."
                        "2026-07-21.0003"
                    ),
                    "repository_path": (
                        "architecture/human-decision-assurance-context-review-"
                        "python-install-observation.json"
                    ),
                    "raw_sha256": (
                        "sha256:7c9e3a64faadee5f764010e6e548768dae4b9b87790668467"
                        "2df0d6ab5a93ec4"
                    ),
                    "byte_count": 15354,
                },
                "pre_correction_gate_validator_binding": {
                    "repository_path": "scripts/validate_gate_a_prerequisites.py",
                    "raw_sha256": (
                        "sha256:137b38ac6e88fe91b43fa0cfdeae2c84a958627c49b1cde37"
                        "9c9029e85f5eab1"
                    ),
                    "byte_count": 196986,
                },
                "pre_correction_architecture_surface_policy_binding": {
                    "policy_id": "odeya-architecture-surface-policy",
                    "repository_path": (
                        "architecture/architecture-surface-policy.json"
                    ),
                    "raw_sha256": (
                        "sha256:389887ff662eaff99c15bd868a645af8438a994c8394ea3d0"
                        "7f569218e65c314"
                    ),
                    "byte_count": 7845,
                },
                "scope_id": "hda-successor-t0-technical-review-scope.0004",
                "direct_input_binding_count": 20,
                "verified_unique_repository_member_count": 72,
                "verified_path_bearing_repository_binding_occurrence_count": 78,
                "verified_pathless_binding_resolution_count": 69,
                "verified_parsed_json_repository_member_count": 40,
                "verified_blob_descriptor_count": 42,
                "verified_local_executable_observation_count": 4,
                "verified_unique_repository_member_byte_count": 981341,
                "observational_sorted_closure_digest": (
                    "sha256:b15bdffa392f4f69aa15a9308fd634d7737e9b178687ff404"
                    "ffe041433b2cea1"
                ),
                "observational_closure_digest_is_canonical_subject_identity": False,
                "any_bound_member_byte_change_invalidates_review": True,
                "reviewed_python_install_run_count": 2,
            },
            "result": "refuted",
            "findings": ["HDA-CTX-011", "HDA-CTX-012"],
            "attacks": [
                ("root-0004-complete-closure-replay", "survived_this_attack"),
                (
                    "root-0004-closed-identity-pathless-attack",
                    "survived_this_attack",
                ),
                (
                    "root-0004-phase-two-and-migration-replay",
                    "survived_this_attack",
                ),
                (
                    "root-0004-two-run-install-execution-replay",
                    "survived_this_attack",
                ),
                (
                    "root-0004-semantic-and-toolchain-replay",
                    "survived_this_attack",
                ),
                ("root-0004-disposable-regeneration", "survived_this_attack"),
                ("root-0004-raw-git-lineage-graft-attack", "refuted"),
                ("root-0004-architecture-surface-admission-attack", "refuted"),
                ("root-0004-authority-boundary", "survived_this_attack"),
            ],
            "code": "round_seven",
        },
        {
            "round_id": (
                "hda-context-review.corrected-integration-refutation.0008"
            ),
            "review_class": (
                "fresh_context_correlated_non_accountable_model_refutation"
            ),
            "subject": {
                "subject_kind": (
                    "exact_bounded_t0_byte_scope_with_reissued_correction_"
                    "observations_and_pre_correction_raw_git_reader"
                ),
                "generation_manifest_binding": {
                    "artifact_id": (
                        "hda-successor-generation-manifest.synthetic.0004"
                    ),
                    "repository_path": (
                        "tests/human-decision-assurance-successor/"
                        "generation-manifest.json"
                    ),
                    "raw_sha256": (
                        "sha256:110a28257eaa1ad822ea5634106a219f67be6c6cace22fea"
                        "1221c92be8da7886"
                    ),
                    "byte_count": 24530,
                },
                "closure_observation_binding": {
                    "observation_id": (
                        "hda-context-review-closure-observation.2026-07-21.0002"
                    ),
                    "repository_path": (
                        "architecture/human-decision-assurance-context-review-"
                        "closure-observation.json"
                    ),
                    "raw_sha256": (
                        "sha256:00368e4094e289fbbbc3de5d30a3eb7f79b709c261b929bf"
                        "f1bb863c5ee19594"
                    ),
                    "byte_count": 119866,
                },
                "python_install_observation_binding": {
                    "observation_id": (
                        "hda-context-review-python-install-observation."
                        "2026-07-21.0003"
                    ),
                    "repository_path": (
                        "architecture/human-decision-assurance-context-review-"
                        "python-install-observation.json"
                    ),
                    "raw_sha256": (
                        "sha256:7c9e3a64faadee5f764010e6e548768dae4b9b87790668467"
                        "2df0d6ab5a93ec4"
                    ),
                    "byte_count": 15354,
                },
                "architecture_surface_policy_binding": {
                    "policy_id": "odeya-architecture-surface-policy",
                    "repository_path": (
                        "architecture/architecture-surface-policy.json"
                    ),
                    "raw_sha256": (
                        "sha256:10eb30db9c46f8771718285d4f5463004f7419f0ded06ce5a"
                        "03efeb0f98ef81d"
                    ),
                    "byte_count": 7927,
                },
                "scope_id": "hda-successor-t0-technical-review-scope.0004",
                "direct_input_binding_count": 20,
                "verified_unique_repository_member_count": 72,
                "verified_path_bearing_repository_binding_occurrence_count": 78,
                "verified_pathless_binding_resolution_count": 69,
                "verified_parsed_json_repository_member_count": 40,
                "verified_blob_descriptor_count": 42,
                "verified_local_executable_observation_count": 4,
                "verified_unique_repository_member_byte_count": 981341,
                "observational_sorted_closure_digest": (
                    "sha256:b15bdffa392f4f69aa15a9308fd634d7737e9b178687ff404"
                    "ffe041433b2cea1"
                ),
                "observational_closure_digest_is_canonical_subject_identity": False,
                "any_bound_member_byte_change_invalidates_review": True,
                "reviewed_python_install_run_count": 2,
                "pre_correction_raw_git_reader_repository_configuration_isolated": False,
                "pre_correction_predecessor_binding_member_vocabulary_closed": False,
                "pre_correction_predecessor_byte_count_type_strict": False,
                "context_review_known_bad_count": 21,
            },
            "result": "refuted",
            "findings": ["HDA-CTX-013", "HDA-CTX-014"],
            "attacks": [
                ("root-0004-complete-closure-replay", "survived_this_attack"),
                (
                    "root-0004-install-observation-structure",
                    "survived_this_attack",
                ),
                (
                    "root-0004-fresh-install-execution-replay",
                    "unable_to_determine",
                ),
                ("root-0004-local-only-raw-git-object-attack", "refuted"),
                (
                    "root-0004-predecessor-binding-type-and-shape-attack",
                    "refuted",
                ),
                (
                    "root-0004-semantic-and-toolchain-replay",
                    "unable_to_determine",
                ),
                (
                    "root-0004-architecture-surface-admission-attack",
                    "survived_this_attack",
                ),
                ("root-0004-full-repository-integration-attack", "refuted"),
                ("root-0004-authority-boundary", "survived_this_attack"),
            ],
            "code": "round_eight",
        },
    ]
    for index, expected in enumerate(expected_rounds):
        observed = rounds[index] if len(rounds) > index else None
        errors.extend(
            context_review_round_errors(
                observed,
                expected_round_id=expected["round_id"],
                expected_review_class=expected["review_class"],
                expected_subject=expected["subject"],
                expected_result=expected["result"],
                expected_finding_refs=expected["findings"],
                expected_attacks=expected["attacks"],
                code=expected["code"],
            )
        )
    errors.extend(git_predecessor_subject_errors(first_subject if not rounds else rounds[0].get("subject")))

    try:
        generation = load(HDA_GENERATION_MANIFEST)
        generation_digest, generation_count = raw_file_binding(HDA_GENERATION_MANIFEST)
        closure = load(HDA_CONTEXT_CLOSURE_OBSERVATION)
        install_observation = load(HDA_CONTEXT_PYTHON_INSTALL_OBSERVATION)
    except (DuplicateKey, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"context_review.current_evidence_unreadable:{exc}")
        generation = {}
        generation_digest = ""
        generation_count = -1
        closure = {}
        install_observation = {}
    current_generation_binding = {
        "artifact_id": generation.get("artifact_id"),
        "repository_path": str(HDA_GENERATION_MANIFEST.relative_to(ROOT)),
        "raw_sha256": generation_digest,
        "byte_count": generation_count,
    }
    closure_summary = closure.get("summary", {}) if isinstance(closure, dict) else {}
    if len(rounds) >= 9:
        historical_reviewed_subject = {
            "subject_kind": (
                "exact_bounded_t0_byte_scope_with_reissued_correction_"
                "observations_corrected_architecture_surface_policy_and_"
                "isolated_local_git_object_reader_excluding_later_review_"
                "report_and_status_prose"
            ),
            "generation_manifest_binding": {
                "artifact_id": "hda-successor-generation-manifest.synthetic.0004",
                "repository_path": (
                    "tests/human-decision-assurance-successor/"
                    "generation-manifest.json"
                ),
                "raw_sha256": (
                    "sha256:110a28257eaa1ad822ea5634106a219f67be6c6cace22fea"
                    "1221c92be8da7886"
                ),
                "byte_count": 24530,
            },
            "closure_observation_binding": {
                "observation_id": (
                    "hda-context-review-closure-observation.2026-07-21.0002"
                ),
                "repository_path": (
                    "architecture/human-decision-assurance-context-review-"
                    "closure-observation.json"
                ),
                "raw_sha256": (
                    "sha256:00368e4094e289fbbbc3de5d30a3eb7f79b709c261b929bf"
                    "f1bb863c5ee19594"
                ),
                "byte_count": 119866,
            },
            "python_install_observation_binding": {
                "observation_id": (
                    "hda-context-review-python-install-observation."
                    "2026-07-21.0003"
                ),
                "repository_path": (
                    "architecture/human-decision-assurance-context-review-"
                    "python-install-observation.json"
                ),
                "raw_sha256": (
                    "sha256:7c9e3a64faadee5f764010e6e548768dae4b9b8779066846"
                    "72df0d6ab5a93ec4"
                ),
                "byte_count": 15354,
            },
            "architecture_surface_policy_binding": {
                "policy_id": "odeya-architecture-surface-policy",
                "repository_path": "architecture/architecture-surface-policy.json",
                "raw_sha256": (
                    "sha256:10eb30db9c46f8771718285d4f5463004f7419f0ded06ce5"
                    "a03efeb0f98ef81d"
                ),
                "byte_count": 7927,
            },
            "scope_id": "hda-successor-t0-technical-review-scope.0004",
            "direct_input_binding_count": 20,
            "verified_unique_repository_member_count": 72,
            "verified_path_bearing_repository_binding_occurrence_count": 78,
            "verified_pathless_binding_resolution_count": 69,
            "verified_parsed_json_repository_member_count": 40,
            "verified_blob_descriptor_count": 42,
            "verified_local_executable_observation_count": 4,
            "verified_unique_repository_member_byte_count": 981341,
            "observational_sorted_closure_digest": (
                "sha256:b15bdffa392f4f69aa15a9308fd634d7737e9b178687ff40"
                "4ffe041433b2cea1"
            ),
            "observational_closure_digest_is_canonical_subject_identity": False,
            "any_bound_member_byte_change_invalidates_review": True,
            "reviewed_python_install_run_count": 2,
            "raw_git_object_attack_control_count": 3,
            "context_review_known_bad_count": 24,
        }
        errors.extend(
            context_review_round_errors(
                rounds[8],
                expected_round_id=(
                    "hda-context-review.corrected-local-object-integration-"
                    "refutation.0009"
                ),
                expected_review_class="fresh_context_correlated_non_accountable_model_refutation",
                expected_subject=historical_reviewed_subject,
                expected_result="refuted",
                expected_finding_refs=["HDA-CTX-015"],
                expected_attacks=[
                    ("root-0004-complete-closure-replay", "survived_this_attack"),
                    (
                        "root-0004-closed-identity-pathless-attack",
                        "survived_this_attack",
                    ),
                    (
                        "root-0004-install-observation-structure",
                        "survived_this_attack",
                    ),
                    (
                        "root-0004-fresh-install-execution-replay",
                        "survived_this_attack",
                    ),
                    (
                        "root-0004-isolated-local-git-object-attack",
                        "survived_this_attack",
                    ),
                    (
                        "root-0004-predecessor-binding-type-and-shape-attack",
                        "survived_this_attack",
                    ),
                    ("root-0004-phase-two-and-migration-replay", "survived_this_attack"),
                    (
                        "root-0004-semantic-and-toolchain-replay",
                        "survived_this_attack",
                    ),
                    ("root-0004-disposable-regeneration", "survived_this_attack"),
                    (
                        "root-0004-architecture-surface-admission-attack",
                        "survived_this_attack",
                    ),
                    (
                        "root-0004-full-repository-integration-attack",
                        "refuted",
                    ),
                    ("root-0004-authority-boundary", "survived_this_attack"),
                ],
                code="round_nine",
            )
        )
        if len(rounds) >= 10:
            round_ten_subject = {
                **historical_reviewed_subject,
                "prq_013_integration_known_bad_count": 2,
            }
            errors.extend(
                context_review_round_errors(
                    rounds[9],
                    expected_round_id=(
                        "hda-context-review.corrected-integration-bounded-"
                        "review.0010"
                    ),
                    expected_review_class=(
                        "fresh_context_correlated_non_accountable_model_refutation"
                    ),
                    expected_subject=round_ten_subject,
                    expected_result="refuted",
                    expected_finding_refs=["HDA-CTX-016"],
                    expected_attacks=[
                        (
                            "root-0004-complete-closure-replay",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-closed-identity-pathless-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-install-observation-structure",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-fresh-install-execution-replay",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-isolated-local-git-object-attack",
                            "refuted",
                        ),
                        (
                            "root-0004-predecessor-binding-type-and-shape-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-phase-two-and-migration-replay",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-semantic-and-toolchain-replay",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-disposable-regeneration",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-architecture-surface-admission-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-prq-013-integration-truth-binding-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0004-full-repository-integration-attack",
                            "refuted",
                        ),
                        (
                            "root-0004-authority-boundary",
                            "survived_this_attack",
                        ),
                    ],
                    code="round_ten",
                )
            )
        if len(rounds) == 11:
            closure_digest, closure_count = raw_file_binding(
                HDA_CONTEXT_CLOSURE_OBSERVATION
            )
            install_digest, install_count = raw_file_binding(
                HDA_CONTEXT_PYTHON_INSTALL_OBSERVATION
            )
            reissued_subject = {
                "subject_kind": (
                    "exact_bounded_t0_byte_scope_with_reissued_generator_local_"
                    "git_object_reader_closure_and_install_observations_"
                    "excluding_later_review_report_and_status_prose"
                ),
                "generation_manifest_binding": current_generation_binding,
                "closure_observation_binding": {
                    "observation_id": (
                        "hda-context-review-closure-observation.2026-07-21.0003"
                    ),
                    "repository_path": str(
                        HDA_CONTEXT_CLOSURE_OBSERVATION.relative_to(ROOT)
                    ),
                    "raw_sha256": closure_digest,
                    "byte_count": closure_count,
                },
                "python_install_observation_binding": {
                    "observation_id": (
                        "hda-context-review-python-install-observation."
                        "2026-07-21.0004"
                    ),
                    "repository_path": str(
                        HDA_CONTEXT_PYTHON_INSTALL_OBSERVATION.relative_to(ROOT)
                    ),
                    "raw_sha256": install_digest,
                    "byte_count": install_count,
                },
                "architecture_surface_policy_binding": {
                    "policy_id": "odeya-architecture-surface-policy",
                    "repository_path": "architecture/architecture-surface-policy.json",
                    "raw_sha256": (
                        "sha256:10eb30db9c46f8771718285d4f5463004f7419f0ded06ce5a"
                        "03efeb0f98ef81d"
                    ),
                    "byte_count": 7927,
                },
                "scope_id": generation.get("bounded_technical_review_scope", {}).get(
                    "scope_id"
                ),
                "direct_input_binding_count": len(
                    generation.get("bounded_technical_review_scope", {}).get(
                        "direct_input_bindings", []
                    )
                ),
                "verified_unique_repository_member_count": closure_summary.get(
                    "unique_repository_member_count"
                ),
                "verified_path_bearing_repository_binding_occurrence_count": (
                    closure_summary.get("repository_binding_occurrence_count")
                ),
                "verified_pathless_binding_resolution_count": closure_summary.get(
                    "pathless_binding_resolution_count"
                ),
                "verified_parsed_json_repository_member_count": closure_summary.get(
                    "parsed_json_repository_member_count"
                ),
                "verified_blob_descriptor_count": closure_summary.get(
                    "blob_descriptor_observation_count"
                ),
                "verified_local_executable_observation_count": closure_summary.get(
                    "executable_observation_count"
                ),
                "verified_unique_repository_member_byte_count": closure_summary.get(
                    "unique_repository_member_byte_count"
                ),
                "observational_sorted_closure_digest": closure_summary.get(
                    "observational_closure_digest"
                ),
                "observational_closure_digest_is_canonical_subject_identity": False,
                "any_bound_member_byte_change_invalidates_review": True,
                "reviewed_python_install_run_count": len(
                    install_observation.get("runs", [])
                    if isinstance(install_observation, dict)
                    else []
                ),
                "raw_git_object_attack_control_count": 4,
                "context_review_known_bad_count": 25,
                "prq_013_integration_known_bad_count": 2,
            }
            errors.extend(
                context_review_round_errors(
                    rounds[10],
                    expected_round_id=(
                        "hda-context-review.reissued-generator-object-reader-"
                        "bounded-review.0011"
                    ),
                    expected_review_class=(
                        "fresh_context_correlated_non_accountable_model_refutation"
                    ),
                    expected_subject=reissued_subject,
                    expected_result="survived_this_attack",
                    expected_finding_refs=[],
                    expected_attacks=[
                        ("root-0005-complete-closure-replay", "survived_this_attack"),
                        (
                            "root-0005-closed-identity-pathless-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-install-observation-structure",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-fresh-install-execution-replay",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-generator-local-git-object-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-predecessor-binding-type-and-shape-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-phase-two-and-migration-replay",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-semantic-and-toolchain-replay",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-exact-bound-disposable-regeneration",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-architecture-surface-admission-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-prq-013-integration-truth-binding-attack",
                            "survived_this_attack",
                        ),
                        (
                            "root-0005-full-repository-integration-attack",
                            "survived_this_attack",
                        ),
                        ("root-0005-authority-boundary", "survived_this_attack"),
                    ],
                    code="round_eleven",
                )
            )

    def report_binding(
        path: Path,
        identity_member: str,
        identity_value: str,
    ) -> dict[str, Any]:
        digest, count = raw_file_binding(path)
        return {
            identity_member: identity_value,
            "repository_path": str(path.relative_to(ROOT)),
            "raw_sha256": digest,
            "byte_count": count,
        }

    expected_corrections = {
        "closure_observation": report_binding(
            HDA_CONTEXT_CLOSURE_OBSERVATION,
            "observation_id",
            "hda-context-review-closure-observation.2026-07-21.0003",
        ),
        "python_install_observation": report_binding(
            HDA_CONTEXT_PYTHON_INSTALL_OBSERVATION,
            "observation_id",
            "hda-context-review-python-install-observation.2026-07-21.0004",
        ),
        "python_install_observation_generator": report_binding(
            HDA_CONTEXT_PYTHON_INSTALL_GENERATOR,
            "artifact_id",
            "hda-context-review-python-install-observation-generator.0003",
        ),
        "python_install_pip_report_run_01": report_binding(
            HDA_CONTEXT_PYTHON_INSTALL_REPORT,
            "artifact_id",
            "hda-context-review-python-install-pip-report.run-01.0002",
        ),
        "python_install_pip_report_run_02": report_binding(
            HDA_CONTEXT_PYTHON_INSTALL_REPORT_RUN_02,
            "artifact_id",
            "hda-context-review-python-install-pip-report.run-02.0002",
        ),
    }
    if value.get("correction_evidence_bindings") != expected_corrections:
        errors.append("context_review.correction_evidence_binding_mismatch")
    errors.extend(context_review_closure_observation_errors(closure))
    errors.extend(python_install_observation_errors(install_observation))

    findings = value.get("finding_ledger")
    expected_finding_count = 14 if len(rounds) == 8 else 15 if len(rounds) == 9 else 16
    expected_ids = [
        f"HDA-CTX-{index:03d}"
        for index in range(1, expected_finding_count + 1)
    ]
    expected_severity = {
        "HDA-CTX-001": "high",
        "HDA-CTX-002": "high",
        "HDA-CTX-003": "high",
        "HDA-CTX-004": "medium",
        "HDA-CTX-005": "high",
        "HDA-CTX-006": "high",
        "HDA-CTX-007": "high",
        "HDA-CTX-008": "high",
        "HDA-CTX-009": "high",
        "HDA-CTX-010": "high",
        "HDA-CTX-011": "medium",
        "HDA-CTX-012": "high",
        "HDA-CTX-013": "high",
        "HDA-CTX-014": "high",
        "HDA-CTX-015": "high",
        "HDA-CTX-016": "high",
    }
    if (
        not isinstance(findings, list)
        or [item.get("finding_id") for item in findings if isinstance(item, dict)]
        != expected_ids
    ):
        errors.append("context_review.finding_ledger_mismatch")
        findings = []
    for finding in findings:
        if (
            not isinstance(finding, dict)
            or finding.get("severity") != expected_severity.get(finding.get("finding_id"))
            or finding.get("finding_state")
            != "changed_candidate_pending_accountable_closure_review"
            or finding.get("accountable_closure_review_completed") is not False
            or not isinstance(finding.get("summary"), str)
            or not finding.get("summary")
            or not isinstance(finding.get("root_cause"), str)
            or not finding.get("root_cause")
            or not isinstance(finding.get("correction"), str)
            or not finding.get("correction")
        ):
            errors.append("context_review.finding_ledger_mismatch")
    finding_one = findings[0] if findings else {}
    if (
        finding_one.get("stale_authentication_challenge_id")
        != "sha256:1b19ecdf21c6a4d9644fe18757cbd11d1bd32b4a0059a23b2e66ff7363e23a05"
        or finding_one.get("corrected_authentication_challenge_id")
        != "sha256:f02587cb898ab1e272f73295b1be167671a0382b98e7dd2f1e2a3344f5e0a6b2"
        or finding_one.get("corrected_authentication_frame_raw_sha256")
        != "sha256:0b1e54b802ada4262e05942a4325a4acc18107d2cb19cfaf8c50d706e466441c"
        or type(finding_one.get("corrected_authentication_frame_byte_count")) is not int
        or finding_one.get("corrected_authentication_frame_byte_count") != 943
    ):
        errors.append("context_review.finding_one_evidence_mismatch")

    if len(rounds) == 8:
        expected_bounded = "refuted"
        expected_semantics = (
            "round_eight_confirmed_the_reissued_root_110a_closure_0002_install_"
            "0003_and_policy_10eb_evidence_but_refuted_the_claimed_local_only_"
            "git_reader_and_strict_predecessor_binding_shape_the_corrected_"
            "reader_and_24_review_known_bads_are_pending_full_integration_and_"
            "fresh_round_nine_review"
        )
    elif len(rounds) == 9:
        expected_bounded = "refuted"
        expected_semantics = (
            "round_nine_confirmed_the_exact_root_110a_closure_0002_install_0003_"
            "policy_10eb_isolated_local_git_reader_strict_binding_controls_and_"
            "24_review_known_bads_but_refuted_repository_integration_because_"
            "the_prq_013_closure_and_its_gate_false_greened_a_stale_positive_"
            "review_and_incomplete_finding_ledger_the_corrected_integration_"
            "gate_is_pending_fresh_round_ten_review"
        )
    elif len(rounds) == 10:
        expected_bounded = "refuted"
        expected_semantics = (
            "round_ten_confirmed_root_110a_closure_0002_install_0003_policy_"
            "10eb_gate_local_git_reader_strict_bindings_and_integration_truth_"
            "controls_but_refuted_the_successor_generator_migration_reader_"
            "because_it_inherited_repository_configuration_the_reissued_root_"
            "97062b_closure_0003_install_0004_and_live_generator_control_are_"
            "pending_fresh_round_eleven_review"
        )
    else:
        expected_bounded = "no_grounded_refutation_observed_within_declared_attacks"
        expected_semantics = (
            "the_reissued_root_97062b_closure_0003_install_0004_policy_10eb_"
            "gate_and_generator_local_git_object_readers_strict_bindings_"
            "integration_truth_controls_and_exact_bound_regeneration_survived_"
            "only_round_eleven_"
            "declared_attacks_and_are_not_declared_correct_approved_independent_"
            "accountably_reviewed_or_gate_ready"
        )
    if (
        value.get("bounded_result") != expected_bounded
        or value.get("bounded_result_semantics") != expected_semantics
    ):
        errors.append("context_review.bounded_result_mismatch")
    if (
        type(value.get("current_consumers_migrated")) is not int
        or value.get("current_consumers_migrated") != 0
    ):
        errors.append("context_review.consumer_migration_escalated")
    invalidation = value.get("invalidation")
    expected_invalidation_keys = {
        "a_future_descendant_may_not_inherit_a_positive_review_without_exact_scope_equality",
        "current_root_does_not_inherit_round_two_positive_evidence",
        "round_four_correction_observation_was_superseded_and_refuted_by_round_five",
        "round_five_correction_observations_were_superseded_and_refuted_by_round_six",
        "round_eight_raw_git_and_binding_controls_were_refuted_and_corrected_before_round_nine",
        "round_seven_integration_surfaces_were_refuted_and_corrected_before_round_eight",
        "round_three_corrective_root_was_superseded_and_refuted_by_round_four",
        "round_two_root_was_superseded_and_refuted_by_round_three",
        "status_prose_this_report_and_later_review_observations_are_outside_the_reviewed_root_to_avoid_self_reference",
    }
    if len(rounds) >= 9:
        expected_invalidation_keys.add(
            "round_nine_integration_truth_surface_was_refuted_and_corrected_"
            "before_round_ten"
        )
    if len(rounds) >= 10:
        expected_invalidation_keys.add(
            "round_ten_generator_git_object_reader_was_refuted_and_corrected_"
            "before_round_eleven"
        )
    if (
        not isinstance(invalidation, dict)
        or set(invalidation) != expected_invalidation_keys
        or any(item is not True for item in invalidation.values())
    ):
        errors.append("context_review.invalidation_boundary_mismatch")
    authority = value.get("authority_boundary")
    expected_authority_keys = {
        "accountable_review_completed",
        "architecture_repository_publication_authorized_by_this_report",
        "external_effects_authorized",
        "gate_a_accepted",
        "organizational_independence_proven",
        "profile_or_schema_issued",
        "prq_013_resolved",
        "real_human_ceremony_observed",
        "ruleset_approved",
        "runtime_or_cloud_authorized",
        "scientific_results_publication_authorized",
        "successor_admitted",
    }
    if (
        not isinstance(authority, dict)
        or set(authority) != expected_authority_keys
        or any(item is not False for item in authority.values())
    ):
        errors.append("context_review.authority_boundary_escalated")
    return errors


def validate_context_isolated_technical_review_known_bads(
    errors: list[str],
) -> int:
    try:
        safe = load(HDA_CONTEXT_REVIEW)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"context review safe control is unreadable: {exc}")
        return 0
    safe_errors = context_isolated_technical_review_errors(safe)
    if safe_errors:
        errors.append(f"context review safe control failed: {safe_errors!r}")
        return 0
    mutations = (
        (
            "context-isolation-erased",
            ("reviewer_provenance", "context_isolated"),
            False,
            "context_review.provenance_boundary_mismatch",
        ),
        (
            "accountable-review-fabricated",
            ("reviewer_provenance", "accountable_reviewer"),
            True,
            "context_review.provenance_boundary_mismatch",
        ),
        (
            "boolean-report-version",
            ("version",),
            True,
            "context_review.identity_or_status_mismatch",
        ),
        (
            "predecessor-tree-swapped",
            (
                "review_rounds",
                0,
                "subject",
                "tree",
            ),
            "0" * 40,
            "context_review.predecessor_git_lineage_mismatch",
        ),
        (
            "predecessor-parent-swapped",
            ("review_rounds", 0, "subject", "sole_parent"),
            "0" * 40,
            "context_review.predecessor_git_parent_mismatch",
        ),
        (
            "predecessor-generation-binding-swapped",
            (
                "review_rounds",
                0,
                "subject",
                "generation_manifest_binding",
                "raw_sha256",
            ),
            "sha256:" + ("0" * 64),
            "context_review.predecessor_generation_manifest_binding_mismatch",
        ),
        (
            "predecessor-vector-byte-count-swapped",
            (
                "review_rounds",
                0,
                "subject",
                "vector_corpus_binding",
                "byte_count",
            ),
            42212,
            "context_review.predecessor_vector_corpus_binding_mismatch",
        ),
        (
            "predecessor-generation-binding-not-object",
            ("review_rounds", 0, "subject", "generation_manifest_binding"),
            None,
            "context_review.predecessor_generation_manifest_binding_shape_invalid",
        ),
        (
            "predecessor-generation-byte-count-float",
            (
                "review_rounds",
                0,
                "subject",
                "generation_manifest_binding",
                "byte_count",
            ),
            16050.0,
            "context_review.predecessor_generation_manifest_binding_shape_invalid",
        ),
        (
            "predecessor-vector-binding-open-shape",
            ("review_rounds", 0, "subject", "vector_corpus_binding"),
            {
                "repository_path": (
                    "tests/human-decision-assurance-successor/vectors.json"
                ),
                "raw_sha256": (
                    "sha256:c81d7d9636d5a4f79a545bbad0ef5454ab8a4bb171d896e003"
                    "5f1096b2c9cc1a"
                ),
                "byte_count": 42211,
                "unreviewed_member": True,
            },
            "context_review.predecessor_vector_corpus_binding_shape_invalid",
        ),
        (
            "current-root-binding-swapped",
            (
                "review_rounds",
                4,
                "subject",
                "reviewed_root_binding",
                "raw_sha256",
            ),
            "sha256:" + ("0" * 64),
            "context_review.round_five_round_mismatch",
        ),
        (
            "round-four-result-promoted-to-accepted",
            ("review_rounds", 3, "result"),
            "accepted",
            "context_review.round_four_round_mismatch",
        ),
        (
            "finding-ledger-erased",
            ("finding_ledger",),
            [],
            "context_review.finding_ledger_mismatch",
        ),
        (
            "bounded-result-promoted-to-accepted",
            ("bounded_result",),
            "accepted",
            "context_review.bounded_result_mismatch",
        ),
        (
            "boolean-consumer-migration",
            ("current_consumers_migrated",),
            False,
            "context_review.consumer_migration_escalated",
        ),
        (
            "gate-a-authority-fabricated",
            ("authority_boundary", "gate_a_accepted"),
            None,
            "context_review.authority_boundary_escalated",
        ),
        (
            "integer-invalidation",
            (
                "invalidation",
                "current_root_does_not_inherit_round_two_positive_evidence",
            ),
            1,
            "context_review.invalidation_boundary_mismatch",
        ),
        (
            "correction-report-binding-swapped",
            (
                "correction_evidence_bindings",
                "python_install_pip_report_run_01",
                "raw_sha256",
            ),
            "sha256:" + ("0" * 64),
            "context_review.correction_evidence_binding_mismatch",
        ),
        (
            "round-four-attack-verdict-swapped",
            ("review_rounds", 3, "attacks", 0, "verdict"),
            "refuted",
            "context_review.round_four_attack_inventory_mismatch",
        ),
        (
            "boolean-mandate-adoption-item",
            ("mandate", "adr_0095_adoption_item"),
            True,
            "context_review.mandate_boundary_mismatch",
        ),
        (
            "finding-accountability-fabricated",
            ("finding_ledger", 7, "accountable_closure_review_completed"),
            True,
            "context_review.finding_ledger_mismatch",
        ),
    )
    passed = 0
    for case_id, path, replacement, expected in mutations:
        candidate = json.loads(json.dumps(safe))
        parent: Any = candidate
        for part in path[:-1]:
            parent = parent[part]
        parent[path[-1]] = replacement
        observed = context_isolated_technical_review_errors(candidate)
        if expected in observed:
            passed += 1
        else:
            errors.append(
                f"context review known-bad {case_id} missed {expected}; "
                f"observed {observed!r}"
            )
    passed += validate_raw_git_object_attack_controls(errors)
    return passed


def human_decision_assurance_errors(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["human_decision_assurance must be an object"]
    errors: list[str] = []
    if set(value) != set(EXPECTED_HUMAN_DECISION_ASSURANCE):
        errors.append("human_decision_assurance members must be closed and exact")
    dynamically_report_bound = {
        "context_isolated_technical_review_binding",
        "context_isolated_technical_review_bounded_result",
    }
    for key, expected_value in EXPECTED_HUMAN_DECISION_ASSURANCE.items():
        if key in dynamically_report_bound:
            continue
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
        "successor_generation_manifest_ref",
        "context_isolated_technical_review_ref",
        "source_evidence_ref",
        "antecedent_decision_ref",
        "decision_ref",
        "co_binding_decision_ref",
        "phase_two_reconstruction_decision_ref",
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

    successor_ref = value.get("successor_generation_manifest_ref")
    successor_binding = value.get("successor_generation_manifest_binding")
    if isinstance(successor_ref, str) and isinstance(successor_binding, dict):
        successor_path = ROOT / successor_ref
        try:
            successor_raw = successor_path.read_bytes()
            successor = load(successor_path)
            vectors = load(
                ROOT / "tests/human-decision-assurance-successor/vectors.json"
            )
            chain_cases = load(
                ROOT
                / "tests/human-decision-assurance-successor/chain-cases.json"
            )
        except (
            OSError,
            json.JSONDecodeError,
            DuplicateKey,
            ValueError,
        ) as exc:
            errors.append(
                "human_decision_assurance successor chain is not strict "
                f"retained evidence: {exc}"
            )
        else:
            observed_digest = "sha256:" + hashlib.sha256(successor_raw).hexdigest()
            expected_successor_binding = {
                "artifact_id": successor.get("artifact_id"),
                "raw_sha256": observed_digest,
                "byte_count": len(successor_raw),
            }
            if successor_binding != expected_successor_binding:
                errors.append(
                    "human_decision_assurance.successor_generation_manifest_"
                    "binding does not match retained strict bytes"
                )

            generated = successor.get("generated_artifacts")
            generated = generated if isinstance(generated, list) else []
            artifact_kind_counts = Counter(
                item.get("artifact_kind")
                for item in generated
                if isinstance(item, dict)
            )
            identities = successor.get("implementation_identity_inventory")
            identities = identities if isinstance(identities, list) else []
            vectors_rows = vectors.get("vectors")
            vectors_rows = vectors_rows if isinstance(vectors_rows, list) else []
            chain_rows = chain_cases.get("cases")
            chain_rows = chain_rows if isinstance(chain_rows, list) else []
            successor_claims_hold = (
                successor.get("artifact_class")
                == "human_decision_assurance_successor_generation_manifest"
                and successor.get("complete_projection_agreement") is True
                and successor.get("content_addressed_backing_blob_count")
                == value.get("synthetic_content_addressed_backing_preimage_count")
                and successor.get("fixture_timestamp_semantics")
                == (
                    "deterministic_fixture_values_not_observed_ceremony_"
                    "runtime_or_external_event_times"
                )
                and artifact_kind_counts["content_addressed_backing_preimage"]
                == value.get("synthetic_content_addressed_backing_preimage_count")
                and artifact_kind_counts["direct_evaluator_stdout_projection"] == 3
                and artifact_kind_counts["schema_valid_recomputation_result"] == 3
                and len(identities) == 3
                and len(set(identities)) == 3
                and len(vectors_rows)
                == value.get("successor_expectation_free_vector_count")
                and len(chain_rows)
                == value.get("successor_chain_known_bad_count")
                and all(
                    isinstance(case, dict)
                    and case.get("kind") == "known_bad"
                    and isinstance(case.get("expected_errors"), list)
                    and bool(case["expected_errors"])
                    and isinstance(case.get("intent_errors"), list)
                    and bool(case["intent_errors"])
                    for case in chain_rows
                )
                and successor.get("organizational_independence_proven") is False
                and successor.get("real_human_ceremony_verified") is False
                and successor.get("gate_a_accepted") is False
                and successor.get("runtime_authorized") is False
                and successor.get("external_effects_authorized") is False
                and successor.get("network_access") is False
            )
            if not successor_claims_hold:
                errors.append(
                    "human_decision_assurance successor manifest or bounded "
                    "corpus counts do not retain the declared synthetic chain"
                )
            if (
                value.get("independent_eligibility_recomputation_retained")
                is not True
                or value.get(
                    "synthetic_conformance_backing_bytes_dereferenced_and_verified"
                )
                is not True
                or value.get("organizational_independence_proven") is not False
            ):
                errors.append(
                    "human_decision_assurance successor proof boundary is not "
                    "source-separated, synthetic, and organizationally unproved"
                )

    review_ref = value.get("context_isolated_technical_review_ref")
    review_binding = value.get("context_isolated_technical_review_binding")
    if isinstance(review_ref, str) and isinstance(review_binding, dict):
        review_path = ROOT / review_ref
        try:
            review_raw = review_path.read_bytes()
            review = load(review_path)
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            DuplicateKey,
            ValueError,
        ) as exc:
            errors.append(
                "human_decision_assurance context review is not strict retained "
                f"evidence: {exc}"
            )
        else:
            expected_review_binding = {
                "report_id": review.get("report_id"),
                "raw_sha256": "sha256:" + hashlib.sha256(review_raw).hexdigest(),
                "byte_count": len(review_raw),
            }
            if review_binding != expected_review_binding:
                errors.append(
                    "human_decision_assurance.context_isolated_technical_review_"
                    "binding does not match retained strict bytes"
                )
            if (
                value.get("context_isolated_technical_review_bounded_result")
                != review.get("bounded_result")
            ):
                errors.append(
                    "human_decision_assurance.context_isolated_technical_review_"
                    "bounded_result does not match retained report"
                )
            errors.extend(context_isolated_technical_review_errors(review))

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
    try:
        current_inventory = load(INVENTORY)
        safe = current_inventory["human_decision_assurance"]
    except (
        DuplicateKey,
        KeyError,
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        errors.append(f"human decision-assurance safe self-test is unreadable: {exc}")
        return 0
    safe = json.loads(json.dumps(safe))
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
            "retained-independent-eligibility-recomputation-erased",
            "independent_eligibility_recomputation_retained",
            False,
        ),
        (
            "independent-recomputation-scope-escalated",
            "independent_recomputation_scope",
            "organizationally_independent_external_review",
        ),
        (
            "organizational-independence-fabricated",
            "organizational_independence_proven",
            True,
        ),
        (
            "successor-generation-manifest-binding-swapped",
            "successor_generation_manifest_binding",
            {
                **EXPECTED_HUMAN_DECISION_ASSURANCE[
                    "successor_generation_manifest_binding"
                ],
                "raw_sha256": "sha256:" + ("0" * 64),
            },
        ),
        (
            "context-review-binding-swapped",
            "context_isolated_technical_review_binding",
            {
                **safe["context_isolated_technical_review_binding"],
                "raw_sha256": "sha256:" + ("0" * 64),
            },
        ),
        (
            "context-review-retention-erased",
            "context_isolated_technical_review_retained",
            False,
        ),
        (
            "context-review-result-promoted-to-accepted",
            "context_isolated_technical_review_bounded_result",
            "accepted",
        ),
        (
            "context-review-promoted-to-accountable",
            "context_isolated_technical_review_is_accountable",
            True,
        ),
        (
            "synthetic-backing-byte-verification-erased",
            "synthetic_conformance_backing_bytes_dereferenced_and_verified",
            False,
        ),
        (
            "synthetic-backing-preimage-count-inflated",
            "synthetic_content_addressed_backing_preimage_count",
            15,
        ),
        (
            "successor-vector-count-inflated",
            "successor_expectation_free_vector_count",
            45,
        ),
        (
            "successor-chain-known-bad-count-inflated",
            "successor_chain_known_bad_count",
            50,
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
        if key == "context_isolated_technical_review_binding":
            expected_reason = (
                "human_decision_assurance.context_isolated_technical_review_"
                "binding does not match retained strict bytes"
            )
        elif key == "context_isolated_technical_review_bounded_result":
            expected_reason = (
                "human_decision_assurance.context_isolated_technical_review_"
                "bounded_result does not match retained report"
            )
        else:
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


def prq_013_closure_errors(
    value: Any,
    assurance: Any,
    review: Any,
) -> list[str]:
    """Bind the machine closure prose to the strict retained review truth."""
    if not isinstance(value, dict):
        return ["PRQ-013 closure must be an object"]
    closure = value.get("closure")
    if not isinstance(closure, str):
        return ["PRQ-013 closure must be text"]
    errors: list[str] = []
    required_fragments = (
        "five separately identified unissued successor schemas",
        "source-separated non-sharing Python, Node.js, and Java",
        "not organizational independence",
        "context-isolated technical-review report refuted the exact published predecessor",
        "correlated non-accountable model-worker evidence",
        "not a ReviewDetermination",
        "zero current consumers are migrated",
        "T0 individual-assurance foundation candidate",
        "T1 AuthorityAssignment",
        "required T2 command, event, state, reducer, currentness, quorum",
        (
            "same-actor confirmation/authenticator cryptographic co-binding "
            "is true strictly as a synthetic construction property"
        ),
        "no real ceremony measured that one natural person performed both acts",
        "Gate A neither requires nor authorizes a live protected ceremony",
        "separately authorized bounded Gate B probe",
    )
    if (
        value.get("finding_id") != "PRQ-013"
        or value.get("status") != "unresolved_blocking"
        or any(fragment not in closure for fragment in required_fragments)
    ):
        errors.append("PRQ-013 must retain the blocking human decision-assurance boundary")

    rounds = review.get("review_rounds") if isinstance(review, dict) else None
    bounded_result = review.get("bounded_result") if isinstance(review, dict) else None
    if not isinstance(rounds, list):
        errors.append("PRQ-013 closure cannot resolve the retained review round count")
    elif bounded_result == "refuted":
        pending_round_by_count = {8: "nine", 9: "ten", 10: "eleven"}
        pending_round = pending_round_by_count.get(len(rounds))
        if pending_round is None:
            errors.append(
                "PRQ-013 closure cannot resolve the next retained review round"
            )
            pending_round = "unresolved"
        expected_result_claim = (
            f"the corrected exact scope remains refuted pending fresh round {pending_round}"
        )
        if expected_result_claim not in closure:
            errors.append(
                "PRQ-013 closure must match the retained context-review bounded result"
            )
    elif bounded_result == "no_grounded_refutation_observed_within_declared_attacks":
        expected_result_claim = (
            "the corrected exact scope retained no_grounded_refutation_observed_"
            "within_declared_round_eleven_attacks"
        )
        if expected_result_claim not in closure:
            errors.append(
                "PRQ-013 closure must match the retained context-review bounded result"
            )
    else:
        errors.append("PRQ-013 closure cannot resolve the retained review bounded result")

    assurance_result = (
        assurance.get("context_isolated_technical_review_bounded_result")
        if isinstance(assurance, dict)
        else None
    )
    if assurance_result != bounded_result:
        errors.append("PRQ-013 closure source result disagrees with the assurance record")

    finding_ledger = review.get("finding_ledger") if isinstance(review, dict) else None
    finding_ids = (
        [item.get("finding_id") for item in finding_ledger]
        if isinstance(finding_ledger, list)
        and all(isinstance(item, dict) for item in finding_ledger)
        else []
    )
    expected_ids = [f"HDA-CTX-{index:03d}" for index in range(1, len(finding_ids) + 1)]
    if not finding_ids or finding_ids != expected_ids:
        errors.append("PRQ-013 closure cannot resolve a contiguous retained finding ledger")
    else:
        last_id = finding_ids[-1]
        pending_claim = (
            f"HDA-CTX-001 through {last_id} remain "
            "changed_candidate_pending_accountable_closure_review"
        )
        closure_obligation = (
            f"HDA-CTX-001 through {last_id} receive accountable closure review"
        )
        if pending_claim not in closure or closure_obligation not in closure:
            errors.append("PRQ-013 closure must retain the complete HDA finding ledger")
    return errors


def validate_prq_013_closure_known_bads(errors: list[str]) -> int:
    try:
        inventory = load(INVENTORY)
        review = load(HDA_CONTEXT_REVIEW)
        safe = inventory["findings"][12]
        assurance = inventory["human_decision_assurance"]
    except (
        DuplicateKey,
        IndexError,
        KeyError,
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        errors.append(f"PRQ-013 closure safe self-test is unreadable: {exc}")
        return 0
    safe_errors = prq_013_closure_errors(safe, assurance, review)
    if safe_errors:
        errors.append(
            "PRQ-013 closure safe self-test was rejected: " + " | ".join(safe_errors)
        )
        return 0

    closure = safe["closure"]
    rounds = review.get("review_rounds")
    pending_round_by_count = {8: "nine", 9: "ten", 10: "eleven"}
    pending_round = pending_round_by_count.get(
        len(rounds) if isinstance(rounds, list) else -1,
        "unresolved",
    )
    result_claim = (
        f"the corrected exact scope remains refuted pending fresh round {pending_round}"
        if review.get("bounded_result") == "refuted"
        else (
            "the corrected exact scope retained no_grounded_refutation_observed_"
            "within_declared_round_eleven_attacks"
        )
    )
    opposite_claim = (
        "the corrected exact scope retained no_grounded_refutation_observed_"
        "within_declared_round_eleven_attacks"
        if review.get("bounded_result") == "refuted"
        else "the corrected exact scope remains refuted pending fresh round eleven"
    )
    result_candidate = json.loads(json.dumps(safe))
    result_candidate["closure"] = closure.replace(result_claim, opposite_claim, 1)
    result_errors = prq_013_closure_errors(result_candidate, assurance, review)

    last_id = review["finding_ledger"][-1]["finding_id"]
    complete_claim = (
        f"HDA-CTX-001 through {last_id} remain "
        "changed_candidate_pending_accountable_closure_review"
    )
    ledger_candidate = json.loads(json.dumps(safe))
    ledger_candidate["closure"] = closure.replace(
        complete_claim,
        "HDA-CTX-001 remains changed_candidate_pending_accountable_closure_review",
        1,
    )
    ledger_errors = prq_013_closure_errors(ledger_candidate, assurance, review)

    passed = 0
    if (
        result_candidate["closure"] != closure
        and "PRQ-013 closure must match the retained context-review bounded result"
        in result_errors
    ):
        passed += 1
    else:
        errors.append(
            "PRQ-013 closure stale-result known-bad did not fire its intended reason"
        )
    if (
        ledger_candidate["closure"] != closure
        and "PRQ-013 closure must retain the complete HDA finding ledger"
        in ledger_errors
    ):
        passed += 1
    else:
        errors.append(
            "PRQ-013 closure incomplete-ledger known-bad did not fire its intended reason"
        )
    return passed


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
        try:
            retained_context_review = load(HDA_CONTEXT_REVIEW)
        except (
            DuplicateKey,
            OSError,
            UnicodeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            errors.append(f"PRQ-013 closure cannot read retained review: {exc}")
            retained_context_review = {}
        errors.extend(
            prq_013_closure_errors(
                prq013,
                inventory.get("human_decision_assurance"),
                retained_context_review,
            )
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
    try:
        closure_observation = load(HDA_CONTEXT_CLOSURE_OBSERVATION)
    except (DuplicateKey, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"context review closure observation is unreadable: {exc}")
    else:
        errors.extend(
            context_review_closure_observation_errors(closure_observation)
        )
    closure_observation_known_bads = (
        validate_context_review_closure_observation_known_bads(errors)
    )
    try:
        python_install_observation = load(
            HDA_CONTEXT_PYTHON_INSTALL_OBSERVATION
        )
    except (DuplicateKey, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Python install observation is unreadable: {exc}")
    else:
        errors.extend(
            python_install_observation_errors(python_install_observation)
        )
    python_install_known_bads = validate_python_install_observation_known_bads(
        errors
    )
    context_review_known_bads = (
        validate_context_isolated_technical_review_known_bads(errors)
    )
    errors.extend(
        next_dependency_contained_tranche_errors(
            inventory.get("next_dependency_contained_tranche")
        )
    )
    next_tranche_known_bads = validate_next_tranche_known_bad(errors)
    prq_009_boundary_known_bads = validate_prq_009_boundary_known_bads(errors)
    prq_013_closure_known_bads = validate_prq_013_closure_known_bads(errors)
    errors.extend(assurance_truth_surface_errors())
    assurance_truth_surface_known_bads = (
        assurance_truth_surface_known_bad_self_tests(errors)
    )
    errors.extend(recovery_truth_surface_errors())
    recovery_truth_surface_known_bads = (
        recovery_truth_surface_known_bad_self_tests(errors)
    )

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
        f"and {context_review_known_bads} context-review known-bads "
        f"and {closure_observation_known_bads} closure-observation known-bads "
        f"and {python_install_known_bads} locked-install known-bads "
        f"and {prq_009_boundary_known_bads} PRQ-009 boundary known-bads "
        f"and {prq_013_closure_known_bads} PRQ-013 closure known-bads "
        f"and {next_tranche_known_bads} next-tranche known-bad "
        f"and {assurance_truth_surface_known_bads} assurance truth-surface "
        f"known-bads and {recovery_truth_surface_known_bads} recovery "
        "truth-surface known-bads "
        "rejected; candidate remains blocked and inactive"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
