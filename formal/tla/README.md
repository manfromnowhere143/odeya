# Odeya Gate A bounded formal models

Status: architecture evidence candidate, 2026-07-15. These models check a finite abstraction of the proposed contracts. They are not runtime code, an implementation proof, a liveness proof, a physical safety case, or Gate A acceptance.

## Model suite

| Module | Contract surface | Safe properties |
|---|---|---|
| `AuthorityCommandGrant.tla` | Command ID/digest binding; immutable accepted/rejected receipt; reservation/use/release; expiry/revocation; maximum use; effective-principal quorum | One bound result and execution; no alias-inflated quorum; no capacity leak; every use was active, unexpired, and sufficiently approved |
| `GrantConsumptionPoint.tla` | The exact resolution of ordinary-command versus cross-boundary-effect grant consumption | Ordinary domain commit consumes atomically; effect intent only reserves; dispatch claim rechecks and consumes; revoke/expiry first blocks dispatch; claim first remains an in-flight fact |
| `ExternalEffects.tla` | T1 intent, dispatch claim, timeout, `completion_unknown`, independent reconciliation, and retry classification | Intent precedes dispatch; no post-terminal dispatch; no blind retry; ambiguity cannot become not-applied without reconciliation; completed reconciliation retains polarity |
| `PublicationRelease.tla` | Candidate, request, human decision, deterministic manifest, exact single-use publication grant, effect, independently ordered visibility observation, dispute, and settlement | Authorized candidate precedes seal; grant/effect bind exact manifest; single use; timeout or visibility alone never means released; release requires retained confirmed application plus exact visibility in either arrival order; exact-visible/confirmed-not-applied contradiction atomically requires dispute and cannot settle |
| `CognitiveControl.tla` | Sealed-truth exposure, material-evidence disposition, consensus, five-dimensional verification capacity, a separate data-access gate, acyclic View→Receipt→Bundle issuance, and dispatch admission | Producers never receive sealed truth; promotion requires disposed material and grounded evidence; consensus is not evidence; every founding verification dimension is reserved; failed/not-run compilation and missing/mismatched bundles refuse dispatch; dispatch binds current position, authority, and data access |
| `ResourceReservation.tla` | One child reservation under a `resource_budget` aggregate across non-fungible execution, money, and verification dimensions; reserve, claim, observe, settle, release, expiry, crash, and recovery | Admission is componentwise with no cross-resource conversion; claim commits the ceiling but does not invent actual use; crash/recovery keeps a claimed ceiling held; release/expiry are pre-claim only; settlement requires retained observation evidence |

Each `*.safe.cfg` disables all fault transitions and asks TLC to check the named invariants over the complete reachable bounded state graph. Each `*.counterexample.cfg` enables exactly one deliberate architectural defect and must terminate with TLC exit code 12 at the intended invariant. A green negative control would be a test-suite failure.

The cognitive identity model deliberately represents View, Receipt, and Bundle as immutable tokens with one dependency order:

```text
schema-valid View subject
  -> externally issued View identity
  -> compilation Receipt that references that View
  -> external Bundle/root that references View + Receipt
  -> current dispatch admission
```

The View never references the Receipt or Bundle. The Receipt never references the Bundle. The static dependency graph and dynamic issuance invariants check this bounded causal order, while actual canonical bytes, digest recomputation, signatures, and collision resistance remain outside the model.

Publication visibility is modeled as an independently arriving observation after dispatch. The safe graph therefore includes both `confirmed_applied -> exact_visible` and `exact_visible -> confirmed_applied` orderings. Settlement is the same conjunction in either order. Under either observation order, exact visibility combined with retained `confirmed_not_applied` atomically enters a monotonic `required` dispute axis and remains `completion_unknown`; it cannot be coerced into released or confirmed-not-released.

Resource capacity is modeled as a componentwise vector rather than one convertible scalar. Claiming changes reservation state to `claimed` and keeps the entire ceiling held; it does not set actual use. A crash and a recovery observation are historical facts, not release authority. Only a separate usage observation permits settlement, while cancellation-style release and expiry are legal only before claim. The four mutation controls independently permit cross-dimension compensation, crash release, settlement without observation, and actual-use inference at claim; each reaches the intended invariant violation.

## Normative consumption-point interpretation

The suite makes one leading Gate A resolution explicit:

```text
ordinary in-ledger command:
  admission + grant use + receipt + domain batch commit atomically

cross-boundary effect:
  T1 external_effect.authorized
    + exact grant-use reservation
    + resource reservation
  -> dispatch-claim transaction rechecks current authority/time/correction
    + authority.grant_use_reserved -> authority.grant_used(dispatch_claim)
    + external_effect.started
  -> provider call outside the transaction
```

If revocation, expiry, cancellation, or correction commits before dispatch claim, it releases or invalidates the exact reservation and start is illegal. If dispatch claim commits first, the in-flight attempt remains historical; later revocation cannot unsend it and reconciliation remains mandatory. The deliberate `consume-at-intent` model instead consumes at T1 and then dispatches without a current-authority recheck; TLC finds the counterexample in three states.

