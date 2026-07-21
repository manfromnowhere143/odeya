package odeya.hda.java21;

import java.math.BigDecimal;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** A dependency-free JSON parser that refuses duplicate names and malformed UTF-8. */
final class StrictJson {
    private static final int MAX_DEPTH = 256;

    private StrictJson() {}

    static Object parse(byte[] bytes) {
        final String text;
        try {
            text = StandardCharsets.UTF_8.newDecoder()
                    .onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                    .decode(ByteBuffer.wrap(bytes))
                    .toString();
        } catch (CharacterCodingException exc) {
            throw new IllegalArgumentException("JSON is not strict UTF-8", exc);
        }
        if (!text.isEmpty() && text.charAt(0) == '\ufeff') {
            throw new IllegalArgumentException("UTF-8 BOM is not admitted");
        }
        return new Parser(text).parseDocument();
    }

    static String write(Object value) {
        StringBuilder out = new StringBuilder();
        writeValue(value, out, 0);
        return out.toString();
    }

    static Object deepCopy(Object value) {
        if (value == null || value instanceof String || value instanceof Boolean
                || value instanceof BigDecimal) {
            return value;
        }
        if (value instanceof Map<?, ?> source) {
            LinkedHashMap<String, Object> copy = new LinkedHashMap<>();
            for (Map.Entry<?, ?> entry : source.entrySet()) {
                if (!(entry.getKey() instanceof String key)) {
                    throw new IllegalArgumentException("JSON object name is not a string");
                }
                copy.put(key, deepCopy(entry.getValue()));
            }
            return copy;
        }
        if (value instanceof List<?> source) {
            ArrayList<Object> copy = new ArrayList<>(source.size());
            for (Object item : source) {
                copy.add(deepCopy(item));
            }
            return copy;
        }
        throw new IllegalArgumentException("value is not in the JSON data model");
    }

    private static void writeValue(Object value, StringBuilder out, int depth) {
        if (depth > MAX_DEPTH) {
            throw new IllegalArgumentException("JSON output nesting exceeds limit");
        }
        if (value == null) {
            out.append("null");
        } else if (value instanceof String string) {
            writeString(string, out);
        } else if (value instanceof Boolean bool) {
            out.append(bool ? "true" : "false");
        } else if (value instanceof BigDecimal number) {
            out.append(number.toPlainString());
        } else if (value instanceof Byte || value instanceof Short || value instanceof Integer
                || value instanceof Long) {
            out.append(value);
        } else if (value instanceof Map<?, ?> object) {
            out.append('{');
            boolean first = true;
            for (Map.Entry<?, ?> entry : object.entrySet()) {
                if (!(entry.getKey() instanceof String key)) {
                    throw new IllegalArgumentException("JSON object name is not a string");
                }
                if (!first) {
                    out.append(',');
                }
                first = false;
                writeString(key, out);
                out.append(':');
                writeValue(entry.getValue(), out, depth + 1);
            }
            out.append('}');
        } else if (value instanceof List<?> array) {
            out.append('[');
            for (int index = 0; index < array.size(); index++) {
                if (index != 0) {
                    out.append(',');
                }
                writeValue(array.get(index), out, depth + 1);
            }
            out.append(']');
        } else {
            throw new IllegalArgumentException("value is not in the JSON data model");
        }
    }

