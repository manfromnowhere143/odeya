import { createHash } from "node:crypto";
import { TextDecoder } from "node:util";

import {
  InputRefusal,
  assertExactKeys,
  isRecord,
  parseStrictJsonText,
} from "./input-adapter.mjs";

const HAS_OWN = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
const SHA256_PATTERN = /^sha256:[0-9a-f]{64}$/;
const IDENTIFIER_PATTERN = /^[a-z][a-z0-9]*(?:[._:-][a-z0-9]+)+$/;
const RESULT_REASON_PATTERN = /^(?:eligible|indeterminate|invalid)\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*$/;
const OBSERVATION_STATUSES = ["supported", "contradicted", "unknown", "not_applicable"];

const DOMAIN_ORDER = [
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
];

const PUBLIC_DOMAIN_ORDER = DOMAIN_ORDER.slice(2);

const CATEGORICAL_INPUT_ORDER = [
  "challenge_consumption_state",
  "prior_consumption_count",
  "result_consumption_count",
  "assertion_acceptance_atomic_action_id",
  "consumption_atomic_action_id",
  "atomic_action_record_role",
  "atomic_action_record_observation",
  "decision_confirmation_principal_id",
  "decision_confirmation_initiator_class",
  "decision_confirmation_separate_from_authenticator_gesture",
  "cross_origin_disposition",
  "signature_counter_disposition",
  "shared_effective_control_principal_ids",
  "verifier_relation_to_decision_principal",
];

const CATEGORICAL_ORDER = [
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
];

const RULESET_KEYS = [
  "schema_version",
  "artifact_class",
  "ruleset_id",
  "ruleset_version",
  "candidate_status",
  "decision_ref",
  "supersedes_ruleset_id",
  "scope",
  "normative_data_model",
  "required_domains",
  "required_evidence_observation_sequence_order",
  "required_categorical_inputs",
  "required_categorical_conditions",
  "domain_fold",
  "domain_input_observation_count_contract",
  "backing_byte_integrity_fold",
  "categorical_law",
  "sanitation_law",
  "precedence_and_totality",
  "integrity_reason_attribution",
  "reason_code_contract",
  "independent_recomputation_contract",
  "acyclic_chain_contract",
  "resource_identity_contract",
  "proof_boundary",
];

const RESOLVER_KEYS = [
  "schema_version",
  "artifact_class",
  "profile_id",
  "profile_version",
  "candidate_status",
  "decision_ref",
  "identity",
  "repository_bundle_transport",
  "closed_role_inventory",
  "descriptor_requirements",
  "total_resolution_algorithm",
  "typed_resolution_outcomes",
  "format_checks",
  "receipt_frame_relation",
  "refusal_rules",
  "proof_boundary",
];

function refuse(condition, message) {
  if (!condition) throw new InputRefusal(message);
}

function exactArray(actual, expected, label) {
  refuse(Array.isArray(actual), `${label}: expected array`);
  refuse(actual.length === expected.length, `${label}: wrong cardinality`);
  for (let index = 0; index < expected.length; index += 1) {
    refuse(actual[index] === expected[index], `${label}: mismatch at index ${index}`);
  }
}

function requireString(value, label) {
  refuse(typeof value === "string", `${label}: expected string`);
  return value;
}

function requireBoolean(value, label) {
  refuse(typeof value === "boolean", `${label}: expected boolean`);
  return value;
}

function requireInteger(value, label, minimum = Number.MIN_SAFE_INTEGER) {
  refuse(Number.isSafeInteger(value) && value >= minimum, `${label}: expected safe integer >= ${minimum}`);
  return value;
}

function sortedUnique(codes) {
  const result = [...new Set(codes)];
  result.sort((left, right) => Buffer.compare(Buffer.from(left, "utf8"), Buffer.from(right, "utf8")));
  for (const code of result) refuse(RESULT_REASON_PATTERN.test(code), `internal error: malformed reason code ${code}`);
  return result;
}

function jsonEqual(left, right) {
  if (left === right) return true;
  if (Array.isArray(left) || Array.isArray(right)) {
    return Array.isArray(left) &&
      Array.isArray(right) &&
      left.length === right.length &&
      left.every((value, index) => jsonEqual(value, right[index]));
  }
  if (isRecord(left) || isRecord(right)) {
    if (!isRecord(left) || !isRecord(right)) return false;
    const leftKeys = Object.keys(left).sort();
    const rightKeys = Object.keys(right).sort();
    return leftKeys.length === rightKeys.length &&
      leftKeys.every((key, index) => key === rightKeys[index] && jsonEqual(left[key], right[key]));
  }
  return false;
}

function assertNestedKeys(object, keys, label) {
  assertExactKeys(object, keys, [], label);
}

