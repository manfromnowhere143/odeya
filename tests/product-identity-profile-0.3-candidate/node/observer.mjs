#!/usr/bin/env node
/*
 * Source-distinct PRQ-002E artifact construction observer.
 *
 * This is not a JCS implementation or a JSON Schema evaluator. It inventories
 * exact bytes, raw number lexemes, identities, and literal type:number
 * assertions for comparison with the Python observation.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const SUITE_ID = "prq-002e-profile-0.3-construction.0001";
const OBSERVER_ID = "nodejs-native-construction-observer.0001";
const CHALLENGE_RE = /^challenge-v1:[0-9a-f]{64}$/;
const NUMBER_RE = /-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/y;
const INTEGER_RE = /^-?(?:0|[1-9][0-9]*)$/;
const DOMAIN_RE = /^odeya-[a-z0-9-]+-v[0-9]+$/;
const PROFILE_RE = /^urn:odeya:canonicalization:[a-z0-9.-]+$/;
const MIN_SAFE_INTEGER = -9007199254740991n;
const MAX_SAFE_INTEGER = 9007199254740991n;
const EXPECTED_ARTIFACTS = [
  ["schema_resource_record_schema", "schemas/schema-resource-record-v0-2.schema.json"],
  ["aggregate_state_subject_record_schema", "schemas/aggregate-state-subject-record-v0-2.schema.json"],
  ["reducer_contract_record_schema", "schemas/reducer-contract-record-v0-2.schema.json"],
  ["event_contract_record_schema", "schemas/event-contract-record-v0-2.schema.json"],
  ["ordered_member_map_commitment_schema", "schemas/ordered-member-map-commitment-v0-2.schema.json"],
  ["schema_registry_schema", "schemas/schema-registry-v0-9.schema.json"],
  ["aggregate_state_subject_registry_schema", "schemas/aggregate-state-subject-registry-v0-8.schema.json"],
  ["reducer_registry_schema", "schemas/reducer-registry-v0-8.schema.json"],
  ["event_contract_registry_schema", "schemas/event-contract-registry-v0-8.schema.json"],
  ["profile_core_schema", "schemas/canonicalization-profile-core-v0-7.schema.json"],
  ["profile_evidence_schema", "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json"],
  ["profile_migration_schema", "schemas/canonicalization-profile-migration-v0-2.schema.json"],
  ["profile_core", "architecture/canonicalization-profile-core-0.3-candidate.json"],
  ["profile_evidence", "architecture/canonicalization-profile-0.3-candidate-evidence.json"],
  ["profile_migration", "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json"],
];
const EXPECTED_MANIFEST_KEYS = [
  "answer_free",
  "artifact_class",
  "artifact_count",
  "artifacts",
  "authority_claim_allowed",
  "environment_path_discovery_allowed",
  "expectation_manifest_may_be_passed_to_observer",
  "expected_outcomes_included",
  "manifest_id",
  "network_access_allowed",
  "peer_result_may_be_passed_to_observer",
  "peer_results_included",
  "peer_source_may_be_passed_to_observer",
  "product_identity_computation_allowed",
  "schema_version",
  "suite_id",
];

function stableStringify(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
}

function sha256Lexical(raw) {
  return `sha256:${crypto.createHash("sha256").update(raw).digest("hex")}`;
}

function assertStrictJson(text, label) {
  /*
   * A source-distinct recursive syntax walk detects duplicate decoded object
   * names before JSON.parse materializes an object. JSON.parse remains the
   * independent value constructor after this walk succeeds.
   */
  let index = 0;
  function fail(message) {
    throw new Error(`${label}: ${message} at offset ${index}`);
  }
  function skipWhitespace() {
    while (index < text.length && /[\u0009\u000a\u000d\u0020]/.test(text[index])) {
      index += 1;
    }
  }
  function parseString() {
    if (text[index] !== '"') fail("expected string");
    const start = index;
    index += 1;
    let escaped = false;
    while (index < text.length) {
      const character = text[index];
      if (escaped) {
        if (character === "u") {
          const digits = text.slice(index + 1, index + 5);
          if (!/^[0-9a-fA-F]{4}$/.test(digits)) fail("invalid unicode escape");
          index += 5;
        } else {
          if (!'"\\/bfnrt'.includes(character)) fail("invalid escape");
          index += 1;
        }
        escaped = false;
        continue;
      }
      if (character === "\\") {
        escaped = true;
        index += 1;
        continue;
      }
      if (character === '"') {
        index += 1;
        return JSON.parse(text.slice(start, index));
      }
      if (character.charCodeAt(0) <= 0x1f) fail("unescaped control character");
      index += 1;
    }
    fail("unterminated string");
  }
  function parseLiteral(literal) {
    if (text.slice(index, index + literal.length) !== literal) {
      fail(`expected ${literal}`);
    }
    index += literal.length;
  }
  function parseNumber() {
    NUMBER_RE.lastIndex = index;
    const match = NUMBER_RE.exec(text);
    if (match === null || match.index !== index) fail("invalid number");
    index = NUMBER_RE.lastIndex;
  }
  function parseArray() {
    index += 1;
    skipWhitespace();
    if (text[index] === "]") {
      index += 1;
      return;
    }
    while (true) {
      parseValue();
      skipWhitespace();
      if (text[index] === "]") {
        index += 1;
        return;
      }
      if (text[index] !== ",") fail("expected array comma or close");
      index += 1;
      skipWhitespace();
    }
  }
  function parseObject() {
    index += 1;
    skipWhitespace();
    const keys = new Set();
    if (text[index] === "}") {
      index += 1;
      return;
    }
    while (true) {
      const key = parseString();
      if (keys.has(key)) fail(`duplicate object member ${JSON.stringify(key)}`);
      keys.add(key);
      skipWhitespace();
      if (text[index] !== ":") fail("expected object colon");
      index += 1;
      skipWhitespace();
      parseValue();
      skipWhitespace();
      if (text[index] === "}") {
        index += 1;
        return;
      }
      if (text[index] !== ",") fail("expected object comma or close");
      index += 1;
      skipWhitespace();
    }
  }
  function parseValue() {
    skipWhitespace();
    const character = text[index];
    if (character === "{") parseObject();
    else if (character === "[") parseArray();
    else if (character === '"') parseString();
    else if (character === "t") parseLiteral("true");
    else if (character === "f") parseLiteral("false");
    else if (character === "n") parseLiteral("null");
    else if (character === "-" || (character >= "0" && character <= "9")) parseNumber();
    else fail("unexpected value token");
  }
  skipWhitespace();
  parseValue();
  skipWhitespace();
  if (index !== text.length) fail("trailing data");
}

