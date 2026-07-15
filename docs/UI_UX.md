# UI/UX Engine Contract: The Research Instrument

Status: engine-facing truth and accessibility contract. Daniel owns Odeya's visual/product design; this document does not prescribe or replace that creative direction.

Odeya's interface is a scientific instrument, not an agent theater dashboard. The engine must give the product enough exact state for a researcher to understand the mission's current truth, inspect why it is true, intervene at the right authority boundary, and resume exact work after interruption.

## Design laws

1. **Scientific truth governs every pixel.** Every status, line, motion, count, and color maps to canonical evidence or is clearly labeled as a projection.
2. **Product face first, proof underneath.** The first view explains the question, current bounded result, uncertainty, and next legal action; deeper layers expose exact lineage.
3. **Unknown stays unknown.** Missing, stale, unmeasured, withheld, and inapplicable are visually and semantically different from zero.
4. **No fake live state.** Commit-paced or polled state shows its timestamp and freshness.
5. **No chain-of-thought theater.** Show plans, actions, evidence, decisions, and concise rationales—not synthetic inner monologue.
6. **One meaningful visual beats card walls.** Geometry should correspond to the research object: experiment DAG, evidence graph, uncertainty interval, causal competition, or claim lineage.
7. **Motion must carry evidence.** Use it for a real new event, changed state, or replay. Respect reduced motion.
8. **Prestige technology is last.** Semantic HTML and SVG come before canvas or WebGPU; use heavier rendering only for measured dense workloads.

## Information architecture

### Portfolio

Answers: What consequential questions are active? Which are blocked? Where is uncertainty being reduced? What resources and authorities are committed?

The portfolio is not a leaderboard. It groups missions by question, consequence, state, next decision, evidence freshness, and risk. Positive and null results share equal visual weight.

### Mission

The primary research cockpit:

- mission question and claim boundary;
- current outcome with scope and uncertainty;
- frozen protocol version and amendment status;
- lifecycle timeline and exact next legal action;
- work DAG with attempts, leases, costs, and blockers;
- competing hypotheses and expected observations;
- bars, falsifiers, baselines, and positive controls;
- evidence and provenance projection;
- verifier identity and independence;
- approvals and authority state;
- corrections and unresolved adversarial findings.

### Experiment

Shows one run manifest, environment, inputs, work items, raw and derived artifacts, actual versus estimated resources, logs, failures, and replay controls. A retry is a separate attempt, never an overwritten row.

### Evidence

An ordered claim-evidence view, not an ornamental network. Selecting a claim reveals supporting, contradicting, missing, invalidated, and superseded evidence; each edge opens exact provenance and capture context.

### Claim

Shows eligible wording, forbidden extrapolations, population and environment scope, uncertainty, falsifier state, verifier result, replication status, dependent publications, and corrections.

### Observatory

Operational view for compute, queues, leases, spend, egress, model/tool versions, policy decisions, and incidents. Operational health never substitutes for scientific validity.

### Thesis intake

Later contribution surface for versioned proposals, prior-art maps, review questions, conflicts, decision reasons, and mission forks. It remains visually separate from established claims.

### Publication

A sanitized evidence projection tied to an exact publication manifest. It carries methods, evidence links, limitations, nulls, corrections, version, and citation details without exposing private data or engine internals.

## Core mission composition

```text
┌──────────────────────────────────────────────────────────────────┐
│ Odeya / Mission title       state · freshness · protocol version │
├───────────────────────────┬──────────────────────────────────────┤
│ Question and bounded      │ Lifecycle / work graph               │
│ current verdict           │ current node and next legal action   │
│ interval + scope          │ attempts · leases · blockers         │
├───────────────────────────┴──────────────────────────────────────┤
│ Evidence geometry: hypotheses ↔ experiments ↔ claims             │
│ select any edge for exact artifact and verifier lineage          │
├───────────────────────────┬──────────────────────────────────────┤
│ Bars / falsifiers         │ Authority / compute / actual cost    │
│ controls / corrections   │ approvals / risks / freshness        │
└───────────────────────────┴──────────────────────────────────────┘
```

On small screens this becomes the same evidence order, not a reduced decorative view: verdict, scope, next action, protocol, evidence, gates, authority, resources.

## Visual language

- Fresh-reader default: white or near-white scientific surface with high-contrast typography.
- Optional black/space-grey reading modes preserve identical semantics.
- Monochrome is the foundation.
- Amber is reserved for genuine caution, off-nominal state, or pending consequential review.
- Cyan can mark missing or stale information, always with text or shape redundancy.
- Positive, negative, null, invalid, and blocked states use words and icons in addition to color.
- Confidence intervals, denominators, and missingness appear with the headline number rather than in a tooltip.

No particles, orbits, decorative 3D graphs, fake telemetry, endlessly animated agents, or cinematic “thinking” surfaces.

## Interaction

- Deep-link every mission, protocol, run, artifact, claim, correction, and publication version.
- Meet WCAG 2.2 AA with keyboard navigation, visible focus, screen-reader semantics, forced colors, reduced motion, 200% text resizing, and reflow at 320 CSS pixels (approximately 400% zoom), plus manual testing of complete research workflows and print output.
- Make evidence provenance reachable in at most two deliberate actions from a claim.
- Preserve filter and time position in URLs.
- Explain disabled actions with the missing authority or evidence, not generic error text.
- Dangerous actions show scope, consequence, reversibility, and exact approving principal.
- Never auto-select an approval on timeout.

## Freshness and projection

Every projection displays:

- source ledger position or manifest;
- generated-at time;
- last canonical event time;
- stale or incomplete reason;
- whether values are measured, estimated, inferred, or withheld.

Client optimism is permitted for ordinary navigation, not scientific, authority, spending, or publication state.

## First design deliverable

The first UI slice should use committed replay data rather than invented fixtures and support five deliberately uncomfortable states:

1. valid supported result with a narrow claim;
2. tight null;
3. protocol-invalid result;
4. blocked mission with unmeasured criteria;
5. corrected claim that remains visible in its historical context.

If the interface makes any of these look like generic failure or converts them into progress theater, it has failed its first evaluation.
