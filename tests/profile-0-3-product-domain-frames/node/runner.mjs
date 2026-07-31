// PRQ-002H nine-domain frame governance runner (Node.js path).
//
// Source-separated peer of the CPython runner: parses every frame with its
// own recursive-descent reader (never JSON.parse), evaluates it against its
// governing product schema through a closed-vocabulary evaluator over the
// exact twelve-schema cohort, traces every governed raw number token to its
// unique RFC 6901 pointer and exactly one final rule, and reserves
// acceptance for frames byte-identical to the retained frozen
// structural-nonidentity fixture of their domain. Zero third-party
// dependencies; never reads the private expectation file. Bounded
// architecture evidence only.

import { createHash } from "node:crypto";
import { readFileSync, lstatSync } from "node:fs";
import { join } from "node:path";
import process from "node:process";

const SCHEMA_VERSION = "0.1.0";
const SUITE_ID = "prq-002h-product-domain-frames.0001";
const IMPLEMENTATION_ID = "nodejs-native-domain-governor.0001";
const MIN_SAFE = -9007199254740991n;
const MAX_SAFE = 9007199254740991n;
const FINAL_RULE_PRECEDENCE = [
  "recursive_integer_valued_const_leaf",
  "integer_type",
];
const FIXTURE_DIR =
  "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity";

const SCHEMA_ROWS = [
  ["schemas/schema-resource-record-v0-2.schema.json", "urn:odeya:schema:schema-resource-record:0.2.0"],
  ["schemas/aggregate-state-subject-record-v0-2.schema.json", "urn:odeya:schema:aggregate-state-subject-record:0.2.0"],
  ["schemas/reducer-contract-record-v0-2.schema.json", "urn:odeya:schema:reducer-contract-record:0.2.0"],
  ["schemas/event-contract-record-v0-2.schema.json", "urn:odeya:schema:event-contract-record:0.2.0"],
  ["schemas/ordered-member-map-commitment-v0-2.schema.json", "urn:odeya:schema:ordered-member-map-commitment:0.2.0"],
  ["schemas/schema-registry-v0-9.schema.json", "urn:odeya:schema:schema-registry:0.9.0"],
  ["schemas/aggregate-state-subject-registry-v0-8.schema.json", "urn:odeya:schema:aggregate-state-subject-registry:0.8.0"],
  ["schemas/reducer-registry-v0-8.schema.json", "urn:odeya:schema:reducer-registry:0.8.0"],
  ["schemas/event-contract-registry-v0-8.schema.json", "urn:odeya:schema:event-contract-registry:0.8.0"],
  ["schemas/canonicalization-profile-core-v0-7.schema.json", "urn:odeya:schema:canonicalization-profile-core:0.7.0"],
  ["schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json", "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0"],
  ["schemas/canonicalization-profile-migration-v0-2.schema.json", "urn:odeya:schema:canonicalization-profile-migration:0.2.0"],
];
const DOMAIN_ROWS = [
  ["schema_resource_record", "schema-resource-record-v0-2", "urn:odeya:schema:schema-resource-record:0.2.0"],
  ["aggregate_state_subject_record", "aggregate-state-subject-record-v0-2", "urn:odeya:schema:aggregate-state-subject-record:0.2.0"],
  ["reducer_contract_record", "reducer-contract-record-v0-2", "urn:odeya:schema:reducer-contract-record:0.2.0"],
  ["event_contract_record", "event-contract-record-v0-2", "urn:odeya:schema:event-contract-record:0.2.0"],
  ["ordered_member_map_commitment", "ordered-member-map-commitment-v0-2", "urn:odeya:schema:ordered-member-map-commitment:0.2.0"],
  ["schema_registry", "schema-registry-v0-9", "urn:odeya:schema:schema-registry:0.9.0"],
  ["aggregate_state_subject_registry", "aggregate-state-subject-registry-v0-8", "urn:odeya:schema:aggregate-state-subject-registry:0.8.0"],
  ["reducer_registry", "reducer-registry-v0-8", "urn:odeya:schema:reducer-registry:0.8.0"],
  ["event_contract_registry", "event-contract-registry-v0-8", "urn:odeya:schema:event-contract-registry:0.8.0"],
];
const APPLICATOR_KEYWORDS = new Set([
  "$ref", "allOf", "if", "then", "else", "items", "prefixItems",
  "properties", "additionalProperties", "$defs",
]);
const ASSERTION_KEYWORDS = new Set([
  "type", "const", "enum", "required", "pattern", "maximum", "minimum",
  "maxItems", "minItems", "maxLength", "minLength", "uniqueItems",
]);
const ANNOTATION_KEYWORDS = new Set([
  "$schema", "$id", "title", "description", "format",
  "x-odeya-digest-scope", "x-odeya-number-token-policy",
]);
const CLOSED_VOCABULARY = new Set([
  ...APPLICATOR_KEYWORDS, ...ASSERTION_KEYWORDS, ...ANNOTATION_KEYWORDS,
]);