function parseArguments(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 2) {
    const name = argv[index];
    const value = argv[index + 1];
    if (!name?.startsWith("--") || value === undefined) {
      throw new Error("arguments must be closed --name value pairs");
    }
    result[name.slice(2)] = value;
  }
  for (const required of ["root", "manifest", "challenge"]) {
    if (typeof result[required] !== "string") {
      throw new Error(`missing --${required}`);
    }
  }
  return result;
}

function strictRepositoryFile(root, relative) {
  if (path.isAbsolute(relative) || relative.split("/").includes("..")) {
    throw new Error(`unsafe repository path: ${relative}`);
  }
  const lexical = path.join(root, relative);
  const info = fs.lstatSync(lexical);
  if (!info.isFile() || info.isSymbolicLink()) {
    throw new Error(`artifact is not a non-symlink regular file: ${relative}`);
  }
  const resolved = fs.realpathSync(lexical);
  const prefix = `${root}${path.sep}`;
  if (!resolved.startsWith(prefix)) {
    throw new Error(`artifact resolves outside repository: ${relative}`);
  }
  return fs.readFileSync(resolved);
}

function numberTokens(text) {
  const tokens = [];
  let index = 0;
  let inString = false;
  let escaped = false;
  while (index < text.length) {
    const character = text[index];
    if (inString) {
      if (escaped) {
        escaped = false;
      } else if (character === "\\") {
        escaped = true;
      } else if (character === '"') {
        inString = false;
      }
      index += 1;
      continue;
    }
    if (character === '"') {
      inString = true;
      index += 1;
      continue;
    }
    if (character === "-" || (character >= "0" && character <= "9")) {
      NUMBER_RE.lastIndex = index;
      const match = NUMBER_RE.exec(text);
      if (match === null || match.index !== index) {
        throw new Error(`unclassified numeric-looking character at offset ${index}`);
      }
      tokens.push(match[0]);
      index = NUMBER_RE.lastIndex;
      continue;
    }
    index += 1;
  }
  if (inString || escaped) {
    throw new Error("unterminated JSON string");
  }
  return tokens;
}

