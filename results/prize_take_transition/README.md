# Prize-taking truth, belief, and before-hand timing

## Question

How should a state engine take a face-down Prize card while keeping the hidden material state, the player's belief state, and the rulebook's "before you put it into your hand" timing synchronized?

Implementation: `tools/prize_take_transition.py`  
Regression: `results/prize_take_transition/reproduce.py`

## Rule-derived timing boundary

The Advanced Player's Rulebook explains that effects using "before you put it into your hand" occur immediately after a previously face-down card is seen and before it enters the hand.

Chansey's Lucky Bonus is the motivating Prize example: after Chansey is taken as a face-down Prize, it can be put onto the Bench before entering the hand, and a successful coin flip can cause another Prize card to be taken.

Therefore a Prize take cannot always be represented as one atomic `Prize -> hand` count move. At minimum there is an intermediate state in which:

- the selected card has left the remaining face-down Prize set;
- its identity is now known to the player;
- the exact physical card can still be referenced by a triggered effect;
- the destination may still change;
- a nested additional Prize take can occur before the first card reaches the hand.

## Belief transition

For an identity-unknown face-down Prize position, `take_face_down_prize_observation()` performs Bayesian conditioning and removal in one step.

For a belief state with grouped counts `s`, Prize count `n`, and observed group `g`, the observation likelihood in that state is:

`count_g(s) / n`.

The selected card is removed from that group, and posterior masses are normalized across all prior states that could have produced the observation.

`take_face_down_prize_branches()` enumerates every possible observed group, its probability, and the posterior belief over the remaining Prize set.

In the regression's four-card toy pool with singleton groups A and B, two filler cards, and two random Prizes:

- taking A has probability 1/4;
- taking B has probability 1/4;
- taking filler has probability 1/2.

After observing and removing A, the one remaining Prize is B with probability 1/3 and filler with probability 2/3.

## Material state transition

`PrizeTruthBeliefState` binds an `IdentityLedger` to the grouped `PrizeBelief` plus an explicit card-class-to-belief-group mapping.

The constructor enforces two invariants:

1. the physical number of remaining Prize cards equals `belief.prize_count`;
2. the actual grouped Prize composition has nonzero probability under the player's belief.

`begin_face_down_prize_take()` then:

1. checks that the selected physical card class maps to the observed belief group;
2. conditions and removes that group from the Prize belief;
3. materializes the exact physical card from the exchangeable Prize count;
4. moves that instance into `prize_pending`.

The explicit instance remains materialized through the before-hand effect window.

`complete_prize_take_to_hand()` moves that same instance to hand and dematerializes it back into an exchangeable hand count once no copy-specific relation remains.

All card-class totals are conserved.

## Nested Prize-taking regression

The regression also creates an exact two-Prize state containing a "Lucky" card and a payload.

It begins taking Lucky and leaves that exact instance in `prize_pending`. Before Lucky is completed to hand, it begins a second Prize take for the payload.

At that point:

- no face-down Prizes remain;
- both selected physical cards are still materialized in the before-hand pending zone;
- the belief correctly has `prize_count = 0`.

The payload can be completed first and Lucky afterward. This demonstrates the event shape needed for Lucky Bonus-style recursive Prize taking without losing the identity of the first card.

## Findings

Prize taking is simultaneously:

- a physical zone transition;
- an information revelation;
- a Bayesian belief update;
- a temporary identity-materialization boundary;
- a trigger window.

Collapsing those into one hand-count update erases strategically and mechanically relevant timing.

The grouped belief update also gives a reusable stochastic branch operator for policy search: each possible Prize observation has an exact probability and a conditioned belief over the remaining hidden Prize set.

## Limits

The current model assumes the selected face-down Prize position is exchangeable with respect to identity. It does not represent persistent position-level knowledge.

This matters when Prize cards are face up or when an effect preserves knowledge of specific physical positions. A positional hidden-state representation is required for deliberate choice among known Prize identities.

The card-class-to-belief-group mapping is supplied by the research question. Group semantics remain external.

The current completion helper covers the ordinary destination of hand. Chansey-style diversion to the Bench still needs a bridge into the board-object kernel.

The model handles one player's belief. Opponent knowledge and public revelation are separate information states.

Effects that replace, shuffle, or otherwise mutate the remaining Prize set should be composed through their own belief transitions.
