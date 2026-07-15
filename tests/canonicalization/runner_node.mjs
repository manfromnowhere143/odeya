#!/usr/bin/env node
/** Independent Node.js architecture-conformance path for odeya-jcs-0.1. */

import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { arch as osArch, endianness, platform as osPlatform, release as osRelease } from 'node:os';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const SUITE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(SUITE, '../..');
const MANIFEST_PATH = resolve(SUITE, 'manifest.json');
const SOURCE_LOCK_PATH = resolve(SUITE, 'source-lock.json');
const UPSTREAM_PATH = resolve(SUITE, 'official/cyberphone/vectors.json');
const DEFAULT_CANONICALIZE_PATH = resolve(
  SUITE,
  'node/node_modules/canonicalize/lib/canonicalize.js'
);
const CANONICALIZE_SPECIFIER = process.env.ODEYA_CANONICALIZE_MODULE ??
  pathToFileURL(DEFAULT_CANONICALIZE_PATH).href;
const canonicalizeModule = await import(CANONICALIZE_SPECIFIER);
const canonicalize = canonicalizeModule.default;
const PROFILE_ID = 'urn:odeya:canonicalization:odeya-jcs-0.1';
const TIMESTAMP_RE = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{6})Z$/;
const DECIMAL_RE = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:e-?(?:0|[1-9][0-9]*))?$/;
const DIGEST_RE = /^sha256:[0-9a-f]{64}$/;
const SEMVER_RE = /^[0-9]+\.[0-9]+\.[0-9]+$/;
const SCHEMA_ID_RE = /^urn:odeya:schema:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?:[0-9]+\.[0-9]+\.[0-9]+$/;
const MISSING_REASONS = new Set([
  'unknown', 'unmeasured', 'unavailable', 'withheld', 'not_applicable'
]);

class Refusal extends Error {
  constructor (code) {
    super(code);
    this.code = code;
  }
}