function negativeZero(token) {
  if (!token.startsWith("-")) {
    return false;
  }
  const significand = token.slice(1).split(/[eE]/, 1)[0].replaceAll(".", "");
  return significand.length > 0 && [...significand].every((character) => character === "0");
}

function stringLiterals(value) {
  const domains = new Set();
  const profiles = new Set();
  function walk(node) {
    if (Array.isArray(node)) {
      for (const child of node) walk(child);
    } else if (node !== null && typeof node === "object") {
      for (const child of Object.values(node)) walk(child);
    } else if (typeof node === "string") {
      if (DOMAIN_RE.test(node)) domains.add(node);
      if (PROFILE_RE.test(node)) profiles.add(node);
    }
  }
  walk(value);
  return {
    domains: [...domains].sort(),
    profiles: [...profiles].sort(),
  };
}

function countLiteralTypeNumberOccurrences(value) {
  let count = 0;
  function walk(node) {
    if (Array.isArray(node)) {
      for (const child of node) walk(child);
    } else if (node !== null && typeof node === "object") {
      const declaredType = node.type;
      if (
        declaredType === "number"
        || (Array.isArray(declaredType) && declaredType.includes("number"))
      ) {
        count += 1;
      }
      for (const child of Object.values(node)) walk(child);
    }
  }
  walk(value);
  return count;
}

function declaredIdentity(document) {
  for (const key of ["$id", "profile_id", "migration_id"]) {
    if (typeof document[key] === "string") return document[key];
  }
  return null;
}

function observeRow(root, sequenceIndex, entry) {
  if (
    entry === null
    || typeof entry !== "object"
    || typeof entry.role !== "string"
    || typeof entry.repository_path !== "string"
  ) {
    throw new Error("input manifest entry requires string role and repository_path");
  }
  const raw = strictRepositoryFile(root, entry.repository_path);
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
    throw new Error(`BOM is forbidden: ${entry.repository_path}`);
  }
  const text = new TextDecoder("utf-8", { fatal: true }).decode(raw);
  assertStrictJson(text, entry.repository_path);
  const document = JSON.parse(text);
  if (document === null || Array.isArray(document) || typeof document !== "object") {
    throw new Error(`artifact root must be an object: ${entry.repository_path}`);
  }
  const tokens = numberTokens(text);
  const integers = tokens.filter((token) => INTEGER_RE.test(token));
  const fractions = tokens.filter((token) => !INTEGER_RE.test(token));
  const outOfDomain = integers.filter((token) => {
    const value = BigInt(token);
    return value < MIN_SAFE_INTEGER || value > MAX_SAFE_INTEGER;
  });
  const literals = stringLiterals(document);
  return {
    sequence_index: sequenceIndex,
    role: entry.role,
    repository_path: entry.repository_path,
    raw_sha256: sha256Lexical(raw),
    byte_count: raw.length,
    declared_identity: declaredIdentity(document),
    schema_version: document.schema_version ?? null,
    raw_number_token_count: tokens.length,
    integer_token_count: integers.length,
    fraction_or_exponent_token_count: fractions.length,
    negative_zero_token_count: tokens.filter((token) => negativeZero(token)).length,
    overlong_number_token_count: tokens.filter(
      (token) => Buffer.byteLength(token, "ascii") > 128,
    ).length,
    out_of_safe_integer_domain_token_count: outOfDomain.length,
    ordered_number_token_sha256: sha256Lexical(Buffer.from(stableStringify(tokens), "utf8")),
    literal_type_number_occurrence_count: countLiteralTypeNumberOccurrences(document),
    domain_literals: literals.domains,
    profile_literals: literals.profiles,
  };
}

