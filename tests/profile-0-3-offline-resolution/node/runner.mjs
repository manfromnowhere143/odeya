// PRQ-002I offline-resolution and binding-replay runner (Node.js path).
//
// Source-separated peer of the CPython runner: parses every universe member
// with its own recursive-descent reader (never JSON.parse), builds the
// schema registry solely from members carrying a urn:odeya:schema:
// identifier, resolves every $ref offline with recorded target digests,
// and replays every declared digest binding by recomputing the referenced
// repository file's raw SHA-256 and byte count from bytes. Consults nothing
// but the repository. Zero third-party dependencies. Bounded architecture
// evidence only.

import { createHash } from "node:crypto";
import { readFileSync, lstatSync } from "node:fs";
import { join } from "node:path";
import process from "node:process";

const SCHEMA_VERSION = "0.1.0";
const SUITE_ID = "prq-002i-offline-resolution.0001";
const IMPLEMENTATION_ID = "nodejs-native-offline-resolver.0001";
const URN_PREFIX = "urn:odeya:schema:";
const SKIP_WALK_KEYS = new Set(["const", "enum", "examples", "default"]);

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
  constructor(text, context) {
    this.text = text;
    this.context = context;
    this.index = 0;
  }
  fail(detail) {
    refuse("universe_member_violation", `${this.context}: ${detail}`);
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
    if (this.index >= this.text.length) this.fail("empty document");
    const value = this.parseValue();
    this.skipWhitespace();
    if (this.index !== this.text.length) this.fail("trailing content");
    return value;
  }
  parseValue() {
    const ch = this.text[this.index];
    if (ch === "{") return this.parseObject();
    if (ch === "[") return this.parseArray();
    if (ch === '"') return this.parseString();
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
    this.fail("unexpected character");
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
      if (this.text[this.index] !== '"') this.fail("expected member name");
      const key = this.parseString();
      this.skipWhitespace();
      if (this.text[this.index] !== ":") this.fail("expected colon");
      this.index += 1;
      this.skipWhitespace();
      const value = this.parseValue();
      if (!object.set(key, value)) {
        this.fail(`duplicate member name ${JSON.stringify(key)}`);
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
      this.fail("expected comma or object end");
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
      this.fail("expected comma or array end");
    }
  }
  parseString() {
    let result = "";
    this.index += 1;
    for (;;) {
      if (this.index >= this.text.length) this.fail("unterminated string");
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
          if (!/^[0-9A-Fa-f]{4}$/.test(hex)) this.fail("invalid unicode escape");
          this.index += 4;
          const code = Number.parseInt(hex, 16);
          if (code >= 0xd800 && code <= 0xdbff) {
            if (
              this.text[this.index] === "\\" &&
              this.text[this.index + 1] === "u"
            ) {
              const low = this.text.slice(this.index + 2, this.index + 6);
              if (!/^[0-9A-Fa-f]{4}$/.test(low)) this.fail("invalid low surrogate");
              const lowCode = Number.parseInt(low, 16);
              if (lowCode < 0xdc00 || lowCode > 0xdfff) {
                this.fail("unpaired surrogate");
              }
              this.index += 6;
              result += String.fromCodePoint(
                0x10000 + (code - 0xd800) * 0x400 + (lowCode - 0xdc00),
              );
            } else {
              this.fail("unpaired surrogate");
            }
          } else if (code >= 0xdc00 && code <= 0xdfff) {
            this.fail("unpaired surrogate");
          } else {
            result += String.fromCharCode(code);
          }
        } else {
          this.fail("invalid escape");
        }
        continue;
      }
      if (ch.charCodeAt(0) < 0x20) this.fail("unescaped control character");
      result += ch;
      this.index += 1;
    }
  }
  parseNumber() {
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(
      this.text.slice(this.index),
    );
    if (match === null) this.fail("malformed number");
    const lexeme = match[0];
    this.index += lexeme.length;
    if (!/^-?(?:0|[1-9][0-9]*)$/.test(lexeme)) {
      this.fail(`non-integer number token ${lexeme}`);
    }
    return new JInt(lexeme);
  }
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
  refuse("universe_member_violation", "unserializable value");
}

function loadMember(root, relative) {
  if (relative.startsWith("/") || relative.split("/").includes("..")) {
    refuse("universe_member_violation", `illegal member path ${relative}`);
  }
  const target = join(root, relative);
  const stat = lstatSync(target, { throwIfNoEntry: false });
  if (stat === undefined || !stat.isFile() || stat.isSymbolicLink()) {
    refuse(
      "universe_member_violation",
      `${relative}: not a regular non-symlink repository file`,
    );
  }
  const raw = readFileSync(target);
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(raw);
  } catch {
    refuse("universe_member_violation", `${relative}: invalid UTF-8`);
  }
  const document = new Parser(text, relative).parseDocument();
  return { raw, document };
}