function sha256 (bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function isPlainObject (value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function exactKeys (value, required, code) {
  if (!isPlainObject(value)) throw new Refusal(code);
  const actual = Object.keys(value).sort();
  const expected = [...required].sort();
  if (actual.length !== expected.length || actual.some((key, index) => key !== expected[index])) {
    throw new Refusal(code);
  }
  return value;
}

function isLexicalZero (token) {
  const unsigned = token.startsWith('-') ? token.slice(1) : token;
  const mantissa = unsigned.split(/[eE]/, 1)[0];
  return [...mantissa].every((char) => char === '0' || char === '.');
}

function hasUnpairedSurrogateInString (value) {
  for (let index = 0; index < value.length; index += 1) {
    const unit = value.charCodeAt(index);
    if (unit >= 0xD800 && unit <= 0xDBFF) {
      if (index + 1 >= value.length) return true;
      const next = value.charCodeAt(index + 1);
      if (next < 0xDC00 || next > 0xDFFF) return true;
      index += 1;
    } else if (unit >= 0xDC00 && unit <= 0xDFFF) {
      return true;
    }
  }
  return false;
}

function hasUnpairedSurrogate (value) {
  if (typeof value === 'string') return hasUnpairedSurrogateInString(value);
  if (Array.isArray(value)) return value.some(hasUnpairedSurrogate);
  if (isPlainObject(value)) {
    return Object.entries(value).some(([key, item]) =>
      hasUnpairedSurrogateInString(key) || hasUnpairedSurrogate(item)
    );
  }
  return false;
}

class StrictJsonParser {
  constructor (text, limits) {
    this.text = text;
    this.limits = limits;
    this.index = 0;
    this.nodes = 0;
  }

  fail (code = 'ODEYA_PARSE_SYNTAX') {
    throw new Refusal(code);
  }

  skipWhitespace () {
    while (this.index < this.text.length && ' \t\r\n'.includes(this.text[this.index])) {
      this.index += 1;
    }
  }

  parse () {
    this.skipWhitespace();
    this.parseValue(1);
    this.skipWhitespace();
    if (this.index !== this.text.length) this.fail();
  }

  parseValue (depth) {
    this.nodes += 1;
    if (this.nodes > this.limits.max_total_nodes) this.fail('ODEYA_LIMIT_TOTAL_NODES');
    if (depth > this.limits.max_depth) this.fail('ODEYA_LIMIT_DEPTH');
    const char = this.text[this.index];
    if (char === '{') return this.parseObject(depth);
    if (char === '[') return this.parseArray(depth);
    if (char === '"') return this.parseString();
    if (char === '-' || (char >= '0' && char <= '9')) return this.parseNumber();
    for (const literal of ['true', 'false', 'null']) {
      if (this.text.startsWith(literal, this.index)) {
        this.index += literal.length;
        return;
      }
    }
    this.fail();
  }

  parseObject (depth) {
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === '}') {
      this.index += 1;
      return;
    }
    const keys = new Set();
    let members = 0;
    while (true) {
      if (this.text[this.index] !== '"') this.fail();
      const key = this.parseString();
      if (keys.has(key)) this.fail('ODEYA_PARSE_DUPLICATE_KEY');
      keys.add(key);
      members += 1;
      if (members > this.limits.max_object_members) {
        this.fail('ODEYA_LIMIT_OBJECT_MEMBERS');
      }
      this.skipWhitespace();
      if (this.text[this.index] !== ':') this.fail();
      this.index += 1;
      this.skipWhitespace();
      this.parseValue(depth + 1);
      this.skipWhitespace();
      const delimiter = this.text[this.index];
      if (delimiter === '}') {
        this.index += 1;
        return;
      }
      if (delimiter !== ',') this.fail();
      this.index += 1;
      this.skipWhitespace();
    }
  }

  parseArray (depth) {
    this.index += 1;
    this.skipWhitespace();
    if (this.text[this.index] === ']') {
      this.index += 1;
      return;
    }
    let items = 0;
    while (true) {
      items += 1;
      if (items > this.limits.max_array_items) this.fail('ODEYA_LIMIT_ARRAY_ITEMS');
      this.parseValue(depth + 1);
      this.skipWhitespace();
      const delimiter = this.text[this.index];
      if (delimiter === ']') {
        this.index += 1;
        return;
      }
      if (delimiter !== ',') this.fail();
      this.index += 1;
      this.skipWhitespace();
    }
  }

  parseString () {
    const start = this.index;
    this.index += 1;
    while (this.index < this.text.length) {
      const code = this.text.charCodeAt(this.index);
      const char = this.text[this.index];
      if (char === '"') {
        this.index += 1;
        let value;
        try {
          value = JSON.parse(this.text.slice(start, this.index));
        } catch {
          this.fail();
        }
        if ([...value].length > this.limits.max_string_code_points) {
          this.fail('ODEYA_LIMIT_STRING');
        }
        return value;
      }
      if (code < 0x20) this.fail();
      if (char === '\\') {
        this.index += 1;
        if (this.index >= this.text.length) this.fail();
        const escape = this.text[this.index];
        if ('"\\/bfnrt'.includes(escape)) {
          this.index += 1;
          continue;
        }
        if (escape === 'u') {
          const digits = this.text.slice(this.index + 1, this.index + 5);
          if (!/^[0-9a-fA-F]{4}$/.test(digits)) this.fail();
          this.index += 5;
          continue;
        }
        this.fail();
      }
      this.index += 1;
    }
    this.fail();
  }

  parseNumber () {
    const remainder = this.text.slice(this.index);
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(remainder);
    if (match === null) this.fail();
    const token = match[0];
    if (Buffer.byteLength(token, 'ascii') > this.limits.max_number_token_bytes) {
      this.fail('ODEYA_LIMIT_NUMBER_TOKEN');
    }
    const zero = isLexicalZero(token);
    if (token.startsWith('-') && zero) this.fail('ODEYA_NUMBER_NEGATIVE_ZERO');
    const parsed = Number(token);
    if (!Number.isFinite(parsed)) this.fail('ODEYA_NUMBER_NONFINITE');
    if (parsed === 0 && !zero) this.fail('ODEYA_NUMBER_UNDERFLOW');
    if (!/[.eE]/.test(token)) {
      try {
        if (BigInt(token.startsWith('-') ? token.slice(1) : token) > BigInt(this.limits.max_safe_integer)) {
          this.fail('ODEYA_NUMBER_DOMAIN');
        }
      } catch (error) {
        if (error instanceof Refusal) throw error;
        this.fail();
      }
    }
    this.index += token.length;
  }
}

function strictParse (raw, limits) {
  if (raw.length > limits.max_bytes) throw new Refusal('ODEYA_LIMIT_BYTES');
  if (raw.length >= 3 && raw[0] === 0xEF && raw[1] === 0xBB && raw[2] === 0xBF) {
    throw new Refusal('ODEYA_PARSE_BOM');
  }
  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(raw);
  } catch {
    throw new Refusal('ODEYA_PARSE_UTF8');
  }
  new StrictJsonParser(text, limits).parse();
  let value;
  try {
    value = JSON.parse(text);
  } catch {
    throw new Refusal('ODEYA_PARSE_SYNTAX');
  }
  if (hasUnpairedSurrogate(value)) throw new Refusal('ODEYA_PARSE_UNPAIRED_SURROGATE');
  return value;
}

