# ADR 0014: Resolve the first-slice atomic admission boundary

- Status: Proposed
- Date: 2026-07-16
- Gate: G2/G3/G5/G6/G7; resolves C1-C8 choices but not immutable records, proof, activation, review, or implementation authority

## Context

The first proof-mission scope was deliberately left non-freezable because eight
conflicts made its command, event, reducer, authority, execution, resource, and
recovery boundaries internally inconsistent. The checkpoint at
`63212488b919b7d8fedce83bc3be344064d7cfe6` retained those conflicts as C1-C8
instead of hiding them behind convenient counts.

The conflicting draft could not safely answer which command owned resource
truth, how correction and invalid-run consequences became atomic, how grants
and reservations terminated, what made local input bytes visible, which reducer
owned verification axes, or what constitutional state existed before the first
mission command.

## Decision

Adopt one bounded, architecture-only resolution candidate with these laws:

1. `ResourceLedger` accepts only reservation lifecycle, typed usage
   observation, and settlement facts. `resource.observed` is not admitted as
   resource truth. The final exact observation and settlement may share one
   atomic command batch.
2. `claim.supersede` is the sole first-slice producer of both claim
   supersession and the transitive dependency-invalidation source fence.
   Dependency edges remain exact references in immutable claim versions; a
   derived reverse index is not authority.
3. `run.determine_validity` is the sole first-slice producer of the atomic run
   validity plus measurement-disposition pair. An invalid run can only pair
   with `no_valid_measurement`.
4. Constitutional bootstrap uses no operational grant. Authority maintenance
   is assignment-only. Ordinary consequential actions consume distinct,
   action-instance-bound, single-use grants in a fixed role-slot order and
   exhaust every consumed grant in the same commit.
5. Local proof execution uses a specialized verification path. Assignment
   binds an active lease, exact local materialization intent, sandbox
   capability, current data-use decisions, and one combined non-fungible
   reservation. `attempt.start` atomically claims the reservation and emits
   both attempt and verification start facts before any byte is mounted or
   process is spawned. `attempt.report` records execution observations;
   verification completion remains a separate scientific determination.
6. Start, invalidation, and controlled expiry are one serializable race.
   Release or expiry is pre-claim only; a claimed ceiling survives crash,
   timeout, revocation, invalidation, and recovery until exact observation and
   settlement.
7. `Verification` is the sole canonical reducer for verification lifecycle,
   reproducibility, replication, transport, dispute, and independence axes.
   The named axes are internal pure fold components, not additional aggregate
   reducers.
8. The separately admitted `RegistryActivation` carries the nonrecursive
   `P0.constitutional-recovery-admission`: non-self-issued root authority,
   exact EngineContractRoot and C0 bundle, externally witnessed checkpoint,
   and a clear current recovery/fork/quarantine frontier. Every first-slice
   command and admission evidence bundle binds that exact activation. A fork,
   quarantine, recovery ambiguity, epoch change, or superseding root
   invalidates it fail-closed.

The resulting representational candidate contains exactly 43 commands, 60
event discriminators, 25 aggregate/state/reducer families, 11 owner modules,
and one external constitutional prerequisite. These are exact candidate-scope
counts, not admitted registry member counts and not implementation evidence.

## Consequences

- `dependency.record_invalidation`, `measurement.determine_disposition`, and
  `verification.start` remain design vocabulary but are outside this slice.
  `attempt.start` and `attempt.report` enter it.
- The local branch does not import the general work graph, stage scheduler,
  data-exposure, provider, or external-effect lifecycle.
- `work_item` and `attempt` enter the first-slice aggregate dependency set.
- `work.lease_expired` enters the event vocabulary. The generic
  `resource.observed` branch leaves canonical resource truth.
- The command-contract schema must represent branch-specific authority paths,
  ordered grant slots, and repeated grant-use/exhaustion occurrences.
- Existing generic work, attempt, verification, correction, validity, and
  resource event payloads require prospective exact member versions before an
  immutable first-slice registry can be constructed.
- Existing single-grant, single-reservation, and boolean-access models remain
  useful component evidence. The added bounded composite authority/resource
  model checks the fixed five-role assignment/start race, but does not prove
  database isolation, exact member conformance, variable profiles, or replay.

## Alternatives rejected

- Sequential correction or invalid-run commands: they expose an unsafe
  intermediate interpretation and make replay cohort completeness ambiguous.
- A second dependency-edge event: it duplicates dependency truth across
  reducers; immutable claim-version references are the canonical edge source.
- General scheduler import: it enlarges the first proof slice without being
  needed for one bounded local verification profile.
- Data-exposure intent for local execution: that contract is provider/effect
  shaped and would falsely describe a network-free local materialization.
- Multiple canonical reducers for one verification aggregate: reducer order and
  semantic ownership would become ambiguous.
- Ordinary commands that create their own checkpoint, root, activation, or
  recovery authority: that is constitutionally recursive.

## Acceptance boundary

This decision resolves the architecture choices only. Gate A remains blocked
until the exact payload, state-subject, reducer, event, command, root,
checkpoint, activation, trace, formal-model, independent-runner, and review
records exist and pass the pre-implementation gate. It authorizes no runtime,
deployment, external effect, publication, or product implementation.