    private static void writeString(String value, StringBuilder out) {
        out.append('"');
        for (int index = 0; index < value.length(); index++) {
            char current = value.charAt(index);
            switch (current) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\b' -> out.append("\\b");
                case '\f' -> out.append("\\f");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                default -> {
                    if (current < 0x20) {
                        out.append(String.format("\\u%04x", (int) current));
                    } else if (Character.isHighSurrogate(current)) {
                        if (index + 1 >= value.length()
                                || !Character.isLowSurrogate(value.charAt(index + 1))) {
                            throw new IllegalArgumentException("unpaired high surrogate in JSON string");
                        }
                        out.append(current).append(value.charAt(++index));
                    } else if (Character.isLowSurrogate(current)) {
                        throw new IllegalArgumentException("unpaired low surrogate in JSON string");
                    } else {
                        out.append(current);
                    }
                }
            }
        }
        out.append('"');
    }

    private static final class Parser {
        private final String input;
        private int position;

        Parser(String input) {
            this.input = input;
        }

        Object parseDocument() {
            skipWhitespace();
            Object result = parseValue(0);
            skipWhitespace();
            if (position != input.length()) {
                fail("trailing data");
            }
            return result;
        }

        private Object parseValue(int depth) {
            if (depth > MAX_DEPTH) {
                fail("nesting exceeds limit");
            }
            if (position >= input.length()) {
                fail("unexpected end of input");
            }
            return switch (input.charAt(position)) {
                case '{' -> parseObject(depth + 1);
                case '[' -> parseArray(depth + 1);
                case '"' -> parseString();
                case 't' -> parseLiteral("true", Boolean.TRUE);
                case 'f' -> parseLiteral("false", Boolean.FALSE);
                case 'n' -> parseLiteral("null", null);
                default -> parseNumber();
            };
        }

        private Map<String, Object> parseObject(int depth) {
            expect('{');
            LinkedHashMap<String, Object> object = new LinkedHashMap<>();
            skipWhitespace();
            if (take('}')) {
                return object;
            }
            while (true) {
                if (position >= input.length() || input.charAt(position) != '"') {
                    fail("object member name must be a string");
                }
                String name = parseString();
                if (object.containsKey(name)) {
                    fail("duplicate object member: " + name);
                }
                skipWhitespace();
                expect(':');
                skipWhitespace();
                object.put(name, parseValue(depth));
                skipWhitespace();
                if (take('}')) {
                    return object;
                }
                expect(',');
                skipWhitespace();
            }
        }

        private List<Object> parseArray(int depth) {
            expect('[');
            ArrayList<Object> array = new ArrayList<>();
            skipWhitespace();
            if (take(']')) {
                return array;
            }
            while (true) {
                array.add(parseValue(depth));
                skipWhitespace();
                if (take(']')) {
                    return array;
                }
                expect(',');
                skipWhitespace();
            }
        }

        private String parseString() {
            expect('"');
            StringBuilder result = new StringBuilder();
            while (position < input.length()) {
                char current = input.charAt(position++);
                if (current == '"') {
                    return result.toString();
                }
                if (current < 0x20) {
                    fail("unescaped control character in string");
                }
                if (current == '\\') {
                    if (position >= input.length()) {
                        fail("truncated string escape");
                    }
                    char escape = input.charAt(position++);
                    switch (escape) {
                        case '"', '\\', '/' -> result.append(escape);
                        case 'b' -> result.append('\b');
                        case 'f' -> result.append('\f');
                        case 'n' -> result.append('\n');
                        case 'r' -> result.append('\r');
                        case 't' -> result.append('\t');
                        case 'u' -> appendUnicodeEscape(result);
                        default -> fail("unknown string escape");
                    }
                } else if (Character.isHighSurrogate(current)) {
                    if (position >= input.length()
                            || !Character.isLowSurrogate(input.charAt(position))) {
                        fail("unpaired high surrogate in string");
                    }
                    result.append(current).append(input.charAt(position++));
                } else if (Character.isLowSurrogate(current)) {
                    fail("unpaired low surrogate in string");
                } else {
                    result.append(current);
                }
            }
            fail("unterminated string");
            return null;
        }

        private void appendUnicodeEscape(StringBuilder result) {
            char first = (char) readHexQuad();
            if (Character.isHighSurrogate(first)) {
                if (position + 6 > input.length() || input.charAt(position) != '\\'
                        || input.charAt(position + 1) != 'u') {
                    fail("escaped high surrogate is not paired");
                }
                position += 2;
                char second = (char) readHexQuad();
                if (!Character.isLowSurrogate(second)) {
                    fail("escaped high surrogate has invalid pair");
                }
                result.append(first).append(second);
            } else if (Character.isLowSurrogate(first)) {
                fail("escaped low surrogate is not paired");
            } else {
                result.append(first);
            }
        }

        private int readHexQuad() {
            if (position + 4 > input.length()) {
                fail("truncated unicode escape");
            }
            int result = 0;
            for (int count = 0; count < 4; count++) {
                char digit = input.charAt(position++);
                int value = Character.digit(digit, 16);
                if (value < 0) {
                    fail("invalid unicode escape");
                }
                result = (result << 4) | value;
            }
            return result;
        }

        private Object parseLiteral(String spelling, Object value) {
            if (!input.startsWith(spelling, position)) {
                fail("invalid literal");
            }
            position += spelling.length();
            return value;
        }

        private BigDecimal parseNumber() {
            int start = position;
            take('-');
            if (take('0')) {
                if (position < input.length() && isDigit(input.charAt(position))) {
                    fail("leading zero in number");
                }
            } else {
                requireDigits();
            }
            if (take('.')) {
                requireDigits();
            }
            if (position < input.length()
                    && (input.charAt(position) == 'e' || input.charAt(position) == 'E')) {
                position++;
                if (position < input.length()
                        && (input.charAt(position) == '+' || input.charAt(position) == '-')) {
                    position++;
                }
                requireDigits();
            }
            try {
                return new BigDecimal(input.substring(start, position));
            } catch (NumberFormatException exc) {
                fail("invalid number");
                return null;
            }
        }

        private void requireDigits() {
            int start = position;
            while (position < input.length() && isDigit(input.charAt(position))) {
                position++;
            }
            if (position == start) {
                fail("number requires a digit");
            }
        }

        private static boolean isDigit(char value) {
            return value >= '0' && value <= '9';
        }

        private void skipWhitespace() {
            while (position < input.length()) {
                char current = input.charAt(position);
                if (current == ' ' || current == '\t' || current == '\n' || current == '\r') {
                    position++;
                } else {
                    return;
                }
            }
        }

        private boolean take(char expected) {
            if (position < input.length() && input.charAt(position) == expected) {
                position++;
                return true;
            }
            return false;
        }

        private void expect(char expected) {
            if (!take(expected)) {
                fail("expected '" + expected + "'");
            }
        }

        private void fail(String message) {
            throw new IllegalArgumentException(message + " at character " + position);
        }
    }
}
