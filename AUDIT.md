# Technical audit — 2026-10-08

Scope: the current `contracts/sequence_compressor.py`, tests, submission
evidence, and the StudioNet deployment in `deployments/studionet.json`.
Current source SHA-256: `f848cd8e95d98825f68f77a7a2fa3d56331b359de7436cea149b4b28f02143a8`.

## Findings and fixes

- A zero-address assignment could leave a segment unable to acknowledge. Both
  assignment methods now reject that address.
- The owner previously had no way to recover an assigned but unacknowledged
  segment from an unavailable or mistaken operator. `reassign_segment` now
  allows owner-only replacement while that segment is `ASSIGNED`; the old
  operator immediately loses authority, and the new operator must be unused
  by other active segments. Acknowledged or sealed segments cannot be reassigned.
- A second `seal_sequence` call was accepted as an idempotent write. It now
  rejects with `sequence_sealed`, making the terminal transition explicit.

## Checks actually run

| Gate | Result |
| --- | --- |
| GenVM lint and semantic validation | PASS |
| Strict typecheck | PASS, zero diagnostics |
| Direct tests | PASS, 11 tests, including role, malformed-model, zero-address, stale-operator, reassignment, and terminal-state cases |
| Five-validator GLSim classification | PASS |
| StudioNet full lifecycle | PASS, 10 finalized execution-successful receipts: deploy, AI compile, 8 lifecycle writes |
| Independent read-only StudioNet regression | PASS, all 10 receipts rechecked |
| Latest-final state | PASS, `SEALED`, 3 assigned and 3 acknowledged segments |
| Deployed source bytes and method schema | PASS, exact source SHA-256 match and all 8 methods present |
| GitHub public MIT source | PASS after publication recheck |

Live contract: https://explorer-studio.genlayer.com/address/0x5c72e9c076e00f0ECB1F953dF1883C3b565789DC

AI compilation: https://explorer-studio.genlayer.com/tx/0x338721e4cbeba7cbc8571e2badd66acc65a027afbc89402fd975e34b9dd78afc

Final seal: https://explorer-studio.genlayer.com/tx/0xcbe120da2e9ee5dda0961808d44da460d830d476db9157f9a6aa9c5faa2ca5dc

The exact ordered transaction list and seven public test addresses are in
`deployments/studionet.json`; private keys were not stored in the repository.
The previous compile-only deployment at
`0x6c8d83FdB74e82E66B5bBf9E48931F906B062457` is historical and is not
evidence for the revised source.

## Remaining boundaries

The semantic labels are validator judgments and can fail consensus or vary
between valid runs. An operator acknowledgement proves only that the assigned
wallet sent that transaction; it does not prove real-world work. An assigned
operator who already acknowledged cannot be replaced, by design. The contract
holds no funds. Public inputs are not authenticated evidence. Technical tests
reduce risk but do not guarantee program acceptance or the absence of every
possible flaw.
