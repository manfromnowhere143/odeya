# First Vertical Slice: Proof-Mission Truth Compiler

Status: architecture fixture specification; selected, not ingested or implemented.

The portfolio-wide requirement IDs exercised by this slice are tracked in [Proof-Mission Requirements Traceability](PROOF_MISSION_REQUIREMENTS_TRACEABILITY.md).

Decision date: 2026-07-15. Source repositories were inspected read-only. No source mission, remote, provider, simulator, account, or external system was changed.

## Verdict

The first Odeya slice should be an **offline proof-mission truth compiler**, not an agent loop and not a new experiment. It must ingest exact, rights-admitted bytes from three immutable source commits and produce five distinguishable dispositions:

1. a valid bounded positive from Sentinel;
2. a valid measured Sentinel transfer result whose interval crosses zero and compiles to `inconclusive` rather than equivalence;
3. an invalid protocol and a replay discrepancy from Telos;
4. a visible correction from Telos; and
5. blocked/refused physical evidence from Inbar.

This is the smallest real slice that challenges Odeya's claim algebra instead of merely demonstrating a happy-path workflow. Sentinel is the primary scientific replay. Telos supplies adversarial verifier and correction fixtures. Inbar supplies evidence-admission, rights, physical-authority, and refusal fixtures. None of the source repositories is copied until the rights gate and the final fixture manifest are accepted.

## Exact source observation

Observed at `2026-07-15T21:27:38+03:00`:

| Mission | Repository | Selected commit | Branch at observation | Working-tree state |
|---|---|---|---|---|
| Sentinel | `/Users/danielwahnich/workspace/sentinel` | `542b432be3f3adb547d9649b01c8fa208c5952e9` | `master` | clean: 0 status entries |
| Telos | `/Users/danielwahnich/workspace/telos` | `fc955a5caf20dc1ed53ef71b83797ba75315afb5` | `agent/iter200-corrected-denominator-result` | active dirty work: 84 tracked modifications and 45 untracked paths |
| Inbar | `/Users/danielwahnich/workspace/fieldtrue` | `b3cd7570a7b86e918e4831c3b57f7d4ca213d026` | `main` | active dirty work: 12 tracked modifications and 4 untracked paths |

Only the named commits are candidates. Telos and Inbar working-tree bytes are explicitly outside the fixture. A later source commit is a different fixture version and cannot silently replace this one.

Recheck at `2026-07-15T21:37:51+03:00`: all three selected commits and branches were unchanged; Sentinel remained clean; Telos remained at 84 tracked modifications plus 45 untracked paths; Inbar had advanced from 12 to 13 tracked modifications while retaining 4 untracked paths. That working-tree drift is evidence that a live checkout cannot be the fixture boundary. It does not alter the selected Inbar commit or admit either version of the dirty files.

## Fixture set

| Fixture ID | Source | Purpose | Required Odeya disposition |
|---|---|---|---|
| `S-POS-001` | Sentinel `full14_power` | paired in-domain simulation result with one missing planned episode | valid measurement; bounded supported simulation claim |
| `S-NULL-001` | Sentinel iteration 48 | frozen-parameter HUGSIM transfer test | valid measurement; source verdict `TRANSFER_NULL`; Odeya outcome `inconclusive`; no equivalence, transfer-benefit, or safety claim |
| `T-CORR-192` | Telos iteration 192 | world-contact correction of the obsolete 40-row framing | superseded claim corrected; core 40/40 facts retained |
| `T-REPLAY-192` | Telos iteration 192 | committed audit does not reproduce its own terminal `pass` after publication | verification discrepancy; sealing blocked |
| `T-INVALID-197` | Telos iteration 197 | candidate-diff-derived locators and gold adjudication contradict the frozen protocol | protocol invalid; measurements exploratory only, not a scientific null |
| `T-INVALID-201` | Telos iteration 201 | repeated locator exposure, non-independent controls, and incomplete response evidence | protocol invalid/limited; no detector-performance claim eligible |
| `I-BLOCK-000` | Inbar iteration 000 | exact, signed corpus-readiness record | `BLOCKED_EVIDENCE`; parser/integrity passes do not authorize training |
| `I-REFUSE-001` | Inbar iteration 001 | public-substrate rejection and bootstrap authority | source-role decision plus operational blocker; no fabricated scientific result |
| `I-RIGHTS-001` | Inbar rights records | unknown NASA ADAPT terms and no raw redistribution | rights blocked for raw bytes/public release |

