# Optional Arc Phone exchange and target rescue

## Exact two-Prize witness

Two face-down Prize positions contain one target `T` and one filler `F` in unknown physical order. The deck has three fillers, and the hand has two Arc Phone and one Trekking Shoes.

Play Arc Phone to exchange the top filler with one physical Prize slot. Play the second Arc Phone to **inspect** the newly outgoing top card. If it is `T`, decline the optional exchange; if it is `F`, exchange with the untouched Prize slot, which must have `T`. Finally use Trekking Shoes to take the top `T`.

The legal policy succeeds in both layouts, probability **1**. A deliberately restricted comparator requiring every Arc Phone to complete a swap succeeds with probability **1/2**. The optional clause thus changes this state's objective probability by **50 percentage points**. This is a controlled counterfactual, not an estimate of a real deck's win rate.

Card-text anchors: Arc Phone `swsh11-152` explicitly states *you may switch* after inspecting the top; Trekking Shoes `swsh10-156` can take top into hand. See [Arc Phone](https://asia.pokemon-card.com/sg/card-search/detail/2749/) and [Trekking Shoes](https://asia.pokemon-card.com/sg/card-search/detail/3614/).

## Exhaustive bounded comparison

Implementation: `tools/arc_phone_optional_swap_policy.py`. Verification: `results/arc_phone_optional_swap_policy/reproduce.py`. The comparator shares the physical Prize/deck posterior and both Shoes modes with [the finite deck-order model](../arc_phone_deck_order_policy/); it changes only the ability to decline Arc Phone's exchange after seeing top.

All grouped 2-, 3-, and 4-Prize states with one `T` Prized, three unknown deck cards drawn from `A,S,F`, and one to three initially accessible copies of each Item were enumerated. States exceeding four total copies of Arc or Shoes across all zones were excluded.

| Prizes | States checked | Optional strictly better | Maximum gain |
| ---: | ---: | ---: | ---: |
| 2 | 164 | 29 | 1/2 |
| 3 | 251 | 101 | 1/3 |
| 4 | 305 | 156 | 1/4 |

The states are equally weighted as *cases*, and are not a frequency model for real games. An independent labeled-world oracle confirms the two-Prize forced policy at `1/2`; the previously verified legal solver confirms the optional value of `1`.

## Research consequence

A card compiler must keep Arc Phone's observation and optional material effect as separate action phases. Choosing whether to swap is permitted after learning top. A planner that always executes the nominal swap loses legal information-contingent options, even when the card and every required resource are in hand.

Additional constraints not modeled include opponent action, locks, card searches, and the strategic value of fillers used as incoming replacement Prizes.
