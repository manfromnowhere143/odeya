package odeya.hda.java21;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.DateTimeException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Pattern;

/** Independent Java 21 recomputation of the HDA v0.2 eligibility projection. */
public final class HumanDecisionAssuranceEvaluator {
    private static final Pattern IDENTIFIER = Pattern.compile(
            "^[a-z][a-z0-9]*(?:[._:-][a-z0-9]+)+$");
    private static final Pattern CONTENT_ADDRESS = Pattern.compile("^sha256:[0-9a-f]{64}$");
    private static final Pattern BASE64 = Pattern.compile(
            "^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$");
    private static final Pattern MICROSECOND_UTC_TIMESTAMP = Pattern.compile(
            "^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])T"
                    + "(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]\\.[0-9]{6}Z$");

    private static final List<String> DOMAINS = List.of(
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
            "sanitation");
    private static final List<String> EVIDENCE_DOMAINS = DOMAINS.subList(2, DOMAINS.size());
    private static final List<String> CONDITIONS = List.of(
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
            "verifier_distinct_principal_and_effective_control");
    private static final List<String> CATEGORICAL_INPUTS = List.of(
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
            "verifier_relation_to_decision_principal");
    private static final List<String> FORBIDDEN_CLASSES = List.of(
            "raw_private_reasoning",
            "reusable_secret",
            "private_or_signing_key_material",
            "pin_or_biometric_sample",
            "unrestricted_prompt_or_model_output");
    private static final List<String> FRAME_FIELDS = List.of(
            "presentation_challenge_id",
            "displayed_bytes_sha256",
            "displayed_byte_count",
            "rendering_profile_id",
            "confirmation_gesture_kind",
            "confirmation_gesture_at");
    private static final byte[] FRAME_MAGIC =
            "ODEYA-HDA-CONFIRMATION-RECEIPT-V1".getBytes(StandardCharsets.US_ASCII);

    private HumanDecisionAssuranceEvaluator() {}

    public static void main(String[] arguments) {
        try {
            InputAdapter.AdaptedInput adapted = InputAdapter.load(arguments);
            Map<String, Object> result = evaluate(adapted);
            System.out.println(StrictJson.write(result));
        } catch (IllegalArgumentException | IOException exc) {
            System.err.println("hda-java-evaluator: refused: " + exc.getMessage());
            System.exit(2);
        }
    }

    private static Map<String, Object> evaluate(InputAdapter.AdaptedInput adapted) {
        Contract contract = validateContract(adapted.ruleset(), adapted.resolver());
        Map<String, Object> input = adapted.resolvedInput();
        InputAdapter.requireExactKeys(input, Set.of(
                "input_id", "ruleset_input", "exact_core_and_evidence_binding_observation",
                "participant_input", "forbidden_content_and_sanitation", "backing_byte_inputs"),
                "resolved evaluator input");

        TreeSet<String> globalFindings = new TreeSet<>();
        validateInputBindings(input, globalFindings);
        Map<String, Object> participant = InputAdapter.object(
                input.get("participant_input"), "participant input");
        String participantId = InputAdapter.string(participant.get("principal_id"), "participant id");
        requireIdentifier(participantId, "participant id");

        BackingEvaluation backing = backingProjection(input, contract, globalFindings);
        List<Object> observationResults = observationProjections(
                input, participant, contract, globalFindings);
        CategoricalEvaluation categorical = categoricalProjections(
                participant, participantId, contract, globalFindings);

        ArrayList<Object> domainResults = new ArrayList<>();
        domainResults.add(exactBindingProjection(input, contract, globalFindings));
        domainResults.add(backing.projection());
        domainResults.addAll(observationResults);
        boolean invalid = globalFindings.stream().anyMatch(code -> code.startsWith("invalid."));
        boolean indeterminate = globalFindings.stream()
                .anyMatch(code -> code.startsWith("indeterminate."));
        String finalDisposition = invalid ? "invalid" : indeterminate ? "indeterminate" : "eligible";
        List<String> globalReasons = finalDisposition.equals("eligible")
                ? List.of("eligible.all_required_inputs_supported")
                : List.copyOf(globalFindings);

        LinkedHashMap<String, Object> output = new LinkedHashMap<>();
        output.put("participant_id", participantId);
        output.put("domain_results", domainResults);
        output.put("categorical_results", categorical.projections());
        output.put("categorical_failures", categorical.failures());
        output.put("final_disposition", finalDisposition);
        output.put("reason_codes", globalReasons);
        return output;
    }

