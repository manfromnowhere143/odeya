# ADR 0072: The sequencing law becomes a gate; twenty more rules isolated

- Status: Executed; records a process failure and removes its cause
- Date: 2026-07-18
- Decision owners: architecture review
- Gate effect: publication requires retained rehearsal evidence bound to
  the exact commit being published; twenty further cross-field rules gain
  ablation-verified cases

## A law that depended on remembering

Earlier today the CI incident produced a written law: rehearse the exact
commit, push, then watch every remote workflow to green. Hours later this
session pushed `d993495` while that commit's rehearsal was **still
running** — reading a TLA+ model's completion line as the rehearsal's.
The rehearsal subsequently passed, so nothing invalid reached the public
surface, and that is luck rather than discipline. A law enforced by
remembering is not a gate; the same reasoning that moved the CI-only pins
into local readers applies to publication itself.

`scripts/ci/push-rehearsed-head.sh` now performs every publication. It
refuses unless the worktree is clean, a rehearsal evidence manifest
exists for the exact `HEAD` being pushed, that manifest binds that commit
and claims no canonical scientific status, and `HEAD` fast-forwards the
remote branch. It prints, on success, that the push is not complete until
the workflows report green — the half no script can perform.

## Twenty more rules

Repair-directed generation closes twenty of the rules the first pass
could not isolate. When deleting the target rule leaves the instance
still invalid, the residual errors name precisely what else broke;
`const`, `enum`, `null`-type and empty-array mismatches introduced by
satisfying the target's own discriminators are repaired, and the
two-sided ablation is re-run — refused with the rule, accepted without
it. Cross-field rule coverage moves 112 to **132 of 286**, all
ablation-verified, corpus 774 to 794 cases.

154 rules still resist: their `if` conditions entangle neighbouring rules
in ways `const`/`enum` repair cannot untangle, and closing them needs
required-field synthesis — constructing absent sub-objects rather than
correcting present ones. That is the next generation increment and it is
named, not attempted.

## Boundary

The publication gate constrains sequence, not judgement: it cannot tell
whether a commit *should* be published. Ablation proves a rule is
noticed, never that the rule is right. Nothing here is an accountable
review determination, an admitted member, or Gate A acceptance.
