#!/usr/bin/env node

import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import process from "node:process";
import { TextDecoder } from "node:util";

import Ajv2020 from "ajv/dist/2020.js";

const IMPLEMENTATION_ID = "nodejs-ajv2020-closed-resolver.0001";
const SUITE_ID = "prq-002d-schema-registry-prehash-replay.0001";
const CONTRACT_ID =
  "urn:odeya:architecture-test:prq-002d:" +
  "schema-registry-prehash-contract:0.1.0";
const REQUIRED_NODE_VERSION = "24.18.0";
const REQUIRED_AJV_VERSION = "8.20.0";
const DRAFT_2020_12_URI =
  "https://json-schema.org/draft/2020-12/schema";
const TEST_SCHEMA_ID_PREFIX = "urn:odeya:architecture-test:";
const MEMBER_KEY_PATTERN = /^[a-z0-9._:@-]+$/u;
const VERSION_PATTERN =
  /^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$/u;
const DECIMAL_PATTERN = /^(?:0|[1-9][0-9]*)$/u;
const SHA256_PATTERN = /^sha256:[0-9a-f]{64}$/u;
const VECTOR_ID_PATTERN = /^PH-[0-9]{4}$/u;
const require = createRequire(import.meta.url);
const LOADED_AJV_VERSION = require("ajv/package.json").version;

const AUTHORITY_BOUNDARY = Object.freeze({
  profile_issued: false,
  profile_conformance_proved: false,
  product_schema_resource_admitted: false,
  product_member_constructed: false,
  product_digest_computed: false,
  commitment_constructed: false,
  registry_snapshot_constructed: false,
  registry_digest_computed: false,
  engine_contract_root_constructed: false,
  activation_constructed: false,
  gate_a_complete: false,
  runtime_authorized: false,
  publication_authorized: false,
});

const ROOT_CLAIM_BOUNDARY = Object.freeze({
  organizational_independence_proven: false,
  independent_host_reproduction_complete: false,
  historical_process_independently_witnessed: false,
  undeclared_filesystem_read_excluded: false,
  complete_offline_registry_proved: false,
  product_identity_computed: false,
  profile_issued: false,
  gate_a_complete: false,
  runtime_authorized: false,
  publication_authorized: false,
});
const EVALUATION_CONTRACT = Object.freeze({
  json_dialect: DRAFT_2020_12_URI,
  member_key_expression: "schema_id@semantic_version",
  member_key_pattern: "^[a-z0-9._:@-]+$",
  ordering: "unsigned_lexicographic_utf8_byte_order",
  duplicate_member_keys: "reject_before_ordering",
  declared_member_count_raw_token: "exact_decimal_integer_token_2",
  resolver_inventory:
    "exactly_two_preloaded_contract_pinned_resources",
  resource_preparse_binding:
    "contract_expected_resource_or_enumerated_semantic_fixture_override_before_parse",
  probe_preparse_binding:
    "contract_expected_probe_or_enumerated_semantic_fixture_override_before_parse",
  resolver_catalog_ordering: "contract_expected_resource_order",
  replay_request_ordering: "contract_expected_replay_order",
  resource_retrieval:
    "deny_all_network_file_search_environment_and_dynamic_fallback",
  source_separated_implementation_count_decimal: "2",
});
const RESOURCE_OVERRIDE_VECTOR_IDS = Object.freeze([
  "PH-0021",
  "PH-0022",
  "PH-0023",
  "PH-0024",
  "PH-0025",
  "PH-0026",
  "PH-0027",
  "PH-0028",
  "PH-0052",
  "PH-0055",
  "PH-0057",
  "PH-0064",
  "PH-0065",
]);
const PROBE_OVERRIDE_VECTOR_IDS = Object.freeze(["PH-0033"]);

class ConformanceError extends Error {
  constructor(code, detail = "") {
    super(detail === "" ? code : `${code}: ${detail}`);
    this.name = "ConformanceError";
    this.code = code;
  }
}

function deny(code, detail = "") {
  throw new ConformanceError(code, detail);
}

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value, expectedKeys) {
  if (!isRecord(value)) {
    return false;
  }
  const actual = Object.keys(value).sort();
  const expected = [...expectedKeys].sort();
  return (
    actual.length === expected.length &&
    actual.every((key, index) => key === expected[index])
  );
}

function stableStringify(value) {
  function sortValue(current) {
    if (Array.isArray(current)) {
      return current.map(sortValue);
    }
    if (!isRecord(current)) {
      return current;
    }
    const sorted = Object.create(null);
    for (const key of Object.keys(current).sort()) {
      sorted[key] = sortValue(current[key]);
    }
    return sorted;
  }
  return JSON.stringify(sortValue(value));
}

function pointerSegment(value) {
  return value.replaceAll("~", "~0").replaceAll("/", "~1");
}

function hasUnpairedSurrogate(value) {
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code >= 0xd800 && code <= 0xdbff) {
      if (index + 1 >= value.length) {
        return true;
      }
      const next = value.charCodeAt(index + 1);
      if (next < 0xdc00 || next > 0xdfff) {
        return true;
      }
      index += 1;
    } else if (code >= 0xdc00 && code <= 0xdfff) {
      return true;
    }
  }
  return false;
}

class StrictJsonParser {
  constructor(text) {
    this.text = text;
    this.index = 0;
    this.numberTokens = new Map();
    this.duplicateKeyObserved = false;
    this.unpairedSurrogateObserved = false;
  }

  parse() {
    this.skipWhitespace();
    const value = this.parseValue("");
    this.skipWhitespace();
    if (this.index !== this.text.length) {
      deny("ODEYA_PARSE_SYNTAX");
    }
    if (this.duplicateKeyObserved) {
      deny("ODEYA_PARSE_DUPLICATE_KEY");
    }
    if (this.unpairedSurrogateObserved) {
      deny("ODEYA_PARSE_UNPAIRED_SURROGATE");
    }
    return { value, numberTokens: this.numberTokens };
  }

  skipWhitespace() {
    while (
      this.index < this.text.length &&
      (this.text[this.index] === " " ||
        this.text[this.index] === "\t" ||
        this.text[this.index] === "\n" ||
        this.text[this.index] === "\r")
    ) {
      this.index += 1;
    }
  }