function resolvePointer(document, fragment, context) {
  if (fragment === "" || fragment === "#") return document;
  if (!fragment.startsWith("#/")) {
    refuse(
      "offline_resolution_violation",
      `${context}: unsupported reference fragment ${fragment}`,
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
          "offline_resolution_violation",
          `${context}: unresolvable fragment ${fragment}`,
        );
      }
      current = current[index];
    } else {
      refuse(
        "offline_resolution_violation",
        `${context}: unresolvable fragment ${fragment}`,
      );
    }
  }
  return current;
}

function parseArguments(argv) {
  const values = new Map();
  for (let index = 2; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (
      value === undefined ||
      !["--repository-root", "--universe", "--source-manifest"].includes(flag)
    ) {
      throw new Error(`unsupported argument ${flag}`);
    }
    values.set(flag, value);
  }
  for (const flag of ["--repository-root", "--universe", "--source-manifest"]) {
    if (!values.has(flag)) throw new Error(`missing argument ${flag}`);
  }
  return values;
}

function main() {
  const argumentsMap = parseArguments(process.argv);
  const root = argumentsMap.get("--repository-root");

  const universeRaw = readFileSync(argumentsMap.get("--universe"));
  const universe = new Parser(
    new TextDecoder("utf-8", { fatal: true }).decode(universeRaw),
    "universe-manifest",
  ).parseDocument();
  if (
    universe.get("suite_id") !== SUITE_ID ||
    universe.get("answer_free") !== true ||
    universe.get("verification_time_directory_discovery_allowed") !== false ||
    universe.get("network_access_allowed") !== false
  ) {
    refuse("universe_census_mismatch", "universe identity flags differ");
  }
  const members = universe.get("members");
  if (
    !Array.isArray(members) ||
    universe.get("member_count_decimal") !== String(members.length)
  ) {
    refuse("universe_census_mismatch", "universe member census differs");
  }
  const roleCounts = new Map();
  const loaded = [];
  const seen = new Set();
  for (const member of members) {
    const role = member.get("role");
    const relative = member.get("repository_path");
    if (typeof role !== "string" || typeof relative !== "string") {
      refuse("universe_census_mismatch", "malformed universe member");
    }
    if (seen.has(relative)) {
      refuse("universe_census_mismatch", `duplicate member ${relative}`);
    }
    seen.add(relative);
    roleCounts.set(role, (roleCounts.get(role) ?? 0) + 1);
    const { raw, document } = loadMember(root, relative);
    loaded.push({ role, relative, raw, document });
  }
  const declared = universe.get("role_counts_decimal");
  const sortedRoles = [...roleCounts.keys()].sort();
  if (
    !isObj(declared) ||
    declared.keys.length !== sortedRoles.length ||
    sortedRoles.some(
      (role, index) =>
        declared.keys[index] !== role ||
        declared.get(role) !== String(roleCounts.get(role)),
    )
  ) {
    refuse("universe_census_mismatch", "universe role census differs");
  }

  const registry = new Map();
  for (const entry of loaded) {
    const document = entry.document;
    if (isObj(document) && typeof document.get("$id") === "string") {
      const schemaId = document.get("$id");
      if (schemaId.startsWith(URN_PREFIX)) {
        if (registry.has(schemaId)) {
          refuse(
            "universe_census_mismatch",
            `duplicate schema identifier ${schemaId}`,
          );
        }
        registry.set(schemaId, entry);
      }
    }
  }
  if (String(registry.size) !== declared.get("schema")) {
    refuse(
      "universe_census_mismatch",
      "registry census differs from declared schema role count",
    );
  }

  const referenceEdges = [];
  function walkSchema(schemaId, node, pointer) {
    if (Array.isArray(node)) {
      node.forEach((child, index) => walkSchema(schemaId, child, `${pointer}/${index}`));
      return;
    }
    if (!isObj(node)) return;
    if (node.has("$dynamicRef") || node.has("$recursiveRef")) {
      refuse(
        "offline_resolution_violation",
        `${schemaId}#${pointer}: dynamic reference is not offline-resolvable`,
      );
    }
    const reference = node.has("$ref") ? node.get("$ref") : undefined;
    if (typeof reference === "string") {
      const context = `${schemaId}#${pointer}/$ref`;
      let targetId;
      let fragment;
      if (reference.startsWith("#")) {
        resolvePointer(registry.get(schemaId).document, reference, context);
        targetId = schemaId;
        fragment = reference;
      } else if (reference.startsWith(URN_PREFIX)) {
        const hashIndex = reference.indexOf("#");
        targetId = hashIndex === -1 ? reference : reference.slice(0, hashIndex);
        if (!registry.has(targetId)) {
          refuse(
            "offline_resolution_violation",
            `${context}: reference target outside the universe registry: ${targetId}`,
          );
        }
        fragment = hashIndex === -1 ? "#" : reference.slice(hashIndex);
        resolvePointer(registry.get(targetId).document, fragment, context);
      } else {
        refuse(
          "offline_resolution_violation",
          `${context}: non-URN, non-fragment reference ${JSON.stringify(reference)}`,
        );
      }
      const target = registry.get(targetId);
      referenceEdges.push({
        source_schema_id: schemaId,
        source_pointer: pointer,
        reference,
        target_schema_id: targetId,
        target_repository_path: target.relative,
        target_raw_sha256: sha256(target.raw),
        fragment,
      });
    }
    for (const key of node.keys) {
      if (SKIP_WALK_KEYS.has(key) || key.startsWith("x-")) continue;
      walkSchema(schemaId, node.get(key), `${pointer}/${pointerEscape(key)}`);
    }
  }
  for (const schemaId of registry.keys()) {
    walkSchema(schemaId, registry.get(schemaId).document, "");
  }

  const bindingEdges = [];
  const shapeCounts = new Map([
    ["path", 0],
    ["repository_path", 0],
    ["schema_path", 0],
  ]);

  function bindingTarget(node) {
    if (
      typeof node.get("repository_path") === "string" &&
      typeof node.get("raw_sha256") === "string"
    ) {
      const count = node.get("byte_count_decimal");
      return [
        "repository_path",
        node.get("repository_path"),
        node.get("raw_sha256"),
        typeof count === "string" ? count : null,
      ];
    }
    if (
      typeof node.get("path") === "string" &&
      typeof node.get("raw_digest") === "string" &&
      isInt(node.get("byte_count"))
    ) {
      return ["path", node.get("path"), node.get("raw_digest"), node.get("byte_count").lexeme];
    }
    if (
      typeof node.get("schema_path") === "string" &&
      typeof node.get("schema_raw_digest") === "string" &&
      isInt(node.get("schema_byte_count"))
    ) {
      return [
        "schema_path",
        node.get("schema_path"),
        node.get("schema_raw_digest"),
        node.get("schema_byte_count").lexeme,
      ];
    }
    return null;
  }

  function walkBindings(memberPath, node, pointer) {
    if (Array.isArray(node)) {
      node.forEach((child, index) =>
        walkBindings(memberPath, child, `${pointer}/${index}`),
      );
      return;
    }
    if (!isObj(node)) return;
    const target = bindingTarget(node);
    if (target !== null) {
      const [shape, relative, declaredDigest, declaredCount] = target;
      const context = `${memberPath}#${pointer}`;
      if (relative.startsWith("/") || relative.split("/").includes("..")) {
        refuse(
          "out_of_repository_target",
          `${context}: binding escapes the repository: ${relative}`,
        );
      }
      const targetPath = join(root, relative);
      const stat = lstatSync(targetPath, { throwIfNoEntry: false });
      if (stat === undefined || !stat.isFile() || stat.isSymbolicLink()) {
        refuse(
          "digest_binding_mismatch",
          `${context}: binding target missing or symlinked: ${relative}`,
        );
      }
      const targetRaw = readFileSync(targetPath);
      if (sha256(targetRaw) !== declaredDigest) {
        refuse(
          "digest_binding_mismatch",
          `${context}: digest differs for ${relative}`,
        );
      }
      if (declaredCount !== null && declaredCount !== String(targetRaw.length)) {
        refuse(
          "digest_binding_mismatch",
          `${context}: byte count differs for ${relative}`,
        );
      }
      shapeCounts.set(shape, shapeCounts.get(shape) + 1);
      bindingEdges.push({
        member_path: memberPath,
        member_pointer: pointer,
        shape,
        target_repository_path: relative,
        target_raw_sha256: declaredDigest,
        target_byte_count_decimal: declaredCount !== null ? declaredCount : "",
      });
    }
    for (const key of node.keys) {
      walkBindings(memberPath, node.get(key), `${pointer}/${pointerEscape(key)}`);
    }
  }
  for (const entry of loaded) {
    walkBindings(entry.relative, entry.document, "");
  }

  const projection = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002i_offline_resolution_projection",
    suite_id: SUITE_ID,
    universe_binding: {
      raw_sha256: sha256(universeRaw),
      member_count_decimal: String(loaded.length),
    },
    census: {
      registry_count_decimal: String(registry.size),
      reference_edge_count_decimal: String(referenceEdges.length),
      binding_edge_count_decimal: String(bindingEdges.length),
      binding_shape_counts_decimal: {
        path: String(shapeCounts.get("path")),
        repository_path: String(shapeCounts.get("repository_path")),
        schema_path: String(shapeCounts.get("schema_path")),
      },
    },
    reference_edges: referenceEdges,
    binding_edges: bindingEdges,
    claim_boundary: {
      declared_universe_and_shapes_only: true,
      historical_residue_identities_resolved: false,
      product_identity_computed: false,
      profile_issued: false,
      prq_002_closed: false,
      gate_a_complete: false,
      publication_authorized: false,
    },
  };
  const projectionBytes = Buffer.from(emit(projection), "utf-8");
  const result = {
    schema_version: SCHEMA_VERSION,
    artifact_class: "prq_002i_offline_resolution_result",
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
          artifact_class: "prq_002i_offline_resolution_refusal",
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
