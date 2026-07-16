# Command identity contract cases

This isolated suite checks exact equality across the structural
`CommandEnvelope`, `CommandReceipt`, standalone `CommandContractRecord`, and
`CommandContractRegistry` fixtures. It is architecture evidence only. Every
result has `usable_for_admission=false`; the coherent baseline is expected to
stop at `blocked_unresolved_identity`, never pass.

The checker first validates all four baseline fixtures against their exact
schemas through a preloaded resource registry. It then structurally validates
every mutated subject before running cross-object checks. A structurally invalid
mutation has the separate outcome `invalid_structural_contract`; it cannot
false-green a semantic mismatch. Every semantic case asserts an exact mismatch
reason set plus the exact independent unresolved-identity set for payload,
handler input/output, record, registry, membership, and activation.

Two cases use `comparison_overrides`. Those overrides do not change the schema-
validated subjects; they are explicitly synthetic, non-admissible comparison
views used to prove that command version, logical payload version, and schema
resource version are independent axes, and that canonicalization profiles may
not disagree once resolved. No override is evidence that a currently forbidden
resolved identity exists.

The suite covers command ID, request digest, idempotency scope, command and
payload identity, schema resource/canonical/closure identity, member key,
record/registry references and digests, membership-proof equality, activation-
reference equality, offline resolution, schema-version suffix, closure root,
and embedded-member equality. Actor-to-actor-binding and target-to-target-
binding projections, digest recomputation, cryptographic membership proof,
activation proof, and EngineContractRoot proof remain open under PRQ-012.

Run:

```bash
.venv-architecture/bin/python tests/command-identity-contracts/check.py
```