  parseValue(path) {
    this.skipWhitespace();
    if (this.index >= this.text.length) {
      deny("ODEYA_PARSE_SYNTAX");
    }
    const current = this.text[this.index];
    if (current === "{") {
      return this.parseObject(path);
    }
    if (current === "[") {
      return this.parseArray(path);
    }
    if (current === '"') {
      return this.parseString();
    }
    if (current === "t" && this.consumeLiteral("true")) {
      return true;
    }
    if (current === "f" && this.consumeLiteral("false")) {
      return false;
    }
    if (current === "n" && this.consumeLiteral("null")) {
      return null;
    }
    if (current === "-" || (current >= "0" && current <= "9")) {
      return this.parseNumber(path);
    }
    deny("ODEYA_PARSE_SYNTAX");
  }

  consumeLiteral(literal) {
    if (this.text.slice(this.index, this.index + literal.length) !== literal) {
      return false;
    }
    this.index += literal.length;
    return true;
  }

  parseObject(path) {
    const result = Object.create(null);
    const keys = new Set();
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === "}") {
      this.index += 1;
      return result;
    }
    while (this.index < this.text.length) {
      this.skipWhitespace();
      if (this.text[this.index] !== '"') {
        deny("ODEYA_PARSE_SYNTAX");
      }
      const key = this.parseString();
      if (keys.has(key)) {
        this.duplicateKeyObserved = true;
      }
      keys.add(key);
      this.skipWhitespace();
      if (this.text[this.index] !== ":") {
        deny("ODEYA_PARSE_SYNTAX");
      }
      this.index += 1;
      const childPath = `${path}/${pointerSegment(key)}`;
      result[key] = this.parseValue(childPath);
      this.skipWhitespace();
      if (this.text[this.index] === "}") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") {
        deny("ODEYA_PARSE_SYNTAX");
      }
      this.index += 1;
    }
    deny("ODEYA_PARSE_SYNTAX");
  }

  parseArray(path) {
    const result = [];
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === "]") {
      this.index += 1;
      return result;
    }
    let itemIndex = 0;
    while (this.index < this.text.length) {
      result.push(this.parseValue(`${path}/${itemIndex}`));
      itemIndex += 1;
      this.skipWhitespace();
      if (this.text[this.index] === "]") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") {
        deny("ODEYA_PARSE_SYNTAX");
      }
      this.index += 1;
    }
    deny("ODEYA_PARSE_SYNTAX");
  }

  parseString() {
    this.index += 1;
    let result = "";
    while (this.index < this.text.length) {
      const current = this.text[this.index];
      if (current === '"') {
        this.index += 1;
        if (hasUnpairedSurrogate(result)) {
          this.unpairedSurrogateObserved = true;
        }
        return result;
      }
      if (current === "\\") {
        this.index += 1;
        if (this.index >= this.text.length) {
          deny("ODEYA_PARSE_SYNTAX");
        }
        const escaped = this.text[this.index];
        const simpleEscapes = {
          '"': '"',
          "\\": "\\",
          "/": "/",
          b: "\b",
          f: "\f",
          n: "\n",
          r: "\r",
          t: "\t",
        };
        if (Object.hasOwn(simpleEscapes, escaped)) {
          result += simpleEscapes[escaped];
          this.index += 1;
          continue;
        }
        if (escaped !== "u") {
          deny("ODEYA_PARSE_SYNTAX");
        }
        const hex = this.text.slice(this.index + 1, this.index + 5);
        if (!/^[0-9a-fA-F]{4}$/u.test(hex)) {
          deny("ODEYA_PARSE_SYNTAX");
        }
        result += String.fromCharCode(Number.parseInt(hex, 16));
        this.index += 5;
        continue;
      }
      if (current.charCodeAt(0) < 0x20) {
        deny("ODEYA_PARSE_SYNTAX");
      }
      result += current;
      this.index += 1;
    }
    deny("ODEYA_PARSE_SYNTAX");
  }

  parseNumber(path) {
    const remainder = this.text.slice(this.index);
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/u.exec(
      remainder,
    );
    if (match === null) {
      deny("ODEYA_PARSE_SYNTAX");
    }
    const raw = match[0];
    const next = remainder[raw.length];
    if (
      next !== undefined &&
      next !== " " &&
      next !== "\t" &&
      next !== "\n" &&
      next !== "\r" &&
      next !== "," &&
      next !== "]" &&
      next !== "}"
    ) {
      deny("ODEYA_PARSE_SYNTAX");
    }
    const value = Number(raw);
    if (!Number.isFinite(value)) {
      deny("ODEYA_PARSE_SYNTAX");
    }
    this.numberTokens.set(path, raw);
    this.index += raw.length;
    return value;
  }
}

function parseStrictJson(rawBytes) {
  let text;
  try {
    text = new TextDecoder("utf-8", {
      fatal: true,
      ignoreBOM: true,
    }).decode(rawBytes);
  } catch {
    deny("ODEYA_PARSE_UTF8");
  }
  if (text.startsWith("\ufeff")) {
    deny("ODEYA_PARSE_BOM");
  }
  return new StrictJsonParser(text).parse();
}

function sha256(rawBytes) {
  return `sha256:${createHash("sha256").update(rawBytes).digest("hex")}`;
}

function byteCountDecimal(rawBytes) {
  return String(rawBytes.byteLength);
}

function readBoundInput(path) {
  const raw = readFileSync(path);
  const parsed = parseStrictJson(raw);
  return {
    raw,
    value: parsed.value,
    numberTokens: parsed.numberTokens,
    binding: {
      raw_sha256: sha256(raw),
      byte_count_decimal: byteCountDecimal(raw),
    },
  };
}

function decodeBase64(value) {
  if (
    typeof value !== "string" ||
    !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/u.test(
      value,
    )
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE");
  }
  const decoded = Buffer.from(value, "base64");
  if (decoded.toString("base64") !== value) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE");
  }
  return decoded;
}

function isCanonicalDecimal(value) {
  return typeof value === "string" && DECIMAL_PATTERN.test(value);
}

function isSha256(value) {
  return typeof value === "string" && SHA256_PATTERN.test(value);
}

