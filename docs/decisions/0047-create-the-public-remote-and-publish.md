# ADR 0047: Create the public remote and publish the architecture

- Status: Executed on the owner's explicit publication instruction of
  2026-07-17
- Date: 2026-07-17
- Decision owners: repository owner (publication authority), architecture
  review (content)
- Gate effect: grants and exercises remote and publication authority for
  this architecture repository; grants no runtime, deployment, or Gate A
  authority

## Context

ADR 0045 packaged the repository for open source and recorded that the
destination values are the owner's alone. The owner then instructed the
publication explicitly. The destination is discovered, not invented: the
owner's GitHub account already publishes the sibling proof missions
Sentinel and Telos under `manfromnowhere143`, and the authenticated GitHub
CLI session confirms the same account.

## Decision

- Destination: `github.com/manfromnowhere143/odeya`, public, alongside
  `sentinel` and `telos` so reviewers can traverse the whole research
  ecosystem under one owner.
- Published content: this repository in full, including the complete
  commit history — the thirty-six-commit decision trail is the story, and
  every commit is owner-authored with fresh-clone rehearsal evidence
  retained locally. The session handoff ships whole, mission soul included:
  it is the soul of the project, not an appendix.
- The default branch is `main`, set to the current rehearsed architecture
  head. The first release tag is `v0.1.0-architecture` on the same commit.
- Pre-push audit: full-history secret scan clean; no workflow depends on
  repository secrets; all workflows run on public `ubuntu-24.04` runners.
- The recovery-identity lines in the session handoff now state the real
  remote and the granted publication authority, because the handoff must
  never describe a world that no longer exists.

## Non-decisions

Publication of the architecture grants nothing else: Gate A acceptance,
runtime construction, deployment, external effects, domain purchase, and
company decisions all remain separate and owner-held. Local rehearsal
evidence directories remain local; they are evidence about commits, not
repository content.

## Consequences

Anyone can clone the architecture, run one command, and watch the
repository prove itself. The public CI must show green on `main`; a red
check on the published default branch is a publication defect to fix
immediately.