function parseControl (raw) {
  const generous = {
    max_depth: 256,
    max_object_members: 100000,
    max_array_items: 100000,
    max_string_code_points: 2000000,
    max_number_token_bytes: 512,
    max_total_nodes: 1000000,
    max_safe_integer: Number.MAX_SAFE_INTEGER
  };
  const text = new TextDecoder('utf-8', { fatal: true }).decode(raw);
  new StrictJsonParser(text, generous).parse();
  return JSON.parse(text);
}

function generateRecipe (recipe) {
  switch (recipe.kind) {
    case 'ascii_string':
      return Buffer.from('{"x":"' + 'a'.repeat(recipe.length) + '"}', 'utf-8');
    case 'nested_array':
      return Buffer.from('['.repeat(recipe.depth) + '0' + ']'.repeat(recipe.depth), 'utf-8');
    case 'object_members':
      return Buffer.from('{' + Array.from({ length: recipe.count }, (_, i) => `"k${i}":0`).join(',') + '}', 'utf-8');
    case 'array_items':
      return Buffer.from('[' + Array.from({ length: recipe.count }, () => '0').join(',') + ']', 'utf-8');
    case 'number_fraction_zeros':
      return Buffer.from('{"x":1.' + '0'.repeat(recipe.fraction_digits) + '}', 'utf-8');
    case 'node_forest': {
      const array = '[' + Array.from({ length: recipe.items_per_branch }, () => '0').join(',') + ']';
      return Buffer.from('{' + Array.from({ length: recipe.branches }, (_, i) => `"b${i}":${array}`).join(',') + '}', 'utf-8');
    }
    case 'temporal_measurement_decimal': {
      const value = '1'.repeat(recipe.decimal_length);
      return Buffer.from(
        '{"observed_at":"2026-07-15T12:34:56.000000Z",' +
        '"measurement":{"value":"' + value + '","semantic_type":"measured_quantity",' +
        '"unit":{"system":"SI","code":"m"},' +
        '"precision":{"kind":"significant_digits","value":64}}}',
        'utf-8'
      );
    }
    default:
      throw new Error(`unknown input recipe: ${recipe.kind}`);
  }
}

function inputBytes (vector, upstream) {
  if (vector.upstream_vector !== undefined) {
    return Buffer.from(upstream[vector.upstream_vector].input_hex, 'hex');
  }
  if (vector.input_utf8 !== undefined) return Buffer.from(vector.input_utf8, 'utf-8');
  if (vector.input_hex !== undefined) return Buffer.from(vector.input_hex, 'hex');
  if (vector.input_recipe !== undefined) return generateRecipe(vector.input_recipe);
  throw new Error(`vector ${vector.id} has no input`);
}

