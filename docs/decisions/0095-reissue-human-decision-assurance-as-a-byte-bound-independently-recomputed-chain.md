# ADR 0095: Reissue human-decision assurance as a byte-bound, independently recomputed chain

- Status: Accepted as direction and architecture design; the byte-bound and
  recomputation tranche is retained candidate evidence, but adoption remains
  incomplete until context-isolated technical review of the exact candidate
  bytes; every successor remains unissued, and Gate A remains blocked
- Date: 2026-07-21
- Decision owners: constitutional authority, security, architecture review,
  evidence integrity
- Gate effect: requires new immutable successor identities and retained
  architecture evidence before the PRQ-013 T0 foundation can be reconsidered;
  grants no human authority, consumer admission, runtime, cloud, Gate B,
  publication, or external-effect authority

## Context

The published `HumanDecisionAssuranceEvidence` 0.1 and
`HumanDecisionAssuranceSeal` 0.1 resource identities are immutable. Published
does not mean issued or admitted: both remain unissued architecture
candidates. It does mean their bytes and semantics cannot be repaired in
place, even when the repair would make them stricter.

Adversarial audit of the retained 0.1 candidate found defects that its current
positive and known-bad controls do not bound:

- an earlier `contradicted` value can be overwritten by `unknown` in four
  evaluator branches: challenge/replay, decision confirmation,
  authentication, and verifier relation;
- absent assertion-acceptance and consumption atomic-action identifiers can
  compare as equal because `None == None`, allowing absence to masquerade as
  atomicity;
- verifier status is carried in a private evaluator-only domain and excluded
  from the declared ruleset's required-domain inventory;
- any sanitation state other than all-supported collapses to `unknown`, so a
  positive sanitation contradiction loses its invalidating meaning;
- a recomputed negative Seal can retain positive-path reason codes left by a
  prior fixture;
- the exact binary confirmation-receipt frame introduced by ADR 0093 is not a
  required Evidence role;
- recorded backing-artifact digests and byte counts can remain placeholders
  with no retained, dereferenceable preimage; and
- one implementation currently assembles and checks both sides of the
  eligibility comparison, so agreement is not independent recomputation.

These are architecture defects, not evidence that a real ceremony failed.
They also do not authorize a live experiment to investigate them. A green
structural validator cannot make missing preimages exist, make two evaluators
independent, or repair an immutable published identity.

## Considered options

### Amend the 0.1 resources in place

Rejected. Changing requirements, evidence roles, precedence, or receipt
bindings under a published resource identity would make the same identifier
resolve to different contracts and would invalidate exact-byte replay.

### Add more checks around the 0.1 Seal

Rejected. A sidecar checker cannot make the 0.1 Evidence contain an omitted
receipt-frame role, cannot provide preimages for placeholder digests, and
cannot make the 0.1 Seal bind the evidence by which backing bytes and
independent agreement were verified.

### Reissue an acyclic successor chain

Accepted as the design direction. New identities make the changed contract
explicit, retain the 0.1 records as historical evidence, and put every
verification receipt upstream of the Seal that cites it.

## Decision

Construct, but do not yet issue, a successor chain with these separately
identified artifacts:

- `HumanDecisionAssuranceEvidence` 0.2;
- `HumanDecisionAssuranceBackingByteVerificationReceipt` 0.1;
- individual-eligibility ruleset 0.2;
- `HumanDecisionAssuranceEligibilityRecomputationResult` 0.1, instantiated
  independently for Python 3.14.2, Node.js 24.18.0, and Temurin Java 21.0.9;
- `HumanDecisionAssuranceEligibilityComparisonReceipt` 0.1; and
- `HumanDecisionAssuranceSeal` 0.2.

The exact schema resource IDs, raw bytes, digests, byte counts, interpreter
locks, and tool identities are adoption evidence. They do not exist merely
because this ADR names their artifact classes.

### Acyclic dependency order

The successor graph is strictly downstream:

```text
Core + source decision + v2 challenge/receipt profile + exact backing blobs
  -> Evidence 0.2

Evidence 0.2 + exact backing blobs + resolver profile
  -> BackingByteVerificationReceipt

Evidence 0.2 + BackingByteVerificationReceipt + ruleset 0.2
  -> Python 3.14.2 recomputation result
  -> Node.js 24.18.0 recomputation result
  -> Temurin Java 21.0.9 recomputation result

three recomputation results + their exact common inputs
  -> EligibilityComparisonReceipt

Core + Evidence 0.2 + ruleset 0.2
     + BackingByteVerificationReceipt
     + EligibilityComparisonReceipt
  -> Seal 0.2
```

