package odeya.hda.java21;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Exact RFC 6902 subset admitted by the expectation-free vector corpus. */
final class JsonPatch {
    private static final Set<String> OPERATIONS = Set.of("add", "copy", "move", "remove", "replace");

    private JsonPatch() {}

    static Object apply(Object document, List<Object> mutations) {
        Object result = StrictJson.deepCopy(document);
        for (int index = 0; index < mutations.size(); index++) {
            Map<String, Object> mutation = object(mutations.get(index), "mutation " + index);
            String operation = string(mutation.get("op"), "mutation op");
            if (!OPERATIONS.contains(operation)) {
                throw new IllegalArgumentException("unadmitted JSON Patch operation: " + operation);
            }
            String path = string(mutation.get("path"), "mutation path");
            Set<String> expectedKeys;
            switch (operation) {
                case "add", "replace" -> expectedKeys = Set.of("op", "path", "value");
                case "copy", "move" -> expectedKeys = Set.of("op", "path", "from");
                case "remove" -> expectedKeys = Set.of("op", "path");
                default -> throw new AssertionError(operation);
            }
            if (!mutation.keySet().equals(expectedKeys)) {
                throw new IllegalArgumentException("mutation members do not match operation " + operation);
            }
            result = switch (operation) {
                case "add" -> add(result, path, StrictJson.deepCopy(mutation.get("value")));
                case "remove" -> remove(result, path).document();
                case "replace" -> replace(result, path, StrictJson.deepCopy(mutation.get("value")));
                case "copy" -> add(result, path,
                        StrictJson.deepCopy(get(result, string(mutation.get("from"), "mutation from"))));
                case "move" -> move(result, string(mutation.get("from"), "mutation from"), path);
                default -> throw new AssertionError(operation);
            };
        }
        return result;
    }

    private static Object move(Object document, String from, String path) {
        List<String> fromTokens = tokens(from);
        List<String> pathTokens = tokens(path);
        if (pathTokens.size() > fromTokens.size()
                && pathTokens.subList(0, fromTokens.size()).equals(fromTokens)) {
            throw new IllegalArgumentException("JSON Patch move target is inside source");
        }
        Removal removal = remove(document, from);
        return add(removal.document(), path, removal.value());
    }

    private static Object replace(Object document, String pointer, Object value) {
        if (pointer.isEmpty()) {
            return value;
        }
        get(document, pointer);
        Removal removal = remove(document, pointer);
        return add(removal.document(), pointer, value);
    }

    private static Object add(Object document, String pointer, Object value) {
        List<String> path = tokens(pointer);
        if (path.isEmpty()) {
            return value;
        }
        Object parent = descend(document, path.subList(0, path.size() - 1));
        String finalToken = path.get(path.size() - 1);
        if (parent instanceof Map<?, ?> rawMap) {
            map(rawMap).put(finalToken, value);
            return document;
        }
        if (parent instanceof List<?> rawList) {
            List<Object> list = list(rawList);
            if (finalToken.equals("-")) {
                list.add(value);
            } else {
                int index = arrayIndex(finalToken, list.size(), true);
                list.add(index, value);
            }
            return document;
        }
        throw new IllegalArgumentException("JSON Patch add parent is scalar");
    }

    private static Removal remove(Object document, String pointer) {
        List<String> path = tokens(pointer);
        if (path.isEmpty()) {
            return new Removal(null, document);
        }
        Object parent = descend(document, path.subList(0, path.size() - 1));
        String finalToken = path.get(path.size() - 1);
        if (parent instanceof Map<?, ?> rawMap) {
            Map<String, Object> map = map(rawMap);
            if (!map.containsKey(finalToken)) {
                throw new IllegalArgumentException("JSON Patch remove member does not exist");
            }
            return new Removal(document, map.remove(finalToken));
        }
        if (parent instanceof List<?> rawList) {
            List<Object> list = list(rawList);
            int index = arrayIndex(finalToken, list.size(), false);
            return new Removal(document, list.remove(index));
        }
        throw new IllegalArgumentException("JSON Patch remove parent is scalar");
    }

    private static Object get(Object document, String pointer) {
        return descend(document, tokens(pointer));
    }

    private static Object descend(Object document, List<String> path) {
        Object current = document;
        for (String token : path) {
            if (current instanceof Map<?, ?> rawMap) {
                Map<String, Object> map = map(rawMap);
                if (!map.containsKey(token)) {
                    throw new IllegalArgumentException("JSON Pointer member does not exist: " + token);
                }
                current = map.get(token);
            } else if (current instanceof List<?> rawList) {
                List<Object> list = list(rawList);
                current = list.get(arrayIndex(token, list.size(), false));
            } else {
                throw new IllegalArgumentException("JSON Pointer traverses a scalar");
            }
        }
        return current;
    }

    private static List<String> tokens(String pointer) {
        if (pointer.isEmpty()) {
            return List.of();
        }
        if (pointer.charAt(0) != '/') {
            throw new IllegalArgumentException("JSON Pointer must be empty or start with '/'");
        }
        String[] encoded = pointer.substring(1).split("/", -1);
        ArrayList<String> decoded = new ArrayList<>(encoded.length);
        for (String token : encoded) {
            StringBuilder result = new StringBuilder();
            for (int index = 0; index < token.length(); index++) {
                char current = token.charAt(index);
                if (current != '~') {
                    result.append(current);
                    continue;
                }
                if (++index >= token.length()) {
                    throw new IllegalArgumentException("truncated JSON Pointer escape");
                }
                char escape = token.charAt(index);
                if (escape == '0') {
                    result.append('~');
                } else if (escape == '1') {
                    result.append('/');
                } else {
                    throw new IllegalArgumentException("unknown JSON Pointer escape");
                }
            }
            decoded.add(result.toString());
        }
        return decoded;
    }

    private static int arrayIndex(String token, int size, boolean allowEnd) {
        if (token.isEmpty() || (token.length() > 1 && token.charAt(0) == '0')) {
            throw new IllegalArgumentException("invalid JSON Pointer array index");
        }
        for (int index = 0; index < token.length(); index++) {
            if (token.charAt(index) < '0' || token.charAt(index) > '9') {
                throw new IllegalArgumentException("invalid JSON Pointer array index");
            }
        }
        final int result;
        try {
            result = Integer.parseInt(token);
        } catch (NumberFormatException exc) {
            throw new IllegalArgumentException("JSON Pointer array index is too large", exc);
        }
        int maximum = allowEnd ? size : size - 1;
        if (result < 0 || result > maximum) {
            throw new IllegalArgumentException("JSON Pointer array index is out of bounds");
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> map(Map<?, ?> map) {
        return (Map<String, Object>) map;
    }

    @SuppressWarnings("unchecked")
    private static List<Object> list(List<?> list) {
        return (List<Object>) list;
    }

    private static Map<String, Object> object(Object value, String label) {
        if (!(value instanceof Map<?, ?> raw)) {
            throw new IllegalArgumentException(label + " must be an object");
        }
        Map<String, Object> result = new java.util.LinkedHashMap<>();
        for (Map.Entry<?, ?> entry : raw.entrySet()) {
            if (!(entry.getKey() instanceof String key)) {
                throw new IllegalArgumentException(label + " has a non-string name");
            }
            result.put(key, entry.getValue());
        }
        return result;
    }

    private static String string(Object value, String label) {
        if (!(value instanceof String result)) {
            throw new IllegalArgumentException(label + " must be a string");
        }
        return result;
    }

    private record Removal(Object document, Object value) {}
}
