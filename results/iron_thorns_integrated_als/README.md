# Integrated Iron Thorns ex ALS

## Question

Can the Iron Thorns ex line be validated from search access through typed attack readiness in one state model?

The human prior describes:

`Tag Call -> Guzma & Hala -> Thunder Mountain Prism Star + Double Colorless Energy -> Volt Cyclone`

Earlier work validated the Energy endpoint after precompiling the Guzma & Hala segment. This result models the upstream card-zone and action transitions, then calls the existing exact Energy evaluator.

Implementation: `tools/iron_thorns_integrated_als.py`  
Regression: `results/iron_thorns_integrated_als/reproduce.py`

## Card anchors

The bundled Expanded-legal records used are:

- Tag Call `sm12-206`: Item; searches for up to two TAG TEAM cards.
- Guzma & Hala `sm12-193`: TAG TEAM Supporter; searches a Stadium and, after discarding two other hand cards, can also search a Pokémon Tool and Special Energy.
- Thunder Mountain Prism Star `sm8-191`: attacks of Lightning Pokémon cost one Lightning Energy less.
- Double Colorless Energy `sm2-166`: provides two Colorless Energy.
- Iron Thorns ex `sv6-77`: Lightning Basic; Volt Cyclone costs Lightning + Colorless + Colorless.

## Baseline state and result

The baseline starts with Iron Thorns ex Active, Tag Call plus two disposable cards in hand, and Guzma & Hala, Thunder Mountain, and Double Colorless Energy in the deck. Item, Supporter, Stadium, manual Energy attachment, and attack actions are available.

The breadth-first search finds this shortest five-action line:

1. Tag Call -> Guzma & Hala to hand.
2. Guzma & Hala; discard two other cards -> Thunder Mountain + Double Colorless Energy to hand.
3. Play Thunder Mountain.
4. Attach Double Colorless Energy to Iron Thorns ex with the normal attachment.
5. Use Volt Cyclone.

At the endpoint, the existing `energy_action_budget.py` evaluator receives two separate effects: Double Colorless Energy supplies `CC`, while Thunder Mountain removes the `L` requirement from the Lightning attack. Together they satisfy `LCC`.

## Findings

**The named line spans several independent resource dimensions.** Item availability, the Supporter window, two discardable cards, Stadium play, the normal Energy attachment, searchable deck objects, and attack availability are all required in the baseline. The regression removes these capacities individually and the line fails.

**Access to Guzma & Hala does not imply access to its full output.** With only one disposable card, Tag Call can still find Guzma & Hala, while the represented Special Energy branch remains unavailable because the optional cost needs two other cards.

**Energy supply and cost reduction remain different channels.** Attached Double Colorless Energy alone leaves the Lightning requirement unpaid. Thunder Mountain alone leaves the reduced `CC` demand without Energy. Their combination is sufficient.

**Locks should remove only the transitions they govern.** If Guzma & Hala begins in hand, Tag Call is unnecessary and the shortest line has four actions. If Thunder Mountain and Double Colorless Energy are already in hand, both Item and Supporter play can be disabled and the three-action Stadium -> attachment -> Volt Cyclone endpoint still exists.

**Prize location is a state dependency.** Moving either Thunder Mountain or the represented Double Colorless Energy from the deck to the Prize zone breaks this specific search line. This model does not convert that fact into a deck-level Prize probability because alternative copies and routes are outside scope.

## Relationship to prior work

This result composes two existing layers:

- `results/typed_access_network/`: zones, locks, Supporter windows, and action legality.
- `results/energy_action_budget/`: typed Energy supply, reductions, and finite action capacity.

It also provides a concrete case for discard-cost AMR, resource-constrained connectors, Prize dependencies, and lock geometry.

## Methodological implication

A route compiler should emit state transitions plus typed endpoint effects rather than only association edges.

For this line, Tag Call changes card zones, Guzma & Hala has an optional-cost output profile, Thunder Mountain changes persistent typed demand, the manual attachment changes attached Energy state, and Volt Cyclone becomes usable only after the Energy kernel confirms the current cost is satisfied.

## Limits and next work

This is a targeted deterministic model. It does not yet sample opening hands or six Prize cards, model a full decklist, enumerate alternate Energy or Stadium routes, handle turn ownership in general, or score strategic value after the attack.

The strongest next extension is to run the integrated transition logic over counted card identities and sampled states from a real Iron Thorns ex list. That would measure actual first-turn-going-second Volt Cyclone probability while preserving discard payability, Prize risk, connector contention, and typed Energy readiness.
