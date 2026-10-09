# Peonia-first position memory in a full-deck Arc Phone rescue

## Question

How much does the absence of a Prize shuffle after Peonia matter when the later Arc Phone/Trekking Shoes retrieval policy is optimized against an actual finite deck, including Shoes' discard-and-draw mode and recovery of Items found on the deck top?

The difference can be large even under the same *known initial Prize composition*.

## Controlled conserving 60-card state

Start with six face-down Prizes containing a known singleton `T` and five target-irrelevant filler cards `F`, but unknown positions. The deck contains 47 cards: two Arc Phone `A`, two Trekking Shoes `S`, and 43 fillers, with unknown top order. The hand has a Peonia, two Arc Phone, two Trekking Shoes and one spare filler; one Basic filler is already Active. These zones account for 60 physical cards. All Items are usable and no other Supporter action is required.

Playing Peonia first selects three physical Prize slots, bringing those cards to hand and returning exactly three hand cards as face-down Prizes. On a target hit, the initially held filler suffices to keep `T` while returning the other selected fillers. On a miss, all selected cards are known fillers, can be returned to their own slots, and the target is known to reside among the three untouched positions. Peonia does **not** require shuffling those Prizes.

The later Item decisions use [the exact exchangeable-deck-tail solver](../arc_phone_lazy_deck/), which preserves physical Prize exclusions, deck-top uncertainty, and both Shoes effects. The player optimizes each Arc Phone look-before-optional-swap and each Shoes take/discard choice.

## Exact result

| Policy | Probability T reaches hand |
| --- | ---: |
| Arc Phone + Shoes, without Peonia | `111820/321057 = 34.828706%` |
| Peonia checks three positions first, then Items | `544697/642114 = 84.828706%` |
| Hypothetical full Prize shuffle after a Peonia miss, then Items | `432877/642114 = 67.414353%` |

Preserving Peonia's actual physical-position exclusions is worth **`55910/321057 = 17.414353` percentage points** versus the shuffle-after-miss counterfactual.

This comparison is conditional on the complete current hand, board, Prize composition and deck composition. It measures an isolated retrieval line and is not an estimate of real-game setup reliability or competitive win rate.

## Why the gain appears

Peonia chooses three of six physical slots. Its immediate target probability is 1/2. After missing, the target is known to be among three untouched slots. The Item policy therefore spends its subsequent probes on still-possible positions.

A hypothetical shuffle after the miss would put the singleton back into any of six positions. Although its *composition* is unchanged, the player loses which three positions Peonia ruled out. Conditional on Peonia missing, the adaptive Item continuation is therefore much weaker.

The genuine card text for Peonia `swsh6-149` instructs card replacement and does not instruct a Prize shuffle. An official [Pokémon Asia Peonia Q&A](https://asia.pokemon-card.com/id/rules/search/?keyword=N&pageNo=68) confirms that replacement Prize cards need not be shuffled and may be placed in the chosen order. Arc Phone `swsh11-152` and Trekking Shoes `swsh10-156` supply the subsequent observation, swap, and draw actions.

## Verification

Implementation: `tools/peonia_arc_lazy_policy.py`. Regression: `results/peonia_arc_lazy_policy/reproduce.py`.

For four small physically enumerated Prize/deck fixtures, an independent full-order exact solver enumerates all legal Peonia-selected subsets of zero through three cards, conditions on actual observed target hits or misses, and optimizes the Item continuation. The compact solver agrees for every tested combination. The full 60-card results and their difference are asserted as exact rational fractions.

## Limits and next work

Peonia is fixed as the first action, and the initial non-target Prizes are all filler. The policy does not optimize playing Peonia *after* an Arc Phone has moved a useful Item into a Prize slot, where Peonia could retrieve that Item at some replacement cost. This is an important possible sequence-dependence effect for a stronger integrated solver. Other omissions include ordinary search/draw, opponent interference, locks, and valuation of replaced filler cards.
