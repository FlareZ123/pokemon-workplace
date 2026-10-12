# Iron Thorns ex: first-turn Guzma & Hala discard-payability sensitivity

## Decision and exact setup

The [60-card English-print adaptation](README.md) raises Double Colorless Energy (DCE) from one to two copies. Its first opening analysis assumes the optional two-card discard to Guzma & Hala (G&H) can be paid whenever mechanically required to search DCE. Actual hands often contain cards valuable for other turns or matchups. This study measures the sensitivity of named Thunder Mountain + DCE access to hypothetical discardability rules.

The exact sample space is a Basic-valid seven-card opening (four Iron Thorns ex), six hidden Prize cards set from the remaining deck, and one first-turn natural draw going second. One Iron Thorns moves from hand to the Active Spot. Counts held fixed: two Tag Call, two G&H and one Thunder Mountain Prism Star. DCE count changes between one and two while the total remains 60.

The optional cost on printed G&H is two *other* hand cards, enabling both Pokémon Tool and Special Energy search. Ordinary Stadium search does not require that discard. Directly held Thunder Mountain+DCE succeeds without G&H. When DCE is held, G&H can fetch missing Thunder Mountain without using the paid branch.

## Three declared policies

1. **Ideal paid:** any mechanically payable two-card discard is allowed, reproducing the previously published named resource-access envelope.
2. **Strict paid:** G&H may discard only two held cards from a predefined safe filler subset of the other cards.
3. **Spare connector paid:** additionally allows extra held G&H or Tag Call copies not needed for the chosen route. All other cards remain protected.

The 12-card illustration designates four Crushing Hammer, four Trainers' Mail, two Enhanced Hammer and two Camping Gear as *hypothetical* acceptable discard cards. These cards have real competing roles, especially in Item-lock matchups. Their true DCI and opportunity cost are not quantified here. No policy is asserted to be a generally optimal way to play the list.

## Exact conditional probabilities

| Designated safe other cards | Original, 1 DCE strict | Adaptation, 2 DCE strict | Adaptation, 2 DCE spare |
| ---: | ---: | ---: | ---: |
| 0 | 4.841275% | 9.234391% | 9.561841% |
| 6 | 8.452492% | 12.954847% | 14.998067% |
| 12 | 16.293836% | **20.953811%** | **23.149687%** |
| 19 | 24.836675% | 29.529449% | 31.079047% |
| 30 | 32.080710% | 36.568688% | 37.020903% |
| 48 | 33.780204% | 38.080141% | 38.080661% |

The idealized figures are **33.781506%** (one DCE) and **38.080680%** (two DCE), independent of the hypothetical safe subset. Under the strict 12-card policy, the adapted package's modeled access is 20.953811%, **17.126869 percentage points** below its unrestricted theoretical envelope. Extra unused Tag Call and G&H cards raise that modeled value to 23.149687%.

The second DCE improves the strictly payable 12-card endpoint by **4.659975 percentage points**, slightly more than the idealized 4.299174-point gain. Some states that formerly needed the optional two-card discard already hold DCE and therefore avoid the cost.

## Independent verification

[Exact integer combinatorics](../../../tools/iron_thorns_gnh_discard_gate.py) marginalize over opening compositions, next-draw category and Price allocation for the three relevant search categories. For efficiency, the code mathematically reorders the first draw before the six hidden Prizes. Uniform sampling makes that joint distribution equivalent to the actual physical sequence.

[Independent regression](discard_gate_reproduce.py) instead enumerates individually labeled cards in physical order: opening hand, Prize cards, then natural draw, and evaluates each physical hand and searchable deck. Three toy configurations cover exactly 13,608, 25,200 and 47,880 accepted opening/Prize/draw worlds. All six probability buckets match the grouped calculation exactly.

The same test independently reproduces the one-DCE and three-DCE previously published idealized resource access and validates the new two-DCE value. It also checks reachability monotonicity, subset inclusion and policy ordering across six declared safe-pool sizes. Windows workflow: [validate-iron-thorns-aichi-english.yml](../../../.github/workflows/validate-iron-thorns-aichi-english.yml).

## Boundaries and next research

These are conditional access rates for the *named* first-turn package, not estimated first-turn Volt Cyclone attack frequencies or game win rates. The model omits search from Trainers' Mail, Speed Lightning Energy draws, Gladion, optional Stadium paths, earlier Item plays, opponent mulligan draws, opponent lock/disruption, Tool usage, later sequencing, matchup-dependent discard costs, and the value of Japanese-only draw cards removed during English adaptation.

The next valuable comparison is an English-print Stadium or draw-engine alternative to the second DCE, using a two-turn policy with actual card-use opportunity costs and eventual matchup evaluation.
