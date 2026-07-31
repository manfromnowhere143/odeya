// PRQ-002G profile-bounded JCS serialization runner (Node.js path).
//
// Source-separated peer of the CPython runner: parses every frame with its
// own recursive-descent reader (never JSON.parse), enforces the exact
// odeya-jcs-0.3 interpretation pinned by ADR 0103 and retained by ADR 0107 —
// strict UTF-8 with BOM refusal, strict RFC 8259 grammar with duplicate
// decoded-name refusal, I-JSON surrogate and noncharacter refusal,
// integer-only numbers in the inclusive safe range, recursive member
// ordering by unsigned UTF-16 code units over decoded names (native JS
// string comparison), ECMAScript 2019 string escaping with U+002F emitted
// unescaped — and emits canonical UTF-8 bytes. Zero third-party
// dependencies; never reads the private expectation file. Bounded
// architecture evidence only.

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import process from "node:process";

const SCHEMA_VERSION = "0.1.0";
const SUITE_ID = "prq-002g-jcs-serialization-conformance.0001";
const IMPLEMENTATION_ID = "nodejs-native-jcs-serializer.0001";
const MIN_SAFE = -9007199254740991n;
const MAX_SAFE = 9007199254740991n;

class Refusal extends Error {
  constructor(code) {
    super(code);
    this.code = code;
  }
}

function refuse(code) {
  throw new Refusal(code);
}

function sha256(raw) {
  return "sha256:" + createHash("sha256").update(raw).digest("hex");
}

class JInt {
  constructor(lexeme) {
    this.lexeme = lexeme;
  }
}

class JObj {
  constructor() {
    this.keys = [];
    this.map = new Map();
  }
  set(key, value) {
    if (this.map.has(key)) {
      return false;
    }
    this.keys.push(key);
    this.map.set(key, value);
    return true;
  }
  get(key) {
    return this.map.get(key);
  }
}