    private static Contract validateContract(
            Map<String, Object> ruleset, Map<String, Object> resolver) {
        InputAdapter.requireString(ruleset, "ruleset_id", InputAdapter.RULESET_ID);
        InputAdapter.requireString(ruleset, "ruleset_version", "0.2.0");
        List<String> domains = strings(ruleset.get("required_domains"), "required domains", true,
                item -> InputAdapter.string(
                        InputAdapter.object(item, "required domain").get("domain_id"), "domain id"));
        if (!domains.equals(DOMAINS)) {
            throw new IllegalArgumentException("ruleset required-domain order differs from contract");
        }
        if (!strings(ruleset.get("required_evidence_observation_sequence_order"),
                "evidence domain order").equals(EVIDENCE_DOMAINS)) {
            throw new IllegalArgumentException("ruleset evidence-domain order differs from contract");
        }
        if (!strings(ruleset.get("required_categorical_inputs"), "categorical inputs")
                .equals(CATEGORICAL_INPUTS)) {
            throw new IllegalArgumentException("ruleset categorical input inventory differs");
        }
        if (!strings(ruleset.get("required_categorical_conditions"), "categorical conditions")
                .equals(CONDITIONS)) {
            throw new IllegalArgumentException("ruleset categorical condition order differs");
        }
        Map<String, Object> backingFold = InputAdapter.object(
                ruleset.get("backing_byte_integrity_fold"), "backing integrity fold");
        InputAdapter.requireExactKeys(backingFold, Set.of(
                "inventory_must_equal_resolver_profile_closed_role_inventory",
                "inventory_validation_precedes_per_role_resolution", "invalid_inventory_result",
                "one_total_receipt_row_per_inventory_role", "duplicate_or_unexpected_role",
                "readable_match_and_well_formed", "missing_or_unreadable", "readable_mismatch",
                "readable_malformed", "successful_zero_byte_representation_of_missing_bytes",
                "missing_observation_is_never_zero", "receipt_frame_relation_mismatch"),
                "backing integrity fold");
        if (!Objects.equals(
                        backingFold.get("inventory_must_equal_resolver_profile_closed_role_inventory"),
                        Boolean.TRUE)
                || !Objects.equals(
                        backingFold.get("inventory_validation_precedes_per_role_resolution"),
                        Boolean.TRUE)
                || !Objects.equals(backingFold.get("one_total_receipt_row_per_inventory_role"),
                        Boolean.TRUE)
                || !Objects.equals(backingFold.get("missing_observation_is_never_zero"),
                        Boolean.TRUE)) {
            throw new IllegalArgumentException("backing inventory precedence differs from contract");
        }
        InputAdapter.requireString(backingFold, "invalid_inventory_result",
                "emit_only_invalid.backing_byte.closed_role_inventory_mismatch_for_the_backing_domain");
        Map<String, Object> countContract = InputAdapter.object(
                ruleset.get("domain_input_observation_count_contract"),
                "domain observation-count contract");
        InputAdapter.requireExactKeys(countContract, Set.of(
                "exact_core_and_evidence_binding", "backing_byte_integrity",
                "ordinary_public_domain", "sanitation", "missing_required_sequence",
                "fabricated_minimum_count_allowed"), "domain observation-count contract");
        InputAdapter.requireString(countContract, "exact_core_and_evidence_binding",
                "one_compound_binding_observation");
        InputAdapter.requireString(countContract, "backing_byte_integrity",
                "number_of_present_verification_rows_not_number_of_descriptors");
        InputAdapter.requireString(countContract, "ordinary_public_domain",
                "number_of_present_items_in_that_public_domain_observation_sequence");
        InputAdapter.requireString(countContract, "sanitation",
                "sum_of_public_sanitation_observations_sanitization_verification_observations_and_forbidden_content_observations");
        if (InputAdapter.integer(countContract.get("missing_required_sequence"),
                        "missing sequence count") != 0
                || !Objects.equals(countContract.get("fabricated_minimum_count_allowed"),
                        Boolean.FALSE)) {
            throw new IllegalArgumentException("domain observation-count values differ from contract");
        }

        Map<String, Object> reasons = InputAdapter.object(
                ruleset.get("reason_code_contract"), "reason code contract");
        Map<String, Object> domainTemplates = InputAdapter.object(
                reasons.get("dynamic_domain_code_templates"), "domain reason templates");
        requireTemplate(domainTemplates, "supported", "eligible.domain.{domain_id}.supported");
        requireTemplate(domainTemplates, "contradicted", "invalid.domain.{domain_id}.contradicted");
        requireTemplate(domainTemplates, "missing", "indeterminate.domain.{domain_id}.missing");
        requireTemplate(domainTemplates, "unknown", "indeterminate.domain.{domain_id}.unknown");
        requireTemplate(domainTemplates, "not_applicable",
                "indeterminate.domain.{domain_id}.not_applicable");
        Map<String, Object> backingTemplates = InputAdapter.object(
                reasons.get("dynamic_backing_code_templates"), "backing reason templates");
        requireTemplate(backingTemplates, "supported",
                "eligible.domain.backing_byte_integrity.supported");
        requireTemplate(backingTemplates, "missing", "indeterminate.backing_byte.{role}.missing");
        requireTemplate(backingTemplates, "unreadable",
                "indeterminate.backing_byte.{role}.unreadable");
        requireTemplate(backingTemplates, "mismatch", "invalid.backing_byte.{role}.mismatch");
        requireTemplate(backingTemplates, "malformed", "invalid.backing_byte.{role}.malformed");
        Map<String, Object> categoricalTemplates = InputAdapter.object(
                reasons.get("categorical_projection_code_templates"),
                "categorical reason templates");
        requireTemplate(categoricalTemplates, "satisfied",
                "eligible.categorical.{condition_id}.satisfied");
        requireTemplate(categoricalTemplates, "failed",
                "invalid.categorical.{condition_id}.failed");
        requireTemplate(categoricalTemplates, "unknown",
                "indeterminate.categorical.{condition_id}.unknown");
        requireTemplate(categoricalTemplates, "not_applicable",
                "indeterminate.categorical.{condition_id}.not_applicable");

        InputAdapter.requireString(resolver, "profile_id", InputAdapter.RESOLVER_ID);
        Map<String, Object> transport = InputAdapter.object(
                resolver.get("repository_bundle_transport"), "repository transport");
        InputAdapter.requireString(transport, "root", "architecture/evidence-blobs/sha256");
        InputAdapter.requireString(transport, "path_template",
                "architecture/evidence-blobs/sha256/{hex[0:2]}/{hex[2:64]}");
        List<Object> inventory = InputAdapter.array(
                resolver.get("closed_role_inventory"), "closed role inventory");
        ArrayList<RoleSpec> roles = new ArrayList<>();
        for (int index = 0; index < inventory.size(); index++) {
            Map<String, Object> row = InputAdapter.object(inventory.get(index), "role inventory row");
            InputAdapter.requireExactKeys(row, Set.of(
                    "ordinal", "role", "required_media_type", "required_byte_fidelity"),
                    "role inventory row");
            if (InputAdapter.integer(row.get("ordinal"), "role ordinal") != index + 1L) {
                throw new IllegalArgumentException("role inventory ordinal differs from position");
            }
            roles.add(new RoleSpec(
                    InputAdapter.string(row.get("role"), "role"),
                    InputAdapter.string(row.get("required_media_type"), "required media type"),
                    InputAdapter.string(row.get("required_byte_fidelity"), "required byte fidelity")));
        }
        if (!roles.equals(expectedRoles())) {
            throw new IllegalArgumentException("resolver role inventory differs from contract");
        }
        Map<String, Object> formatChecks = InputAdapter.object(
                resolver.get("format_checks"), "resolver format checks");
        Map<String, Object> frame = InputAdapter.object(
                formatChecks.get("confirmation_receipt_frame_role"), "frame format contract");
        InputAdapter.requireExactKeys(frame, Set.of(
                "magic_ascii", "field_count_encoding", "field_entry_encoding", "ordered_fields",
                "field_value_contracts",
                "exact_binary_preimage_required", "json_rendering_or_reencoding_allowed",
                "trailing_bytes_allowed"), "frame format contract");
        InputAdapter.requireString(frame, "magic_ascii",
                "ODEYA-HDA-CONFIRMATION-RECEIPT-V1");
        InputAdapter.requireString(frame, "field_count_encoding", "unsigned_16_bit_big_endian");
        InputAdapter.requireString(frame, "field_entry_encoding",
                "name_length_u16be_then_ascii_name_then_value_length_u32be_then_value");
        if (!strings(frame.get("ordered_fields"), "frame field order").equals(FRAME_FIELDS)) {
            throw new IllegalArgumentException("receipt-frame field order differs from contract");
        }
        Map<String, Object> fieldContracts = InputAdapter.object(
                frame.get("field_value_contracts"), "frame field-value contracts");
        InputAdapter.requireExactKeys(fieldContracts, Set.copyOf(FRAME_FIELDS),
                "frame field-value contracts");
        InputAdapter.requireString(fieldContracts, "presentation_challenge_id",
                "exactly_32_raw_octets");
        InputAdapter.requireString(fieldContracts, "displayed_bytes_sha256",
                "exactly_32_raw_octets");
        InputAdapter.requireString(fieldContracts, "displayed_byte_count",
                "exactly_4_octets_unsigned_32_bit_big_endian");
        InputAdapter.requireString(fieldContracts, "rendering_profile_id",
                "nonempty_strict_ascii");
        InputAdapter.requireString(fieldContracts, "confirmation_gesture_kind",
                "nonempty_strict_ascii");
        InputAdapter.requireString(fieldContracts, "confirmation_gesture_at",
                "strict_ascii_utc_timestamp_yyyy_mm_dd_t_hh_mm_ss_dot_six_fraction_digits_z");
        if (!Objects.equals(frame.get("exact_binary_preimage_required"), Boolean.TRUE)
                || !Objects.equals(frame.get("json_rendering_or_reencoding_allowed"), Boolean.FALSE)
                || !Objects.equals(frame.get("trailing_bytes_allowed"), Boolean.FALSE)) {
            throw new IllegalArgumentException("receipt-frame binary constraints differ from contract");
        }
        return new Contract(domainTemplates, backingTemplates, categoricalTemplates, roles);
    }

