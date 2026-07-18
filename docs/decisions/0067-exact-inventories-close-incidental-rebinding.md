# ADR 0067: Exact inventories close the incidental-rebinding attack

- Status: Executed; closes the final surviving weakness of ADR 0063
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: the three subset-enforced suites now require a declared
  intent code and an equality-enforced inventory of every code the
  mutation fires; the reviewer's rebinding attack is refused in all three

## The weakness

`work-identity-successor-cohort`, `work-intent-identity-candidate`, and
`canonical-profile-candidate` enforced their declared error codes as a
subset of the observed set. Independent review showed the consequence:
for 35 of 37 cohort cases the declaration could be rebound to an
incidental co-firing code — with the intended code deleted from the
declaration entirely — and the suite stayed green. The census gate
certified those declarations as bindings, so ADR 0062's claim that
these harnesses "already enforce them exactly" was false.

## The correction

Each adversarial case now carries two fields. `intent_errors` preserves
exactly what was authored before — the code the case exists to prove —
and must fire. The inventory field (`expected_errors`, or
`required_errors` for the profile suite) now holds the complete observed
set and is enforced by equality.

Equality is what defeats the attack: the intended code cannot be dropped
from the declaration while it still fires, because the declaration must
equal the observed set. If the guard behind the intended code is
weakened, the observed set shrinks and the equality fails. If a case is
rebound to an incidental code, the intended code remains observed and
undeclared, and the equality fails. Both directions were exercised as
attack controls against all three committed suites before retention.

Making the inventory exact also makes each mutation's blast radius
visible and pinned: a new co-firing guard now forces a deliberate case
update rather than passing unnoticed under a subset check.

## Boundary

Exactness is a mechanical property; naming which of the observed codes
is intent-central remains authoring discipline, now recorded per case
in `intent_errors` rather than left implicit. The census gate certifies
presence of both fields, not the correctness of the intent label. The
remaining unattributed corpora (architecture-schema's 457 negatives,
the canonicalization vectors) are unchanged and still counted in every
census run. Nothing here is an accountable review determination, an
admitted member, or Gate A acceptance.
