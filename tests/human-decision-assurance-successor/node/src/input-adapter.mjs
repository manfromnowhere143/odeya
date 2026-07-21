import { readFileSync, realpathSync } from "node:fs";
import { basename, normalize, sep } from "node:path";
import { TextDecoder } from "node:util";

const MAX_INPUT_BYTES = 16 * 1024 * 1024;
const FORBIDDEN_COMPONENTS = new Set(["cases.json", "python", "java"]);
const HAS_OWN = (value, key) => Object.prototype.hasOwnProperty.call(value, key);

export class InputRefusal extends Error {
  constructor(message) {
    super(message);
    this.name = "InputRefusal";
  }
}

function refuse(condition, message) {
  if (!condition) {
    throw new InputRefusal(message);
  }
}

function validateUnicodeScalarString(value, label) {
  for (let index = 0; index < value.length; index += 1) {
    const unit = value.charCodeAt(index);
    if (unit >= 0xd800 && unit <= 0xdbff) {
      refuse(index + 1 < value.length, `${label}: unpaired high surrogate`);
      const next = value.charCodeAt(index + 1);
      refuse(next >= 0xdc00 && next <= 0xdfff, `${label}: unpaired high surrogate`);
      index += 1;
    } else {
      refuse(!(unit >= 0xdc00 && unit <= 0xdfff), `${label}: unpaired low surrogate`);
    }
  }
}

class StrictJsonParser {
  constructor(text, label) {
    this.text = text;
    this.label = label;
    this.index = 0;
  }

  parse() {
    this.skipWhitespace();
    const result = this.parseValue();
    this.skipWhitespace();
    refuse(this.index === this.text.length, `${this.label}: trailing bytes after JSON value`);
    return result;
  }

  skipWhitespace() {
    while (this.index < this.text.length && " \t\r\n".includes(this.text[this.index])) {
      this.index += 1;
    }
  }

  parseValue() {
    refuse(this.index < this.text.length, `${this.label}: unexpected end of JSON`);
    const character = this.text[this.index];
    if (character === "{") return this.parseObject();
    if (character === "[") return this.parseArray();
    if (character === '"') return this.parseString();
    if (character === "t") return this.parseLiteral("true", true);
    if (character === "f") return this.parseLiteral("false", false);
    if (character === "n") return this.parseLiteral("null", null);
    if (character === "-" || (character >= "0" && character <= "9")) return this.parseNumber();
    throw new InputRefusal(`${this.label}: invalid JSON token at character ${this.index}`);
  }

  parseObject() {
    this.index += 1;
    this.skipWhitespace();
    const result = Object.create(null);
    const names = new Set();
    if (this.text[this.index] === "}") {
      this.index += 1;
      return result;
    }
    while (true) {
      refuse(this.text[this.index] === '"', `${this.label}: object member name must be a string`);
      const name = this.parseString();
      refuse(!names.has(name), `${this.label}: duplicate object member ${JSON.stringify(name)}`);
      names.add(name);
      this.skipWhitespace();
      refuse(this.text[this.index] === ":", `${this.label}: missing colon after object member`);
      this.index += 1;
      this.skipWhitespace();
      result[name] = this.parseValue();
      this.skipWhitespace();
      if (this.text[this.index] === "}") {
        this.index += 1;
        return result;
      }
      refuse(this.text[this.index] === ",", `${this.label}: missing comma between object members`);
      this.index += 1;
      this.skipWhitespace();
    }
  }

  parseArray() {
    this.index += 1;
    this.skipWhitespace();
    const result = [];
    if (this.text[this.index] === "]") {
      this.index += 1;
      return result;
    }
    while (true) {
      result.push(this.parseValue());
      this.skipWhitespace();
      if (this.text[this.index] === "]") {
        this.index += 1;
        return result;
      }
      refuse(this.text[this.index] === ",", `${this.label}: missing comma between array items`);
      this.index += 1;
      this.skipWhitespace();
    }
  }

  parseString() {
    const start = this.index;
    this.index += 1;
    while (this.index < this.text.length) {
      const code = this.text.charCodeAt(this.index);
      if (code === 0x22) {
        this.index += 1;
        const value = JSON.parse(this.text.slice(start, this.index));
        validateUnicodeScalarString(value, this.label);
        return value;
      }
      refuse(code >= 0x20, `${this.label}: unescaped control character in string`);
      if (code === 0x5c) {
        this.index += 1;
        refuse(this.index < this.text.length, `${this.label}: truncated string escape`);
        const escaped = this.text[this.index];
        if (escaped === "u") {
          const digits = this.text.slice(this.index + 1, this.index + 5);
          refuse(/^[0-9a-fA-F]{4}$/.test(digits), `${this.label}: malformed Unicode escape`);
          this.index += 4;
        } else {
          refuse('"\\/bfnrt'.includes(escaped), `${this.label}: malformed string escape`);
        }
      }
      this.index += 1;
    }
    throw new InputRefusal(`${this.label}: unterminated string`);
  }

