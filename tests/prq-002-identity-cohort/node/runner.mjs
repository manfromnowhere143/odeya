#!/usr/bin/env node
/** Separate-language Node.js recomputer for the PRQ-002A identity probe. */

import { createHash } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const SUITE = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = resolve(SUITE, '../..');
const PROFILE_ID = 'urn:odeya:canonicalization:prq-002-identity-probe-jcs-0.1';
const PROFILE_SCHEMA_ID =
  'urn:odeya:architecture-schema:prq-002-identity-probe-profile:0.1.0';
const IDENTITY_SCOPE = 'prq_002_structural_probe_only';
const PROBE_STATUS = 'test_only_non_issuable_structural_probe';
if (Object.hasOwn(process.env, 'ODEYA_PRQ002_CANONICALIZE_MODULE')) {
  throw new Error('ambient canonicalize module override is forbidden');
}
const CANONICALIZE_PATH = pathToFileURL(
  resolve(SUITE, 'node/node_modules/canonicalize/lib/canonicalize.js')
).href;
const canonicalizeModule = await import(CANONICALIZE_PATH);
const canonicalize = canonicalizeModule.default;

const SCHEMA_MEMBER_ROLES = [
  'aggregate_state_member_probe_schema',
  'event_member_probe_schema',
  'identity_probe_profile_schema',
  'ordered_commitment_probe_schema',
  'pure_snapshot_probe_schema',
  'reducer_member_probe_schema',
  'schema_member_probe_schema',
  'structural_event_schema',
  'structural_state_schema'
];
const MEMBER_ROLES = [...SCHEMA_MEMBER_ROLES, 'aggregate_state', 'reducer', 'event'];
const FAMILIES = [
  'schema_registry',
  'aggregate_state_subject_registry',
  'reducer_registry',
  'event_contract_registry'
];
const FAMILY_MEMBER_ROLES = {
  schema_registry: SCHEMA_MEMBER_ROLES,
  aggregate_state_subject_registry: ['aggregate_state'],
  reducer_registry: ['reducer'],
  event_contract_registry: ['event']
};
const FAMILY_KEY_EXPRESSIONS = {
  schema_registry: 'schema_id@semantic_version',
  aggregate_state_subject_registry: 'aggregate_type',
  reducer_registry: 'aggregate_type',
  event_contract_registry: 'event_type@event_version'
};
const SNAPSHOT_DOMAINS = {
  schema_registry: 'odeya-prq-002-schema-registry-snapshot-probe-v1',
  aggregate_state_subject_registry:
    'odeya-prq-002-aggregate-state-registry-snapshot-probe-v1',
  reducer_registry: 'odeya-prq-002-reducer-registry-snapshot-probe-v1',
  event_contract_registry: 'odeya-prq-002-event-registry-snapshot-probe-v1'
};
const SNAPSHOT_REGISTRY_IDS = {
  schema_registry: 'schema-registry-probe',
  aggregate_state_subject_registry: 'aggregate-state-subject-registry-probe',
  reducer_registry: 'reducer-registry-probe',
  event_contract_registry: 'event-contract-registry-probe'
};
const COHORT_AUTHORITY_KEYS = new Set([
  'canonical_identity_issued',
  'registry_admission',
  'engine_contract_root_binding',
  'gate_a_acceptance',
  'runtime_authority',
  'external_effect_authority',
  'publication_authority'
]);
const PROFILE_AUTHORITY_KEYS = new Set([
  'canonical_identity_issued',
  'profile_registry_member_exists',
  'product_schema_domain_rebinding_authorized',
  'engine_contract_root_binding_exists',
  'gate_a_complete',
  'runtime_authorized',
  'deployment_authorized',
  'external_effects_authorized',
  'publication_authorized'
]);
const ROLE_DOMAINS = {
  aggregate_state: 'odeya-prq-002-aggregate-state-member-probe-v1',
  reducer: 'odeya-prq-002-reducer-member-probe-v1',
  event: 'odeya-prq-002-event-member-probe-v1'
};
const EXPECTED_PARSER_SEMANTICS = {
  positive_underflow: {
    input: '1e-400',
    outcome: 'accepted',
    ieee754_conversion: 'positive_zero'
  },
  negative_underflow: {
    input: '-1e-400',
    outcome: 'accepted',
    ieee754_conversion: 'negative_zero'
  },
  lexical_negative_zero: {
    input: '-0',
    outcome: 'refused',
    error: 'strict_input_negative_zero'
  }
};

class StrictInputError extends Error {
  constructor (code) {
    super(code);
    this.code = code;
  }
}

function sha256Bytes (bytes) {
  return `sha256:${createHash('sha256').update(bytes).digest('hex')}`;
}

function bindFile (path) {
  const raw = readFileSync(path);
  return { raw_sha256: sha256Bytes(raw), byte_count: raw.length };
}

function bindBytes (bytes) {
  return { raw_sha256: sha256Bytes(bytes), byte_count: bytes.length };
}