export function validateRuleset(ruleset) {
  assertNestedKeys(ruleset, RULESET_KEYS, "ruleset");
  refuse(ruleset.schema_version === "0.2.0", "ruleset: unsupported schema_version");
  refuse(
    ruleset.artifact_class === "human_decision_assurance_individual_eligibility_ruleset_candidate",
    "ruleset: wrong artifact_class",
  );
  refuse(
    ruleset.ruleset_id === "urn:odeya:human-decision-assurance-eligibility:0.2.0-candidate",
    "ruleset: wrong ruleset_id",
  );
  refuse(ruleset.ruleset_version === "0.2.0", "ruleset: wrong ruleset_version");
  refuse(
    ruleset.candidate_status === "unissued_architecture_candidate_not_policy_authority",
    "ruleset: wrong candidate_status",
  );

  assertNestedKeys(
    ruleset.normative_data_model,
    [
      "serialization",
      "object_member_names_unique",
      "unknown_members",
      "numbers",
      "strings",
      "arrays",
      "content_address_pattern",
      "identifier_pattern",
      "observation_status_domain",
      "read_disposition_domain",
      "comparison_disposition_domain",
      "result_disposition_domain",
    ],
    "ruleset normative_data_model",
  );
  refuse(ruleset.normative_data_model.serialization === "json_utf8", "ruleset: serialization changed");
  refuse(ruleset.normative_data_model.object_member_names_unique === true, "ruleset: duplicate-name law changed");
  refuse(ruleset.normative_data_model.unknown_members === "refuse", "ruleset: unknown-member law changed");
  refuse(ruleset.normative_data_model.content_address_pattern === "^sha256:[0-9a-f]{64}$", "ruleset: digest pattern changed");
  refuse(ruleset.normative_data_model.identifier_pattern === "^[a-z][a-z0-9]*(?:[._:-][a-z0-9]+)+$", "ruleset: identifier pattern changed");
  exactArray(ruleset.normative_data_model.observation_status_domain, OBSERVATION_STATUSES, "ruleset observation statuses");
  exactArray(ruleset.normative_data_model.result_disposition_domain, ["eligible", "indeterminate", "invalid"], "ruleset result dispositions");

  refuse(Array.isArray(ruleset.required_domains), "ruleset: required_domains must be an array");
  exactArray(ruleset.required_domains.map((entry) => entry.domain_id), DOMAIN_ORDER, "ruleset required domains");
  for (let index = 0; index < ruleset.required_domains.length; index += 1) {
    const entry = ruleset.required_domains[index];
    assertNestedKeys(entry, ["domain_id", "source", "required_in_evidence_observation_sequences"], `ruleset required domain ${index}`);
    requireString(entry.source, `ruleset required domain ${index} source`);
    requireBoolean(entry.required_in_evidence_observation_sequences, `ruleset required domain ${index} evidence flag`);
    refuse(
      entry.required_in_evidence_observation_sequences === (index >= 2),
      `ruleset required domain ${index}: evidence flag mismatch`,
    );
  }
  exactArray(
    ruleset.required_evidence_observation_sequence_order,
    PUBLIC_DOMAIN_ORDER,
    "ruleset public domain order",
  );
  exactArray(ruleset.required_categorical_inputs, CATEGORICAL_INPUT_ORDER, "ruleset categorical inputs");
  exactArray(ruleset.required_categorical_conditions, CATEGORICAL_ORDER, "ruleset categorical conditions");

  assertNestedKeys(
    ruleset.domain_fold,
    [
      "input",
      "algorithm",
      "empty_or_absent_required_sequence",
      "contradicted_then_unknown",
      "unknown_then_contradicted",
      "reason_emission",
      "lower_precedence_raw_observation_codes_retained_after_contradiction",
      "implementation_private_domains_allowed",
      "undeclared_eligibility_bearing_input",
    ],
    "ruleset domain_fold",
  );
  refuse(ruleset.domain_fold.contradicted_then_unknown === "contradicted", "ruleset: contradicted precedence changed");
  refuse(ruleset.domain_fold.unknown_then_contradicted === "contradicted", "ruleset: contradicted precedence changed");
  refuse(
    ruleset.domain_fold.reason_emission === "emit_exactly_the_code_for_the_single_folded_domain_outcome_not_one_code_per_raw_observation",
    "ruleset: domain reason-emission contract changed",
  );
  refuse(
    ruleset.domain_fold.lower_precedence_raw_observation_codes_retained_after_contradiction === false,
    "ruleset: lower-precedence domain reasons retained",
  );
  refuse(ruleset.domain_fold.implementation_private_domains_allowed === false, "ruleset: private domains admitted");

  assertNestedKeys(
    ruleset.domain_input_observation_count_contract,
    [
      "exact_core_and_evidence_binding",
      "backing_byte_integrity",
      "ordinary_public_domain",
      "sanitation",
      "missing_required_sequence",
      "fabricated_minimum_count_allowed",
    ],
    "ruleset domain input observation count contract",
  );
  refuse(
    ruleset.domain_input_observation_count_contract.exact_core_and_evidence_binding === "one_compound_binding_observation",
    "ruleset: exact-binding count contract changed",
  );
  refuse(
    ruleset.domain_input_observation_count_contract.backing_byte_integrity === "number_of_present_verification_rows_not_number_of_descriptors",
    "ruleset: backing count contract changed",
  );
  refuse(ruleset.domain_input_observation_count_contract.missing_required_sequence === 0, "ruleset: missing sequence count changed");
  refuse(ruleset.domain_input_observation_count_contract.fabricated_minimum_count_allowed === false, "ruleset: fabricated count admitted");

  assertNestedKeys(
    ruleset.backing_byte_integrity_fold,
    [
      "inventory_must_equal_resolver_profile_closed_role_inventory",
      "inventory_validation_precedes_per_role_resolution",
      "invalid_inventory_result",
      "one_total_receipt_row_per_inventory_role",
      "duplicate_or_unexpected_role",
      "readable_match_and_well_formed",
      "missing_or_unreadable",
      "readable_mismatch",
      "readable_malformed",
      "successful_zero_byte_representation_of_missing_bytes",
      "missing_observation_is_never_zero",
      "receipt_frame_relation_mismatch",
    ],
    "ruleset backing-byte fold",
  );
  refuse(ruleset.backing_byte_integrity_fold.inventory_validation_precedes_per_role_resolution === true, "ruleset: backing inventory no longer precedes resolution");
  refuse(
    ruleset.backing_byte_integrity_fold.invalid_inventory_result === "emit_only_invalid.backing_byte.closed_role_inventory_mismatch_for_the_backing_domain",
    "ruleset: invalid backing inventory result changed",
  );

  assertNestedKeys(
    ruleset.reason_code_contract,
    [
      "grammar",
      "character_set",
      "sort_order",
      "uniqueness",
      "negative_prefixes",
      "eligible_exact_reason_codes",
      "invalid_result_reason_set",
      "indeterminate_result_reason_set",
      "positive_code_in_negative_result",
      "negative_code_in_eligible_result",
      "stale_unknown_duplicate_unsorted_or_extra_code",
      "recorded_set_must_equal_recomputed_set",
      "dynamic_domain_code_templates",
      "dynamic_backing_code_templates",
      "categorical_projection_code_templates",
      "fixed_reason_codes",
    ],
    "ruleset reason_code_contract",
  );
  const domainTemplates = ruleset.reason_code_contract.dynamic_domain_code_templates;
  assertNestedKeys(domainTemplates, ["supported", "contradicted", "missing", "unknown", "not_applicable"], "ruleset domain reason templates");
  refuse(domainTemplates.supported === "eligible.domain.{domain_id}.supported", "ruleset: supported domain template changed");
  refuse(domainTemplates.contradicted === "invalid.domain.{domain_id}.contradicted", "ruleset: contradicted domain template changed");
  refuse(domainTemplates.missing === "indeterminate.domain.{domain_id}.missing", "ruleset: missing domain template changed");
  refuse(domainTemplates.unknown === "indeterminate.domain.{domain_id}.unknown", "ruleset: unknown domain template changed");
  refuse(domainTemplates.not_applicable === "indeterminate.domain.{domain_id}.not_applicable", "ruleset: not-applicable domain template changed");
  const backingTemplates = ruleset.reason_code_contract.dynamic_backing_code_templates;
  assertNestedKeys(backingTemplates, ["supported", "missing", "unreadable", "mismatch", "malformed"], "ruleset backing reason templates");
  refuse(backingTemplates.supported === "eligible.domain.backing_byte_integrity.supported", "ruleset: backing supported code changed");
  const categoricalTemplates = ruleset.reason_code_contract.categorical_projection_code_templates;
  assertNestedKeys(
    categoricalTemplates,
    ["satisfied", "failed", "unknown", "not_applicable", "global_negative_union_rule", "global_eligible_rule"],
    "ruleset categorical reason templates",
  );
  refuse(categoricalTemplates.satisfied === "eligible.categorical.{condition_id}.satisfied", "ruleset: categorical satisfied template changed");
  refuse(categoricalTemplates.failed === "invalid.categorical.{condition_id}.failed", "ruleset: categorical failed template changed");
  refuse(categoricalTemplates.unknown === "indeterminate.categorical.{condition_id}.unknown", "ruleset: categorical unknown template changed");
  refuse(categoricalTemplates.not_applicable === "indeterminate.categorical.{condition_id}.not_applicable", "ruleset: categorical not-applicable template changed");
  exactArray(ruleset.reason_code_contract.eligible_exact_reason_codes, ["eligible.all_required_inputs_supported"], "ruleset eligible reason set");
  refuse(ruleset.reason_code_contract.recorded_set_must_equal_recomputed_set === true, "ruleset: result equality law changed");

  assertNestedKeys(
    ruleset.sanitation_law,
    [
      "observation_sequence_uses_domain_fold",
      "any_contradicted_observation",
      "any_nonempty_forbidden_content_finding",
      "missing_unknown_or_not_applicable_without_contradiction",
      "all_required_observations_supported_and_no_forbidden_content",
      "contradiction_may_be_collapsed_to_unknown",
      "dedicated_contradiction_code",
      "generic_domain_contradiction_code_also_emitted",
    ],
    "ruleset sanitation law",
  );
  refuse(ruleset.sanitation_law.dedicated_contradiction_code === "invalid.sanitation.contradicted", "ruleset: sanitation contradiction code changed");
  refuse(ruleset.sanitation_law.generic_domain_contradiction_code_also_emitted === false, "ruleset: generic sanitation contradiction admitted");

  assertNestedKeys(
    ruleset.precedence_and_totality,
    [
      "ordered_precedence",
      "invalid",
      "indeterminate",
      "eligible",
      "later_inputs_may_weaken_an_earlier_finding",
      "evaluation_is_total_over_every_declared_input",
      "missing_is_zero",
      "timeout_retry_exhaustion_or_missing_reviewer_implies_approval",
    ],
    "ruleset precedence_and_totality",
  );
  exactArray(ruleset.precedence_and_totality.ordered_precedence, ["invalid", "indeterminate", "eligible"], "ruleset precedence");
  refuse(ruleset.precedence_and_totality.later_inputs_may_weaken_an_earlier_finding === false, "ruleset: monotonicity changed");
  refuse(ruleset.precedence_and_totality.missing_is_zero === false, "ruleset: missing became zero");

  assertNestedKeys(
    ruleset.integrity_reason_attribution,
    ["required_domain_inventory_mismatch", "undeclared_eligibility_domain", "resource_identity_version_mismatch", "global_reason_set_copies_each_attributed_negative_code"],
    "ruleset integrity reason attribution",
  );
  for (const field of ["required_domain_inventory_mismatch", "undeclared_eligibility_domain", "resource_identity_version_mismatch"]) {
    refuse(ruleset.integrity_reason_attribution[field] === "exact_core_and_evidence_binding_domain", `ruleset: ${field} attribution changed`);
  }
  refuse(ruleset.integrity_reason_attribution.global_reason_set_copies_each_attributed_negative_code === true, "ruleset: integrity reasons not copied globally");

  const recomputation = ruleset.independent_recomputation_contract;
  refuse(isRecord(recomputation), "ruleset: recomputation contract missing");
  exactArray(recomputation.required_result_roles, ["python", "nodejs_24_18_0", "java_21_0_9"], "ruleset implementation roles");
  refuse(
    isRecord(recomputation.required_toolchain_versions) &&
      recomputation.required_toolchain_versions.nodejs_24_18_0 === "24.18.0",
    "ruleset: Node.js toolchain identity changed",
  );
  refuse(recomputation.full_ordered_domain_projection_required === true, "ruleset: full domain projection not required");
  refuse(recomputation.full_categorical_projection_required === true, "ruleset: full categorical projection not required");
  refuse(recomputation.full_reason_code_set_required === true, "ruleset: full reason set not required");
  return ruleset;
}