  parseNumber() {
    const remainder = this.text.slice(this.index);
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(remainder);
    refuse(match !== null, `${this.label}: malformed number`);
    this.index += match[0].length;
    const value = Number(match[0]);
    refuse(Number.isFinite(value), `${this.label}: non-finite number`);
    if (!/[.eE]/.test(match[0])) {
      refuse(Number.isSafeInteger(value), `${this.label}: integer is outside the exact safe range`);
      refuse(!Object.is(value, -0), `${this.label}: negative zero is not admitted`);
    }
    return value;
  }

  parseLiteral(literal, value) {
    refuse(this.text.startsWith(literal, this.index), `${this.label}: malformed literal`);
    this.index += literal.length;
    return value;
  }
}

export function parseStrictJsonText(text, label = "JSON input") {
  refuse(typeof text === "string", `${label}: parser input must be text`);
  return new StrictJsonParser(text, label).parse();
}

function assertPermittedInputPath(path, expectedBasename, label) {
  refuse(typeof path === "string" && path.length > 0, `${label}: missing path`);
  refuse(basename(path) === expectedBasename, `${label}: expected basename ${expectedBasename}`);
  let resolvedPath;
  try {
    resolvedPath = realpathSync(path);
  } catch (error) {
    throw new InputRefusal(`${label}: cannot resolve input (${error.code ?? "resolution_error"})`);
  }
  refuse(basename(resolvedPath) === expectedBasename, `${label}: resolved basename is not ${expectedBasename}`);
  const components = normalize(resolvedPath).split(sep);
  for (const component of components) {
    if (component !== expectedBasename) {
      refuse(!FORBIDDEN_COMPONENTS.has(component), `${label}: forbidden path component ${component}`);
    }
  }
  return resolvedPath;
}

export function readStrictJson(path, expectedBasename, label) {
  const resolvedPath = assertPermittedInputPath(path, expectedBasename, label);
  let raw;
  try {
    raw = readFileSync(resolvedPath);
  } catch (error) {
    throw new InputRefusal(`${label}: cannot read input (${error.code ?? "read_error"})`);
  }
  refuse(raw.length > 0 && raw.length <= MAX_INPUT_BYTES, `${label}: byte count outside admitted bounds`);
  refuse(
    !(raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf),
    `${label}: UTF-8 BOM is not admitted`,
  );
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(raw);
  } catch {
    throw new InputRefusal(`${label}: input is not strict UTF-8`);
  }
  refuse(text.charCodeAt(0) !== 0xfeff, `${label}: UTF-8 BOM is not admitted`);
  return parseStrictJsonText(text, label);
}

export function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function assertExactKeys(value, required, optional, label) {
  refuse(isRecord(value), `${label}: expected object`);
  const allowed = new Set([...required, ...optional]);
  for (const key of Object.keys(value)) {
    refuse(allowed.has(key), `${label}: unknown member ${key}`);
  }
  for (const key of required) {
    refuse(HAS_OWN(value, key), `${label}: missing member ${key}`);
  }
}

function cloneJson(value) {
  if (Array.isArray(value)) return value.map(cloneJson);
  if (isRecord(value)) {
    const result = Object.create(null);
    for (const [key, member] of Object.entries(value)) result[key] = cloneJson(member);
    return result;
  }
  return value;
}

function parsePointer(pointer, label) {
  refuse(typeof pointer === "string", `${label}: JSON Pointer must be a string`);
  if (pointer === "") return [];
  refuse(pointer.startsWith("/"), `${label}: JSON Pointer must start with /`);
  return pointer.slice(1).split("/").map((token) => {
    refuse(!/~(?:[^01]|$)/.test(token), `${label}: malformed JSON Pointer escape`);
    return token.replaceAll("~1", "/").replaceAll("~0", "~");
  });
}

function arrayIndex(token, length, allowAppend, label) {
  if (allowAppend && token === "-") return length;
  refuse(/^(?:0|[1-9][0-9]*)$/.test(token), `${label}: invalid array index ${token}`);
  const index = Number(token);
  refuse(Number.isSafeInteger(index), `${label}: array index is not safe`);
  refuse(index < length || (allowAppend && index === length), `${label}: array index out of range`);
  return index;
}

