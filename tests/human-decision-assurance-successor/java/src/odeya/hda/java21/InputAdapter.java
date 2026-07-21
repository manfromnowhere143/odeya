package odeya.hda.java21;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Reads exactly the three normative input surfaces and resolves one vector. */
final class InputAdapter {
    static final int MAX_FILE_BYTES = 16 * 1024 * 1024;
    static final String RULESET_ID =
            "urn:odeya:human-decision-assurance-eligibility:0.2.0-candidate";
    static final String RESOLVER_ID =
            "urn:odeya:human-decision-assurance:content-address-resolver:0.1.0-candidate";

    private InputAdapter() {}

    record AdaptedInput(
            Map<String, Object> ruleset,
            Map<String, Object> resolver,
            Map<String, Object> vectorCorpus,
            Map<String, Object> resolvedInput,
            String vectorId) {}

    static AdaptedInput load(String[] arguments) throws IOException {
        Map<String, Path> paths = parseArguments(arguments);
        Map<String, Object> vectors = readObject(paths.get("--vectors"), "vectors.json");
        Map<String, Object> ruleset = readObject(
                paths.get("--ruleset"),
                "human-decision-assurance-individual-eligibility-ruleset-v2-candidate.json");
        Map<String, Object> resolver = readObject(
                paths.get("--resolver"),
                "human-decision-assurance-content-address-resolver-profile-v1-candidate.json");

        requireExactKeys(vectors, Set.of(
                "suite_version", "artifact_class", "candidate_status", "ruleset_id",
                "resolver_profile_id", "mutation_language", "base_input", "vectors"),
                "vector corpus");
        requireString(vectors, "artifact_class",
                "human_decision_assurance_successor_expectation_free_evaluator_inputs");
        requireString(vectors, "ruleset_id", RULESET_ID);
        requireString(vectors, "resolver_profile_id", RESOLVER_ID);
        requireString(ruleset, "ruleset_id", RULESET_ID);
        requireString(ruleset, "ruleset_version", "0.2.0");
        requireString(resolver, "profile_id", RESOLVER_ID);
        requireString(resolver, "profile_version", "0.1.0");
        validateMutationLanguage(object(vectors.get("mutation_language"), "mutation language"));

        String vectorId = paths.get("--vector-id").toString();
        Map<String, Object> baseInput = object(vectors.get("base_input"), "base input");
        List<Object> vectorList = array(vectors.get("vectors"), "vectors");
        Map<String, Map<String, Object>> byId = indexVectors(vectorList);
        Object resolved = resolveVector(vectorId, baseInput, byId, new HashSet<>());
        return new AdaptedInput(
                ruleset, resolver, vectors, object(resolved, "resolved vector input"), vectorId);
    }

    private static Map<String, Path> parseArguments(String[] arguments) {
        if (arguments.length != 8) {
            throw new IllegalArgumentException(
                    "usage: --vectors PATH --ruleset PATH --resolver PATH --vector-id ID");
        }
        Map<String, Path> result = new HashMap<>();
        Set<String> pathOptions = Set.of("--vectors", "--ruleset", "--resolver");
        for (int index = 0; index < arguments.length; index += 2) {
            String option = arguments[index];
            if (!pathOptions.contains(option) && !option.equals("--vector-id")) {
                throw new IllegalArgumentException("unknown command-line option: " + option);
            }
            if (result.containsKey(option)) {
                throw new IllegalArgumentException("duplicate command-line option: " + option);
            }
            String value = arguments[index + 1];
            if (value.isEmpty()) {
                throw new IllegalArgumentException("empty command-line value for " + option);
            }
            result.put(option, Path.of(value));
        }
        if (!result.keySet().equals(Set.of("--vectors", "--ruleset", "--resolver", "--vector-id"))) {
            throw new IllegalArgumentException("a required command-line option is absent");
        }
        return result;
    }