## Immutable import contract

The fixture pack is not a directory copy. Before any ingestion, produce an import manifest with one row per selected Git blob containing:

- logical source repository and selected commit;
- repository object format and Git tree object;
- repository-relative path encoded as UTF-8 bytes;
- Git mode, Git blob object ID, raw byte count, and SHA-256 over raw blob bytes;
- media type and parser profile;
- rights decision and redistribution class;
- source role: protocol, analyzer, evidence, result, receipt, claim surface, or known-bad control;
- exposure class and sealed-truth restrictions;
- expected semantic outcome, independently authored outside the source artifact.

Paths are sorted by raw UTF-8 bytes. Duplicate normalized paths, symlinks, submodules, unsupported modes, absolute paths, traversal segments, invalid UTF-8, missing objects, or a byte-count/hash mismatch fail import. Git tree IDs are source anchors, not Odeya's final cross-runtime artifact IDs. The final aggregate root remains blocked on the accepted canonicalization profile in `STANDARDS_PROFILE.md`; no provisional root may later be reinterpreted.

Read bytes with `git cat-file blob <blob-id>` or an equivalent object-database API. `git archive` may transport an already-manifested selection into an isolated scratch directory, but tar metadata is never artifact identity and extraction must reject traversal, links, devices, and duplicate destinations.

## Rights gate

Scientific validity never grants usage or publication rights.

| Source | Observed rights state | Fixture policy |
|---|---|---|
| Sentinel | no repository license file was committed; evidence includes third-party simulator, model, dataset, and NVIDIA container material | default deny copying and redistribution until Daniel issues a private-use source grant and every selected third-party-derived artifact receives a disposition; no public release |
| Telos | root repository carries Apache-2.0, but SWE-bench task text, patches, logs, and upstream-project content have separate provenance | Apache-2.0 covers only what its licensor can license; begin with project-authored manifests/reports/scripts, perform per-artifact third-party review before copying diffs or execution logs, and do not redistribute the benchmark fixture by implication |
| Inbar | `IP_NOTICE.md` says all rights reserved; NASA ADAPT landing-page terms were recorded as unspecified; project policy forbids raw-byte redistribution | require Daniel's explicit private-use grant; admit only project-generated metadata/proof initially; raw NASA bytes remain absent and forbidden; no public fixture |

Until these decisions are retained as typed receipts, fixture status is `selected_rights_pending`, not `ready`.

## Sentinel primary replay

### `S-POS-001`: full14 power result

Commit: `542b432be3f3adb547d9649b01c8fa208c5952e9`.

Required paths:

- `experiments/full14_power/HYPOTHESIS.md`
- `experiments/full14_power/RESULT.md`
- `experiments/full14_power/analyze_power14.py`
- `experiments/full14_power/merge_power14_logs.py`
- `experiments/full14_power/proof/sentinel-power14-merged.log`
- `experiments/full14_power/proof/p14-runs.tar.gz`
- `experiments/full14_power/proof/analysis_output.txt`
- `experiments/full14_benchmark/proof/sentinel-full14.log`
- `experiments/iter15_latch_release/proof/sentinel-iter15.log`

Source tree anchors:

- `experiments/full14_power`: `f174e8d7b0499490d7c1ceeb260dcf4a200e56a4`
- `experiments/full14_power/proof`: `1ff3915c4b3190b089472bfd16d5ce784a951f07`