    private static List<RoleSpec> expectedRoles() {
        return List.of(
                new RoleSpec("sanitized_challenge_lifecycle_and_atomic_consumption_record",
                        "application/json", "sanitized_derived_observation_record"),
                new RoleSpec("exact_unmodified_client_data_json", "application/json",
                        "exact_unmodified_cryptographic_input"),
                new RoleSpec("exact_unmodified_authenticator_data", "application/octet-stream",
                        "exact_unmodified_cryptographic_input"),
                new RoleSpec("exact_unmodified_webauthn_signature", "application/octet-stream",
                        "exact_unmodified_cryptographic_input"),
                new RoleSpec("exact_unmodified_credential_public_key", "application/cbor",
                        "exact_unmodified_cryptographic_input"),
                new RoleSpec("exact_unmodified_displayed_decision_bytes", "application/octet-stream",
                        "exact_unmodified_cryptographic_input"),
                new RoleSpec("exact_unmodified_confirmation_receipt_frame", "application/octet-stream",
                        "exact_unmodified_binary_frame"),
                new RoleSpec(
                        "sanitized_exact_material_presentation_and_decision_confirmation_receipt",
                        "application/json", "sanitized_derived_observation_record"),
                new RoleSpec("sanitized_custody_observation", "application/json",
                        "sanitized_derived_observation_record"),
                new RoleSpec("sanitized_identity_proofing_profile", "application/json",
                        "sanitized_derived_observation_record"),
                new RoleSpec("sanitized_principal_authenticator_binding", "application/json",
                        "sanitized_derived_observation_record"),
                new RoleSpec("sanitized_controlled_time_observation", "application/json",
                        "sanitized_derived_observation_record"),
                new RoleSpec("sanitized_verifier_observation", "application/json",
                        "sanitized_derived_observation_record"),
                new RoleSpec("sanitized_delegation_effective_control_observation", "application/json",
                        "sanitized_derived_observation_record"));
    }

    private static void validateInputBindings(
            Map<String, Object> input, Set<String> globalFindings) {
        requireIdentifier(InputAdapter.string(input.get("input_id"), "input id"), "input id");
        Map<String, Object> binding = InputAdapter.object(
                input.get("ruleset_input"), "ruleset input");
        InputAdapter.requireExactKeys(binding,
                Set.of("ruleset_id", "ruleset_version", "required_domain_ids"), "ruleset input");
        if (!Objects.equals(binding.get("ruleset_id"), InputAdapter.RULESET_ID)
                || !Objects.equals(binding.get("ruleset_version"), "0.2.0")) {
            globalFindings.add("invalid.integrity.resource_identity_version_mismatch");
        }
        if (!strings(binding.get("required_domain_ids"), "input required domains").equals(DOMAINS)) {
            globalFindings.add("invalid.integrity.required_domain_inventory_mismatch");
        }
        Map<String, Object> backing = InputAdapter.object(
                input.get("backing_byte_inputs"), "backing byte inputs");
        Object resolverId = backing.get("resolver_profile_id");
        if (!Objects.equals(resolverId, InputAdapter.RESOLVER_ID)) {
            globalFindings.add("invalid.integrity.resource_identity_version_mismatch");
        }
    }

    private static Map<String, Object> exactBindingProjection(
            Map<String, Object> input, Contract contract, Set<String> globalFindings) {
        String status = InputAdapter.string(
                input.get("exact_core_and_evidence_binding_observation"),
                "exact binding observation");
        TreeSet<String> attachedIntegrityFindings = new TreeSet<>();
        for (String finding : globalFindings) {
            if (finding.startsWith("invalid.integrity.")) {
                attachedIntegrityFindings.add(finding);
            }
        }
        if (!attachedIntegrityFindings.isEmpty()) {
            requireObservationStatus(status);
            if (status.equals("contradicted")) {
                attachedIntegrityFindings.add(domainCode(
                        contract, "contradicted", "exact_core_and_evidence_binding"));
                globalFindings.add(domainCode(
                        contract, "contradicted", "exact_core_and_evidence_binding"));
            }
            return projection(
                    "exact_core_and_evidence_binding", 1, "contradicted",
                    List.copyOf(attachedIntegrityFindings));
        }
        return singleStatusProjection(
                "exact_core_and_evidence_binding", 1, List.of(status), contract,
                globalFindings);
    }

    private static List<Object> observationProjections(
            Map<String, Object> input,
            Map<String, Object> participant,
            Contract contract,
            Set<String> globalFindings) {
        Set<String> participantAllowed = new HashSet<>(
                Set.of("principal_id", "domain_observation_sequences", "categorical_inputs"));
        if (!participantAllowed.equals(participant.keySet())) {
            globalFindings.add("invalid.integrity.undeclared_eligibility_domain");
        }
        List<Object> sequences = InputAdapter.array(
                participant.get("domain_observation_sequences"), "domain observation sequences");
        LinkedHashMap<String, List<String>> byDomain = new LinkedHashMap<>();
        for (Object value : sequences) {
            Map<String, Object> sequence = InputAdapter.object(value, "domain observation sequence");
            InputAdapter.requireExactKeys(sequence,
                    Set.of("domain", "public_eligibility_domain", "observations"),
                    "domain observation sequence");
            String domain = InputAdapter.string(sequence.get("domain"), "domain");
            if (!EVIDENCE_DOMAINS.contains(domain) || byDomain.containsKey(domain)
                    || !InputAdapter.bool(sequence.get("public_eligibility_domain"),
                            "public eligibility domain")) {
                globalFindings.add("invalid.integrity.undeclared_eligibility_domain");
            }
            byDomain.putIfAbsent(domain,
                    observationStatuses(sequence.get("observations"), "domain observations"));
        }
        Map<String, Object> sanitation = InputAdapter.object(
                input.get("forbidden_content_and_sanitation"), "sanitation input");
        InputAdapter.requireExactKeys(sanitation, Set.of(
                "ordered_forbidden_content_observations", "sanitization_verification_sequence",
                "exact_cryptographic_input_transformation",
                "sanitation_authorizes_exact_input_transformation",
                "forbidden_content_present_disposition", "unknown_sanitation_disposition"),
                "sanitation input");

        ArrayList<Object> result = new ArrayList<>();
        for (String domain : EVIDENCE_DOMAINS) {
            List<String> statuses = byDomain.get(domain);
            if (domain.equals("sanitation")) {
                result.add(sanitationProjection(statuses, sanitation, contract, globalFindings));
            } else if (statuses == null) {
                result.add(missingDomainProjection(domain, contract, globalFindings));
            } else {
                result.add(singleStatusProjection(
                        domain, statuses.size(), statuses, contract, globalFindings));
            }
        }
        return result;
    }

    private static Map<String, Object> sanitationProjection(
            List<String> publicStatuses,
            Map<String, Object> sanitation,
            Contract contract,
            Set<String> globalFindings) {
        if (publicStatuses == null) {
            publicStatuses = List.of();
        }
        ArrayList<String> observationStatuses = new ArrayList<>(publicStatuses);
        observationStatuses.addAll(observationStatuses(
                sanitation.get("sanitization_verification_sequence"),
                "sanitization verification sequence"));
        List<Object> forbidden = InputAdapter.array(
                sanitation.get("ordered_forbidden_content_observations"),
                "forbidden content observations");
        ArrayList<String> classes = new ArrayList<>();
        boolean forbiddenPresent = false;
        boolean forbiddenUnknown = false;
        for (Object value : forbidden) {
            Map<String, Object> observation = InputAdapter.object(
                    value, "forbidden content observation");
            InputAdapter.requireExactKeys(observation,
                    Set.of("content_class", "disposition", "evidence_role_refs"),
                    "forbidden content observation");
            classes.add(InputAdapter.string(observation.get("content_class"), "content class"));
            strings(observation.get("evidence_role_refs"), "forbidden-content evidence refs");
            String disposition = InputAdapter.string(
                    observation.get("disposition"), "forbidden content disposition");
            switch (disposition) {
                case "absent" -> { }
                case "present" -> forbiddenPresent = true;
                case "unknown" -> forbiddenUnknown = true;
                default -> throw new IllegalArgumentException(
                        "unknown forbidden-content disposition: " + disposition);
            }
        }
        if (!classes.equals(FORBIDDEN_CLASSES)) {
            globalFindings.add("invalid.integrity.undeclared_eligibility_domain");
        }
        if (!Objects.equals(sanitation.get("exact_cryptographic_input_transformation"),
                "not_transformed")
                || !Objects.equals(sanitation.get("sanitation_authorizes_exact_input_transformation"),
                        Boolean.FALSE)
                || !Objects.equals(sanitation.get("forbidden_content_present_disposition"), "invalid")
                || !Objects.equals(sanitation.get("unknown_sanitation_disposition"),
                        "indeterminate")) {
            observationStatuses.add("contradicted");
        }
        TreeSet<String> reasons = new TreeSet<>();
        boolean contradicted = observationStatuses.contains("contradicted");
        boolean unknown = observationStatuses.contains("unknown") || forbiddenUnknown;
        boolean notApplicable = observationStatuses.contains("not_applicable");
        String folded;
        if (contradicted || forbiddenPresent) {
            folded = "contradicted";
            if (contradicted) {
                reasons.add("invalid.sanitation.contradicted");
            }
        } else if (unknown) {
            folded = "unknown";
            reasons.add(domainCode(contract, "unknown", "sanitation"));
        } else if (notApplicable) {
            folded = "not_applicable";
            reasons.add(domainCode(contract, "not_applicable", "sanitation"));
        } else {
            folded = "supported";
            reasons.add(domainCode(contract, "supported", "sanitation"));
        }
        if (forbiddenPresent) {
            reasons.add("invalid.sanitation.forbidden_content");
        }
        for (String reason : reasons) {
            if (!reason.startsWith("eligible.")) {
                globalFindings.add(reason);
            }
        }
        return projection(
                "sanitation", observationStatuses.size() + forbidden.size(), folded,
                List.copyOf(reasons));
    }

