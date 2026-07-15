# Architecture schema conformance

This directory tests the architecture contracts only. It does not implement or
exercise an Odeya runtime, and a pass is not Gate A acceptance.

`manifest.json` registers immutable valid fixtures plus explicit JSON Pointer
mutations that must be rejected. The validator first proves every adversarial
case starts from a valid base; this prevents a broken base fixture from creating
a false-positive rejection. Every schema must have at least one valid and one
invalid case.

The harness asserts JSON Schema Draft 2020-12 meta-validity, rejects duplicate
JSON object members, enables RFC 3339 `date-time` format assertions, and refuses
dependency-version drift. Run it in an isolated environment:

```bash
python3 -m venv /tmp/odeya-architecture-venv
/tmp/odeya-architecture-venv/bin/python -m pip install -r requirements-architecture.txt
/tmp/odeya-architecture-venv/bin/python scripts/validate.py
```

These are structural tests. Ordering of timestamps, digest recomputation,
cross-record referential integrity, authority separation, unit compatibility,
transactional invariants, and scientific validity require semantic validators
and later Gate B probes; schema acceptance must never be presented as evidence
for those properties.
