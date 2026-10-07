# Deck search and shuffle with a materialized top card

## Question

If another effect has materialized the current deck top as a stable physical instance, what happens when a later effect searches and shuffles that deck?

The top card must remain part of the searchable deck. The search-plus-shuffle boundary can safely remove its special top-position relation before target selection.

Implementation: `tools/deck_search_shuffle_topology.py`  
Regression: `results/deck_search_shuffle_topology/reproduce.py`

## Aliasing problem

The identity layer can represent a known or correlated top card as a materialized instance in zone `deck_top`.

Typed search infrastructure normally queries exchangeable counts in zone `deck`.

If those representations are composed naively, a card sitting at `deck_top` disappears from the searchable population even though it is physically part of the deck.

That can create a false failure when the desired search target is the current top card.

## Safe collapse boundary

A deck search that is followed by a required shuffle destroys the old top position.

`open_deck_for_search()` therefore:

1. moves the old top instance into the general deck;
2. dematerializes that relation-free copy into the exchangeable deck count;
3. leaves Prize instances and every other materialized relation unchanged.

The regression begins with A and B exchangeable in deck and C materialized as the top.

After opening the deck for search, A, B, and C each appear in the exchangeable deck population.

## Exact searched target

`search_deck_card_to_play()` can then materialize one selected exact card class directly from deck into a concrete board object.

The regression deliberately chooses C, the former top. This is the target that a naive split representation would have missed.

## Post-shuffle top

After search resolution, `finish_shuffle_with_sampled_top()` takes one caller-supplied sampled class from the remaining exchangeable deck and materializes it as the new `deck_top`.

This represents one deterministic branch of a shuffle outcome while preserving exact material conservation.

## Finding

Top-of-deck position is a temporary physical relation, not a separate card population.

Search and shuffle provide a natural boundary where that relation can be collapsed. The old top must rejoin the searchable deck before target selection, and a new top relation can be materialized only after the shuffle outcome is chosen.

## Limits

This kernel handles physical truth only.

It does not yet compute the probability of each possible post-shuffle top class.

Observer beliefs require a conditional distribution because uncertain Prize composition changes the remaining deck composition. Treating the new top as independent of Prize state is generally wrong.

The module also assumes the search effect is followed by a shuffle. Effects that inspect or reorder the deck without shuffling need a stronger ordered-deck representation.

## Next work

Build the corresponding belief transition. For each possible Prize composition, derive the remaining deck counts and sample the new top conditionally from those counts. This will preserve composition/top correlation for observers who have not reached K1 while allowing a K1 observer's posterior to sharpen appropriately.
