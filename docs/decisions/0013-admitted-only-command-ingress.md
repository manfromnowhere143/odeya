# 0013: Admit only registry-complete commands at ingress

- Status: Proposed
- Date: 2026-07-15
- Gate: G2/G3/G6/G7; requires exact registry, envelope, receipt, refusal, replay, and independent conformance evidence

## Context

The current command-envelope candidate enumerates 121 command names, while only thirteen separate closed payload-schema candidates exist and no immutable machine command registry is enrolled at an accepted digest. The envelope and receipt also require an exact command-schema identity/digest and an exact registry member reference. A command name with no schema or member record therefore cannot honestly construct either object.

Treating an unimplemented name as a reserved command inside the executable envelope would force one of two unsafe outcomes: fabricate schema/member identity, or weaken required references into nullable fields. Checking only that no handler is installed is not a safety boundary; a future routing mistake, partial deployment, or stale adapter could turn a vocabulary placeholder into an executable path.

The ingress boundary must also preserve exact retries after a command version is retired, reject changed bytes under an already settled command ID, and apply parser limits before trusting any discriminator. These requirements need one explicit order rather than an ambiguous “lookup during validation.”

## Proposed decision

`CommandEnvelope` enumerates only commands contract-admitted by the exact command-registry/root snapshot. Every enumerated command type/version has complete payload-schema bytes, one immutable command contract record, legal event/cohort alternatives, reducer/state/rule bindings, limits, fixtures, review evidence, and a declared decider/handler port contract. Unknown and reserved design names are not envelope discriminators and are not admitted command-registry members.

`contract-admitted` is an architecture status, not proof that runtime code exists or permission to run it. A later runtime activation may enable only a contract-admitted set for which exact handler conformance and deployment evidence exist. At that activation, the enabled registry, generated envelope, and handler map must be identical. Gate A can freeze contract semantics and prospective activation prerequisites; it does not create handlers or authorize ingress.

Ingress is ordered as follows:

1. **Bound the frame.** Apply transport byte, nesting, token/key, decompression, and rate limits before discriminator or payload processing. No lookup authorizes unbounded parsing.
2. **Extract a minimal selector.** Read only tenant, idempotency namespace, command ID, command type, and command semantic version under a small closed selector grammar. The selector is routing input, not a command, authority proof, receipt, or canonical fact. The server selects the active registry/root snapshot; a caller cannot choose `latest` or activate a snapshot.
3. **Resolve historical settlement first.** Lookup `tenant + namespace + command_id`. If a receipt already exists, resolve its retained historical envelope, record, schema, and registry snapshot. Recompute the request under that historical contract. Exact bytes/digest return the same receipt; changed binding returns a non-canonical idempotency-conflict response referencing the immutable prior receipt. No second `CommandReceipt` is created.
4. **Resolve new admission.** If no receipt exists, lookup command type/version in the server-selected active admitted index. No member, reserved name, inactive/superseded member, unavailable active root, or invalid membership proof stops before `CommandEnvelope` construction, payload validation, handler lookup, authority evaluation, or domain transaction.
5. **Refuse without fabrication.** Pre-envelope refusal returns the stable ingress code `command_contract_not_admitted` where disclosure policy permits. It may create bounded security/operational telemetry or a future typed `IngressRefusalObservation`, but never a `CommandReceipt`, domain event, grant use, reservation, resource commitment, outbox record, or synthetic command-contract reference.
6. **Validate the admitted command.** An admitted hit loads the exact active envelope, payload schema, command record, and activation/root evidence. The full envelope must bind those identities exactly; then payload, references, current state, policy, authority, rights, resource, semantic, and event-cohort rules run in the constitutional admission order.

A structurally valid, admitted envelope may receive a bound rejected receipt for payload-schema failure, unavailable payload-schema bytes named by an otherwise valid member, stale state, failed authority/policy/rights/resource rules, or illegal transition. Structurally unbindable input, unknown/reserved command names, invalid registry membership, and changed reuse of an existing command ID cannot receive a new `CommandReceipt` because no honest new member/request settlement exists.

## Reserved design vocabulary

Unimplemented command names may remain in a separate non-executable `command-design-vocabulary` artifact for planning and review. A reserved entry:

