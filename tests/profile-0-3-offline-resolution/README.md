# PRQ-002I: dependency-closed offline resolution for the declared universe

This suite retains the bounded two-implementation evidence required by
[ADR 0109](../../docs/decisions/0109-prove-dependency-closed-offline-resolution.md):
the declared 199-member repository universe — the full 144-schema corpus,
the canonicalization candidate records and raw-number contract, the nine
frozen structural-nonidentity fixtures, and the retained artifacts of the
PRQ-002F, PRQ-002G, and PRQ-002H suites — is dependency-closed. Every one
of the 6,456 schema `$ref` edges resolves offline (in-document fragments by
exact RFC 6901 pointer; absolute `urn:odeya:schema:` references against the
registry with recorded target digests; anything else refuses, including
`$dynamicRef`), and every one of the 241 declared digest bindings across
three declared shapes recomputes exactly from repository bytes. No network,
no verification-time directory discovery, no environment, no alias, no
fallback.

Two source-separated zero-dependency implementations emit byte-identical
projections carrying the complete edge lists; the dedicated validator is a
third recomputation path that re-derives every edge itself before checking
any byte census, regenerates the universe deterministically, rejects 26
embedded known-bad mutations — including an injected HTTP reference, an
unknown-URN reference, a bound-target byte drift, and symmetric coherent
forgeries of both results — and re-executes both runners under
`--recompute-all`.

## Named residue and claim boundary

Four historical resource identities remain outside this universe by design
and are declared in the universe manifest rather than silently resolved:
`command-contract-registry:0.1.0`, `command-receipt:0.3.0`,
`work-contract:0.1.0`, and the retained exact `command-envelope:0.4.0`
vocabulary source. Binding shapes outside the three declared forms are not
claimed. The closure claim covers the declared universe at the retaining
commit only: no out-of-universe closure, no product identity or digest, no
profile issuance, no PRQ-002 closure, no Gate A acceptance, and no runtime
or publication authority.
