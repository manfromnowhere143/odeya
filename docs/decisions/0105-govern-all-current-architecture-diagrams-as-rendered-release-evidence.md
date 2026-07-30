# ADR 0105: Govern all current architecture diagrams as rendered release evidence

- Status: Proposed architecture-release candidate; not operator accepted
- Date: 2026-07-29
- Decision owners: architecture review, documentation integrity, repository release
- Gate effect: strengthens validation of architecture documentation bytes; grants
  no semantic correctness, visual-design acceptance, implementation, runtime,
  publication, scientific, or Gate A authority

## Context

The repository-release contract previously extracted and rendered only the
single Mermaid block in `README.md`. Six additional current diagrams in
`docs/ARCHITECTURE.md`, `docs/COGNITIVE_ARCHITECTURE.md`, and
`docs/HUMAN_DECISION_ASSURANCE.md` could therefore remain syntactically broken
or visually unusable while the release check stayed green.

The gap was not merely cosmetic. A complete review on 2026-07-29 found diagrams
that lagged the prose contracts by:

- drawing candidate artifacts and epistemic graph deltas around deterministic
  kernel admission;
- making blocked and invalid conditions look like scientific lifecycle phases;
- collapsing publication decision, manifest seal, single-use grant, effect,
  observation, reconciliation, and correction;
- presenting proposed HDA wrapper paths as current and collapsing retained
  `indeterminate` and `invalid` dispositions; and
- using visually unqualified independence language where only role separation
  or measured independence was intended.

A diagram is not authority, but a current diagram is a high-bandwidth
architecture claim. Letting it evade the same exact-byte release surface as its
surrounding prose creates a predictable reviewer and recovery hazard.

## Decision

### Close the current diagram census

Repository-release validation admits exactly seven Mermaid blocks across four
governed documents:

| Document | Exact block count |
| --- | ---: |
| `README.md` | 1 |
| `docs/ARCHITECTURE.md` | 3 |
| `docs/COGNITIVE_ARCHITECTURE.md` | 1 |
| `docs/HUMAN_DECISION_ASSURANCE.md` | 2 |

A missing, extra, empty, unclosed, or forbidden-directive block refuses the
release contract. Every other Git-tracked Markdown file must contain zero
Mermaid blocks. The census recognizes CommonMark backtick and tilde fences,
valid top-level fence lengths and indentation, normalized Mermaid info tokens,
and exact closing-fence rules. A broad marker pass fails closed on
container-carried, nested, attribute-only, or indented-code Mermaid-looking
fences instead of allowing them to evade extraction.

The validator retains four passing in-memory controls and thirty-one known-bad
inventory mutations covering missing, extra, empty, unsafe directives
including tab-separated `click`, unclosed and short-close blocks, alternate
fences and info spacing, ungoverned lowercase and uppercase-extension
documents, refusal of a lowercase-only Git discovery pathspec, blockquote/list
containers, nested text, attribute-only info, legacy and YAML-frontmatter
configuration, unquoted or quoted image-node assets, generic attribute
objects, HTML/Markdown images, CSS `url(...)`, protocol-relative locations,
and HTTP(S), file, data, blob, or FTP URI schemes. The README map keeps its
additional exact phrase and scientific/release-cluster checks.

Adding, removing, or relocating a governed diagram is therefore an explicit
release-contract change. It must update the census and its adversarial controls
rather than silently changing what the renderer sees.

### Render every governed source

`scripts/ci/render-readme-architecture.sh` extracts the exact seven-block census
and renders every block with the integrity-locked Mermaid CLI 11.16.0 through
the bounded Chrome 150 major. Every render must produce a nonempty image with
the expected file signature.

The release validator reads without universal-newline translation, binds the
renderer's complete exact bytes, and retains four additional release-script
known-bads that weaken the expected count, stop after the README, remove the
per-image signature assertion, or substitute a CRLF byte sequence. A renderer
change must therefore update this decision, its exact-byte binding, and the
closed mutation matrix together.

The release evidence keeps the README SVG and the complete render log. The
other six images are ephemeral diagnostics: their successful named render is
retained in `mermaid.log`, while exact source bytes remain canonical in Git.
This preserves the existing release-manifest profile rather than treating
generated images as architecture authority.

The source gate rejects the current Mermaid constructs that can request
browser-loaded resources, including relative image assets and explicit local,
embedded, or network URI schemes. This is a bounded source-admission control,
not a browser egress sandbox or proof against an unknown renderer defect.

### Keep semantic review separate

Parsing and rendering prove only that the exact source is accepted by the
bounded renderer. They do not prove that:

- an arrow represents the right causal, authority, or dependency relation;
- a label uses the accepted scientific or policy taxonomy;
- the result is accessible, legible at every viewport, or accepted product
  design;
- a proposed component exists; or
- the architecture is correct, complete, independently reviewed, or accepted.

Semantic review remains required against the contracts named by each diagram.
Visual inspection remains required when diagram structure or labels change.
Daniel's protected UI/UX lane remains separate.

## Consequences

- All seven current diagrams now share one exact inventory and renderer gate.
- Future diagram drift fails locally and in fresh-clone release rehearsal
  instead of surviving behind a green README-only render.
- The render stage is slower because it launches the bounded renderer for every
  block; this cost is accepted for the small closed census.
- Generated non-README images remain disposable diagnostics, while Git source
  and the named render log remain the retained release evidence.
- No diagram, render, validator, review, or consensus grants Gate A, runtime,
  release, product identity, or scientific authority.