function main() {
  const args = parseArguments(process.argv.slice(2));
  if (!CHALLENGE_RE.test(args.challenge)) {
    throw new Error("challenge does not match the closed lexical contract");
  }
  const root = fs.realpathSync(args.root);
  const manifestPath = fs.realpathSync(args.manifest);
  if (!manifestPath.startsWith(`${root}${path.sep}`)) {
    throw new Error("input manifest resolves outside repository");
  }
  const manifestText = fs.readFileSync(manifestPath, "utf8");
  assertStrictJson(manifestText, "input manifest");
  const manifest = JSON.parse(manifestText);
  if (
    Object.keys(manifest).sort().join("\n") !== EXPECTED_MANIFEST_KEYS.join("\n")
  ) {
    throw new Error("input manifest member inventory drifted");
  }
  const expectedScalars = {
    schema_version: "0.1.0",
    artifact_class: "profile_0_3_construction_observer_input_manifest",
    suite_id: SUITE_ID,
    manifest_id: "prq-002e-profile-0.3-construction-inputs.0001",
    answer_free: true,
    expected_outcomes_included: false,
    peer_results_included: false,
    artifact_count: EXPECTED_ARTIFACTS.length,
    network_access_allowed: false,
    environment_path_discovery_allowed: false,
    expectation_manifest_may_be_passed_to_observer: false,
    peer_source_may_be_passed_to_observer: false,
    peer_result_may_be_passed_to_observer: false,
    product_identity_computation_allowed: false,
    authority_claim_allowed: false,
  };
  for (const [key, expected] of Object.entries(expectedScalars)) {
    if (typeof manifest[key] !== typeof expected || manifest[key] !== expected) {
      throw new Error("input manifest identity, count, or nonclaim drifted");
    }
  }
  if (!Array.isArray(manifest.artifacts)) {
    throw new Error("input manifest artifacts must be an array");
  }
  const observedInventory = manifest.artifacts.map((entry) => {
    if (
      entry === null
      || typeof entry !== "object"
      || Array.isArray(entry)
      || Object.keys(entry).sort().join("\n") !== "repository_path\nrole"
    ) {
      return null;
    }
    return [entry.role, entry.repository_path];
  });
  if (stableStringify(observedInventory) !== stableStringify(EXPECTED_ARTIFACTS)) {
    throw new Error("input manifest exact ordered artifact inventory drifted");
  }
  const rows = manifest.artifacts.map(
    (entry, index) => observeRow(root, index + 1, entry),
  );
  const projection = {
    schema_version: "0.1.0",
    artifact_class: "profile_0_3_construction_observation",
    suite_id: SUITE_ID,
    observer_id: OBSERVER_ID,
    challenge: args.challenge,
    artifact_count: rows.length,
    artifacts: rows,
    network_access_requested: false,
    expectations_received: false,
    peer_source_received: false,
    peer_result_received: false,
    canonicalization_conformance_claimed: false,
    product_identity_computed: false,
    authority_claimed: false,
  };
  process.stdout.write(`${stableStringify(projection)}\n`);
}

main();
