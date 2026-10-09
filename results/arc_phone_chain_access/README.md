# Arc Phone chaining: one final draw can resolve several Prize probes

## Question and verified card semantics

Can several consecutively played Arc Phone Items probe distinct face-down Prize positions with only one Trekking Shoes used at the end? Yes, conditionally. Arc Phone (`swsh11-152`) looks at the current deck top before optionally exchanging it with one face-down Prize card. After an exchange, the next Arc Phone looks at the *previously outgoing Prize card*. If it is the target, the player can decline the second exchange and use Trekking Shoes (`swsh10-156`) to take the top card. If it is not the target, the player can exchange it with a previously untested Prize slot. Both are Items, so this sequence does not use another Supporter action.

Source texts: [official Arc Phone](https://asia.pokemon-card.com/sg/card-search/detail/2749/), [official Trekking Shoes](https://asia.pokemon-card.com/sg/card-search/detail/3614/), and [official Peonia](https://asia.pokemon-card.com/sg/card-search/detail/1564/). The bundled prints are marked Expanded-legal, though deck-level legality and current tournament restrictions remain independent checks.

## Fixed-access result

Assume six face-down Prizes, one target singleton known to be Prized, an otherwise irrelevant top-of-deck card, and sufficient expendable cards to pay Peonia's replacements. Peonia takes three chosen Prize cards. If the target is among them, it stays in hand. Otherwise their replaced physical slots are known non-target positions and three untested slots remain.

With **three Arc Phone and one Trekking Shoes already in hand** after Peonia, the chained policy probes each untouched position at most once and retrieves the target with **100% conditional probability**. The same three Arc Phone with a deliberately restricted policy requiring a *different Trekking Shoes after every probe* can test only one position when only one Shoes is accessible, yielding **4/6 = 66.666667%** including Peonia. In the fixed-resource comparison, chaining thus saves two Trekking Shoes and increases same-turn target access by **33.333333 percentage points**.

This is a conditional legal-action witness, not a competitive consistency estimate. It assumes Item access, no Item lock, permission to keep the retrieved target, and a usable final deck-top draw. The card swapped from the deck into the Prize zone can have strategic value outside this objective.

## Exact hand/Prize population study

Implementation: `tools/arc_phone_chain_access.py`. Regression: `results/arc_phone_chain_access/reproduce.py`.

The illustrative 60-card population is **1 target, 1 Peonia, 4 Arc Phone, 4 Trekking Shoes, 50 grouped fillers**. Condition on the singleton target being among the initial six Prizes. The other five Prizes are sampled without replacement; then an accessible hand window of `d` cards is sampled without replacement from the remaining 54. This deliberately omits mulligans, opener Basic restrictions, ordinary search/draw, active lock effects, and Supporter acquisition after that hand window.

The policy knows initial Prize *composition* (K1), while its physical Prize positions remain hidden. It may play Peonia for one, two, or three positions or skip Peonia. After seeing cards taken by Peonia, it must return exactly as many cards from hand to known positions. The model optimizes those payments, first preserving strategically neutral filler where possible. Peonia can incidentally retrieve Arc Phone or Trekking Shoes that started Prized. A target taken by Peonia counts as successfully kept only if a different hand card can be returned in its place.

A chained policy uses a series of distinct Arc Phone probes with one final Trekking Shoes. A controlled comparator uses a separate Trekking Shoes for every Arc Phone probe and does **not** credit follow-up Items gained through those intermediate Shoes. That restriction matters: real intermediate Shoes can put a revealed Arc Phone or another Shoes in hand, enabling further plays. The comparator is a defined policy class, not an optimized all-legal-actions baseline.

| Accessible hand cards `d` | Chained policy | Restricted per-probe Shoes | Chaining gain |
| ---: | ---: | ---: | ---: |
| 7 | 9.106102882% | 8.718450599% | +0.3876523 pp |
| 10 | 14.688731236% | 13.641616046% | +1.0471152 pp |
| 13 | 20.877584509% | 18.897862778% | +1.9797217 pp |
| 16 | 27.454249200% | 24.380362545% | +3.0738867 pp |

The full-population figures are conditional on the target having been Prized. They are acquisition probabilities under the narrow policy model, not win-rate or real-game setup estimates. They include the probability that Peonia and relevant Items themselves occupy inaccessible Prizes.

## Validation

A separate labeled enumeration for a ten-card toy deck (`1 target, 1 Peonia, 2 Arc Phone, 2 Shoes, 4 fillers`), with three Prizes and hand windows of one through four cards, reproduces the grouped exact model. It enumerates the physical Prize permutations, hand combinations, Peonia observations, and every candidate replacement-card subset. All eight chain/per-probe comparisons agree as exact `Fraction` values. The bundled card data checks validate card text and Expanded flags for `swsh11-152`, `swsh10-156`, and `swsh6-149`.

## Open next step

Build an execution-level planner where Trekking Shoes can retrieve useful Trainer cards mid-chain or draw a different card after discarding the exposed top, rather than treating all newly exposed non-target cards as inert. Incorporate top-of-deck resource protection and card-specific restrictions. Compare that fully adaptive policy with the fixed-resource chain before giving deck-building recommendations. The existing `prize_position_belief`, `prize_top_draw_belief`, and `prize_position_policy` modules provide useful foundations.