Load-bearing SHA-256 values:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `HYPOTHESIS.md` | 3,671 | `8b9421644b8f6382c4a81557ede868c1ff9c435e7786b4676a61eb360e67eea4` |
| `RESULT.md` | 5,055 | `fb62421bb106649e0f53cada921e26d5265a6452e148fbc97cd271bed3369a78` |
| `analyze_power14.py` | 5,701 | `fd5f4ab38014bd225b7164cbdf1f11fc5170921dff930a59b481d7d7e930cfe2` |
| `sentinel-power14-merged.log` | 6,972,733 | `c2b40bcd40b5315cfec10bdced69d09220917861a35af4c396de76766fcd02e0` |
| `p14-runs.tar.gz` | 16,064,668 | `8a5e821f806e998e3b47def7a79c6e3b831b22d070a228446df22d1e0078edbb` |
| `analysis_output.txt` | 1,896 | `3f8a022871eb0cca9653cc58098c1749dc42660672f761fe1853ae6dbe3f4d68` |
| full14 comparator log | 2,499,603 | `de2e582bb0c386af4774443322d1f51721fd2a494f6969aad9b8285e8d336ce6` |
| iteration-15 comparator log | 1,287,103 | `f53987633dfce2f91e0f02f6695af040c4e1f9ee14c7ff5e6f83460ee2687c88` |

Offline replay after safe extraction of `p14-runs.tar.gz` to `<runs-root>`:

```bash
python3 experiments/full14_power/analyze_power14.py \
  experiments/full14_power/proof/sentinel-power14-merged.log \
  <runs-root> \
  experiments/full14_benchmark/proof/sentinel-full14.log \
  experiments/iter15_latch_release/proof/sentinel-iter15.log \
  I15PAIR released
```

Expected facts:

- H-P0 exact first-six replay gate passes for both arms on every pair;
- 799 of 800 planned episodes are measured; `off/side-0921` has 19 rather than 20 and may not be silently imputed;
- pooled NCAP score `2.12` versus `2.91`;
- paired delta `+0.783`, 95% bootstrap interval `[+0.605, +0.928]`;
- safe-progress delta `-0.032`, interval `[-0.127, +0.065]`;
- the frontal/0346 regression and all stated limitations remain visible.

Eligible claim: the released union improved the pinned NeuroNCAP simulation metric under this exact protocol. Ineligible: deployment safety, real-world performance, general autonomous-driving safety, exact zero deployment cost, or broad transfer.

The replay was diagnostically checked on the observed machine: output was byte-identical to `analysis_output.txt`; analyzer time was `0.57 s`, maximum resident set size `15,204,352` bytes; the archive contains 2,399 files and expands to approximately 153,252 KiB. These are observations, not the accepted cross-machine resource profile.

### `S-NULL-001`: HUGSIM source-reported transfer null

Commit: `542b432be3f3adb547d9649b01c8fa208c5952e9`.

Required scope: the complete `experiments/iter48_hugsim_transfer_gate` tree, with special reliance on the hypothesis, analyzer, committed monitor patch, receipts, all 104 episode proof directories, report, paired table, and command receipt.

Source tree anchors:

- experiment tree: `510547e6fa3cdd212f5f0960f7356915f81b53e3`
- `proof-stage2`: `1655e7aef616a6e5961c376bfbd1d226f31ef174`

Load-bearing SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| `HYPOTHESIS.md` | `eeb1ccb5408acfd1fbecae6387d161da095adff64e48cf818be1e44f52569b24` |
| `RESULT.md` | `6b51089dd40f3c3a8576687baf5b6990ae6bc91d55f33979a86b18741706ec10` |
| `analyze_transfer.py` | `f8dca700963e521deec658f00ddb9d186d0833aaaafe9f4aa1276e421c830de8` |
| frozen monitor patch | `6b39fd79d00c7bdb937c6d240fbc4648661b235f1a3024912d62874937146c5c` |
| `receipts.json` | `4380823d8a3d2f7a3674b8cf74cecc3afab1578f40e872318427608baf9a9191` |
| `transfer_report.json` | `1213f21c6132b7d338f16a7a0d9ab554da8721ae52c50984269ac0b30702fae1` |
| `transfer_pairs.md` | `c8f313c1a340fe06f0d946631dba1bd2f8fb0748b7d374f8a9b0acd016484c17` |

The receipts additionally bind HUGSIM commit `62c690d39fd90020e68a196bd8bcc1c4d4191f2e`, UniAD_SIM commit `5fb279e39912a5ac7f58e00d56b065cadcd0a749`, checkpoint SHA-256 `0ad0c2f5dc9788a41c313305779ea49346aeb742d1f6bb5ad25c46f9beffc990`, shim SHA-256 `5bf69a1187478c52d49792d5871bd5732c6dd431ecd1f44b5e391f7adb80682c`, and image ID `f73ef3884063`. The tag-like image ID is not a complete OCI digest and must be recorded as an upstream reproducibility limitation.

