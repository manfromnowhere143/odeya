# Reducer Registry

Status: proposed Gate A contract, 2026-07-15. Event schemas describe retained facts; this registry defines the only legal fold from those facts to canonical aggregate state. No runtime reducer implementation is authorized, and the machine registry is not yet complete.

## Reducer law

For aggregate type `A`, reducer version `r`, and exact ordered events `e_1...e_n`:

\[
s_n = \operatorname{fold}_r(s_0,e_{1:n}).
\]

The fold is pure, deterministic, total over its declared readable event versions, and fail-closed outside them. It returns either exact next state plus invariant results or an explicit reduction failure. It never skips an event to keep a projection running.

Canonical state at a position is derived from original retained event bytes or a reviewed semantics-preserving upcast view. An upcast never rewrites the original event, digest, position, or historical meaning.

## `ReducerContractRecord`

Every aggregate/reducer version has one immutable record:

```text
reducer ID and semantic version
owning module and aggregate type
initial-state schema/version/digest
state schema/version/digest
readable event type/version/schema/digest set
required event ordering and batch-cohort constraints
pure reducer implementation identity or architecture pseudocode digest
precondition, transition, and postcondition rule IDs
orthogonal axes owned and forbidden axes
unknown/indeterminate/missing default policy
correction, supersession, invalidation, and tombstone behavior
snapshot/checkpoint compatibility and verification
upcast registry and old-reader policy
positive, negative, boundary, metamorphic, race, and replay vectors
independent implementation/result evidence
resource/complexity ceilings
owner, review, effective, expiry, and supersession evidence
```

The ordered registry snapshot has one canonical digest. Command admission and architecture traces bind the exact reducer contract where a transition depends on current fold state. `latest` is forbidden.

## Separation from command and projection

Three functions remain distinct:

```text
decide(command, current states, controlled inputs)
  -> reject | noop | ordered event-batch proposal

reduce(current aggregate state, one committed event)
  -> next aggregate state | reduction failure

project(canonical event/checkpoint set, audience/profile)
  -> rebuildable projection snapshot | projection failure
```

The command decider cannot mutate state directly. The canonical reducer cannot call policy, storage, network, model, clock, randomness, or another aggregate reducer. The audience projection cannot reinterpret or authorize canonical facts.

A command/event pair does not prove reducer correctness. Every emitted event must name exactly one canonical aggregate owner, and that owner's registry must declare it readable. Events may additionally feed rebuildable projections, but no second canonical aggregate reduces the same event.

## State-schema rules

Canonical aggregate state schemas:

- separate orthogonal axes instead of one omnibus status;
- distinguish unknown, absent, unmeasured, unavailable, withheld, and not applicable;
- retain version/current/superseded pointers without deleting history;
- contain only values derivable from the event prefix and frozen registries;
- carry last event position/version/digest and reducer identity;
- never store a model-generated narrative as a derived fact;
- never infer scientific, authority, rights, recovery, or publication state from another axis;
- reject unknown safety-relevant enum values; and
- use bounded structures with explicit overflow/compaction semantics.

Snapshots are performance artifacts. A snapshot is admitted only when its reducer/event/checkpoint identities match and replay from an independently verified prior checkpoint yields the same state digest. A bad/missing snapshot cannot change history; the system replays or quarantines.

## Transaction cohorts

Reducers process one event at a time, but semantic validation also checks complete command cohorts. A reducer cannot assume that another aggregate's companion event exists merely because its local event is valid.

The command transaction proves the closed event-batch alternative, and a batch validator proves relations such as:

- grant reservation/use/release and effect transition;
- resource creation/claim/pre-claim release-or-expiry/observation/settlement and the exact attempt/effect/verification cohort;
- validity plus measurement disposition where inseparable;
- correction plus dependency invalidation/outbox;
- deletion/revocation plus access/projection fence;
- recovery decision plus quarantine/service-scope state; and
- publication start/settlement plus exact effect/observation evidence.

On replay, a missing or incompatible cohort is an integrity incident. Reducers do not synthesize the missing fact.

## Orthogonal reducer families

At minimum the founding registry must make these non-collapse properties explicit:

