# Revealed deck-search targets are Bayesian signals

## Question

If a player fully inspects their deck, learns their Prize composition, and then publicly reveals the card they chose to search for, can that target choice reveal information about hidden Prize cards to the opponent?

Yes.

Implementation: `tools/deck_search_target_signal.py`

Regression: `results/deck_search_target_signal/reproduce.py`

## Concrete search pattern

The bundled card pool contains Quick Ball `swsh1-179`, marked Expanded-legal in the local data. Its search instruction finds a Basic Pokémon, reveals that Pokémon, puts it into hand, and then shuffles the deck.

That reveal creates a public observation after the searcher has privately inspected the deck.

The result is generic over target labels. Quick Ball supplies a concrete example of the information channel.

## Model

The state begins with a position-aware Prize belief.

A target-selection policy maps each possible grouped Prize composition to a probability distribution over publicly observable search targets.

When an opponent observes target t, each supported Prize state s is reweighted by:

`P(t | composition(s))`

and the posterior is normalized.

The searching player already learned the exact Prize composition from full deck inspection. Their own state is therefore conditioned directly on that exact composition. The observed target is checked against the supplied policy, but it does not add uncertainty to the actor.

After the searched card leaves the deck, the deck-plus-Prize pool is reduced by one copy of that target group and by one total card. The post-shuffle top distribution is then derived conditionally on each observer's updated Prize state.

## Six-card witness

Use six labeled cards:

- singleton A;
- singleton search targets X and Y;
- three filler cards.

Two ordered Prize positions are dealt.

The deterministic policy is:

- prefer X when A is Prized and X is available;
- prefer Y when A is unprized and Y is available;
- otherwise use whichever of X or Y is available;
- use a pass branch if both search targets are Prized.

This policy is an abstract strategic line choice. It is designed to isolate the information carried by the public target.

Suppose the opponent observes X.

Across the 15 equally likely unordered two-card Prize sets, exactly 7 produce target X. They are:

- A plus Y;
- A plus one of three fillers;
- Y plus one of three fillers.

Therefore, after observing X:

- P(A is Prized) = 4/7;
- P(Y is Prized) = 4/7;
- P(A and Y are both Prized) = 1/7;
- P(X is Prized) = 0.

The last fact follows from target availability. The first three depend on the actor's target-selection policy.

## Post-shuffle consequence

After X is searched into hand, five cards remain in the deck-plus-Prize pool and three remain in deck.

For the opponent:

- P(top=A) = 1/7;
- P(top=Y) = 1/7;
- P(top=filler) = 5/7;
- P(top=X) = 0.

Now choose one exact actor world where the Prize composition is A plus filler.

The actor's K1 posterior gives:

- P(top=A) = 0;
- P(top=Y) = 1/3;
- P(top=filler) = 2/3.

The two players therefore assign different top-card probabilities to the same shuffled deck because they possess different information about the same exact physical world.

## Exact validation

The opponent regression exhaustively enumerates:

- 6 x 5 = 30 ordered Prize pairs;
- only the pairs whose policy selects X;
- 3 possible shuffled top cards after X is removed.

There are 42 conditioned labeled branches.

The analytic posterior matches every collapsed exhaustive branch probability.

The actor regression separately conditions on exact Prize composition A=1, X=0, Y=0 and matches its exhaustive labeled branches.

The test also supplies an incoherent policy that claims X can be revealed even when the singleton X is Prized. The post-search pool consistency check rejects that policy because removing X from the deck would leave less than the Prized X count.

## Strategic interpretation

Search-target choice can be an information-bearing action.

A simulator that gives the searching player K1 while leaving the opponent's prior unchanged after a public reveal loses information that the opponent can rationally infer from the searcher's behavior.

This is the same broad phenomenon already demonstrated for optional Prize/top swaps: an action selected after private observation can leak information through policy.

The consequence is broader than Prize prediction. If target choice identifies which line the searcher is protecting, it can affect the opponent's gust target, disruption timing, lock choice, Prize planning, or resource allocation.

## Limits

The target-selection policy is supplied externally. The tool does not infer strategic policy from card text or game utility.

The model assumes the target identity is public. Searches that put an unrestricted card into hand without revealing it do not create this same direct target observation.

The current bridge also works at grouped target identity. It does not yet execute a concrete physical search target from `SearchableDeckPhysicalState`.

## Next work

The next integration should bind the observed target to an exact physical search transition.

A combined transaction should:

1. derive the actor's K1 state from physical truth;
2. condition other observers on the publicly revealed target;
3. move that exact target instance from deck to its destination;
4. shuffle and materialize an exact new top;
5. require every observer posterior to retain positive support on the resulting exact world;
6. conserve all card classes across the transaction.

A later policy layer can derive target probabilities from a concrete line evaluator instead of taking them as input.
