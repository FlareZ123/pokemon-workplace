# Physical deck-search/shuffle belief bridge

## Question

Can the K0/K1 search-shuffle belief update be tied directly to the repository's exact physical identity ledger without separately supplying the actor's Prize composition or the deck-plus-Prize pool counts?

Yes.

Implementation: tools/deck_search_shuffle_physical_belief.py

Regression: results/deck_search_shuffle_physical_belief/reproduce.py

## Composition

This result composes:

- SearchableDeckPhysicalState from tools/deck_search_shuffle_topology.py;
- the observer-relative search/shuffle belief transition from tools/deck_search_shuffle_belief.py;
- exact physical top/Prize grouping and truth-support checks from tools/top_prize_physical_bridge.py;
- the shared IdentityLedger conservation layer.

The physical searchable state is the phase after the old top relation has been collapsed into the unordered deck and before the new shuffled top has been materialized.

## Derived state

The bridge derives two quantities from physical truth.

First, it counts the exact grouped composition of the materialized Prize instances. This is the K1 composition the searching player can infer from a full deck inspection.

Second, it scans all exchangeable and materialized cards still in deck or Prize zones to obtain:

- modeled group counts in the current deck-plus-Prize pool;
- total pool size, including unmodeled filler.

Cards already moved to hand, play, discard, Lost Zone, or another public zone are naturally excluded.

Those derived values feed the observer belief transition. The searching actor conditions on the exact Prize composition. Other observers retain their existing priors.

## Exact top materialization

The caller supplies one exact sampled top card class from the remaining unordered deck.

The existing physical shuffle kernel materializes that copy and moves it to deck_top. The bridge then projects the resulting exact top and Prize instances into the modeled groups and requires every observer posterior to assign positive probability to that physical world.

This keeps three layers synchronized:

1. exact physical card identity;
2. observer-relative hidden-state belief;
3. grouped strategic abstraction.

## Regression witness

The five-card pool contains:

- one A;
- two B;
- two filler cards.

The exact physical Prize zone is A plus one filler, leaving both B copies and one filler in the deck.

The bridge derives:

- exact actor Prize counts: A=1, B=0;
- current group pool counts: A=1, B=2;
- pool size: 5.

A B copy is then sampled as the exact post-shuffle top.

The actor's K1 belief gives B top probability 2/3. The uninformed observer's K0 belief gives B top probability 2/5. Both assign positive probability to the exact world:

top=B, Prizes=(A, filler).

Per-class card totals are identical before and after top materialization.

## Failure witness

The same state attempts to sample the singleton A as the new deck top.

The physical kernel rejects the transition because A is materially in the Prize zone and no exchangeable A copy exists in the deck.

This is a useful cross-layer check. The actor belief already gives top=A probability zero, and the physical ledger independently prevents the impossible materialization.

## Strategic interpretation

A full deck search should update more than a Boolean K0/K1 flag.

Once the exact Prize composition is learned, the player's probability distribution over future shuffled draws changes immediately. The physical ledger can supply the exact conditioning event, while the grouped belief layer can represent the strategic consequences without duplicating card instances.

This also gives a reusable simulator invariant: every observer belief must retain support on the exact material world after a hidden-state transition.

## Limits

The bridge currently receives the sampled exact top card as a deterministic branch. It does not perform random sampling itself because the belief kernel already represents the full probability distribution and deterministic branch selection is easier to reproduce.

The model also assumes that any information carried by the search target itself has already been handled. A publicly revealed target selected after private deck inspection can convey additional information about the searcher's hidden state or policy.

## Next work

The next information problem is search-target signaling.

When several legal targets are available and the searcher chooses after seeing the complete deck, an opponent can update from the publicly revealed chosen target. That update depends on the searcher's selection policy, just as an optional Arc Phone swap can reveal information through the actor's decision.

A useful next result would condition the opponent's Prize/top posterior on a target-selection policy while keeping the actor's K1 state and the exact physical search transaction synchronized.
