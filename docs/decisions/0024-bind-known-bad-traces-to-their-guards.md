# ADR 0024: Bind every known-bad lifecycle trace to the guard that must refuse it

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-16
- Decision owners: lifecycle closure, canonical identity, cognitive contracts,
  security, architecture review
- Gate effect: completes the PRQ-005 known-bad class set and makes the retained
  lifecycle refusals guard-specific; does not close PRQ-005, admit a member,
  accept Gate A, or authorize runtime work

## Context

Non-negotiable law 11 requires every gate to have a known-bad proof that it
fires. The lifecycle closure suite retained twenty-five adversarial traces, each
naming a guard through `adversarial_tag`. The checker asserted only that some
error was produced. It never asserted which guard produced it.

That gap is not theoretical. Seven of the twenty-five retained traces refuse
with more than one error, and the surplus errors are incidental to the named
guard. In the AuthorityGrant model, any `authority.grant_used` step sets a
pending exhaustion that produces `grant trace ends with an unexhausted final
use` at trace end. That error fires whether or not the use-while-terminal guard
exists, so it masks the guard the trace was written to prove.

Two mutations of the exact committed checker bytes were confirmed blind:

- widening `authority.grant_activated` to accept `active` makes a second
  activation legal. The suite passed, reporting the same
  `cases=sha256:1dbfbd72e2c5856cc43052754bb2c8238f996fad85d1b212c1534e60d4cd49ac`
  digest as the unmutated tree.
- widening `authority.grant_used` to accept `revoked` and `expired` makes use
  after revocation or expiry legal while leaving use-before-active guarded. The
  suite passed.

PRQ-005 separately enumerates four required known-bad classes: use before
activation, double activation, issued-as-active, and use after expiry or
revocation. Only the first and third had retained traces. The
`required_adversarial_tags` list did not detect this, because it was derived
from the traces that existed rather than from the PRQ's stated requirements. A
coverage list that is a restatement of current coverage cannot discover missing
coverage.

This is the discipline already stated for the first vertical slice: a generic
parser error is not proof that the scientific gate works. The same rule was not
applied to the suite's own refusals.

## Decision

Make each retained known-bad trace prove its own guard:

- add the two absent PRQ-005 classes as exact traces —
  `grant-bad-double-activation`, and `grant-bad-use-after-revoked` plus
  `grant-bad-use-after-expired`, keeping revocation and expiry distinct because
  they are separate terminal states reached by separate events;
- add `expected_refusal_contains` to all twenty-eight adversarial cases, naming
  the substring of the refusal that is that guard's own error, with incidental
  errors excluded on purpose; and
- fail the suite when a known-bad trace is accepted, declares no guard, or is
  refused by something other than its declared guard.

Both previously blind mutations now fail closed. The use-while-terminal
mutation fails with `refused, but not by its declared guard "uses a grant while
'revoked'"; got ['grant trace ends with an unexhausted final use']`, naming the
exact incidental error that had been masking it.

No transition table, canonical state vocabulary, event identity, schema byte, or
first-slice boundary is changed. The AuthorityGrant state machine was already
correct for both classes; the defect was evidentiary, not behavioural.

## Non-decisions

This decision does not:

- close PRQ-005, PRQ-006, PRQ-007, or any other prerequisite finding, which
  additionally require an independently reproduced verdict that no single
  producing agent may supply for its own change;
- claim the remaining nineteen single-error traces were verified as isolated
  beyond their now-declared guard;
- prove the six lifecycle models are complete, only that each retained refusal
  is attributable;
- change the 43/60/25/11 first-slice boundary, any state vocabulary, or any
  schema resource;
- admit a member, issue a canonical digest, or resolve any identity; or
- accept Gate A or authorize assignment, dispatch, runtime, or external effects.

## Consequences

A weakened lifecycle guard can no longer hide behind an incidental refusal in
this suite, and PRQ-005 now has a retained trace for each of the four classes it
names. That statement is bounded to guards a trace actually exercises and must
not be read as suite-wide coverage. Independent review confirmed both blindness
claims and both halves of the change as load-bearing — the added traces alone
still miss use-after-terminal, and `expected_refusal_contains` alone cannot
supply an absent class — and separately established that the pre-existing
`grant_use_before_active` trace was itself blind to its own guard: widening the
use guard to accept `issued` left the suite green before this change.

The same review found seven AuthorityGrant guards that remain weakenable with
the suite green because no trace exercises them at all: `exceeds max_uses`, the
immediate-exhaustion rule, the trailing unexhausted-use rule, `declared_from`
consistency, the `not_issued` start requirement, the single-use requirement, and
the unknown-event refusal. None is a PRQ-005 class, so this decision's scope
holds, but two are notable. The README asserts that a single final use is
immediately exhausted, and that property has no known-bad proof — the same law
11 defect this decision exists to fix, still present in the same model. And the
trailing-exhaustion rule that masked the use-after-terminal guard is itself
unproven. Those seven do not hide behind incidental refusals; they have no
evidence at all, which is the weaker position. The `expected_refusal_contains` bindings are themselves a reviewable
surface: a substring that is too generic would silently re-admit the masking it
was added to prevent, so each one must be read against its model's error set
rather than trusted because the suite is green. Each of the twenty-eight
bindings currently matches exactly one error of its own case.

Two limitations are accepted rather than hidden. First, this suite raises
free-text errors with interpolated step indices, so the bindings match on
message substrings rather than on stable error codes. Message rewording breaks
the assertion, which fails closed and is therefore safe, but a structured
refusal code per guard would be the stronger contract and is deferred rather
than dismissed. Second, refusal attribution now has five spellings across the
suites — `required_errors`, `expected_reasons`, `expected_errors`,
`expected_error`, and this one. That divergence is itself a
`CANON-SCHEMA-DEFS-001`-class finding at the harness level and should be
converged on one exact vocabulary before any of these suites is treated as
retained Gate A review evidence.

Refusal attribution is already established practice elsewhere and this suite was
the laggard, not the pioneer: `canonical-profile-candidate` uses
`required_errors`, `command-identity-contracts` uses `expected_reasons`,
`work-identity-successor-cohort` and `work-intent-identity-candidate` use
`expected_errors`, and `work-intent-reference-resolution` uses
`expected_error`. Lifecycle closure predates the practice and was never
upgraded to it.

Six suites still assert refusal without attribution, covering 229 known-bad
cases: `cognitive-contracts` (107), `projection-contracts` (37),
`constitutional-construction` (29), `first-slice-resolution` (21),
`mathematical-contracts` (19), and `architecture-review` (16).
`physical-contracts` retains no known-bad case. Those 229 are not shown here to
be blind; only that they cannot currently distinguish a guard firing from an
incidental refusal, which is the condition that made this suite blind. They
should be audited the same way, by mutation rather than by inspection.

The coverage-list defect is more general than this suite: a required-tag list
derived from current coverage cannot find a missing class, so each PRQ's
enumerated classes should be checked against retained traces directly.
