# Java 21 eligibility recomputation

This subtree is the independently authored, zero-third-party-dependency Java
implementation of the candidate HDA 0.2 individual-eligibility ruleset. It is
architecture evaluation tooling, not runtime, approval, policy, ceremony, or
Gate A authority.

The process reads exactly three normative surfaces: `vectors.json`, the
candidate eligibility ruleset, and the candidate content-address resolver
profile. The input adapter refuses other filenames before reading them. It
never reads expected-result fixtures, another implementation's source, or
another implementation's output. Its output contains only the deterministic
participant projection requested by the comparison harness.

Compile with the exact toolchain and flags pinned in `dependency-lock.json`:

```text
javac --release 21 -encoding UTF-8 -Xlint:all -Werror \
  -d build/classes \
  src/odeya/hda/java21/StrictJson.java \
  src/odeya/hda/java21/JsonPatch.java \
  src/odeya/hda/java21/InputAdapter.java \
  src/odeya/hda/java21/HumanDecisionAssuranceEvaluator.java
```

Invoke the compiled main class with all four closed options:

```text
java -cp build/classes odeya.hda.java21.HumanDecisionAssuranceEvaluator \
  --vectors ../vectors.json \
  --ruleset ../../../architecture/human-decision-assurance-individual-eligibility-ruleset-v2-candidate.json \
  --resolver ../../../architecture/human-decision-assurance-content-address-resolver-profile-v1-candidate.json \
  --vector-id safe-complete-eligible
```

No mutable alias, network resolution, clock, locale, timezone, randomness, or
generated source participates in the computation.