class Refusal extends Error {
  constructor(code, detail) {
    super(detail ?? code);
    this.code = code;
    this.detail = detail ?? code;
  }
}
class FrameRefusal extends Error {
  constructor(code) {
    super(code);
    this.code = code;
  }
}
function refuse(code, detail) {
  throw new Refusal(code, detail);
}
function frameRefuse(code) {
  throw new FrameRefusal(code);
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
    if (this.map.has(key)) return false;
    this.keys.push(key);
    this.map.set(key, value);
    return true;
  }
  has(key) {
    return this.map.has(key);
  }
  get(key) {
    return this.map.get(key);
  }
}
function isInt(v) {
  return v instanceof JInt;
}
function isObj(v) {
  return v instanceof JObj;
}

class Parser {
  constructor(text) {
    this.text = text;
    this.index = 0;
    this.numberLexemes = [];
  }
  fail() {
    frameRefuse("malformed_json");
  }
  skipWhitespace() {
    while (this.index < this.text.length) {
      const ch = this.text[this.index];
      if (ch === " " || ch === "\t" || ch === "\n" || ch === "\r") this.index += 1;
      else break;
    }
  }
  parseDocument() {
    this.skipWhitespace();
    if (this.index >= this.text.length) this.fail();
    const value = this.parseValue();
    this.skipWhitespace();
    if (this.index !== this.text.length) frameRefuse("trailing_content");
    return value;
  }
  parseValue() {
    const ch = this.text[this.index];
    if (ch === "{") return this.parseObject();
    if (ch === "[") return this.parseArray();
    if (ch === '"') return this.parseString();
    if (this.text.startsWith("NaN", this.index)) frameRefuse("non_finite_literal");
    if (this.text.startsWith("Infinity", this.index)) frameRefuse("non_finite_literal");
    if (this.text.startsWith("-Infinity", this.index)) frameRefuse("non_finite_literal");
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
      if (!object.set(key, value)) frameRefuse("duplicate_decoded_member_name");
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
                frameRefuse("unpaired_surrogate");
              }
              this.index += 6;
              result += String.fromCodePoint(
                0x10000 + (code - 0xd800) * 0x400 + (lowCode - 0xdc00),
              );
            } else {
              frameRefuse("unpaired_surrogate");
            }
          } else if (code >= 0xdc00 && code <= 0xdfff) {
            frameRefuse("unpaired_surrogate");
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
      frameRefuse("non_integer_number_token");
    }
    if (lexeme.startsWith("-0")) frameRefuse("lexical_negative_zero");
    const value = BigInt(lexeme);
    if (value < MIN_SAFE || value > MAX_SAFE) {
      frameRefuse("integer_outside_safe_range");
    }
    this.numberLexemes.push(lexeme);
    return new JInt(lexeme);
  }
}