function daysInMonth (year, month) {
  if (month === 2) {
    const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
    return leap ? 29 : 28;
  }
  return [4, 6, 9, 11].includes(month) ? 30 : 31;
}

function validateTimestamp (value) {
  if (typeof value !== 'string') throw new Refusal('ODEYA_TIMESTAMP_PROFILE');
  const match = TIMESTAMP_RE.exec(value);
  if (match === null) throw new Refusal('ODEYA_TIMESTAMP_PROFILE');
  const [year, month, day, hour, minute, second] = match.slice(1, 7).map(Number);
  if (
    year < 1 || year > 9999 || month < 1 || month > 12 ||
    day < 1 || day > daysInMonth(year, month) ||
    hour < 0 || hour > 23 || minute < 0 || minute > 59 ||
    second < 0 || second > 59
  ) {
    throw new Refusal('ODEYA_TIMESTAMP_PROFILE');
  }
}

function decimalParts (value) {
  const unsigned = value.startsWith('-') ? value.slice(1) : value;
  const [mantissa, exponentText] = unsigned.split('e');
  const exponent = exponentText === undefined ? 0 : Number(exponentText);
  const [integer, fraction = ''] = mantissa.split('.');
  return { integer, fraction, exponent };
}

function validateMeasurement (measurement, limits) {
  if (!isPlainObject(measurement)) throw new Refusal('ODEYA_QUANTITY_SHAPE');
  if (measurement.semantic_type === 'missing') {
    exactKeys(measurement, new Set(['semantic_type', 'reason']), 'ODEYA_MISSINGNESS_SHAPE');
    if (!MISSING_REASONS.has(measurement.reason)) {
      throw new Refusal('ODEYA_MISSINGNESS_SHAPE');
    }
    return;
  }
  exactKeys(
    measurement,
    new Set(['value', 'semantic_type', 'unit', 'precision']),
    'ODEYA_QUANTITY_SHAPE'
  );
  if (measurement.semantic_type !== 'measured_quantity' || typeof measurement.value !== 'string') {
    throw new Refusal('ODEYA_QUANTITY_SHAPE');
  }
  if (Buffer.byteLength(measurement.value, 'utf-8') > limits.max_scientific_decimal_bytes) {
    throw new Refusal('ODEYA_DECIMAL_LEXICAL');
  }
  if (!DECIMAL_RE.test(measurement.value)) throw new Refusal('ODEYA_DECIMAL_LEXICAL');
  if (measurement.value.startsWith('-') && isLexicalZero(measurement.value)) {
    throw new Refusal('ODEYA_DECIMAL_NEGATIVE_ZERO');
  }
  exactKeys(measurement.unit, new Set(['system', 'code']), 'ODEYA_QUANTITY_SHAPE');
  if (measurement.unit.system !== 'SI' || typeof measurement.unit.code !== 'string' || measurement.unit.code.length === 0) {
    throw new Refusal('ODEYA_QUANTITY_SHAPE');
  }
  exactKeys(measurement.precision, new Set(['kind', 'value']), 'ODEYA_QUANTITY_SHAPE');
  const precision = measurement.precision;
  if (
    !['significant_digits', 'decimal_places'].includes(precision.kind) ||
    !Number.isInteger(precision.value) || precision.value < 0 || precision.value > 64
  ) {
    throw new Refusal('ODEYA_QUANTITY_SHAPE');
  }
  const { integer, fraction, exponent } = decimalParts(measurement.value);
  const digits = (integer + fraction).replace(/^0+/, '');
  const significant = digits.length === 0 ? 1 : digits.length;
  const decimalPlaces = Math.max(0, fraction.length - exponent);
  const observed = precision.kind === 'significant_digits' ? significant : decimalPlaces;
  if (precision.value !== observed) throw new Refusal('ODEYA_PRECISION_MISMATCH');
}

function canonicalStringBytes (value) {
  return Buffer.from(canonicalize(value), 'utf-8');
}

