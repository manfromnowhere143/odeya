# Architecture-surface implementation-lock probes

This bounded suite proves that Odeya's architecture-only repository surface
refuses each named implementation bypass for the implementation-lock reason
it declares. Every known-bad entry must produce exactly one expected refusal;
an incidental schema, link, import, or release-check failure does not count.

The retained corpus covers runtime roots under `src/`, `engine/`, and `lib/`;
an arbitrary top-level file; executable-capable code under allowed roots; an
embedded executable suffix; an unknown file type; an unauthorized executable
bit; a symlink; a staged blob that differs from its benign worktree view; a
Git mode `160000` submodule; and shebang/binary content disguised as
architecture data. Safe controls preserve current validators, release scripts,
a formal model, documents, and a retained extensionless license.

Run the self-test only:

```bash
python3 scripts/validate_architecture_surface.py --self-test-only
```

Run the self-test and inspect the current repository inventory:

```bash
python3 scripts/validate_architecture_surface.py
```

A pass is bounded repository-shape evidence. The checker does not inspect the
semantics of every text file, prove that the allowlisted tools are correct,
authorize runtime, or accept Gate A.
