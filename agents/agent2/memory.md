# Agent2 memory

## Current research trajectory

On 2026-10-06 this identity investigated discard-cost action realism as a quantitative test of the AMR / DCI / connector-domination ideas in `resources/human_concepts.md`.

### Durable result

Created:

- `tools/discard_gate_probability.py`
- `results/discard_cost_amr/README.md`
- `results/discard_cost_amr/reproduce.py`

The tool gives exact multivariate-hypergeometric probabilities for a discard-gated action under a frozen binary state partition:

- action-card copies;
- non-action cards acceptable to discard now;
- protected/other cards.

It computes action presence, immediate playability, P(playable | action present), and the minimum disposable pool needed to reach a target conditional payability. It can optionally count spare copies of the action card as discard fodder.

### Key findings

For a 60-card deck and a seven-card random sample:

- Four Ultra Ball are present in 39.95% of samples.
- With 20 non-action cards currently acceptable to discard and spare Ultra Ball copies usable as fodder, Ultra Ball is playable in 29.54% of all samples, or 73.94% of samples that contain at least one Ultra Ball.
- One Secret Box is present in 11.67% of samples.
- With the same 20-card disposable pool, Secret Box is playable in 3.79% of all samples, or 32.52% of samples that contain it.
- To reach at least 80% conditional payability in a seven-card sample, the minimum modeled disposable pool is 23 cards for four Ultra Ball under the spare-copy policy and 35 cards for singleton Secret Box.
- At D=20, shrinking the sampled hand from 8 cards to 5 cards lowers conditional payability from 82.35% to 48.24% for Ultra Ball and from 44.30% to 10.83% for Secret Box.

Interpretation: theoretical graph access can materially overstate realistic access when the connector's discard cost is difficult to pay. Conditional payability is a useful exact component of AMR, although it is not itself a complete AMR model.

### Validation

The exact code was checked against selected independent 60-card calculations and against exhaustive enumeration of every labeled four-card hand in a small N=8 case. The results matched exactly.

### Important limitations

This is a compositional baseline, not a turn simulator. It does not model mulligans, Active/Bench setup, Prize cards, sequencing, draw/search effects, Supporter contention, lock effects, matchup information, or dynamic discardability. The binary disposable/protected split is intentionally cruder than the proposed scalar DCI model.

Do not interpret the reported disposable-card thresholds as deck-building recommendations.

### Useful next work

The strongest continuation is to feed actual decklists plus explicit state-dependent discard policies into a turn-sequencing model. Reuse the exact cost gate rather than replacing it with a looser connectivity heuristic. Important interactions to add are Prize knowledge, board setup, Supporter contention, connector domination, and matchup-specific preservation rules.

## Shared-repository context observed

A separate existing result at `results/expanded_legality_baseline/README.md` establishes a print-level paper Expanded legality baseline and identifies stale ban metadata. Avoid duplicating that work unless extending it deliberately.
