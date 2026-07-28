#!/usr/bin/env node
/**
 * Source-separated Node.js observer for PRQ-002C raw-number token typing.
 *
 * This implementation intentionally does not share parsing source with the
 * Python observer. It uses a local recursive-descent JSON parser so numeric
 * lexemes and duplicate decoded names survive before JavaScript Number
 * mapping.
 */

import { createHash } from "node:crypto";
import { readFileSync, realpathSync } from "node:fs";
import process from "node:process";

const SUITE_ID = "prq-002c-raw-number-typing.0001";
const VECTOR_SET_ID = "prq-002c-raw-number-vectors.synthetic.0003";
const CONTRACT_ID =
  "urn:odeya:canonicalization:raw-number-token-contract:0.1.0";
const TYPE_FRAME_ID = "odeya.raw-number-integer-type-position.v1";
const CONST_FRAME_ID = "odeya.raw-number-integer-const-position.v1";
const IMPLEMENTATION_ID = "nodejs-recursive-descent-raw-lexeme.0003";
const EXPECTED_RUNTIME = "24.18.0";
const MIN_INTEGER = -9007199254740991n;
const MAX_INTEGER = 9007199254740991n;
const MAX_NUMBER_TOKEN_BYTES = 128;
const CHALLENGE_RE = /^challenge-v1:[0-9a-f]{64}$/;
const OPAQUE_VECTOR_ID_RE = /^RN-[0-9]{4}$/;
const VECTOR_KEYS = [
  "decoded_byte_count",
  "decoded_raw_sha256",
  "input_base64",
  "media_type",
  "sequence_index",
  "vector_id",
];

class ParseFailure extends Error {
  constructor(code) {
    super(code);
    this.code = code;
  }
}

class RawNumber {
  constructor(tokenClass, lexeme) {
    this.tokenClass = tokenClass;
    this.lexeme = lexeme;
  }
}

class StrictParser {
  constructor(text) {
    this.text = text;
    this.index = 0;
    this.duplicateName = false;
    this.unpairedSurrogate = false;
  }

  parse() {
    this.skipWhitespace();
    const value = this.parseValue();
    this.skipWhitespace();
    if (this.index !== this.text.length) {
      throw new ParseFailure("ODEYA_PARSE_SYNTAX");
    }
    if (this.duplicateName) {
      throw new ParseFailure("ODEYA_PARSE_DUPLICATE_KEY");
    }
    if (this.unpairedSurrogate) {
      throw new ParseFailure("ODEYA_PARSE_UNPAIRED_SURROGATE");
    }
    return value;
  }

  skipWhitespace() {
    while (
      this.index < this.text.length &&
      " \t\r\n".includes(this.text[this.index])
    ) {
      this.index += 1;
    }
  }

  parseValue() {
    const character = this.text[this.index];
    if (character === "{") return this.parseObject();
    if (character === "[") return this.parseArray();
    if (character === '"') return this.parseString();
    if (character === "t" && this.consumeLiteral("true")) return true;
    if (character === "f" && this.consumeLiteral("false")) return false;
    if (character === "n" && this.consumeLiteral("null")) return null;
    if (character === "-" || (character >= "0" && character <= "9")) {
      return this.parseNumber();
    }
    throw new ParseFailure("ODEYA_PARSE_SYNTAX");
  }

  consumeLiteral(literal) {
    if (this.text.slice(this.index, this.index + literal.length) !== literal) {
      return false;
    }
    this.index += literal.length;
    return true;
  }

