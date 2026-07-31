// PRQ-002F raw-aware numeric trace conformance runner (Node.js path).
//
// Source-separated peer of the CPython runner: this implementation parses
// every subject with its own recursive-descent JSON reader (never JSON.parse,
// which silently drops duplicate member names), recomputes the static
// numeric-position inventory of the twelve final odeya-jcs-0.3 schemas from
// raw bytes, settles schema-document versus metaschema treatment as an
// explicit typed disposition, constructs complete raw-aware applicability
// traces for the fifteen frozen construction subjects, and executes one
// complete cross-object conformance path over the exact cohort. Zero
// third-party dependencies. It never reads the peer source, the peer result,
// or the suite's private expectations.
//
// Any violation refuses the whole projection with exactly one declared
// refusal code on stdout and exit status 1. Success emits one deterministic
// result document on stdout and exit status 0. Bounded architecture evidence
// only: no conformance beyond the fifteen subjects, no product identity, no
// profile issuance, no PRQ-002 closure, no Gate A acceptance, and no runtime
// or publication authority follows.

import { createHash } from "node:crypto";
import { readFileSync, lstatSync } from "node:fs";
import { join } from "node:path";
import process from "node:process";

const SCHEMA_VERSION = "0.1.0";
const SUITE_ID = "prq-002f-numeric-trace-conformance.0001";
const IMPLEMENTATION_ID = "nodejs-native-numeric-trace.0001";
const CONTRACT_PATH =
  "architecture/prq-002f-numeric-trace-conformance-contract-v1-candidate.json";
const PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.3";
const RAW_NUMBER_CONTRACT_ID =
  "urn:odeya:canonicalization:raw-number-token-contract:0.1.0";
const MIN_SAFE_INTEGER = -9007199254740991n;
const MAX_SAFE_INTEGER = 9007199254740991n;
const SCHEMA_DOCUMENT_TOKEN_RULE =
  "schema_definition_data_not_instance_position";
const METASCHEMA_DISPOSITION = "blocked_out_of_cohort_metaschema_not_retained";
const FINAL_RULE_PRECEDENCE = [
  "recursive_integer_valued_const_leaf",
  "integer_type",
];

// The complete fifteen-row subject census is hard-coded here, independently
// of the shared input manifest and of the Python implementation, so a
// mutation of one shared file cannot become two-implementation consensus.
// Row: [role, path, rawSha256, byteCountDecimal, schemaId, kind, governing]
const SUBJECT_ROWS = [
  [
    "schema_resource_record_schema",
    "schemas/schema-resource-record-v0-2.schema.json",
    "sha256:9e7dc959e8d764e0665d36e8e45af9102cc837ebf35f87a5e3591766db0689a9",
    "9420",
    "urn:odeya:schema:schema-resource-record:0.2.0",
    "schema_document",
    null,
  ],
  [
    "aggregate_state_subject_record_schema",
    "schemas/aggregate-state-subject-record-v0-2.schema.json",
    "sha256:6e0b10755f32795cb71eebd4cd627921563bda8f333367a59b0ebb61723a73e0",
    "17537",
    "urn:odeya:schema:aggregate-state-subject-record:0.2.0",
    "schema_document",
    null,
  ],
  [
    "reducer_contract_record_schema",
    "schemas/reducer-contract-record-v0-2.schema.json",
    "sha256:18f5e6f866ac2add6d4620dd6f2a5473ca5b8d150f11d81e5ce6896c46639523",
    "19324",
    "urn:odeya:schema:reducer-contract-record:0.2.0",
    "schema_document",
    null,
  ],
  [
    "event_contract_record_schema",
    "schemas/event-contract-record-v0-2.schema.json",
    "sha256:3bae0e8f44e0b88b6e467c789db75aa1d4ddfbbb27aada9221d7b7cacc4c3d2c",
    "13937",
    "urn:odeya:schema:event-contract-record:0.2.0",
    "schema_document",
    null,
  ],
  [
    "ordered_member_map_commitment_schema",
    "schemas/ordered-member-map-commitment-v0-2.schema.json",
    "sha256:d672627e678ab5149bc27d2a2a6833823978975057a74593deb34775790a56ac",
    "10712",
    "urn:odeya:schema:ordered-member-map-commitment:0.2.0",
    "schema_document",
    null,
  ],
  [
    "schema_registry_schema",
    "schemas/schema-registry-v0-9.schema.json",
    "sha256:914dc00de6caad731b776eab7b99bfe573a8fab1211d12f366a986aff4acb4df",
    "7703",
    "urn:odeya:schema:schema-registry:0.9.0",
    "schema_document",
    null,
  ],
  [
    "aggregate_state_subject_registry_schema",
    "schemas/aggregate-state-subject-registry-v0-8.schema.json",
    "sha256:a04c6ea24414dcb6279d73b6583f45bab90c53264737d8a95e12afd227a7dc8c",
    "7931",
    "urn:odeya:schema:aggregate-state-subject-registry:0.8.0",
    "schema_document",
    null,
  ],
  [
    "reducer_registry_schema",
    "schemas/reducer-registry-v0-8.schema.json",
    "sha256:ca919c845a555c6e336d0f750038a7415e6d54c714c0374ebc31a75e172e36ce",
    "7716",
    "urn:odeya:schema:reducer-registry:0.8.0",
    "schema_document",
    null,
  ],
  [
    "event_contract_registry_schema",
    "schemas/event-contract-registry-v0-8.schema.json",
    "sha256:b2895f003ed4c56fe8cd4037386b343daabb91e46bf5b214912e3727ce39cafd",
    "7806",
    "urn:odeya:schema:event-contract-registry:0.8.0",
    "schema_document",
    null,
  ],
  [
    "profile_core_schema",
    "schemas/canonicalization-profile-core-v0-7.schema.json",
    "sha256:47b726f0c4a62870567a5c2228d7510e86fc3e28f100bdd62962f35d39b8e330",
    "219537",
    "urn:odeya:schema:canonicalization-profile-core:0.7.0",
    "schema_document",
    null,
  ],
  [
    "profile_evidence_schema",
    "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json",
    "sha256:3f01f5902b6d0a52aa12dd638b225784559379dba3b64f65e97bd2f3fa7fbe64",
    "185844",
    "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0",
    "schema_document",
    null,
  ],
  [
    "profile_migration_schema",
    "schemas/canonicalization-profile-migration-v0-2.schema.json",
    "sha256:3573eba7ddd9209e9d3039282a8db41db031a267ea0b9003edd8ca7ddd5ab217",
    "64569",
    "urn:odeya:schema:canonicalization-profile-migration:0.2.0",
    "schema_document",
    null,
  ],
  [
    "profile_core",
    "architecture/canonicalization-profile-core-0.3-candidate.json",
    "sha256:d91a7e53b1f729c0750646c8131701187911e5ffbde03897ef81ba0197e31562",
    "790376",
    null,
    "record_instance",
    "profile_core_schema",
  ],
  [
    "profile_evidence",
    "architecture/canonicalization-profile-0.3-candidate-evidence.json",
    "sha256:e53d953481279368159499811e958756d5fa89479828b24a03fcbc0256b2ee4e",
    "778908",
    null,
    "record_instance",
    "profile_evidence_schema",
  ],
  [
    "profile_migration",
    "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json",
    "sha256:6ae5640d8b92b26038a1feb1772a615a476223f392e8f55595903f954eacab37",
    "25869",
    null,
    "record_instance",
    "profile_migration_schema",
  ],
];

