# ADR 0038: The first wave tranche executes

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, work
- Gate effect: resolves disposition class D1 completely — the canonical
  migration audit's fixture-timestamp blocker stands at zero — and corrects two
  gates that could not observe success; admits no member and accepts no Gate A
  row

## Execution

The accepted D1 disposition was one identical lexical rewrite: 236
nonconformant fixture timestamps, every one the same seconds-precision shape,
normalized to the frozen UTC microsecond form. Executed mechanically across
110 fixture files; the regenerated audit reports the class at zero and the
other five classes byte-identically unchanged (122 / 129 / 668 / 56 / 11).
The live disposition candidate recomputes to 986 findings, and the acceptance
record retains the 1,222-finding basis the classes were accepted against.

## What the wave taught the gates

Reaching zero exposed that two guards assumed blockage was permanent:

- the profile-evidence schema pinned every blocker count with `minimum: 1`,
  so the evidence could not represent a resolved class. Reissued to 0.2.0 at
  the same path under the ledger's own precedent, blocker minimums now zero,
  corpus counts still at least one; and
- the prerequisite validator read a class's absence from `blocking_findings`
  as a mismatch, when the audit emits a finding only while its count is
  nonzero. Absence is exactly count zero, and the validator now says so.

Both are the same defect this mission has now met at every layer: a gate
written inside the blocked state that refuses the state it exists to reach.

## The deliberate-change cascade, walked

The normalized fixtures were bound, byte-exact, in more places than any list
predicted, and every binding was rebound deliberately rather than loosened:
the work-contract candidate's embedded predecessor projection; the successor
cohort evidence's render-digests; the cohort evidence schema's pinned consts,
reissued to 0.2.0; the reissue ledger's candidate entries; the module
dependency manifest's schema identities and self-digest; and the closure
record and profile evidence digests. The full validator passes at the end of
the chain.

## Non-decisions

This decision does not touch classes D2 through D9, whose tranches follow in
the dictated sequence — domain registrations and the profile-core edit first.
It does not admit a member, issue a canonical digest, or accept Gate A.
