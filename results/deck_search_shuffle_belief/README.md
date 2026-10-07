# Deck-search/shuffle belief transition

## Question

When a player fully inspects their deck and then shuffles, how should a hidden-state model update both Prize knowledge and the distribution of the new top card?

The physical search/shuffle result already established that a materialized old top card must collapse back into the unordered searchable deck before target selection. Its open gap was informational: the new top cannot generally be sampled independently of uncertain Prize composition.

Implementation: tools/deck_search_shuffle_belief.py

Regression: results/deck_search_shuffle_belief/reproduce.py

## Rules and strategic basis

The Advanced Player's Rulebook section H states that the searching player may look through the contents of their deck while searching, and that a search which looks through the deck is followed by a shuffle.

For a player who knows their own decklist and visible zones, full deck inspection can reveal which missing cards are in the Prize cards. This is the K0 to K1 transition described in resources/human_concepts.md and quantified by results/prize_information_value/.

The shuffle creates a second hidden-state question. If a singleton is known to be Prized, it cannot also be the next deck-top card. If its Prize status is still uncertain, the observer's top-card distribution must remain correlated with that uncertainty.

## Model

The input Prize state is position-aware.

For each observer-supported Prize state s:

1. count how many copies of every modeled group are in s;
2. subtract those copies from the current deck-plus-Prize pool counts;
3. derive the remaining unordered deck counts;
4. sample the new top card from those remaining counts;
5. retain the original Prize positions in the same joint support state.

If D is the number of cards remaining in the deck after fixing s, then for group g:

P(top = g | s) = remaining_deck_count(g, s) / D

The searcher first conditions their Prize belief on the exact composition learned from deck inspection. Other observers keep their existing Prize prior unless some separate public observation gives them additional information.

The result therefore produces one TopPrizeJointBelief per observer rather than one marginal top distribution.

## Exact toy witness

Use five labeled cards:

- A1;
- B1 and B2;
- F1 and F2 as unmodeled filler.

Two ordered Prize positions are dealt, leaving three cards in the deck.

Before any private deck inspection, an observer who only knows this pool has the following post-shuffle top marginals:

- P(top=A) = 1/5;
- P(top=B) = 2/5;
- P(top=filler) = 2/5.

Now suppose the acting player fully inspects the remaining deck and infers that the exact Prize composition contains one A and no B.

Their next-top distribution becomes:

- P(top=A) = 0;
- P(top=B) = 2/3;
- P(top=filler) = 1/3.

No card was recovered. The change comes only from information.

## Correlation witness

For the uninformed observer, both of these marginals are positive:

- P(top=A) = 1/5;
- P(Prize slot 0=A) = 1/5.

Their product is therefore positive.

The true joint probability is exactly:

P(top=A and Prize slot 0=A) = 0

because the pool contains only one A copy.

A model that samples a post-shuffle top independently from the Prize belief invents impossible worlds.

## Validation

The reproducer performs an independent labeled-card exhaustive enumeration.

It enumerates every ordered pair of distinct Prize cards from the five-card pool, collapses those exact identities into A/B/filler groups, and builds the input positional Prize belief.

It then enumerates every ordered triple:

Prize slot 0, Prize slot 1, post-shuffle top

over distinct labeled cards. There are 5 x 4 x 3 = 60 exact branches.

The analytic joint belief matches every collapsed exhaustive branch probability.

A second exhaustive comparison conditions on the actor's exact K1 composition of one A and zero B. The actor's analytic posterior again matches every conditional labeled branch.

The regression also rejects an impossible claimed exact Prize composition.

## Strategic interpretation

The first full deck search is both a material connector action and an information event.

After K1, a player can update probabilities for future random draws from the deck because the inferred Prize composition changes the remaining deck composition. This matters even when the card searched for is strategically ordinary.

The effect is strongest for low-copy resources. A singleton known to be Prized immediately has zero next-draw probability until some later transition moves or reshuffles that copy back into the deck.

This also gives a concrete reason to preserve joint hidden-zone state. Prize composition and future deck-top identity are mechanically anti-correlated through finite card multiplicities.

## Limits

This kernel starts after the currently relevant deck-plus-Prize pool has been defined.

It does not yet infer those pool counts from the physical ledger, and it does not model information carried by the identity of a publicly revealed search target. A target choice made after private deck inspection can itself be policy-censored evidence for an opponent, analogous to the optional Arc Phone signaling already modeled elsewhere.

The tool also models the new top after a full shuffle. Effects that reorder or inspect the deck without shuffling require an ordered-deck representation.

## Next work

The next physical integration should derive the actor's exact Prize composition and the current pool counts directly from SearchableDeckPhysicalState, sample one exact new top instance, and verify that every observer posterior retains support on that exact physical world.

A later information layer should model publicly revealed search targets and selection policy, because observing which card the searcher chose can update an opponent's posterior even when the rest of the searched deck remains private.
