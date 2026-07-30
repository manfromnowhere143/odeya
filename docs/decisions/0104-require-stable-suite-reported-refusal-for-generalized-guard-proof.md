# ADR 0104: Require stable suite-reported refusal for generalized guard proof

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-29
- Decision owners: architecture review, evidence integrity, repository release
- Gate effect: proposes an architecture-validation invariant for the
  generalized suite-guard record; grants no correctness, implementation,
  runtime, publication, scientific, or Gate A authority

## Context

[ADR 0065](0065-detection-kind-in-coverage-records.md) made crash detections
visible in the dedicated lifecycle coverage records. [ADR
0079](0079-the-suite-guard-audit-generalized.md) then generalized
refusal-statement mutation across isolated checker suites. Its retained
`0.1.0` record credited any nonzero mutated-suite result as proof and labelled
non-traceback failures `case_attributed`. That label was stronger than the
observation: the generalized audit had neither an exact case-ID refusal
protocol nor a stability control around the mutation.

The unpublished local candidate
`d4b6a821ff9d83aca45a3573403930ab36923dfd` exposed the defect at the
fresh-clone boundary. Its local retained record reported 502 of 1260 guards
proved. Session-observed terminal output from the clean clone reported 501 of
1260 and the rehearsal refused at `suite-guard-coverage`; that diagnostic was
not retained. The external failure receipt is:

`/Users/danielwahnich/workspace/odeya-release-evidence/d4b6a821ff9d83aca45a3573403930ab36923dfd/failure-receipt.txt`

with SHA-256
`e8d0e66b19c1b6832f5f734e6644eef90a6aa93f9f78bf6700940ee7c3a0d23a`.
That receipt records `partial_diagnostics_retained=false` and proves only the
named failed stage and its subject binding. It does not retain the 501 count or
prove why the two session-observed measurements differed.

The session separately ran the old
`product-identity-profile-candidate` checker with guard index 42 disabled in
an isolated copy. The exact ablation exited zero and printed `PASS`. That was
the causal diagnostic used to identify the locally credited row as false, but
it was not retained evidence and cannot be reconstructed from the failure
receipt. The correction therefore strengthens the reusable proof rule rather
than treating that one diagnostic as a new coverage claim.

## Decision

### Correct only the generalized record

The generalized suite-guard record moves to version `0.2.0` and uses the
proof machine below. This decision corrects ADRs 0065 and 0079 only for that
record. The dedicated lifecycle statement and condition records retain their
separately scoped historical semantics and measurements; this decision does
not silently reinterpret them.

### Require a syntax-valid ABA refusal

Before a generalized guard can be recorded as proved, the audit must:

1. require the suite's initial unmodified control to pass;
2. disable exactly the discovered refusal construct in an isolated tree and
   require the resulting checker source to compile;
3. run the mutated suite and observe exit status exactly one, nonempty combined
   standard output and standard error, and no Python interpreter traceback;
4. restore the unmodified checker bytes, refresh only any declared
   isolated-copy checker-byte binding, and require the restored control to
   pass;
5. reinstall the identical mutated checker bytes, refresh the same bounded
   binding, and observe the same refusal again; and
6. require the two mutated observations to have the same `sha256:` fingerprint
   over one compact, sorted-key UTF-8 JSON frame containing the exact numeric
   return code and the exact, separately framed `stdout` and `stderr`
   strings.

The proved row binds that fingerprint. Combining the two streams is permitted
only for the bounded nonempty/no-traceback classifier; the fingerprint keeps
their boundary intact. The restored pass between identical failing mutations
is the ABA control. It makes one stable mutation-specific observation
falsifiable; it is not case attribution or correctness.

Syntax-invalid mutations, empty output, tracebacks, exit codes other than one,
signals, timeouts, failed restored controls, changed repeat output, and every
other unstable observation remain unproved. When the audit can retain such a
detected row, it records that row as crash-only rather than crediting proof;
an instrument-level timeout or execution error may instead abort the
measurement and cannot produce a successful record.

The `0.2.0` guard states are closed:

| `proved` | `detection` | `refusal_fingerprint` | Meaning |
| --- | --- | --- | --- |
| `true` | `suite_reported_refusal` | `sha256:` plus 64 lowercase hexadecimal digits | ABA-stable bounded refusal |
| `false` | `crash` | `null` | crash-only or unstable detection; not proof |
| `false` | `null` | `null` | mutation left the suite passing |

No other Boolean, label, fingerprint, missing member, or extra member is
admitted. The audit's startup self-tests must refuse classifier, framing,
syntax, and ABA weakenings, and the cheap record validator must reject every
state outside this machine. These controls remain bounded proof-of-proof
checks, not a terminal end to the regress described by [ADR
0069](0069-adversarial-review-round-three.md).

### Quarantine the nested predecessor checker

The predecessor `product-identity-profile-candidate` suite invokes the
successor profile checker under a timeout. Under concurrent load, a successor
timeout or other resource failure can become an ordinary exit-one predecessor
report and masquerade as a stable refusal. The generalized audit therefore
runs all other subjects in its bounded process pool, waits for that pool to
finish, and then runs the predecessor suite serially.

Serial ordering removes that known competition with the successor audit. It
does not prove that every resource or startup failure has been excluded.
The `0.2.0` record binds a closed `execution_schedule` object with exact
integer `parallel_max_workers=4`, the sole ordered `serial_suites` member
`product-identity-profile-candidate`, and
`serial_after_parallel=true`. Startup and cheap-validator known-bads reject a
worker-count change, empty or substituted serial inventory, overlap or
incomplete partition, non-Boolean sequencing claim, and an extra schedule
member.

### Preserve the failed attempt and remeasure

The unpublished `d4b6a821ff9d83aca45a3573403930ab36923dfd` candidate is
superseded by the containing amended direct-child candidate; resolve that
candidate's exact SHA from Git. The failed candidate's external
failure receipt remains retained as failed-attempt history; it is not a
successful rehearsal manifest and must not be overwritten or presented as
one.

This decision asserts no corrected numerator, unproved count, or crash count.
Those values exist only after the final `0.2.0` audit is retained and a fresh
clone reproduces the exact candidate bytes.

## Boundaries and non-decisions

The classifier still has no suite-specific machine-readable case-ID envelope.
An exit-one, nonempty, non-traceback startup or infrastructure failure can
therefore still match its bounded refusal shape. ABA reduces one class of
instability; it does not eliminate that masking possibility.

The audit assumes exclusive ownership of each isolated copy while it restores
and replaces checker bytes. It does not claim hostile-concurrent-writer
resistance, ancestor-directory rename safety, a process sandbox, operating
system isolation, dependency-behavior proof, or independent-host
reproduction.

A proved generalized guard establishes only statement reachability for the
exact retained checker and mutation vocabulary. It does not establish
condition coverage, correct intent, complete guard discovery, exact case
attribution, suite correctness, scientific validity, organizational
independence, accountable review, Gate A acceptance, or implementation
authorization. It grants no runtime, deployment, credential, spending, data
access, publication, or external-effect authority.

## Consequences

Generalized coverage can no longer increase because a mutation merely crashes
or because one transient failure happens to return nonzero. Each credited row
now carries a repeatable output identity around a passing restored control,
while unstable observations remain visible without flattering the proof
count.

The cost is additional suite executions and a deliberately narrower claim.
Exact case attribution requires a future suite-specific machine-readable
refusal protocol. Stronger concurrency and startup guarantees require
separate process-isolation and exclusive-writer evidence rather than another
label in this record.
