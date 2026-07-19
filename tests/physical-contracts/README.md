# Physical contract candidate suite

This isolated suite tests the candidate machine contracts behind the physical-science constitution. It is intentionally outside runtime and publication enrollment.

Run:

```bash
.venv-architecture/bin/python tests/physical-contracts/check.py
```

The checker validates eight physical schemas plus the generic
`VerificationPackage` schema with duplicate-key rejection and Draft 2020-12
meta-validation, verifies their dependency graph is acyclic, enforces the
fixed UTC-microsecond and no-negative-zero lexical profiles, and executes the
case inventory in `cases.json`.

The bounded local semantic checks cover registered-unit identity, exact
seven-base dimensions, time ordering, Type A/Type B versus
aleatory/epistemic classification, matrix shape/symmetry/range, hardware
coverage reconciliation, calibration validity, calibration/validation
partition independence, physical-measurement scope, safety-envelope validity,
and one exact resolver-backed join from the retained physical verification
fixture to its typed `PhysicalEvidenceVector` subject. That join derives the
required IV4 class, physical-validity and safety applicability, and bounded
terminal language from the selected subject predicates. It rejects the former
false-positive pairing of IV4 and a passing physical-validity dimension with
“No physical-world assertion.”

The suite does not establish covariance positive semidefiniteness, propagation
correctness, frame transforms, general registry resolution, canonical digest
recomputation, physical truth, model adequacy, metrological traceability, VVUQ
credibility, or safety.

The checker pins and validates one exact fixture for every schema:

- `physical-quantity.valid.json`: exact-decimal force with registered Newton binding, seven-base dimension vector, frame, controlled time, spatial support, and provenance.
- `uncertainty-budget.valid.json`: distinct Type A/Type B and aleatory/epistemic classifications with covariance, correlation, shared-source, calibration, and propagation evidence.
- `physical-measurement-result.valid.json`: a measured physical-world result with raw signal, instrument and firmware identity, environmental context, calibration chain, uncertainty binding, acquisition provenance, and clear quality flags.
- `asset-configuration-snapshot.inbar-blocked.valid.json`: the Inbar fail-closed condition where hardware identity is unknown and zero observed components is an observation, never a success claim.
- `physical-model-record.valid.json`: separated conceptual, code, numerical, discrepancy, calibration, and independent physical-validation partitions.
- `physical-evidence-vector.valid.json`: the exact ten-component credibility vector and P0–P12 gate set.
- `safety-envelope.valid.json`: a current, recommendation-only envelope with runtime assurance and a closed actuator boundary.
- `physical-experiment-contract.inbar-refused.valid.json`: an Inbar experiment refusal caused by unknown hardware and indeterminate measurement capability, with no execution or actuator authority.
- `../architecture-schema/fixtures/verification-run-physical.valid.json`: a
  synthetic `VerificationPackage` example whose exact typed subject is the
  physical-evidence-vector fixture, whose selected physical and safety
  predicates require matching passing dimensions, and whose terminal language
  explicitly grants no action, dispatch, publication, or Gate A authority.

Passing this suite grants no execution, publication, actuator, registry, reducer, method, metric, verification, or Gate A authority.