The backing-byte receipt and comparison receipt must not bind, name, predict,
or reserve a Seal ID or Seal digest. No recomputation result may bind a Seal.
The Seal binds the exact raw bytes of both receipts. This one-way relation is
the acyclicity invariant; no post-hoc receipt can be inserted into a Seal it
was computed from.

### Evidence 0.2 and actual backing bytes

Evidence 0.2 replaces digest-only assertions with an exact, closed role
inventory whose every entry has:

- one unique role and artifact identifier;
- a lowercase `sha256:<64-hex>` content address equal to its raw SHA-256;
- a positive raw byte count and exact media type;
- an explicit byte-fidelity class; and
- a resolver-independent link to the exact retained preimage.

For repository architecture evidence, each preimage is materialized in the
candidate bundle under a path derived only from its content address:

```text
architecture/evidence-blobs/sha256/<first-two-hex>/<remaining-62-hex>
```

The path is a repository-bundle transport, not canonical object identity. The
digest is always recomputed from the file bytes; neither the filename nor the
descriptor is trusted as proof of content.

The closed role inventory must include the exact binary
`ODEYA-HDA-CONFIRMATION-RECEIPT-V1` frame bytes used by the v2 two-phase
challenge profile as
`exact_unmodified_confirmation_receipt_frame`. Those are the bytes whose
digest enters the phase-two authentication frame. A JSON rendering, parsed
object, or later re-encoding cannot substitute for that binary preimage.
Existing exact cryptographic inputs likewise remain exact bytes; sanitation
metadata never authorizes their transformation.

A synthetic preimage is permitted only when it is retained as actual bytes and
unambiguously labelled synthetic. A digest with no retained preimage is not an
artifact. If policy forbids retaining required bytes, the chain cannot become
eligible; the system must not retain a placeholder digest and imply that the
bytes were verified.

### Backing-byte verification receipt

The `BackingByteVerificationReceipt` is a content-addressed architecture
record produced before eligibility evaluation. It binds:

- the exact Evidence 0.2 schema resource and Evidence raw digest and byte
  count;
- the exact resolver profile and closed expected role inventory;
- for every role, the expected content address, byte count, media type, and
  byte-fidelity class;
- the observed raw digest and byte count recomputed from the dereferenced
  preimage;
- a typed read disposition and a typed comparison disposition; and
- the recomputed receipt-frame digest and its exact relation to the v2
  presentation and authentication frames.

The receipt is total over the inventory: it records one row for every expected
role, including a row that could not be read. It cannot omit a failed row. Its
own identity is computed from its final exact bytes; the receipt does not
contain its own digest.

The receipt distinguishes these cases without collapsing them:

- **missing or unreadable**: no bytes were available to compare, including a
  missing content address, denied read, truncated transport with no complete
  candidate, or resolver failure. The observation is `unknown`, the
  participant disposition is at most `indeterminate`, and no eligible Seal
  may be assembled;
- **readable mismatch**: bytes were available but their digest, byte count,
  role, media type, fidelity class, framing, or declared relation disagreed
  with the exact descriptor or normative frame. This is `contradicted` and
  the disposition is `invalid`; and
- **readable malformed content**: the retained bytes are readable but cannot
  satisfy the required binary or structured format. This is a mismatch, not
  unavailability, and is therefore `invalid`.

Missing is never represented as zero bytes. Unreadable is never promoted to a
match. Mismatch is never softened to unknown by deleting the observed bytes.

### Eligibility ruleset 0.2

Ruleset 0.2 is the only normative derivation contract for all three
implementations. It declares every required domain, including verifier
independence, in its public ordered inventory. Implementations may not add a
private eligibility-bearing domain or exclude a declared one from final
precedence.

Its fold is monotonic and total:

1. any explicit contradiction, readable mismatch, failed categorical
   condition, forbidden-content finding, or independent-result disagreement
   yields `invalid`;
2. otherwise, any absent, missing, unreadable, `unknown`, or
   `not_applicable` required input yields `indeterminate`; and
3. only all-supported required observations and satisfied categorical
   conditions yield `eligible`.

Once a domain is contradicted, a later unknown value cannot overwrite it.
That rule applies to challenge/replay, decision confirmation, authentication,
verifier relation, sanitation, and every future required domain.

Atomic acceptance and consumption require two present, nonempty, syntactically
valid identifiers, an exact equality relation between them, and backing
evidence for the one controlled atomic action. Both identifiers absent, either
identifier absent, or an unreadable atomic-action record is
`indeterminate`. Two present unequal identifiers or a readable record that
contradicts atomic execution is `invalid`. Equality is evaluated only after
presence and type checks, so null equality can never establish atomicity.