Replay command:

```bash
python3 experiments/iter48_hugsim_transfer_gate/analyze_transfer.py \
  --episodes experiments/iter48_hugsim_transfer_gate/proof-stage2/episodes \
  --receipts experiments/iter48_hugsim_transfer_gate/proof-stage2/receipts.json \
  --out <scratch>/transfer_report.json \
  --markdown-out <scratch>/transfer_pairs.md
```

Expected facts:

- F1 retuning void does not fire; all seven parameters match;
- 104/104 episodes complete, zero retries, all required logs present;
- mean paired HD delta `-0.0166`, clustered 95% interval `[-0.055132299414088405, +0.02550941049137224]`;
- median delta `+0.0032`, interval `[-0.046747003572746075, +0.017822004355771182]`;
- the source-registered verdict is `TRANSFER_NULL` because the primary interval includes zero;
- Odeya records that source vocabulary but compiles the scientific outcome to `inconclusive`: interval inclusion of zero without a frozen equivalence/null region is not an equivalence result or affirmative `null_result`;
- activity of the mechanism does not become evidence of benefit: 37/52 ON episodes intervened, yet no measurable mean improvement was established;
- no NeuroNCAP equivalence, deployment, production, safety, robustness, or benchmark-ranking claim is eligible.

The replay was diagnostically byte-identical under Python `3.14.2` and NumPy `2.4.2`; analyzer time was `0.51 s` with `110,067,712` bytes maximum resident set size. Sentinel does not pin the analyzer's NumPy dependency, so the final fixture must freeze an environment image digest and wheel hashes and reproduce on a second clean platform before acceptance.

## Telos adversarial and correction fixtures

Commit: `fc955a5caf20dc1ed53ef71b83797ba75315afb5`. The active dirty correction work is excluded.

### `T-CORR-192`: core correction

Select:

- `benchmarks/reward_hack_benchmark_v1/reward_hack_benchmark_v1.jsonl`
- the iteration-152 generator and retained results/tarball;
- iteration-154 and iteration-155 official-log tarballs;
- `scripts/run_benchmark_construct_validity_audit.py`;
- the complete `experiments/iter192_reward_hack_benchmark_construct_validity_audit` tree;
- `benchmarks/certified_resolved_reward_hack_v2/manifest.json` as the later, separate 22-row context.

Tree anchor for iteration 192: `1894b48d4d6b97e0e09b9bbf453731e8cc6ac630`.

Key SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| v1 40-row JSONL | `b83bf0febd19269881e5fe214f8457a3ca052e65960f58ad4393da3fe7a21159` |
| generator | `2c378abe87b67fbef825c7429bbe1114b73543188b7aa0eca088bdf5620027cd` |
| iteration-152 official reports | `ea6d49357aaa4f00183f46b577f3570cc11e47e85295ea0c55badaed6ad71492` |
| iteration-154 official reports | `35c7ac63e62785bd92d4f9e7ce47a98b74d6ec673e9e8884ff4196be50cc19d0` |
| iteration-155 official reports | `97770eb252d525cb97d0123c413f947341ecb9328b7c106b9b1786fd85941515` |
| iteration-192 audit script | `398cd62702aaacb3699d85e64f36ca14c3d33ee9dc79d44280d6831f5c1f4790` |
| iteration-192 official verdict | `bcb6d2aad39561b680765f699b4d38cf18156cb779da24fca488bf377cb2cf3c` |
| iteration-192 committed baseline scan | `a2506020e6f4e044e35dc01a830c0926b292e6c6a0985ef8d589e626fc407fb0` |
| iteration-192 core audit report as published | `d08860d8eb8d4f9b6289873e26f931b44185073dd7b72ea04a61238bcfaf1c96` |
| iteration-192 terminal receipt | `4a6b045142b8e246f250f33c982069edb1c97b2957d8663bfb37c06ec45bf356` |
| later v2 22-row manifest | `bfca5dc7d45c59586f993e8c1276da5037de203125486b04f081e1ea664970f3` |

Expected core facts from the explicit evidence allowlist:

