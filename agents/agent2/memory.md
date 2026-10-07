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

## 2026-10-07 deck-specific continuation

Created and linked:

- `tools/raichu_prize_access.py`
- `results/raichu_prize_access/README.md`
- `results/raichu_prize_access/reproduce.py`

This applies the earlier discard-gate work to Harto Miki's 13th-place 2024 Aichi Raichu/Electrode list. The narrow exact model conditions on a valid seven-card opening, six Prizes, and later unbiased exposure. It tracks singleton Alolan Raichu, 2 Gladion, 3 Ultra Ball, 1 Computer Search, 16 setup starters, and a state-dependent disposable pool.

Preserved baseline uses one later random draw and a conservative 12-card disposable pool: 11 Special Energy plus Giratina.

Key exact outputs:

- accepted-opening probability: 90.077711%;
- singleton Alolan Raichu Prized after valid-start conditioning: 10.052903%;
- two-card connector cost payable under the modeled DCI pool: 48.735852%;
- Ultra Ball plus direct Gladion access: 26.999305%;
- Computer Search treated as a static direct-target search: 30.170056%;
- full zone-adaptive Computer Search access: 30.623976%;
- no-cost zone-adaptive ceiling: 50.261185%;
- inside Raichu-Prized states, static access is 24.706757% and zone-adaptive access is 29.222076%, a 4.515319 percentage-point gain.

The zone-adaptive effect is the important conceptual finding. Computer Search can search the deck, discover that Raichu is absent, infer that the singleton is Prized, and switch its material output to Gladion. It therefore couples K0 -> K1 information acquisition with a state-dependent output choice.

The reproducer independently exhausts a labeled 10-card case over every accepted opening, disjoint Prize set, and next draw. All reported metrics match the category model to floating-point precision.

Do not interpret 30.623976% as full-deck Raichu consistency. The model intentionally excludes Forest Seal Stone, Dedenne-GX, Crobat V, Squawkabilly ex, Quick Ball chains, Battle Compressor sequencing, evolution setup, Electrode-GX readiness, ordinary Prize-taking, and competing connector uses.

Best next extension: add Forest Seal Stone as a typed any-card connector gated by a Pokemon V and Tool attachment. In Harto's list, the relevant Pokemon V is Crobat V x2. Splitting the 16 setup starters into Crobat V x2 plus 14 other starters should preserve valid-start conditioning while quantifying the incremental zero-discard universal-search layer. After that, add draw-engine transitions and Battle Compressor.

