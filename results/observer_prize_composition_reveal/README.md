# Observer-relative K0 to K1 Prize composition

## Question

How should the first full deck search change an observer-indexed Prize belief?

The searching player can learn exact Prize composition by inspecting the remaining deck and comparing it with the known decklist, while physical Prize positions remain face down unless another effect reveals them.

Implementation: `tools/observer_prize_composition_reveal.py`  
Regression: `results/observer_prize_composition_reveal/reproduce.py`

## K0 prior

The toy state has two face-down Prize slots.

Exactly one modeled singleton is Prized. Before a full deck search, the observer assigns equal probability to:

- A being Prized;
- B being Prized.

The physical slot containing that singleton is also unknown.

Both players begin from this same belief.

## Full-deck inspection

The searcher inspects the deck and can infer that A is missing while B is present.

The K1 update conditions the searcher on exact modeled Prize composition:

- A count = 1;
- B count = 0.

The update deliberately does not reveal which physical Prize slot contains A, so each slot remains 50% likely to be A.

The opponent receives no composition observation and keeps the original 50/50 composition uncertainty.

## Finding

K1 is observer-relative and composition-specific.

A deck search should not collapse face-down Prize positions into known positions. It should remove uncertainty about which modeled cards are in the Prize zone for the searching player.

This transition composes naturally with the existing positional and cross-zone belief layers.

## Why this matters for Dream Ball

Dream Ball itself opens the deck and then shuffles it.

If it is the player's first deck search, its resolution can create K1 Prize knowledge at the same time that the deck-top position becomes randomized.

Those information events belong in the search/shuffle transaction rather than being approximated by a generic "search succeeded" flag.

## Limits

The caller supplies the exact modeled Prize composition inferred from the deck inspection.

This module does not reconstruct that composition from a full 60-card decklist and visible-zone ledger. A higher-level canonical state can do that mechanically.

The result conditions only the modeled Prize groups. Unmodeled cards remain represented by the filler group.

## Next work

Compose K1 conditioning with a deck-search shuffle boundary that collapses the materialized old top back into the searchable deck, executes an exact search target, and samples a new top from the remaining physical deck.