function parseArguments(argv) {
  const expectedFlags = new Set([
    "--vectors",
    "--contract",
    "--source-manifest",
  ]);
  const values = Object.create(null);
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (
      !expectedFlags.has(flag) ||
      typeof value !== "string" ||
      value.length === 0 ||
      Object.hasOwn(values, flag)
    ) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid CLI arguments");
    }
    values[flag] = value;
  }
  if (
    argv.length !== 6 ||
    [...expectedFlags].some((flag) => !Object.hasOwn(values, flag))
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid CLI arguments");
  }
  return values;
}

function validateFalseBoundary(value, expectedKeys, expectedCount) {
  if (
    !exactKeys(value, expectedKeys) ||
    Object.keys(value).length !== expectedCount
  ) {
    return false;
  }
  return expectedKeys.every((key) => value[key] === false);
}

function sameFalseBoundary(actual, expected) {
  const keys = Object.keys(expected);
  return validateFalseBoundary(actual, keys, keys.length);
}

function validateVectorsRoot(root) {
  if (
    !exactKeys(root, [
      "schema_version",
      "artifact_class",
      "vector_set_id",
      "vector_count_decimal",
      "vectors",
    ]) ||
    root.schema_version !== "0.1.0" ||
    root.artifact_class !==
      "prq_002d_schema_registry_prehash_vector_set" ||
    typeof root.vector_set_id !== "string" ||
    root.vector_set_id.length === 0 ||
    !isCanonicalDecimal(root.vector_count_decimal) ||
    !Array.isArray(root.vectors) ||
    BigInt(root.vector_count_decimal) !== BigInt(root.vectors.length)
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid vector-set root");
  }
  const ids = new Set();
  const sequences = new Set();
  for (const vector of root.vectors) {
    if (
      !isRecord(vector) ||
      typeof vector.vector_id !== "string" ||
      !VECTOR_ID_PATTERN.test(vector.vector_id) ||
      !isCanonicalDecimal(vector.sequence_index_decimal) ||
      !Array.isArray(vector.files)
    ) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid vector frame");
    }
    if (ids.has(vector.vector_id) || sequences.has(vector.sequence_index_decimal)) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "duplicate vector identity");
    }
    ids.add(vector.vector_id);
    sequences.add(vector.sequence_index_decimal);
  }
}

