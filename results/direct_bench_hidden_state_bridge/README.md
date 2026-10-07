# Hidden-state bridge for direct-Bench Trainer search

## Question

Does a direct deck-to-Bench search still create the same K1 and public target-selection information effects as a reveal-to-hand search?

For a single public target such as Nest Ball, yes.

Implementation: `tools/direct_bench_hidden_state_bridge.py`  
Regression: `results/direct_bench_hidden_state_bridge/reproduce.py`

## Composition

The bridge starts from a searchable physical deck state whose exact Prize instances are known to the simulator but represented through observer-relative beliefs.

It then composes:

1. the searching player's full-deck inspection and exact Prize-composition inference;
2. a target-selection policy conditioned on that private Prize information;
3. the publicly observable chosen Basic Pokémon;
4. the atomic direct-Bench Trainer transaction;
5. removal of the selected target from the deck/Prize pool;
6. the following shuffle and one exact sampled top card;
7. truth-support validation for every observer posterior.

The searched Pokémon remains in play throughout the post-search state. It is never represented in hand.

## Public target signaling

Nest Ball does not need literal `reveal it` wording for the selected identity to become public. The chosen Pokémon is placed face up onto the Bench as part of resolving the effect.

The same target-signal Bayesian layer used for revealed hand searches therefore applies to the public selection policy, while the physical destination remains different.

## Exact witness

The deterministic regression uses six hidden-zone cards:

- singleton A;
- singleton searchable Basics X and Y;
- three filler cards.

The exact material world has A and one filler Prized, X and Y in deck, and Nest Ball in hand. The policy prefers X when A is Prized and Y when A is not Prized.

Observing X therefore carries information about A's Prize status.

After Nest Ball places X directly onto the Bench and the deck is shuffled with Y materialized as the sampled top:

- the actor's posterior has `P(top=Y)=1/3`;
- the other observer's posterior has `P(top=Y)=1/7`;
- X is an in-play board instance rather than a hand instance;
- Nest Ball is in discard;
- Y is the exact `deck_top` instance;
- both observer posteriors retain positive probability on the exact world;
- board state and hidden physical state share the same final identity ledger;
- all card-class totals are conserved.

These posterior values match the analogous single-target revealed-search geometry because the information event is the same target choice, while the destination state is different.

## Strategic consequence

Search destination and information leakage are separate dimensions.

Two effects can produce the same public target signal and the same K1 posterior update while leaving materially different gameplay states. A hand-search route preserves a card in hand; Nest Ball commits it immediately to the Bench.

A simulator should therefore avoid encoding `public target` as synonymous with `target moved to hand`.

## Boundaries

The bridge currently requires exactly one selected target.

Battle VIP Pass and other multi-target direct placements need a policy model over ordered or unordered target sets before their signaling can be represented without inventing information.

The bridge also assumes the deck is already in searchable unordered form. Opening an existing materialized deck top before search remains the responsibility of the deck-search topology layer.