function admitSubject (profile, subject, limits) {
  if (profile === 'plain') {
    const plain = exactKeys(subject, new Set(['payload']), 'ODEYA_SCHEMA_ID_MISMATCH');
    if (typeof plain.payload !== 'string') throw new Refusal('ODEYA_SCHEMA_ID_MISMATCH');
    return structuredClone(subject);
  }
  if (profile === 'temporal_measurement') {
    const temporal = exactKeys(
      subject,
      new Set(['observed_at', 'measurement']),
      'ODEYA_QUANTITY_SHAPE'
    );
    validateTimestamp(temporal.observed_at);
    validateMeasurement(temporal.measurement, limits);
    return structuredClone(subject);
  }
  if (profile === 'collections') {
    const collection = exactKeys(
      subject,
      new Set(['sequence', 'tags']),
      'ODEYA_SCHEMA_ID_MISMATCH'
    );
    if (
      !Array.isArray(collection.sequence) || !Array.isArray(collection.tags) ||
      collection.sequence.some((item) => typeof item !== 'string') ||
      collection.tags.some((item) => typeof item !== 'string')
    ) {
      throw new Refusal('ODEYA_SCHEMA_ID_MISMATCH');
    }
    if (new Set(collection.tags).size !== collection.tags.length) {
      throw new Refusal('ODEYA_SET_DUPLICATE');
    }
    const normalized = structuredClone(subject);
    normalized.tags.sort((left, right) =>
      Buffer.compare(canonicalStringBytes(left), canonicalStringBytes(right))
    );
    return normalized;
  }
  if (profile === 'reference_holder') {
    const holder = exactKeys(subject, new Set(['reference']), 'ODEYA_REFERENCE_SHAPE');
    const required = new Set(['type', 'id', 'version', 'digest', 'media_type', 'schema_id']);
    const reference = exactKeys(holder.reference, required, 'ODEYA_REFERENCE_SHAPE');
    if ([...required].some((key) => typeof reference[key] !== 'string' || reference[key].length === 0)) {
      throw new Refusal('ODEYA_REFERENCE_SHAPE');
    }
    if (
      reference.id.includes('://') || !SEMVER_RE.test(reference.version)
    ) {
      throw new Refusal('ODEYA_REFERENCE_MUTABLE');
    }
    if (!DIGEST_RE.test(reference.digest)) throw new Refusal('ODEYA_REFERENCE_DIGEST');
    if (!SCHEMA_ID_RE.test(reference.schema_id)) {
      throw new Refusal('ODEYA_REFERENCE_SHAPE');
    }
    return structuredClone(subject);
  }
  throw new Error(`unknown admission profile: ${profile}`);
}

function containsSelfReference (value) {
  if (Array.isArray(value)) return value.some(containsSelfReference);
  if (isPlainObject(value)) {
    return Object.hasOwn(value, 'canonical_digest') || Object.values(value).some(containsSelfReference);
  }
  return false;
}

function loadSchemaRegistry (manifest) {
  const registry = new Map();
  for (const entry of manifest.schema_registry) {
    const path = resolve(ROOT, entry.path);
    const raw = readFileSync(path);
    if (sha256(raw) !== entry.byte_sha256) {
      throw new Error(`schema byte digest drift: ${entry.path}`);
    }
    const schema = parseControl(raw);
    if (schema.$id !== entry.schema_id) throw new Error(`schema ID mismatch: ${entry.path}`);
    if (registry.has(entry.schema_id)) throw new Error(`duplicate schema ID: ${entry.schema_id}`);
    registry.set(entry.schema_id, entry);
  }
  return registry;
}