The architecture candidate now includes `authority.grant_use_reserved`, typed `authority.grant_use_reservation_released(to=released|expired|cancelled)`, dispatch-aware `authority.grant_used`, exact reservation ID/TTL/target binding, three closed external-effect command payloads, replay traces, and the grant-policy `consumption_point`. That resolves the representational ambiguity in the candidate, but it is not Gate A closure: accepted registry/reducer digests, independent semantic validators, recovery vectors, and independent architecture/security review remain. See [formal finding FM-A-001](FINDINGS.md).

## Toolchain pin

The suite uses the official stable TLA+ tools release `v1.7.4`, TLC `2.19` revision `5a47802b5c391f59ecdd44117981f4ff8c0656ba`. On 2026-07-15 the official API also listed `v1.8.0` as a prerelease; this evidence run intentionally selected the latest stable release rather than a same-day prerelease.

- Official project: <https://github.com/tlaplus/tlaplus>
- Stable release: <https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4>
- Asset: <https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar>
- Asset size: `2,274,532` bytes
- Locally verified SHA-256: `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`
- Java used for the retained run: OpenJDK `21.0.9`; TLA+ tools require Java 11 or newer

No binary is vendored. Fetch it only into `/tmp` and verify it before use:

```bash
mkdir -p /tmp/odeya-tla/v1.7.4
curl -fL --retry 3 \
  https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar \
  -o /tmp/odeya-tla/v1.7.4/tla2tools.jar
printf '%s  %s\n' \
  936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88 \
  /tmp/odeya-tla/v1.7.4/tla2tools.jar | shasum -a 256 -c -
```

The machine-readable pin is [toolchain.lock.json](toolchain.lock.json).

## Reproduce

From the repository root:

```bash
bash formal/tla/check.sh
```

The script verifies the jar digest, parses every module with SANY, and runs TLC breadth-first sequentially with one worker. The six primary safe configurations and all negative controls use seed `20260715` and fingerprint polynomial `0`; CognitiveControl is also rerun as a supplemental safe execution with seed `20260716` and polynomial `1`. The harness recognizes expected counterexample exit code `12`. Every case receives an isolated metadata directory below `/tmp`; this also avoids a TLA+ tools temporary-standard-module race observed when independent TLC JVMs were launched concurrently. The supplemental run is the same model/configuration/checker under a second fingerprint profile, not an independent proof. The repository remains architecture-only.

The direct safe-run form is:

```bash
cd formal/tla
java -XX:+UseParallelGC \
  -jar /tmp/odeya-tla/v1.7.4/tla2tools.jar \
  -workers 1 -seed 20260715 -fp 0 -cleanup \
  -metadir /tmp/odeya-tla/manual/authority \
  -config AuthorityCommandGrant.safe.cfg \
  AuthorityCommandGrant.tla
```

Exact recorded outcomes, source digests, and negative-control traces are in [RESULTS.md](RESULTS.md) and [results-manifest.json](results-manifest.json).

## Explicit assumptions

The safe checks prove invariance only for the checked transition systems and bounds:

- canonical database transitions are atomic and serializable in the order TLC explores;
- authentication, signature verification, schema/digest correctness, policy input integrity, and durable storage are assumed inputs, not cryptographically implemented here;
- time is one controlled discrete counter with exact comparison and no clock uncertainty model;
- identities and digests are uninterpreted model values; collision resistance and canonicalization are outside this suite;
- same-ID/same-digest replay is represented as a stuttering step that returns the retained result; transport response bytes and replay counters are not state variables;
- authority uses at most two command identities, two digests, three presented principals with two effective principals, maximum use one, and a three-tick horizon in the retained config;
- external effects use two effect identities, one retry-safe profile and one unsafe profile, with at most two dispatch attempts;
- publication uses two candidates, two deterministically paired manifests, one publication grant, one effect, and one destination/visibility oracle;
- cognitive control uses two material-evidence items, one producer-visibility bit, one verifier-visibility bit, five unit-capacity verification dimensions (`deterministic`, `compute`, `expert`, `physical`, `safety`), one Boolean data-access gate, two abstract View/Receipt identities, one current Bundle, and one position/authority advance; data access is not fungible capacity, and the model checks causal identity binding rather than cryptographic digest correctness;
- resource reservation uses one child reservation and three positive integer dimensions (`execution`, `money`, `verification`) with one fixed capacity/demand vector per configuration; it does not model multiple-reservation packing, partial observation, heterogeneous units, exchange rates, refund arithmetic, price drift, or liveness of reconciliation;
- provider outcomes and reconciliation results are nondeterministic but truthful when admitted under the modeled evidence rule;
- transaction cohorts, multiple grants per command/effect, partial multi-destination publication, nested delegation, multi-reservation arithmetic, leases, checkpoints, recovery forks, rights graphs, and physical interlocks are not expanded here; and
- no fairness or temporal liveness condition is asserted. The models prove that bad states are unreachable within bounds, not that a good terminal state is eventually reached.

The state-space fingerprint collision estimates are retained with the results. A bounded TLC pass cannot establish implementation conformance; later authorized code needs refinement mapping, trace extraction, concurrency/fault injection, and independent formal review.