export function validateResolver(resolver) {
  assertNestedKeys(resolver, RESOLVER_KEYS, "resolver profile");
  refuse(resolver.schema_version === "0.1.0", "resolver profile: unsupported schema_version");
  refuse(
    resolver.artifact_class === "human_decision_assurance_content_address_resolver_profile_candidate",
    "resolver profile: wrong artifact_class",
  );
  refuse(
    resolver.profile_id === "urn:odeya:human-decision-assurance:content-address-resolver:0.1.0-candidate",
    "resolver profile: wrong profile_id",
  );
  refuse(resolver.profile_version === "0.1.0", "resolver profile: wrong profile_version");

  assertNestedKeys(
    resolver.identity,
    ["canonical_object_identity", "content_address_pattern", "digest_algorithm", "digest_input", "filename_or_descriptor_is_proof", "transport_path_is_identity"],
    "resolver identity",
  );
  refuse(resolver.identity.content_address_pattern === "^sha256:[0-9a-f]{64}$", "resolver: digest pattern changed");
  refuse(resolver.identity.digest_algorithm === "sha-256", "resolver: digest algorithm changed");
  refuse(resolver.identity.digest_input === "exact_raw_preimage_bytes", "resolver: digest input changed");
  refuse(resolver.identity.filename_or_descriptor_is_proof === false, "resolver: descriptor became proof");
  refuse(resolver.identity.transport_path_is_identity === false, "resolver: path became identity");

  const transport = resolver.repository_bundle_transport;
  assertNestedKeys(
    transport,
    [
      "root",
      "path_template",
      "path_is_derived_only_from_content_address",
      "absolute_paths_allowed",
      "dot_segments_allowed",
      "symbolic_links_allowed",
      "hard_link_identity_trusted",
      "network_fallback_allowed",
      "environment_variable_expansion_allowed",
      "resolver_search_path_allowed",
      "read_mode",
      "maximum_read_count_per_role",
      "bytes_may_be_normalized_or_reencoded",
    ],
    "resolver transport",
  );
  refuse(transport.root === "architecture/evidence-blobs/sha256", "resolver: transport root changed");
  refuse(transport.path_template === "architecture/evidence-blobs/sha256/{hex[0:2]}/{hex[2:64]}", "resolver: path template changed");
  refuse(transport.path_is_derived_only_from_content_address === true, "resolver: path derivation changed");
  refuse(transport.network_fallback_allowed === false, "resolver: network fallback admitted");
  refuse(transport.read_mode === "binary_exact_no_newline_conversion", "resolver: read mode changed");
  refuse(transport.maximum_read_count_per_role === 1, "resolver: read count changed");
  refuse(transport.bytes_may_be_normalized_or_reencoded === false, "resolver: normalization admitted");

  refuse(Array.isArray(resolver.closed_role_inventory) && resolver.closed_role_inventory.length === 14, "resolver: closed role inventory must contain 14 roles");
  const roleNames = new Set();
  for (let index = 0; index < resolver.closed_role_inventory.length; index += 1) {
    const role = resolver.closed_role_inventory[index];
    assertNestedKeys(role, ["ordinal", "role", "required_media_type", "required_byte_fidelity"], `resolver role ${index}`);
    refuse(role.ordinal === index + 1, `resolver role ${index}: ordinal mismatch`);
    requireString(role.role, `resolver role ${index} role`);
    refuse(!roleNames.has(role.role), `resolver role ${index}: duplicate role`);
    roleNames.add(role.role);
    requireString(role.required_media_type, `resolver role ${index} media type`);
    requireString(role.required_byte_fidelity, `resolver role ${index} byte fidelity`);
  }

  const descriptor = resolver.descriptor_requirements;
  assertNestedKeys(
    descriptor,
    [
      "role_unique_and_exactly_once",
      "artifact_id_unique_and_nonempty",
      "content_address_lowercase_and_syntactically_valid",
      "byte_count_positive_integer",
      "media_type_exact_match_to_role",
      "byte_fidelity_exact_match_to_role",
      "resolver_independent_blob_path_exact_match",
      "inventory_order_exact_match",
      "extra_roles_allowed",
    ],
    "resolver descriptor requirements",
  );
  for (const [name, value] of Object.entries(descriptor)) {
    refuse(value === (name !== "extra_roles_allowed"), `resolver descriptor requirement ${name} changed`);
  }

  assertNestedKeys(resolver.format_checks, ["json_roles", "cbor_role", "confirmation_receipt_frame_role"], "resolver format checks");
  refuse(resolver.format_checks.json_roles === "strict_utf8_json_with_unique_member_names_and_no_nonfinite_numbers", "resolver: JSON format changed");
  refuse(resolver.format_checks.cbor_role === "one_complete_deterministically_decodable_cbor_item_without_trailing_bytes", "resolver: CBOR format changed");
  const frame = resolver.format_checks.confirmation_receipt_frame_role;
  assertNestedKeys(
    frame,
    ["magic_ascii", "field_count_encoding", "field_entry_encoding", "ordered_fields", "field_value_contracts", "exact_binary_preimage_required", "json_rendering_or_reencoding_allowed", "trailing_bytes_allowed"],
    "resolver frame format",
  );
  refuse(frame.magic_ascii === "ODEYA-HDA-CONFIRMATION-RECEIPT-V1", "resolver: frame magic changed");
  exactArray(
    frame.ordered_fields,
    ["presentation_challenge_id", "displayed_bytes_sha256", "displayed_byte_count", "rendering_profile_id", "confirmation_gesture_kind", "confirmation_gesture_at"],
    "resolver frame field order",
  );
  assertNestedKeys(
    frame.field_value_contracts,
    ["presentation_challenge_id", "displayed_bytes_sha256", "displayed_byte_count", "rendering_profile_id", "confirmation_gesture_kind", "confirmation_gesture_at"],
    "resolver frame value contracts",
  );
  refuse(frame.field_value_contracts.presentation_challenge_id === "exactly_32_raw_octets", "resolver: challenge frame value changed");
  refuse(frame.field_value_contracts.displayed_bytes_sha256 === "exactly_32_raw_octets", "resolver: displayed digest frame value changed");
  refuse(frame.field_value_contracts.displayed_byte_count === "exactly_4_octets_unsigned_32_bit_big_endian", "resolver: displayed count frame value changed");
  refuse(frame.field_value_contracts.rendering_profile_id === "nonempty_strict_ascii", "resolver: rendering profile frame value changed");
  refuse(frame.field_value_contracts.confirmation_gesture_kind === "nonempty_strict_ascii", "resolver: gesture kind frame value changed");
  refuse(
    frame.field_value_contracts.confirmation_gesture_at === "strict_ascii_utc_timestamp_yyyy_mm_dd_t_hh_mm_ss_dot_six_fraction_digits_z",
    "resolver: gesture timestamp frame value changed",
  );
  refuse(frame.exact_binary_preimage_required === true, "resolver: exact frame bytes not required");
  refuse(frame.json_rendering_or_reencoding_allowed === false, "resolver: frame reencoding admitted");
  refuse(frame.trailing_bytes_allowed === false, "resolver: frame trailing bytes admitted");
  return resolver;
}

