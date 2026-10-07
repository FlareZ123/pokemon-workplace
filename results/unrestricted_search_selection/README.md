# Unrestricted deck-search cardinality: useful outputs are not physical selections

## Question

When a card searches the deck for an unrestricted `card` or fixed number of `cards`, can a state planner materialize only strategically useful targets?

No. The Advanced Player's Rulebook gives unrestricted deck search a distinct selection rule. Once an unrestricted fixed-count search occurs, the player must take the stated number of cards. If fewer cards remain, the closest-possible rule reduces the physical take to the remaining deck size.

Implementation: `tools/unrestricted_search_selection.py`
Regression: `results/unrestricted_search_selection/reproduce.py`

## Rulebook basis

H. Deck says ordinary searches may select fewer cards, including zero. It then gives an explicit exception for searches for any card or cards without a type limitation: the specified number must be selected. The card-text rules also say that if a specified quantity is unavailable, apply the closest possible number.

This yields two local cardinality laws:

- restricted fixed search: minimum 0, maximum `min(specified_count, eligible_count)`;
- unrestricted fixed search: minimum and maximum `min(specified_count, deck_size)`.

This result excludes `up to N` wording from the exact-count semantic island.

## Snapshot catalog

The conservative scan finds **69 effectively legal Expanded print-level effects across 43 names** matching literal exact unrestricted search wording.

| Source | Effects |
| --- | ---: |
| Pokémon attacks | 27 |
| Abilities | 22 |
| Trainer rules | 20 |
| **Total** | **69** |

There are 63 exact-one effects and 6 exact-two effects. Destinations are 56 to hand and 13 to the top of the deck.

The Trainer-rule rows span 11 names: Camping Gear, Ciphermaniac's Codebreaking, Computer Search, Cram-o-matic, Delivery Drone, Farewell Bell, Mallow, Raihan, Red's Challenge, Reserved Ticket, and Reversal Trigger.

The six exact-two rows are two Mallow prints, three Ciphermaniac's Codebreaking prints, and Dialga `sv8-135`'s Time Manipulation attack.

## Computer Search counterexample

Suppose the strategically desired singleton is absent while two unrelated cards remain. A target-only abstraction may emit a zero-output branch after the search cost is paid.

That physical transition is wrong. Computer Search uses an unrestricted exact-one search. Once the search occurs and the deck is nonempty, one physical card must be selected.

The reproducer finds exactly two grouped witnesses, one for either fallback card. There is no zero-card witness.

The strategic objective may still fail, yet the forced card changes hand contents, deck size, discard capacity, future draws, and continuation provenance.

## Exact-two counterexample

Mallow searches for two cards, shuffles, then places those cards on top in any order. With one desired card and two fillers remaining, the exact physical witnesses include desired plus filler and two fillers. There is no legal one-card selection.

A useful-output vector can therefore have one supplied demand unit while the physical selected-card count is two.

## Architectural implication

An unrestricted fixed search needs a physical-selection witness in addition to a useful-output vector. A complete action witness should preserve:

- strategically useful output;
- all physically selected cards;
- mandatory filler selections;
- destination and ordering of filler cards.

This distinction matters before composing search with zone conservation, discard replenishment, hidden-state updates, top-deck planning, provenance, or multi-turn continuation value.

The existing single-output compiler covers selector-limited searches such as Quick Ball and Ultra Ball. Those hidden-deck searches retain a legal zero-selection branch. Treating unrestricted `card` as merely the broadest selector would erase the nonzero minimum and should be avoided.

## Validation

The regression checks the 69-effect / 43-name snapshot, source/count/destination distributions, representative Computer Search, Mallow, and Dialga effects, forced fallback selection, forced second-card filler selection, legal zero-selection on restricted search, and closest-possible behavior when the deck is short.

## Limits

The parser is literal. It excludes `up to N` unrestricted wording, unusual historical phrasings, destinations outside hand/top-deck in the captured family, activation gates, and reprint-equivalent prints outside the direct Expanded set universe.

## Next useful work

The next integration is a physical-selection layer for unrestricted search execution. For exact-two search, every selected card should materialize even when only one satisfies the current strategic demand. Ordered top-deck payloads can then feed the existing top-card belief machinery.