function scanStrings(value) {
  if (typeof value === "string") {
    for (const character of value) {
      const codePoint = character.codePointAt(0);
      if (codePoint >= 0xd800 && codePoint <= 0xdfff) {
        frameRefuse("unpaired_surrogate");
      }
      if (
        (codePoint >= 0xfdd0 && codePoint <= 0xfdef) ||
        (codePoint & 0xffff) === 0xfffe ||
        (codePoint & 0xffff) === 0xffff
      ) {
        frameRefuse("unicode_noncharacter");
      }
    }
    return;
  }
  if (isObj(value)) {
    for (const key of value.keys) {
      scanStrings(key);
      scanStrings(value.get(key));
    }
  } else if (Array.isArray(value)) {
    for (const child of value) scanStrings(child);
  }
}

function parseFrame(raw) {
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
    frameRefuse("leading_byte_order_mark");
  }
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(raw);
  } catch {
    frameRefuse("invalid_utf8_encoding");
  }
  const parser = new Parser(text);
  const document = parser.parseDocument();
  scanStrings(document);
  return { document, numberLexemes: parser.numberLexemes };
}

function pointerEscape(token) {
  return token.replaceAll("~", "~0").replaceAll("/", "~1");
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

function emit(value) {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (isInt(value)) return value.lexeme;
  if (typeof value === "string") return escapeString(value);
  if (Array.isArray(value)) return "[" + value.map(emit).join(",") + "]";
  if (isObj(value)) {
    return (
      "{" +
      value.keys
        .map((key) => escapeString(key) + ":" + emit(value.get(key)))
        .join(",") +
      "}"
    );
  }
  if (typeof value === "object") {
    return (
      "{" +
      Object.keys(value)
        .map((key) => escapeString(key) + ":" + emit(value[key]))
        .join(",") +
      "}"
    );
  }
  frameRefuse("malformed_json");
}

function* iterLocations(value, pointer = "") {
  yield [pointer, value];
  if (isObj(value)) {
    for (const key of value.keys) {
      yield* iterLocations(value.get(key), `${pointer}/${pointerEscape(key)}`);
    }
  } else if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      yield* iterLocations(value[index], `${pointer}/${index}`);
    }
  }
}