| Aggregate family | Must remain separate |
|---|---|
| Protocol | freeze, exposure, integrity, amendment/fork/supersession |
| Attempt | execution terminality versus artifact, validity, measurement, stage state |
| Measurement/run | run validity, measurement disposition, metric result, falsifier result |
| Verification | assignment, execution, replay, independence, dispute, invalidation, replication/transport |
| Claim | proposal/disposition, immutable version eligibility, correction/supersession/retraction |
| Authority | assignment, grant lifecycle, reservation, consumption, exhaustion, expiry, revocation |
| Resource budget | one child per reservation ID; active versus claimed hold; estimate, ceiling, attempted, actual, billed, refunded, consumed, overage, unused, and missingness axes; execution/currency/verification dimensions |
| Data | asset lifecycle, rights assertion, executable decision, exposure, retention, hold, deletion |
| Effect/publication | intent, dispatch claim, observation, ambiguity, reconciliation, exact-visible release |
| Recovery | checkpoint, witness/consistency, backup write/verification/recoverability, restore, policy frontier, quarantine/epoch |
| Learning | grounded outcome, candidate, shadow/canary evidence, promotion/rollback |

The ResourceLedger reducer accepts the six closed resource events and no caller mutation. Per child, legal paths are `none -> active -> claimed -> settled` and `active -> released|expired`. Claim preserves the full ceiling and leaves actual use unobserved; crash/recovery is no transition. Settlement requires exact observations and enforces componentwise `net=reserved_consumed+overage` and `ceiling=reserved_consumed+unused`. The reducer rejects duplicate dimension keys, cross-resource conversion, dimension compensation, release/expiry after claim, settlement from active, and unknown-to-zero coercion.

No reducer may derive `null_result` from an invalid or unmeasured run, restore an expired/revoked grant, release a claimed resource ceiling because a process died, reopen a service scope from a restore report, call an unwitnessed checkpoint canonical, or call a released publication current after correction/withdrawal.

## Compatibility

Changes are classified:

- **representation-compatible:** same meaning; tested reader addition or canonical-preserving upcast;
- **semantic-compatible extension:** new optional fact ignored only when explicitly safe and outside owned axes;
- **semantic break:** changes transition, default, authority, scientific consequence, correction, rights, recovery, or release meaning;
- **unsupported:** old reader cannot preserve safety and must stop.

A semantic break creates a new event/reducer version and prospective migration decision. Unknown major versions and unknown values on scientific/authority/rights/recovery/publication axes fail reduction. “Ignore unknown events” is forbidden for canonical folds.

Historical reducers remain available or reproducibly reconstructible for retained events. Migration creates new snapshots/projections and explicit transformation evidence; it never rehashes old events as if originally written under the new semantics.

## Independent replay

Gate A requires two independently implemented, language/runtime-separated trace runners for the constitutional first-slice reducers. Each consumes the same original event bytes, registry, controlled inputs, and expected checkpoint and emits:

```text
runner/build/environment identity
registry and input-set digest
per-event accept/reject and state digest
final aggregate states and heads
invariant results
unsupported/indeterminate findings
resource use
```

Agreement is necessary, not sufficient. Shared generated code, shared reducer library, copied logic, or one runner wrapping the other does not count as independent. Disagreement blocks the affected candidate and retains both outputs.

## Adversarial traces

Every reducer family includes:

- event delivered to the wrong aggregate;
- gap, duplicate, reorder, broken previous digest, bad batch index, or wrong aggregate version;
- legal event type with payload from another type;
- old reader encountering new major version or safety enum;
- no-op or duplicate delivery changing state;
- context/clock/randomness changing replay;
- invalid run followed by null outcome;
- interval-crossing-zero followed by equivalence/support;
- correction without dependency invalidation;
- grant use after revoke/expiry or released reservation consumed;
- resource claim with an incomplete start cohort, release/expiry after claim, crash-driven release, settlement without exact observations, unavailable usage treated as zero, cross-currency/resource conversion, or one verification dimension compensating another;
- exposure/deletion/hold/rights states widening permission;
- restored snapshot resurrecting data/grant/claim/publication state;
- fork selected by wall clock rather than witnessed consistency evidence;
- release from timeout/provider receipt without exact visibility; and
- state digest equality despite a one-byte meaningful event mutation.

Each negative trace must fail at the intended layer. A schema rejection cannot be credited as evidence that a transition invariant works.

## Machine closure

The architecture validator must eventually prove:

- every aggregate type maps to exactly one active reducer contract;
- every event type/version maps to exactly one canonical reducer owner;
- every command event-batch alternative contains only events declared by its target reducers;
- every state/event/schema/rule identity and digest resolves offline;
- aggregate/reducer/module ownership agrees with the dependency manifest;
- all declared trace IDs exist and expected outcomes reproduce;
- reducer registries and generated documentation reproduce byte-for-byte; and
- no projection reducer is registered as canonical or vice versa.

## Acceptance boundary

The current event schemas and trace fixtures do not close this registry. Gate A requires the exact machine records, state schemas, independent trace runners, compatibility vectors, cohort validation, and independent distributed-systems/scientific review. Product database code, actual transaction isolation, and operational replay remain later conformance evidence.