function validateContract(contract) {
  if (
    !exactKeys(contract, [
      "schema_version",
      "artifact_class",
      "contract_id",
      "suite_id",
      "status",
      "decision_ref",
      "predecessor_checkpoint",
      "predecessor_evidence_bindings",
      "expected_resource_count_decimal",
      "safe_bundle_binding",
      "expected_resources",
      "preparse_resource_binding_overrides",
      "preparse_probe_binding_overrides",
      "expected_replays",
      "expected_reference_edges",
      "evaluation_contract",
      "authority_boundary",
      "claim_boundary",
    ]) ||
    contract.schema_version !== "0.1.0" ||
    contract.artifact_class !==
      "prq_002d_schema_registry_prehash_contract" ||
    contract.suite_id !== SUITE_ID ||
    contract.contract_id !== CONTRACT_ID ||
    contract.status !==
      "architecture_only_non_product_nonidentity_candidate" ||
    contract.decision_ref !==
      "docs/decisions/0102-prove-non-product-prehash-schema-registry-replay.md" ||
    stableStringify(contract.predecessor_checkpoint) !==
      stableStringify({
        commit: "d3ec64f3abfc64467c0bc3bfae330d86e2af89b2",
        tree: "69304534a61a7c5d085d183d847285a181eaabfc",
      }) ||
    !Array.isArray(contract.predecessor_evidence_bindings) ||
    contract.predecessor_evidence_bindings.length !== 2 ||
    contract.expected_resource_count_decimal !== "2" ||
    !exactKeys(contract.safe_bundle_binding, [
      "repository_path",
      "raw_sha256",
      "byte_count_decimal",
    ]) ||
    typeof contract.safe_bundle_binding.repository_path !== "string" ||
    !isSha256(contract.safe_bundle_binding.raw_sha256) ||
    !isCanonicalDecimal(
      contract.safe_bundle_binding.byte_count_decimal,
    ) ||
    stableStringify(contract.evaluation_contract) !==
      stableStringify(EVALUATION_CONTRACT) ||
    !Array.isArray(contract.expected_resources) ||
    contract.expected_resources.length !== 2 ||
    !Array.isArray(contract.preparse_resource_binding_overrides) ||
    contract.preparse_resource_binding_overrides.length !==
      RESOURCE_OVERRIDE_VECTOR_IDS.length ||
    !Array.isArray(contract.preparse_probe_binding_overrides) ||
    contract.preparse_probe_binding_overrides.length !==
      PROBE_OVERRIDE_VECTOR_IDS.length ||
    !Array.isArray(contract.expected_replays) ||
    contract.expected_replays.length !== 2 ||
    !Array.isArray(contract.expected_reference_edges) ||
    contract.expected_reference_edges.length !== 1 ||
    !sameFalseBoundary(contract.authority_boundary, AUTHORITY_BOUNDARY) ||
    !sameFalseBoundary(contract.claim_boundary, ROOT_CLAIM_BOUNDARY)
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid contract root");
  }
  const expectedPredecessorBindings = [
    [
      "raw_number_decision",
      "docs/decisions/0101-require-raw-number-token-provenance-before-profile-conformance.md",
    ],
    [
      "raw_number_comparison",
      "tests/product-identity-raw-number-typing/results/comparison-receipt.json",
    ],
  ];
  for (
    let index = 0;
    index < expectedPredecessorBindings.length;
    index += 1
  ) {
    const binding = contract.predecessor_evidence_bindings[index];
    const [role, path] = expectedPredecessorBindings[index];
    if (
      !exactKeys(binding, [
        "role",
        "repository_path",
        "raw_sha256",
        "byte_count_decimal",
      ]) ||
      binding.role !== role ||
      binding.repository_path !== path ||
      !isSha256(binding.raw_sha256) ||
      !isCanonicalDecimal(binding.byte_count_decimal)
    ) {
      deny(
        "ODEYA_CONFORMANCE_FRAME_SHAPE",
        "invalid predecessor binding",
      );
    }
  }
  const resourceIds = new Set();
  const resourceBlobIds = new Set();
  const memberKeys = new Set();
  for (const resource of contract.expected_resources) {
    if (
      !exactKeys(resource, [
        "schema_id",
        "semantic_version",
        "member_key",
        "resource_blob_id",
        "repository_path",
        "resource_raw_sha256",
        "resource_byte_count_decimal",
      ]) ||
      typeof resource.schema_id !== "string" ||
      !resource.schema_id.startsWith(TEST_SCHEMA_ID_PREFIX) ||
      typeof resource.semantic_version !== "string" ||
      !VERSION_PATTERN.test(resource.semantic_version) ||
      resource.member_key !==
        `${resource.schema_id}@${resource.semantic_version}` ||
      !MEMBER_KEY_PATTERN.test(resource.member_key) ||
      typeof resource.resource_blob_id !== "string" ||
      resource.resource_blob_id.length === 0 ||
      typeof resource.repository_path !== "string" ||
      resource.repository_path.length === 0 ||
      !isSha256(resource.resource_raw_sha256) ||
      !isCanonicalDecimal(resource.resource_byte_count_decimal) ||
      resourceIds.has(resource.schema_id) ||
      resourceBlobIds.has(resource.resource_blob_id) ||
      memberKeys.has(resource.member_key)
    ) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid expected resource");
    }
    resourceIds.add(resource.schema_id);
    resourceBlobIds.add(resource.resource_blob_id);
    memberKeys.add(resource.member_key);
  }
  const orderedContractKeys = contract.expected_resources.map(
    (resource) => resource.member_key,
  );
  if (
    compareUtf8(orderedContractKeys[0], orderedContractKeys[1]) >= 0
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "unordered expected resources");
  }
  const safeResourceBindings = new Map(
    contract.expected_resources.map((resource) => [
      resource.resource_blob_id,
      {
        raw_sha256: resource.resource_raw_sha256,
        byte_count_decimal: resource.resource_byte_count_decimal,
      },
    ]),
  );
  for (
    let index = 0;
    index < RESOURCE_OVERRIDE_VECTOR_IDS.length;
    index += 1
  ) {
    const override = contract.preparse_resource_binding_overrides[index];
    if (
      !exactKeys(override, [
        "vector_id",
        "resource_blob_id",
        "resource_raw_sha256",
        "resource_byte_count_decimal",
      ]) ||
      override.vector_id !== RESOURCE_OVERRIDE_VECTOR_IDS[index] ||
      override.resource_blob_id !== "resource-001" ||
      !safeResourceBindings.has(override.resource_blob_id) ||
      !isSha256(override.resource_raw_sha256) ||
      !isCanonicalDecimal(override.resource_byte_count_decimal) ||
      stableStringify({
        raw_sha256: override.resource_raw_sha256,
        byte_count_decimal: override.resource_byte_count_decimal,
      }) ===
        stableStringify(
          safeResourceBindings.get(override.resource_blob_id),
        )
    ) {
      deny(
        "ODEYA_CONFORMANCE_FRAME_SHAPE",
        "invalid resource preparse override",
      );
    }
  }
  const replayUris = new Set();
  const probeBlobIds = new Set();
  for (const replay of contract.expected_replays) {
    if (
      !exactKeys(replay, [
        "request_uri",
        "probe_blob_id",
        "repository_path",
        "probe_raw_sha256",
        "probe_byte_count_decimal",
      ]) ||
      typeof replay.request_uri !== "string" ||
      !resourceIds.has(replay.request_uri) ||
      typeof replay.probe_blob_id !== "string" ||
      replay.probe_blob_id.length === 0 ||
      typeof replay.repository_path !== "string" ||
      replay.repository_path.length === 0 ||
      !isSha256(replay.probe_raw_sha256) ||
      !isCanonicalDecimal(replay.probe_byte_count_decimal) ||
      replayUris.has(replay.request_uri) ||
      probeBlobIds.has(replay.probe_blob_id)
    ) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid expected replay");
    }
    replayUris.add(replay.request_uri);
    probeBlobIds.add(replay.probe_blob_id);
  }
  if (
    contract.expected_replays.some(
      (replay, index) =>
        replay.request_uri !==
        contract.expected_resources[index].schema_id,
    )
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "unordered expected replays");
  }
  const safeProbeBindings = new Map(
    contract.expected_replays.map((replay) => [
      replay.probe_blob_id,
      {
        raw_sha256: replay.probe_raw_sha256,
        byte_count_decimal: replay.probe_byte_count_decimal,
      },
    ]),
  );
  for (
    let index = 0;
    index < PROBE_OVERRIDE_VECTOR_IDS.length;
    index += 1
  ) {
    const override = contract.preparse_probe_binding_overrides[index];
    if (
      !exactKeys(override, [
        "vector_id",
        "probe_blob_id",
        "probe_raw_sha256",
        "probe_byte_count_decimal",
      ]) ||
      override.vector_id !== PROBE_OVERRIDE_VECTOR_IDS[index] ||
      override.probe_blob_id !== "probe-001" ||
      !isSha256(override.probe_raw_sha256) ||
      !isCanonicalDecimal(override.probe_byte_count_decimal) ||
      !safeProbeBindings.has(override.probe_blob_id) ||
      stableStringify({
        raw_sha256: override.probe_raw_sha256,
        byte_count_decimal: override.probe_byte_count_decimal,
      }) === stableStringify(safeProbeBindings.get(override.probe_blob_id))
    ) {
      deny(
        "ODEYA_CONFORMANCE_FRAME_SHAPE",
        "invalid probe preparse override",
      );
    }
  }
  const edge = contract.expected_reference_edges[0];
  if (
    !exactKeys(edge, [
      "source_schema_id",
      "keyword_location",
      "target_schema_id",
    ]) ||
    edge.source_schema_id !== contract.expected_resources[0].schema_id ||
    edge.target_schema_id !== contract.expected_resources[1].schema_id ||
    edge.keyword_location !== "/properties/peer/$ref"
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid expected reference edge");
  }
}

