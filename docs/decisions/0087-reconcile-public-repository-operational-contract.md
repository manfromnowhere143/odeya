# ADR 0087: Reconcile the public-repository operational contract

- Status: Executed as an architecture/release truth correction; its remote
  protection finding was subsequently closed at the account-control layer by
  ADR 0091 rulesets `19178198` and `19178503`. The first complete
  candidate-to-main activation remains separately pending
- Date: 2026-07-19
- Decision owners: repository owner (publication authority), architecture
  review (release truth)
- Gate effect: supersedes the unexecuted private-remote bootstrap prose with an
  ongoing evidence-gated publication contract for the existing public remote;
  grants no runtime, deployment, scientific-publication, or Gate A authority

## The contradiction

ADR 0047 records the owner's executed decision to create and publish
`https://github.com/manfromnowhere143/odeya` as a public architecture
repository. The repository-release contract, roadmap, status, and later
sections of the session handoff still described a future private remote whose
creation and first push required Gate A. Those statements cannot all be true.

The repository bytes and remote observations on 2026-07-19 establish:

- the canonical remote exists and is public;
- its default branch is `main`;
- `origin/main` equals
  `50e4bc6bfd634c7d5fe11cf0114e1fee94b4e62d`;
- all three workflow families on that exact head are green;
- secret scanning and secret-scanning push protection are enabled;
- Dependabot security updates are disabled;
- no repository ruleset exists and `main` is not server-side protected; and
- the local pre-push hook is not protection for a fresh clone or a caller that
  bypasses local configuration.

The public remote is therefore an executed fact and an authorized architecture
publication surface. Server-side governance remains weaker than the release
contract intends.

## Decision

1. The canonical repository identity is the existing public GitHub repository,
   not a future private bootstrap.
2. Architecture commits may be published only through the exact-commit
   rehearsal, publication-history audit, guarded push, remote-check
   observation, remote-main rehearsal, and invariant-profile comparison
   defined by `docs/REPOSITORY_RELEASE.md`.
3. Publication of architecture bytes remains distinct from Gate A acceptance,
   engine implementation, research publication, deployment, credentials,
   paid compute, mission data, or any other external effect.
4. A new clone is not protected by the repository's local hook until
   `core.hooksPath=.githooks` is configured. That limitation stays explicit.
5. A server-side `main` ruleset with required checks, reviewed changes, linear
   history, and no force-push/deletion is the next repository-governance
   operation. It must be observed after configuration; prose cannot represent
   it as active beforehand.
6. Historical bootstrap instructions remain evidence of the intended process,
   not current instructions. No session may recreate, rename, privatize,
   transfer, or delete the remote from this decision.

## Known-bad boundary

The release validator must refuse a contract that:

- again says no remote exists or that the canonical repository is private;
- omits the exact existing public repository identity;
- treats a local hook as server-side protection;
- allows an architecture push without evidence bound to the exact commit; or
- converts repository publication into runtime or Gate A authority.

The retained workflow mutations continue to prove that write permissions,
untrusted triggers, secret/token plumbing, self-hosted runners, shallow
history, and undeclared jobs are refused. They do not prove GitHub account
configuration; that evidence requires independent remote observation.

## Consequences

Operational recovery now starts from the public repository fact and current
remote head. The release contract becomes an ongoing publication protocol
instead of an unexecuted activation plan. The absence of a server-side ruleset
was recorded here as an open blocker rather than silently replaced by
confidence in a local hook. On 2026-07-19 ADR 0091 later closed that
account-control finding: both no-bypass rulesets were applied and read back,
pull requests were disabled, and the exact merge/Actions policies were
observed. Bootstrap candidate `a25d026bd7233dfc452accc6087ded0bf015d7b4`
then passed four workflows and ten jobs on attempt 1. Those later facts do not
rewrite this ADR's historical observation and do not, without the final
candidate cycle and activation receipt, establish complete publication
activation.