function resolveParent(document, tokens, label) {
  refuse(tokens.length > 0, `${label}: document-root mutation is not admitted`);
  let parent = document;
  for (const token of tokens.slice(0, -1)) {
    if (Array.isArray(parent)) {
      parent = parent[arrayIndex(token, parent.length, false, label)];
    } else {
      refuse(isRecord(parent) && HAS_OWN(parent, token), `${label}: path does not exist`);
      parent = parent[token];
    }
  }
  return { parent, token: tokens[tokens.length - 1] };
}

function readAt(document, pointer, label) {
  const tokens = parsePointer(pointer, label);
  let value = document;
  for (const token of tokens) {
    if (Array.isArray(value)) {
      value = value[arrayIndex(token, value.length, false, label)];
    } else {
      refuse(isRecord(value) && HAS_OWN(value, token), `${label}: source path does not exist`);
      value = value[token];
    }
  }
  return value;
}

function removeAt(document, pointer, label) {
  const tokens = parsePointer(pointer, label);
  const { parent, token } = resolveParent(document, tokens, label);
  if (Array.isArray(parent)) {
    const index = arrayIndex(token, parent.length, false, label);
    return parent.splice(index, 1)[0];
  }
  refuse(isRecord(parent) && HAS_OWN(parent, token), `${label}: removal path does not exist`);
  const value = parent[token];
  delete parent[token];
  return value;
}

function addAt(document, pointer, value, label) {
  const tokens = parsePointer(pointer, label);
  const { parent, token } = resolveParent(document, tokens, label);
  if (Array.isArray(parent)) {
    const index = arrayIndex(token, parent.length, true, label);
    parent.splice(index, 0, cloneJson(value));
    return;
  }
  refuse(isRecord(parent), `${label}: addition parent is not a container`);
  parent[token] = cloneJson(value);
}

function replaceAt(document, pointer, value, label) {
  const tokens = parsePointer(pointer, label);
  const { parent, token } = resolveParent(document, tokens, label);
  if (Array.isArray(parent)) {
    parent[arrayIndex(token, parent.length, false, label)] = cloneJson(value);
    return;
  }
  refuse(isRecord(parent) && HAS_OWN(parent, token), `${label}: replacement path does not exist`);
  parent[token] = cloneJson(value);
}

function applyPatch(document, mutations, vectorId) {
  const result = cloneJson(document);
  for (let index = 0; index < mutations.length; index += 1) {
    const mutation = mutations[index];
    const label = `vector ${vectorId} mutation ${index}`;
    if (mutation.op === "add") {
      addAt(result, mutation.path, mutation.value, label);
    } else if (mutation.op === "remove") {
      removeAt(result, mutation.path, label);
    } else if (mutation.op === "replace") {
      replaceAt(result, mutation.path, mutation.value, label);
    } else if (mutation.op === "copy") {
      addAt(result, mutation.path, cloneJson(readAt(result, mutation.from, label)), label);
    } else if (mutation.op === "move") {
      const fromTokens = parsePointer(mutation.from, label);
      const pathTokens = parsePointer(mutation.path, label);
      refuse(
        pathTokens.length <= fromTokens.length ||
          !fromTokens.every((token, tokenIndex) => token === pathTokens[tokenIndex]),
        `${label}: cannot move a value into its descendant`,
      );
      addAt(result, mutation.path, removeAt(result, mutation.from, label), label);
    } else {
      throw new InputRefusal(`${label}: unadmitted operation ${String(mutation.op)}`);
    }
  }
  return result;
}

function validateMutation(mutation, label) {
  refuse(isRecord(mutation), `${label}: mutation must be an object`);
  const operation = mutation.op;
  refuse(["add", "copy", "move", "remove", "replace"].includes(operation), `${label}: unsupported operation`);
  if (operation === "add" || operation === "replace") {
    assertExactKeys(mutation, ["op", "path", "value"], [], label);
  } else if (operation === "copy" || operation === "move") {
    assertExactKeys(mutation, ["op", "path", "from"], [], label);
  } else {
    assertExactKeys(mutation, ["op", "path"], [], label);
  }
  parsePointer(mutation.path, label);
  if (operation === "copy" || operation === "move") parsePointer(mutation.from, label);
}