function validateSourceManifest(manifest) {
  if (
    !exactKeys(manifest, [
      "schema_version",
      "artifact_class",
      "suite_id",
      "role",
      "implementation_id",
      "language",
      "runtime_version",
      "parser_strategy",
      "schema_strategy",
      "source_file_count_decimal",
      "source_files",
      "allowed_input_roles",
      "private_expectation_consumption_allowed",
      "peer_source_consumption_allowed",
      "peer_result_consumption_allowed",
      "network_access_requested",
      "filesystem_isolation_proven",
    ]) ||
    manifest.schema_version !== "0.1.0" ||
    manifest.artifact_class !==
      "prq_002d_schema_registry_prehash_source_manifest" ||
    manifest.role !== "node" ||
    manifest.implementation_id !== IMPLEMENTATION_ID ||
    manifest.language !== "JavaScript" ||
    manifest.runtime_version !== REQUIRED_NODE_VERSION ||
    manifest.parser_strategy !==
      "recursive_descent_strict_json_with_raw_count_token" ||
    manifest.schema_strategy !== "ajv_8_20_0_strict_preloaded_only" ||
    manifest.source_file_count_decimal !== "4" ||
    !Array.isArray(manifest.source_files) ||
    manifest.source_files.length !== 4 ||
    !Array.isArray(manifest.allowed_input_roles) ||
    JSON.stringify(manifest.allowed_input_roles) !==
      JSON.stringify(["vectors", "contract", "source_manifest"]) ||
    manifest.private_expectation_consumption_allowed !== false ||
    manifest.peer_source_consumption_allowed !== false ||
    manifest.peer_result_consumption_allowed !== false ||
    manifest.network_access_requested !== false ||
    manifest.filesystem_isolation_proven !== false
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid source manifest");
  }
  const expectedSourcePaths = new Map([
    [
      "runner",
      "tests/schema-registry-prehash-replay/node/runner.mjs",
    ],
    [
      "package_manifest",
      "tests/schema-registry-prehash-replay/node/package.json",
    ],
    [
      "package_lock",
      "tests/schema-registry-prehash-replay/node/package-lock.json",
    ],
    [
      "toolchain_installer",
      "scripts/ci/install-node.sh",
    ],
  ]);
  const seenRoles = new Set();
  for (const sourceFile of manifest.source_files) {
    if (
      !exactKeys(sourceFile, [
        "role",
        "repository_path",
        "raw_sha256",
        "byte_count_decimal",
      ]) ||
      !expectedSourcePaths.has(sourceFile.role) ||
      sourceFile.repository_path !== expectedSourcePaths.get(sourceFile.role) ||
      !isSha256(sourceFile.raw_sha256) ||
      !isCanonicalDecimal(sourceFile.byte_count_decimal) ||
      seenRoles.has(sourceFile.role)
    ) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE", "invalid source binding");
    }
    seenRoles.add(sourceFile.role);
  }
}

function validateVectorFiles(vector) {
  if (
    !exactKeys(vector, [
      "sequence_index_decimal",
      "vector_id",
      "files",
    ])
  ) {
    deny("ODEYA_CONFORMANCE_FRAME_SHAPE");
  }
  const files = new Map();
  for (const file of vector.files) {
    if (
      !exactKeys(file, [
        "blob_id",
        "media_type",
        "raw_sha256",
        "byte_count_decimal",
        "content_base64",
      ]) ||
      typeof file.blob_id !== "string" ||
      file.blob_id.length === 0 ||
      file.media_type !== "application/json" ||
      !isSha256(file.raw_sha256) ||
      !isCanonicalDecimal(file.byte_count_decimal) ||
      files.has(file.blob_id)
    ) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE");
    }
    files.set(file.blob_id, {
      frame: file,
      raw: decodeBase64(file.content_base64),
    });
  }
  return files;
}

function verifyFrameBinding(file, countCode, digestCode) {
  if (byteCountDecimal(file.raw) !== file.frame.byte_count_decimal) {
    deny(countCode);
  }
  if (sha256(file.raw) !== file.frame.raw_sha256) {
    deny(digestCode);
  }
}

function compareUtf8(left, right) {
  return Buffer.compare(Buffer.from(left, "utf8"), Buffer.from(right, "utf8"));
}

function inspectSchemaKeywords(value, topLevel = true) {
  if (Array.isArray(value)) {
    for (const item of value) {
      inspectSchemaKeywords(item, false);
    }
    return;
  }
  if (!isRecord(value)) {
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    if (!topLevel && key === "$id") {
      deny("ODEYA_PREHASH_RESOURCE_SCHEMA");
    }
    if (
      key === "$dynamicRef" ||
      key === "$dynamicAnchor" ||
      key === "$anchor"
    ) {
      deny("ODEYA_PREHASH_RESOURCE_SCHEMA");
    }
    if (
      key === "$ref" &&
      (typeof child !== "string" ||
        !child.startsWith(
          "urn:odeya:architecture-test:prq-002d:",
        ) ||
        child.includes("#"))
    ) {
      deny("ODEYA_PREHASH_RESOURCE_SCHEMA");
    }
    inspectSchemaKeywords(child, false);
  }
}

function collectReferenceEdges(
  value,
  sourceSchemaId,
  pointer = "",
) {
  const edges = [];
  if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      edges.push(
        ...collectReferenceEdges(
          value[index],
          sourceSchemaId,
          `${pointer}/${index}`,
        ),
      );
    }
    return edges;
  }
  if (!isRecord(value)) {
    return edges;
  }
  for (const [key, child] of Object.entries(value)) {
    const location = `${pointer}/${pointerSegment(key)}`;
    if (key === "$ref" && typeof child === "string") {
      edges.push({
        source_schema_id: sourceSchemaId,
        keyword_location: location,
        target_schema_id: child,
      });
    }
    edges.push(
      ...collectReferenceEdges(
        child,
        sourceSchemaId,
        location,
      ),
    );
  }
  return edges;
}

function memberShapeIsValid(member) {
  return (
    exactKeys(member, [
      "member_key",
      "schema_id",
      "semantic_version",
      "resource_raw_sha256",
      "resource_byte_count_decimal",
    ]) &&
    typeof member.member_key === "string" &&
    MEMBER_KEY_PATTERN.test(member.member_key) &&
    typeof member.schema_id === "string" &&
    member.schema_id.startsWith(TEST_SCHEMA_ID_PREFIX) &&
    MEMBER_KEY_PATTERN.test(member.schema_id) &&
    typeof member.semantic_version === "string" &&
    VERSION_PATTERN.test(member.semantic_version) &&
    isSha256(member.resource_raw_sha256) &&
    isCanonicalDecimal(member.resource_byte_count_decimal)
  );
}