- is absent from the active envelope discriminator set and command registry;
- has no payload-schema reference, handler, authority/grant modes, legal transition, event alternative, or activation proof;
- cannot be addressed by a command receipt or interpreted as a compatibility promise; and
- can be promoted only prospectively by adding complete contract evidence, generating a new admitted-only envelope, and activating a newly sealed registry/root snapshot.

Retired admitted records and schema bytes remain readable for historical replay. Retirement blocks new admission; it does not erase old meaning or prevent exact receipt replay.

## Registry and generation boundary

The immutable command-contract records are the source set for the admitted command surface. Generated envelope branches and documentation must reproduce byte-for-byte from that set. Record subjects refer to stable schema/event/reducer/rule identities but never embed their parent registry snapshot or activation digest. Membership proofs and activation wrappers bind records to a snapshot externally. One acyclic engine-contract root binds the compatible command registry, generated envelope, event/reducer/state/rule/module registries, schemas, canonicalization profile, and activation evidence.

At any runtime activation, the enabled envelope discriminator set, enabled registry member set, and conforming handler map must be exactly equal. Missing, duplicate, extra, nullable, reserved, or stale members fail activation.

## Gate A and A-002 scope

A-002 may close for one explicitly named, dependency-closed Gate A command set without pretending that all 121 design names are executable or frozen. The closure set is derived from the accepted first-slice mission and every constitutional, authority, data, recovery, effect, correction, and publication dependency it can reach. The thirteen current payload candidates do not by themselves define that set.

For the scoped set, every envelope discriminator must resolve offline to exact bytes and machine semantics, every event alternative must resolve to one canonical reducer/state transition, semantic/race/replay vectors must pass, and independent review must close critical/high findings. Commands outside that sealed set remain reserved design vocabulary. Expanding the admitted set is a new prospective registry/root activation, not a patch to the accepted snapshot.

The current 121-discriminator envelope is therefore an architecture/red-team candidate, not an acceptable production ingress contract and not A-002 closure evidence.

## Rejected alternatives

### Reserved record variant with null schema or handler

Rejected because it contradicts the exact schema/member references required by the envelope and receipt, creates two meanings for “registry member,” and makes accidental execution depend on negative handler state.

### Admit all 121 names before their contracts exist

Rejected because syntactic enumeration is not semantic admission. It would freeze invented payload, transition, authority, and compatibility promises or leave them implementation-defined.

### Parse the full generic payload before registry resolution

Rejected because it spends unbounded parser/validation work on unauthenticated design vocabulary and increases denial-of-service and parser-differential exposure. Only generic frame limits and the bounded selector precede lookup.

### Reject retired exact retries against the current registry

Rejected because it breaks immutable idempotency. Historical receipt lookup and historical readers precede active-new-command resolution.

### Create a rejected receipt for unknown commands or changed ID reuse

Rejected because the required exact member/request binding does not exist for an unknown command, and a changed reuse cannot replace or coexist with the immutable prior receipt for the same idempotency key.

## Falsifiers and acceptance evidence

Keep this decision proposed if any of the following remains true:

- an envelope discriminator lacks an exact active record, payload schema, reducer/event closure, rule set, handler identity, or fixture set;
- a reserved/unknown name reaches payload validation, handler resolution, authority evaluation, or a canonical transaction;
- an ingress refusal fabricates a member, schema digest, receipt, event, grant/resource consequence, or outbox row;
- caller-supplied registry selection can bypass server activation/currentness;
- exact replay of a retired command fails, changes its receipt, or resolves through current rather than historical semantics;
- changed bytes under a settled command ID create a second receipt or execute;
- runtime activation permits enabled envelope, registry, and conforming handler sets to differ;
- registry/envelope/root identities form a content-digest cycle; or
- the claimed A-002 closure set is not exact and dependency-closed.

Acceptance requires the bounded selector/refusal contracts, admitted-only generated envelope, exact command registry and activation/root schemas, historical replay and changed-reuse vectors, unknown/reserved/fake-member adversarial fixtures, two independent registry/digest validators, command-event-reducer graph validation, race/recovery traces, independent security/distributed-systems review, and Daniel's signature on the exact Gate A candidate. It does not authorize runtime implementation.
