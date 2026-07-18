# Guard-coverage closure plan

Status: designed roadmap for the 396 unproved guards ADR 0079 measured and
ADR 0080-0082 began closing. Not an accepted contract, not Gate A. Every
number here comes from `architecture/suite-guard-coverage.json`, regenerated
by `scripts/audit_suite_guard_coverage.py`.

## Where coverage stands

Repository guard coverage is 219 of 615 proved by mutation, every proof
case-attributed, zero crash-detected. lifecycle-closure carries its own
dedicated statement (178/185) and condition (100/103) audits and is not in
this figure.

## The 396 open guards, by closure method

Two proven mechanical patterns and one targeted-case class account for all
of them. The split is measured, not estimated.

### Harness-hygiene — 137 guards, proven pattern (ADR 0080/0081)

Guards a malformed case can never reach in a passing suite: "case is not an
object", "mutation failed", "safe reference rejected", the coverage floors.
They close by an in-harness self-test that constructs the malformed thing in
memory, with a meta proof asserting the distinct-refusal count so a
duplicated probe is caught. Four suites are done this way; the rest follow
the same factoring. Concentrations: first-slice-resolution 25,
constitutional-construction 21, projection-contracts 18.

Terminal residue, per ADR 0069: each suite's self-test has its own refusal
statements that only fire when a guard is already broken, plus the
clean-tree collection statements. These are the terminal turtles — closable
by one more injection level at diminishing value, named where each suite
stops.

### Artifact-mutation vocabulary — proven pattern (ADR 0082)

Guards on a once-loaded static record (`inventory_errors` and its kin). A
bounded-replace mutation model against a deep copy, plus ablation-verified
generation, closes them mechanically. Proven on first-slice-resolution's
inventory (20 to 36 statement guards). Applies wherever a suite checks a
loaded artifact once: the module manifest, the identity map, the
disposition record. A generator per artifact, each case verified to fire
its guard before retention.

### Per-case domain logic — targeted cases

Guards inside per-case checkers that no retained case exercises, and that
depend on real evaluate semantics — cross-field comparisons, file-vs-file
equalities, git-derived lineage. These do not fall to a single mutation
vocabulary; each needs a case constructed from the check's own condition,
ablation-verified in the ADR 0071 style. Some are genuinely unreachable by
a candidate mutation without editing retained fixtures (which would corrupt
the safe baseline) and are honest residue, not oversights.
work-intent-reference-resolution is the worked example: of 20 open, roughly
half are candidate-reachable and half are file/git-derived.

## Order of work

1. Harness-hygiene across the eight remaining suites — mechanical, the ADR
   0080 factoring, ~137 guards, highest ratio of guards to effort.
2. Artifact-mutation vocabulary for each once-loaded record — mechanical,
   the ADR 0082 pattern, generator-driven and ablation-verified.
3. Targeted domain cases — careful, per-check, ADR 0071 style, with the
   genuinely-unreachable residue named per suite.

Each increment is measured by the generalized audit before commit, and no
guard is claimed proved that the audit did not confirm.

## Boundary

Statement reachability only; coverage is not correctness. A proved guard
fires, it is not shown to enforce the right rule. Nothing here is an
accountable review determination, an admitted member, or Gate A acceptance.