  parseObject() {
    const result = Object.create(null);
    const names = new Set();
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === "}") {
      this.index += 1;
      return result;
    }
    while (this.index < this.text.length) {
      if (this.text[this.index] !== '"') {
        throw new ParseFailure("ODEYA_PARSE_SYNTAX");
      }
      const name = this.parseString();
      const duplicateName = names.has(name);
      names.add(name);
      this.skipWhitespace();
      if (this.text[this.index] !== ":") {
        throw new ParseFailure("ODEYA_PARSE_SYNTAX");
      }
      this.index += 1;
      this.skipWhitespace();
      result[name] = this.parseValue();
      if (duplicateName) {
        this.duplicateName = true;
      }
      this.skipWhitespace();
      if (this.text[this.index] === "}") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") {
        throw new ParseFailure("ODEYA_PARSE_SYNTAX");
      }
      this.index += 1;
      this.skipWhitespace();
    }
    throw new ParseFailure("ODEYA_PARSE_SYNTAX");
  }

  parseArray() {
    const result = [];
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === "]") {
      this.index += 1;
      return result;
    }
    while (this.index < this.text.length) {
      result.push(this.parseValue());
      this.skipWhitespace();
      if (this.text[this.index] === "]") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") {
        throw new ParseFailure("ODEYA_PARSE_SYNTAX");
      }
      this.index += 1;
      this.skipWhitespace();
    }
    throw new ParseFailure("ODEYA_PARSE_SYNTAX");
  }

  parseString() {
    if (this.text[this.index] !== '"') {
      throw new ParseFailure("ODEYA_PARSE_SYNTAX");
    }
    this.index += 1;
    let result = "";
    while (this.index < this.text.length) {
      const character = this.text[this.index];
      const code = this.text.charCodeAt(this.index);
      if (character === '"') {
        this.index += 1;
        return result;
      }
      if (character === "\\") {
        this.index += 1;
        if (this.index >= this.text.length) {
          throw new ParseFailure("ODEYA_PARSE_SYNTAX");
        }
        const escape = this.text[this.index];
        const simple = {
          '"': '"',
          "\\": "\\",
          "/": "/",
          b: "\b",
          f: "\f",
          n: "\n",
          r: "\r",
          t: "\t",
        };
        if (Object.hasOwn(simple, escape)) {
          result += simple[escape];
          this.index += 1;
          continue;
        }
        if (escape !== "u") {
          throw new ParseFailure("ODEYA_PARSE_SYNTAX");
        }
        const first = this.parseUnicodeEscape();
        if (first >= 0xd800 && first <= 0xdbff) {
          if (
            this.text[this.index] !== "\\" ||
            this.text[this.index + 1] !== "u"
          ) {
            this.unpairedSurrogate = true;
            result += String.fromCharCode(first);
            continue;
          }
          this.index += 1;
          const second = this.parseUnicodeEscape();
          if (second < 0xdc00 || second > 0xdfff) {
            this.unpairedSurrogate = true;
            result += String.fromCharCode(first, second);
            continue;
          }
          const scalar =
            0x10000 + ((first - 0xd800) << 10) + (second - 0xdc00);
          result += String.fromCodePoint(scalar);
          continue;
        }
        if (first >= 0xdc00 && first <= 0xdfff) {
          this.unpairedSurrogate = true;
          result += String.fromCharCode(first);
          continue;
        }
        result += String.fromCharCode(first);
        continue;
      }
      if (code < 0x20) {
        throw new ParseFailure("ODEYA_PARSE_SYNTAX");
      }
      if (code >= 0xd800 && code <= 0xdbff) {
        const second = this.text.charCodeAt(this.index + 1);
        if (second < 0xdc00 || second > 0xdfff) {
          this.unpairedSurrogate = true;
          result += character;
          this.index += 1;
          continue;
        }
        result += character + this.text[this.index + 1];
        this.index += 2;
        continue;
      }
      if (code >= 0xdc00 && code <= 0xdfff) {
        this.unpairedSurrogate = true;
        result += character;
        this.index += 1;
        continue;
      }
      result += character;
      this.index += 1;
    }
    throw new ParseFailure("ODEYA_PARSE_SYNTAX");
  }

  parseUnicodeEscape() {
    if (this.text[this.index] !== "u") {
      throw new ParseFailure("ODEYA_PARSE_SYNTAX");
    }
    const hex = this.text.slice(this.index + 1, this.index + 5);
    if (!/^[0-9a-fA-F]{4}$/.test(hex)) {
      throw new ParseFailure("ODEYA_PARSE_SYNTAX");
    }
    this.index += 5;
    return Number.parseInt(hex, 16);
  }

  parseNumber() {
    const remaining = this.text.slice(this.index);
    const match =
      /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(
        remaining,
      );
    if (match === null) {
      throw new ParseFailure("ODEYA_PARSE_SYNTAX");
    }
    const lexeme = match[0];
    this.index += lexeme.length;
    const tokenClass = /[.eE]/.test(lexeme)
      ? "number_token"
      : "integer_token";
    return new RawNumber(tokenClass, lexeme);
  }
}