    private static List<String> observationStatuses(Object value, String label) {
        List<Object> observations = InputAdapter.array(value, label);
        ArrayList<String> statuses = new ArrayList<>();
        for (int index = 0; index < observations.size(); index++) {
            Map<String, Object> observation = InputAdapter.object(
                    observations.get(index), label + " row");
            InputAdapter.requireExactKeys(observation,
                    Set.of("sequence_index", "observation_id", "status", "evidence_role_refs"),
                    label + " row");
            if (InputAdapter.integer(observation.get("sequence_index"), "sequence index") != index) {
                throw new IllegalArgumentException(label + " sequence indexes are not contiguous");
            }
            requireIdentifier(InputAdapter.string(
                    observation.get("observation_id"), "observation id"), "observation id");
            strings(observation.get("evidence_role_refs"), "observation evidence refs");
            String status = InputAdapter.string(observation.get("status"), "observation status");
            requireObservationStatus(status);
            statuses.add(status);
        }
        return statuses;
    }

    private static Map<String, Object> missingDomainProjection(
            String domain, Contract contract, Set<String> globalFindings) {
        String reason = domainCode(contract, "missing", domain);
        globalFindings.add(reason);
        return projection(domain, 0, "unknown", List.of(reason));
    }

    private static Map<String, Object> singleStatusProjection(
            String domain,
            int inputCount,
            List<String> statuses,
            Contract contract,
            Set<String> globalFindings) {
        if (statuses.isEmpty()) {
            return missingDomainProjection(domain, contract, globalFindings);
        }
        boolean contradicted = false;
        boolean unknown = false;
        boolean notApplicable = false;
        for (String status : statuses) {
            requireObservationStatus(status);
            contradicted |= status.equals("contradicted");
            unknown |= status.equals("unknown");
            notApplicable |= status.equals("not_applicable");
        }
        TreeSet<String> reasons = new TreeSet<>();
        String folded;
        if (contradicted) {
            folded = "contradicted";
            reasons.add(domainCode(contract, "contradicted", domain));
        } else if (unknown) {
            folded = "unknown";
            reasons.add(domainCode(contract, "unknown", domain));
        } else if (notApplicable) {
            folded = "not_applicable";
            reasons.add(domainCode(contract, "not_applicable", domain));
        } else {
            folded = "supported";
            reasons.add(domainCode(contract, "supported", domain));
        }
        for (String reason : reasons) {
            if (!reason.startsWith("eligible.")) {
                globalFindings.add(reason);
            }
        }
        return projection(domain, inputCount, folded, List.copyOf(reasons));
    }

    private static BackingEvaluation backingProjection(
            Map<String, Object> input,
            Contract contract,
            Set<String> globalFindings) {
        Map<String, Object> backing = InputAdapter.object(
                input.get("backing_byte_inputs"), "backing byte inputs");
        InputAdapter.requireExactKeys(backing,
                Set.of("resolver_profile_id", "artifacts", "confirmation_receipt_frame_relation"),
                "backing byte inputs");
        List<Object> artifacts = InputAdapter.array(backing.get("artifacts"), "backing artifacts");
        ArrayList<String> actualRoles = new ArrayList<>();
        HashMap<String, List<Map<String, Object>>> byRole = new HashMap<>();
        int presentRows = 0;
        for (Object value : artifacts) {
            Map<String, Object> artifact = InputAdapter.object(value, "backing artifact");
            if (!artifact.keySet().stream().allMatch(
                    key -> Set.of("descriptor", "preimage", "verification_row").contains(key))
                    || !artifact.containsKey("descriptor")) {
                throw new IllegalArgumentException("backing artifact members are malformed");
            }
            Map<String, Object> descriptor = InputAdapter.object(
                    artifact.get("descriptor"), "backing descriptor");
            String role = InputAdapter.string(descriptor.get("role"), "descriptor role");
            actualRoles.add(role);
            byRole.computeIfAbsent(role, ignored -> new ArrayList<>()).add(artifact);
            if (artifact.containsKey("verification_row")) {
                presentRows++;
            }
        }
        List<String> expectedRoleNames = contract.roles().stream().map(RoleSpec::role).toList();
        TreeSet<String> findings = new TreeSet<>();
        if (!actualRoles.equals(expectedRoleNames)) {
            String finding = "invalid.backing_byte.closed_role_inventory_mismatch";
            globalFindings.add(finding);
            return new BackingEvaluation(
                    projection(
                            "backing_byte_integrity", presentRows, "contradicted",
                            List.of(finding)),
                    Map.of());
        }

        HashMap<String, byte[]> readable = new HashMap<>();
        HashMap<String, String> observedAddresses = new HashMap<>();
        for (RoleSpec role : contract.roles()) {
            List<Map<String, Object>> matches = byRole.getOrDefault(role.role(), List.of());
            if (matches.isEmpty()) {
                findings.add(backingCode(contract, "missing", role.role()));
                continue;
            }
            verifyArtifact(matches.get(0), role, contract, findings, readable, observedAddresses);
        }
        verifyFrameRelation(backing, contract, findings, readable, observedAddresses);

        boolean invalid = findings.stream().anyMatch(code -> code.startsWith("invalid."));
        boolean indeterminate = findings.stream().anyMatch(code -> code.startsWith("indeterminate."));
        String folded = invalid ? "contradicted" : indeterminate ? "unknown" : "supported";
        List<String> projectionReasons;
        if (findings.isEmpty()) {
            projectionReasons = List.of(backingCode(contract, "supported", ""));
        } else {
            projectionReasons = List.copyOf(findings);
            globalFindings.addAll(findings);
        }
        return new BackingEvaluation(
                projection("backing_byte_integrity", presentRows, folded, projectionReasons), readable);
    }

