# Security Policy

Odeya is an architecture-only repository: it contains contracts, validators,
fixtures, and decision records, and deliberately no executable engine,
deployment, credentials, or network surface. Its security posture is
therefore about the integrity of the evidence chain, not a running service.

## Reporting

Report suspected integrity defects — a gate that cannot fire, a validator
that can be satisfied by wrong bytes, a trap whose known-bad payload has
silently become valid, a ledger row whose predecessor does not verify —
by opening a GitHub issue describing the exact bytes and the check that
should have refused them. If the finding would let someone make the
repository lie about itself, mark the issue title with `[integrity]`.

There is no bug bounty. The most valued report is a reproducible
demonstration that a green check coexists with a broken invariant; that
class of finding has historically produced this repository's strongest
corrections (see ADRs 0024, 0030, and 0033).

## Boundary

A green validator run is evidence about this repository snapshot only. It is
never scientific truth, runtime safety, or authorization for external
effects. Gate A acceptance, runtime authority, and release authority are
retained exclusively by the repository owner.
