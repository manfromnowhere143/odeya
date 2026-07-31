# PRQ-002G: profile-bounded JCS serialization conformance for `odeya-jcs-0.3`

This suite retains the bounded two-implementation evidence required by
[ADR 0107](../../docs/decisions/0107-prove-profile-bounded-jcs-serialization-conformance.md):
the exact RFC 8785 interpretation that `odeya-jcs-0.3` pins — verified errata
6292 and 7920 only, ECMA-262 2019 string output, U+002F emitted unescaped,
recursive member ordering by unsigned UTF-16 code units over decoded names,
no Unicode normalization, strict I-JSON surrogate and noncharacter refusal,
and deterministic refusal of every lexical negative zero — executed by two
source- and language-separated zero-dependency implementations over an
answer-free 61-frame corpus (28 accepted, 33 refused).

## The scope is the profile's, on purpose

The profile's raw-number contract admits only integer tokens in the
inclusive safe range, so every number this serialization can ever emit is an
exact decimal integer string. General ECMAScript binary64 shortest-round-trip
serialization — including RFC 8785's double-precision appendix vectors — is
deliberately outside this suite and is claimed by nothing here: a
`type: number` position refuses before serialization is reached. There is no
separate architecture contract pair for this suite by design; ADR 0107 and
this suite's manifest carry the pinned interpretation, and the retaining
commit binds them.

## The discriminating vector

`utf16-unit-order-discriminator` places a U+E000 member name beside a
U+1F600 member name. Unsigned UTF-16 code-unit order sorts the
supplementary-plane name first (its high surrogate 0xD83D precedes 0xE000);
Unicode code-point order sorts it last. The retained canonical output pins
the UTF-16 answer, so an implementation that sorts by code points — including
Python's native string comparison, which is why the Python path realizes the
order explicitly via UTF-16BE byte comparison — cannot reproduce the corpus.
A retained known-bad rewrites this frame's output into code-point order and
must be refused.

## Files and evidence

`vectors.json` carries raw input bytes as lowercase hex, so invalid-UTF-8 and
byte-order-mark frames are first-class; it is answer-free and both runners
consume only it. `cases.json` is the private expectation file (dispositions
and refusal codes only — canonical outputs are never authored, only computed)
and no implementation may read it. The runners emit deterministic result
documents whose projections must be byte-identical; the external comparison
receipt is written last; the execution receipts remain self-attested
byte-consistency records. The dedicated validator
`scripts/validate_profile_0_3_jcs_conformance.py` is a third implementation
that re-derives every frame before checking any byte census, rejects 27
embedded known-bad mutations with declared singleton codes, and re-executes
both runners under `--recompute-all`.

## Claim boundary

No general number serialization, no out-of-corpus conformance, no product
digest or canonicalization of any cohort subject, no organizational
independence, no independent-host reproduction, no profile issuance, no
PRQ-002 closure, no Gate A acceptance, and no runtime or publication
authority.