function validateObservation(observation, label) {
  assertNestedKeys(observation, ["sequence_index", "observation_id", "status", "evidence_role_refs"], label);
  requireInteger(observation.sequence_index, `${label} sequence_index`, 0);
  requireString(observation.observation_id, `${label} observation_id`);
  refuse(OBSERVATION_STATUSES.includes(observation.status), `${label}: invalid status`);
  refuse(Array.isArray(observation.evidence_role_refs), `${label}: evidence_role_refs must be an array`);
  observation.evidence_role_refs.forEach((role, index) => requireString(role, `${label} evidence_role_refs[${index}]`));
}

function validateMaterializedInput(input) {
  assertNestedKeys(
    input,
    ["input_id", "ruleset_input", "exact_core_and_evidence_binding_observation", "participant_input", "forbidden_content_and_sanitation", "backing_byte_inputs"],
    "materialized input",
  );
  requireString(input.input_id, "materialized input input_id");
  refuse(OBSERVATION_STATUSES.includes(input.exact_core_and_evidence_binding_observation), "materialized input: invalid exact-binding observation");

  assertNestedKeys(input.ruleset_input, ["ruleset_id", "ruleset_version", "required_domain_ids"], "materialized input ruleset_input");
  requireString(input.ruleset_input.ruleset_id, "materialized input ruleset_id");
  requireString(input.ruleset_input.ruleset_version, "materialized input ruleset_version");
  refuse(Array.isArray(input.ruleset_input.required_domain_ids), "materialized input: required_domain_ids must be an array");
  input.ruleset_input.required_domain_ids.forEach((domain, index) => requireString(domain, `materialized input required_domain_ids[${index}]`));

  const participant = input.participant_input;
  refuse(isRecord(participant), "materialized input: participant_input must be an object");
  const participantKeys = new Set(Object.keys(participant));
  for (const required of ["principal_id", "domain_observation_sequences", "categorical_inputs"]) {
    refuse(participantKeys.has(required), `materialized input participant_input: missing ${required}`);
  }
  const undeclaredParticipantKeys = [...participantKeys].filter(
    (key) => !["principal_id", "domain_observation_sequences", "categorical_inputs"].includes(key),
  );
  requireString(participant.principal_id, "materialized input principal_id");
  refuse(Array.isArray(participant.domain_observation_sequences), "materialized input: domain_observation_sequences must be an array");
  for (let sequenceIndex = 0; sequenceIndex < participant.domain_observation_sequences.length; sequenceIndex += 1) {
    const sequence = participant.domain_observation_sequences[sequenceIndex];
    assertNestedKeys(sequence, ["domain", "public_eligibility_domain", "observations"], `materialized input domain sequence ${sequenceIndex}`);
    requireString(sequence.domain, `materialized input domain sequence ${sequenceIndex} domain`);
    requireBoolean(sequence.public_eligibility_domain, `materialized input domain sequence ${sequenceIndex} public flag`);
    refuse(Array.isArray(sequence.observations), `materialized input domain sequence ${sequenceIndex}: observations must be an array`);
    sequence.observations.forEach((observation, observationIndex) => {
      validateObservation(observation, `materialized input domain sequence ${sequenceIndex} observation ${observationIndex}`);
      refuse(observation.sequence_index === observationIndex, `materialized input domain sequence ${sequenceIndex}: sequence_index mismatch`);
    });
  }

  assertExactKeys(participant.categorical_inputs, [], CATEGORICAL_INPUT_ORDER, "materialized input categorical_inputs");

  const sanitation = input.forbidden_content_and_sanitation;
  assertNestedKeys(
    sanitation,
    [
      "ordered_forbidden_content_observations",
      "sanitization_verification_sequence",
      "exact_cryptographic_input_transformation",
      "sanitation_authorizes_exact_input_transformation",
      "forbidden_content_present_disposition",
      "unknown_sanitation_disposition",
    ],
    "materialized input sanitation",
  );
  refuse(Array.isArray(sanitation.ordered_forbidden_content_observations), "materialized input: forbidden content observations must be an array");
  sanitation.ordered_forbidden_content_observations.forEach((observation, index) => {
    assertNestedKeys(observation, ["content_class", "disposition", "evidence_role_refs"], `materialized input forbidden observation ${index}`);
    requireString(observation.content_class, `materialized input forbidden observation ${index} content_class`);
    refuse(["absent", "present", "unknown", "not_applicable"].includes(observation.disposition), `materialized input forbidden observation ${index}: invalid disposition`);
    refuse(Array.isArray(observation.evidence_role_refs), `materialized input forbidden observation ${index}: evidence_role_refs must be an array`);
    observation.evidence_role_refs.forEach((role, roleIndex) => requireString(role, `materialized input forbidden observation ${index} role ${roleIndex}`));
  });
  refuse(Array.isArray(sanitation.sanitization_verification_sequence), "materialized input: sanitization verification must be an array");
  sanitation.sanitization_verification_sequence.forEach((observation, index) => {
    validateObservation(observation, `materialized input sanitization verification ${index}`);
    refuse(observation.sequence_index === index, "materialized input: sanitization verification sequence_index mismatch");
  });
  requireString(sanitation.exact_cryptographic_input_transformation, "materialized input exact transformation");
  requireBoolean(sanitation.sanitation_authorizes_exact_input_transformation, "materialized input transformation authority");
  requireString(sanitation.forbidden_content_present_disposition, "materialized input forbidden disposition rule");
  requireString(sanitation.unknown_sanitation_disposition, "materialized input unknown sanitation rule");

  const backing = input.backing_byte_inputs;
  assertNestedKeys(backing, ["resolver_profile_id", "artifacts", "confirmation_receipt_frame_relation"], "materialized input backing_byte_inputs");
  requireString(backing.resolver_profile_id, "materialized input resolver_profile_id");
  refuse(Array.isArray(backing.artifacts), "materialized input: artifacts must be an array");
  backing.artifacts.forEach((artifact, index) => {
    assertExactKeys(artifact, ["descriptor"], ["preimage", "verification_row"], `materialized input artifact ${index}`);
    assertNestedKeys(
      artifact.descriptor,
      ["artifact_id", "role", "content_address", "byte_count", "media_type", "byte_fidelity", "repository_blob_path", "synthetic_preimage", "sanitization_status"],
      `materialized input artifact ${index} descriptor`,
    );
    requireString(artifact.descriptor.artifact_id, `materialized input artifact ${index} artifact_id`);
    requireString(artifact.descriptor.role, `materialized input artifact ${index} role`);
    requireString(artifact.descriptor.content_address, `materialized input artifact ${index} content_address`);
    requireInteger(artifact.descriptor.byte_count, `materialized input artifact ${index} byte_count`, 0);
    requireString(artifact.descriptor.media_type, `materialized input artifact ${index} media_type`);
    requireString(artifact.descriptor.byte_fidelity, `materialized input artifact ${index} byte_fidelity`);
    requireString(artifact.descriptor.repository_blob_path, `materialized input artifact ${index} repository_blob_path`);
    requireBoolean(artifact.descriptor.synthetic_preimage, `materialized input artifact ${index} synthetic_preimage`);
    requireString(artifact.descriptor.sanitization_status, `materialized input artifact ${index} sanitization_status`);
    if (HAS_OWN(artifact, "preimage")) {
      assertExactKeys(artifact.preimage, ["repository_blob_path"], ["raw_base64"], `materialized input artifact ${index} preimage`);
      requireString(artifact.preimage.repository_blob_path, `materialized input artifact ${index} preimage path`);
      if (HAS_OWN(artifact.preimage, "raw_base64")) requireString(artifact.preimage.raw_base64, `materialized input artifact ${index} raw_base64`);
    }
    if (HAS_OWN(artifact, "verification_row")) {
      assertNestedKeys(
        artifact.verification_row,
        [
          "role",
          "artifact_id",
          "expected_content_address",
          "expected_byte_count",
          "expected_media_type",
          "expected_byte_fidelity",
          "repository_blob_path",
          "read_disposition",
          "observed_raw_sha256",
          "observed_byte_count",
          "format_disposition",
          "comparison_disposition",
          "integrity_observation",
        ],
        `materialized input artifact ${index} verification_row`,
      );
    }
  });
  assertNestedKeys(
    backing.confirmation_receipt_frame_relation,
    [
      "frame_role",
      "expected_frame_content_address",
      "observed_frame_raw_sha256",
      "presentation_challenge_id",
      "authentication_challenge_id",
      "authentication_frame_committed_receipt_sha256",
      "binary_framing_disposition",
      "presentation_to_receipt_relation_disposition",
      "receipt_to_authentication_relation_disposition",
    ],
    "materialized input frame relation",
  );
  return { undeclaredParticipantKeys };
}

