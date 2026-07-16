# Prerequisite lifecycle closure checker

This directory retains finite, architecture-only evidence for the lifecycle
prerequisites closed by ADR 0017. It checks the candidate contracts directly
against positive and adversarial traces for:

- `AuthorityGrant`: issue is `not_issued -> issued`, activation is
  `issued -> active`, use is legal only while active, a single final use is
  immediately exhausted, and expiry/revocation are legal only from issued or
  active;
- `protocol.frozen`: the first canonical protocol is materialized from
  aggregate absence as version 1 with an exact frozen `ProtocolSnapshot`,
  draft/validation/exposure/integrity evidence, and one atomic ordered
  protocol-grant cohort;
- `data_use.decided`: authority is the `data_rights` bounded grant and the
  grant-use, decision, and final-use exhaustion are one ordered commit; and
- `WorkLease`: the canonical first-slice vocabulary is exactly `unleased`,
  `active`, `released`, `revoked`, and `expired`. `stale` and `completed` may
  describe projections but are not canonical lease states.

The checker also binds the exact 60 first-slice event identities to their
ResearchEvent 0.7.0 branches and logical payload type identities, preserves the
25 aggregate/reducer-family count, and explicitly verifies the four event-v1
branches whose logical payload type identity is v2. It verifies the enclosing
schema resource by exact raw digest and byte count while keeping every
per-payload contract unresolved and null.

The state-machine traces do not resolve a WorkLease record resource. The
identity map records
`urn:odeya:schema:canonical-work-lease:0.1.0` as missing and blocking because
ResearchEvent references it but no such schema resource exists. Creating that
resource requires a separate reviewed schema/test/ownership tranche.

Run from the repository root:

```bash
python3 tests/lifecycle-closure/check.py
```

Passing is bounded consistency evidence only. It does not create immutable
payload contracts, a canonical WorkLease resource, or EventContractRecords,
prove payload digest resolution,
activate registries, authorize a runtime, or complete Gate A.
