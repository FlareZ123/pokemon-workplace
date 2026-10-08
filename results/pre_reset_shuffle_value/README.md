# Pre-reset shuffle value: when the search-before-reset dominance breaks

## Question

The search-before-reset result proves material equivalence only when deck order is abstracted to an unknown randomized composition.

What happens when the player has information about the upcoming draw window?

The answer is exact.

Implementation: `tools/pre_reset_shuffle_value.py`  
Regression: `results/pre_reset_shuffle_value/reproduce.py`

## Exact threshold

Condition on a singleton target being in an N-card deck.

Let:

- `d` be the number of cards the reset will draw;
- `p` be the player's pre-shuffle probability that the target lies within those next `d` physical deck positions.

If the player resets without shuffling first, direct target exposure is:

`P(hit without shuffle) = p`.

If Quick Ball or another full-deck search shuffles before the reset, the target becomes uniformly distributed over the N deck positions:

`P(hit after shuffle) = d / N`.

Therefore:

`shuffle value = d/N - p`.

The shuffle is neutral exactly when `p = d/N`.

It improves direct exposure when `p < d/N`.

It harms direct exposure when `p > d/N`.

## Harto-sized reset window

The preceding Harto branch has 46 cards in deck before a six-card Dedechange or Squawk and Seize draw when no search target has been removed.

For `N = 46` and `d = 6`:

`d/N = 6/46 = 13.043478%`.

Several informative boundary cases follow.

| Pre-shuffle order belief | Reset-first target exposure | Search/shuffle-first target exposure | Shuffle delta |
| --- | ---: | ---: | ---: |
| Target certainly inside next 6 | 100.000000% | 13.043478% | **-86.956522 pp** |
| Completely exchangeable order | 13.043478% | 13.043478% | 0 |
| Target certainly outside next 6 | 0% | 13.043478% | **+13.043478 pp** |
| Only top card known to be a non-target, remaining 45 positions uniform | 11.111111% | 13.043478% | **+1.932367 pp** |

The known-non-target row uses `5/45`: one of the six draw positions is already occupied by a known miss, while the singleton target is uniform among the other 45 positions.

## Interpretation

The previous material-equivalence theorem remains correct in its declared state projection. Its deck representation intentionally discards physical order.

This result shows why that abstraction is a real boundary rather than a bookkeeping detail.

A mandatory shuffle destroys useful top-deck concentration and erases harmful top-deck concentration. The sign depends on the player's belief about the immediate draw window.

So "Quick Ball is free before Dedechange" needs a precise qualifier:

> its **hand-material payment** can be incrementally free while its mandatory shuffle still has informational or positional opportunity cost.

This separates two resources that a coarse DCI model can accidentally merge:

- hand material;
- deck-order information.

## Relation to existing belief-state work

The repository already contains `prize_top_swap_belief/`, which shows that moving hidden cards between Prizes and the top deck can create cross-zone correlations that independent marginals lose.

The present result is complementary. It asks how much a forced shuffle is worth after the state already contains non-exchangeable top-deck information.

A future unified planner should therefore carry both:

- zone-composition belief;
- deck-position belief when an effect or prior observation makes order strategically relevant.

## Scope

This calculation only values direct exposure of one singleton target in the reset draw.

It excludes:

- K1 Prize information gained by the search;
- other useful cards in the draw window;
- search outputs that deliberately thin the deck;
- discard-pile utility;
- later turns;
- opponent interaction.

Those omitted terms can offset or reinforce the direct shuffle delta.

## Next work

The strongest extension is a joint value model:

`net search-first value = K1 information value + optional search-output value + shuffle delta + other intermediate-state effects`.

That would place the earlier search-before-reset dominance theorem and this deck-order counterweight inside one decision rule instead of treating either as universal.