function resolverShapeIsValid(resolver) {
  return (
    exactKeys(resolver, [
      "request_uri",
      "resource_blob_id",
      "resource_raw_sha256",
      "resource_byte_count_decimal",
    ]) &&
    typeof resolver.request_uri === "string" &&
    resolver.request_uri.startsWith(TEST_SCHEMA_ID_PREFIX) &&
    typeof resolver.resource_blob_id === "string" &&
    resolver.resource_blob_id.length > 0 &&
    isSha256(resolver.resource_raw_sha256) &&
    isCanonicalDecimal(resolver.resource_byte_count_decimal)
  );
}

function replayShapeIsValid(replay) {
  return (
    exactKeys(replay, ["request_uri", "probe_blob_id"]) &&
    typeof replay.request_uri === "string" &&
    replay.request_uri.startsWith(TEST_SCHEMA_ID_PREFIX) &&
    typeof replay.probe_blob_id === "string" &&
    replay.probe_blob_id.length > 0
  );
}

function preparseResourceBinding(contract, vectorId, expected) {
  const override = contract.preparse_resource_binding_overrides.find(
    (candidate) =>
      candidate.vector_id === vectorId &&
      candidate.resource_blob_id === expected.resource_blob_id,
  );
  return override === undefined
    ? {
        raw_sha256: expected.resource_raw_sha256,
        byte_count_decimal: expected.resource_byte_count_decimal,
      }
    : {
        raw_sha256: override.resource_raw_sha256,
        byte_count_decimal: override.resource_byte_count_decimal,
      };
}

function preparseProbeBinding(contract, vectorId, expected) {
  const override = contract.preparse_probe_binding_overrides.find(
    (candidate) =>
      candidate.vector_id === vectorId &&
      candidate.probe_blob_id === expected.probe_blob_id,
  );
  return override === undefined
    ? {
        raw_sha256: expected.probe_raw_sha256,
        byte_count_decimal: expected.probe_byte_count_decimal,
      }
    : {
        raw_sha256: override.probe_raw_sha256,
        byte_count_decimal: override.probe_byte_count_decimal,
      };
}

function makeBaseRow(vector, bundleFile) {
  return {
    sequence_index_decimal: vector.sequence_index_decimal,
    vector_id: vector.vector_id,
    bundle_raw_sha256: bundleFile === undefined ? null : sha256(bundleFile.raw),
    bundle_byte_count_decimal:
      bundleFile === undefined ? null : byteCountDecimal(bundleFile.raw),
    declared_member_count_raw_token: null,
    final_disposition: "refused",
    final_code: "ODEYA_CONFORMANCE_FRAME_SHAPE",
    ordered_member_keys: [],
    resolved_replay_bindings: [],
    validated_probe_count_decimal: null,
  };
}

