# Canonicalization evaluator-integrity evidence

Status: bounded architecture-evidence falsifier; the canonical profile remains
unissued and causal execution origin remains unproved.

This suite tests the evidence boundary of the retained canonicalization
comparator without changing the comparator, canonical vectors, oracle, source
lock, runners, result files, or comparison receipt. It exists because a copy of
the retained Python result, relabelled only with the retained Node
`implementation` metadata, makes the unchanged comparator return success with
`implementation_agreement=true`.

The checker therefore keeps three propositions separate:

- oracle conformity: `pass`, `fail`, `indeterminate`, or `not_run`;
- cross-result comparison: `exact`, `disagree`, `indeterminate`, or `not_run`;
- execution/source separation: `proven_within_declared_scope`, `not_proven`,
  or `contradicted`.

For the unmodified retained pair, oracle conformity is `pass` and
case-projection comparison is `exact`, but execution origin is
`unwitnessed_retained_artifact`; source separation is `not_proven`. The
copied-and-relabelled trial deliberately reproduces the inner false accept,
while the outer trial provenance classifies claimed source separation as
`contradicted`. An omission makes comparison `indeterminate` even when the
legacy agreement Boolean remains true. Identical wrong answers are `exact`
comparison plus oracle `fail`, never a pass.

The safe control passes the exact retained result bytes to the comparator. The
copied-and-relabelled attack creates a distinct right-hand byte sequence whose
parsed value equals the retained Node-labelled result. Its witness binds the
source raw and parsed-object digests, the intermediate copied-object digest,
the transformed raw digest, and the exact permitted field delta. The checker
therefore rejects a neutralized or no-op mutation even if an attacker fabricates
an intermediate hash.

`cases.json` binds the candidate contract and declares one safe control, nine
fixed attacks, and thirty-three meta-gate known-bads. Every comparator trial uses
fixed arguments, isolated temporary result copies, a five-second timeout, no
shell-selected command, and two identical repetitions. The checker rejects
duplicate JSON keys, open shapes, unsafe or duplicate paths, symlinks,
digest/size drift, changed censuses, changed trace order, unsupported
dispositions, fabricated coverage, a blinded gate, a no-op copied-output
mutation, and any authority or nonclaim bit with the wrong value. Exact role,
lexical-path, resolved-path, and inode bindings prevent aliases and role swaps;
final and ancestor symlinks are refused. Comparator processes have their own
process group, and timeout termination targets that group rather than only the
parent PID. The retained timeout control does not separately spawn and observe
a child process. The checker has no write, update, bless, or regeneration mode;
temporary files are discarded after each trial.

Run the focused evidence check with:

```bash
python3 scripts/validate_canonicalization_evaluator_integrity.py
```

A zero exit means the fixed defect boundary and the meta-gate reproduced their
declared observations. It does not repair the comparator, prove two executions,
establish organizational independence, issue a profile, accept Gate A, or
authorize runtime, credentials, deployment, publication, or external effects.
