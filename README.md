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

Write methods: `compile_sequence`, `assign_segment`, `reassign_segment`, `acknowledge_segment`, `seal_sequence`

View methods: `get_compilation`, `get_segment`, `segment_total`

## First-time StudioNet walkthrough

1. Open the [current deployed contract](https://explorer-studio.genlayer.com/address/0x5c72e9c076e00f0ECB1F953dF1883C3b565789DC) in GenLayer Studio and connect a StudioNet wallet. All inputs are public; use example text rather than private plans.
2. Call `compile_sequence` with a key not previously used by that wallet, for example `assembly-run`; `labels_json` = `["Preparation","Execution","Verification"]`; `entries_json` = `["Confirm the public work boundary","Stage the marked equipment","Install the first component","Install the second component","Inspect the completed assembly"]`; and `classification_policy` = `Classify each ordered entry by its operational phase without changing or reordering any entry.` The two JSON values are strings containing valid JSON, not separate array arguments.
3. After the AI transaction finalizes, use the returned `compilation_id` (or lowercase wallet address followed by `:ASSEMBLY-RUN`) with `get_compilation`. Its `entry_labels` list shows the consensus labels and `segment_count` shows the run-length-compressed segment total. Call `get_segment(compilation_id, 0)` to inspect the first segment.
4. To test the optional assignment lifecycle, the owner calls `assign_segment` once per segment with a different nonzero operator wallet for each. If an operator is unavailable before acknowledging, the owner may call `reassign_segment` with a different unused wallet; the old wallet then loses acknowledgement authority. Each current operator calls `acknowledge_segment` with its own wallet. The owner calls `seal_sequence` only after every segment is acknowledged. An acknowledgement is a wallet statement, not independent proof that physical work was completed.

## Verification

```text
pip install -r requirements.txt
genvm-lint check contracts/sequence_compressor.py
genvm-lint typecheck contracts/sequence_compressor.py --strict
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5
gltest tests/integration -q --network localnet
```

The live smoke test is opt-in (`RUN_STUDIONET=1`) and uses disposable in-process
wallets. It performs the full compile, assign, reassign, acknowledge, and seal
flow, waits for finalized successful receipts, reads `LATEST_FINAL`, and fails
unless deployed source bytes and schema match this repository.

StudioNet contract: https://explorer-studio.genlayer.com/address/0x5c72e9c076e00f0ECB1F953dF1883C3b565789DC

See `AUDIT.md`, `ORIGINALITY.md`, `SOURCE_POLICY.md`, `SECURITY.md`,
`SUBMISSION.md`, and `deployments/studionet.json` for the final evidence.

## Boundary

The contract moves no funds and does not establish identity, ownership,
professional authority, source authenticity, physical truth, or legal effect.
All caller inputs and calldata are public. Off-chain clients own authentication,
privacy, source curation, indexing, and the decision to rely on a result.