function sha256Address(bytes) {
  return `sha256:${createHash("sha256").update(bytes).digest("hex")}`;
}

function derivedRepositoryPath(contentAddress) {
  if (!SHA256_PATTERN.test(contentAddress)) return null;
  const hexadecimal = contentAddress.slice("sha256:".length);
  return `architecture/evidence-blobs/sha256/${hexadecimal.slice(0, 2)}/${hexadecimal.slice(2)}`;
}

function decodeBase64Strict(value) {
  if (typeof value !== "string" || value.length === 0 || value.length % 4 !== 0) return null;
  if (!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)) return null;
  const decoded = Buffer.from(value, "base64");
  if (decoded.toString("base64") !== value) return null;
  return decoded;
}

function decodeUtf8Strict(bytes, label) {
  try {
    const text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(bytes);
    refuse(text.charCodeAt(0) !== 0xfeff, `${label}: UTF-8 BOM is not admitted`);
    return text;
  } catch (error) {
    if (error instanceof InputRefusal) throw error;
    throw new InputRefusal(`${label}: malformed UTF-8`);
  }
}

function validStrictJsonBytes(bytes) {
  try {
    parseStrictJsonText(decodeUtf8Strict(bytes, "embedded JSON"), "embedded JSON");
    return true;
  } catch (error) {
    if (error instanceof InputRefusal) return false;
    throw error;
  }
}

function compareDeterministicCborKeys(left, right) {
  if (left.length !== right.length) return left.length - right.length;
  return Buffer.compare(left, right);
}

function validDeterministicCbor(bytes) {
  let offset = 0;

  const take = (count) => {
    if (!Number.isSafeInteger(count) || count < 0 || offset + count > bytes.length) {
      throw new Error("truncated CBOR");
    }
    const start = offset;
    offset += count;
    return bytes.subarray(start, offset);
  };

  const argument = (additional) => {
    if (additional < 24) return BigInt(additional);
    if (additional === 24) {
      const value = BigInt(take(1).readUInt8(0));
      if (value < 24n) throw new Error("non-minimal CBOR integer");
      return value;
    }
    if (additional === 25) {
      const value = BigInt(take(2).readUInt16BE(0));
      if (value <= 0xffn) throw new Error("non-minimal CBOR integer");
      return value;
    }
    if (additional === 26) {
      const value = BigInt(take(4).readUInt32BE(0));
      if (value <= 0xffffn) throw new Error("non-minimal CBOR integer");
      return value;
    }
    if (additional === 27) {
      const value = take(8).readBigUInt64BE(0);
      if (value <= 0xffffffffn) throw new Error("non-minimal CBOR integer");
      return value;
    }
    throw new Error("indefinite or reserved CBOR argument");
  };

  const safeLength = (value) => {
    if (value > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error("oversized CBOR length");
    return Number(value);
  };

  const item = (depth = 0) => {
    if (depth > 256) throw new Error("CBOR nesting limit exceeded");
    const start = offset;
    const head = take(1).readUInt8(0);
    const major = head >> 5;
    const additional = head & 0x1f;
    if (major === 0 || major === 1) {
      argument(additional);
    } else if (major === 2 || major === 3) {
      const payload = take(safeLength(argument(additional)));
      if (major === 3) decodeUtf8Strict(payload, "embedded CBOR text");
    } else if (major === 4) {
      const count = safeLength(argument(additional));
      for (let index = 0; index < count; index += 1) item(depth + 1);
    } else if (major === 5) {
      const count = safeLength(argument(additional));
      let previousKey = null;
      for (let index = 0; index < count; index += 1) {
        const keyStart = offset;
        item(depth + 1);
        const encodedKey = bytes.subarray(keyStart, offset);
        if (previousKey !== null && compareDeterministicCborKeys(previousKey, encodedKey) >= 0) {
          throw new Error("CBOR map keys are not uniquely sorted");
        }
        previousKey = encodedKey;
        item(depth + 1);
      }
    } else if (major === 6) {
      argument(additional);
      item(depth + 1);
    } else if (major === 7) {
      if (additional <= 23) {
        if (additional < 20) throw new Error("unassigned CBOR simple value");
      } else if (additional === 24) {
        const simple = take(1).readUInt8(0);
        if (simple < 32) throw new Error("non-minimal CBOR simple value");
      } else if (additional === 25) {
        const word = take(2).readUInt16BE(0);
        const exponent = (word >> 10) & 0x1f;
        const fraction = word & 0x3ff;
        if (exponent === 0x1f) throw new Error("non-finite CBOR float");
        void fraction;
      } else if (additional === 26) {
        const value = take(4).readFloatBE(0);
        if (!Number.isFinite(value)) throw new Error("non-finite CBOR float");
      } else if (additional === 27) {
        const value = take(8).readDoubleBE(0);
        if (!Number.isFinite(value)) throw new Error("non-finite CBOR float");
      } else {
        throw new Error("break or reserved CBOR simple value");
      }
    } else {
      throw new Error("unknown CBOR major type");
    }
    return bytes.subarray(start, offset);
  };

  try {
    item();
    return offset === bytes.length;
  } catch {
    return false;
  }
}

function parseConfirmationReceiptFrame(bytes, frameProfile) {
  const magic = Buffer.from(frameProfile.magic_ascii, "ascii");
  let offset = 0;
  const take = (count) => {
    if (!Number.isSafeInteger(count) || count < 0 || offset + count > bytes.length) {
      throw new Error("truncated frame");
    }
    const start = offset;
    offset += count;
    return bytes.subarray(start, offset);
  };
  try {
    if (!take(magic.length).equals(magic)) return null;
    const fieldCount = take(2).readUInt16BE(0);
    if (fieldCount !== frameProfile.ordered_fields.length) return null;
    const values = Object.create(null);
    for (let fieldIndex = 0; fieldIndex < fieldCount; fieldIndex += 1) {
      const nameLength = take(2).readUInt16BE(0);
      const nameBytes = take(nameLength);
      if ([...nameBytes].some((byte) => byte > 0x7f)) return null;
      const name = nameBytes.toString("ascii");
      if (name !== frameProfile.ordered_fields[fieldIndex]) return null;
      const valueLength = take(4).readUInt32BE(0);
      values[name] = take(valueLength);
    }
    if (offset !== bytes.length) return null;
    if (values.presentation_challenge_id.length !== 32) return null;
    if (values.displayed_bytes_sha256.length !== 32) return null;
    if (values.displayed_byte_count.length !== 4) return null;
    const displayedByteCount = values.displayed_byte_count.readUInt32BE(0);
    if ([...values.rendering_profile_id, ...values.confirmation_gesture_kind, ...values.confirmation_gesture_at].some((byte) => byte > 0x7f)) return null;
    const renderingProfileId = values.rendering_profile_id.toString("ascii");
    const gestureKind = values.confirmation_gesture_kind.toString("ascii");
    const gestureAt = values.confirmation_gesture_at.toString("ascii");
    if (renderingProfileId.length === 0 || gestureKind.length === 0 || gestureAt.length === 0) return null;
    if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$/.test(gestureAt)) return null;
    return {
      presentationChallengeId: `sha256:${values.presentation_challenge_id.toString("hex")}`,
      displayedBytesSha256: `sha256:${values.displayed_bytes_sha256.toString("hex")}`,
      displayedByteCount,
      renderingProfileId,
      gestureKind,
      gestureAt,
    };
  } catch {
    return null;
  }
}

function domainCode(ruleset, kind, domain) {
  return ruleset.reason_code_contract.dynamic_domain_code_templates[kind].replace("{domain_id}", domain);
}

function backingCode(ruleset, kind, role) {
  return ruleset.reason_code_contract.dynamic_backing_code_templates[kind].replace("{role}", role);
}

function categoricalCode(ruleset, kind, conditionId) {
  return ruleset.reason_code_contract.categorical_projection_code_templates[kind].replace("{condition_id}", conditionId);
}