const SCHEMA_BINDING_IDS = [
  "schema_resource_record",
  "aggregate_state_subject_record",
  "reducer_contract_record",
  "event_contract_record",
  "ordered_member_map_commitment",
  "schema_registry_v0_9",
  "aggregate_state_subject_registry_v0_8",
  "reducer_registry_v0_8",
  "event_contract_registry_v0_8",
  "canonicalization_profile_core_v0_7",
  "canonicalization_profile_candidate_evidence_v0_7",
  "canonicalization_profile_migration_v0_2",
];
const EXPECTED_GRAPH_NODES = [
  ...SCHEMA_BINDING_IDS,
  "successor_profile_core_artifact",
  "successor_profile_evidence_artifact",
  "successor_profile_migration_artifact",
];
const EXPECTED_GRAPH_EDGES = [
  ["schema_registry_v0_9", "ordered_member_map_commitment"],
  ["aggregate_state_subject_registry_v0_8", "ordered_member_map_commitment"],
  ["reducer_registry_v0_8", "ordered_member_map_commitment"],
  ["event_contract_registry_v0_8", "ordered_member_map_commitment"],
  ...SCHEMA_BINDING_IDS.map((node) => [
    "successor_profile_core_artifact",
    node,
  ]),
  ["successor_profile_evidence_artifact", "successor_profile_core_artifact"],
  [
    "successor_profile_migration_artifact",
    "successor_profile_evidence_artifact",
  ],
];

const APPLICATOR_KEYWORDS = new Set([
  "$ref",
  "allOf",
  "if",
  "then",
  "else",
  "items",
  "prefixItems",
  "properties",
  "additionalProperties",
  "$defs",
]);
const ASSERTION_KEYWORDS = new Set([
  "type",
  "const",
  "enum",
  "required",
  "pattern",
  "maximum",
  "minimum",
  "maxItems",
  "minItems",
  "maxLength",
  "minLength",
  "uniqueItems",
]);
const ANNOTATION_KEYWORDS = new Set([
  "$schema",
  "$id",
  "title",
  "description",
  "format",
  "x-odeya-digest-scope",
  "x-odeya-number-token-policy",
]);
const CLOSED_VOCABULARY = new Set([
  ...APPLICATOR_KEYWORDS,
  ...ASSERTION_KEYWORDS,
  ...ANNOTATION_KEYWORDS,
]);

class Refusal extends Error {
  constructor(code, detail) {
    super(detail);
    this.code = code;
    this.detail = detail;
  }
}

function refuse(code, detail) {
  throw new Refusal(code, detail);
}

function sha256(raw) {
  return "sha256:" + createHash("sha256").update(raw).digest("hex");
}

// JInt models a JSON integer as a BigInt so lexical fidelity survives; JObj
// models an object as an insertion-ordered member list with duplicate
// detection at parse time.
class JInt {
  constructor(lexeme) {
    this.lexeme = lexeme;
    this.value = BigInt(lexeme);
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
  has(key) {
    return this.map.has(key);
  }
  get(key) {
    return this.map.get(key);
  }
}

function isInt(value) {
  return value instanceof JInt;
}

function isObj(value) {
  return value instanceof JObj;
}

// Recursive-descent JSON parser over the decoded text. Refuses duplicate
// member names, any non-integer number lexeme, negative zero, out-of-range
// integers, and trailing content. Records every number lexeme in document
// order.
class Parser {
  constructor(text, subject) {
    this.text = text;
    this.subject = subject;
    this.index = 0;
    this.numberLexemes = [];
  }
  error(detail) {
    refuse(
      "subject_byte_binding_mismatch",
      `${this.subject}: invalid JSON: ${detail} at ${this.index}`,
    );
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
    const value = this.parseValue();
    this.skipWhitespace();
    if (this.index !== this.text.length) {
      this.error("trailing content");
    }
    return value;
  }
  parseValue() {
    const ch = this.text[this.index];
    if (ch === "{") {
      return this.parseObject();
    }
    if (ch === "[") {
      return this.parseArray();
    }
    if (ch === '"') {
      return this.parseString();
    }
    if (ch === "-" || (ch >= "0" && ch <= "9")) {
      return this.parseNumber();
    }
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
    this.error("unexpected character");
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
      if (this.text[this.index] !== '"') {
        this.error("expected member name");
      }
      const key = this.parseString();
      this.skipWhitespace();
      if (this.text[this.index] !== ":") {
        this.error("expected colon");
      }
      this.index += 1;
      this.skipWhitespace();
      const value = this.parseValue();
      if (!object.set(key, value)) {
        refuse(
          "raw_token_reconciliation_mismatch",
          `${this.subject}: duplicate decoded object member name: ${JSON.stringify(key)}`,
        );
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
      this.error("expected comma or object end");
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
      this.error("expected comma or array end");
    }
  }
  parseString() {
    let result = "";
    this.index += 1;
    for (;;) {
      if (this.index >= this.text.length) {
        this.error("unterminated string");
      }
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
          if (!/^[0-9A-Fa-f]{4}$/.test(hex)) {
            this.error("invalid unicode escape");
          }
          this.index += 4;
          const code = Number.parseInt(hex, 16);
          if (code >= 0xd800 && code <= 0xdbff) {
            if (
              this.text[this.index] === "\\" &&
              this.text[this.index + 1] === "u"
            ) {
              const low = this.text.slice(this.index + 2, this.index + 6);
              if (!/^[0-9A-Fa-f]{4}$/.test(low)) {
                this.error("invalid low surrogate escape");
              }
              const lowCode = Number.parseInt(low, 16);
              if (lowCode < 0xdc00 || lowCode > 0xdfff) {
                this.error("unpaired high surrogate");
              }
              this.index += 6;
              result += String.fromCodePoint(
                0x10000 + (code - 0xd800) * 0x400 + (lowCode - 0xdc00),
              );
            } else {
              this.error("unpaired high surrogate");
            }
          } else if (code >= 0xdc00 && code <= 0xdfff) {
            this.error("unpaired low surrogate");
          } else {
            result += String.fromCharCode(code);
          }
        } else {
          this.error("invalid escape");
        }
        continue;
      }
      const codePoint = ch.codePointAt(0);
      if (codePoint < 0x20) {
        this.error("unescaped control character");
      }
      result += String.fromCodePoint(codePoint);
      this.index += ch.length > 1 ? 2 : codePoint > 0xffff ? 2 : 1;
      if (codePoint > 0xffff) {
        // fromCodePoint consumed a surrogate pair from the source text.
      }
    }
  }
  parseNumber() {
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(
      this.text.slice(this.index),
    );
    if (match === null) {
      this.error("malformed number");
    }
    const lexeme = match[0];
    this.index += lexeme.length;
    if (!/^-?(?:0|[1-9][0-9]*)$/.test(lexeme)) {
      refuse(
        "raw_token_policy_violation",
        `${this.subject}: non-integer raw number token: ${lexeme}`,
      );
    }
    if (lexeme.startsWith("-0")) {
      refuse(
        "raw_token_policy_violation",
        `${this.subject}: lexical negative zero ${lexeme}`,
      );
    }
    const value = BigInt(lexeme);
    if (value < MIN_SAFE_INTEGER || value > MAX_SAFE_INTEGER) {
      refuse(
        "raw_token_policy_violation",
        `${this.subject}: raw integer outside safe range ${lexeme}`,
      );
    }
    this.numberLexemes.push(lexeme);
    return new JInt(lexeme);
  }
}