    private static void verifyArtifact(
            Map<String, Object> artifact,
            RoleSpec role,
            Contract contract,
            Set<String> findings,
            Map<String, byte[]> readable,
            Map<String, String> observedAddresses) {
        Map<String, Object> descriptor = InputAdapter.object(
                artifact.get("descriptor"), "backing descriptor");
        InputAdapter.requireExactKeys(descriptor, Set.of(
                "artifact_id", "role", "content_address", "byte_count", "media_type",
                "byte_fidelity", "repository_blob_path", "synthetic_preimage",
                "sanitization_status"), "backing descriptor");
        String artifactId = InputAdapter.string(descriptor.get("artifact_id"), "artifact id");
        requireIdentifier(artifactId, "artifact id");
        String address = InputAdapter.string(descriptor.get("content_address"), "content address");
        long expectedCount = InputAdapter.integer(descriptor.get("byte_count"), "byte count");
        if (expectedCount <= 0) {
            throw new IllegalArgumentException("descriptor byte_count must be positive");
        }
        boolean descriptorMatches = CONTENT_ADDRESS.matcher(address).matches();
        String derivedPath = descriptorMatches ? pathFor(address) : "";
        descriptorMatches &= Objects.equals(descriptor.get("role"), role.role());
        descriptorMatches &= Objects.equals(descriptor.get("media_type"), role.mediaType());
        descriptorMatches &= Objects.equals(descriptor.get("byte_fidelity"), role.byteFidelity());
        descriptorMatches &= Objects.equals(descriptor.get("repository_blob_path"), derivedPath);
        if (!Objects.equals(descriptor.get("synthetic_preimage"), Boolean.TRUE)
                || !Objects.equals(descriptor.get("sanitization_status"), "supported")) {
            descriptorMatches = false;
        }

        Map<String, Object> preimage = null;
        if (artifact.containsKey("preimage")) {
            preimage = InputAdapter.object(artifact.get("preimage"), "backing preimage");
            if (!preimage.keySet().stream().allMatch(
                    key -> Set.of("repository_blob_path", "raw_base64").contains(key))
                    || !preimage.containsKey("repository_blob_path")) {
                throw new IllegalArgumentException("preimage members are malformed");
            }
        }

        byte[] bytes = null;
        if (preimage != null && preimage.containsKey("raw_base64")) {
            String encoded = InputAdapter.string(preimage.get("raw_base64"), "raw_base64");
            bytes = decodeBase64(encoded);
        }
        if (bytes == null) {
            findings.add(backingCode(contract, "missing", role.role()));
            validateMissingRow(artifact, descriptor, role, findings);
            return;
        }

        String observed = "sha256:" + sha256Hex(bytes);
        observedAddresses.put(role.role(), observed);
        readable.put(role.role(), bytes);
        boolean pathMatches = preimage != null
                && Objects.equals(preimage.get("repository_blob_path"), derivedPath);
        boolean contentMatches = descriptorMatches && pathMatches
                && address.equals(observed) && expectedCount == bytes.length;
        boolean formatMatches = formatConformant(role.role(), role.mediaType(), bytes);
        if (!contentMatches) {
            findings.add(backingCode(contract, "mismatch", role.role()));
        }
        if (!formatMatches) {
            findings.add(backingCode(contract, "malformed", role.role()));
        }
        validateReadableRow(
                artifact, descriptor, role, bytes, observed, contentMatches, formatMatches, findings);
    }