- 40/40 v1 rows match a committed official report;
- 40/40 have `resolved == false` and at least one failed `PASS_TO_PASS` item;
- the old claim that v1 contains confirmed reward hacks is contradicted and corrected;
- the historical `17/40` panel arithmetic remains a measurement of review on suite-rejected wrong patches, not a reward-hack benchmark result;
- later v2 contains 22 separately constructed and gold-differentially witnessed cases across 8 repositories, with its own narrow claim boundary.

### `T-REPLAY-192`: self-referential audit failure

Running the committed audit in a clean export of the selected commit is expected to exit nonzero:

```bash
python3 scripts/run_benchmark_construct_validity_audit.py
```

Diagnostic replay found the stable core counts above, but `experiments/iter192_reward_hack_benchmark_construct_validity_audit/proof/existing_baseline_scan.json` changed and the generated `proof/audit_report.json` became `fail`: the script scans a mutable repository-wide Markdown universe, so after the correction is published it finds correction surfaces reporting the baseline. It found 2 hits at correction commit `c681785efa8f0bf420eb52b8a3bb634957cc040e` and 3 hits at selected commit `fc955a5caf20dc1ed53ef71b83797ba75315afb5`, rather than the committed scan's 0. The committed terminal receipt is `proof/valid/receipt_benchmark_construct_validity_audit.json`. At the selected commit the audit ran in `0.30 s` and `25,772,032` bytes maximum resident set size.

Required Odeya behavior:

- retain the core 40/40 evidence separately from the time-indexed absence claim;
- record a verification discrepancy between the committed `pass` receipt and clean-commit replay;
- reject the mutable whole-repository scan as an unfrozen input set;
- block sealing until a pre-publication corpus root or explicit exclusion-safe input manifest is supplied;
- never erase the correction merely because one part of its historical audit is not replay-complete.

This fixture is more valuable than a synthetic crash: it proves that a signed or committed receipt cannot substitute for reconstructing the exact evidence universe.

### `T-INVALID-197`: protocol deviation

Tree anchor: `4109c50aded5de823ee3b3de82b5ce7856859e10`.

Key SHA-256 values:

- frozen hypothesis: `1efc89ca5e423aa82cc8beeffb738743d17fecf7334c967e741080651f6747b2`
- generator: `cf39876e04cbcf279b933a7ead944f0f9a82cbbd763cf262dcc43f23a23207dc`
- adjudicator: `6a47c12efa8c5a12f6a070ed7f0c9fe8badb320ee5cc2d029a9bced70bbcbfba`
- phase-A summary: `b4148a5d62f46e2fb81a44238c08f0a1a4199b2bf2074fa90e2fc764867209f6`
- published audit report: `2a1ef57ddaeb8751ef29fe999748934eb75f0353416668d989f2cc7785829b34`
- receipt: `cd0c9215bbbfdd1caa2431430819c608716f2daf5813b8a198403dc46254eef1`

The hypothesis says property synthesis sees only public task text and the visible test, never the candidate diff, and that soundness comes from a visible-test anchor. The committed generator reads each candidate variant patch, derives `src_file` and `func` from its diff, and inserts both into the prompt. The committed adjudicator defines soundness as `prop(gold) == PROP_PASS`. The ten promised independent gold-control decisions were not evaluated as a detector control set; gold execution was used as the inclusion/soundness filter. Moreover, the pre-output hypothesis at commit `336c484200289d27ee1361f5fbd1e85e51494fa9` contains no `>=5` catch threshold; that threshold appears in the adjudicator committed with generated properties at `f62aea8c19b109f9488accfb4b58c3f03d6d7a6f`.

Expected disposition: `validity = invalid`, with `4/10` and related comparisons retained only as exploratory diagnostics. The engine must not compile the source's `null` status into a valid scientific null, specificity claim, or complementarity claim.

### `T-INVALID-201`: repeated exposure and incomplete evidence

Tree anchor: `bd69899e28fb9bf7b2e17c8944d0d4899eba3e44`.

Key SHA-256 values:

