#!/usr/bin/env node

import {
  InputRefusal,
  materializeVector,
  parseCommandLine,
  readStrictJson,
  validateVectorCorpus,
} from "./input-adapter.mjs";
import { evaluateEligibility, validateResolver, validateRuleset } from "./evaluator.mjs";

const EXACT_NODE_VERSION = "v24.18.0";
const RULESET_BASENAME = "human-decision-assurance-individual-eligibility-ruleset-v2-candidate.json";
const RESOLVER_BASENAME = "human-decision-assurance-content-address-resolver-profile-v1-candidate.json";

function refuse(condition, message) {
  if (!condition) throw new InputRefusal(message);
}

function main() {
  refuse(process.version === EXACT_NODE_VERSION, `exact Node.js ${EXACT_NODE_VERSION.slice(1)} required; observed ${process.version}`);
  const command = parseCommandLine(process.argv.slice(2));
  const corpus = validateVectorCorpus(readStrictJson(command.vectorsPath, "vectors.json", "vectors corpus"));
  const ruleset = validateRuleset(readStrictJson(command.rulesetPath, RULESET_BASENAME, "eligibility ruleset"));
  const resolver = validateResolver(readStrictJson(command.resolverPath, RESOLVER_BASENAME, "resolver profile"));
  refuse(corpus.ruleset_id === ruleset.ruleset_id, "vectors corpus: ruleset identity mismatch");
  refuse(corpus.resolver_profile_id === resolver.profile_id, "vectors corpus: resolver identity mismatch");
  const input = materializeVector(corpus, command.vectorId);
  const output = evaluateEligibility(input, ruleset, resolver);
  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
}

try {
  main();
} catch (error) {
  if (error instanceof InputRefusal) {
    process.stderr.write(`input refused: ${error.message}\n`);
    process.exitCode = 2;
  } else {
    process.stderr.write(`evaluator failure: ${error instanceof Error ? error.message : "unknown error"}\n`);
    process.exitCode = 1;
  }
}
