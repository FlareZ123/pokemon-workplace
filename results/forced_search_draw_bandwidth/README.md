# Mandatory search filler changes draw-to-N bandwidth

## Question

Can a simulator that records only strategically useful search output miscalculate a later draw-until-N effect after an unrestricted exact-count search?

Yes. The mandatory physical filler from an otherwise strategically failed search changes hand size.

Implementation: `tools/search_draw_bandwidth.py`
Regression: `results/forced_search_draw_bandwidth/reproduce.py`

## Concrete Computer Search -> Crobat V witness

Consider a seven-card hand with Computer Search, two payable discard cards, and a Crobat V that will be played later. The intended Computer Search target is unavailable in deck, so the represented strategic output is zero. The deck is otherwise nonempty.

Mechanical hand-size sequence:

1. play Computer Search: 7 -> 6;
2. discard two cards: 6 -> 4;
3. unrestricted exact-one search must take a fallback: 4 -> 5;
4. play Crobat V: 5 -> 4;
5. Dark Asset draws until six: draw 2.

A demand-only miss that moves no search card produces hand size 3 before Dark Asset and predicts draw 3. It overstates the draw by one.

## Hand-size regime

For the same Computer Search cost and one later hand play, with Dark Asset drawing to six:

| Initial hand | Physical draws | Useful-only model | Overstatement |
| ---: | ---: | ---: | ---: |
| 4 | 5 | 6 | 1 |
| 5 | 4 | 5 | 1 |
| 6 | 3 | 4 | 1 |
| 7 | 2 | 3 | 1 |
| 8 | 1 | 2 | 1 |
| 9 | 0 | 1 | 1 |
| 10 | 0 | 0 | 0 |

One forced filler removes exactly one later draw whenever the useful-only hand state is below the draw-to-six ceiling. Once both states are already at or above six, the difference disappears.

## Boundary checks

If the exact-one searched card is itself useful, both representations move one card into hand and the draw counts agree.

If the deck is empty, closest-possible search cardinality is zero, so there is no forced filler and the draw counts agree.

## Relation to connector cost modeling

The repository already shows that connector payment can increase later draw bandwidth by shrinking the hand. This result adds the opposite coupling from search resolution: mandatory filler can decrease later draw bandwidth by refilling the hand even when the current strategic demand was missed.

A scalar connector cost or useful-output vector alone therefore does not determine later draw-to-N volume. The physical post-action hand size does.

## Modeling implication

For continuation-aware planning, a search action should update the physical hand before a later draw-to-N effect is valued. This remains true in branches where the intended strategic target is unavailable.

The same principle generalizes to any hand-size-sensitive effect and to exact-two unrestricted searches that can force more than one non-demand payload.

## Limits

This is a deterministic hand-size coupling model. It does not claim the illustrated Computer Search -> Crobat V sequence is always strategically correct. It isolates the arithmetic consequence conditional on taking that line.

The model also treats the post-search fallback only by count. Which fallback is selected can carry additional discardability, signaling, or continuation value.

## Next work

A deck-specific follow-up can inject mandatory fallback selection into an exact Crobat Dark Asset access model and quantify how often the one-card draw difference changes access to a downstream target.
