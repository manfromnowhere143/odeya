# PRQ-002H: nine-product-domain frame governance for `odeya-jcs-0.3`

This suite retains the bounded two-implementation evidence required by
[ADR 0108](../../docs/decisions/0108-prove-nine-product-domain-frame-governance.md):
every one of the nine `odeya-jcs-0.3` product-domain schemas demonstrably
governs — it accepts its one frozen structural-nonidentity fixture with a
complete dual-implementation raw-number token trace, and refuses its five
named attack classes through both production paths.

## The corpus

54 answer-free frames across the nine domains. The nine accepted frames are
byte-for-byte the nine frozen structural-nonidentity fixtures from ADR 0103,
verified against the retained repository bytes by both runners and by the
validator: acceptance is structurally reserved for the exact frozen bytes,
so a schema-valid instance that is not the retained fixture refuses with
`fixture_byte_binding_mismatch`, and no new governed instance can enter
through this suite. The 45 refused frames are five deterministic mutations
per domain — an integral-fraction spelling, a lexical negative zero, an
out-of-safe-range integer, an undeclared member that
`additionalProperties: false` must reject, and a removed first-required
member — each refusing with a declared singleton code through BOTH
implementations, so every domain's refusal surface is exercised as data, not
only as validator mutation.

## Two implementations, one binding gate

`python/runner.py` and `node/runner.mjs` are source-separated and
zero-dependency; each hard-codes the twelve-schema reference census and the
nine fixture bindings independently of the shared vector file, evaluates
through the closed-vocabulary evaluator that refuses unknown keywords, and
traces every governed integer token to its unique RFC 6901 pointer with
exactly one final rule. Their projections must be byte-identical; the
external comparison receipt is written last.

The dedicated validator
`scripts/validate_profile_0_3_product_domain_frames.py` is the binding and
consistency gate in the PRQ-002D parent style: the dual semantic evaluation
paths for this suite are the two runners themselves, and the validator
byte-binds the corpus to the frozen fixtures and governing schemas
(recomputed from current repository bytes), cross-checks the private
expectations against both retained projections, rejects 29 embedded
known-bad mutations — including symmetric coherent forgeries of both
results — with declared singleton codes, and re-executes both runners under
`--recompute-all`. That the parent is a binding gate rather than a third
evaluator is a named design boundary of this suite, not an oversight.

## Claim boundary

The governed instances are and remain structural nonidentity fixtures:
governing them creates no member, commitment, snapshot, digest, identity, or
admission. No conformance beyond the retained corpus, no product digest, no
organizational independence, no independent-host reproduction, no profile
issuance, no PRQ-002 closure, no Gate A acceptance, and no runtime or
publication authority.
