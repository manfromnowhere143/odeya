# ADR 0097: Adversarially validate the canonicalization evaluator before profile issuance

- Status: Accepted as a bounded architecture-evidence falsifier and issuance
  blocker; the canonical profile remains unissued
- Date: 2026-07-22
- Decision owners: canonical identity, evidence integrity, security
- Gate effect: separates oracle conformity, result comparison, and execution
  origin; grants no profile issuance, admission, independence, Gate A,
  runtime, dispatch, deployment, publication, or external-effect authority

## Context

The retained canonicalization package has 64 cases, four metamorphic
relations, two language-specific result files, and a comparison receipt. The
current comparator checks the frozen oracle, common input bindings, declared
implementation metadata, complete case projections, and agreement between the
two retained results. Those are useful bounded checks, but the result bytes do
not contain a causal receipt proving that the declared runner produced them.

An adversarial no-write probe demonstrated the distinction. It paired the
retained Python result with a copy of the same result whose `implementation`
object alone was replaced by the retained Node metadata. The comparator
returned zero with `status=pass` and `implementation_agreement=true`. The
metadata satisfied the expected Python/Node identities even though both case
sets came from one retained result. A separate omission probe made the overall
comparison fail while leaving `implementation_agreement=true`, because that
boolean currently means only that no error string begins with
`implementation disagreement`.

Therefore the current receipt proves neither execution origin nor independent
execution. Agreement, oracle conformity, completeness, and source separation
are different propositions. Combining them into one pass or one Boolean can
turn copied, incomplete, or common-mode-wrong evidence into a stronger claim
than the retained bytes support.

## Decision

### Add one bounded meta-evaluator, not an evaluator runtime

Odeya adds one central architecture-evidence checker and one compact candidate
record for canonicalization-evaluator integrity. The tranche does not change
the frozen canonical vectors, expectations, source lock, runners, results,
comparison receipt, profile core, profile evidence, schema corpus, or HDA
chain. It does not execute either canonicalizer and does not introduce a new
schema. A schema becomes necessary only if an admitted Odeya consumer later
uses this record type.

The candidate binds the exact published source checkpoint and the exact bytes
of the comparator, manifest, expectations, source lock, both results, and
comparison receipt. The checker byte digest is recorded in the candidate; the
candidate digest is recorded in the case corpus. The case corpus carries no
self-digest, so the dependency remains acyclic.

### Keep three dispositions separate

Every observation preserves these independent states:

- oracle conformity: `pass`, `fail`, `indeterminate`, or `not_run`;
- cross-result case-projection comparison: `exact`, `disagree`, `indeterminate`, or
  `not_run`; and
- execution/source separation: `proven_within_declared_scope`, `not_proven`,
  or `contradicted`.

The unmodified retained result pair may support oracle `pass` and case-projection
comparison `exact`. Its execution origin remains
`unwitnessed_retained_artifact`, so execution/source separation is
`not_proven`. Different language labels, package names, or result metadata do
not establish separate executions, hosts, organizations, or incentives.

No observation can support profile issuance unless execution receipts bind
the fixed commands, source and dependency bytes, inputs, environment,
termination status, complete captured outputs, and result digests. This
tranche contains no such witness and must refuse every stronger claim.

### Retain case contract, repeated trial, trace, and outcome evidence

The case corpus retains each intended falsifier, minimized mutation, and exact
expected outcome. The checker executes each deterministic case twice, compares
the complete observations, and emits one representative observation plus its
repetition count and observation digest. That emitted observation includes an
ordered trace, the complete comparator return code and parsed receipt, and the
three dispositions above. Integrated foundation validation checks the
checker's exit status and does not retain its successful stdout as a repository
artifact.

The safe control supplies the retained Python and Node result files without
reserializing them. The copied-and-relabelled attack instead constructs a
separate right-hand byte sequence: its parsed JSON value equals the retained
Node-labelled result, but its raw digest differs. A mutation witness binds the
source raw and parsed-object digests, the intermediate copied-object digest,
the exact transformed raw digest, and the allowed implementation-field delta.
The postcondition rejects a no-op copy, an unchanged raw source, any additional
semantic delta, or a fabricated witness.

The required trace order is:

1. verify exact subject bindings;
2. materialize an isolated result pair;
3. apply one fixed declared mutation;
4. execute the unchanged comparator;
5. strictly parse the complete receipt;
6. compare the full observation; and
7. check the claim boundary.

The retained attack matrix includes copied output with relabelled
implementation metadata, one-sided tampering, identical common-mode wrong
answers, coordinated omission, duplicate case identity, infrastructure-error
relabeling, implementation-identity substitution, and shared false input or
manifest bindings. A safe control is retained separately. Agreement on the
same wrong answer is `exact` comparison plus failed oracle conformity, not a
pass. Malformed, incomplete, or nonterminal result evidence is
`indeterminate` when the checker can form an observation. A missing bound file
or comparator timeout instead aborts validation without emitting a comparison
disposition. Neither condition is approval by silence.

### Make the gate itself load-bearing

The checker rejects duplicate JSON keys, extra or missing fields, unsafe or
duplicate paths, non-regular files, symlinks, digest or byte-count drift,
changed case census, changed trace order, and unsupported disposition
vocabularies. Comparator executions use one hard-coded command and fixed
arguments in isolated temporary copies with a bounded timeout. Evidence may
name only the mutation fixed by its hard-coded case contract; neither the shell
nor an arbitrary evidence value selects a command or mutation target. Each
trial must reproduce the same complete observation twice.

Thirty-three gate known-bads exercise their named boundaries, including a
blinded or always-pass result, a narrowed observation, fabricated profile
issuance, fabricated human calibration, and a prompt-injection coverage claim
when the subject has no natural-language instruction channel. They also cover
every authority and nonclaim bit, duplicate-key parsing, role/path
substitution, final and ancestor symlinks, timeout configuration and
process-group termination, delegate blindness, and a neutralized copied-output
mutation. They are not a mutation proof of every checker branch. Comparator
processes run in their own process group so timeout termination targets that
group. Exact lexical, resolved, and inode identities keep the seven subject
roles distinct. The checker has no write, update, bless, or regeneration mode.

### Treat a detected defect as a blocker, not a hidden failure

The meta-evaluator is successful when it reproducibly detects and correctly
classifies the comparator's demonstrated false-accept boundary. That success
does not repair the comparator or make its retained results execution
evidence. The candidate therefore records the current execution-origin gap as
blocking. A future successor may close it only by reissuing changed identities
and retaining causal execution receipts plus their own adversarial controls.

## Consequences and nonclaims

This tranche improves the evidence boundary without changing canonical
subjects or the frozen HDA census. Schema, shared-case, isolated-suite,
canonical-vector, metamorphic-relation, and canonical-audit counts are
expected to remain unchanged; all figures must be remeasured rather than
copied.

The current `implementation_agreement` Boolean remains attributable to its
exact historical receipt but is not an independence or execution-origin
claim. The profile remains unissued. Private holdouts, fuzzing, independent
hosts, organizational independence, stochastic or model-grader calibration,
human inter-rater evidence, and accountable canonical-profile review remain
absent.

This is architecture evidence only. It authorizes no product code,
credentials, provider integration, runtime, cloud resource, data access,
spending, deployment, scientific-results publication, Gate A decision, or
external effect.