function foldObservationStatuses(ruleset, domain, statuses, count, requiredSourceMissing = false) {
  const contradicted = statuses.includes("contradicted");
  const unknown = statuses.includes("unknown");
  const notApplicable = statuses.includes("not_applicable");
  const missing = statuses.length === 0 || requiredSourceMissing;
  let foldedStatus;
  let reasonKind;
  if (contradicted) {
    foldedStatus = "contradicted";
    reasonKind = "contradicted";
  } else if (missing) {
    foldedStatus = "unknown";
    reasonKind = "missing";
  } else if (unknown) {
    foldedStatus = "unknown";
    reasonKind = "unknown";
  } else if (notApplicable) {
    foldedStatus = "not_applicable";
    reasonKind = "not_applicable";
  } else {
    foldedStatus = "supported";
    reasonKind = "supported";
  }
  return {
    domain,
    input_observation_count: count,
    folded_status: foldedStatus,
    reason_codes: [domainCode(ruleset, reasonKind, domain)],
  };
}

function withInvalidDomainFindings(projection, invalidReasons) {
  if (invalidReasons.length === 0) return projection;
  return {
    domain: projection.domain,
    input_observation_count: projection.input_observation_count,
    folded_status: "contradicted",
    reason_codes: sortedUnique(invalidReasons),
  };
}

function expectedVerificationRow(descriptor, outcome) {
  return {
    role: descriptor.role,
    artifact_id: descriptor.artifact_id,
    expected_content_address: descriptor.content_address,
    expected_byte_count: descriptor.byte_count,
    expected_media_type: descriptor.media_type,
    expected_byte_fidelity: descriptor.byte_fidelity,
    repository_blob_path: descriptor.repository_blob_path,
    read_disposition: outcome.readDisposition,
    observed_raw_sha256: outcome.observedDigest,
    observed_byte_count: outcome.observedByteCount,
    format_disposition: outcome.formatDisposition,
    comparison_disposition: outcome.comparisonDisposition,
    integrity_observation: outcome.integrityObservation,
  };
}

function roleFormatIsValid(role, bytes, resolver) {
  if (role === "exact_unmodified_confirmation_receipt_frame") {
    return parseConfirmationReceiptFrame(bytes, resolver.format_checks.confirmation_receipt_frame_role) !== null;
  }
  if (role === "exact_unmodified_credential_public_key") return validDeterministicCbor(bytes);
  const roleProfile = resolver.closed_role_inventory.find((entry) => entry.role === role);
  if (roleProfile?.required_media_type === "application/json") return validStrictJsonBytes(bytes);
  return true;
}

function verifyBackingBytes(input, resolver, ruleset) {
  const artifacts = input.backing_byte_inputs.artifacts;
  const expectedRoles = resolver.closed_role_inventory.map((entry) => entry.role);
  const actualRoles = artifacts.map((artifact) => artifact.descriptor.role);
  const reasons = [];
  const roleStates = new Map();
  const rowCount = artifacts.filter((artifact) => HAS_OWN(artifact, "verification_row")).length;
  const expectedRoleSet = new Set(expectedRoles);
  const artifactIdSet = new Set();

  if (!jsonEqual(actualRoles, expectedRoles) || new Set(actualRoles).size !== actualRoles.length) {
    return {
      domain: "backing_byte_integrity",
      input_observation_count: rowCount,
      folded_status: "contradicted",
      reason_codes: ["invalid.backing_byte.closed_role_inventory_mismatch"],
    };
  }
  for (const artifact of artifacts) {
    if (artifactIdSet.has(artifact.descriptor.artifact_id)) {
      reasons.push(backingCode(ruleset, "mismatch", artifact.descriptor.role));
    }
    artifactIdSet.add(artifact.descriptor.artifact_id);
  }

  for (const artifact of artifacts) {
    const descriptor = artifact.descriptor;
    const role = descriptor.role;
    if (!expectedRoleSet.has(role)) continue;
    const roleProfile = resolver.closed_role_inventory.find((entry) => entry.role === role);
    const derivedPath = derivedRepositoryPath(descriptor.content_address);
    const descriptorGood =
      typeof descriptor.artifact_id === "string" && descriptor.artifact_id.length > 0 &&
      SHA256_PATTERN.test(descriptor.content_address) &&
      Number.isSafeInteger(descriptor.byte_count) && descriptor.byte_count > 0 &&
      descriptor.media_type === roleProfile.required_media_type &&
      descriptor.byte_fidelity === roleProfile.required_byte_fidelity &&
      derivedPath !== null && descriptor.repository_blob_path === derivedPath;

    const hasEncodedPreimage =
      HAS_OWN(artifact, "preimage") && HAS_OWN(artifact.preimage, "raw_base64");
    if (!hasEncodedPreimage) {
      reasons.push(backingCode(ruleset, "missing", role));
      const outcome = {
        readDisposition: "missing",
        observedDigest: null,
        observedByteCount: null,
        formatDisposition: "not_evaluated_no_read",
        comparisonDisposition: "not_compared_no_read",
        integrityObservation: "unknown",
      };
      if (!HAS_OWN(artifact, "verification_row")) {
        reasons.push("invalid.backing_byte.failed_row_omitted");
      } else if (!jsonEqual(artifact.verification_row, expectedVerificationRow(descriptor, outcome))) {
        const row = artifact.verification_row;
        if (row.read_disposition === "readable_complete" && row.comparison_disposition === "match") {
          if (row.observed_byte_count === 0) {
            reasons.push("invalid.backing_byte.missing_recorded_as_zero_byte_match");
          } else {
            reasons.push("invalid.backing_byte.missing_recorded_as_readable_match");
          }
        } else {
          reasons.push(backingCode(ruleset, "mismatch", role));
        }
      }
      if (!descriptorGood) reasons.push(backingCode(ruleset, "mismatch", role));
      if (!roleStates.has(role)) roleStates.set(role, { kind: "missing", descriptor, bytes: null, frame: null });
      continue;
    }

    const bytes = decodeBase64Strict(artifact.preimage.raw_base64);
    if (bytes === null) {
      reasons.push(backingCode(ruleset, "unreadable", role));
      const outcome = {
        readDisposition: "unreadable",
        observedDigest: null,
        observedByteCount: null,
        formatDisposition: "not_evaluated_no_read",
        comparisonDisposition: "not_compared_no_read",
        integrityObservation: "unknown",
      };
      if (!HAS_OWN(artifact, "verification_row")) {
        reasons.push("invalid.backing_byte.failed_row_omitted");
      } else if (!jsonEqual(artifact.verification_row, expectedVerificationRow(descriptor, outcome))) {
        reasons.push(backingCode(ruleset, "mismatch", role));
      }
      if (!roleStates.has(role)) roleStates.set(role, { kind: "unreadable", descriptor, bytes: null, frame: null });
      continue;
    }

    const observedDigest = sha256Address(bytes);
    const formatGood = roleFormatIsValid(role, bytes, resolver);
    const preimagePathGood = artifact.preimage.repository_blob_path === derivedPath;
    const byteIdentityGood =
      observedDigest === descriptor.content_address && bytes.length === descriptor.byte_count;
    const comparisonGood = descriptorGood && preimagePathGood && byteIdentityGood && formatGood;
    const outcome = {
      readDisposition: "readable_complete",
      observedDigest,
      observedByteCount: bytes.length,
      formatDisposition: formatGood ? "conformant" : "malformed",
      comparisonDisposition: comparisonGood ? "match" : "mismatch",
      integrityObservation: comparisonGood ? "supported" : "contradicted",
    };
    if (!formatGood) reasons.push(backingCode(ruleset, "malformed", role));
    if (!comparisonGood) reasons.push(backingCode(ruleset, "mismatch", role));
    if (!HAS_OWN(artifact, "verification_row")) {
      reasons.push("invalid.backing_byte.failed_row_omitted");
    } else if (!jsonEqual(artifact.verification_row, expectedVerificationRow(descriptor, outcome))) {
      reasons.push(backingCode(ruleset, "mismatch", role));
    }
    if (!roleStates.has(role)) {
      roleStates.set(role, {
        kind: comparisonGood ? "match" : "mismatch",
        descriptor,
        bytes,
        frame: role === "exact_unmodified_confirmation_receipt_frame"
          ? parseConfirmationReceiptFrame(bytes, resolver.format_checks.confirmation_receipt_frame_role)
          : null,
        observedDigest,
      });
    }
  }

  const relation = input.backing_byte_inputs.confirmation_receipt_frame_relation;
  const frameState = roleStates.get("exact_unmodified_confirmation_receipt_frame");
  const displayedState = roleStates.get("exact_unmodified_displayed_decision_bytes");
  let relationGood =
    frameState?.bytes !== null && frameState?.frame !== null &&
    displayedState?.bytes !== null &&
    relation.frame_role === "exact_unmodified_confirmation_receipt_frame" &&
    SHA256_PATTERN.test(relation.authentication_challenge_id) &&
    relation.expected_frame_content_address === frameState?.descriptor.content_address &&
    relation.observed_frame_raw_sha256 === frameState?.observedDigest &&
    relation.authentication_frame_committed_receipt_sha256 === frameState?.observedDigest &&
    relation.binary_framing_disposition === "supported" &&
    relation.presentation_to_receipt_relation_disposition === "supported" &&
    relation.receipt_to_authentication_relation_disposition === "supported";
  if (relationGood) {
    relationGood =
      frameState.frame.presentationChallengeId === relation.presentation_challenge_id &&
      frameState.frame.displayedBytesSha256 === displayedState.observedDigest &&
      frameState.frame.displayedBytesSha256 === displayedState.descriptor.content_address &&
      frameState.frame.displayedByteCount === displayedState.bytes.length &&
      frameState.frame.displayedByteCount === displayedState.descriptor.byte_count;
  }
  if (!relationGood) reasons.push("invalid.backing_byte.confirmation_receipt_relation_mismatch");

  const negativeReasons = sortedUnique(reasons);
  let foldedStatus = "supported";
  if (negativeReasons.some((code) => code.startsWith("invalid."))) foldedStatus = "contradicted";
  else if (negativeReasons.length > 0) foldedStatus = "unknown";
  return {
    domain: "backing_byte_integrity",
    input_observation_count: rowCount,
    folded_status: foldedStatus,
    reason_codes: foldedStatus === "supported"
      ? [domainCode(ruleset, "supported", "backing_byte_integrity")]
      : negativeReasons,
  };
}