function decodeStrict(raw, subject) {
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
    refuse("subject_byte_binding_mismatch", `${subject}: leading BOM`);
  }
  const decoder = new TextDecoder("utf-8", { fatal: true });
  try {
    return decoder.decode(raw);
  } catch (error) {
    refuse(
      "subject_byte_binding_mismatch",
      `${subject}: invalid UTF-8: ${error.message}`,
    );
  }
}

function pointerEscape(token) {
  return token.replaceAll("~", "~0").replaceAll("/", "~1");
}

// Compact serializer matching the Python reference byte-for-byte for the
// document model: JObj keys in insertion order, JInt as its exact lexeme,
// strings escaped like json.dumps(ensure_ascii=False).
function escapeString(value) {
  let out = '"';
  for (const ch of value) {
    const code = ch.codePointAt(0);
    if (ch === '"') out += '\\"';
    else if (ch === "\\") out += "\\\\";
    else if (ch === "\n") out += "\\n";
    else if (ch === "\r") out += "\\r";
    else if (ch === "\t") out += "\\t";
    else if (ch === "\b") out += "\\b";
    else if (ch === "\f") out += "\\f";
    else if (code < 0x20) out += "\\u" + code.toString(16).padStart(4, "0");
    else out += ch;
  }
  return out + '"';
}

function serialize(value) {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (isInt(value)) return value.lexeme;
  if (typeof value === "number") {
    if (!Number.isInteger(value)) {
      refuse("census_decimal_typing_violation", "non-integer number in output");
    }
    return String(value);
  }
  if (typeof value === "string") return escapeString(value);
  if (Array.isArray(value)) {
    return "[" + value.map(serialize).join(",") + "]";
  }
  if (isObj(value)) {
    return (
      "{" +
      value.keys
        .map((key) => escapeString(key) + ":" + serialize(value.get(key)))
        .join(",") +
      "}"
    );
  }
  if (typeof value === "object") {
    return (
      "{" +
      Object.keys(value)
        .map((key) => escapeString(key) + ":" + serialize(value[key]))
        .join(",") +
      "}"
    );
  }
  refuse("census_decimal_typing_violation", "unserializable value");
}