Sanitation is a declared domain with the same precedence law. Any explicit
sanitation contradiction or forbidden-content finding is `invalid`.
Otherwise missing or unknown sanitation evidence is `indeterminate`; only all
required sanitation observations supported is supported.

Reason codes are an exact deterministic output of ruleset evaluation. A
negative determination and every negative Seal section must contain exactly
the sorted, unique recomputed negative reason-code set. Positive-path codes
such as `all_required_observations_supported` are forbidden when the result is
`indeterminate`, `invalid`, or `blocked`. An eligible result cannot carry a
negative code. Fixture residue is never preserved across recomputation.

### Non-sharing recomputation across three language toolchains

Three implementations must independently parse the normative artifacts,
dereference every backing byte, apply ruleset 0.2, and serialize a complete
raw projection:

- one Python 3.14.2 implementation under its hash-locked dependency profile;
- one Node.js 24.18.0 implementation under an exact lockfile and dependency
  profile; and
- one Temurin Java 21.0.9 implementation under a separate exact source,
  configuration, adapter, and dependency profile.

They may share only the published schemas, ruleset, exact input bytes, and
normative input vectors that contain no expected result. They must not share
Odeya evaluator source, generated evaluator code, parsing or normalization
helpers, intermediate state, expected-result fixtures, or output from either
implementation. A separately deterministic evidence assembler wraps, but does
not reinterpret, each raw projection. Each retained result record binds the
exact raw projection bytes, implementation-source digest,
interpreter/toolchain identity, dependency-lock digest, exact input-manifest
digest, backing-byte receipt, domain results, categorical failures, final
disposition, and reason codes. Machine validation proves that every copied
projection field exactly equals the bound raw output; the wrapper is never
described as direct evaluator output.

The Java implementation is a third language/toolchain oracle for correlated
implementation defects, not an external policy or scientific authority. Its
source identity, exact Temurin version, configuration bytes, input-adapter
bytes, dependency profile, input bytes, output bytes, and exit disposition
must be retained. It executes offline for architecture evidence; it is not a
network service, cloud experiment, model vote, or organizationally independent
review.

The `EligibilityComparisonReceipt` binds all three exact result bytes and
their common Evidence, backing-byte receipt, and ruleset inputs. It compares
every declared domain, every categorical failure, the final disposition, and
the exact reason-code set. One missing or unreadable result is
`indeterminate`. Any field disagreement among readable results is
`invalid`. Exact agreement is necessary but not sufficient for admission: the
agreed result itself must be eligible and all other Gate requirements remain.

### Seal 0.2

Seal 0.2 binds, by schema resource ID, raw SHA-256, and byte count:

- the exact Core and Evidence 0.2;
- ruleset 0.2;
- the `BackingByteVerificationReceipt`; and
- the `EligibilityComparisonReceipt`.

It copies the agreed recomputation output without weakening it. A Seal cannot
be eligible unless both receipts are supported, all three retained results
agree exactly, and their agreed disposition is eligible. A missing receipt or
result produces no positive Seal; a mismatching receipt or result produces an
invalid Seal. Seal 0.2 remains a singleton-assurance record, not an approval,
aggregate quorum, authority assignment, or consumer-currentness decision.

## Versioning and adoption

Evidence 0.1, Seal 0.1, their fixtures, and their published resource IDs remain
unaltered and replayable. They are superseded for future PRQ-013 foundation
work but are not rewritten, relabelled as 0.2, or retroactively accepted. Core
0.1 may remain an exact upstream input if its bytes require no change; any Core
contract change requires its own successor identity.

This ADR accepts the successor direction and dependency design only. Adoption
is incomplete until one exact candidate commit retains all of:

1. the new schemas, ruleset, resource identities, and actual content-addressed
   preimages;
2. a safe synthetic chain and the complete one-mutation known-bad corpus;
3. source-separated, non-sharing Python 3.14.2, Node.js 24.18.0, and Temurin
   Java 21.0.9 implementations and their exact environment locks;
4. all three raw projections and their bound result records;
5. backing-byte and comparison receipts that satisfy the acyclic graph;
6. machine validation that recomputes every digest and refusal from repository
   bytes; and
7. a context-isolated technical-review determination over the exact candidate
   bytes, with reviewer provenance retained and with that determination
   explicitly barred from counting as accountable review or Gate A acceptance.

Even that retained tranche remains unissued architecture evidence. Profile or
schema issuance, admission, accountable security and authority review, and
Daniel's exact-byte Gate A decision remain separate unresolved obligations.

### Retained candidate-evidence checkpoint

The candidate prepared for the containing exact commit now retains the first
six evidence classes above:

- five successor schemas and seven schema-valid fixtures;
- fourteen content-addressed synthetic backing preimages, with every digest,
  byte count, descriptor relation, and verification row rederived from the
  retained bytes rather than trusted from a filename or record;
