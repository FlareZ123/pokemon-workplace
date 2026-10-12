# Finite-deck copy counts constrain hidden Prize/hand beliefs

Observer-relative beliefs about face-down Prizes, top-deck cards and unknown hand composition can accidentally assign weight to impossible worlds containing more copies of a card group than the deck physically contains. We provide a conservative, necessary-feasibility filter with typed copy totals and optionally counted public cards outside the modeled zones.

Implementation: `tools/prize_hand_copy_budget.py` and executable proof `results/prize_hand_copy_budget/reproduce.py`.

## Exact four-world proof

Four hidden worlds are equally probable. Each has a deck-top class, a tagged Prize-origin hand class and one other hand card class:

| World | Top | Tagged | Other hand | Legal under group inventory? |
| --- | --- | --- | --- | --- |
| Actual | S | C | O | Yes |
| Counterfactual | F | C | C | No: two C with only one C in deck |
| Counterfactual | S | O | C | Yes |
| Counterfactual | F | O | O | Yes |

The complete modeled deck has group capacities S=1, F=1, C=1 and O=2. Suppose one uniformly random card is publicly discarded as C. An independent rational enumeration of two possible physical discard origins gives:

| Posterior | Unfiltered | Copy-feasible |
| --- | ---: | ---: |
| P(top S) | 1/2 | **1** |
| P(tagged card is C) | 3/4 | **1/2** |
| P(tagged copy still in hand) | 1/4 | 1/2 |

The physical regression materializes the valid world with tagged C and other O and actually discards the tagged copy. The owner distinguishes physical origins, while the opponent retains their uncertain origin posterior. Card instances are conserved. Impossible input inventories, unmodeled groups, and zero-support cases are rejected.

## Boundaries

Every hidden world counts group copies explicitly represented in the top card, remaining Prizes, tagged hand card and other hand cards, together with *disjoint* publicly known outside copies. A world exceeding the initial deck group total is impossible. A world below these ceilings may still fail more detailed exact-print, zone-occupancy, or search-history constraints. Hidden group labels and observer policies are illustrative, and these probabilities do not represent match win rates.

This necessary conditioning protects downstream draw/search decision policies from accidentally relying on physical impossibilities.
