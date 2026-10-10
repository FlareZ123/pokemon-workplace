# Adversarial cross-oracle sweep for draw, allocation and order models

The primary research results use exact, hand-audited toy examples. This additional reproducible quality check tests the same dynamic programs against many more physical arrangements and observation patterns.

## Method

`results/prize_exposure_property_sweep/reproduce.py` uses a fixed pseudorandom seed `20261010` to select **220** reproducible five-card configurations.

Every configuration contains a Pokémon-group card P and an Energy-group card E, with three further cards selected from P, E, FLEX and X. Every physical copy has its own instance ID. The oracle independently enumerates all **120 physical deck permutations**, even when several copies share a strategic group.

In each case:

1. Construct the exact group-count prior over deck top plus remaining deck with no Prize cards, using the same finite-pool model available in the broader Prize research.
2. Choose an ordered-prefix depth from 0 to 3 and a random subset of physically valid position observations.
3. Condition the belief on those observations and independently filter the enumerated physical decks in the same way.
4. Select a random draw window length and required P/E counts.
5. Compare the following predictions to the physical-deal oracle, both with the preserved deck order and with a full-deck shuffle:
   - univariate P exposure;
   - simultaneous P and E minimums;
   - allocation feasibility, where a FLEX card may choose one of two outputs or provide both simultaneously.
6. Draw the top card within the dynamic program and check that its newly exposed top group distribution matches the original physical second-card distribution for every modeled group.

The allocation oracle directly explores profile assignments to individually drawn physical cards; the production allocation probability calculator uses a grouped multivariate hypergeometric dynamic program. Their computational representations are intentionally different.

## Scope and interpretation

The 220 cases are a **deterministic property-based regression sample** across input variants. Each case examines all 120 possible physical deck orders. This is not a proof for every legal Pokémon deck, although a failed case gives an exact reproducible counterexample.

The physical deck has only five cards and no Prize-zone occupancy in this sweep. Other dedicated regressions exercise Prize positions, face-up constraints and physical transfers. This sweep specifically stress-tests the probabilistic interfaces that combine ordered prefixes, multiple target categories, and per-copy resource allocation.

The test deliberately samples source-independent abstract role profiles. Printed card effects, legality, activation costs and full gameplay remain outside this probability oracle.