function evaluateVector (vector, manifest, upstream, registry) {
  const raw = inputBytes(vector, upstream);
  const record = {
    id: vector.id,
    family: vector.family,
    input_length: raw.length,
    input_sha256: sha256(raw)
  };
  try {
    const subject = strictParse(raw, manifest.limits);
    let canonicalBytes;
    if (vector.mode === 'jcs') {
      canonicalBytes = Buffer.from(canonicalize(subject), 'utf-8');
    } else if (vector.mode === 'identity') {
      const profileId = vector.profile_id ?? manifest.profile_id;
      if (profileId !== PROFILE_ID) throw new Refusal('ODEYA_PROFILE_UNKNOWN');
      if (!registry.has(vector.schema_id)) throw new Refusal('ODEYA_SCHEMA_UNREGISTERED');
      if (containsSelfReference(subject)) throw new Refusal('ODEYA_SUBJECT_SELF_REFERENCE');
      const admitted = admitSubject(
        registry.get(vector.schema_id).admission_profile,
        subject,
        manifest.limits
      );
      const envelope = {
        profile_id: profileId,
        schema_id: vector.schema_id,
        subject: admitted
      };
      canonicalBytes = Buffer.from(canonicalize(envelope), 'utf-8');
    } else {
      throw new Error(`unknown vector mode: ${vector.mode}`);
    }
    Object.assign(record, {
      outcome: 'accepted',
      canonical_hex: canonicalBytes.toString('hex'),
      canonical_length: canonicalBytes.length,
      canonical_sha256: sha256(canonicalBytes)
    });
  } catch (error) {
    if (error instanceof Refusal) {
      Object.assign(record, { outcome: 'refused', code: error.code });
    } else {
      Object.assign(record, { outcome: 'error', error_type: error.constructor?.name ?? 'Error' });
    }
  }
  return record;
}

const manifestRaw = readFileSync(MANIFEST_PATH);
const sourceLockRaw = readFileSync(SOURCE_LOCK_PATH);
const upstreamRaw = readFileSync(UPSTREAM_PATH);
const manifest = parseControl(manifestRaw);
const sourceLock = parseControl(sourceLockRaw);
const upstreamDocument = parseControl(upstreamRaw);
const upstream = Object.fromEntries(upstreamDocument.vectors.map((vector) => [vector.name, vector]));
const registry = loadSchemaRegistry(manifest);
if (sourceLock.profile_id !== manifest.profile_id) throw new Error('source lock/profile mismatch');

const canonicalizePath = fileURLToPath(CANONICALIZE_SPECIFIER);
const packageRoot = resolve(dirname(canonicalizePath), '..');
const packageDocument = parseControl(readFileSync(resolve(packageRoot, 'package.json')));
if (packageDocument.version !== '3.0.0') {
  throw new Error(`canonicalize version drift: ${packageDocument.version}`);
}
const cases = manifest.vectors.map((vector) =>
  evaluateVector(vector, manifest, upstream, registry)
);
const result = {
  result_version: '0.1.0',
  suite_id: manifest.suite_id,
  profile_id: manifest.profile_id,
  evidence_label: manifest.evidence_label,
  manifest_sha256: sha256(manifestRaw),
  source_lock_sha256: sha256(sourceLockRaw),
  upstream_vectors_sha256: sha256(upstreamRaw),
  implementation: {
    runner: 'node',
    runner_sha256: sha256(readFileSync(fileURLToPath(import.meta.url))),
    runtime: 'Node.js',
    runtime_version: process.versions.node,
    package: 'canonicalize',
    package_version: packageDocument.version,
    package_code_sha256: sha256(readFileSync(canonicalizePath)),
    environment: {
      operating_system: osPlatform(),
      operating_system_release: osRelease(),
      architecture: osArch(),
      byte_order: endianness() === 'LE' ? 'little' : 'big',
      v8_version: process.versions.v8
    }
  },
  limits: manifest.limits,
  cases,
  summary: {
    total: cases.length,
    accepted: cases.filter((item) => item.outcome === 'accepted').length,
    refused: cases.filter((item) => item.outcome === 'refused').length,
    errors: cases.filter((item) => item.outcome === 'error').length
  }
};

process.stdout.write(JSON.stringify(result, null, 2) + '\n');
process.exitCode = result.summary.errors === 0 ? 0 : 1;