function equalSerialized(left, right) {
  return serialize(left) === serialize(right);
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

function integerTokenRows(document, numberLexemes, subject) {
  const located = [];
  for (const [pointer, value] of iterLocations(document)) {
    if (isInt(value)) {
      located.push({ pointer, lexeme: value.lexeme });
    }
  }
  const walkLexemes = located.map((row) => row.lexeme);
  if (
    walkLexemes.length !== numberLexemes.length ||
    walkLexemes.some((lexeme, index) => lexeme !== numberLexemes[index])
  ) {
    refuse(
      "raw_token_reconciliation_mismatch",
      `${subject}: raw lexeme sequence differs from document walk`,
    );
  }
  const seen = new Set();
  for (const row of located) {
    if (seen.has(row.pointer)) {
      refuse(
        "duplicate_instance_pointer",
        `${subject}: duplicate RFC 6901 instance pointer`,
      );
    }
    seen.add(row.pointer);
  }
  return located.map((row, ordinal) => ({
    ordinal_decimal: String(ordinal),
    raw_lexeme: row.lexeme,
    decimal_value: row.lexeme,
    instance_pointer: row.pointer,
  }));
}

function resolvePointer(document, fragment, subject) {
  if (fragment === "" || fragment === "#") {
    return document;
  }
  if (!fragment.startsWith("#/")) {
    refuse(
      "out_of_cohort_reference",
      `${subject}: unsupported reference fragment ${fragment}`,
    );
  }
  let current = document;
  for (const encoded of fragment.slice(2).split("/")) {
    const token = encoded.replaceAll("~1", "/").replaceAll("~0", "~");
    if (isObj(current) && current.has(token)) {
      current = current.get(token);
    } else if (Array.isArray(current)) {
      const index = Number.parseInt(token, 10);
      if (!Number.isInteger(index) || index < 0 || index >= current.length) {
        refuse(
          "out_of_cohort_reference",
          `${subject}: unresolved fragment ${fragment}`,
        );
      }
      current = current[index];
    } else {
      refuse(
        "out_of_cohort_reference",
        `${subject}: unresolved fragment ${fragment}`,
      );
    }
  }
  return current;
}

function collectIntegerConstLeaves(value, schemaLocation) {
  const rows = [];
  for (const [relativePointer, child] of iterLocations(value)) {
    if (isInt(child)) {
      rows.push({
        schema_location: `${schemaLocation}${relativePointer}`,
        assertion_keyword: "const",
        position_rule: "recursive_integer_valued_const_leaf",
        decimal_value: child.lexeme,
      });
    }
  }
  return rows;
}

function typeOf(node) {
  return isObj(node) ? node.get("type") : undefined;
}

function typeIncludes(nodeType, name) {
  if (typeof nodeType === "string") return nodeType === name;
  if (Array.isArray(nodeType)) return nodeType.includes(name);
  return false;
}

function expandedNumericPositions(rootSchemaId, byId) {
  const integerTypes = [];
  const integerConsts = [];
  const unclassified = [];

  function appendConstLeaves(
    value,
    evaluationPath,
    resolvedSchemaId,
    resolvedDigest,
    keywordLocation,
    relativePointer = "",
  ) {
    if (isInt(value)) {
      integerConsts.push({
        evaluation_path: evaluationPath.map((step) => ({ ...step })),
        resolved_schema_id: resolvedSchemaId,
        resolved_schema_raw_digest: resolvedDigest,
        assertion_schema_location: keywordLocation,
        position_rule: "recursive_integer_valued_const_leaf",
        const_leaf_pointer: relativePointer,
        decimal_value: value.lexeme,
      });
      return;
    }
    if (isObj(value)) {
      for (const key of value.keys) {
        appendConstLeaves(
          value.get(key),
          [...evaluationPath, { kind: "const_object_member", token: key }],
          resolvedSchemaId,
          resolvedDigest,
          keywordLocation,
          `${relativePointer}/${pointerEscape(key)}`,
        );
      }
    } else if (Array.isArray(value)) {
      value.forEach((child, index) => {
        appendConstLeaves(
          child,
          [
            ...evaluationPath,
            { kind: "const_array_index", token: String(index) },
          ],
          resolvedSchemaId,
          resolvedDigest,
          keywordLocation,
          `${relativePointer}/${index}`,
        );
      });
    }
  }

  function descend(resolvedSchemaId, node, schemaPointer, evaluationPath, refStack) {
    if (node === true) {
      unclassified.push(`${resolvedSchemaId}#${schemaPointer}:true_schema`);
      return;
    }
    if (node === false || !isObj(node)) {
      return;
    }
    const resolvedDigest = sha256(byId.get(resolvedSchemaId).raw);
    const nodeType = typeOf(node);
    if (typeIncludes(nodeType, "integer")) {
      integerTypes.push({
        evaluation_path: evaluationPath.map((step) => ({ ...step })),
        resolved_schema_id: resolvedSchemaId,
        resolved_schema_raw_digest: resolvedDigest,
        assertion_schema_location: `${resolvedSchemaId}#${schemaPointer}/type`,
        position_rule: "integer_type",
      });
    }
    if (typeIncludes(nodeType, "number")) {
      unclassified.push(`${resolvedSchemaId}#${schemaPointer}/type`);
    }
    if (node.has("const")) {
      appendConstLeaves(
        node.get("const"),
        evaluationPath,
        resolvedSchemaId,
        resolvedDigest,
        `${resolvedSchemaId}#${schemaPointer}/const`,
      );
    }
    if (node.has("enum") && node.get("enum").some((item) => isInt(item))) {
      if (nodeType !== "integer") {
        unclassified.push(`${resolvedSchemaId}#${schemaPointer}/enum`);
      }
    }
    const reference = node.has("$ref") ? node.get("$ref") : undefined;
    if (typeof reference === "string") {
      const hashIndex = reference.indexOf("#");
      const targetBase =
        hashIndex === -1 ? reference : reference.slice(0, hashIndex);
      const targetId = targetBase === "" ? resolvedSchemaId : targetBase;
      if (!byId.has(targetId)) {
        refuse(
          "out_of_cohort_reference",
          `unresolved exact-cohort reference: ${reference}`,
        );
      }
      const fragment = hashIndex === -1 ? "" : reference.slice(hashIndex);
      const refKey = `${targetId} ${fragment === "" ? "#" : fragment}`;
      if (refStack.includes(refKey)) {
        refuse(
          "static_inventory_recomputation_mismatch",
          `numeric applicability reference cycle: ${reference}`,
        );
      }
      const targetDocument = byId.get(targetId).document;
      descend(
        targetId,
        resolvePointer(targetDocument, fragment, targetId),
        fragment === "" ? "" : fragment.slice(1),
        [...evaluationPath, { kind: "ref", token: reference }],
        [...refStack, refKey],
      );
    }
    const mappingKeywords = [
      ["properties", "property"],
      ["patternProperties", "pattern_property"],
      ["dependentSchemas", "dependent_schema"],
    ];
    for (const [keyword, kind] of mappingKeywords) {
      const children = node.has(keyword) ? node.get(keyword) : undefined;
      if (isObj(children)) {
        for (const name of children.keys) {
          descend(
            resolvedSchemaId,
            children.get(name),
            `${schemaPointer}/${pointerEscape(keyword)}/${pointerEscape(name)}`,
            [...evaluationPath, { kind, token: name }],
            refStack,
          );
        }
      }
    }
    const indexedKeywords = [
      ["allOf", "all_of_branch"],
      ["anyOf", "any_of_branch"],
      ["oneOf", "one_of_branch"],
      ["prefixItems", "prefix_item_index"],
    ];
    for (const [keyword, kind] of indexedKeywords) {
      const children = node.has(keyword) ? node.get(keyword) : undefined;
      if (Array.isArray(children)) {
        children.forEach((child, index) => {
          descend(
            resolvedSchemaId,
            child,
            `${schemaPointer}/${keyword}/${index}`,
            [...evaluationPath, { kind, token: String(index) }],
            refStack,
          );
        });
      }
    }
    const singletonKeywords = [
      ["items", "items"],
      ["contains", "contains"],
      ["if", "if_branch"],
      ["then", "then_branch"],
      ["else", "else_branch"],
      ["not", "not_branch"],
      ["additionalProperties", "additional_property"],
      ["unevaluatedProperties", "unevaluated_property"],
      ["unevaluatedItems", "unevaluated_item"],
    ];
    for (const [keyword, kind] of singletonKeywords) {
      const child = node.has(keyword) ? node.get(keyword) : undefined;
      if ((isObj(child) || child === true) && child !== false) {
        descend(
          resolvedSchemaId,
          child,
          `${schemaPointer}/${keyword}`,
          [...evaluationPath, { kind, token: keyword }],
          refStack,
        );
      }
    }
  }

  descend(
    rootSchemaId,
    byId.get(rootSchemaId).document,
    "",
    [],
    [`${rootSchemaId} #`],
  );

  function deduplicate(rows) {
    const seen = new Set();
    const result = [];
    for (const row of rows) {
      const marker = serialize(row);
      if (!seen.has(marker)) {
        seen.add(marker);
        result.push(row);
      }
    }
    return result;
  }

  return {
    integerTypes: deduplicate(integerTypes),
    integerConsts: deduplicate(integerConsts),
    unclassified: [...new Set(unclassified)].sort(),
  };
}

function recomputeStaticInventory(schemaSubjects) {
  const byId = new Map();
  for (const subject of schemaSubjects) {
    byId.set(subject.schemaId, subject);
  }
  const rows = [];
  for (const subject of schemaSubjects) {
    const { path, document, raw, schemaId } = subject;
    if (!isObj(document) || document.get("$id") !== schemaId) {
      refuse("schema_id_mismatch", `${path}: schema $id drift`);
    }
    const integerTypes = [];
    const integerConsts = [];
    const referenceEdges = [];
    const typeNumbers = [];
    const numberUnions = [];
    const unclassified = [];

    const visitSchema = (node, pointer) => {
      if (node === true || node === false) return;
      if (Array.isArray(node)) {
        node.forEach((child, index) => visitSchema(child, `${pointer}/${index}`));
        return;
      }
      if (!isObj(node)) return;
      const nodeType = typeOf(node);
      if (nodeType === "number") {
        typeNumbers.push(`${schemaId}#${pointer}/type`);
      } else if (Array.isArray(nodeType) && nodeType.includes("number")) {
        numberUnions.push(`${schemaId}#${pointer}/type`);
      }
      if (typeIncludes(nodeType, "integer")) {
        integerTypes.push({
          schema_location: `${schemaId}#${pointer}/type`,
          assertion_keyword: "type",
          position_rule: "integer_type",
        });
      }
      if (node.has("const")) {
        integerConsts.push(
          ...collectIntegerConstLeaves(
            node.get("const"),
            `${schemaId}#${pointer}/const`,
          ),
        );
      }
      if (node.has("enum") && node.get("enum").some((item) => isInt(item))) {
        if (nodeType !== "integer") {
          unclassified.push(`${schemaId}#${pointer}/enum`);
        }
      }
      const numericKeywords = [
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
      ];
      if (
        numericKeywords.some((keyword) => node.has(keyword)) &&
        nodeType !== "integer" &&
        nodeType !== "number"
      ) {
        unclassified.push(`${schemaId}#${pointer}`);
      }
      if (node.has("$dynamicRef") || node.has("$recursiveRef")) {
        refuse(
          "static_inventory_recomputation_mismatch",
          `${path}: dynamic/recursive reference is outside this inventory`,
        );
      }
      const reference = node.has("$ref") ? node.get("$ref") : undefined;
      if (typeof reference === "string") {
        const hashIndex = reference.indexOf("#");
        const targetBase =
          hashIndex === -1 ? reference : reference.slice(0, hashIndex);
        const resolvedId = targetBase === "" ? schemaId : targetBase;
        if (!byId.has(resolvedId)) {
          refuse(
            "out_of_cohort_reference",
            `${path}: unresolved exact-cohort reference ${reference}`,
          );
        }
        const target = byId.get(resolvedId);
        const fragment = hashIndex === -1 ? "" : reference.slice(hashIndex);
        resolvePointer(target.document, fragment, resolvedId);
        referenceEdges.push({
          source_schema_location: `${schemaId}#${pointer}/$ref`,
          target_schema_id: resolvedId,
          target_schema_raw_digest: sha256(target.raw),
          target_schema_path: target.path,
          target_fragment: fragment === "" ? "#" : fragment,
        });
      }
      for (const key of node.keys) {
        const child = node.get(key);
        if (
          key === "const" ||
          key === "enum" ||
          key === "examples" ||
          key === "default" ||
          key.startsWith("x-")
        ) {
          continue;
        }
        if (
          (key === "$defs" ||
            key === "definitions" ||
            key === "properties" ||
            key === "patternProperties" ||
            key === "dependentSchemas") &&
          isObj(child)
        ) {
          for (const name of child.keys) {
            visitSchema(
              child.get(name),
              `${pointer}/${pointerEscape(key)}/${pointerEscape(name)}`,
            );
          }
          continue;
        }
        if (isObj(child) || Array.isArray(child) || child === true || child === false) {
          visitSchema(child, `${pointer}/${pointerEscape(key)}`);
        }
      }
    };

    visitSchema(document, "");
    const expanded = expandedNumericPositions(schemaId, byId);
    if (
      typeNumbers.length > 0 ||
      numberUnions.length > 0 ||
      unclassified.length > 0 ||
      expanded.unclassified.length > 0
    ) {
      refuse(
        "unclassified_numeric_position",
        `${path}: unsupported numeric position`,
      );
    }
    const tokenRows = integerTokenRows(document, subject.numberLexemes, path);
    const documentTokens = tokenRows.map((row) => ({
      document_pointer: row.instance_pointer,
      raw_lexeme: row.raw_lexeme,
      decimal_value: row.decimal_value,
    }));
    const tokenDigest = sha256(Buffer.from(serialize(documentTokens), "utf-8"));
    const positionProjection = {
      integer_type_assertions: integerTypes,
      integer_const_leaves: integerConsts,
      expanded_instance_integer_type_positions: expanded.integerTypes,
      expanded_instance_integer_const_positions: expanded.integerConsts,
      resolved_reference_edges: referenceEdges,
    };
    rows.push({
      schema_path: path,
      schema_id: schemaId,
      schema_raw_digest: sha256(raw),
      schema_byte_count: raw.length,
      schema_document_numeric_literals_are_instance_positions: false,
      schema_document_numeric_token_count: documentTokens.length,
      schema_document_number_tokens: documentTokens,
      schema_document_numeric_token_inventory_sha256: tokenDigest,
      integer_type_assertion_count: integerTypes.length,
      integer_type_assertions: integerTypes,
      integer_const_leaf_count: integerConsts.length,
      integer_const_leaves: integerConsts,
      expanded_instance_integer_type_position_count: expanded.integerTypes.length,
      expanded_instance_integer_type_positions: expanded.integerTypes,
      expanded_instance_integer_const_position_count:
        expanded.integerConsts.length,
      expanded_instance_integer_const_positions: expanded.integerConsts,
      resolved_reference_edge_count: referenceEdges.length,
      resolved_reference_edges: referenceEdges,
      type_number_assertions: [],
      number_admitting_unions: [],
      unclassified_numeric_assertions: [],
      position_inventory_sha256: sha256(
        Buffer.from(serialize(positionProjection), "utf-8"),
      ),
    });
  }
  return {
    inventory_kind:
      "static_exact_schema_position_inventory_without_subject_digest",
    derivation_input: "twelve_final_schema_byte_strings_only",
    schema_count: 12,
    profile_id: PROFILE_ID,
    raw_number_contract_id: RAW_NUMBER_CONTRACT_ID,
    future_instance_pointers_included: false,
    concrete_subject_digests_included: false,
    schema_document_numeric_literals_are_future_instance_positions: false,
    type_number_supported: false,
    number_admitting_unions_supported: false,
    unclassified_numeric_positions_permitted: false,
    schemas: rows,
  };
}

class ClosedEvaluator {
  constructor(byId, subject) {
    this.byId = byId;
    this.subject = subject;
    this.applicable = new Map();
  }
  note(instancePointer, schemaId, schemaDigest, location, rule) {
    if (!this.applicable.has(instancePointer)) {
      this.applicable.set(instancePointer, []);
    }
    const rows = this.applicable.get(instancePointer);
    const row = {
      resolved_schema_id: schemaId,
      resolved_schema_raw_digest: schemaDigest,
      assertion_schema_location: location,
      position_rule: rule,
    };
    const marker = serialize(row);
    if (!rows.some((existing) => serialize(existing) === marker)) {
      rows.push(row);
    }
  }
  checkVocabulary(node, location) {
    for (const key of node.keys) {
      if (!CLOSED_VOCABULARY.has(key)) {
        refuse(
          "closed_vocabulary_violation",
          `${this.subject}: unimplemented schema keyword ${JSON.stringify(key)} at ${location}`,
        );
      }
    }
  }
  constMatches(expected, instance, instancePointer, schemaId, schemaDigest, location, relative = "") {
    if (isInt(expected)) {
      if (isInt(instance) && instance.lexeme === expected.lexeme) {
        this.note(
          instancePointer,
          schemaId,
          schemaDigest,
          `${location}${relative}`,
          "recursive_integer_valued_const_leaf",
        );
        return true;
      }
      return false;
    }
    if (
      expected === null ||
      expected === true ||
      expected === false ||
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
          expected.get(key),
          instance.get(key),
          `${instancePointer}/${pointerEscape(key)}`,
          schemaId,
          schemaDigest,
          location,
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
          child,
          instance[index],
          `${instancePointer}/${index}`,
          schemaId,
          schemaDigest,
          location,
          `${relative}/${index}`,
        ),
      );
    }
    return false;
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
    this.checkVocabulary(node, location);
    const schemaDigest = sha256(this.byId.get(schemaId).raw);
    let valid = true;

    const reference = node.has("$ref") ? node.get("$ref") : undefined;
    if (typeof reference === "string") {
      const hashIndex = reference.indexOf("#");
      const targetBase =
        hashIndex === -1 ? reference : reference.slice(0, hashIndex);
      const resolvedId = targetBase === "" ? schemaId : targetBase;
      if (!this.byId.has(resolvedId)) {
        refuse(
          "out_of_cohort_reference",
          `${this.subject}: reference outside exact cohort ${reference}`,
        );
      }
      const fragment = hashIndex === -1 ? "" : reference.slice(hashIndex);
      const refKey = `${resolvedId} ${fragment === "" ? "#" : fragment} ${instancePointer}`;
      if (refStack.includes(refKey)) {
        refuse(
          "fallback_resolution_forbidden",
          `${this.subject}: reference cycle at ${reference}`,
        );
      }
      const targetNode = resolvePointer(
        this.byId.get(resolvedId).document,
        fragment,
        resolvedId,
      );
      if (
        !this.evaluate(
          resolvedId,
          targetNode,
          fragment === "" ? "" : fragment.slice(1),
          instance,
          instancePointer,
          [...refStack, refKey],
          errors,
        )
      ) {
        valid = false;
      }
    }

    const nodeType = typeOf(node);
    if (nodeType !== undefined) {
      const allowed = Array.isArray(nodeType) ? nodeType : [nodeType];
      if (allowed.includes("number")) {
        refuse(
          "unclassified_numeric_position",
          `${this.subject}: type admits number at ${location}/type`,
        );
      }
      let matched = false;
      for (const typeName of allowed) {
        if (typeName === "object" && isObj(instance)) matched = true;
        else if (typeName === "array" && Array.isArray(instance)) matched = true;
        else if (typeName === "string" && typeof instance === "string") matched = true;
        else if (typeName === "boolean" && (instance === true || instance === false)) matched = true;
        else if (typeName === "integer" && isInt(instance)) matched = true;
        else if (typeName === "null" && instance === null) matched = true;
      }
      if (!matched) {
        errors.push(`${instancePointer}: type mismatch at ${location}`);
        valid = false;
      }
      if (allowed.includes("integer") && isInt(instance)) {
        this.note(
          instancePointer,
          schemaId,
          schemaDigest,
          `${location}/type`,
          "integer_type",
        );
      }
    }

    if (node.has("const")) {
      if (
        !this.constMatches(
          node.get("const"),
          instance,
          instancePointer,
          schemaId,
          schemaDigest,
          `${location}/const`,
        )
      ) {
        errors.push(`${instancePointer}: const mismatch at ${location}`);
        valid = false;
      }
    }
    if (node.has("enum")) {
      const members = node.get("enum");
      if (members.some((item) => isInt(item)) && nodeType !== "integer") {
        refuse(
          "unclassified_numeric_position",
          `${this.subject}: integer enum outside integer type at ${location}/enum`,
        );
      }
      const instanceMarker = serialize(instance);
      if (!members.some((member) => serialize(member) === instanceMarker)) {
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
      if (node.has("minimum") && instance.value < node.get("minimum").value) {
        errors.push(`${instancePointer}: minimum at ${location}`);
        valid = false;
      }
      if (node.has("maximum") && instance.value > node.get("maximum").value) {
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
        const markers = instance.map((item) => serialize(item));
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
              schemaId,
              prefix[index],
              `${schemaPointer}/prefixItems/${index}`,
              instance[index],
              `${instancePointer}/${index}`,
              refStack,
              errors,
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
                schemaId,
                items,
                `${schemaPointer}/items`,
                instance[index],
                `${instancePointer}/${index}`,
                refStack,
                errors,
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
                schemaId,
                properties.get(name),
                `${schemaPointer}/properties/${pointerEscape(name)}`,
                instance.get(name),
                `${instancePointer}/${pointerEscape(name)}`,
                refStack,
                errors,
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
              schemaId,
              additional,
              `${schemaPointer}/additionalProperties`,
              instance.get(name),
              `${instancePointer}/${pointerEscape(name)}`,
              refStack,
              errors,
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
            schemaId,
            subschema,
            `${schemaPointer}/allOf/${index}`,
            instance,
            instancePointer,
            refStack,
            errors,
          )
        ) {
          valid = false;
        }
      });
    }

    if (node.has("if")) {
      const silent = [];
      const condition = this.evaluate(
        schemaId,
        node.get("if"),
        `${schemaPointer}/if`,
        instance,
        instancePointer,
        refStack,
        silent,
      );
      const branchKey = condition ? "then" : "else";
      if (node.has(branchKey)) {
        if (
          !this.evaluate(
            schemaId,
            node.get(branchKey),
            `${schemaPointer}/${branchKey}`,
            instance,
            instancePointer,
            refStack,
            errors,
          )
        ) {
          valid = false;
        }
      }
    }
    return valid;
  }
}

