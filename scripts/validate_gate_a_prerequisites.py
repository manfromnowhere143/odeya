#!/usr/bin/env python3
"""Validate the architecture-only Gate A prerequisite closure inventory.

This checker proves cross-file inventory equality and nonrecursive dependency
intent only. A pass is not a frozen canonical profile, immutable registry,
constitutional admission, Gate A acceptance, or runtime authorization.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
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
# path, governed heading, end heading, unit kind, unique marker, ordinal,
# SHA-256 of the normalized exact unit, then its complete governed section.
CURRENT_ASSURANCE_UNITS = (
    (
        "docs/HUMAN_DECISION_ASSURANCE.md", "## Retained nonclaims", None,
        "bullet", "The application confirmation receipt and authenticator actor", 3,
        "22d92e1a3afd115ef693ab611315b84f27c740f893063e3de68b5d4187220e4c",
        "832dde591a36cb040d82935144566f52ce32dbe9f504927a9cc9bbac6c806cfd",
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
        "574b7e1a489c8db2bfde219445eedb0f3fc3574e10e741d5bda17e44529f2eeb",
        "5d89475743c1ec7d92caac048ce158a2c9e5a1fca50a731ee5f12a3c0400ff75",
    ),
    (
        "docs/ARCHITECTURE_STATUS.md", "## Critical blockers", None, "table_row", "| A-016 |", None,
        "1a6d4e01a4c712fc52e294b9c73468d2a94e9b50fb6d1b8c208660e1609bbd0a",
        "bfc10627b31d48125e9095c92a61916380ba584006683f5ec9cc011eaa6e11d4",
    ),
    (
        "docs/SESSION_HANDOFF.md", "## What this lane established, and where to put pressure next", None,
        "bullet", "**PRQ-013 now has retained byte-bound/recomputation candidate evidence, not closure.**", 1,
        "ddd88f99d459c0cfb3d9f9f57c12cab6d55d95dafd33ebf8fdaa14d4466c87fe",
        "9184df2c5b288ba5589d6312ca82d7686f8b5e07c61b709dd54c0c450b88e0cc",
    ),
    (
        "docs/SESSION_HANDOFF.md", "## Active PRQ-013 candidate — resolve release status from Git", None,
        "paragraph", "Those are structural and bounded-semantic candidate measurements", 6,
        "e0e4fd58d204a82cbcc698f436818e390225733fd52474dd96f9f449d986852c",
        "b230955b3e07c6d841c5f575c26f3536c14a01148c6c939a0c4f0a1d1fff86d9",
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
PUBLISHED_BASELINE = "34cad10a42027730a515614fc0a5bd664dd8933b"
PUBLISHED_BASELINE_TREE = "4ea6a2c751f76cb97a434e749104ed9f667a68d4"
RECOVERY_INVARIANT_SHA256 = "37b25307a3691eb275d6d457e2643e7400aa09d700b1fdb37ac63170bcb3cf2a"
# SHA-256 of the normalized 51-line recovery program. Its separately named
# cardinality line keeps the single-parent invariant reviewable.
EXPECTED_RECOVERY_PROGRAM_SHA256 = "017526e98aeaec645f10b6f3cbf63aceb5d52ba12f46490d37a6d8891a31529c"
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
        "artifact_id": "hda-successor-generation-manifest.synthetic.0001",
        "raw_sha256": (
            "sha256:f401a95c52ccc49791872584971450c723d3c9d2632d66cbd3e9761fea26e247"
        ),
        "byte_count": 16050,
    },
    "synthetic_conformance_backing_bytes_dereferenced_and_verified": True,
    "synthetic_content_addressed_backing_preimage_count": 14,
    "successor_expectation_free_vector_count": 44,
    "successor_chain_known_bad_count": 48,
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
    "closure_disposition":
        "retain_unissued_t0_byte_bound_and_source_separated_recomputation_"
        "candidate_evidence_pending_context_isolated_technical_review_then_"
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
        "successor_generation_manifest_ref",
        "source_evidence_ref",
        "antecedent_decision_ref",
        "decision_ref",
        "co_binding_decision_ref",
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
            49,
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
            and "five separately identified unissued successor schemas"
            in prq013.get(
                "closure", ""
            )
            and "source-separated non-sharing Python, Node.js, and Java"
            in prq013.get("closure", "")
            and "not organizational independence" in prq013.get("closure", "")
            and "no context-isolated technical determination"
            in prq013.get("closure", "")
            and "zero current consumers are migrated" in prq013.get(
                "closure", ""
            )
            and "T0 individual-assurance foundation candidate"
            in prq013.get("closure", "")
            and "T1 AuthorityAssignment" in prq013.get("closure", "")
            and "required T2 command, event, state, reducer, currentness, quorum"
            in prq013.get("closure", "")
            and (
                "same-actor confirmation/authenticator cryptographic co-binding "
                "is true strictly as a synthetic construction property"
            )
            in prq013.get("closure", "")
            and (
                "no real ceremony measured that one natural person performed both acts"
            )
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
        f"and {prq_009_boundary_known_bads} PRQ-009 boundary known-bads "
        f"and {next_tranche_known_bads} next-tranche known-bad "
        f"and {assurance_truth_surface_known_bads} assurance truth-surface "
        f"known-bads and {recovery_truth_surface_known_bads} recovery "
        "truth-surface known-bads "
        "rejected; candidate remains blocked and inactive"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