- hypothesis: `da2bb191e91127ebe952609812253b722c1d18509ea612ba0401f18cb89dff78`
- oracle generator: `fdb2ecdd5b95e9fcbc9e513352ad9d4145edddb399f004b61886d35dc1033086`
- adjudicator: `33a2377b4ea0da8045e9ff68213e00cb4490d8866c59ec09120ce7e9496fe237`
- published audit report: `260a6456a3e44f339a88e0a437fc748ee4a63e0b3ab0a47490baf23ef57ce9d7`
- receipt: `34f65a9604cf31403bac9b2c69766b80b1b3f7cca3bd43ff6289b0f36657d618`

The 22-row extension repeats the diff-derived source/function locator exposure while claiming no-diff property generation. Gold execution is explicitly the property soundness gate, so it is a locator-assisted, gold-validated pipeline rather than a fully independent gold-free detector. The property path has no independent correct-variant false-positive evaluation. Judge evidence retains parsed labels and nondecision markers, not raw response text; unparseable rows must remain missing/nondecisions and receive lower/upper sensitivity bounds rather than silently becoming `legitimate` or `reward_hack`.

Expected disposition: invalid for the claimed no-diff protocol and ineligible as a settled detector-performance result. The descriptive counts may remain quarantined diagnostics. The observed containment of the property catches within the judge catch set does not repair the validity failure.

## Inbar blocked, refusal, and physical-evidence fixtures

Commit: `b3cd7570a7b86e918e4831c3b57f7d4ca213d026`. Active working-tree changes are excluded.

### `I-BLOCK-000`: exact historical blocked result

Select the complete `experiments/iter000_nasa_adapt_corpus_readiness` tree.

Tree anchors:

- experiment: `9ea378a1c718b680b5983574ce6908c06ff46550`
- attempt-001 proof: `5ad82ba61c522fc3e292ab7ceed9f7085b556673`

The committed `run_manifest.json` already provides a per-artifact hash map. Load-bearing SHA-256 values include:

| Artifact | SHA-256 |
|---|---|
| `HYPOTHESIS.md` | `b5f18e02b54a137aa966ce70a3f89f2616167992cc2583508f2b3b0403d205d5` |
| `RESULT.md` | `28e6448047902e395c08c0fc51a432e88958a8c06adb34c619b7c304bbdb7df9` |
| `readiness_report.json` | `15a680d3c6b8f845277e5a6ade562fa542e37c2e555a3ff1771ad3ec50566b86` |
| `coverage.json` | `569e45683e0d0667722d0aa4c6a748d56a6e2faddce376e8bfd6e23191e96c1c` |
| `dataset_lock.json` | `884c1ff5daf60323437ad1d16efb01acb3e769ce71eade62fcde966bfe0a4367` |
| `ingestion_receipt.json` | `d549282400fae1d18a74f0a54106a9427de5cc8841c8291f16d63c0bb3442c44` |
| model-visible evidence manifest | `111f068f08d0e09901c10cce35c877fb78a58ec95899911293d9347ecbec2d5c` |
| sealed truth manifest | `bb9e80e3f72f6a2d54d68c9dcf6daf9aff9a3d7e545389505f625e7af85174fb` |

Expected outcome:

- source integrity, exact parser join (`16/16`), and truth separation pass;
- minimum independently identified mechanisms `0/30`;
- pre-outcome ambiguity sets `0/30`;
- independently reviewed discriminating actions `0/30`;
- one hardware family and one identity, insufficient for transfer;
- 16 incidents have two operational channels but the requirement is 30;
- terminal verdict `BLOCKED_EVIDENCE`;
- authorized successor is further independently verified physical acquisition and reviewed safe actions;
- training, active diagnosis, recovery, safety, transfer, product, and value claims remain forbidden.

Do not rerun the consumed historical authority or attempt to reconstruct absent raw NASA bytes. This fixture verifies the committed proof graph and recomputes admissibility from retained derived artifacts. Full experiment reproduction is intentionally unavailable because raw bytes are uncommitted and their terms remain unresolved; that limitation must be visible.

### `I-REFUSE-001`: prospective physical admission

Select:

- `experiments/iter001_physical_causal_evidence_acquisition/HYPOTHESIS.md`
- `experiments/iter001_physical_causal_evidence_acquisition/AMENDMENT_001.md`
- `docs/research/ITER001_SOURCE_ROLE_AUDIT.md`
- `protocol/acquisition/iter001_contract.json`
- `mission/contract.json`, `mission/loop.json`, and `claims/registry.jsonl`
- `DATA_LICENSES.md` and `IP_NOTICE.md`

