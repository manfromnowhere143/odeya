# Constitutional construction adversarial checker

This isolated architecture suite checks the contracts in
[`architecture/constitutional-construction-order.schema.json`](../../architecture/constitutional-construction-order.schema.json)
and
[`architecture/blocked-construction-receipt.schema.json`](../../architecture/blocked-construction-receipt.schema.json).

Run it from the repository root:

```bash
python3 tests/constitutional-construction/check.py
```

The suite schema-checks a prospective replacement core/evidence/seal profile
and a fail-closed blocked receipt. Every family profile explicitly says that
the named existing source-candidate bytes do not conform and that transitive
version migration remains blocking. It then applies semantic mutations to a
deliberately synthetic, blocked chain to prove rejection of concrete
cross-object mismatches:
root/C0/checkpoint/P0 bindings, component sets, recovery frontier, witnesses,
command/envelope/handler equality, activation sequence and scope, attestation
digest, recovery quorum, and critical role separation.

All digest-shaped values in the fixtures are test tokens. A pass creates no
real witness, handler evidence, root, C0, checkpoint, P0, RegistryActivation,
Gate A acceptance, or runtime authority.