function genericCategoricalProjection(ruleset, conditionId, value, satisfied) {
  let status;
  if (value === undefined || value === null || value === "unknown") status = "unknown";
  else if (value === "not_applicable") status = "not_applicable";
  else status = satisfied(value) ? "satisfied" : "failed";
  return {
    condition_id: conditionId,
    status,
    reason_codes: [categoricalCode(ruleset, status, conditionId)],
  };
}

function atomicBackingAvailability(input) {
  const requiredRole = "sanitized_challenge_lifecycle_and_atomic_consumption_record";
  const artifact = input.backing_byte_inputs.artifacts.find(
    (candidate) => candidate.descriptor.role === requiredRole,
  );
  if (artifact === undefined || !HAS_OWN(artifact, "preimage") || !HAS_OWN(artifact.preimage, "raw_base64")) {
    return "missing";
  }
  return decodeBase64Strict(artifact.preimage.raw_base64) === null ? "unreadable" : "available";
}

function atomicActionProjection(ruleset, categorical, input) {
  const conditionId = "assertion_acceptance_and_consumption_atomic_action_equal";
  const invalidReasons = [];
  const indeterminateReasons = [];
  let sawUnknown = false;
  let sawNotApplicable = false;

  const identifier = (field, missingCode, malformedCode) => {
    if (!HAS_OWN(categorical, field) || categorical[field] === null || categorical[field] === "unknown") {
      sawUnknown = true;
      indeterminateReasons.push(missingCode);
      return null;
    }
    if (categorical[field] === "not_applicable") {
      sawNotApplicable = true;
      indeterminateReasons.push(missingCode);
      return null;
    }
    if (typeof categorical[field] !== "string" || !IDENTIFIER_PATTERN.test(categorical[field])) {
      invalidReasons.push(malformedCode);
      return null;
    }
    return categorical[field];
  };

  const acceptance = identifier(
    "assertion_acceptance_atomic_action_id",
    "indeterminate.atomic_action.acceptance_id_missing",
    "invalid.atomic_action.acceptance_id_malformed",
  );
  const consumption = identifier(
    "consumption_atomic_action_id",
    "indeterminate.atomic_action.consumption_id_missing",
    "invalid.atomic_action.consumption_id_malformed",
  );
  if (acceptance !== null && consumption !== null && acceptance !== consumption) {
    invalidReasons.push("invalid.atomic_action.identifiers_unequal");
  }

  const requiredRole = "sanitized_challenge_lifecycle_and_atomic_consumption_record";
  if (!HAS_OWN(categorical, "atomic_action_record_role") || categorical.atomic_action_record_role === null || categorical.atomic_action_record_role === "unknown") {
    sawUnknown = true;
    indeterminateReasons.push("indeterminate.atomic_action.backing_record_missing");
  } else if (categorical.atomic_action_record_role === "not_applicable") {
    sawNotApplicable = true;
    indeterminateReasons.push("indeterminate.atomic_action.backing_record_missing");
  } else if (categorical.atomic_action_record_role !== requiredRole) {
    invalidReasons.push("invalid.atomic_action.backing_record_malformed");
  }

  const backingAvailability = atomicBackingAvailability(input);
  if (!HAS_OWN(categorical, "atomic_action_record_observation") || categorical.atomic_action_record_observation === null) {
    sawUnknown = true;
    indeterminateReasons.push("indeterminate.atomic_action.backing_record_missing");
  } else if (categorical.atomic_action_record_observation === "unknown") {
    sawUnknown = true;
    indeterminateReasons.push(
      backingAvailability === "missing"
        ? "indeterminate.atomic_action.backing_record_missing"
        : "indeterminate.atomic_action.backing_record_unreadable",
    );
  } else if (categorical.atomic_action_record_observation === "not_applicable") {
    sawNotApplicable = true;
    indeterminateReasons.push(
      backingAvailability === "missing"
        ? "indeterminate.atomic_action.backing_record_missing"
        : "indeterminate.atomic_action.backing_record_unreadable",
    );
  } else if (categorical.atomic_action_record_observation === "contradicted") {
    invalidReasons.push("invalid.atomic_action.backing_record_contradicted");
  } else if (categorical.atomic_action_record_observation !== "supported") {
    invalidReasons.push("invalid.atomic_action.backing_record_malformed");
  }

  let status = "satisfied";
  if (invalidReasons.length > 0) status = "failed";
  else if (sawUnknown) status = "unknown";
  else if (sawNotApplicable) status = "not_applicable";
  const reasons = status === "satisfied"
    ? [categoricalCode(ruleset, "satisfied", conditionId)]
    : sortedUnique([...invalidReasons, ...indeterminateReasons]);
  return { condition_id: conditionId, status, reason_codes: reasons };
}

function categoricalProjections(input, ruleset) {
  const categorical = input.participant_input.categorical_inputs;
  const principalId = input.participant_input.principal_id;
  const projections = [
    genericCategoricalProjection(
      ruleset,
      "challenge_consumption_state_fresh_consumed_once",
      categorical.challenge_consumption_state,
      (value) => value === "fresh_consumed_once",
    ),
    genericCategoricalProjection(
      ruleset,
      "challenge_not_previously_consumed",
      categorical.prior_consumption_count,
      (value) => Number.isSafeInteger(value) && value === 0,
    ),
    genericCategoricalProjection(
      ruleset,
      "challenge_consumed_exactly_once",
      categorical.result_consumption_count,
      (value) => Number.isSafeInteger(value) && value === 1,
    ),
    atomicActionProjection(ruleset, categorical, input),
    genericCategoricalProjection(
      ruleset,
      "decision_confirmation_principal_matches_observation",
      categorical.decision_confirmation_principal_id,
      (value) => typeof value === "string" && value === principalId,
    ),
    genericCategoricalProjection(
      ruleset,
      "decision_confirmation_human_initiated",
      categorical.decision_confirmation_initiator_class,
      (value) => value === "human_initiated",
    ),
    genericCategoricalProjection(
      ruleset,
      "decision_confirmation_separate_from_authenticator_gesture",
      categorical.decision_confirmation_separate_from_authenticator_gesture,
      (value) => value === true,
    ),
    genericCategoricalProjection(
      ruleset,
      "same_origin_candidate_context_supported",
      categorical.cross_origin_disposition,
      (value) => value === "same_origin_supported",
    ),
    genericCategoricalProjection(
      ruleset,
      "no_authenticator_clone_risk_signal",
      categorical.signature_counter_disposition,
      (value) => value === "observed_no_clone_conclusion",
    ),
    genericCategoricalProjection(
      ruleset,
      "no_shared_effective_control_principals",
      categorical.shared_effective_control_principal_ids,
      (value) => Array.isArray(value) && value.length === 0,
    ),
    genericCategoricalProjection(
      ruleset,
      "verifier_distinct_principal_and_effective_control",
      categorical.verifier_relation_to_decision_principal,
      (value) => value === "distinct_principal_and_effective_control",
    ),
  ];
  exactArray(projections.map((projection) => projection.condition_id), CATEGORICAL_ORDER, "internal categorical projection order");
  return projections;
}