export function validateVectorCorpus(corpus) {
  assertExactKeys(
    corpus,
    ["suite_version", "artifact_class", "candidate_status", "ruleset_id", "resolver_profile_id", "mutation_language", "base_input", "vectors"],
    [],
    "vectors corpus",
  );
  refuse(corpus.suite_version === "0.1.0", "vectors corpus: unsupported suite_version");
  refuse(
    corpus.artifact_class === "human_decision_assurance_successor_expectation_free_evaluator_inputs",
    "vectors corpus: wrong artifact_class",
  );
  refuse(Array.isArray(corpus.vectors) && corpus.vectors.length > 0, "vectors corpus: vectors must be nonempty");
  assertExactKeys(
    corpus.mutation_language,
    ["standard", "allowed_operations", "array_append_token", "application_order", "base_vector_resolution", "cycles_or_unknown_base_vector_ids"],
    [],
    "vectors corpus mutation_language",
  );
  refuse(corpus.mutation_language.standard === "rfc6902_json_patch_subset", "vectors corpus: wrong mutation language");
  const expectedOperations = ["add", "copy", "move", "remove", "replace"];
  refuse(
    JSON.stringify(corpus.mutation_language.allowed_operations) === JSON.stringify(expectedOperations),
    "vectors corpus: operation inventory mismatch",
  );
  refuse(corpus.mutation_language.array_append_token === "-", "vectors corpus: wrong append token");
  const identifiers = new Set();
  for (let index = 0; index < corpus.vectors.length; index += 1) {
    const vector = corpus.vectors[index];
    assertExactKeys(vector, ["vector_id", "mutations"], ["base_vector_id"], `vector ${index}`);
    refuse(typeof vector.vector_id === "string" && /^[a-z0-9][a-z0-9-]{0,127}$/.test(vector.vector_id), `vector ${index}: invalid vector_id`);
    refuse(!identifiers.has(vector.vector_id), `vector ${index}: duplicate vector_id`);
    identifiers.add(vector.vector_id);
    if (HAS_OWN(vector, "base_vector_id")) {
      refuse(typeof vector.base_vector_id === "string", `vector ${vector.vector_id}: invalid base_vector_id`);
    }
    refuse(Array.isArray(vector.mutations), `vector ${vector.vector_id}: mutations must be an array`);
    vector.mutations.forEach((mutation, mutationIndex) =>
      validateMutation(mutation, `vector ${vector.vector_id} mutation ${mutationIndex}`),
    );
  }
  const byId = new Map(corpus.vectors.map((vector) => [vector.vector_id, vector]));
  const complete = new Set();
  const active = new Set();
  const visit = (id) => {
    if (complete.has(id)) return;
    refuse(!active.has(id), `vector ${id}: base_vector_id cycle`);
    active.add(id);
    const vector = byId.get(id);
    if (HAS_OWN(vector, "base_vector_id")) {
      refuse(byId.has(vector.base_vector_id), `vector ${id}: unknown base_vector_id ${vector.base_vector_id}`);
      visit(vector.base_vector_id);
    }
    active.delete(id);
    complete.add(id);
  };
  for (const vector of corpus.vectors) visit(vector.vector_id);
  for (const vector of corpus.vectors) materializeVector(corpus, vector.vector_id);
  return corpus;
}

export function materializeVector(corpus, vectorId) {
  refuse(typeof vectorId === "string" && vectorId.length > 0, "vector id is required");
  const byId = new Map(corpus.vectors.map((vector) => [vector.vector_id, vector]));
  refuse(byId.has(vectorId), `unknown vector id ${vectorId}`);
  const active = new Set();
  const resolved = new Map();
  const resolve = (id) => {
    if (resolved.has(id)) return cloneJson(resolved.get(id));
    refuse(byId.has(id), `vector ${id}: unknown base_vector_id`);
    refuse(!active.has(id), `vector ${id}: base_vector_id cycle`);
    active.add(id);
    const vector = byId.get(id);
    let input = HAS_OWN(vector, "base_vector_id") ? resolve(vector.base_vector_id) : cloneJson(corpus.base_input);
    input = applyPatch(input, vector.mutations, id);
    active.delete(id);
    resolved.set(id, input);
    return cloneJson(input);
  };
  return resolve(vectorId);
}

export function parseCommandLine(argv) {
  refuse(Array.isArray(argv), "command line is unavailable");
  const admitted = new Set(["--vectors", "--ruleset", "--resolver", "--vector-id"]);
  const values = Object.create(null);
  for (let index = 0; index < argv.length; index += 2) {
    const option = argv[index];
    refuse(admitted.has(option), `unknown or misplaced argument ${String(option)}`);
    refuse(!HAS_OWN(values, option), `duplicate argument ${option}`);
    refuse(index + 1 < argv.length, `missing value for ${option}`);
    values[option] = argv[index + 1];
  }
  for (const option of admitted) refuse(HAS_OWN(values, option), `missing required argument ${option}`);
  return {
    vectorsPath: values["--vectors"],
    rulesetPath: values["--ruleset"],
    resolverPath: values["--resolver"],
    vectorId: values["--vector-id"],
  };
}
