# Prize conditioning has distinct ex-ante and exact-hand layers

## Question

How does the pre-search Prize posterior from the belief model reconcile with the repository's earlier result that setup starters and non-starters have different Prize probabilities after mulligan conditioning?

Both are correct at different information levels.

Conditioning only on the event "the opening hand is valid" biases starter and non-starter Prize marginals differently.

Conditioning on the identities of the actual accepted hand removes that class-level asymmetry among cards that are absent from the hand. Every remaining physical card is symmetric with respect to the subsequent random Prize subset.

Reproducer: `results/prize_conditioning_layers/reproduce.py`

## Layer 1: valid-start event only

Before the identities of the accepted hand are specified, suppose the model knows only that the hand satisfied the setup rule.

Prize configurations containing more setup-eligible starters are slightly less likely to be compatible with that event, because those starters were unavailable to make the opening valid.

The existing `results/prize_rescue_start_condition/` result formalizes this effect.

It correctly finds:

- a specific starter has a lower post-mulligan Prize marginal than the unconditional rate;
- a specific non-starter has a slightly higher marginal.

This is an ex-ante posterior over possible accepted hands and Prize sets.

## Layer 2: condition on the actual accepted hand

Now suppose the exact accepted hand `H` is known.

Its cards are known to be outside the initial Prize set.

Conditional on that exact hand, the remaining randomized cards are exchangeable for the subsequent Prize selection.

For:

- deck size `N`;
- accepted hand size `H`;
- Prize count `P`;

any particular physical card absent from the accepted hand has:

`P(card is Prized | exact hand, card absent) = P / (N-H)`

This no longer depends on whether that absent card is a setup starter.

A card present in the accepted hand has Prize probability zero.

## Standard 60-card consequence

With a seven-card accepted opening and six Prize cards:

`P = 6`

`N-H = 53`

Any specific singleton absent from the observed opening hand therefore has:

`6 / 53 = 11.320754717%`

initial Prize probability.

If the singleton is in the opening hand, its Prize probability is zero.

This is the basis for the default `visible_nonprize_cards=7` state in `tools/prize_belief.py`.

The 11.32% figure is conditional on knowing the singleton is absent from the seven-card hand. It should not be confused with the ex-ante post-mulligan marginal of that singleton before the hand identities are known.

## Exhaustive small-deck validation

The reproducer uses a ten-card toy deck:

- starters: S0, S1, S2;
- target non-starter: X;
- six filler non-starters;
- opening hand size 3;
- Prize count 2.

It exhaustively enumerates:

1. every three-card hand containing at least one starter;
2. every two-card Prize subset from the remaining cards.

Across all states conditioned only on a valid opening:

| Target | Prize probability |
| --- | ---: |
| Starter S0 | 16.470588235% |
| Non-starter X | 21.512605042% |

The unconditional marginal would be 20%.

The valid-start event produces the expected starter/non-starter asymmetry.

Next condition on the exact accepted hand:

`{S1, F1, F2}`

Neither S0 nor X is in that hand.

Seven cards remain, and two become Prizes.

Both targets now have:

`2/7 = 28.571428571%`

Prize probability.

Their setup classes no longer matter once their identical visible status is known.

## Why the apparent reversal is coherent

There are three distinct statements.

1. Before setup information, a labeled card has the unconditional Prize marginal.
2. After learning only that setup succeeded, starter status changes the posterior.
3. After learning the exact accepted hand, each absent labeled card shares the same remaining-population Prize probability.

The information in statement 3 is stronger than the information in statement 2.

Bayesian conditioning on a more specific observation can remove an asymmetry that existed under a coarser observation.

## Implication for simulators

The correct posterior depends on what the simulated player actually knows.

A simulator that has generated the exact opening hand should condition Prize beliefs on those exact identities.

It should not continue using only the coarser "valid start occurred" marginals for cards whose hand presence or absence is already known.

Conversely, a pre-game analytic calculation that averages over all possible accepted hands should retain the valid-start conditioning effect.

This distinction matters when comparing:

- ex-ante deck-construction risk;
- the player's in-game belief after seeing the opening hand;
- later beliefs after additional draws and reveals.

## Natural information timeline

A consistent model can use:

`deck-construction prior -> valid-start event -> exact accepted hand -> later visible cards -> partial Prize/deck observations -> exact inspection`

Each arrow conditions the Prize belief on more information.

Prize-zone mutations can later broaden the belief again, as shown in `results/prize_knowledge_nonmonotonic/`.

## Validation

The reproducer independently enumerates the complete small-deck state space rather than relying on the analytic claim.

It asserts:

- the target starter's Prize marginal is below the unconditional 20% after conditioning only on a valid start;
- the target non-starter's marginal is above 20%;
- after conditioning on an exact valid hand containing neither target, both marginals equal `P/(N-H)`;
- the standard 60-card absent-singleton posterior equals `6/53`;
- a singleton visible in the hand has zero Prize probability.

## Limitations

The symmetry claim assumes the exact hand observation fully specifies the setup acceptance event relevant to the player's own deck order.

Unusual setup policies that depend on additional hidden information could require extra conditioning variables.

The result also describes initial Prize selection. Later effects that modify the deck or Prize zone require the dynamic belief kernel.

## Next useful work

The next integration point is the setup simulator.

Instead of reporting only aggregate valid-start Prize marginals, it can emit a `PrizeBelief` conditioned on the exact accepted hand.

That belief can then flow directly into the later observation and decision kernels.