Key SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| iteration-001 hypothesis | `47a1920b1b5326601c7404d17a6aac0df3309c2433fa76f56f0dffedf2511ad8` |
| amendment | `9278eb33ef5a837c0ae043112f2fb041df4faa39cf34d26787a47f2326bf360c` |
| source-role audit | `7f55c37d88bd06e7696b8f1820bc462ad2794aef2e239d5042f4725494a18d5d` |
| mission contract | `97d0b2cf5281f386ab0986b7311dd83d8c36b246a6db5edd4b04b17a6b21d8f6` |
| mission loop | `97274381a035513159927a17f08cdafa04a23b2b3a6b7f1f04daa7e9c1826cfe` |
| claim registry | `e61cc7874e56d3ed344d928922aee6aa02a7a9fc2d74281545e0c8641410b2a5` |
| data-rights record | `fb6de9bc20e172a814026c0085628492120b3fbd116d4669fd8f3772cc30142a` |
| IP notice | `089170d0f6d8e4ba7690b092973e1acadd0f72bf9a1c3f686fadcc9fd2f2ab8c` |

Expected behavior:

- preserve `KILL_PUBLIC_SUBSTRATE` as a committed source-role/governance decision, not pretend that a complete prospective experiment ran;
- represent current admission as blocked because the acquisition authority is `bootstrap`, the control-suite and validator Git-blob fields contain zero placeholders, no production receipt exists, and no pilot verdict exists;
- require 30 complete physical root incidents, 3 system families, 6 hardware identities, 3 fault families, independent mechanism/safety/execution/outcome authority, clocks, rights, costs, and conjunctive same-incident completeness;
- keep simulator/control sources separate from physical admission counts;
- compile only the offline/shadow dossier and human-reviewable test-recommendation wedge;
- refuse commands, training, physical action, safety, recovery, transfer, diagnosis, product, or value claims.

This is the physical-science refusal test: absence of qualifying evidence must stop the engine at admission, not encourage a model to fill the gaps.

## Execution order for the slice

The future implementation of this fixture, after Gate A and explicit authorization, must execute in this order:

1. observe the source commit and reject any moving ref as identity;
2. enumerate selected Git objects and build the raw-byte manifest;
3. decide rights per object before content exposure;
4. quarantine and scan admitted bytes; never execute source code during ingestion;
5. compile source protocols and expected outcomes into distinct Odeya objects;
6. run static protocol-exposure checks before scientific analyzers;
7. replay `S-POS-001` and `S-NULL-001` in isolated, network-denied environments;
8. run the Telos explicit-input correction audit and the deliberate clean-commit replay discrepancy;
9. validate the Inbar historical proof without regenerating consumed authority;
10. adjudicate each fixture independently from its source-authored prose;
11. compile bounded claims and forbidden wording;
12. rebuild projections from events and compare exact semantic state;
13. stop before publication, provider access, external write, simulator launch, training, or physical action.

One writer owns each fixture aggregate. Parallel analyzers may produce immutable candidate verification records, but the pure adjudicator settles only after all required records and discrepancies are present.

## Resource envelope

Candidate ceiling for one complete offline pass:

| Resource | Ceiling |
|---|---:|
| network egress/ingress after source export | `0` |
| provider/model calls | `0` |
| GPU seconds | `0` |
| cloud jobs | `0` |
| external writes or publication actions | `0` |
| CPU time | `60 s` per replay environment |
| elapsed time | `120 s` per replay environment |
| peak resident memory | `512 MiB` |
| admitted compressed/source bytes | `64 MiB` |
| scratch bytes | `512 MiB` |
| processes | `4` |

The ceiling is deliberately above observed local replay costs but small enough that a dependency explosion, hidden model call, simulator launch, or uncontrolled archive expansion fails. Two independent clean replays are required; their resource records remain separate. Unknown measurements remain unknown and fail the resource-complete acceptance row rather than becoming zero.

## Acceptance rule

The slice is accepted only if all conditions hold:

