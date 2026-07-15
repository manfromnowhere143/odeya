# Thesis Intake

The long-term “GitHub for research theses” vision is coherent if Odeya governs proposals rather than pretending to automate truth. A human contribution enters as an untrusted, immutable proposal. If admitted, it becomes a funded research branch with its own contract; only verified evidence can update shared knowledge.

This surface is a later phase. The first engine milestone uses operator-authored missions and human admission decisions.

## Proposal package

A thesis proposal includes:

- stable proposal ID, version, author identity or declared pseudonymity, and signature;
- concise question and proposed mechanism;
- intended real-world value and affected decisions;
- scope, assumptions, competing explanations, and named falsifiers;
- prior work, citations, claimed novelty, and known collisions;
- available evidence, data, code, compute, and access requirements;
- requested confidentiality and disclosure state;
- ownership, license, data rights, conflicts, and export or safety constraints;
- expected resource envelope and human expertise needed;
- what acceptance, rejection, or a null result would mean.

Attachments, code, links, and instructions remain quarantined until screened.

## Admission lifecycle

```text
submitted
  -> identity/rights/safety quarantine
  -> duplicate and prior-art map
  -> falsifiability and evidence-access review
  -> feasibility and resource review
  -> conflict and portfolio review
  -> accept / defer / decline / request revision
  -> if accepted: forked ResearchMissionSpec
```

Each transition has an accountable principal, retained evidence, and reason. Declined or deferred proposals remain discoverable according to the contributor's disclosure choice and legal constraints.

## Decision dimensions

Reviewers see dimensions separately rather than one mystical score:

- clarity and falsifiability;
- potential information gain;
- decision or real-world consequence;
- novelty and complementarity with the portfolio;
- evidence and substrate availability;
- feasibility under current tools, compute, and expertise;
- expected cost and time to a discriminating test;
- safety, misuse, privacy, rights, and publication risk;
- quality of competing explanations;
- independence and replication path.

Automated systems may retrieve prior work, flag duplicates, test schema completeness, propose reviewers, and estimate resource bands. They do not make an irreversible admission, rights, or safety decision in the founding phases.

## Decision meanings

- **Accept:** worth testing under a specified scope and resource envelope.
- **Request revision:** potentially admissible but missing named information.
- **Defer:** coherent but blocked by timing, evidence, expertise, portfolio, safety case, or resources.
- **Decline:** outside charter, not falsifiable enough, materially duplicated, unsafe under available controls, rights-incompatible, or too weak relative to alternatives.

Acceptance does not endorse the thesis. Decline does not establish falsehood. Both are portfolio decisions with reasons and an appeal or revision path.

## Mission fork

An accepted proposal is copied into a new immutable mission origin record. Subsequent protocol, evidence, claims, corrections, and publication are owned by that mission branch. The original proposal remains unchanged and linked.

Contributor credit and access are explicit. A contributor cannot silently inherit execution, verifier, publication, or shared-memory authority.

## Knowledge absorption

A proposal never enters the claim graph as established knowledge. The sequence is:

```text
proposal
  -> candidate claim
  -> preregistered test
  -> retained evidence
  -> independent verification
  -> bounded adjudication
  -> optional replication
  -> versioned claim/epistemic-graph update
```

Negative, null, invalid, and blocked outcomes remain part of the mission record. Contributor reputation can prioritize review attention, but it cannot replace evidence.

## Abuse and integrity controls

- isolate code and active content before inspection;
- scan for plagiarism, citation fabrication, malware, secrets, and personal data;
- keep private submissions out of general retrieval and model training by default;
- prevent proposal flooding with rate limits and staged identity requirements;
- declare conflicts and reviewer exposure;
- use sealed review where novelty or identity bias matters;
- keep reviewer reasoning and decision evidence auditable without exposing private chain of thought;
- support embargo, withdrawal, correction, and lawful removal.

## Future product surfaces

The contribution system should feel more like a rigorous pull request than a social feed:

- versioned thesis diff;
- prior-art and duplication map;
- unresolved questions and requested evidence;
- reviewer assignments and conflicts;
- decision timeline and reasons;
- mission fork and exact downstream state;
- reproducible evidence package;
- correction and replication history.

Popularity, follower counts, and visual prestige must not determine scientific admission.