function evaluateVector(vector, contract) {
  let files;
  let bundleFile;
  let row = makeBaseRow(vector, undefined);
  try {
    files = validateVectorFiles(vector);
    bundleFile = files.get("bundle");
    row = makeBaseRow(vector, bundleFile);
    if (bundleFile === undefined) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE");
    }
    verifyFrameBinding(
      bundleFile,
      "ODEYA_CONFORMANCE_FRAME_SHAPE",
      "ODEYA_CONFORMANCE_FRAME_SHAPE",
    );

    const parsedBundle = parseStrictJson(bundleFile.raw);
    const bundle = parsedBundle.value;
    const countToken = parsedBundle.numberTokens.get(
      "/declared_member_count",
    );
    row.declared_member_count_raw_token = countToken ?? null;
    if (
      !exactKeys(bundle, [
        "schema_version",
        "artifact_class",
        "scope",
        "declared_member_count",
        "members",
        "resolver_catalog",
        "replay_requests",
        "authority_boundary",
      ]) ||
      bundle.schema_version !== "0.1.0" ||
      bundle.artifact_class !==
        "prq_002d_non_product_schema_registry_prehash_bundle" ||
      bundle.scope !== "architecture_test_only_non_product_nonidentity"
    ) {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE");
    }

    if (typeof bundle.declared_member_count !== "number") {
      deny("ODEYA_CONFORMANCE_FRAME_SHAPE");
    }
    if (
      typeof countToken === "string" &&
      countToken.startsWith("-") &&
      Object.is(bundle.declared_member_count, -0)
    ) {
      deny("ODEYA_NUMBER_NEGATIVE_ZERO");
    }
    if (
      typeof countToken !== "string" ||
      !DECIMAL_PATTERN.test(countToken)
    ) {
      deny("ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED");
    }
    if (!Number.isSafeInteger(bundle.declared_member_count)) {
      deny("ODEYA_NUMBER_DOMAIN");
    }

    if (
      !sameFalseBoundary(
        bundle.authority_boundary,
        AUTHORITY_BOUNDARY,
      )
    ) {
      deny("ODEYA_PREHASH_AUTHORITY_BOUNDARY");
    }

    if (
      bundle.declared_member_count !== 2 ||
      String(bundle.declared_member_count) !==
        contract.expected_resource_count_decimal
    ) {
      deny("ODEYA_PREHASH_COUNT");
    }

    if (
      !Array.isArray(bundle.members) ||
      bundle.members.length !== 2 ||
      !bundle.members.every(memberShapeIsValid) ||
      !Array.isArray(bundle.resolver_catalog) ||
      !Array.isArray(bundle.replay_requests)
    ) {
      deny("ODEYA_PREHASH_MEMBER_SHAPE");
    }

    const memberKeys = bundle.members.map((member) => member.member_key);
    if (new Set(memberKeys).size !== memberKeys.length) {
      deny("ODEYA_PREHASH_DUPLICATE_KEY");
    }
    for (let index = 1; index < memberKeys.length; index += 1) {
      if (compareUtf8(memberKeys[index - 1], memberKeys[index]) >= 0) {
        deny("ODEYA_PREHASH_ORDER");
      }
    }

    if (
      bundle.resolver_catalog.length !== 2 ||
      !bundle.resolver_catalog.every(resolverShapeIsValid)
    ) {
      deny("ODEYA_PREHASH_RESOLVER_INVENTORY");
    }
    const resolverByUri = new Map();
    for (const resolver of bundle.resolver_catalog) {
      if (resolverByUri.has(resolver.request_uri)) {
        deny("ODEYA_PREHASH_RESOLVER_INVENTORY");
      }
      resolverByUri.set(resolver.request_uri, resolver);
    }
    const expectedResourceUris = contract.expected_resources.map(
      (resource) => resource.schema_id,
    );
    const expectedResourceIds = new Set(expectedResourceUris);
    if (
      resolverByUri.size !== expectedResourceIds.size ||
      [...resolverByUri.keys()].some(
        (requestUri) => !expectedResourceIds.has(requestUri),
      ) ||
      bundle.resolver_catalog.some(
        (resolver, index) =>
          resolver.request_uri !== expectedResourceUris[index],
      )
    ) {
      deny("ODEYA_PREHASH_RESOLVER_INVENTORY");
    }

    const expectedBlobIds = new Set([
      "bundle",
      ...contract.expected_resources.map(
        (resource) => resource.resource_blob_id,
      ),
      ...contract.expected_replays.map((replay) => replay.probe_blob_id),
    ]);
    if (
      files.size !== expectedBlobIds.size ||
      [...files.keys()].some((blobId) => !expectedBlobIds.has(blobId))
    ) {
      deny("ODEYA_PREHASH_RESOLVER_INVENTORY");
    }

    const ajv = new Ajv2020({
      strict: true,
      allErrors: false,
      coerceTypes: false,
      useDefaults: false,
      removeAdditional: false,
      validateSchema: true,
      validateFormats: false,
      loadSchema: undefined,
      ownProperties: true,
      messages: false,
      verbose: false,
    });
    const schemaRecords = [];
    for (
      let resourceIndex = 0;
      resourceIndex < contract.expected_resources.length;
      resourceIndex += 1
    ) {
      const expected = contract.expected_resources[resourceIndex];
      const resourceFile = files.get(expected.resource_blob_id);
      if (resourceFile === undefined) {
        deny("ODEYA_PREHASH_RESOURCE_BYTE_COUNT");
      }
      verifyFrameBinding(
        resourceFile,
        "ODEYA_PREHASH_RESOURCE_BYTE_COUNT",
        "ODEYA_PREHASH_RESOURCE_RAW_DIGEST",
      );
      const member = bundle.members[resourceIndex];
      if (
        member.resource_byte_count_decimal !==
          byteCountDecimal(resourceFile.raw)
      ) {
        deny("ODEYA_PREHASH_RESOURCE_BYTE_COUNT");
      }
      if (member.resource_raw_sha256 !== sha256(resourceFile.raw)) {
        deny("ODEYA_PREHASH_RESOURCE_RAW_DIGEST");
      }
      const resolver = bundle.resolver_catalog[resourceIndex];
      if (
        resolver.request_uri !== expected.schema_id ||
        resolver.resource_blob_id !== expected.resource_blob_id
      ) {
        deny("ODEYA_PREHASH_RESOLVER_TARGET");
      }
      if (
        resolver.resource_byte_count_decimal !==
        byteCountDecimal(resourceFile.raw)
      ) {
        deny("ODEYA_PREHASH_RESOURCE_BYTE_COUNT");
      }
      if (resolver.resource_raw_sha256 !== sha256(resourceFile.raw)) {
        deny("ODEYA_PREHASH_RESOURCE_RAW_DIGEST");
      }
      const authoritativeResourceBinding = preparseResourceBinding(
        contract,
        vector.vector_id,
        expected,
      );
      if (
        byteCountDecimal(resourceFile.raw) !==
          authoritativeResourceBinding.byte_count_decimal ||
        sha256(resourceFile.raw) !==
          authoritativeResourceBinding.raw_sha256
      ) {
        deny("ODEYA_PREHASH_RESOLVER_TARGET");
      }

      let parsedResource;
      try {
        parsedResource = parseStrictJson(resourceFile.raw).value;
      } catch (error) {
        if (error instanceof ConformanceError) {
          deny("ODEYA_PREHASH_RESOURCE_PARSE");
        }
        throw error;
      }
      if (!isRecord(parsedResource)) {
        deny("ODEYA_PREHASH_RESOURCE_PARSE");
      }
      if (parsedResource.$schema !== DRAFT_2020_12_URI) {
        deny("ODEYA_PREHASH_RESOURCE_DIALECT");
      }
      inspectSchemaKeywords(parsedResource, true);
      const expectedReferenceEdges =
        contract.expected_reference_edges.filter(
          (edge) => edge.source_schema_id === expected.schema_id,
        );
      if (
        stableStringify(
          collectReferenceEdges(parsedResource, expected.schema_id),
        ) !== stableStringify(expectedReferenceEdges)
      ) {
        deny("ODEYA_PREHASH_RESOURCE_SCHEMA");
      }
      if (
        typeof parsedResource.$id !== "string" ||
        parsedResource.$id !== expected.schema_id
      ) {
        deny("ODEYA_PREHASH_RESOURCE_ID");
      }
      const bodyVersion =
        isRecord(parsedResource.properties) &&
        isRecord(parsedResource.properties.schema_version)
          ? parsedResource.properties.schema_version.const
          : undefined;
      const idTerminal = parsedResource.$id.split(":").at(-1);
      if (
        typeof bodyVersion !== "string" ||
        !VERSION_PATTERN.test(bodyVersion) ||
        bodyVersion !== expected.semantic_version ||
        idTerminal !== bodyVersion
      ) {
        deny("ODEYA_PREHASH_RESOURCE_VERSION");
      }
      try {
        if (ajv.validateSchema(parsedResource) !== true) {
          deny("ODEYA_PREHASH_RESOURCE_SCHEMA");
        }
      } catch (error) {
        if (
          error instanceof ConformanceError &&
          error.code === "ODEYA_PREHASH_RESOURCE_SCHEMA"
        ) {
          throw error;
        }
        deny("ODEYA_PREHASH_RESOURCE_SCHEMA");
      }
      const derivedKey = `${parsedResource.$id}@${bodyVersion}`;
      if (member.schema_id !== parsedResource.$id) {
        deny("ODEYA_PREHASH_RESOURCE_ID");
      }
      if (member.semantic_version !== bodyVersion) {
        deny("ODEYA_PREHASH_RESOURCE_VERSION");
      }
      if (
        member.member_key !== derivedKey ||
        expected.member_key !== derivedKey
      ) {
        deny("ODEYA_PREHASH_KEY_BODY");
      }
      schemaRecords.push({
        expected,
        schema: parsedResource,
        raw: resourceFile.raw,
      });
    }

    for (const record of schemaRecords) {
      try {
        ajv.addSchema(record.schema, record.expected.schema_id);
      } catch (error) {
        if (
          error instanceof ConformanceError &&
          error.code === "ODEYA_PREHASH_RESOURCE_SCHEMA"
        ) {
          throw error;
        }
        deny("ODEYA_PREHASH_RESOURCE_SCHEMA");
      }
    }

    if (
      bundle.replay_requests.length !== contract.expected_replays.length ||
      !bundle.replay_requests.every(replayShapeIsValid)
    ) {
      deny("ODEYA_PREHASH_REPLAY_REQUEST");
    }
    const replayByUri = new Map();
    for (const replay of bundle.replay_requests) {
      if (replayByUri.has(replay.request_uri)) {
        deny("ODEYA_PREHASH_REPLAY_REQUEST");
      }
      replayByUri.set(replay.request_uri, replay);
    }
    const expectedReplayUris = new Set(
      contract.expected_replays.map((replay) => replay.request_uri),
    );
    if (
      replayByUri.size !== expectedReplayUris.size ||
      [...replayByUri.keys()].some(
        (requestUri) => !expectedReplayUris.has(requestUri),
      ) ||
      bundle.replay_requests.some(
        (replay, index) =>
          replay.request_uri !==
          contract.expected_replays[index].request_uri ||
          replay.probe_blob_id !==
          contract.expected_replays[index].probe_blob_id,
      )
    ) {
      deny("ODEYA_PREHASH_REPLAY_REQUEST");
    }

    const resolvedReplayBindings = [];
    for (const expectedReplay of contract.expected_replays) {
      const replay = replayByUri.get(expectedReplay.request_uri);
      if (
        replay === undefined ||
        replay.probe_blob_id !== expectedReplay.probe_blob_id
      ) {
        deny("ODEYA_PREHASH_REPLAY_REQUEST");
      }
      const probeFile = files.get(expectedReplay.probe_blob_id);
      if (probeFile === undefined) {
        deny("ODEYA_PREHASH_REPLAY_VALIDATION");
      }
      if (
        byteCountDecimal(probeFile.raw) !==
          probeFile.frame.byte_count_decimal ||
        sha256(probeFile.raw) !== probeFile.frame.raw_sha256
      ) {
        deny("ODEYA_PREHASH_REPLAY_VALIDATION");
      }
      const authoritativeProbeBinding = preparseProbeBinding(
        contract,
        vector.vector_id,
        expectedReplay,
      );
      if (
        byteCountDecimal(probeFile.raw) !==
          authoritativeProbeBinding.byte_count_decimal ||
        sha256(probeFile.raw) !== authoritativeProbeBinding.raw_sha256
      ) {
        deny("ODEYA_PREHASH_REPLAY_REQUEST");
      }
      let probe;
      try {
        probe = parseStrictJson(probeFile.raw).value;
      } catch (error) {
        if (error instanceof ConformanceError) {
          deny("ODEYA_PREHASH_REPLAY_VALIDATION");
        }
        throw error;
      }
      let validate;
      try {
        validate = ajv.getSchema(expectedReplay.request_uri);
      } catch {
        deny("ODEYA_PREHASH_REPLAY_VALIDATION");
      }
      if (typeof validate !== "function" || validate(probe) !== true) {
        deny("ODEYA_PREHASH_REPLAY_VALIDATION");
      }
      const resolver = resolverByUri.get(expectedReplay.request_uri);
      resolvedReplayBindings.push({
        request_uri: expectedReplay.request_uri,
        resolved_schema_id: expectedReplay.request_uri,
        resource_blob_id: resolver.resource_blob_id,
        resource_byte_count_decimal:
          resolver.resource_byte_count_decimal,
        resource_raw_sha256: resolver.resource_raw_sha256,
      });
    }

    row.final_disposition = "accepted";
    row.final_code = "ODEYA_PREHASH_REPLAY_ACCEPTED";
    row.ordered_member_keys = memberKeys;
    row.resolved_replay_bindings = resolvedReplayBindings;
    row.validated_probe_count_decimal = String(
      resolvedReplayBindings.length,
    );
    return row;
  } catch (error) {
    if (!(error instanceof ConformanceError)) {
      throw error;
    }
    row.final_disposition = "refused";
    row.final_code = error.code;
    row.ordered_member_keys = [];
    row.resolved_replay_bindings = [];
    row.validated_probe_count_decimal = null;
    return row;
  }
}