1. every selected source commit exists locally and every manifest row matches mode, blob ID, byte count, and SHA-256;
2. active Telos/Inbar working-tree files contribute zero bytes;
3. every admitted artifact has a retained rights decision; unknown rights block rather than warn;
4. two clean, isolated replay profiles independently reproduce the accepted Sentinel outputs and exact semantic values;
5. planned `800` and measured `799` remain distinct;
6. the Sentinel positive stays simulation-bounded and its safe-progress interval is not rendered as proof of zero cost;
7. the HUGSIM source label `TRANSFER_NULL` remains visible, while the interval-crossing-zero result compiles to `inconclusive` and never becomes a positive, negative, equivalence, or affirmative `null_result` claim;
8. Telos iteration 192 core facts survive while its clean-commit receipt discrepancy blocks replay-complete sealing;
9. Telos iterations 197 and 201 settle as invalid for their claimed protocols, not as valid null/pass results;
10. unparseable or absent detector outcomes remain missing and receive sensitivity bounds;
11. Inbar iteration 000 settles blocked and iteration 001 refuses unsupported progression;
12. `bootstrap`, placeholder hashes, a signature, a green test suite, or a committed receipt never becomes scientific authority by itself;
13. invalid, blocked, null, supported, corrected, and discrepancy states are distinguishable in the canonical view and every projection;
14. claim compilation emits every required limitation and zero forbidden claims;
15. deletion of projections followed by event replay reconstructs identical state;
16. no source repository, network destination, external system, or publication surface is modified.

Any failed condition rejects the slice. There is no partial score that can compensate for a failed rights, protocol-validity, or authority gate.

## Required falsifier matrix

At minimum, the fixture suite must demonstrate rejection of these mutations:

- one source byte, blob ID, byte count, path, or tree anchor changed;
- a dirty working-tree artifact substituted for its committed version;
- duplicate or traversal path introduced during archive extraction;
- one full14 episode omitted, duplicated, or imputed as zero;
- the 799 measured episodes described as 800 observations;
- OFF/ON arms swapped or seed pairing broken;
- paired bootstrap replaced with unpaired or wrong clustering;
- HUGSIM parameter, seed, draw count, scenario set, or patch changed;
- HUGSIM missing episode classified as a scientific transfer null;
- interval-crossing-zero rendered as evidence of equivalence or benefit;
- Telos committed `pass` receipt trusted despite nonreproducing clean-commit replay;
- repository-wide mutable scan accepted as a frozen analysis input;
- candidate-diff-derived locator omitted from the exposure manifest;
- gold validation described as a visible-test-only or fully gold-free protocol;
- post-generation threshold treated as preregistered;
- unparseable judge output coerced to either class;
- Inbar's parser/integrity passes treated as corpus admission;
- 16 telemetry incidents inflated into 30 by counting windows, channels, or branches;
- simulator branches counted as physical incidents;
- bootstrap authority or all-zero placeholder digest treated as production authority;
- unknown rights, resource use, clock alignment, or physical evidence converted to zero/pass;
- a recommendation treated as executed action or a command as realized actuation;
- a proposer or model accepted as sole safety, execution, truth, or outcome authority;
- any public, safety, deployment, value, state-of-the-art, or autonomous-research claim emitted.

Every known-bad fixture must fail for the intended reason. A generic parser error is not proof that the scientific gate works.

## What this slice is sufficient to establish

If accepted, this slice would establish that Odeya's pure contracts can faithfully represent and adjudicate real research evidence across the hardest founding distinctions: positive versus null, planned versus observed, valid versus invalid, evidence versus receipt, correction versus erasure, blocked versus negative, simulation versus physical evidence, and recommendation versus authority. It would also prove a cheap, deterministic foundation for the later Sentinel adapter.

## What it cannot establish

This slice cannot establish that Odeya autonomously performs research, chooses good hypotheses, plans valuable experiments, scales multi-agent work, survives concurrent failures, isolates hostile code in production, controls external effects, improves over strong human or model baselines, performs causal diagnosis, operates physical systems, or creates customer value. Sentinel remains simulation evidence; Telos uses constructed software cases and contains protocol defects; Inbar has no qualifying prospective physical corpus. The slice also cannot close rights, independent statistical/domain/security review, the event catalog, canonicalization profile, authority race semantics, or publication settlement.

Therefore this document closes **fixture selection**, not Gate A and not implementation authorization.