class ClosedEvaluator {
  constructor(byId) {
    this.byId = byId;
    this.applicable = new Map();
  }
  note(instancePointer, schemaId, digest, location, rule) {
    if (!this.applicable.has(instancePointer)) {
      this.applicable.set(instancePointer, []);
    }
    const rows = this.applicable.get(instancePointer);
    const row = {
      resolved_schema_id: schemaId,
      resolved_schema_raw_digest: digest,
      assertion_schema_location: location,
      position_rule: rule,
    };
    const marker = emit(row);
    if (!rows.some((existing) => emit(existing) === marker)) rows.push(row);
  }
  constMatches(expected, instance, instancePointer, schemaId, digest, location, relative = "") {
    if (isInt(expected)) {
      if (isInt(instance) && instance.lexeme === expected.lexeme) {
        this.note(
          instancePointer, schemaId, digest,
          `${location}${relative}`,
          "recursive_integer_valued_const_leaf",
        );
        return true;
      }
      return false;
    }
    if (
      expected === null || expected === true || expected === false ||
      typeof expected === "string"
    ) {
      return instance === expected;
    }
    if (isObj(expected)) {
      if (!isObj(instance)) return false;
      if (instance.keys.length !== expected.keys.length) return false;
      for (const key of expected.keys) {
        if (!instance.has(key)) return false;
      }
      return expected.keys.every((key) =>
        this.constMatches(
          expected.get(key), instance.get(key),
          `${instancePointer}/${pointerEscape(key)}`,
          schemaId, digest, location,
          `${relative}/${pointerEscape(key)}`,
        ),
      );
    }
    if (Array.isArray(expected)) {
      if (!Array.isArray(instance) || instance.length !== expected.length) {
        return false;
      }
      return expected.every((child, index) =>
        this.constMatches(
          child, instance[index], `${instancePointer}/${index}`,
          schemaId, digest, location, `${relative}/${index}`,
        ),
      );
    }
    return false;
  }
  resolvePointer(document, fragment) {
    if (fragment === "" || fragment === "#") return document;
    if (!fragment.startsWith("#/")) frameRefuse("out_of_cohort_reference");
    let current = document;
    for (const encoded of fragment.slice(2).split("/")) {
      const token = encoded.replaceAll("~1", "/").replaceAll("~0", "~");
      if (isObj(current) && current.has(token)) {
        current = current.get(token);
      } else if (Array.isArray(current)) {
        const index = Number.parseInt(token, 10);
        if (!Number.isInteger(index) || index < 0 || index >= current.length) {
          frameRefuse("out_of_cohort_reference");
        }
        current = current[index];
      } else {
        frameRefuse("out_of_cohort_reference");
      }
    }
    return current;
  }
  evaluate(schemaId, node, schemaPointer, instance, instancePointer, refStack, errors) {
    if (node === true) return true;
    if (node === false) {
      errors.push(`${instancePointer}: false schema`);
      return false;
    }
    if (!isObj(node)) {
      errors.push(`${instancePointer}: non-schema node`);
      return false;
    }
    const location = `${schemaId}#${schemaPointer}`;
    for (const key of node.keys) {
      if (!CLOSED_VOCABULARY.has(key)) frameRefuse("closed_vocabulary_violation");
    }
    const digest = sha256(this.byId.get(schemaId).raw);
    let valid = true;
    const reference = node.has("$ref") ? node.get("$ref") : undefined;
    if (typeof reference === "string") {
      const hashIndex = reference.indexOf("#");
      const targetBase =
        hashIndex === -1 ? reference : reference.slice(0, hashIndex);
      const resolvedId = targetBase === "" ? schemaId : targetBase;
      if (!this.byId.has(resolvedId)) frameRefuse("out_of_cohort_reference");
      const fragment = hashIndex === -1 ? "" : reference.slice(hashIndex);
      const refKey = `${resolvedId} ${fragment === "" ? "#" : fragment} ${instancePointer}`;
      if (refStack.includes(refKey)) frameRefuse("out_of_cohort_reference");
      const targetNode = this.resolvePointer(
        this.byId.get(resolvedId).document, fragment,
      );
      if (
        !this.evaluate(
          resolvedId, targetNode,
          fragment === "" ? "" : fragment.slice(1),
          instance, instancePointer,
          [...refStack, refKey], errors,
        )
      ) {
        valid = false;
      }
    }
    const nodeType = node.has("type") ? node.get("type") : undefined;
    if (nodeType !== undefined) {
      const allowed = Array.isArray(nodeType) ? nodeType : [nodeType];
      const matched =
        (allowed.includes("object") && isObj(instance)) ||
        (allowed.includes("array") && Array.isArray(instance)) ||
        (allowed.includes("string") && typeof instance === "string") ||
        (allowed.includes("boolean") &&
          (instance === true || instance === false)) ||
        (allowed.includes("integer") && isInt(instance)) ||
        (allowed.includes("null") && instance === null);
      if (!matched) {
        errors.push(`${instancePointer}: type mismatch at ${location}`);
        valid = false;
      }
      if (allowed.includes("integer") && isInt(instance)) {
        this.note(instancePointer, schemaId, digest, `${location}/type`, "integer_type");
      }
    }
    if (node.has("const")) {
      if (
        !this.constMatches(
          node.get("const"), instance, instancePointer, schemaId, digest,
          `${location}/const`,
        )
      ) {
        errors.push(`${instancePointer}: const mismatch at ${location}`);
        valid = false;
      }
    }
    if (node.has("enum")) {
      const instanceMarker = emit(instance);
      if (!node.get("enum").some((member) => emit(member) === instanceMarker)) {
        errors.push(`${instancePointer}: enum mismatch at ${location}`);
        valid = false;
      }
    }
    if (typeof instance === "string") {
      const length = [...instance].length;
      if (node.has("minLength") && length < Number(node.get("minLength").lexeme)) {
        errors.push(`${instancePointer}: minLength at ${location}`);
        valid = false;
      }
      if (node.has("maxLength") && length > Number(node.get("maxLength").lexeme)) {
        errors.push(`${instancePointer}: maxLength at ${location}`);
        valid = false;
      }
      if (node.has("pattern")) {
        const expression = new RegExp(node.get("pattern"), "u");
        if (!expression.test(instance)) {
          errors.push(`${instancePointer}: pattern at ${location}`);
          valid = false;
        }
      }
    }
    if (isInt(instance)) {
      const value = BigInt(instance.lexeme);
      if (node.has("minimum") && value < BigInt(node.get("minimum").lexeme)) {
        errors.push(`${instancePointer}: minimum at ${location}`);
        valid = false;
      }
      if (node.has("maximum") && value > BigInt(node.get("maximum").lexeme)) {
        errors.push(`${instancePointer}: maximum at ${location}`);
        valid = false;
      }
    }
    if (Array.isArray(instance)) {
      if (node.has("minItems") && instance.length < Number(node.get("minItems").lexeme)) {
        errors.push(`${instancePointer}: minItems at ${location}`);
        valid = false;
      }
      if (node.has("maxItems") && instance.length > Number(node.get("maxItems").lexeme)) {
        errors.push(`${instancePointer}: maxItems at ${location}`);
        valid = false;
      }
      if (node.has("uniqueItems") && node.get("uniqueItems") === true) {
        const markers = instance.map((item) => emit(item));
        if (new Set(markers).size !== markers.length) {
          errors.push(`${instancePointer}: uniqueItems at ${location}`);
          valid = false;
        }
      }
      const prefix = node.has("prefixItems") ? node.get("prefixItems") : undefined;
      let prefixLength = 0;
      if (Array.isArray(prefix)) {
        prefixLength = prefix.length;
        for (let index = 0; index < prefix.length && index < instance.length; index += 1) {
          if (
            !this.evaluate(
              schemaId, prefix[index],
              `${schemaPointer}/prefixItems/${index}`,
              instance[index], `${instancePointer}/${index}`,
              refStack, errors,
            )
          ) {
            valid = false;
          }
        }
      }
      if (node.has("items")) {
        const items = node.get("items");
        if (items === false) {
          if (instance.length > prefixLength) {
            errors.push(`${instancePointer}: items false at ${location}`);
            valid = false;
          }
        } else {
          for (let index = prefixLength; index < instance.length; index += 1) {
            if (
              !this.evaluate(
                schemaId, items, `${schemaPointer}/items`,
                instance[index], `${instancePointer}/${index}`,
                refStack, errors,
              )
            ) {
              valid = false;
            }
          }
        }
      }
    }
    if (isObj(instance)) {
      const required = node.has("required") ? node.get("required") : undefined;
      if (Array.isArray(required)) {
        for (const name of required) {
          if (!instance.has(name)) {
            errors.push(
              `${instancePointer}: missing required ${JSON.stringify(name)} at ${location}`,
            );
            valid = false;
          }
        }
      }
      const properties = node.has("properties") ? node.get("properties") : undefined;
      const declared = new Set(isObj(properties) ? properties.keys : []);
      if (isObj(properties)) {
        for (const name of properties.keys) {
          if (instance.has(name)) {
            if (
              !this.evaluate(
                schemaId, properties.get(name),
                `${schemaPointer}/properties/${pointerEscape(name)}`,
                instance.get(name),
                `${instancePointer}/${pointerEscape(name)}`,
                refStack, errors,
              )
            ) {
              valid = false;
            }
          }
        }
      }
      if (node.has("additionalProperties")) {
        const additional = node.get("additionalProperties");
        for (const name of instance.keys) {
          if (declared.has(name)) continue;
          if (additional === false) {
            errors.push(
              `${instancePointer}: additional property ${JSON.stringify(name)} at ${location}`,
            );
            valid = false;
          } else if (
            !this.evaluate(
              schemaId, additional,
              `${schemaPointer}/additionalProperties`,
              instance.get(name),
              `${instancePointer}/${pointerEscape(name)}`,
              refStack, errors,
            )
          ) {
            valid = false;
          }
        }
      }
    }
    const allOf = node.has("allOf") ? node.get("allOf") : undefined;
    if (Array.isArray(allOf)) {
      allOf.forEach((subschema, index) => {
        if (
          !this.evaluate(
            schemaId, subschema, `${schemaPointer}/allOf/${index}`,
            instance, instancePointer, refStack, errors,
          )
        ) {
          valid = false;
        }
      });
    }
    if (node.has("if")) {
      const silent = [];
      const condition = this.evaluate(
        schemaId, node.get("if"), `${schemaPointer}/if`,
        instance, instancePointer, refStack, silent,
      );
      const branch = condition ? "then" : "else";
      if (node.has(branch)) {
        if (
          !this.evaluate(
            schemaId, node.get(branch), `${schemaPointer}/${branch}`,
            instance, instancePointer, refStack, errors,
          )
        ) {
          valid = false;
        }
      }
    }
    return valid;
  }
}

