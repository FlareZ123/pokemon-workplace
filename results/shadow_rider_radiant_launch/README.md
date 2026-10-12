# Champion Shadow Rider: exact Radiant Eternatus / two-VMAX opening geometry

## Question

How often can the tournament-winning [Aichi Shadow Rider list](../competitive_deck_baselines/) put **two Shadow Rider Calyrex VMAX from the deck** onto its Bench through Radiant Eternatus's Climactic Gate, using only direct access or a physically present Mysterious Treasure, by the first natural draw going second?

This matters because a list with four VMAX and four Pokémon search Items may appear nearly guaranteed to launch two VMAX, despite six hidden Prize cards, direct opening-hand depletion of VMAX stock, and the need for a different Basic Pokémon in the Active Spot.

## Inputs, scope, and action contract

The complete 60-card source has **14 Basics**, including the singleton Radiant Eternatus, **four Shadow Rider Calyrex VMAX**, and **four Mysterious Treasure**. Collapse its physical identities into five named categories:

| Category | Physical copies |
| --- | ---: |
| Radiant Eternatus | 1 |
| Shadow Rider Calyrex VMAX | 4 |
| Mysterious Treasure | 4 |
| All other opening-eligible Basic Pokémon | 13 |
| All other cards | 38 |

The action model draws seven cards, rejects mulligans, sets six Prizes from the remaining physical stock, and takes exactly one natural draw going second. It uses the best legal opening Active choice for this specific Radiant launch: reserve a non-Radiant Basic in the Active Spot if one appeared **in the opening seven**. Radiant on the Bench can be played from hand, or searched from the deck by a held Mysterious Treasure when Radiant is still searchable. That Item searches Psychic/Dragon Pokémon at a one-card discard cost. Radiant's Climactic Gate chooses up to **two VMAX from the remaining deck**, puts them on the Bench, and ends the turn.

We count two VMAX as success only if at least two of the four Shadow Rider VMAX remain **in the deck after the opening, Prize, and first draw**. A VMAX in hand is not a target for Climactic Gate, and a VMAX Prized is unavailable to that search.

**Deliberate exclusions:** no Hisuian Heavy Ball, Fog Crystal, Supporter or Ability draw, other connectors, opponent bonus mulligan cards, Item or Ability lock, matchup utility, manual Bench placement conflicts, or post-launch attack turns. Mysterious Treasure cost is *mechanically* payable at this point because after the first draw and selecting a starting Active there are seven cards available, but the model does not price the opportunity cost of discarding any one of them. These are **narrow first-turn launch probabilities**, not match win rates.

## Exact results

Every accepted opening and physical six-Prize draw is weighted with multivariate hypergeometric coefficients. The result is a rational number without Monte Carlo noise. Percentages are conditional on a valid seven-card Basic opening and one subsequent natural draw.

| Outcome | Probability |
| --- | ---: |
| Two VMAX via Radiant already in hand | **12.017840120%** |
| Two VMAX via Mysterious Treasure -> Radiant | **31.681322310%** |
| **Total two-VMAX launch via these routes** | **43.699162430%** |
| Radiant available via either route, regardless of VMAX stock | **45.025040638%** |
| Valid Basic opening with no alternate Basic available as the starting Active | **2.815545248%** |
| No represented access to Radiant | **52.159414114%** |

The difference between overall Radiant availability and two-VMAX launch is **1.325878207 percentage points**, caused by having fewer than two searchable VMAX copies under the represented routes.

The Treasure route contributes more successful states than direct Radiant access because it provides four additional chances to reach the unique Radiant while Radiant remains in the deck. Treating Mysterious Treasure as a free connector overstates genuine feasibility when the player has strategically protected cards in hand. Using the Item for Radiant also excludes its alternative use to fetch Shadow Rider Pokémon or other tactical Psychic/Dragon targets. These opportunity costs need actual decision-policy experiments.

## Reproducibility and adversarial check

The self-contained [reproducer](reproduce.py):

1. Imports the **actual 60-card baseline counts** rather than silently inventing a second list.
2. Enumerates all valid opening class allocations, six-Prize allocations, and first-draw categories, weighted by each physical multiplicity.
3. Asserts total normalized probability mass is exactly one.
4. Independently enumerates **8,925 labeled physical worlds** of a ten-card toy deck with three-card opening and two Prizes and proves equality with the grouped model in every output class.
5. Locks key 60-card results to exact rational fractions, so changes to the policy or formula require review.

Run the module from the repository root as \`python -m results.shadow_rider_radiant_launch.reproduce\`. The workflow [validate Radiant launch](../../.github/workflows/validate-shadow-rider-radiant-launch.yml) tests it on Windows.

## Next important experiments

- Model actual K0/K1 knowledge and the discardability of cards in the physical hand when Mysterious Treasure would find Radiant.
- Determine whether later board advantage from two VMAX is worth ending the turn before attacking or playing other actions.
- Compare opposing Item/Ability lock, VMAX Prize liability, and recovery packages in full match simulation.
- Include alternative first-turn paths (Hisuian Heavy Ball, natural draw, and other searches) without double-counting overlapping openings.