function loadSubject(root, relative) {
  if (
    relative.includes(" ") ||
    relative.startsWith("/") ||
    relative.split("/").includes("..")
  ) {
    refuse(
      "subject_byte_binding_mismatch",
      `illegal subject path ${JSON.stringify(relative)}`,
    );
  }
  const target = join(root, relative);
  const stat = lstatSync(target, { throwIfNoEntry: false });
  if (stat === undefined || !stat.isFile() || stat.isSymbolicLink()) {
    refuse(
      "subject_byte_binding_mismatch",
      `${relative}: not a regular non-symlink file`,
    );
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
      !["--repository-root", "--contract", "--source-manifest"].includes(flag)
    ) {
      refuse("execution_binding_mismatch", `unsupported argument ${flag}`);
    }
    values.set(flag, value);
  }
  for (const flag of ["--repository-root", "--contract", "--source-manifest"]) {
    if (!values.has(flag)) {
      refuse("execution_binding_mismatch", `missing argument ${flag}`);
    }
  }
  return values;
}

function main() {
  const argumentsMap = parseArguments(process.argv);
  const root = argumentsMap.get("--repository-root");

  const contractRaw = readFileSync(argumentsMap.get("--contract"));
  const contractParser = new Parser(decodeStrict(contractRaw, "contract"), "contract");
  const contract = contractParser.parseDocument();
  if (
    !isObj(contract) ||
    contract.get("contract_id") !== "prq-002f-numeric-trace-conformance-contract.0001"
  ) {
    refuse("subject_census_mismatch", "unexpected contract identity");
  }
  const contractSubjects = contract.get("subjects");
  if (!Array.isArray(contractSubjects) || contractSubjects.length !== 15) {
    refuse("subject_census_mismatch", "contract subject census is not 15 rows");
  }

  const subjects = [];
  const parsedByRole = new Map();
  SUBJECT_ROWS.forEach((row, index) => {
    const [role, relative, expectedDigest, expectedCount, schemaId, kind, governing] = row;
    const raw = loadSubject(root, relative);
    const digest = sha256(raw);
    if (digest !== expectedDigest) {
      refuse(
        "subject_byte_binding_mismatch",
        `${relative}: raw digest differs from hard-coded census`,
      );
    }
    if (String(raw.length) !== expectedCount) {
      refuse(
        "subject_byte_binding_mismatch",
        `${relative}: byte count differs from hard-coded census`,
      );
    }
    const contractRow = contractSubjects[index];
    if (
      !isObj(contractRow) ||
      contractRow.get("role") !== role ||
      contractRow.get("repository_path") !== relative ||
      contractRow.get("raw_sha256") !== digest ||
      contractRow.get("byte_count_decimal") !== String(raw.length) ||
      contractRow.get("subject_kind") !== kind
    ) {
      refuse(
        "subject_census_mismatch",
        `${relative}: contract subject row differs from observed bytes`,
      );
    }
    const parser = new Parser(decodeStrict(raw, relative), relative);
    const document = parser.parseDocument();
    if (kind === "schema_document") {
      if (
        !isObj(document) ||
        document.get("$id") !== schemaId ||
        contractRow.get("schema_id") !== schemaId
      ) {
        refuse("schema_id_mismatch", `${relative}: schema $id drift`);
      }
    } else if (contractRow.get("governing_schema_role") !== governing) {
      refuse("subject_census_mismatch", `${relative}: governing schema role drift`);
    }
    parsedByRole.set(role, {
      role,
      path: relative,
      raw,
      document,
      schemaId,
      kind,
      governing,
      numberLexemes: parser.numberLexemes,
    });
    subjects.push({
      role,
      repository_path: relative,
      raw_sha256: digest,
      byte_count_decimal: String(raw.length),
      subject_kind: kind,
    });
  });

  const schemaSubjects = SUBJECT_ROWS.filter((row) => row[5] === "schema_document").map(
    (row) => parsedByRole.get(row[0]),
  );
  const inventory = recomputeStaticInventory(schemaSubjects);

  const core = parsedByRole.get("profile_core").document;
  const retainedInventory = core.get("static_numeric_applicability_inventory");
  if (!equalSerialized(retainedInventory, inventory)) {
    refuse(
      "static_inventory_recomputation_mismatch",
      "retained core inventory differs from independent recomputation",
    );
  }

  const graph = core.get("digest_dependency_graph");
  const graphNodes = isObj(graph) ? graph.get("nodes") : undefined;
  const graphEdges = (isObj(graph) && Array.isArray(graph.get("edges"))
    ? graph.get("edges")
    : []
  ).map((edge) => [
    isObj(edge) ? edge.get("subject") : undefined,
    isObj(edge) ? edge.get("dependency") : undefined,
  ]);
  if (
    !Array.isArray(graphNodes) ||
    serialize(graphNodes) !== serialize(EXPECTED_GRAPH_NODES) ||
    serialize(graphEdges) !== serialize(EXPECTED_GRAPH_EDGES)
  ) {
    refuse(
      "digest_dependency_graph_mismatch",
      "retained digest dependency graph differs from expectation",
    );
  }
  if (graphEdges.some(([subject, dependency]) => subject === dependency)) {
    refuse("digest_dependency_graph_mismatch", "self edge in dependency graph");
  }

  const evidence = parsedByRole.get("profile_evidence").document;
  const coreBytes = parsedByRole.get("profile_core").raw;
  const evidenceBytes = parsedByRole.get("profile_evidence").raw;
  let citationCount = 0;
  const coreBinding = evidence.get("profile_core_binding");
  if (
    !isObj(coreBinding) ||
    coreBinding.get("profile_core_raw_digest") !== sha256(coreBytes) ||
    !isInt(coreBinding.get("profile_core_byte_count")) ||
    coreBinding.get("profile_core_byte_count").lexeme !== String(coreBytes.length)
  ) {
    refuse(
      "digest_dependency_graph_mismatch",
      "evidence core binding differs from recomputed core bytes",
    );
  }
  citationCount += 1;
  const schemaBindings = evidence.get("successor_schema_bindings");
  if (!Array.isArray(schemaBindings) || schemaBindings.length !== 12) {
    refuse(
      "digest_dependency_graph_mismatch",
      "evidence successor schema bindings are not twelve rows",
    );
  }
  const bindingByPath = new Map();
  for (const binding of schemaBindings) {
    if (isObj(binding)) {
      bindingByPath.set(binding.get("path"), binding);
    }
  }
  for (const row of SUBJECT_ROWS) {
    if (row[5] !== "schema_document") continue;
    const subjectBytes = parsedByRole.get(row[0]).raw;
    const binding = bindingByPath.get(row[1]);
    if (
      !isObj(binding) ||
      binding.get("schema_id") !== row[4] ||
      binding.get("raw_digest") !== sha256(subjectBytes) ||
      !isInt(binding.get("byte_count")) ||
      binding.get("byte_count").lexeme !== String(subjectBytes.length)
    ) {
      refuse(
        "digest_dependency_graph_mismatch",
        `evidence binding for ${row[1]} differs from recomputed bytes`,
      );
    }
    citationCount += 1;
  }
  const migration = parsedByRole.get("profile_migration").document;
  const successorBinding = migration.get("successor_profile_binding");
  if (
    !isObj(successorBinding) ||
    successorBinding.get("profile_evidence_path") !==
      "architecture/canonicalization-profile-0.3-candidate-evidence.json" ||
    successorBinding.get("profile_evidence_raw_digest") !== sha256(evidenceBytes) ||
    !isInt(successorBinding.get("profile_evidence_byte_count")) ||
    successorBinding.get("profile_evidence_byte_count").lexeme !==
      String(evidenceBytes.length) ||
    successorBinding.get("profile_core_raw_digest") !== sha256(coreBytes) ||
    !isInt(successorBinding.get("profile_core_byte_count")) ||
    successorBinding.get("profile_core_byte_count").lexeme !==
      String(coreBytes.length)
  ) {
    refuse(
      "digest_dependency_graph_mismatch",
      "migration record does not bind the exact evidence and core bytes",
    );
  }
  citationCount += 4;

  const traces = [];
  for (const row of SUBJECT_ROWS) {
    const [role, relative, , , , kind, governing] = row;
    const parsed = parsedByRole.get(role);
    const tokenRows = integerTokenRows(parsed.document, parsed.numberLexemes, relative);
    let tokens;
    if (kind === "schema_document") {
      const inventoryRow = inventory.schemas.find(
        (schema) => schema.schema_path === relative,
      );
      if (tokenRows.length !== inventoryRow.schema_document_numeric_token_count) {
        refuse(
          "raw_token_reconciliation_mismatch",
          `${relative}: trace token count differs from inventory`,
        );
      }
      tokens = tokenRows.map((token) => ({
        ordinal_decimal: token.ordinal_decimal,
        raw_lexeme: token.raw_lexeme,
        decimal_value: token.decimal_value,
        instance_pointer: token.instance_pointer,
        classification: {
          final_rule: SCHEMA_DOCUMENT_TOKEN_RULE,
          metaschema_evaluation: METASCHEMA_DISPOSITION,
        },
      }));
    } else {
      const byId = new Map();
      for (const schemaSubject of schemaSubjects) {
        byId.set(schemaSubject.schemaId, schemaSubject);
      }
      const governingId = SUBJECT_ROWS.find((r) => r[0] === governing)[4];
      const evaluator = new ClosedEvaluator(byId, relative);
      const errors = [];
      if (
        !evaluator.evaluate(
          governingId,
          byId.get(governingId).document,
          "",
          parsed.document,
          "",
          [`${governingId} # `],
          errors,
        )
      ) {
        refuse(
          "record_schema_validation_failed",
          `${relative}: ${errors.length > 0 ? errors[0] : "schema validation failed"}`,
        );
      }
      tokens = tokenRows.map((token) => {
        const applicable = evaluator.applicable.get(token.instance_pointer) ?? [];
        if (applicable.length === 0) {
          refuse(
            "unclassified_instance_numeric_position",
            `${relative}: token at ${token.instance_pointer} has no applicable integer rule`,
          );
        }
        const rules = new Set(applicable.map((entry) => entry.position_rule));
        for (const rule of rules) {
          if (!FINAL_RULE_PRECEDENCE.includes(rule)) {
            refuse(
              "multiply_classified_instance_position",
              `${relative}: unexpected rule ${rule}`,
            );
          }
        }
        const finalRule = rules.has(FINAL_RULE_PRECEDENCE[0])
          ? FINAL_RULE_PRECEDENCE[0]
          : FINAL_RULE_PRECEDENCE[1];
        return {
          ordinal_decimal: token.ordinal_decimal,
          raw_lexeme: token.raw_lexeme,
          decimal_value: token.decimal_value,
          instance_pointer: token.instance_pointer,
          classification: {
            final_rule: finalRule,
            applicable_assertions: applicable,
          },
        };
      });
    }
    traces.push({
      role,
      repository_path: relative,
      raw_sha256: sha256(parsed.raw),
      byte_count_decimal: String(parsed.raw.length),
      subject_kind: kind,
      token_count_decimal: String(tokenRows.length),
      tokens,
    });
  }

  const sum = (selector) =>
    inventory.schemas.reduce((total, schema) => total + selector(schema), 0);
  const totals = {
    schema_document_numeric_token_count_decimal: String(
      sum((schema) => schema.schema_document_numeric_token_count),
    ),
    integer_type_assertion_count_decimal: String(
      sum((schema) => schema.integer_type_assertion_count),
    ),
    integer_const_leaf_count_decimal: String(
      sum((schema) => schema.integer_const_leaf_count),
    ),
    expanded_instance_integer_type_position_count_decimal: String(
      sum((schema) => schema.expanded_instance_integer_type_position_count),
    ),
    expanded_instance_integer_const_position_count_decimal: String(
      sum((schema) => schema.expanded_instance_integer_const_position_count),
    ),
    resolved_reference_edge_count_decimal: String(
      sum((schema) => schema.resolved_reference_edge_count),
    ),
    schema_byte_count_decimal: String(sum((schema) => schema.schema_byte_count)),
  };
  const projection = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002f_numeric_trace_projection",
    suite_id: SUITE_ID,
    profile_id: PROFILE_ID,
    raw_number_contract_id: RAW_NUMBER_CONTRACT_ID,
    contract_binding: {
      repository_path: CONTRACT_PATH,
      raw_sha256: sha256(contractRaw),
      byte_count_decimal: String(contractRaw.length),
    },
    subject_census: subjects,
    static_inventory_comparison: {
      recomputed_matches_retained_core_inventory: true,
      schema_count_decimal: "12",
      totals,
      per_schema: inventory.schemas.map((schema) => ({
        schema_id: schema.schema_id,
        schema_raw_digest: schema.schema_raw_digest,
        schema_byte_count_decimal: String(schema.schema_byte_count),
        schema_document_numeric_token_count_decimal: String(
          schema.schema_document_numeric_token_count,
        ),
        schema_document_numeric_token_inventory_sha256:
          schema.schema_document_numeric_token_inventory_sha256,
        position_inventory_sha256: schema.position_inventory_sha256,
      })),
    },
    metaschema_settlement: {
      schema_document_token_rule: SCHEMA_DOCUMENT_TOKEN_RULE,
      metaschema_evaluation_disposition: METASCHEMA_DISPOSITION,
      schema_document_subject_count_decimal: "12",
    },
    traces,
    cross_object_conformance: {
      record_validation: SUBJECT_ROWS.filter((row) => row[5] === "record_instance").map(
        (row) => ({
          role: row[0],
          governing_schema_role: row[6],
          schema_valid: true,
        }),
      ),
      digest_dependency_graph: {
        node_count_decimal: String(EXPECTED_GRAPH_NODES.length),
        edge_count_decimal: String(EXPECTED_GRAPH_EDGES.length),
        retained_graph_matches_expectation: true,
        byte_citation_verified_count_decimal: String(citationCount),
      },
    },
    claim_boundary: {
      conformance_scope: "exact_fifteen_subject_cohort_only",
      product_identity_computed: false,
      profile_issued: false,
      prq_002_closed: false,
      gate_a_complete: false,
      runtime_authorized: false,
      publication_authorized: false,
    },
  };
  const projectionBytes = Buffer.from(serialize(projection), "utf-8");
  const result = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002f_numeric_trace_result",
    suite_id: SUITE_ID,
    implementation_id: IMPLEMENTATION_ID,
    implementation_role: "node",
    projection_sha256: sha256(projectionBytes),
    projection,
  };
  process.stdout.write(Buffer.from(serialize(result), "utf-8"));
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
        serialize({
          schema_version: SCHEMA_VERSION,
          artifact_class: "prq_002f_numeric_trace_refusal",
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