class Parser {
  constructor(text) {
    this.text = text;
    this.index = 0;
  }
  fail() {
    refuse("malformed_json");
  }
  skipWhitespace() {
    while (this.index < this.text.length) {
      const ch = this.text[this.index];
      if (ch === " " || ch === "\t" || ch === "\n" || ch === "\r") {
        this.index += 1;
      } else {
        break;
      }
    }
  }
  parseDocument() {
    this.skipWhitespace();
    if (this.index >= this.text.length) {
      this.fail();
    }
    const value = this.parseValue();
    this.skipWhitespace();
    if (this.index !== this.text.length) {
      refuse("trailing_content");
    }
    return value;
  }
  parseValue() {
    const ch = this.text[this.index];
    if (ch === "{") return this.parseObject();
    if (ch === "[") return this.parseArray();
    if (ch === '"') return this.parseString();
    if (this.text.startsWith("NaN", this.index)) {
      refuse("non_finite_literal");
    }
    if (this.text.startsWith("Infinity", this.index)) {
      refuse("non_finite_literal");
    }
    if (this.text.startsWith("-Infinity", this.index)) {
      refuse("non_finite_literal");
    }
    if (ch === "-" || (ch >= "0" && ch <= "9")) return this.parseNumber();
    if (this.text.startsWith("true", this.index)) {
      this.index += 4;
      return true;
    }
    if (this.text.startsWith("false", this.index)) {
      this.index += 5;
      return false;
    }
    if (this.text.startsWith("null", this.index)) {
      this.index += 4;
      return null;
    }
    this.fail();
  }
  parseObject() {
    const object = new JObj();
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === "}") {
      this.index += 1;
      return object;
    }
    for (;;) {
      this.skipWhitespace();
      if (this.text[this.index] !== '"') this.fail();
      const key = this.parseString();
      this.skipWhitespace();
      if (this.text[this.index] !== ":") this.fail();
      this.index += 1;
      this.skipWhitespace();
      const value = this.parseValue();
      if (!object.set(key, value)) {
        refuse("duplicate_decoded_member_name");
      }
      this.skipWhitespace();
      const next = this.text[this.index];
      if (next === ",") {
        this.index += 1;
        continue;
      }
      if (next === "}") {
        this.index += 1;
        return object;
      }
      this.fail();
    }
  }
  parseArray() {
    const array = [];
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === "]") {
      this.index += 1;
      return array;
    }
    for (;;) {
      this.skipWhitespace();
      array.push(this.parseValue());
      this.skipWhitespace();
      const next = this.text[this.index];
      if (next === ",") {
        this.index += 1;
        continue;
      }
      if (next === "]") {
        this.index += 1;
        return array;
      }
      this.fail();
    }
  }
  parseString() {
    let result = "";
    this.index += 1;
    for (;;) {
      if (this.index >= this.text.length) this.fail();
      const ch = this.text[this.index];
      if (ch === '"') {
        this.index += 1;
        return result;
      }
      if (ch === "\\") {
        const escape = this.text[this.index + 1];
        this.index += 2;
        if (escape === '"') result += '"';
        else if (escape === "\\") result += "\\";
        else if (escape === "/") result += "/";
        else if (escape === "b") result += "\b";
        else if (escape === "f") result += "\f";
        else if (escape === "n") result += "\n";
        else if (escape === "r") result += "\r";
        else if (escape === "t") result += "\t";
        else if (escape === "u") {
          const hex = this.text.slice(this.index, this.index + 4);
          if (!/^[0-9A-Fa-f]{4}$/.test(hex)) this.fail();
          this.index += 4;
          const code = Number.parseInt(hex, 16);
          if (code >= 0xd800 && code <= 0xdbff) {
            if (
              this.text[this.index] === "\\" &&
              this.text[this.index + 1] === "u"
            ) {
              const low = this.text.slice(this.index + 2, this.index + 6);
              if (!/^[0-9A-Fa-f]{4}$/.test(low)) this.fail();
              const lowCode = Number.parseInt(low, 16);
              if (lowCode < 0xdc00 || lowCode > 0xdfff) {
                refuse("unpaired_surrogate");
              }
              this.index += 6;
              result += String.fromCodePoint(
                0x10000 + (code - 0xd800) * 0x400 + (lowCode - 0xdc00),
              );
            } else {
              refuse("unpaired_surrogate");
            }
          } else if (code >= 0xdc00 && code <= 0xdfff) {
            refuse("unpaired_surrogate");
          } else {
            result += String.fromCharCode(code);
          }
        } else {
          this.fail();
        }
        continue;
      }
      const unit = ch.charCodeAt(0);
      if (unit < 0x20) this.fail();
      result += ch;
      this.index += 1;
    }
  }
  parseNumber() {
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(
      this.text.slice(this.index),
    );
    if (match === null) this.fail();
    const lexeme = match[0];
    this.index += lexeme.length;
    if (!/^-?(?:0|[1-9][0-9]*)$/.test(lexeme)) {
      refuse("non_integer_number_token");
    }
    if (lexeme.startsWith("-0")) {
      refuse("lexical_negative_zero");
    }
    const value = BigInt(lexeme);
    if (value < MIN_SAFE || value > MAX_SAFE) {
      refuse("integer_outside_safe_range");
    }
    return new JInt(lexeme);
  }
}

function scanStrings(value) {
  if (typeof value === "string") {
    for (const character of value) {
      const codePoint = character.codePointAt(0);
      if (codePoint >= 0xd800 && codePoint <= 0xdfff) {
        refuse("unpaired_surrogate");
      }
      if (
        (codePoint >= 0xfdd0 && codePoint <= 0xfdef) ||
        (codePoint & 0xffff) === 0xfffe ||
        (codePoint & 0xffff) === 0xffff
      ) {
        refuse("unicode_noncharacter");
      }
    }
    return;
  }
  if (value instanceof JObj) {
    for (const key of value.keys) {
      scanStrings(key);
      scanStrings(value.get(key));
    }
  } else if (Array.isArray(value)) {
    for (const child of value) {
      scanStrings(child);
    }
  }
}

function parseFrame(raw) {
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
    refuse("leading_byte_order_mark");
  }
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(raw);
  } catch {
    refuse("invalid_utf8_encoding");
  }
  const document = new Parser(text).parseDocument();
  scanStrings(document);
  return document;
}