function isObject (value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function deepCopy (value) {
  return structuredClone(value);
}

function equal (left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function sortedUnique (values) {
  return [...new Set(values)].sort();
}

function schemaTypeMatches (value, expected) {
  if (expected === 'object') return isObject(value);
  if (expected === 'array') return Array.isArray(value);
  if (expected === 'string') return typeof value === 'string';
  if (expected === 'integer') return Number.isInteger(value);
  if (expected === 'number') return typeof value === 'number' && Number.isFinite(value);
  if (expected === 'boolean') return typeof value === 'boolean';
  if (expected === 'null') return value === null;
  return false;
}

function schemaPointer (document, fragment) {
  if (fragment === '') return document;
  if (!fragment.startsWith('/')) throw new Error('unsupported schema fragment');
  let current = document;
  for (const token of fragment.slice(1).split('/')) {
    const decoded = token.replaceAll('~1', '/').replaceAll('~0', '~');
    current = Array.isArray(current) ? current[Number(decoded)] : current[decoded];
  }
  return current;
}

function validateProbeSchema (
  instance,
  schema,
  registry,
  rootSchema = null,
  path = ''
) {
  const errors = [];
  if (typeof schema === 'boolean') return schema ? [] : [`${path}:false_schema`];
  if (!isObject(schema)) return [`${path}:invalid_schema`];
  const root = rootSchema ?? schema;
  if (Object.hasOwn(schema, '$ref')) {
    const reference = schema.$ref;
    let targetRoot;
    let fragment;
    if (typeof reference !== 'string') return [`${path}:invalid_ref`];
    if (reference.startsWith('#')) {
      targetRoot = root;
      fragment = reference.slice(1);
    } else {
      const marker = reference.indexOf('#');
      const base = marker === -1 ? reference : reference.slice(0, marker);
      fragment = marker === -1 ? '' : reference.slice(marker + 1);
      targetRoot = registry[base];
      if (targetRoot === undefined) return [`${path}:unresolved_ref`];
    }
    let target;
    try {
      target = schemaPointer(targetRoot, fragment);
    } catch {
      return [`${path}:unresolved_ref`];
    }
    errors.push(...validateProbeSchema(instance, target, registry, targetRoot, path));
  }
  if (typeof schema.type === 'string' && !schemaTypeMatches(instance, schema.type)) {
    errors.push(`${path}:type`);
    return errors;
  }
  if (Object.hasOwn(schema, 'const') && !equal(instance, schema.const)) {
    errors.push(`${path}:const`);
  }
  if (Array.isArray(schema.enum) &&
      !schema.enum.some(item => equal(instance, item))) {
    errors.push(`${path}:enum`);
  }
  if (Array.isArray(schema.allOf)) {
    schema.allOf.forEach((child, index) => {
      errors.push(...validateProbeSchema(
        instance, child, registry, root, `${path}/allOf/${index}`
      ));
    });
  }
  if (Array.isArray(schema.oneOf)) {
    const matches = schema.oneOf.filter(
      child => validateProbeSchema(instance, child, registry, root, path).length === 0
    ).length;
    if (matches !== 1) errors.push(`${path}:oneOf`);
  }
  if (isObject(schema.if) || typeof schema.if === 'boolean') {
    const condition = validateProbeSchema(
      instance, schema.if, registry, root, path
    ).length === 0;
    const branch = condition ? schema.then : schema.else;
    if (isObject(branch) || typeof branch === 'boolean') {
      errors.push(...validateProbeSchema(instance, branch, registry, root, path));
    }
  }
  if (isObject(instance)) {
    if (Array.isArray(schema.required)) {
      for (const name of schema.required) {
        if (!Object.hasOwn(instance, name)) errors.push(`${path}/${name}:required`);
      }
    }
    if (isObject(schema.properties)) {
      for (const [name, child] of Object.entries(schema.properties)) {
        if (Object.hasOwn(instance, name)) {
          errors.push(...validateProbeSchema(
            instance[name], child, registry, root, `${path}/${name}`
          ));
        }
      }
      if (schema.additionalProperties === false) {
        for (const name of Object.keys(instance)) {
          if (!Object.hasOwn(schema.properties, name)) {
            errors.push(`${path}/${name}:additionalProperties`);
          }
        }
      }
    }
  }
  if (Array.isArray(instance)) {
    if (Number.isInteger(schema.minItems) && instance.length < schema.minItems) {
      errors.push(`${path}:minItems`);
    }
    if (Number.isInteger(schema.maxItems) && instance.length > schema.maxItems) {
      errors.push(`${path}:maxItems`);
    }
    if (schema.uniqueItems === true) {
      const rendered = instance.map(item => canonicalize(item));
      if (new Set(rendered).size !== rendered.length) errors.push(`${path}:uniqueItems`);
    }
    const prefix = Array.isArray(schema.prefixItems) ? schema.prefixItems : [];
    prefix.slice(0, instance.length).forEach((child, index) => {
      errors.push(...validateProbeSchema(
        instance[index], child, registry, root, `${path}/${index}`
      ));
    });
    const start = prefix.length;
    if (schema.items === false && instance.length > start) {
      errors.push(`${path}:items`);
    } else if (isObject(schema.items) || typeof schema.items === 'boolean') {
      for (let index = start; index < instance.length; index += 1) {
        errors.push(...validateProbeSchema(
          instance[index], schema.items, registry, root, `${path}/${index}`
        ));
      }
    }
  }
  if (typeof instance === 'string') {
    const length = [...instance].length;
    if (Number.isInteger(schema.minLength) && length < schema.minLength) {
      errors.push(`${path}:minLength`);
    }
    if (Number.isInteger(schema.maxLength) && length > schema.maxLength) {
      errors.push(`${path}:maxLength`);
    }
    if (typeof schema.pattern === 'string' &&
        !(new RegExp(schema.pattern, 'u')).test(instance)) {
      errors.push(`${path}:pattern`);
    }
  }
  if (Number.isInteger(instance) && typeof schema.minimum === 'number' &&
      instance < schema.minimum) {
    errors.push(`${path}:minimum`);
  }
  return errors;
}

class StrictParser {
  constructor (text) {
    this.text = text;
    this.index = 0;
  }

  fail (code = 'strict_input_syntax') {
    throw new StrictInputError(code);
  }

  whitespace () {
    while (this.index < this.text.length && ' \t\r\n'.includes(this.text[this.index])) {
      this.index += 1;
    }
  }

  parse () {
    this.whitespace();
    const value = this.value();
    this.whitespace();
    if (this.index !== this.text.length) this.fail('strict_input_trailing_data');
    return value;
  }

  value () {
    const char = this.text[this.index];
    if (char === '{') return this.object();
    if (char === '[') return this.array();
    if (char === '"') return this.string();
    if (char === '-' || (char >= '0' && char <= '9')) return this.number();
    for (const [token, value] of [['true', true], ['false', false], ['null', null]]) {
      if (this.text.startsWith(token, this.index)) {
        this.index += token.length;
        return value;
      }
    }
    if (this.text.startsWith('NaN', this.index) ||
        this.text.startsWith('Infinity', this.index) ||
        this.text.startsWith('-Infinity', this.index)) {
      this.fail('strict_input_nonfinite');
    }
    this.fail();
  }

  object () {
    const output = {};
    const names = new Set();
    this.index += 1;
    this.whitespace();
    if (this.text[this.index] === '}') {
      this.index += 1;
      return output;
    }
    while (true) {
      if (this.text[this.index] !== '"') this.fail();
      const name = this.string();
      if (names.has(name)) this.fail('strict_input_duplicate_key');
      names.add(name);
      this.whitespace();
      if (this.text[this.index] !== ':') this.fail();
      this.index += 1;
      this.whitespace();
      output[name] = this.value();
      this.whitespace();
      if (this.text[this.index] === '}') {
        this.index += 1;
        return output;
      }
      if (this.text[this.index] !== ',') this.fail();
      this.index += 1;
      this.whitespace();
    }
  }

  array () {
    const output = [];
    this.index += 1;
    this.whitespace();
    if (this.text[this.index] === ']') {
      this.index += 1;
      return output;
    }
    while (true) {
      output.push(this.value());
      this.whitespace();
      if (this.text[this.index] === ']') {
        this.index += 1;
        return output;
      }
      if (this.text[this.index] !== ',') this.fail();
      this.index += 1;
      this.whitespace();
    }
  }

  string () {
    const start = this.index;
    this.index += 1;
    while (this.index < this.text.length) {
      const char = this.text[this.index];
      if (char === '"') {
        this.index += 1;
        try {
          const value = JSON.parse(this.text.slice(start, this.index));
          if ([...value].some(character => {
            const code = character.codePointAt(0);
            return code >= 0xD800 && code <= 0xDFFF;
          })) this.fail('strict_input_unicode');
          return value;
        } catch (error) {
          if (error instanceof StrictInputError) throw error;
          this.fail();
        }
      }
      if (char === '\\') {
        this.index += 1;
        if (this.index >= this.text.length) this.fail();
        const escape = this.text[this.index];
        if ('"\\/bfnrt'.includes(escape)) {
          this.index += 1;
          continue;
        }
        if (escape === 'u' && /^[0-9a-fA-F]{4}$/.test(
          this.text.slice(this.index + 1, this.index + 5)
        )) {
          this.index += 5;
          continue;
        }
        this.fail();
      }
      if (this.text.charCodeAt(this.index) < 0x20) this.fail();
      this.index += 1;
    }
    this.fail();
  }

  number () {
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(
      this.text.slice(this.index)
    );
    if (match === null) this.fail();
    const token = match[0];
    const unsigned = token.startsWith('-') ? token.slice(1) : token;
    const mantissa = unsigned.split(/[eE]/)[0];
    const lexicalZero = [...mantissa].every(char => char === '0' || char === '.');
    if (token.startsWith('-') && lexicalZero) this.fail('strict_input_negative_zero');
    const value = Number(token);
    if (!Number.isFinite(value)) this.fail('strict_input_nonfinite');
    this.index += token.length;
    return value;
  }
}

function strictLoadBytes (raw) {
  if (raw.length >= 3 && raw[0] === 0xEF && raw[1] === 0xBB && raw[2] === 0xBF) {
    throw new StrictInputError('strict_input_bom');
  }
  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(raw);
  } catch {
    throw new StrictInputError('strict_input_utf8');
  }
  return new StrictParser(text).parse();
}

function strictLoadPath (path) {
  return strictLoadBytes(readFileSync(path));
}

function parserSemanticsObservation () {
  const observation = {};
  for (const [name, token] of [
    ['positive_underflow', '1e-400'],
    ['negative_underflow', '-1e-400']
  ]) {
    const value = strictLoadBytes(Buffer.from(token, 'ascii'));
    observation[name] = {
      input: token,
      outcome: 'accepted',
      ieee754_conversion: Object.is(value, -0) ? 'negative_zero' : 'positive_zero'
    };
  }
  try {
    strictLoadBytes(Buffer.from('-0', 'ascii'));
    observation.lexical_negative_zero = {
      input: '-0',
      outcome: 'accepted',
      error: null
    };
  } catch (error) {
    if (!(error instanceof StrictInputError)) throw error;
    observation.lexical_negative_zero = {
      input: '-0',
      outcome: 'refused',
      error: error.code
    };
  }
  return observation;
}

function pointerParts (pointer) {
  if (typeof pointer !== 'string' || !pointer.startsWith('/')) {
    throw new Error('mutation path is not an absolute JSON pointer');
  }
  return pointer.slice(1).split('/').map(
    token => token.replaceAll('~1', '/').replaceAll('~0', '~')
  );
}

function resolvePointer (document, pointer) {
  let current = document;
  for (const token of pointerParts(pointer)) {
    if (Array.isArray(current)) {
      const index = Number(token);
      if (!Number.isInteger(index) || index < 0 || index >= current.length) {
        throw new Error('JSON pointer array index is absent');
      }
      current = current[index];
    } else if (isObject(current) && Object.hasOwn(current, token)) {
      current = current[token];
    } else {
      throw new Error('JSON pointer object member is absent');
    }
  }
  return current;
}

function patchObject (document, mutation) {
  const parts = pointerParts(mutation.path);
  let parent = document;
  for (const token of parts.slice(0, -1)) {
    parent = Array.isArray(parent) ? parent[Number(token)] : parent[token];
  }
  const final = parts.at(-1);
  if (mutation.op === 'remove') {
    if (Array.isArray(parent)) parent.splice(Number(final), 1);
    else delete parent[final];
    return;
  }
  const value = Object.hasOwn(mutation, 'value_from')
    ? deepCopy(resolvePointer(document, mutation.value_from))
    : deepCopy(mutation.value);
  if (Array.isArray(parent)) {
    if (mutation.op === 'add') {
      if (final === '-') parent.push(value);
      else parent.splice(Number(final), 0, value);
    } else if (mutation.op === 'replace') {
      parent[Number(final)] = value;
    } else if (mutation.op === 'swap') {
      const other = Number(mutation.other_index);
      const index = Number(final);
      [parent[index], parent[other]] = [parent[other], parent[index]];
    } else {
      throw new Error(`unsupported list mutation ${mutation.op}`);
    }
  } else if (mutation.op === 'add') {
    if (Object.hasOwn(parent, final)) throw new Error('add target exists');
    parent[final] = value;
  } else if (mutation.op === 'replace') {
    if (!Object.hasOwn(parent, final)) throw new Error('replace target absent');
    parent[final] = value;
  } else {
    throw new Error(`unsupported object mutation ${mutation.op}`);
  }
}

function mutateRaw (raw, mutation) {
  if (mutation.op === 'prepend_bom') {
    return Buffer.concat([Buffer.from([0xEF, 0xBB, 0xBF]), raw]);
  }
  if (mutation.op === 'append_trailing_object') {
    return Buffer.concat([raw, Buffer.from('\n{}\n')]);
  }
  if (mutation.op === 'inject_invalid_utf8') {
    return Buffer.concat([raw.subarray(0, 1), Buffer.from([0xFF]), raw.subarray(1)]);
  }
  const text = raw.toString('utf8');
  if (mutation.op === 'duplicate_top_level_status') {
    const needle = '  "status": "test_only_non_issuable_structural_probe",';
    if (!text.includes(needle)) throw new Error('status anchor absent');
    return Buffer.from(text.replace(needle, `${needle}\n${needle}`));
  }
  const needle = '"member_count": 9';
  if (!text.includes(needle)) throw new Error('member-count anchor absent');
  if (mutation.op === 'lexical_negative_zero') {
    return Buffer.from(text.replace(needle, '"member_count": -0'));
  }
  if (mutation.op === 'lexical_nonfinite') {
    return Buffer.from(text.replace(needle, '"member_count": NaN'));
  }
  if (mutation.op === 'numeric_overflow') {
    return Buffer.from(text.replace(needle, '"member_count": 1e400'));
  }
  if (mutation.op === 'escaped_lone_surrogate') {
    const artifact = '"artifact_class": "prq_002_identity_probe_candidate_cohort"';
    if (!text.includes(artifact)) throw new Error('artifact-class anchor absent');
    return Buffer.from(text.replace(artifact, '"artifact_class": "\\ud800"'));
  }
  throw new Error(`unsupported raw mutation ${mutation.op}`);
}

function schemaIndex (manifest) {
  return Object.fromEntries(manifest.schema_resources.map(item => [item.role, item]));
}

function schemaDocument (resource) {
  const value = strictLoadPath(resolve(ROOT, resource.path));
  if (!isObject(value)) throw new Error('schema is not an object');
  return value;
}

function expectedProfileRef (manifest) {
  return {
    profile_id: PROFILE_ID,
    profile_version: '0.1.0',
    profile_core_schema_id: PROFILE_SCHEMA_ID,
    profile_core_raw_digest: manifest.probe_profile_core.raw_sha256
  };
}

function expectedContract (
  schemas,
  manifest,
  schemaRole,
  schema,
  resultField,
  domain
) {
  return {
    algorithm: 'sha256',
    domain_separator: domain,
    canonicalization_profile_ref: expectedProfileRef(manifest),
    subject_schema_ref: {
      schema_id: schemas[schemaRole].schema_id,
      schema_digest: schemas[schemaRole].raw_sha256
    },
    included_json_pointers: schema.required
      .filter(name => name !== resultField)
      .map(name => `/${name}`),
    excluded_json_pointers: [`/${resultField}`]
  };
}

function scopedDigest (subject, contractField) {
  const contract = subject[contractField];
  const projection = {};
  for (const pointer of contract.included_json_pointers) {
    const parts = pointerParts(pointer);
    if (parts.length !== 1) throw new Error('digest pointer is not root-only');
    projection[parts[0]] = deepCopy(resolvePointer(subject, pointer));
  }
  const scoped = {
    digest_contract: deepCopy(contract),
    resolved_subject_schema: deepCopy(contract.subject_schema_ref),
    projection
  };
  const canonicalText = canonicalize(scoped);
  if (typeof canonicalText !== 'string') throw new Error('canonicalizer did not return text');
  const raw = Buffer.from(canonicalText, 'utf8');
  const digest = sha256Bytes(raw);
  return {
    digest,
    canonical_byte_count: raw.length,
    canonical_hex: raw.toString('hex'),
    canonical_sha256: digest
  };
}

function falseBoundary (value, exactKeys) {
  return isObject(value) &&
    equal(Object.keys(value).sort(), [...exactKeys].sort()) &&
    Object.values(value).every(item => item === false);
}

function expectedSchemaBytes (schemas, role) {
  const resource = schemas[role.slice(0, -'_schema'.length)];
  return {
    schema_id: resource.schema_id,
    semantic_version: '0.1.0',
    byte_digest: resource.raw_sha256,
    byte_count: resource.byte_count,
    media_type: 'application/schema+json',
    encoding: 'utf-8',
    dialect: 'https://json-schema.org/draft/2020-12/schema',
    root_json_type: 'object',
    retrieval: 'content_addressed_retained_raw_bytes'
  };
}

function validateProfile (candidate, manifest, schemas, errors) {
  const profile = candidate.profile;
  if (!isObject(profile)) {
    errors.push('profile_contract_mismatch');
    return;
  }
  if (profile.schema_version !== '0.1.0' ||
      profile.artifact_class !== 'prq_002_identity_probe_profile' ||
      profile.profile_id !== PROFILE_ID ||
      profile.profile_version !== '0.1.0' ||
      profile.status !== PROBE_STATUS) {
    errors.push('profile_contract_mismatch');
  }
  const core = manifest.base_profile_core;
  const coreRef = {
    profile_id: 'urn:odeya:canonicalization:odeya-jcs-0.1',
    profile_version: '0.1.0',
    profile_core_schema_id: 'urn:odeya:schema:canonicalization-profile-core:0.5.0',
    profile_core_raw_digest: core.raw_sha256,
    profile_core_byte_count: core.byte_count,
    profile_core_schema_raw_digest: core.schema_raw_sha256,
    profile_core_schema_byte_count: core.schema_byte_count
  };
  if (!equal(profile.base_profile_core_ref, coreRef)) {
    errors.push('profile_base_core_binding_mismatch');
  }
  const expectedDomains = manifest.domain_bindings.map(domain => {
    const resource = schemas[domain.schema_role];
    return {
      domain_separator: domain.domain_separator,
      subject_class: domain.subject_class,
      declaring_schema_id: resource.schema_id,
      declaring_schema_raw_digest: resource.raw_sha256,
      declaring_schema_byte_count: resource.byte_count,
      binding_status: 'probe_only_not_registered_not_issuable'
    };
  });
  if (!equal(profile.domain_registry, expectedDomains)) {
    errors.push('profile_domain_registry_mismatch');
  }
  if (!falseBoundary(profile.authority_boundary, PROFILE_AUTHORITY_KEYS)) {
    errors.push('profile_authority_boundary_mismatch');
  }
}

function validateSchemaMembers (candidate, manifest, schemas, errors, records) {
  const members = candidate.members;
  if (!isObject(members)) {
    errors.push('member_inventory_mismatch');
    return;
  }
  const schema = schemaDocument(schemas.schema_member_probe);
  const contract = expectedContract(
    schemas,
    manifest,
    'schema_member_probe',
    schema,
    'member_digest',
    'odeya-prq-002-schema-member-probe-v1'
  );
  for (const role of SCHEMA_MEMBER_ROLES) {
    const member = members[role];
    if (!isObject(member)) {
      errors.push('schema_member_inventory_mismatch');
      continue;
    }
    if (!equal(Object.keys(member).sort(), [...schema.required].sort())) {
      errors.push('schema_member_shape_mismatch');
    }
    const schemaBytes = expectedSchemaBytes(schemas, role);
    if (!equal(member.schema_bytes, schemaBytes)) {
      errors.push('schema_member_raw_binding_mismatch');
    }
    const key = `${schemaBytes.schema_id}@${schemaBytes.semantic_version}`;
    if (member.member_key !== key) errors.push('schema_member_key_mismatch');
    if (!equal(member.member_digest_contract, contract)) {
      errors.push('schema_member_digest_contract_mismatch');
    }
    try {
      const record = scopedDigest(member, 'member_digest_contract');
      records[role] = record;
      if (member.member_digest !== record.digest) {
        errors.push('schema_member_digest_mismatch');
      }
    } catch {
      errors.push('schema_member_digest_construction_failed');
    }
  }
}

function expectedStateSchemaRef (members, schemas) {
  const resource = schemas.structural_state;
  const member = members.structural_state_schema;
  return {
    schema_member_key: member.member_key,
    schema_id: resource.schema_id,
    semantic_version: '0.1.0',
    byte_digest: resource.raw_sha256,
    byte_count: resource.byte_count,
    dialect: 'https://json-schema.org/draft/2020-12/schema',
    root_json_type: 'object',
    schema_member_digest: member.member_digest
  };
}

function expectedEventSchemaRef (members, schemas) {
  const resource = schemas.structural_event;
  const member = members.structural_event_schema;
  return {
    schema_member_key: member.member_key,
    schema_id: resource.schema_id,
    semantic_version: '0.1.0',
    byte_digest: resource.raw_sha256,
    byte_count: resource.byte_count,
    dialect: 'https://json-schema.org/draft/2020-12/schema',
    root_json_type: 'object',
    schema_member_digest: member.member_digest
  };
}

function validateGraphMembers (candidate, manifest, schemas, errors, records) {
  const members = candidate.members;
  if (!isObject(members)) return;
  if (!equal(Object.keys(members).sort(), [...MEMBER_ROLES].sort())) {
    errors.push('member_inventory_mismatch');
  }
  const state = members.aggregate_state;
  const reducer = members.reducer;
  const event = members.event;
  if (![state, reducer, event].every(isObject)) {
    errors.push('graph_member_inventory_mismatch');
    return;
  }
  const eventReverse = {
    event_type: 'structural.event_recorded',
    event_version: '0.1.0',
    reference_kind: 'logical_reverse_reference',
    resolution_requirement: 'future_same_root_exact_member'
  };
  const reducerReverse = {
    aggregate_type: 'structural-aggregate',
    reducer_id: 'reducer.structural-aggregate',
    reducer_version: '0.1.0',
    reference_kind: 'logical_reverse_reference',
    resolution_requirement: 'future_same_root_exact_member'
  };
  const stateContract = expectedContract(
    schemas,
    manifest,
    'aggregate_state_member_probe',
    schemaDocument(schemas.aggregate_state_member_probe),
    'member_digest',
    ROLE_DOMAINS.aggregate_state
  );
  if (state.member_key !== 'structural-aggregate' ||
      state.aggregate_type !== 'structural-aggregate' ||
      state.state_subject_id !== 'state.structural-aggregate' ||
      state.state_subject_version !== '0.1.0' ||
      state.owning_module !== 'structural-module') {
    errors.push('state_identity_mismatch');
  }
  if (!equal(state.state_schema_ref, expectedStateSchemaRef(members, schemas))) {
    errors.push('state_schema_reference_mismatch');
  }
  if (!equal(state.canonical_reducer_ref, reducerReverse) ||
      !equal(state.origin_event_refs, [eventReverse])) {
    errors.push('state_reverse_reference_mismatch');
  }
  if (!equal(state.member_digest_contract, stateContract)) {
    errors.push('state_digest_contract_mismatch');
  }
  try {
    const record = scopedDigest(state, 'member_digest_contract');
    records.aggregate_state = record;
    if (state.member_digest !== record.digest) errors.push('state_member_digest_mismatch');
  } catch {
    errors.push('state_digest_construction_failed');
  }

  const reducerContract = expectedContract(
    schemas,
    manifest,
    'reducer_member_probe',
    schemaDocument(schemas.reducer_member_probe),
    'member_digest',
    ROLE_DOMAINS.reducer
  );
  if (reducer.member_key !== 'structural-aggregate' ||
      reducer.aggregate_type !== 'structural-aggregate' ||
      reducer.reducer_id !== 'reducer.structural-aggregate' ||
      reducer.reducer_version !== '0.1.0' ||
      reducer.owning_module !== 'structural-module') {
    errors.push('reducer_identity_mismatch');
  }
  const stateRef = {
    aggregate_type: 'structural-aggregate',
    state_subject_id: 'state.structural-aggregate',
    state_subject_version: '0.1.0',
    state_member_digest: state.member_digest,
    resolution: 'exact_probe_member_digest'
  };
  if (!equal(reducer.state_subject_ref, stateRef)) {
    errors.push('reducer_state_reference_mismatch');
  }
  if (!equal(reducer.accepted_event_refs, [eventReverse])) {
    errors.push('reducer_reverse_reference_mismatch');
  }
  if (!equal(reducer.member_digest_contract, reducerContract)) {
    errors.push('reducer_digest_contract_mismatch');
  }
  try {
    const record = scopedDigest(reducer, 'member_digest_contract');
    records.reducer = record;
    if (reducer.member_digest !== record.digest) errors.push('reducer_member_digest_mismatch');
  } catch {
    errors.push('reducer_digest_construction_failed');
  }

  const eventContract = expectedContract(
    schemas,
    manifest,
    'event_member_probe',
    schemaDocument(schemas.event_member_probe),
    'member_digest',
    ROLE_DOMAINS.event
  );
  if (event.member_key !== 'structural.event_recorded@0.1.0' ||
      event.event_type !== 'structural.event_recorded' ||
      event.event_version !== '0.1.0' ||
      event.payload_type_id !==
        'urn:odeya:architecture:event-payload:structural.event-recorded:0.1.0') {
    errors.push('event_identity_mismatch');
  }
  const payload = {
    event_envelope_schema_ref: expectedEventSchemaRef(members, schemas),
    payload_json_pointer: '/oneOf/0/properties/payload',
    payload_required: true,
    nullable: false,
    exact_branch_required: true
  };
  if (!equal(event.payload_contract, payload)) {
    errors.push('event_schema_reference_mismatch');
  }
  const owner = {
    owning_module: 'structural-module',
    aggregate_type: 'structural-aggregate',
    ownership_cardinality: 'exactly_one'
  };
  if (!equal(event.aggregate_owner, owner)) {
    errors.push('event_aggregate_owner_mismatch');
  }
  const command = {
    command_type: 'structural.command_probe',
    command_version: '0.1.0',
    reference_kind: 'logical_reverse_reference',
    resolution_requirement: 'future_same_root_exact_member'
  };
  if (!equal(event.producer_command_refs, [command])) {
    errors.push('event_command_reference_mismatch');
  }
  const reducerRef = {
    aggregate_type: 'structural-aggregate',
    reducer_id: 'reducer.structural-aggregate',
    reducer_version: '0.1.0',
    reducer_member_digest: reducer.member_digest,
    resolution: 'exact_probe_member_digest'
  };
  if (!equal(event.canonical_reducer_ref, reducerRef)) {
    errors.push('event_reducer_reference_mismatch');
  }
  if (!equal(event.member_digest_contract, eventContract)) {
    errors.push('event_digest_contract_mismatch');
  }
  try {
    const record = scopedDigest(event, 'member_digest_contract');
    records.event = record;
    if (event.member_digest !== record.digest) errors.push('event_member_digest_mismatch');
  } catch {
    errors.push('event_digest_construction_failed');
  }
}

function memberPair (members, role) {
  return {
    member_key: members[role].member_key,
    member_digest: members[role].member_digest
  };
}

function byteCompare (left, right) {
  return Buffer.compare(Buffer.from(left, 'utf8'), Buffer.from(right, 'utf8'));
}

function validateCommitments (candidate, manifest, schemas, errors, records) {
  const commitments = candidate.commitments;
  const members = candidate.members;
  const profile = candidate.profile;
  if (![commitments, members, profile].every(isObject)) {
    errors.push('commitment_inventory_mismatch');
    return;
  }
  if (!equal(Object.keys(commitments).sort(), [...FAMILIES].sort())) {
    errors.push('commitment_inventory_mismatch');
  }
  const schema = schemaDocument(schemas.ordered_commitment_probe);
  const contract = expectedContract(
    schemas,
    manifest,
    'ordered_commitment_probe',
    schema,
    'ordered_member_pairs_digest',
    'odeya-prq-002-ordered-member-map-commitment-probe-v1'
  );
  for (const family of FAMILIES) {
    const commitment = commitments[family];
    if (!isObject(commitment)) {
      errors.push('commitment_inventory_mismatch');
      continue;
    }
    const expectedPairs = FAMILY_MEMBER_ROLES[family]
      .map(role => memberPair(members, role))
      .sort((left, right) => byteCompare(left.member_key, right.member_key));
    const observed = commitment.ordered_members;
    if (!Array.isArray(observed)) {
      errors.push('commitment_member_set_mismatch');
    } else {
      const keys = observed.filter(isObject).map(item => item.member_key);
      if (new Set(keys).size !== keys.length) {
        errors.push('commitment_member_keys_not_unique');
      }
      const ordered = [...keys].sort(byteCompare);
      if (!equal(keys, ordered)) errors.push('commitment_order_mismatch');
      if (!equal(observed, expectedPairs)) errors.push('commitment_member_set_mismatch');
    }
    if (commitment.member_count !== expectedPairs.length) {
      errors.push('commitment_count_mismatch');
    }
    const keyContract = profile.member_key_profiles?.[family];
    if (commitment.registry_family !== family ||
        commitment.algorithm !== 'odeya-canonical-map-commitment-v1' ||
        !equal(commitment.member_key_contract, keyContract) ||
        keyContract?.member_key_expression !== FAMILY_KEY_EXPRESSIONS[family]) {
      errors.push('commitment_family_contract_mismatch');
    }
    if (!equal(commitment.ordered_member_pairs_digest_contract, contract)) {
      errors.push('commitment_digest_contract_mismatch');
    }
    try {
      const record = scopedDigest(commitment, 'ordered_member_pairs_digest_contract');
      records[family] = record;
      if (commitment.ordered_member_pairs_digest !== record.digest) {
        errors.push('commitment_digest_mismatch');
      }
    } catch {
      errors.push('commitment_digest_construction_failed');
    }
  }
}

function validateSnapshots (candidate, manifest, schemas, errors, records) {
  const snapshots = candidate.snapshots;
  const commitments = candidate.commitments;
  if (!isObject(snapshots) || !isObject(commitments)) {
    errors.push('snapshot_inventory_mismatch');
    return;
  }
  if (!equal(Object.keys(snapshots).sort(), [...FAMILIES].sort())) {
    errors.push('snapshot_inventory_mismatch');
  }
  const schema = schemaDocument(schemas.pure_snapshot_probe);
  const expectedTop = [...schema.required].sort();
  for (const family of FAMILIES) {
    const snapshot = snapshots[family];
    if (!isObject(snapshot)) {
      errors.push('snapshot_inventory_mismatch');
      continue;
    }
    if (!equal(Object.keys(snapshot).sort(), expectedTop)) {
      errors.push('snapshot_forbidden_member_present');
    }
    const contract = expectedContract(
      schemas,
      manifest,
      'pure_snapshot_probe',
      schema,
      'snapshot_digest',
      SNAPSHOT_DOMAINS[family]
    );
    if (snapshot.registry_family !== family ||
        snapshot.identity_scope !== IDENTITY_SCOPE ||
        snapshot.version !== '0.1.0') {
      errors.push('snapshot_identity_mismatch');
    }
    if (snapshot.registry_id !== SNAPSHOT_REGISTRY_IDS[family]) {
      errors.push('snapshot_registry_id_mismatch');
    }
    const predecessor = snapshot.supersedes_snapshot_ref;
    if (predecessor !== null) {
      errors.push('snapshot_predecessor_reference_mismatch');
    }
    if (!equal(snapshot.canonicalization_profile_ref, expectedProfileRef(manifest))) {
      errors.push('snapshot_profile_reference_mismatch');
    }
    if (!equal(snapshot.member_set_commitment, commitments[family])) {
      errors.push('snapshot_commitment_binding_mismatch');
    }
    if (!equal(snapshot.snapshot_digest_contract, contract)) {
      errors.push('snapshot_digest_contract_mismatch');
    }
    try {
      const record = scopedDigest(snapshot, 'snapshot_digest_contract');
      records[family] = record;
      if (snapshot.snapshot_digest !== record.digest) {
        errors.push('snapshot_digest_mismatch');
      }
    } catch {
      errors.push('snapshot_digest_construction_failed');
    }
  }
}

function evaluateCandidate (candidate, manifest) {
  const errors = [];
  if (!isObject(candidate)) return { errors: ['cohort_shape_mismatch'], projection: {} };
  const top = [
    'schema_version', 'artifact_class', 'status', 'profile', 'members',
    'commitments', 'snapshots', 'authority_boundary'
  ].sort();
  if (!equal(Object.keys(candidate).sort(), top)) errors.push('cohort_shape_mismatch');
  if (candidate.schema_version !== '0.1.0' ||
      candidate.artifact_class !== 'prq_002_identity_probe_candidate_cohort' ||
      candidate.status !== PROBE_STATUS) {
    errors.push('cohort_status_mismatch');
  }
  if (!falseBoundary(candidate.authority_boundary, COHORT_AUTHORITY_KEYS)) {
    errors.push('cohort_authority_boundary_mismatch');
  }
  const schemas = schemaIndex(manifest);
  const schemaRoles = [
    'identity_probe_profile',
    'schema_member_probe',
    'aggregate_state_member_probe',
    'reducer_member_probe',
    'event_member_probe',
    'ordered_commitment_probe',
    'pure_snapshot_probe',
    'structural_state',
    'structural_event'
  ];
  if (!equal(Object.keys(schemas).sort(), schemaRoles.sort())) {
    return {
      errors: sortedUnique([...errors, 'schema_resource_inventory_mismatch']),
      projection: {}
    };
  }
  for (const [field, code] of [
    ['base_profile_core', 'base_profile_core_raw_binding_mismatch'],
    ['probe_profile_core', 'probe_profile_core_raw_binding_mismatch']
  ]) {
    const item = manifest[field];
    try {
      const observed = bindFile(resolve(ROOT, item.path));
      if (item.raw_sha256 !== observed.raw_sha256 ||
          item.byte_count !== observed.byte_count) {
        errors.push(code);
      }
    } catch {
      errors.push(code);
    }
    try {
      const observedSchema = bindFile(resolve(ROOT, item.schema_path));
      if (item.schema_raw_sha256 !== observedSchema.raw_sha256 ||
          item.schema_byte_count !== observedSchema.byte_count) {
        errors.push(`${field}_schema_raw_binding_mismatch`);
      }
    } catch {
      errors.push(`${field}_schema_raw_binding_mismatch`);
    }
  }
  let retainedProbeCore = null;
  try {
    retainedProbeCore = strictLoadPath(resolve(ROOT, manifest.probe_profile_core.path));
  } catch {}
  if (!equal(candidate.profile, retainedProbeCore)) {
    errors.push('probe_profile_core_instance_mismatch');
  }
  const schemaDocuments = {};
  for (const [role, resource] of Object.entries(schemas)) {
    let observed;
    try {
      observed = bindFile(resolve(ROOT, resource.path));
      const schema = schemaDocument(resource);
      schemaDocuments[role] = schema;
      if (schema.$id !== resource.schema_id) errors.push('schema_resource_id_mismatch');
    } catch {
      errors.push('schema_resource_parse_failure');
      continue;
    }
    if (resource.raw_sha256 !== observed.raw_sha256 ||
        resource.byte_count !== observed.byte_count) {
      errors.push('schema_resource_raw_binding_mismatch');
    }
  }
  const registry = Object.fromEntries(
    Object.values(schemaDocuments)
      .filter(schema => typeof schema.$id === 'string')
      .map(schema => [schema.$id, schema])
  );
  if (validateProbeSchema(
    candidate.profile,
    schemaDocuments.identity_probe_profile ?? {},
    registry
  ).length > 0) {
    errors.push('profile_schema_invalid');
  }
  if (isObject(candidate.members)) {
    for (const role of SCHEMA_MEMBER_ROLES) {
      if (validateProbeSchema(
        candidate.members[role],
        schemaDocuments.schema_member_probe ?? {},
        registry
      ).length > 0) {
        errors.push('schema_member_schema_invalid');
      }
    }
    for (const [role, schemaRole] of [
      ['aggregate_state', 'aggregate_state_member_probe'],
      ['reducer', 'reducer_member_probe'],
      ['event', 'event_member_probe']
    ]) {
      if (validateProbeSchema(
        candidate.members[role],
        schemaDocuments[schemaRole] ?? {},
        registry
      ).length > 0) {
        errors.push(`${role}_schema_invalid`);
      }
    }
  }
  if (isObject(candidate.commitments)) {
    for (const family of FAMILIES) {
      if (validateProbeSchema(
        candidate.commitments[family],
        schemaDocuments.ordered_commitment_probe ?? {},
        registry
      ).length > 0) {
        errors.push('commitment_schema_invalid');
      }
    }
  }
  if (isObject(candidate.snapshots)) {
    for (const family of FAMILIES) {
      if (validateProbeSchema(
        candidate.snapshots[family],
        schemaDocuments.pure_snapshot_probe ?? {},
        registry
      ).length > 0) {
        errors.push('snapshot_schema_invalid');
      }
    }
  }
  validateProfile(candidate, manifest, schemas, errors);
  const members = {};
  validateSchemaMembers(candidate, manifest, schemas, errors, members);
  validateGraphMembers(candidate, manifest, schemas, errors, members);
  const commitments = {};
  validateCommitments(candidate, manifest, schemas, errors, commitments);
  const snapshots = {};
  validateSnapshots(candidate, manifest, schemas, errors, snapshots);
  return {
    errors: sortedUnique(errors),
    projection: {
      cohort_census: {
        profile_instances: 1,
        schema_members: SCHEMA_MEMBER_ROLES.length,
        graph_members: 3,
        members: MEMBER_ROLES.length,
        commitments: FAMILIES.length,
        snapshots: FAMILIES.length,
        total_probe_objects: 21
      },
      member_digest_records: members,
      commitment_digest_records: commitments,
      snapshot_digest_records: snapshots
    }
  };
}

function materializeCase (baseRaw, item) {
  if (item.mutation === null || item.mutation === undefined) {
    try {
      return { candidate: strictLoadBytes(baseRaw), strictError: null };
    } catch (error) {
      if (error instanceof StrictInputError) {
        return { candidate: null, strictError: error.code };
      }
      throw error;
    }
  }
  if (item.mutation.layer === 'raw') {
    try {
      return {
        candidate: strictLoadBytes(mutateRaw(baseRaw, item.mutation)),
        strictError: null
      };
    } catch (error) {
      if (error instanceof StrictInputError) {
        return { candidate: null, strictError: error.code };
      }
      throw error;
    }
  }
  const candidate = strictLoadBytes(baseRaw);
  patchObject(candidate, item.mutation);
  return { candidate, strictError: null };
}

function evaluateCases (baseRaw, manifest, cases) {
  const rows = [];
  let safeProjection = {};
  for (const item of cases.cases) {
    const materialized = materializeCase(baseRaw, item);
    let errors;
    let projection = {};
    if (materialized.strictError !== null) {
      errors = [materialized.strictError];
    } else {
      const evaluated = evaluateCandidate(materialized.candidate, manifest);
      errors = evaluated.errors;
      projection = evaluated.projection;
    }
    if (item.kind === 'safe') safeProjection = projection;
    rows.push({
      id: item.id,
      kind: item.kind,
      outcome: errors.length === 0 ? 'accepted' : 'refused',
      errors
    });
  }
  const summary = {
    case_count: rows.length,
    safe_count: rows.filter(row => row.kind === 'safe').length,
    adversarial_count: rows.filter(row => row.kind === 'adversarial').length,
    accepted_count: rows.filter(row => row.outcome === 'accepted').length,
    refused_count: rows.filter(row => row.outcome === 'refused').length
  };
  return { rows, safeProjection, summary };
}

function sourceFileBinding (manifest) {
  const row = manifest.source_files.find(
    item => item.repository_path.endsWith('/node/runner.mjs')
  );
  if (row === undefined) throw new Error('source manifest does not bind runner.mjs');
  return deepCopy(row);
}

function parseArgs (argv) {
  const parsed = {};
  for (let index = 0; index < argv.length;) {
    const option = argv[index];
    if (option === '--emit-execution-attestation') {
      parsed.emitExecutionAttestation = true;
      index += 1;
      continue;
    }
    const value = argv[index + 1];
    if (![
      '--input',
      '--manifest',
      '--cases',
      '--attestation-challenge'
    ].includes(option) || value === undefined) {
      throw new Error(
        'usage: runner.mjs --input PATH --manifest PATH --cases PATH ' +
        '--attestation-challenge CHALLENGE ' +
        '--emit-execution-attestation'
      );
    }
    if (option === '--attestation-challenge') {
      parsed.attestationChallenge = value;
    } else {
      parsed[option.slice(2)] = resolve(value);
    }
    index += 2;
  }
  if (!parsed.input || !parsed.manifest || !parsed.cases ||
      !/^challenge-v1:[0-9a-f]{64}$/.test(parsed.attestationChallenge) ||
      parsed.emitExecutionAttestation !== true) {
    throw new Error('all runner paths are required');
  }
  return parsed;
}

function buildExecutionAttestation (paths, resultLineBinding) {
  const runnerPath = fileURLToPath(import.meta.url);
  const sourceManifestPath = resolve(SUITE, 'node/source-manifest.json');
  const canonicalizerPath = resolve(
    SUITE, 'node/node_modules/canonicalize/lib/canonicalize.js'
  );
  const attested = path => ({
    absolute_path: resolve(path),
    ...bindFile(path)
  });
  return {
    schema_version: '0.1.0',
    artifact_class: 'prq_002_identity_probe_execution_attestation',
    implementation_role: 'node',
    challenge: paths.attestationChallenge,
    result_line_binding: resultLineBinding,
    runtime: {
      name: 'Node.js',
      version: process.versions.node,
      process_exec_path: process.execPath,
      resolved_executable: realpathSync(process.execPath),
      executable_binding: bindFile(realpathSync(process.execPath)),
      process_argv0: process.argv0
    },
    process_argv: process.argv,
    bindings: {
      runner: attested(runnerPath),
      input: attested(paths.input),
      input_manifest: attested(paths.manifest),
      cases: attested(paths.cases),
      source_manifest: attested(sourceManifestPath),
      canonicalizer_source: attested(canonicalizerPath)
    }
  };
}

function buildResult (paths) {
  const manifest = strictLoadPath(paths.manifest);
  const cases = strictLoadPath(paths.cases);
  const baseRaw = readFileSync(paths.input);
  const evaluated = evaluateCases(baseRaw, manifest, cases);
  const sourceManifestPath = resolve(SUITE, 'node/source-manifest.json');
  const dependencyLockPath = resolve(SUITE, 'node/package-lock.json');
  const suiteManifestPath = resolve(SUITE, 'manifest.json');
  const sourceManifest = strictLoadPath(sourceManifestPath);
  const expectations = Object.fromEntries(cases.cases.map(item => [item.id, item]));
  const expectationsMatch = evaluated.rows.every(row =>
    equal(row.errors, expectations[row.id].expected_errors) &&
    (row.kind !== 'adversarial' ||
      expectations[row.id].intent_errors.every(code => row.errors.includes(code)))
  );
  const safe = evaluated.summary.safe_count === 1 &&
    evaluated.summary.accepted_count === 1 &&
    evaluated.summary.refused_count === evaluated.summary.adversarial_count;
  const parserSemantics = parserSemanticsObservation();
  return {
    schema_version: '0.1.0',
    artifact_class: 'prq_002_identity_probe_recomputation_result',
    result_id: 'prq-002-identity-result.node-canonicalize-3_0_0.0001',
    status: expectationsMatch && safe &&
      equal(parserSemantics, EXPECTED_PARSER_SEMANTICS) ? 'pass' : 'fail',
    evidence_status: PROBE_STATUS,
    implementation: {
      role: 'node',
      runtime: 'Node.js',
      runtime_version: process.versions.node,
      package: 'canonicalize',
      package_version: '3.0.0',
      canonicalization_entrypoint: 'canonicalize default export',
      source_file_binding: sourceFileBinding(sourceManifest),
      source_manifest_binding: bindFile(sourceManifestPath),
      dependency_manifest_binding: bindFile(resolve(SUITE, 'node/package.json')),
      dependency_lock_binding: bindFile(dependencyLockPath),
      peer_source_consumed: false,
      generated_source_consumed: false,
      expected_result_fixture_consumed: false
    },
    input_bindings: {
      suite_manifest: bindFile(suiteManifestPath),
      input_manifest: bindFile(paths.manifest),
      candidate_cohort: bindFile(paths.input),
      cases: bindFile(paths.cases)
    },
    safe_projection: evaluated.safeProjection,
    parser_semantics: parserSemantics,
    cases: evaluated.rows,
    summary: evaluated.summary,
    authority_boundary: {
      canonical_identity_issued: false,
      registry_admission: false,
      engine_contract_root_binding: false,
      gate_a_acceptance: false,
      runtime_authority: false,
      external_effect_authority: false,
      publication_authority: false
    }
  };
}

try {
  const paths = parseArgs(process.argv.slice(2));
  const result = buildResult(paths);
  const resultLine = Buffer.from(`${canonicalize(result)}\n`, 'utf8');
  const attestation = buildExecutionAttestation(paths, bindBytes(resultLine));
  const attestationLine = Buffer.from(`${canonicalize(attestation)}\n`, 'utf8');
  process.stdout.write(attestationLine);
  process.stdout.write(resultLine);
  process.exitCode = result.status === 'pass' ? 0 : 1;
} catch (error) {
  process.stdout.write(JSON.stringify({
    schema_version: '0.1.0',
    artifact_class: 'prq_002_identity_probe_recomputation_failure',
    status: 'fail',
    error_type: error?.constructor?.name ?? 'Error'
  }) + '\n');
  process.exitCode = 1;
}
