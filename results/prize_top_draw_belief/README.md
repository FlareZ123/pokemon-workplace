# Correlated top draw after a Prize swap

## Question

When Arc Phone moves an uncertain Prize card to the top of the deck, what information update should occur when that top card is immediately observed or drawn?

The answer depends on the **joint** top-deck and Prize posterior.

Implementation: `tools/prize_top_draw_belief.py`

Regression: `results/prize_top_draw_belief/reproduce.py`

This result composes agent41's validated `TopPrizeJointBelief` with a later top-card observation. It does not duplicate the Arc Phone swap transition itself.

## Motivating line

A concrete same-turn Expanded sequence is:

`Peonia -> Arc Phone -> Trekking Shoes`.

The bundled Trekking Shoes print `swsh10-156` says:

`Look at the top card of your deck. You may put that card into your hand.`

After Arc Phone, the outgoing Prize identity can be uncertain while remaining correlated with the untouched Prize positions. Trekking Shoes reveals that outgoing top card and may put it into hand.

That observation must condition the remaining Prize posterior before the joint top variable is discarded.

## Minimal regression

Start with two face-down Prize positions containing exactly:

- one A;
- one B.

Their physical order is unknown.

The known incoming top card is X. Arc Phone switches X with Prize slot 0.

The validated joint swap kernel produces:

- 50%: top A, Prizes X + B;
- 50%: top B, Prizes X + A.

Both top marginals are 50/50.

The untouched Prize slot is also marginally 50/50 A/B.

Those marginals are strongly correlated.

## Drawing top A

If Trekking Shoes reveals and takes top A:

- observation probability: 1/2;
- selected Prize slot remains X with certainty;
- untouched Prize slot becomes B with certainty.

The posterior probability that A remains in the untouched Prize slot is zero.

## Drawing top B

If Trekking Shoes reveals and takes top B:

- observation probability: 1/2;
- selected Prize slot remains X with certainty;
- untouched Prize slot becomes A with certainty.

Again, the top observation resolves the correlated hidden Prize identity.

## Why independent marginals fail

Suppose a simulator had projected the post-Arc state into two independent summaries:

- top deck: 50% A, 50% B;
- untouched Prize: 50% A, 50% B.

After observing top A, an independent-Prize marginal would still assign 50% probability that the untouched Prize is A.

The true probability is zero.

The error is therefore a Bayesian state-update failure, even though both pre-observation marginals were individually correct.

## Transition API

`draw_observed_top(state, observed_group)` returns:

- the drawn strategic group;
- the probability of that top observation;
- the remaining position-and-visibility Prize posterior conditioned on the observation.

`top_draw_outcomes(state)` enumerates every possible grouped top observation with nonzero probability.

The physical card movement into hand remains outside this information kernel. The existing material-state layers should own exact zone movement.

## Relationship to the Peonia positional policy

The Peonia position result shows when Arc Phone can choose a higher-value physical Prize slot.

The Arc Phone joint-swap result shows that the outgoing top identity remains correlated with untouched Prizes.

This adapter supplies the next observation step.

Together, these layers support a position-aware same-turn line:

1. Peonia changes which physical Prize slots are known or ruled out.
2. Arc Phone selects one eligible face-down slot.
3. The swap creates a correlated top/Prize belief.
4. Trekking Shoes observes and can take the new top card.
5. The remaining Prize posterior updates using that observation.

This is a materially stronger representation than treating `TARGET Prized`, `top TARGET probability`, and `remaining TARGET probability` as independent scalars.

## Validation

The regression:

- verifies the bundled Trekking Shoes text;
- constructs the exact A/B unknown-order Prize state;
- uses the existing `swap_known_top_with_face_down_prize()` transition;
- confirms the 50/50 top marginal;
- conditions on top A and proves untouched Prize B with probability 1;
- conditions on top B and proves untouched Prize A with probability 1;
- verifies the enumerated draw-outcome probabilities sum to one.

## Limits

This is an acting-player belief transition.

Observer-indexed top-draw information can differ when the opponent does not see the top card or cannot infer the incoming Arc Phone identity.

The adapter tracks strategic groups rather than exact physical instance IDs.

It represents one top card. Multi-card top-deck manipulation would require a richer ordered-deck belief.

## Next work

A high-value continuation is an observer-indexed top-draw adapter that lets one player's Trekking Shoes observation condition their joint belief while another observer receives only the public action information.

A policy-level continuation is to compose the full Peonia -> Arc Phone -> Trekking Shoes line with card access, Item lock, Supporter bandwidth, and the turn-action budget.
