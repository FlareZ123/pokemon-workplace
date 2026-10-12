# The extra first-turn draw can remove a Shadow Rider VMAX search target

## Strategic question

For Yasunori Kato's winning 2026 Aichi Shadow Rider Calyrex list, how does the **one natural draw going second** affect a narrow Radiant Eternatus two-VMAX launch compared with using Climactic Gate on the first turn going first, where there is no natural draw?

The earlier [Radiant opening analysis](../shadow_rider_radiant_launch/) computed the marginal after one draw. The new paired exact model holds the **same seven-card valid Basic opening and six physical Prize cards** fixed, then compares a no-draw action with every possible top-card identity.

## Exact matched-world result

The launcher counts Radiant Eternatus from hand or fetched by one of four Mysterious Treasure Items, an eligible other Basic starting Active, and at least two Shadow Rider Calyrex VMAX still physically searchable in deck.

| Same-world transition | Probability of valid opening |
| --- | ---: |
| No dual-VMAX launch before draw; yes after draw | **4.3853588775%** |
| Yes before draw; no after draw | **0.2649846061%** |
| Yes before and after | **39.3138035529%** |
| No before and after | **56.0358529636%** |

These four mutually exclusive classes sum to 100%. Marginals are:

| Turn order opening | Two-VMAX access via named routes |
| --- | ---: |
| First player, no turn-one draw | **39.5787881589%** |
| Second player, one turn-one draw | **43.6991624304%** |
| Net advantage from the draw | **+4.1203742714 percentage points** |

A draw can cause **regression** in the launch endpoint. Every lost case draws a Shadow Rider Calyrex VMAX when the deck had exactly two searchable VMAX before the draw. Moving one into hand makes the second VMAX search impossible with Climactic Gate alone. The unconditional loss mass is exactly **0.2649846061%** of Basic-valid starts.

The gross gain has two fully identifiable origins: drawing Radiant Eternatus when Treasure could not previously reach it (+0.9668960922 percentage points), or drawing Mysterious Treasure while the unique Radiant remains in the deck (+3.4184627853 points). There are no positive transitions from drawing other category types in this narrow policy. Gross positives minus negatives give the net gain above.

## Reproducibility

[Reproducer](reproduce.py) performs multivariate hypergeometric weighted enumeration across every grouped opening, Prize set, and draw. It independently checks **8,925 labeled physical toy worlds** with a physically enumerated ten-card deck and a three-card opening/two Prizes; every yes/no transition and draw-category reason matches. It also crosschecks the after-draw marginal against the independent existing [Radiant launch model](../shadow_rider_radiant_launch/reproduce.py) and asserts exact rational numerator/denominator values.

This is a concrete **search-target depletion** effect: increasing hand cards is usually helpful for broad game strategy, but can degrade a deck-only search effect's immediate target inventory. To evaluate the true utility of going first or second, a model must include whether the VMAX drawn into hand becomes usable on the next turn, the opponent's response, setup exposure, attacking and ability restrictions, and subsequent turns. **This result does not imply going second is globally better.**