function sha256(raw) {
  return `sha256:${createHash("sha256").update(raw).digest("hex")}`;
}

function binding(path) {
  const raw = readFileSync(path);
  return {
    repository_path: path,
    raw_sha256: sha256(raw),
    byte_count: raw.length,
  };
}

function stableStringify(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  return `{${Object.keys(value)
    .sort()
    .map(
      (key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`,
    )
    .join(",")}}`;
}

function strictUtf8(raw) {
  let text;
  try {
    text = new TextDecoder("utf-8", {
      fatal: true,
      ignoreBOM: true,
    }).decode(raw);
  } catch {
    throw new ParseFailure("ODEYA_PARSE_UTF8");
  }
  if (
    raw.length >= 3 &&
    raw[0] === 0xef &&
    raw[1] === 0xbb &&
    raw[2] === 0xbf
  ) {
    throw new ParseFailure("ODEYA_PARSE_BOM");
  }
  return text;
}

function significandIsZero(lexeme) {
  const body = lexeme.startsWith("-") ? lexeme.slice(1) : lexeme;
  const mantissa = body.split(/[eE]/, 1)[0];
  const digits = mantissa.replace(".", "");
  return digits.length > 0 && /^0+$/.test(digits);
}

function observe(sequenceIndex, vectorId, raw) {
  const base = {
    sequence_index: sequenceIndex,
    vector_id: vectorId,
    decoded_input_sha256: sha256(raw),
    decoded_byte_count: raw.length,
    lexical_disposition: "accepted",
    position_rule: null,
    raw_number_token: null,
    raw_number_token_byte_count: null,
    token_class: null,
    binary64_conversion_class: null,
    integer_position_disposition: null,
    final_disposition: "refused",
    final_code: null,
    integer_decimal: null,
  };
  let value;
  try {
    value = new StrictParser(strictUtf8(raw)).parse();
  } catch (error) {
    if (!(error instanceof ParseFailure)) throw error;
    base.lexical_disposition = "refused";
    base.final_code = error.code;
    return base;
  }
  if (
    value === null ||
    Array.isArray(value) ||
    typeof value !== "object" ||
    Object.keys(value).sort().join("\0") !==
      ["frame_id", "integer_value"].sort().join("\0") ||
    ![TYPE_FRAME_ID, CONST_FRAME_ID].includes(value.frame_id)
  ) {
    base.final_code = "ODEYA_CONFORMANCE_FRAME_SHAPE";
    return base;
  }
  const isConst = value.frame_id === CONST_FRAME_ID;
  base.position_rule = isConst
    ? "integer_const_decimal_1"
    : "type_integer";
  const number = value.integer_value;
  if (!(number instanceof RawNumber)) {
    base.integer_position_disposition = "refused";
    base.final_code = "ODEYA_SCHEMA_TYPE";
    return base;
  }
  base.raw_number_token = number.lexeme;
  base.raw_number_token_byte_count = Buffer.byteLength(
    number.lexeme,
    "ascii",
  );
  base.token_class = number.tokenClass;
  if (base.raw_number_token_byte_count > MAX_NUMBER_TOKEN_BYTES) {
    base.final_code = "ODEYA_LIMIT_NUMBER_TOKEN";
    return base;
  }
  if (number.lexeme.startsWith("-") && significandIsZero(number.lexeme)) {
    base.binary64_conversion_class = "negative_zero_exact_decimal";
    base.final_code = "ODEYA_NUMBER_NEGATIVE_ZERO";
    return base;
  }
  const converted = Number(number.lexeme);
  if (!Number.isFinite(converted)) {
    base.binary64_conversion_class = "nonfinite";
    base.final_code = "ODEYA_NUMBER_NONFINITE";
    return base;
  }
  if (converted === 0 && !significandIsZero(number.lexeme)) {
    base.binary64_conversion_class = Object.is(converted, -0)
      ? "underflow_to_negative_zero"
      : "underflow_to_positive_zero";
    base.final_code = "ODEYA_NUMBER_UNDERFLOW";
    return base;
  }
  base.binary64_conversion_class =
    converted === 0 ? "positive_zero" : "finite_nonzero";
  if (number.tokenClass === "number_token") {
    base.integer_position_disposition = "refused";
    base.final_code = "ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED";
    return base;
  }
  const integer = BigInt(number.lexeme);
  if (integer < MIN_INTEGER || integer > MAX_INTEGER) {
    base.integer_position_disposition = "refused";
    base.final_code = "ODEYA_NUMBER_DOMAIN";
    return base;
  }
  if (isConst && integer !== 1n) {
    base.integer_position_disposition = "refused";
    base.final_code = "ODEYA_SCHEMA_CONST";
    return base;
  }
  base.integer_position_disposition = "accepted";
  base.final_disposition = "accepted";
  base.integer_decimal = number.lexeme;
  return base;
}

function parseArguments(argv) {
  const values = {};
  let emit = false;
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (flag === "--emit-execution-attestation") {
      emit = true;
      continue;
    }
    if (!flag.startsWith("--") || index + 1 >= argv.length) {
      throw new Error(`invalid argument ${flag}`);
    }
    values[flag.slice(2)] = argv[index + 1];
    index += 1;
  }
  const required = [
    "vectors",
    "manifest",
    "contract",
    "contract-schema",
    "profile-core",
    "profile-evidence",
    "source-manifest",
    "attestation-challenge",
  ];
  if (
    Object.keys(values).length !== required.length ||
    required.some((name) => !(name in values))
  ) {
    throw new Error("argument inventory differs");
  }
  return { values, emit };
}

function readJson(path) {
  const value = JSON.parse(readFileSync(path, "utf8"));
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new Error(`${path} must contain one object`);
  }
  return value;
}

function validateVectors(document) {
  const expectedRoot = [
    "answer_free",
    "artifact_class",
    "decoded_input_bindings_present",
    "expected_outcomes_present",
    "opaque_vector_ids",
    "schema_version",
    "status",
    "vector_count",
    "vector_set_id",
    "vectors",
  ];
  if (
    Object.keys(document).sort().join("\0") !==
      expectedRoot.sort().join("\0") ||
    document.schema_version !== "0.3.0" ||
    document.artifact_class !==
      "prq_002c_answer_free_raw_number_vector_set" ||
    document.vector_set_id !== VECTOR_SET_ID ||
    document.status !== "synthetic_non_product_answer_free" ||
    document.answer_free !== true ||
    document.opaque_vector_ids !== true ||
    document.expected_outcomes_present !== false ||
    document.decoded_input_bindings_present !== true ||
    !Array.isArray(document.vectors) ||
    !Number.isInteger(document.vector_count) ||
    document.vector_count !== document.vectors.length
  ) {
    throw new Error("vector root or answer-free boundary differs");
  }
  const seen = new Set();
  for (let index = 0; index < document.vectors.length; index += 1) {
    const vector = document.vectors[index];
    if (
      vector === null ||
      Array.isArray(vector) ||
      typeof vector !== "object" ||
      Object.keys(vector).sort().join("\0") !== VECTOR_KEYS.join("\0") ||
      vector.sequence_index !== index ||
      typeof vector.vector_id !== "string" ||
      !OPAQUE_VECTOR_ID_RE.test(vector.vector_id) ||
      seen.has(vector.vector_id) ||
      vector.media_type !== "application/json" ||
      typeof vector.decoded_raw_sha256 !== "string" ||
      !Number.isInteger(vector.decoded_byte_count) ||
      typeof vector.input_base64 !== "string"
    ) {
      throw new Error(`vector ${index} identity differs`);
    }
    seen.add(vector.vector_id);
    const raw = Buffer.from(vector.input_base64, "base64");
    if (
      raw.toString("base64") !== vector.input_base64 ||
      sha256(raw) !== vector.decoded_raw_sha256 ||
      raw.length !== vector.decoded_byte_count
    ) {
      throw new Error(`vector ${index} decoded binding differs`);
    }
  }
  return document.vectors;
}

function verifyInputManifest(manifest, rolePaths) {
  const expectedRoot = [
    "answer_free_child_input",
    "artifact_class",
    "binding_count",
    "bindings",
    "blocked_profile_predecessor_checkpoint",
    "manifest_id",
    "schema_version",
    "suite_id",
    "vector_set_id",
  ];
  if (
    Object.keys(manifest).sort().join("\0") !==
      expectedRoot.sort().join("\0") ||
    manifest.schema_version !== "0.2.0" ||
    manifest.artifact_class !== "prq_002c_raw_number_input_manifest" ||
    manifest.manifest_id !==
      "prq-002c-raw-number-input-manifest.0003" ||
    manifest.suite_id !== SUITE_ID ||
    manifest.vector_set_id !== VECTOR_SET_ID ||
    stableStringify(manifest.blocked_profile_predecessor_checkpoint) !==
      stableStringify({
        commit: "a79d86b0a5e9581b3bacb57214cf180df3443566",
        tree: "d44e9eb4751b97871aa9c995664782a5d031fb48",
      }) ||
    manifest.answer_free_child_input !== true ||
    manifest.binding_count !== Object.keys(rolePaths).length ||
    !Array.isArray(manifest.bindings) ||
    manifest.bindings.length !== Object.keys(rolePaths).length
  ) {
    throw new Error("input manifest identity differs");
  }
  const byRole = Object.fromEntries(
    manifest.bindings.map((row) => [row.role, row]),
  );
  if (
    Object.keys(byRole).sort().join("\0") !==
    Object.keys(rolePaths).sort().join("\0")
  ) {
    throw new Error("input manifest roles differ");
  }
  for (const [role, path] of Object.entries(rolePaths)) {
    const observed = binding(path);
    if (
      byRole[role].raw_sha256 !== observed.raw_sha256 ||
      byRole[role].byte_count !== observed.byte_count
    ) {
      throw new Error(`input binding differs for ${role}`);
    }
  }
}

function main() {
  const { values, emit } = parseArguments(process.argv.slice(2));
  const runtimeVersion = process.versions.node;
  if (runtimeVersion !== EXPECTED_RUNTIME) {
    throw new Error(`runtime version differs: ${runtimeVersion}`);
  }
  if (
    process.execArgv.length !== 1 ||
    process.execArgv[0] !== "--disable-proto=throw"
  ) {
    throw new Error("required Node.js process flags differ");
  }
  if (!CHALLENGE_RE.test(values["attestation-challenge"])) {
    throw new Error("attestation challenge shape differs");
  }
  const manifest = readJson(values.manifest);
  const contract = readJson(values.contract);
  const sourceManifest = readJson(values["source-manifest"]);
  const vectorsDocument = readJson(values.vectors);
  if (
    contract.contract_id !== CONTRACT_ID ||
    contract.status !== "proposed_architecture_only_non_product_contract"
  ) {
    throw new Error("token contract identity differs");
  }
  if (
    sourceManifest.implementation_id !== IMPLEMENTATION_ID ||
    sourceManifest.peer_source_consumption_allowed !== false ||
    sourceManifest.peer_result_consumption_allowed !== false ||
    sourceManifest.private_expectation_consumption_allowed !== false
  ) {
    throw new Error("source manifest boundary differs");
  }
  const rolePaths = {
    vectors: values.vectors,
    token_contract: values.contract,
    token_contract_schema: values["contract-schema"],
    blocked_profile_core: values["profile-core"],
    blocked_profile_evidence: values["profile-evidence"],
  };
  verifyInputManifest(manifest, rolePaths);
  const vectors = validateVectors(vectorsDocument);
  const results = vectors.map((vector) =>
    observe(
      vector.sequence_index,
      vector.vector_id,
      Buffer.from(vector.input_base64, "base64"),
    ),
  );
  const projection = {
    suite_id: SUITE_ID,
    vector_set_id: VECTOR_SET_ID,
    token_contract_id: CONTRACT_ID,
    vector_count: results.length,
    results,
    claim_boundary: {
      bounded_raw_number_observation_produced: true,
      source_separated_agreement_observed: false,
      generic_schema_path_evaluation_proved: false,
      number_position_semantics_complete: false,
      successor_profile_conformance_complete: false,
      product_identity_computed: false,
      profile_issued: false,
      gate_a_complete: false,
      runtime_authorized: false,
      publication_authorized: false,
    },
  };
  const projectionBinding = sha256(
    Buffer.from(stableStringify(projection), "ascii"),
  );
  const sourceBinding = binding(values["source-manifest"]);
  const implementationCausalBinding = sha256(
    Buffer.from(
      stableStringify({
        implementation_id: IMPLEMENTATION_ID,
        source_manifest_raw_sha256: sourceBinding.raw_sha256,
        projection_raw_sha256: projectionBinding,
      }),
      "ascii",
    ),
  );
  const result = {
    schema_version: "0.1.0",
    artifact_class: "prq_002c_raw_number_observation_result",
    implementation: {
      role: "node",
      implementation_id: IMPLEMENTATION_ID,
      runtime: "Node.js",
      runtime_version: runtimeVersion,
      parser_strategy:
        "recursive_descent_deferred_restriction_classification",
      source_manifest_binding: sourceBinding,
    },
    input_manifest_binding: binding(values.manifest),
    implementation_causal_binding: implementationCausalBinding,
    projection,
  };
  const resultLine = Buffer.from(stableStringify(result), "ascii");
  if (!emit) {
    process.stdout.write(resultLine);
    process.stdout.write("\n");
    return;
  }
  const executable = realpathSync(process.execPath);
  const runner = realpathSync(new URL(import.meta.url).pathname);
  const attestation = {
    schema_version: "0.1.0",
    artifact_class: "prq_002c_child_execution_attestation",
    suite_id: SUITE_ID,
    implementation_id: IMPLEMENTATION_ID,
    challenge: values["attestation-challenge"],
    argv: [
      process.execPath,
      ...process.execArgv,
      runner,
      ...process.argv.slice(2),
    ],
    runtime: {
      family: "Node.js",
      version: runtimeVersion,
      executable: binding(executable),
    },
    runner_binding: binding(runner),
    source_manifest_binding: binding(values["source-manifest"]),
    input_manifest_binding: binding(values.manifest),
    vector_set_binding: binding(values.vectors),
    token_contract_binding: binding(values.contract),
    result_line_binding: {
      raw_sha256: sha256(resultLine),
      byte_count: resultLine.length,
    },
    network_access_requested: false,
    private_expectations_received: false,
    peer_source_received: false,
    peer_result_received: false,
    product_identity_computed: false,
  };
  process.stdout.write(stableStringify(attestation));
  process.stdout.write("\n");
  process.stdout.write(resultLine);
  process.stdout.write("\n");
}

main();