function publicSequenceInventory(input) {
  const sequences = input.participant_input.domain_observation_sequences;
  const firstByDomain = new Map();
  for (const sequence of sequences) {
    if (!firstByDomain.has(sequence.domain)) firstByDomain.set(sequence.domain, sequence);
  }
  return { sequences, firstByDomain };
}

function exactBindingProjection(input, ruleset, resolver, shapeObservations) {
  const projection = foldObservationStatuses(
    ruleset,
    "exact_core_and_evidence_binding",
    [input.exact_core_and_evidence_binding_observation],
    1,
  );
  const invalidReasons = [];
  if (
    input.ruleset_input.ruleset_id !== ruleset.ruleset_id ||
    input.ruleset_input.ruleset_version !== ruleset.ruleset_version ||
    input.backing_byte_inputs.resolver_profile_id !== resolver.profile_id
  ) {
    invalidReasons.push("invalid.integrity.resource_identity_version_mismatch");
  }
  if (!jsonEqual(input.ruleset_input.required_domain_ids, DOMAIN_ORDER)) {
    invalidReasons.push("invalid.integrity.required_domain_inventory_mismatch");
  }
  const { sequences } = publicSequenceInventory(input);
  if (sequences.some((sequence) => sequence.public_eligibility_domain !== true)) {
    invalidReasons.push("invalid.integrity.undeclared_eligibility_domain");
  }
  if (
    sequences.some((sequence) => !PUBLIC_DOMAIN_ORDER.includes(sequence.domain)) ||
    shapeObservations.undeclaredParticipantKeys.length > 0
  ) {
    invalidReasons.push("invalid.integrity.undeclared_eligibility_domain");
  }
  const sanitation = input.forbidden_content_and_sanitation;
  if (
    sanitation.exact_cryptographic_input_transformation !== "not_transformed" ||
    sanitation.sanitation_authorizes_exact_input_transformation !== false ||
    sanitation.forbidden_content_present_disposition !== "invalid" ||
    sanitation.unknown_sanitation_disposition !== "indeterminate"
  ) {
    invalidReasons.push("invalid.integrity.undeclared_eligibility_domain");
  }
  return withInvalidDomainFindings(projection, invalidReasons);
}

function publicDomainProjection(input, ruleset, domain) {
  const { firstByDomain } = publicSequenceInventory(input);
  const sequence = firstByDomain.get(domain);
  if (sequence === undefined) return foldObservationStatuses(ruleset, domain, [], 0, true);
  return foldObservationStatuses(
    ruleset,
    domain,
    sequence.observations.map((observation) => observation.status),
    sequence.observations.length,
  );
}

function sanitationProjection(input, ruleset) {
  const { firstByDomain } = publicSequenceInventory(input);
  const publicSequence = firstByDomain.get("sanitation");
  const sanitation = input.forbidden_content_and_sanitation;
  const statuses = [];
  if (publicSequence !== undefined) statuses.push(...publicSequence.observations.map((observation) => observation.status));
  statuses.push(...sanitation.sanitization_verification_sequence.map((observation) => observation.status));
  const invalidReasons = [];
  for (const observation of sanitation.ordered_forbidden_content_observations) {
    if (observation.disposition === "present") invalidReasons.push("invalid.sanitation.forbidden_content");
    else if (observation.disposition === "unknown") statuses.push("unknown");
    else if (observation.disposition === "not_applicable") statuses.push("not_applicable");
  }
  if (statuses.includes("contradicted")) invalidReasons.push("invalid.sanitation.contradicted");
  const missingSource =
    publicSequence === undefined || publicSequence.observations.length === 0 ||
    sanitation.sanitization_verification_sequence.length === 0 ||
    sanitation.ordered_forbidden_content_observations.length === 0;
  const count =
    (publicSequence?.observations.length ?? 0) +
    sanitation.sanitization_verification_sequence.length +
    sanitation.ordered_forbidden_content_observations.length;
  return withInvalidDomainFindings(
    foldObservationStatuses(ruleset, "sanitation", statuses, count, missingSource),
    invalidReasons,
  );
}

function globalReasonSet(domainResults, categoricalResults, finalDisposition) {
  if (finalDisposition === "eligible") return ["eligible.all_required_inputs_supported"];
  const reasons = [];
  for (const domain of domainResults) {
    reasons.push(...domain.reason_codes.filter((code) => !code.startsWith("eligible.")));
  }
  for (const categorical of categoricalResults) {
    reasons.push(...categorical.reason_codes.filter((code) => !code.startsWith("eligible.")));
  }
  return sortedUnique(reasons);
}

export function evaluateEligibility(input, ruleset, resolver) {
  const shapeObservations = validateMaterializedInput(input);
  validateRuleset(ruleset);
  validateResolver(resolver);
  refuse(IDENTIFIER_PATTERN.test(input.participant_input.principal_id), "materialized input: malformed participant principal_id");

  const domainResults = [
    exactBindingProjection(input, ruleset, resolver, shapeObservations),
    verifyBackingBytes(input, resolver, ruleset),
    publicDomainProjection(input, ruleset, "challenge_and_replay"),
    publicDomainProjection(input, ruleset, "decision_confirmation"),
    publicDomainProjection(input, ruleset, "authentication"),
    publicDomainProjection(input, ruleset, "identity_and_authenticator_binding"),
    publicDomainProjection(input, ruleset, "custody"),
    publicDomainProjection(input, ruleset, "delegation_objections_conflicts"),
    publicDomainProjection(input, ruleset, "controlled_time"),
    publicDomainProjection(input, ruleset, "verifier_independence"),
    sanitationProjection(input, ruleset),
  ];
  exactArray(domainResults.map((result) => result.domain), DOMAIN_ORDER, "internal domain projection order");

  const categoricalResults = categoricalProjections(input, ruleset);
  const hasInvalid =
    domainResults.some((result) => result.folded_status === "contradicted") ||
    categoricalResults.some((result) => result.status === "failed");
  const hasIndeterminate =
    domainResults.some((result) => ["unknown", "not_applicable"].includes(result.folded_status)) ||
    categoricalResults.some((result) => ["unknown", "not_applicable"].includes(result.status));
  const finalDisposition = hasInvalid ? "invalid" : hasIndeterminate ? "indeterminate" : "eligible";
  const categoricalFailures = categoricalResults
    .filter((result) => result.status === "failed")
    .map((result) => result.condition_id)
    .sort((left, right) => Buffer.compare(Buffer.from(left, "utf8"), Buffer.from(right, "utf8")));
  const reasonCodes = globalReasonSet(domainResults, categoricalResults, finalDisposition);
  refuse(reasonCodes.length > 0, "internal error: empty global reason set");
  if (finalDisposition === "invalid") {
    refuse(reasonCodes.some((code) => code.startsWith("invalid.")), "internal error: invalid result without invalid reason");
  } else if (finalDisposition === "indeterminate") {
    refuse(reasonCodes.every((code) => code.startsWith("indeterminate.")), "internal error: indeterminate result has non-indeterminate reason");
  }
  return {
    participant_id: input.participant_input.principal_id,
    domain_results: domainResults,
    categorical_results: categoricalResults,
    categorical_failures: categoricalFailures,
    final_disposition: finalDisposition,
    reason_codes: reasonCodes,
  };
}