    private static Map<String, Object> readObject(Path path, String requiredFilename) throws IOException {
        if (!path.getFileName().toString().equals(requiredFilename)) {
            throw new IllegalArgumentException("input filename is not admitted: " + path.getFileName());
        }
        if (Files.isSymbolicLink(path)
                || !Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS)) {
            throw new IllegalArgumentException("input must be a regular non-symbolic-link file");
        }
        long size = Files.size(path);
        if (size <= 0 || size > MAX_FILE_BYTES) {
            throw new IllegalArgumentException("input file size is outside the admitted range");
        }
        return object(StrictJson.parse(Files.readAllBytes(path)), requiredFilename);
    }

    private static void validateMutationLanguage(Map<String, Object> language) {
        requireExactKeys(language, Set.of(
                "standard", "allowed_operations", "array_append_token", "application_order",
                "base_vector_resolution", "cycles_or_unknown_base_vector_ids"),
                "mutation language");
        requireString(language, "standard", "rfc6902_json_patch_subset");
        requireString(language, "array_append_token", "-");
        List<Object> operations = array(language.get("allowed_operations"), "allowed operations");
        List<String> actual = new ArrayList<>();
        for (Object operation : operations) {
            actual.add(string(operation, "allowed operation"));
        }
        if (!actual.equals(List.of("add", "copy", "move", "remove", "replace"))) {
            throw new IllegalArgumentException("mutation operation inventory differs from contract");
        }
    }

    private static Map<String, Map<String, Object>> indexVectors(List<Object> vectors) {
        LinkedHashMap<String, Map<String, Object>> result = new LinkedHashMap<>();
        for (Object value : vectors) {
            Map<String, Object> vector = object(value, "vector");
            Set<String> allowed = vector.containsKey("base_vector_id")
                    ? Set.of("vector_id", "base_vector_id", "mutations")
                    : Set.of("vector_id", "mutations");
            requireExactKeys(vector, allowed, "vector");
            String id = string(vector.get("vector_id"), "vector id");
            if (id.isEmpty() || result.put(id, vector) != null) {
                throw new IllegalArgumentException("empty or duplicate vector id: " + id);
            }
            array(vector.get("mutations"), "vector mutations");
            if (vector.containsKey("base_vector_id")) {
                string(vector.get("base_vector_id"), "base vector id");
            }
        }
        if (result.isEmpty()) {
            throw new IllegalArgumentException("vector corpus is empty");
        }
        return result;
    }

    private static Object resolveVector(
            String id,
            Map<String, Object> baseInput,
            Map<String, Map<String, Object>> byId,
            Set<String> resolving) {
        Map<String, Object> vector = byId.get(id);
        if (vector == null) {
            throw new IllegalArgumentException("unknown vector id: " + id);
        }
        if (!resolving.add(id)) {
            throw new IllegalArgumentException("base_vector_id cycle at: " + id);
        }
        Object inherited;
        if (vector.containsKey("base_vector_id")) {
            inherited = resolveVector(
                    string(vector.get("base_vector_id"), "base vector id"),
                    baseInput, byId, resolving);
        } else {
            inherited = StrictJson.deepCopy(baseInput);
        }
        Object resolved = JsonPatch.apply(inherited, array(vector.get("mutations"), "mutations"));
        resolving.remove(id);
        return resolved;
    }

    static Map<String, Object> object(Object value, String label) {
        if (!(value instanceof Map<?, ?> raw)) {
            throw new IllegalArgumentException(label + " must be an object");
        }
        LinkedHashMap<String, Object> result = new LinkedHashMap<>();
        for (Map.Entry<?, ?> entry : raw.entrySet()) {
            if (!(entry.getKey() instanceof String key)) {
                throw new IllegalArgumentException(label + " has a non-string name");
            }
            result.put(key, entry.getValue());
        }
        return result;
    }

    static List<Object> array(Object value, String label) {
        if (!(value instanceof List<?> raw)) {
            throw new IllegalArgumentException(label + " must be an array");
        }
        return new ArrayList<>(raw);
    }

    static String string(Object value, String label) {
        if (!(value instanceof String result)) {
            throw new IllegalArgumentException(label + " must be a string");
        }
        return result;
    }

    static String nullableString(Object value, String label) {
        return value == null ? null : string(value, label);
    }

    static boolean bool(Object value, String label) {
        if (!(value instanceof Boolean result)) {
            throw new IllegalArgumentException(label + " must be boolean");
        }
        return result;
    }

    static long integer(Object value, String label) {
        if (!(value instanceof BigDecimal number)) {
            throw new IllegalArgumentException(label + " must be an integer");
        }
        try {
            return number.longValueExact();
        } catch (ArithmeticException exc) {
            throw new IllegalArgumentException(label + " must be an exact 64-bit integer", exc);
        }
    }

    static void requireString(Map<String, Object> object, String name, String expected) {
        String actual = string(object.get(name), name);
        if (!actual.equals(expected)) {
            throw new IllegalArgumentException(name + " differs from the admitted identity");
        }
    }

    static void requireExactKeys(Map<String, Object> object, Set<String> expected, String label) {
        if (!object.keySet().equals(expected)) {
            throw new IllegalArgumentException(label + " members differ from the closed contract");
        }
    }
}
