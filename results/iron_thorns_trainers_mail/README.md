# Trainers' Mail extension for Aichi Iron Thorns ex

## Question

How much first-turn-going-second Volt Cyclone access does Trainers' Mail add to the narrow Iron Thorns ex line used by the three published 2026 Aichi Open League lists?

The baseline is the exact named route:

`Tag Call -> Guzma & Hala -> Thunder Mountain Prism Star + Double Colorless Energy -> Volt Cyclone`

This extension adds Trainers' Mail search behavior while leaving other Trainer effects outside the action set.

Implementation: `tools/iron_thorns_trainers_mail.py`  
Regression: `results/iron_thorns_trainers_mail/reproduce.py`

## Model

For every accepted seven-card opening, six-card Prize allocation, and first draw going second, the model tracks Guzma & Hala, Tag Call, Thunder Mountain, Double Colorless Energy, Trainers' Mail, other Trainers, and other non-Trainers.

Each Trainers' Mail use enumerates every possible top-four category composition with exact hypergeometric weights. The solver then chooses the legal target that maximizes the represented continuation value. It may take Guzma & Hala, Tag Call, Thunder Mountain, another Trainer whose own effect is ignored, or no card.

The selected card leaves the deck. Unselected revealed cards return to the deck after the shuffle. Another Trainers' Mail therefore samples the updated deck rather than a permanently depleted top-four group.

Double Colorless Energy cannot be selected by Trainers' Mail.

## Published list counts

| Player | Trainers' Mail | Double Colorless Energy | Other Trainers |
| --- | ---: | ---: | ---: |
| Kazuma Kashi | 3 | 1 | 40 |
| Ryoya Fujii | 4 | 3 | 39 |
| Kohei Hamamichi | 2 | 1 | 41 |

All three lists have 4 Iron Thorns ex, 2 Guzma & Hala, 2 Tag Call, and 1 Thunder Mountain Prism Star.

## Exact result

Conditioned on a legal opening and the first draw going second:

| Player | Narrow route | With Trainers' Mail | Increment |
| --- | ---: | ---: | ---: |
| Kazuma Kashi | 33.781505711% | **38.821051379%** | **+5.039545669 pp** |
| Ryoya Fujii | 39.107850627% | **46.623420409%** | **+7.515569782 pp** |
| Kohei Hamamichi | 33.781505711% | **37.195582431%** | **+3.414076720 pp** |

Kazuma and Kohei share the same narrow baseline because their relevant Tag Call, Guzma & Hala, Thunder Mountain, and DCE counts are the same. Their Mail-aware values differ because Kazuma has one additional Trainers' Mail.

Ryoya combines four Trainers' Mail with three DCE, so more states become useful after Mail finds Thunder Mountain, Tag Call, or Guzma & Hala.

## Findings

**Trainers' Mail is a multi-channel connector.** It can find Guzma & Hala directly, find Tag Call as indirect Guzma & Hala access, or find Thunder Mountain in a state where DCE is already available.

**Connector value depends on payload density.** Trainers' Mail cannot search DCE, yet extra DCE copies raise the value of Mail because more states already satisfy the Energy-card channel when Mail repairs a Trainer channel.

**Repeated top-four searches are stateful.** A Mail that takes any Trainer removes one card from the deck before a later Mail. Taking Thunder Mountain also removes the need to solve that channel. The post-search state therefore matters.

**Mechanical discardability remains weaker than strategic discardability.** The represented first-turn lines retain enough card count to pay Guzma & Hala's two-card optional discard when needed. The model does not claim those cards have high DCI.

## Relationship to Gladion and mulligan work

`results/iron_thorns_turn1_probability/` separately adds information-aware Gladion rescue to the Kazuma baseline, and also quantifies opponent mulligan bonus draws.

The Mail increment here should not be added arithmetically to the Gladion increment. Trainers' Mail changes which states can reach Tag Call, while Tag Call can establish exact Prize knowledge and change whether Gladion is the best Supporter.

A combined policy must evaluate both mechanisms in the same state.

## Validation

The opening, Prize, turn-draw, and Trainers' Mail layers are exact combinatorial enumerations. The recursive Mail continuation value is memoized by represented hand and deck state.

The reproducer derives each list's modeled counts from the existing Aichi list transcription and asserts the exact values above.

## Limits

This result omits Gladion's rescue effect, opponent mulligan bonus draws, other draw-Supporter effects, VS Seeker, Speed Lightning Energy draw effects, alternate attack packages, opponent interaction, and strategic DCI beyond raw hand count.

Other Trainer cards may be selected by Trainers' Mail to thin the deck, but their own effects are not executed.

## Next useful work

Combine Trainers' Mail, Tag Call's K1 transition, and Gladion rescue in one exact first-turn policy, then add opponent mulligan bonus draws to that same state model.
