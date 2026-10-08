# SequenceCompressor

Semantic sequence run compiler.

Batch: A

## Why it is GenLayer-native

Consensus labels every ordered entry from a closed alphabet; deterministic run-length encoding creates assignable contiguous work segments.

The LLM handles only the bounded semantic step. Deterministic contract code owns
the reusable algorithm, state transitions, access control, tie-breaking, and
views. One deployment supports many caller-keyed records; it is not tied to the
StudioNet fixture or one organization.

## Public interface

Write methods: `compile_sequence`, `assign_segment`, `acknowledge_segment`, `seal_sequence`

View methods: `get_compilation`, `get_segment`, `segment_total`

## First-time StudioNet walkthrough

1. Open the [deployed contract](https://explorer-studio.genlayer.com/address/0x6c8d83FdB74e82E66B5bBf9E48931F906B062457) in GenLayer Studio and connect a StudioNet wallet. All inputs are public; use example text rather than private plans.
2. Call `compile_sequence` with a key not previously used by that wallet, for example `assembly-run`; `labels_json` = `["Preparation","Execution","Verification"]`; `entries_json` = `["Confirm the public work boundary","Stage the marked equipment","Install the first component","Install the second component","Inspect the completed assembly"]`; and `classification_policy` = `Classify each ordered entry by its operational phase without changing or reordering any entry.` The two JSON values are strings containing valid JSON, not separate array arguments.
3. After the AI transaction finalizes, use the returned `compilation_id` (or lowercase wallet address followed by `:ASSEMBLY-RUN`) with `get_compilation`. Its `entry_labels` list shows the consensus labels and `segment_count` shows the run-length-compressed segment total. Call `get_segment(compilation_id, 0)` to inspect the first segment.
4. To test the optional assignment lifecycle, the owner calls `assign_segment` once per segment with a different operator wallet for each. Each operator uses its own wallet to call `acknowledge_segment`. The owner then calls `seal_sequence`. An acknowledgement is a wallet statement, not independent proof that physical work was completed. An unresponsive operator currently prevents sealing; choose operators you trust for this test.

## Verification

```text
pip install -r requirements.txt
genvm-lint check contracts/sequence_compressor.py
genvm-lint typecheck contracts/sequence_compressor.py --strict
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5
gltest tests/integration -q --network localnet
```

The live smoke test is opt-in and requires a repository-specific wallet bundle
outside the repository. It waits for finalized receipts, reads `LATEST_FINAL`,
retrieves deployed source and schema from StudioNet, and fails unless the source
bytes exactly match this repository.

StudioNet contract: https://explorer-studio.genlayer.com/address/0x6c8d83FdB74e82E66B5bBf9E48931F906B062457

See `AUDIT.md`, `ORIGINALITY.md`, `SOURCE_POLICY.md`, `SECURITY.md`,
`SUBMISSION.md`, and `deployments/studionet.json` for the final evidence.

## Boundary

The contract moves no funds and does not establish identity, ownership,
professional authority, source authenticity, physical truth, or legal effect.
All caller inputs and calldata are public. Off-chain clients own authentication,
privacy, source curation, indexing, and the decision to rely on a result.