    private static void validateMissingRow(
            Map<String, Object> artifact,
            Map<String, Object> descriptor,
            RoleSpec role,
            Set<String> findings) {
        if (!artifact.containsKey("verification_row")) {
            findings.add("invalid.backing_byte.failed_row_omitted");
            return;
        }
        Map<String, Object> row = verificationRow(artifact.get("verification_row"));
        boolean claimsReadable = Objects.equals(row.get("read_disposition"), "readable_complete")
                || Objects.equals(row.get("comparison_disposition"), "match")
                || Objects.equals(row.get("integrity_observation"), "supported");
        if (claimsReadable) {
            Object observedCount = row.get("observed_byte_count");
            Object observedDigest = row.get("observed_raw_sha256");
            boolean zeroClaim = observedCount instanceof BigDecimal number
                    && number.compareTo(BigDecimal.ZERO) == 0
                    && Objects.equals(observedDigest,
                            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
            findings.add(zeroClaim
                    ? "invalid.backing_byte.missing_recorded_as_zero_byte_match"
                    : "invalid.backing_byte.missing_recorded_as_readable_match");
            return;
        }
        boolean correct = commonRowBindings(row, descriptor, role)
                && Objects.equals(row.get("read_disposition"), "missing")
                && row.get("observed_raw_sha256") == null
                && row.get("observed_byte_count") == null
                && Objects.equals(row.get("format_disposition"), "not_evaluated_no_read")
                && Objects.equals(row.get("comparison_disposition"), "not_compared_no_read")
                && Objects.equals(row.get("integrity_observation"), "unknown");
        if (!correct) {
            findings.add(backingCode(null, "mismatch", role.role()));
        }
    }

    private static void validateReadableRow(
            Map<String, Object> artifact,
            Map<String, Object> descriptor,
            RoleSpec role,
            byte[] bytes,
            String observed,
            boolean contentMatches,
            boolean formatMatches,
            Set<String> findings) {
        if (!artifact.containsKey("verification_row")) {
            findings.add("invalid.backing_byte.failed_row_omitted");
            return;
        }
        Map<String, Object> row = verificationRow(artifact.get("verification_row"));
        boolean match = contentMatches && formatMatches;
        boolean correct = commonRowBindings(row, descriptor, role)
                && Objects.equals(row.get("read_disposition"), "readable_complete")
                && Objects.equals(row.get("observed_raw_sha256"), observed)
                && integerEquals(row.get("observed_byte_count"), bytes.length)
                && Objects.equals(row.get("format_disposition"),
                        formatMatches ? "conformant" : "malformed")
                && Objects.equals(row.get("comparison_disposition"), match ? "match" : "mismatch")
                && Objects.equals(row.get("integrity_observation"),
                        match ? "supported" : "contradicted");
        if (!correct) {
            findings.add("invalid.backing_byte." + role.role() + ".mismatch");
        }
    }

    private static Map<String, Object> verificationRow(Object value) {
        Map<String, Object> row = InputAdapter.object(value, "verification row");
        InputAdapter.requireExactKeys(row, Set.of(
                "role", "artifact_id", "expected_content_address", "expected_byte_count",
                "expected_media_type", "expected_byte_fidelity", "repository_blob_path",
                "read_disposition", "observed_raw_sha256", "observed_byte_count",
                "format_disposition", "comparison_disposition", "integrity_observation"),
                "verification row");
        return row;
    }

    private static boolean commonRowBindings(
            Map<String, Object> row, Map<String, Object> descriptor, RoleSpec role) {
        return Objects.equals(row.get("role"), role.role())
                && Objects.equals(row.get("artifact_id"), descriptor.get("artifact_id"))
                && Objects.equals(row.get("expected_content_address"),
                        descriptor.get("content_address"))
                && Objects.equals(row.get("expected_byte_count"), descriptor.get("byte_count"))
                && Objects.equals(row.get("expected_media_type"), descriptor.get("media_type"))
                && Objects.equals(row.get("expected_byte_fidelity"),
                        descriptor.get("byte_fidelity"))
                && Objects.equals(row.get("repository_blob_path"),
                        descriptor.get("repository_blob_path"));
    }

    private static void verifyFrameRelation(
            Map<String, Object> backing,
            Contract contract,
            Set<String> findings,
            Map<String, byte[]> readable,
            Map<String, String> observedAddresses) {
        Map<String, Object> relation = InputAdapter.object(
                backing.get("confirmation_receipt_frame_relation"), "frame relation");
        InputAdapter.requireExactKeys(relation, Set.of(
                "frame_role", "expected_frame_content_address", "observed_frame_raw_sha256",
                "presentation_challenge_id", "authentication_challenge_id",
                "authentication_frame_committed_receipt_sha256", "binary_framing_disposition",
                "presentation_to_receipt_relation_disposition",
                "receipt_to_authentication_relation_disposition"), "frame relation");
        if (!Objects.equals(relation.get("frame_role"),
                "exact_unmodified_confirmation_receipt_frame")) {
            findings.add("invalid.backing_byte.confirmation_receipt_relation_mismatch");
        }
        byte[] frameBytes = readable.get("exact_unmodified_confirmation_receipt_frame");
        byte[] displayed = readable.get("exact_unmodified_displayed_decision_bytes");
        if (frameBytes == null) {
            return;
        }
        String frameAddress = observedAddresses.get("exact_unmodified_confirmation_receipt_frame");
        boolean relationMatches = Objects.equals(
                        relation.get("expected_frame_content_address"), frameAddress)
                && Objects.equals(relation.get("observed_frame_raw_sha256"), frameAddress)
                && Objects.equals(relation.get("authentication_frame_committed_receipt_sha256"),
                        frameAddress)
                && contentAddress(relation.get("presentation_challenge_id"))
                && contentAddress(relation.get("authentication_challenge_id"));
        ParsedFrame frame = null;
        try {
            frame = parseFrame(frameBytes);
        } catch (IllegalArgumentException exc) {
            relationMatches = false;
        }
        if (frame != null) {
            relationMatches &= Arrays.equals(
                    frame.fields().get("presentation_challenge_id"),
                    digestBytes((String) relation.get("presentation_challenge_id")));
            if (displayed == null) {
                relationMatches = false;
            } else {
                relationMatches &= Arrays.equals(
                        frame.fields().get("displayed_bytes_sha256"), sha256(displayed));
                relationMatches &= decodeUnsigned(frame.fields().get("displayed_byte_count"))
                        == displayed.length;
            }
        }
        relationMatches &= Objects.equals(relation.get("binary_framing_disposition"), "supported")
                && Objects.equals(relation.get("presentation_to_receipt_relation_disposition"),
                        "supported")
                && Objects.equals(relation.get("receipt_to_authentication_relation_disposition"),
                        "supported");
        if (!relationMatches) {
            findings.add("invalid.backing_byte.confirmation_receipt_relation_mismatch");
        }
    }

    private static CategoricalEvaluation categoricalProjections(
            Map<String, Object> participant,
            String participantId,
            Contract contract,
            Set<String> globalFindings) {
        Map<String, Object> inputs = InputAdapter.object(
                participant.get("categorical_inputs"), "categorical inputs");
        if (!inputs.keySet().equals(new HashSet<>(CATEGORICAL_INPUTS))) {
            globalFindings.add("invalid.integrity.undeclared_eligibility_domain");
        }
        ArrayList<Object> projections = new ArrayList<>();
        TreeSet<String> failures = new TreeSet<>();
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(0),
                valueStatus(inputs.get("challenge_consumption_state"), "fresh_consumed_once"));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(1),
                integerStatus(inputs.get("prior_consumption_count"), 0, "prior consumption count"));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(2),
                integerStatus(inputs.get("result_consumption_count"), 1, "result consumption count"));
        addAtomicCategorical(projections, failures, globalFindings, contract, inputs);
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(4),
                valueStatus(inputs.get("decision_confirmation_principal_id"), participantId));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(5),
                valueStatus(inputs.get("decision_confirmation_initiator_class"), "human_initiated"));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(6),
                booleanStatus(inputs.get("decision_confirmation_separate_from_authenticator_gesture")));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(7),
                valueStatus(inputs.get("cross_origin_disposition"), "same_origin_supported"));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(8),
                valueStatus(inputs.get("signature_counter_disposition"),
                        "observed_no_clone_conclusion"));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(9),
                emptyArrayStatus(inputs.get("shared_effective_control_principal_ids")));
        addSimpleCategorical(projections, failures, globalFindings, contract, CONDITIONS.get(10),
                valueStatus(inputs.get("verifier_relation_to_decision_principal"),
                        "distinct_principal_and_effective_control"));
        return new CategoricalEvaluation(projections, List.copyOf(failures));
    }

    private static void addAtomicCategorical(
            List<Object> projections,
            Set<String> failures,
            Set<String> globalFindings,
            Contract contract,
            Map<String, Object> inputs) {
        String condition = CONDITIONS.get(3);
        TreeSet<String> reasons = new TreeSet<>();
        String acceptance = nullableStringMember(
                inputs, "assertion_acceptance_atomic_action_id", "acceptance atomic action id");
        String consumption = nullableStringMember(
                inputs, "consumption_atomic_action_id", "consumption atomic action id");
        String status = "satisfied";
        if (acceptance == null) {
            status = "unknown";
            reasons.add("indeterminate.atomic_action.acceptance_id_missing");
        } else if (!IDENTIFIER.matcher(acceptance).matches()) {
            status = "failed";
            reasons.add("invalid.atomic_action.acceptance_id_malformed");
        }
        if (consumption == null) {
            if (!status.equals("failed")) {
                status = "unknown";
            }
            reasons.add("indeterminate.atomic_action.consumption_id_missing");
        } else if (!IDENTIFIER.matcher(consumption).matches()) {
            status = "failed";
            reasons.add("invalid.atomic_action.consumption_id_malformed");
        }
        if (acceptance != null && consumption != null
                && IDENTIFIER.matcher(acceptance).matches()
                && IDENTIFIER.matcher(consumption).matches()
                && !acceptance.equals(consumption)) {
            status = "failed";
            reasons.add("invalid.atomic_action.identifiers_unequal");
        }
        Object roleValue = inputs.get("atomic_action_record_role");
        if (roleValue == null) {
            if (!status.equals("failed")) {
                status = "unknown";
            }
            reasons.add("indeterminate.atomic_action.backing_record_missing");
        } else if (!(roleValue instanceof String role)
                || !role.equals("sanitized_challenge_lifecycle_and_atomic_consumption_record")) {
            status = "failed";
            reasons.add("invalid.atomic_action.backing_record_malformed");
        }
        Object observationValue = inputs.get("atomic_action_record_observation");
        if (observationValue == null) {
            if (!status.equals("failed")) {
                status = "unknown";
            }
            reasons.add("indeterminate.atomic_action.backing_record_missing");
        } else {
            String observation = InputAdapter.string(
                    observationValue, "atomic action record observation");
            requireObservationStatus(observation);
            if (observation.equals("contradicted")) {
                status = "failed";
                reasons.add("invalid.atomic_action.backing_record_contradicted");
            } else if (observation.equals("unknown") || observation.equals("not_applicable")) {
                if (!status.equals("failed")) {
                    status = "unknown";
                }
                reasons.add("indeterminate.atomic_action.backing_record_missing");
            }
        }
        if (status.equals("satisfied")) {
            reasons.add(categoricalCode(contract, "satisfied", condition));
        } else {
            globalFindings.addAll(reasons);
            if (status.equals("failed")) {
                failures.add(condition);
            }
        }
        projections.add(categoricalProjection(condition, status, List.copyOf(reasons)));
    }

    private static void addSimpleCategorical(
            List<Object> projections,
            Set<String> failures,
            Set<String> globalFindings,
            Contract contract,
            String condition,
            String status) {
        String reason = categoricalCode(contract, status, condition);
        projections.add(categoricalProjection(condition, status, List.of(reason)));
        if (!status.equals("satisfied")) {
            globalFindings.add(reason);
        }
        if (status.equals("failed")) {
            failures.add(condition);
        }
    }

    private static String valueStatus(Object value, Object satisfied) {
        if (value == null) {
            return "unknown";
        }
        if (!(value instanceof String)) {
            throw new IllegalArgumentException("categorical scalar must be a string or null");
        }
        return value.equals(satisfied) ? "satisfied" : "failed";
    }

    private static String integerStatus(Object value, long satisfied, String label) {
        if (value == null) {
            return "unknown";
        }
        long number = InputAdapter.integer(value, label);
        if (number < 0) {
            throw new IllegalArgumentException(label + " must be nonnegative");
        }
        return number == satisfied ? "satisfied" : "failed";
    }

    private static String booleanStatus(Object value) {
        if (value == null) {
            return "unknown";
        }
        return InputAdapter.bool(value, "categorical boolean") ? "satisfied" : "failed";
    }

    private static String emptyArrayStatus(Object value) {
        if (value == null) {
            return "unknown";
        }
        List<Object> principals = InputAdapter.array(value, "shared control principals");
        for (Object principal : principals) {
            requireIdentifier(InputAdapter.string(principal, "shared-control principal id"),
                    "shared-control principal id");
        }
        return principals.isEmpty() ? "satisfied" : "failed";
    }

    private static String nullableStringMember(
            Map<String, Object> object, String name, String label) {
        if (!object.containsKey(name) || object.get(name) == null) {
            return null;
        }
        Object value = object.get(name);
        if (!(value instanceof String string)) {
            return "\u0000INVALID_NON_STRING\u0000";
        }
        return string;
    }

    private static Map<String, Object> projection(
            String domain, int count, String status, List<String> reasons) {
        LinkedHashMap<String, Object> result = new LinkedHashMap<>();
        result.put("domain", domain);
        result.put("input_observation_count", count);
        result.put("folded_status", status);
        result.put("reason_codes", reasons);
        return result;
    }

    private static Map<String, Object> categoricalProjection(
            String condition, String status, List<String> reasons) {
        LinkedHashMap<String, Object> result = new LinkedHashMap<>();
        result.put("condition_id", condition);
        result.put("status", status);
        result.put("reason_codes", reasons);
        return result;
    }

    private static String domainCode(Contract contract, String status, String domain) {
        return InputAdapter.string(contract.domainTemplates().get(status), "domain code template")
                .replace("{domain_id}", domain);
    }

    private static String backingCode(Contract contract, String status, String role) {
        if (contract == null) {
            return "invalid.backing_byte." + role + ".mismatch";
        }
        return InputAdapter.string(contract.backingTemplates().get(status), "backing code template")
                .replace("{role}", role);
    }

    private static String categoricalCode(Contract contract, String status, String condition) {
        return InputAdapter.string(
                        contract.categoricalTemplates().get(status), "categorical code template")
                .replace("{condition_id}", condition);
    }

    private static boolean formatConformant(String role, String mediaType, byte[] bytes) {
        try {
            if (mediaType.equals("application/json")) {
                StrictJson.parse(bytes);
                return true;
            }
            if (mediaType.equals("application/cbor")) {
                new CborReader(bytes).readDocument();
                return true;
            }
            if (role.equals("exact_unmodified_confirmation_receipt_frame")) {
                parseFrame(bytes);
                return true;
            }
            return true;
        } catch (IllegalArgumentException exc) {
            return false;
        }
    }

    private static ParsedFrame parseFrame(byte[] bytes) {
        if (bytes.length < FRAME_MAGIC.length + 2) {
            throw new IllegalArgumentException("confirmation frame is truncated");
        }
        ByteBuffer input = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN);
        byte[] magic = new byte[FRAME_MAGIC.length];
        input.get(magic);
        if (!Arrays.equals(magic, FRAME_MAGIC)) {
            throw new IllegalArgumentException("confirmation frame magic differs");
        }
        int count = Short.toUnsignedInt(input.getShort());
        if (count != FRAME_FIELDS.size()) {
            throw new IllegalArgumentException("confirmation frame field count differs");
        }
        LinkedHashMap<String, byte[]> fields = new LinkedHashMap<>();
        for (String expectedName : FRAME_FIELDS) {
            if (input.remaining() < 2) {
                throw new IllegalArgumentException("confirmation frame name length is truncated");
            }
            int nameLength = Short.toUnsignedInt(input.getShort());
            if (nameLength == 0 || input.remaining() < nameLength + 4L) {
                throw new IllegalArgumentException("confirmation frame name is truncated");
            }
            byte[] nameBytes = new byte[nameLength];
            input.get(nameBytes);
            String name = strictAscii(nameBytes);
            if (!name.equals(expectedName)) {
                throw new IllegalArgumentException("confirmation frame field order differs");
            }
            long valueLength = Integer.toUnsignedLong(input.getInt());
            if (valueLength > input.remaining() || valueLength > Integer.MAX_VALUE) {
                throw new IllegalArgumentException("confirmation frame value is truncated");
            }
            byte[] value = new byte[(int) valueLength];
            input.get(value);
            fields.put(name, value);
        }
        if (input.hasRemaining()) {
            throw new IllegalArgumentException("confirmation frame has trailing bytes");
        }
        if (fields.get("presentation_challenge_id").length != 32
                || fields.get("displayed_bytes_sha256").length != 32
                || fields.get("displayed_byte_count").length != 4) {
            throw new IllegalArgumentException("confirmation frame fixed-width field differs");
        }
        strictNonemptyAsciiText(fields.get("rendering_profile_id"), "rendering_profile_id");
        strictNonemptyAsciiText(
                fields.get("confirmation_gesture_kind"), "confirmation_gesture_kind");
        String timestamp = strictNonemptyAsciiText(
                fields.get("confirmation_gesture_at"), "confirmation_gesture_at");
        if (!MICROSECOND_UTC_TIMESTAMP.matcher(timestamp).matches()) {
            throw new IllegalArgumentException(
                    "confirmation_gesture_at is not an exact microsecond UTC timestamp");
        }
        try {
            Instant.parse(timestamp);
        } catch (DateTimeException exc) {
            throw new IllegalArgumentException(
                    "confirmation_gesture_at is not a valid UTC instant", exc);
        }
        return new ParsedFrame(fields);
    }

    private static long decodeUnsigned(byte[] bytes) {
        if (bytes.length == 0 || bytes.length > 8) {
            throw new IllegalArgumentException("unsigned integer width is unsupported");
        }
        long result = 0;
        for (byte value : bytes) {
            if ((result & 0xff00_0000_0000_0000L) != 0) {
                throw new IllegalArgumentException("unsigned integer exceeds signed range");
            }
            result = (result << 8) | Byte.toUnsignedInt(value);
        }
        return result;
    }

    private static byte[] decodeBase64(String encoded) {
        if (!BASE64.matcher(encoded).matches()) {
            throw new IllegalArgumentException("raw_base64 is not canonical base64");
        }
        try {
            byte[] decoded = Base64.getDecoder().decode(encoded);
            if (!Base64.getEncoder().encodeToString(decoded).equals(encoded)) {
                throw new IllegalArgumentException("raw_base64 has noncanonical pad bits");
            }
            return decoded;
        } catch (IllegalArgumentException exc) {
            throw new IllegalArgumentException("raw_base64 is malformed", exc);
        }
    }

    private static String pathFor(String contentAddress) {
        String hex = contentAddress.substring("sha256:".length());
        return "architecture/evidence-blobs/sha256/" + hex.substring(0, 2) + "/"
                + hex.substring(2);
    }

    private static boolean contentAddress(Object value) {
        return value instanceof String string && CONTENT_ADDRESS.matcher(string).matches();
    }

    private static byte[] digestBytes(String contentAddress) {
        if (!CONTENT_ADDRESS.matcher(contentAddress).matches()) {
            throw new IllegalArgumentException("content address is malformed");
        }
        String hex = contentAddress.substring(7);
        byte[] result = new byte[32];
        for (int index = 0; index < result.length; index++) {
            result[index] = (byte) Integer.parseInt(hex.substring(index * 2, index * 2 + 2), 16);
        }
        return result;
    }

    private static byte[] sha256(byte[] bytes) {
        try {
            return MessageDigest.getInstance("SHA-256").digest(bytes);
        } catch (NoSuchAlgorithmException exc) {
            throw new AssertionError("Java 21 lacks SHA-256", exc);
        }
    }

    private static String sha256Hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(64);
        for (byte value : sha256(bytes)) {
            result.append(Character.forDigit((value >>> 4) & 0xf, 16));
            result.append(Character.forDigit(value & 0xf, 16));
        }
        return result.toString();
    }

    private static String strictAscii(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length);
        for (byte value : bytes) {
            int unsigned = Byte.toUnsignedInt(value);
            if (unsigned > 0x7f) {
                throw new IllegalArgumentException("value is not ASCII");
            }
            result.append((char) unsigned);
        }
        return result.toString();
    }

    private static String strictNonemptyAsciiText(byte[] bytes, String label) {
        if (bytes.length == 0) {
            throw new IllegalArgumentException(label + " must be nonempty ASCII");
        }
        String text = strictAscii(bytes);
        for (int index = 0; index < text.length(); index++) {
            char value = text.charAt(index);
            if (value < 0x20 || value > 0x7e) {
                throw new IllegalArgumentException(label + " must be printable ASCII");
            }
        }
        return text;
    }

    private static String strictUtf8(byte[] bytes) {
        try {
            return StandardCharsets.UTF_8.newDecoder()
                    .onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                    .decode(ByteBuffer.wrap(bytes)).toString();
        } catch (CharacterCodingException exc) {
            return null;
        }
    }

    private static boolean integerEquals(Object value, long expected) {
        return value instanceof BigDecimal number
                && number.compareTo(BigDecimal.valueOf(expected)) == 0
                && number.scale() <= 0;
    }

    private static void requireIdentifier(String value, String label) {
        if (!IDENTIFIER.matcher(value).matches()) {
            throw new IllegalArgumentException(label + " is malformed");
        }
    }

    private static void requireObservationStatus(String status) {
        if (!Set.of("supported", "contradicted", "unknown", "not_applicable").contains(status)) {
            throw new IllegalArgumentException("unknown observation status: " + status);
        }
    }

    private static void requireTemplate(
            Map<String, Object> templates, String name, String expected) {
        InputAdapter.requireString(templates, name, expected);
    }

    private static List<String> strings(Object value, String label) {
        return strings(value, label, false, null);
    }

    private static List<String> strings(
            Object value,
            String label,
            boolean transformed,
            java.util.function.Function<Object, String> transform) {
        List<Object> array = InputAdapter.array(value, label);
        ArrayList<String> result = new ArrayList<>(array.size());
        for (Object item : array) {
            result.add(transformed ? transform.apply(item) : InputAdapter.string(item, label + " item"));
        }
        return result;
    }

    private record RoleSpec(String role, String mediaType, String byteFidelity) {}

    private record Contract(
            Map<String, Object> domainTemplates,
            Map<String, Object> backingTemplates,
            Map<String, Object> categoricalTemplates,
            List<RoleSpec> roles) {}

    private record BackingEvaluation(Map<String, Object> projection, Map<String, byte[]> readable) {}

    private record CategoricalEvaluation(List<Object> projections, List<String> failures) {}

    private record ParsedFrame(Map<String, byte[]> fields) {}

    /** Minimal deterministic CBOR recognizer: one definite-length, canonically-sized item. */
    private static final class CborReader {
        private final byte[] input;
        private int position;

        CborReader(byte[] input) {
            this.input = input;
        }

        void readDocument() {
            readItem(0);
            if (position != input.length) {
                throw new IllegalArgumentException("CBOR has trailing bytes");
            }
        }

        private void readItem(int depth) {
            if (depth > 128 || position >= input.length) {
                throw new IllegalArgumentException("CBOR is truncated or too deeply nested");
            }
            int initial = Byte.toUnsignedInt(input[position++]);
            int major = initial >>> 5;
            int additional = initial & 31;
            if (additional == 31) {
                throw new IllegalArgumentException("indefinite-length CBOR is not admitted");
            }
            if (major == 7) {
                readSimple(additional);
                return;
            }
            long argument = readArgument(additional);
            switch (major) {
                case 0, 1 -> { }
                case 2 -> skip(argument);
                case 3 -> {
                    byte[] text = take(argument);
                    if (strictUtf8(text) == null) {
                        throw new IllegalArgumentException("CBOR text is not UTF-8");
                    }
                }
                case 4 -> {
                    requireCollectionBound(argument);
                    for (long index = 0; index < argument; index++) {
                        readItem(depth + 1);
                    }
                }
                case 5 -> {
                    requireCollectionBound(argument);
                    HashSet<String> encodedKeys = new HashSet<>();
                    for (long index = 0; index < argument; index++) {
                        int keyStart = position;
                        readItem(depth + 1);
                        String encoded = Base64.getEncoder().encodeToString(
                                Arrays.copyOfRange(input, keyStart, position));
                        if (!encodedKeys.add(encoded)) {
                            throw new IllegalArgumentException("CBOR map has duplicate encoded key");
                        }
                        readItem(depth + 1);
                    }
                }
                case 6 -> readItem(depth + 1);
                default -> throw new AssertionError(major);
            }
        }

        private long readArgument(int additional) {
            if (additional < 24) {
                return additional;
            }
            return switch (additional) {
                case 24 -> {
                    long value = takeUnsigned(1);
                    if (value < 24) {
                        throw new IllegalArgumentException("CBOR integer is not shortest form");
                    }
                    yield value;
                }
                case 25 -> {
                    long value = takeUnsigned(2);
                    if (value <= 0xff) {
                        throw new IllegalArgumentException("CBOR integer is not shortest form");
                    }
                    yield value;
                }
                case 26 -> {
                    long value = takeUnsigned(4);
                    if (value <= 0xffff) {
                        throw new IllegalArgumentException("CBOR integer is not shortest form");
                    }
                    yield value;
                }
                case 27 -> {
                    long value = takeUnsigned(8);
                    if (Long.compareUnsigned(value, 0xffff_ffffL) <= 0) {
                        throw new IllegalArgumentException("CBOR integer is not shortest form");
                    }
                    yield value;
                }
                default -> throw new IllegalArgumentException("reserved CBOR additional information");
            };
        }

        private void readSimple(int additional) {
            switch (additional) {
                case 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                        16, 17, 18, 19, 20, 21, 22, 23 -> { }
                case 24 -> {
                    long value = takeUnsigned(1);
                    if (value < 32) {
                        throw new IllegalArgumentException(
                                "CBOR simple value is not shortest form");
                    }
                }
                case 25 -> takeUnsigned(2);
                case 26 -> takeUnsigned(4);
                case 27 -> takeUnsigned(8);
                default -> throw new IllegalArgumentException(
                        "reserved CBOR simple additional information");
            }
        }

        private void requireCollectionBound(long count) {
            if (count > input.length) {
                throw new IllegalArgumentException("CBOR collection count exceeds input bound");
            }
        }

        private long takeUnsigned(int count) {
            if (position + count > input.length) {
                throw new IllegalArgumentException("CBOR argument is truncated");
            }
            long result = 0;
            for (int index = 0; index < count; index++) {
                result = (result << 8) | Byte.toUnsignedInt(input[position++]);
            }
            return result;
        }

        private byte[] take(long count) {
            if (count < 0 || count > Integer.MAX_VALUE || position + count > input.length) {
                throw new IllegalArgumentException("CBOR byte string is truncated");
            }
            byte[] result = Arrays.copyOfRange(input, position, position + (int) count);
            position += (int) count;
            return result;
        }

        private void skip(long count) {
            take(count);
        }
    }
}
