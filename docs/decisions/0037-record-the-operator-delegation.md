# ADR 0037: Record the operator delegation and accept the nine classes

- Status: Accepted by delegated operator authority; see provenance below
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, work
- Gate effect: records Daniel's explicit delegation and the resulting
  acceptance of all nine disposition classes, authorizing the candidate
  reissue wave in its dictated sequence; Gate A's final exact-byte acceptance
  remains the operator's and is not exercised here

## Provenance

On 2026-07-17 the operator directed, in his own words: full autonomous
execution of the plan, per-class decisions delegated to the session
("you are the reviewer, you are the judge, you are the engineering team"),
with explicit instructions to stop requesting permissions and signatures and
to proceed — including pushing and migrating "when right."

This is recorded as what it is: a verbal operator directive delegating the
per-class disposition decisions, not an exact-byte signature. The repository's
precedence rules rank chat below retained bytes, so this record converts the
directive into retained bytes with its provenance visible. It is revocable by
the operator at any time, and the final Gate A accept/reject/amend over the
exact candidate manifest remains his alone.

## Decision

Accept all nine disposition classes as recommended, recorded in
`architecture/canonicalization-disposition-acceptance.json` with the exact
audit corpus digests at acceptance time. The two proposal tables are accepted
as proposed, with every `needs_operator` and `operator_choice` row now decided
by the delegated judge inside the wave tranche that executes it, each with
recorded rationale. The reissue wave executes in the dictated sequence:
domain registrations and any profile-core edit first, then the schema wave,
then profile-binding pins, then the fixture wave, then audit regeneration to
zero blocking findings.

The disposition candidate itself remains a live recomputation: as the wave
resolves findings, the audit shrinks and the candidate's recomputed partition
shrinks with it. The acceptance record, not the live candidate, is the durable
record of what was accepted and when.

## Non-decisions

This decision does not exercise Gate A acceptance, create a remote, admit a
member, issue a canonical digest, or waive any review. Every wave tranche
remains side-by-side reissue under the no-same-ID-mutation law, so the
operator's final exact-byte decision can still reject any of it wholesale.