function main() {
  if (process.versions.node !== REQUIRED_NODE_VERSION) {
    deny(
      "ODEYA_CONFORMANCE_FRAME_SHAPE",
      `Node ${REQUIRED_NODE_VERSION} required; received ${process.versions.node}`,
    );
  }
  if (LOADED_AJV_VERSION !== REQUIRED_AJV_VERSION) {
    deny(
      "ODEYA_CONFORMANCE_FRAME_SHAPE",
      `Ajv ${REQUIRED_AJV_VERSION} required; received ${LOADED_AJV_VERSION}`,
    );
  }
  const args = parseArguments(process.argv.slice(2));
  const vectorsInput = readBoundInput(args["--vectors"]);
  const contractInput = readBoundInput(args["--contract"]);
  const sourceManifestInput = readBoundInput(args["--source-manifest"]);

  validateVectorsRoot(vectorsInput.value);
  validateContract(contractInput.value);
  validateSourceManifest(sourceManifestInput.value);

  const results = vectorsInput.value.vectors.map((vector) =>
    evaluateVector(vector, contractInput.value),
  );
  const output = {
    schema_version: "0.1.0",
    artifact_class:
      "prq_002d_schema_registry_prehash_observation",
    suite_id: contractInput.value.suite_id,
    implementation_id: IMPLEMENTATION_ID,
    vector_set_id: vectorsInput.value.vector_set_id,
    vector_count_decimal: vectorsInput.value.vector_count_decimal,
    input_bindings: {
      vectors: vectorsInput.binding,
      contract: contractInput.binding,
      source_manifest: sourceManifestInput.binding,
    },
    results,
    claim_boundary: ROOT_CLAIM_BOUNDARY,
  };
  process.stdout.write(`${stableStringify(output)}\n`);
}

try {
  main();
} catch (error) {
  if (error instanceof ConformanceError) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 2;
  } else {
    throw error;
  }
}