- forty-four expectation-free vectors evaluated by source-separated,
  non-sharing Python 3.14.2, Node.js 24.18.0, and Temurin Java 21.0.9 source
  trees, yielding 132 exact passing recomputations;
- three direct projections and three bound result records whose comparison is
  exact across `participant_id`, `domain_results`, `categorical_results`,
  `categorical_failures`, `final_disposition`, and `reason_codes`;
- forty-eight intent-bound downstream chain known-bads over backing truth,
  results, comparison, acyclicity, receipt and Seal bindings, source/runtime
  identity, and predecessor immutability; and
- machine regeneration and validation from repository bytes, including the
  retained false authority boundaries.

Every fixed time in that synthetic evidence is a deterministic fixture time,
not a ceremony observation, trusted timestamp, or proof of freshness. Exact
Git identity and release evidence for the containing subject must be resolved
from Git and the release contract; this ADR cannot supply them.

The seventh adoption item is still absent: no context-isolated technical-review
determination over the exact candidate bytes is retained. Until that review is
completed with provenance and its non-accountable boundary made explicit, ADR
0095 adoption remains incomplete. The three source paths establish the stated
code-separation and non-sharing controls, not organizational independence;
organizationally independent authorship or review has not been proven.

## Known-bad proof obligations

The successor is not adopted until isolated, intent-bound, one-mutation tests
refuse at least:

- each of the four contradiction-plus-unknown overwrite cases, while a
  missing-only control remains `indeterminate`;
- two absent atomic-action IDs, either one absent, empty or malformed IDs, two
  unequal IDs, a missing atomic-action preimage, and a readable contradictory
  atomic-action record;
- verifier status removed from the ruleset, hidden under an undeclared key,
  contradicted then replaced by unknown, or omitted from the result;
- contradicted sanitation collapsed to unknown, forbidden content with an
  otherwise supported sanitation set, and missing sanitation promoted to
  supported;
- an invalid or indeterminate determination retaining a positive-path reason
  code, a stale negative code, a duplicate code, an unsorted code set, or a
  reason set different from independent recomputation;
- the binary confirmation-receipt-frame role missing, duplicated, role-swapped,
  re-encoded, truncated, or changed after its digest enters the phase-two
  frame;
- a descriptor with no preimage, a filename that claims a digest different
  from its bytes, a wrong byte count or media type, and a readable malformed
  preimage;
- omission of a failed backing-byte row or representing missing bytes as a
  successful zero-byte artifact;
- one evaluator result presented twice, two results produced by the same
  implementation identity, shared evaluator source or generated evaluator
  code, an unpinned interpreter or dependency graph, and a result that does
  not bind its exact inputs;
- a missing Java 21.0.9 result, a readable Java disagreement, and a
  comparison that checks only the final disposition while domain or reason
  outputs differ;
- either receipt naming or hashing Seal 0.2, Seal 0.2 omitting either receipt,
  or a receipt substituted after comparison; and
- any changed Evidence or Seal semantics published under a 0.1 resource ID.

Each refusal must be paired with a safe control that proves the exact intended
invariant, not merely that some unrelated validation error occurred.

## Consequences and retained nonclaims

The successor makes exact backing bytes and independent recomputation part of
the assurance graph instead of prose outside it. It also increases the
evidence surface: new schemas, blobs, tools, locks, results, receipts, and
known-bads must all remain replayable. Agreement among three evaluators is
stronger defect-detection evidence than one implementation checking itself,
but correlated specifications can still make all three agree incorrectly.

This decision does not establish that:

- any declared person, credential, ceremony, assignment, custody,
  effective-control relation, or verifier-independence claim is real;
- a natural person saw, understood, or agreed with any bytes;
- synthetic content-addressed preimages are real-world evidence;
- independent code paths are organizationally independent review;
- exact evaluator agreement proves the ruleset is normatively correct;
- singleton eligibility is approval, current authority, aggregate quorum, or
  an admitted `AssuredDecision`; or
- any current consumer accepts Evidence 0.2 or Seal 0.2.

PRQ-013 remains `unresolved_blocking`. T1 authority assignment, T2 command,
event, state, reducer, currentness, quorum, wrapper, and consumer migration
dependencies remain absent or unaccepted. Gate A remains blocked pending its
complete retained evidence and the operator's exact-byte decision.

This ADR authorizes architecture work only. It does not authorize runtime or
application implementation, credential use, cloud or Google Cloud access,
network services, spending, a real protected ceremony, a Gate B probe,
deployment, scientific-results publication, or any external effect. Gate B is
not entered, exercised, or weakened by constructing this successor chain.
