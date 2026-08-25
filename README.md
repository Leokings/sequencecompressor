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