function loadRepositoryFile(root, relative) {
  const target = join(root, relative);
  const stat = lstatSync(target, { throwIfNoEntry: false });
  if (stat === undefined || !stat.isFile() || stat.isSymbolicLink()) {
    refuse("corpus_census_mismatch", `${relative}: not a regular repository file`);
  }
  return readFileSync(target);
}

function parseArguments(argv) {
  const values = new Map();
  for (let index = 2; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (
      value === undefined ||
      !["--repository-root", "--vectors", "--source-manifest"].includes(flag)
    ) {
      throw new Error(`unsupported argument ${flag}`);
    }
    values.set(flag, value);
  }
  for (const flag of ["--repository-root", "--vectors", "--source-manifest"]) {
    if (!values.has(flag)) throw new Error(`missing argument ${flag}`);
  }
  return values;
}

function main() {
  const argumentsMap = parseArguments(process.argv);
  const root = argumentsMap.get("--repository-root");

  const byId = new Map();
  for (const [relative, schemaId] of SCHEMA_ROWS) {
    const raw = loadRepositoryFile(root, relative);
    const { document } = parseFrame(raw);
    if (!isObj(document) || document.get("$id") !== schemaId) {
      refuse("corpus_census_mismatch", `${relative}: schema $id drift`);
    }
    byId.set(schemaId, { document, raw });
  }
  const fixtures = new Map();
  for (const [domain, slug, governingId] of DOMAIN_ROWS) {
    const relative = `${FIXTURE_DIR}/prq-002e-${slug}.structural-nonidentity.json`;
    fixtures.set(domain, {
      raw: loadRepositoryFile(root, relative),
      governingId,
    });
  }

  const vectorsRaw = readFileSync(argumentsMap.get("--vectors"));
  const vectors = JSON.parse(vectorsRaw.toString("utf-8"));
  if (vectors.suite_id !== SUITE_ID || vectors.answer_free !== true) {
    refuse("corpus_census_mismatch", "vector file identity differs");
  }

  const rows = [];
  let accepted = 0;
  let refusedCount = 0;
  for (const frame of vectors.frames) {
    const domain = frame.domain;
    if (!fixtures.has(domain)) {
      refuse("corpus_census_mismatch", `${frame.frame_id}: unknown domain`);
    }
    const { raw: fixtureRaw, governingId } = fixtures.get(domain);
    const raw = Buffer.from(frame.raw_hex, "hex");
    try {
      const { document, numberLexemes } = parseFrame(raw);
      const evaluator = new ClosedEvaluator(byId);
      const errors = [];
      if (
        !evaluator.evaluate(
          governingId, byId.get(governingId).document, "", document, "",
          [`${governingId} # `], errors,
        )
      ) {
        frameRefuse("record_schema_validation_failed");
      }
      const located = [];
      for (const [pointer, value] of iterLocations(document)) {
        if (isInt(value)) located.push({ pointer, lexeme: value.lexeme });
      }
      if (
        located.length !== numberLexemes.length ||
        located.some((row, index) => row.lexeme !== numberLexemes[index])
      ) {
        frameRefuse("malformed_json");
      }
      const tokens = [];
      for (const token of located) {
        const applicable = evaluator.applicable.get(token.pointer) ?? [];
        if (applicable.length === 0) {
          frameRefuse("unclassified_instance_numeric_position");
        }
        const rules = new Set(applicable.map((entry) => entry.position_rule));
        for (const rule of rules) {
          if (!FINAL_RULE_PRECEDENCE.includes(rule)) {
            frameRefuse("multiply_classified_instance_position");
          }
        }
        const finalRule = rules.has(FINAL_RULE_PRECEDENCE[0])
          ? FINAL_RULE_PRECEDENCE[0]
          : FINAL_RULE_PRECEDENCE[1];
        tokens.push({
          ordinal_decimal: String(tokens.length),
          raw_lexeme: token.lexeme,
          decimal_value: token.lexeme,
          instance_pointer: token.pointer,
          classification: {
            final_rule: finalRule,
            applicable_assertions: applicable,
          },
        });
      }
      if (!raw.equals(fixtureRaw)) {
        frameRefuse("fixture_byte_binding_mismatch");
      }
      accepted += 1;
      rows.push({
        frame_id: frame.frame_id,
        domain,
        disposition: "accepted",
        governing_schema_id: governingId,
        governing_schema_raw_digest: sha256(byId.get(governingId).raw),
        raw_sha256: sha256(raw),
        byte_count_decimal: String(raw.length),
        token_count_decimal: String(tokens.length),
        tokens,
      });
    } catch (error) {
      if (!(error instanceof FrameRefusal)) throw error;
      refusedCount += 1;
      rows.push({
        frame_id: frame.frame_id,
        domain,
        disposition: "refused",
        refusal_code: error.code,
      });
    }
  }
  const projection = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002h_product_domain_frame_projection",
    suite_id: SUITE_ID,
    vectors_binding: {
      raw_sha256: sha256(vectorsRaw),
      frame_count_decimal: String(rows.length),
    },
    census: {
      domain_count_decimal: String(DOMAIN_ROWS.length),
      accepted_count_decimal: String(accepted),
      refused_count_decimal: String(refusedCount),
    },
    frames: rows,
    claim_boundary: {
      governed_instances_are_structural_nonidentity_fixtures_only: true,
      product_identity_computed: false,
      product_digest_computed: false,
      profile_issued: false,
      prq_002_closed: false,
      gate_a_complete: false,
      publication_authorized: false,
    },
  };
  const projectionBytes = Buffer.from(emit(projection), "utf-8");
  const result = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002h_product_domain_frame_result",
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
try {
  process.exitCode = main();
} catch (error) {
  if (error instanceof Refusal) {
    process.stdout.write(
      Buffer.from(
        emit({
          schema_version: SCHEMA_VERSION,
          artifact_class: "prq_002h_product_domain_frame_refusal",
          suite_id: SUITE_ID,
          implementation_id: IMPLEMENTATION_ID,
          refusal_code: error.code,
          detail: error.detail,
        }),
        "utf-8",
      ),
    );
    process.exitCode = 1;
  } else {
    throw error;
  }
}