function escapeString(value) {
  let out = '"';
  for (const character of value) {
    if (character === '"') out += '\\"';
    else if (character === "\\") out += "\\\\";
    else if (character === "\b") out += "\\b";
    else if (character === "\f") out += "\\f";
    else if (character === "\n") out += "\\n";
    else if (character === "\r") out += "\\r";
    else if (character === "\t") out += "\\t";
    else if (character.codePointAt(0) < 0x20) {
      out += "\\u" + character.codePointAt(0).toString(16).padStart(4, "0");
    } else {
      out += character;
    }
  }
  return out + '"';
}

function canonicalize(value) {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (value instanceof JInt) return value.lexeme;
  if (typeof value === "string") return escapeString(value);
  if (Array.isArray(value)) {
    return "[" + value.map(canonicalize).join(",") + "]";
  }
  if (value instanceof JObj) {
    const ordered = [...value.keys].sort();
    return (
      "{" +
      ordered
        .map((name) => escapeString(name) + ":" + canonicalize(value.get(name)))
        .join(",") +
      "}"
    );
  }
  refuse("malformed_json");
}

// Compact result serializer matching Python json.dumps(ensure_ascii=False,
// separators=(",", ":")) byte-for-byte for plain objects built in fixed
// insertion order.
function emit(value) {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "string") return escapeString(value);
  if (Array.isArray(value)) return "[" + value.map(emit).join(",") + "]";
  if (typeof value === "object") {
    return (
      "{" +
      Object.keys(value)
        .map((key) => escapeString(key) + ":" + emit(value[key]))
        .join(",") +
      "}"
    );
  }
  refuse("malformed_json");
}

function parseArguments(argv) {
  const values = new Map();
  for (let index = 2; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (value === undefined || !["--vectors", "--source-manifest"].includes(flag)) {
      throw new Error(`unsupported argument ${flag}`);
    }
    values.set(flag, value);
  }
  for (const flag of ["--vectors", "--source-manifest"]) {
    if (!values.has(flag)) {
      throw new Error(`missing argument ${flag}`);
    }
  }
  return values;
}

function main() {
  const argumentsMap = parseArguments(process.argv);
  const vectorsRaw = readFileSync(argumentsMap.get("--vectors"));
  const vectors = JSON.parse(vectorsRaw.toString("utf-8"));
  if (vectors.suite_id !== SUITE_ID || vectors.answer_free !== true) {
    throw new Error("vector file identity is not the answer-free corpus");
  }
  const rows = [];
  let accepted = 0;
  let refused = 0;
  for (const frame of vectors.frames) {
    const raw = Buffer.from(frame.raw_hex, "hex");
    try {
      const document = parseFrame(raw);
      const canonical = Buffer.from(canonicalize(document), "utf-8");
      accepted += 1;
      rows.push({
        frame_id: frame.frame_id,
        disposition: "accepted",
        canonical_hex: canonical.toString("hex"),
        canonical_sha256: sha256(canonical),
        canonical_byte_count_decimal: String(canonical.length),
      });
    } catch (error) {
      if (!(error instanceof Refusal)) {
        throw error;
      }
      refused += 1;
      rows.push({
        frame_id: frame.frame_id,
        disposition: "refused",
        refusal_code: error.code,
      });
    }
  }
  const projection = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002g_jcs_conformance_projection",
    suite_id: SUITE_ID,
    vectors_binding: {
      raw_sha256: sha256(vectorsRaw),
      frame_count_decimal: String(rows.length),
    },
    census: {
      accepted_count_decimal: String(accepted),
      refused_count_decimal: String(refused),
    },
    frames: rows,
    claim_boundary: {
      profile_bounded_integer_scope_only: true,
      general_binary64_serialization_proven: false,
      product_digest_computed: false,
      profile_issued: false,
      gate_a_complete: false,
      publication_authorized: false,
    },
  };
  const projectionBytes = Buffer.from(emit(projection), "utf-8");
  const result = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002g_jcs_conformance_result",
    suite_id: SUITE_ID,
    implementation_id: IMPLEMENTATION_ID,
    implementation_role: "node",
    projection_sha256: sha256(projectionBytes),
    projection,
  };
  process.stdout.write(Buffer.from(emit(result), "utf-8"));
  return 0;
}

// Never call process.exit() after writing: stdout to a pipe flushes
// asynchronously and an immediate exit truncates the emitted document.
process.exitCode = main();
