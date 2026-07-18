# ADR 0064: Dissolve the compound-name under-bindings

- Status: Executed; closes the second of ADR 0063's surviving weaknesses
- Date: 2026-07-18
- Decision owners: architecture review
- Gate effect: every prong of the eight compound-name known-bad cases
  now has its own sibling case binding its own constraint; the review's
  demonstrated silent deletions are detected

## The weakness

Round-two review showed that a case whose name promises several
constraints — "complete, passing, signed evidence"; "incomplete lanes
or open high"; "prior identity, change evidence, and human signature" —
bound exactly one, and the unbound prongs could be deleted from the
schema with the suite green. This is the conjoined-case masking form
one level up: one case standing in for N proofs while providing one.

## The dissolution

Eighteen sibling cases, cloned from their parents with identical
mutations and one binding per prong: thirteen in architecture-review
(the four evidence-pass consts of the review-ready rule, the closure
evidence and reviewed-at legs, the changed-candidate identity and
evidence legs, both open-high legs, and the three carry-forward legs),
three in constitutional-construction (the local-isolated, action-class,
and external-effects legs of the P0 recovery ceiling), and two in
first-slice-resolution (the unresolved-fork and open-recovery legs of
the C8 frontier rule). Each fires its declared constraint on the
current bytes. An ablation control was exercised: deleting the
operator-decision open-high const — one of the review's demonstrated
silent deletions — now fails the suite through its prong case.

The contract-profile partitions grew accordingly and the local
partition gate caught both changes before commit, as built.

## Boundary

The first-slice catch-all messages remain generic (two cases share
"assignment events are missing, extra, split, duplicated, or out of
order"); sharpening those messages is checker-text work, not case work,
and remains open. Nothing here is an accountable review determination
or Gate A acceptance.
