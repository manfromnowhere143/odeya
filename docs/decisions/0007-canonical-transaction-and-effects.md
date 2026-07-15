# 0007: Canonical transaction authority and recoverable cross-plane effects

- Status: Proposed
- Date: 2026-07-15
- Gate: G6/G7; requires operator acceptance before implementation authorization

## Context

Odeya must coordinate PostgreSQL, immutable object storage, a durable scheduler, isolated workers, projections, and external systems. None of the last five can participate honestly in one database transaction. A naive dual write can produce an object without metadata, an event without a notification, a provider effect without a receipt, or workflow history that disagrees with scientific state.

The architecture already requires an append-only scientific kernel, content-addressed artifacts, a transactional outbox, at-least-once delivery, and explicit reconciliation. It needs one decision that defines which system owns meaning and what every cross-plane success actually proves.

## Decision

Adopt the transaction and recovery semantics in `docs/TRANSACTION_MODEL.md`:

1. A committed Odeya domain-event batch in PostgreSQL is the linearization point for scientific, authority, and publication state.
2. The same database transaction records the command result, aggregate-head advance, required authority/resource changes, invariant-bearing records, and causally required outbox entries.
3. Artifact bytes are staged, stream-validated, and conditionally materialized at an immutable digest key before a command canonically registers promotion. Materialized-but-unregistered bytes are inert orphans.
4. A Temporal-class substrate is a replaceable operational scheduler. Its history is not the scientific ledger, and every callback re-enters through a validated command.
5. External effects use an authorize/intent transaction, an out-of-transaction dispatch, a retained observation transaction, and explicit reconciliation. Timeout never establishes non-application, and no cross-system exactly-once claim is made.
6. Projections and indexes are rebuildable views at disclosed ledger positions and carry no transition authority.

The specific PostgreSQL, object-store, scheduler, and adapter products remain provisional until their accepted probes and conformance evidence pass. This decision freezes semantics, not a vendor.

## Consequences

- The modular monolith can enforce the hardest invariants in one local transaction while workers remain isolated.
- Every external boundary is at least once plus idempotency/reconciliation, not magical exactly once.
- Some artifact promotions may leave temporary storage orphans; retention and reconciliation are mandatory.
- Some effects remain visibly `completion_unknown` and block progress rather than being guessed into success or failure.
- Scheduler replacement cannot change mission, evidence, claim, or release meaning.
- Cross-aggregate transaction cohorts must be explicit and rare; all other coordination is an event-driven saga with append-only compensation.
- Infrastructure code must prove crash behavior before the architecture treats the selected products as conformant.

## Rejected alternatives

- **Distributed two-phase commit across PostgreSQL, object storage, scheduler, and providers:** unavailable across important boundaries, operationally brittle, and incapable of proving physical or publication outcomes.
- **Temporal/workflow history as the domain ledger:** couples scientific meaning to a replaceable scheduler and lets callbacks or replay semantics become authority.
- **Object-store events as artifact promotion:** object creation proves bytes exist, not provenance, rights, validation, or scientific eligibility.
- **Direct worker or adapter writes:** bypasses authority, one-writer, idempotency, and claim-boundary enforcement.
- **Best-effort database plus message dual writes:** permits committed facts with lost delivery and delivered messages for rolled-back facts.
- **Treating timeout as failure and retrying:** can duplicate publication, spend, messages, repository writes, or physical effects.

## Falsifiers and acceptance evidence

Keep this ADR `Proposed` if any of the following remains true:

- an accepted command can commit without its required outbox or authority consumption;
- a worker, scheduler, adapter, projection, or UI can advance domain state directly;
- object-store success can make an artifact claim-eligible before ledger registration;
- scheduler loss changes a prior scientific verdict;
- an ambiguous external write can be automatically retried without an accepted idempotency and reconciliation contract;
- same-ID/different-payload command reuse can execute; or
- crash traces cannot deterministically identify retained state and the next legal action.

Acceptance requires the Gate A artifacts named in `TRANSACTION_MODEL.md`, independent architecture review, and explicit operator approval. Product conformance additionally requires an authorized Gate B crash-recovery probe; accepting this ADR alone does not authorize runtime implementation.
