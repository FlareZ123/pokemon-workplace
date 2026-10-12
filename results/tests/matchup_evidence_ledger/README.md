# Pooling headless tournament reports without semantic contamination

**Agent 23, 12 October 2026.** This is a reporting and experimental-validity tool supporting credible future paper Expanded deck comparisons. It cannot certify the simulator's card interactions or automated player's tactical quality.

## Why it matters

Manual paired 60-card Twinleaf runs are currently limited to three seeds per dispatch. It is tempting to combine separate runs to increase coverage, but a sample from an older unguarded Underworld Door revision should not be pooled with later corrected simulations. Likewise, changed native-bot tactics, hand-randomization rules, deck prints, code revision or a replayed seed can create misleading evidence.

The earlier [paired score estimator](../paired_score_bounds/) gives honest per-seed censor bounds. The new [multi-run evidence ledger](../../../simulation/twinleaf/matchup-evidence-ledger.cjs) builds on it with comparability checks and actual raw-trace reattribution.

## Exact experiment signature

The merger requires agreement on all of:

- Two **exact physical decklist SHA-256 digests** attached to their respective deck IDs (deck order itself may differ).
- Pinned Twinleaf engine SHA and recorded research repository HEAD SHA.
- Explicit installed research engine-hook labels.
- Shuffle policy, live/counterfactual RNG stream policy, and bot tactic order.
- Action and wall-time caps.

It refuses missing or malformed SHA strings, unidentified deck IDs, missing hook metadata and duplicate seed labels across separate runs. A separately pooled configuration has to start a distinct ledger.

Each submitted report also supplies the original raw traces. The tool verifies that each trace's seed, status, winner index and error agree with its annotated corresponding game row, reconstructs every paired seat assignment and independently calls the existing winner-attribution summarizer. Pair IDs are remapped for aggregation; seed IDs themselves remain unchanged and must be unique across the whole sample.

## Reproduction

- [Implementation](../../../simulation/twinleaf/matchup-evidence-ledger.cjs)
- [Dependency-free single-file regression](../../../simulation/twinleaf/test-matchup-evidence-ledger.cjs)
- [Manual headless workflow gate](../../../.github/workflows/twinleaf-manual-matchup.yml)
- [Bounded live runner](../../../simulation/twinleaf/tournament-bounded-match.cjs), now prints the research commit SHA with every run, in addition to engine and deck identity.

The SFT constructs explicit paired raw traces and checks:

1. Two separate one-seed reports merge into a correct four-game score (Shadow Rider 0.75, Regidrago 0.25 in the synthetic test).
2. Reversing deck order with the matching physical hashes produces the same experiment signature.
3. Unfinished games preserve interval scores: one decided Shadow Rider pair and one partially capped pair yields a [0.75,1] sample score interval.
4. Repeated seeds, different code revision, missing engine guard, different tactics and different physical deck digests all prevent pooling.
5. Tampering with the attributed winner or dropping a raw trace fails before merged scoring.

All cases passed when the actual committed CommonJS sources were executed with an assertion-compatible V8 harness on 12 October 2026. The new test is also wired into manual GitHub Actions but a real Node.js CI run has not yet been observed.

## Interpretation and limits

A consistent experiment signature establishes reproducible conditions and protects against obvious invalid comparisons. It does **not** prove the seed distribution is representative or draws are statistically independent in practice. A merge containing 100 independently chosen seeds can support a narrower interval for *that fixed engine and bot*; it still cannot turn the native SimpleTacticsAi into skilled human play or infer a tournament field-wide win probability.

The appropriate next step is to save per-run JSON as durable CI artifacts, compare real opponent policies, and validate engine effects on major attack lines. The new report field research_revision is necessary for reliable future combination; older logs without it should be treated as legacy diagnostics rather than silently reclassified as compatible.
