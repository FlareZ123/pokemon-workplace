# Prize-taking conservation and belief updates

## Question

When a player takes a face-down Prize card into hand, how should a simulator update both the exact hidden-zone truth and that player's uncertainty about the remaining Prize cards?

Implementation: `tools/prize_take_conservation.py`  
Regression: `results/prize_take_conservation/reproduce.py`

## Why this is a separate transition

The post-Knock-Out resolver can determine how many Prize cards a player takes and whether that ends the game, but a count alone does not identify which physical cards moved.

The existing `IdentityLedger` can represent exact exchangeable card-class counts by zone. The existing `PrizeBelief` can represent a probability distribution over grouped Prize compositions. Before this result, those two layers did not share a Prize-taking transition.

A complete state update needs both:

1. exact hidden truth: one physical card class moves from `prize` to `hand`;
2. player information: the taken card is now known to that player, so the belief conditions on its observed group and removes it from the remaining Prize set.

## Bayesian removal transition

`take_observed_random_prize()` treats the current face-down Prize positions as exchangeable, consistent with the existing grouped belief kernel.

For each possible Prize-composition state:

1. weight the state by the fraction of Prize positions containing the observed group;
2. condition on that observation;
3. decrement the observed group's count, or only the filler count when the card is outside the modeled groups;
4. reduce `prize_count` by one;
5. merge any posterior states that become identical and normalize their probability mass.

This differs from `PrizeBelief.observe_random_position()`, which reveals a Prize card while leaving it in the Prize set.

`take_observed_prizes()` applies the removal transition repeatedly for multi-Prize awards.

## Labeled toy validation

The regression independently enumerates every two-card Prize subset from the five labeled cards:

`A, B, F1, F2, F3`

and then every equally likely choice of one Prize position.

The exact labeled calculation gives:

- probability the next taken Prize is A: `1/5 = 20%`;
- after observing and removing A, probability B is the remaining Prize: `1/4 = 25%`.

The grouped `PrizeBelief` transition reproduces both values exactly.

After then taking a filler Prize, the Prize count becomes zero and the posterior collapses to the unique empty composition.

The regression also checks the reversed observation order for the same two observed cards and reaches the same terminal empty-Prize belief.

## Physical conservation bridge

`take_exact_prize_cards()` moves exact card classes from the exchangeable `prize` count into `hand` and asserts that per-class totals are unchanged.

`take_prizes_and_update_belief()` composes the physical and informational transitions.

Its input pairs each exact underlying card class with the strategic belief group observed by the player. The caller owns that semantic mapping because the grouping depends on the research question.

The regression uses an exact hidden state where the two physical Prizes are A and a filler card while the player begins from the uncertain five-card hypergeometric prior.

After taking A:

- the exact A card class is in hand;
- one filler physical Prize remains;
- the player's posterior still assigns 25% probability that B is the remaining Prize because the player has not observed that second card.

After taking the filler:

- both exact physical cards are in hand;
- the physical Prize count is zero;
- the grouped belief also has zero Prize positions and is exact.

Physical card totals remain invariant throughout.

## Finding

Prize taking is simultaneously a material transition and an information transition.

Moving a card from `prize` to `hand` without updating the belief leaves stale uncertainty. Conditioning on an observed Prize without moving the physical card leaves the hidden-zone truth wrong.

The two layers should therefore advance together at the boundary where a Prize card becomes part of the player's hand.

## Relationship to prior work

This fills one explicit limitation in both:

- `results/prize_belief_kernel/`, which previously had no Prize-removal action;
- `results/post_knockout_game_resolution/`, which tracks Prize counts but not the physical identities moved to hand.

It also fits the repository's broader materialization principle: exchangeable hidden cards can remain aggregated by class and zone until mechanics require more identity.

## Limits

The transition assumes Prize positions are exchangeable with respect to identity. Position-specific information from earlier effects requires a richer belief representation.

The player's observed strategic group is supplied by the caller. This adapter does not infer card semantics from the database.

Only the taking player's belief is updated. An opponent normally does not learn the private identity of a face-down Prize card merely because it entered the other player's hand, so opponent knowledge requires its own observation model.

The physical ledger aggregates exchangeable Prize copies by card class and does not assign persistent identity to individual face-down Prize positions.

Prize awards are supplied elsewhere. This module does not determine how many Prizes a Knocked Out Pokémon is worth or apply Prize-modifying effects.

## Next work

The next composition step is to connect this transition to the post-Knock-Out phase so an awarded Prize count selects exact hidden Prize cards, updates the taker's belief, evaluates the terminal game state, and requests replacement-Active choices only if the game continues.
