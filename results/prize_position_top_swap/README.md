# Face-down Prize positional memory and top-deck swaps

## Question and source

Can a count-only Prize belief, or even a face-up/face-down composition partition, represent what a player knows after **Arc Phone** (Lost Origin `swsh11-152`)?

The bundled paper Expanded card database gives Arc Phone's Item text:

> Look at the top card of your deck. You may switch that card with 1 of your face-down Prize cards. (The cards stay face down.)

The face-down restriction makes individual physical positions strategically relevant. The outgoing Prize identity need not be revealed. The incoming card's identity can nevertheless remain known to the player who inspected the deck top.

## Relationship to earlier research

This extends existing `prize_position_belief/`, `prize_slot_visibility/`, and `prize_top_swap_belief/` work. The earlier joint kernel already proves that an Arc Phone swap creates cross-zone correlations for the **acting player with a known incoming card**. The new contribution is a hypergeometric joint prior including the unknown incoming top, asymmetric actor/opponent updates for the *same physical action*, exact labeled-deal validation of both observer posteriors, and face-down-only shuffle/reveal continuations. `as_existing_top_prize_joint` and its inverse exchange the full posterior with the earlier `TopPrizeJointBelief` representation. The regression cross-validates the overlapping acting-player transition against the older implementation, preventing this new research from becoming a disconnected second rules engine.

## Result

A player's state needs **position-indexed hidden identities and a correlated deck top** when known cards can enter particular face-down Prize positions. Such knowledge can exist without a single face-up Prize. Collapsing to either `PrizeBelief` or `PrizeVisibilityBelief` loses it.

`tools/prize_position_top_swap.py` implements a finite distribution over joint assignments of named Prize positions and the next deck-top card. Its `observe_top` conditions only the observer who privately saw the top card. Its `swap_face_down_with_top` permutes identities across zones for all observers, preserving physical joint multiplicities. `reveal_prize` conditions a publicly seen identity and makes that position ineligible for future face-down-only swaps. Explicit `shuffle_face_down_positions` uniformly randomizes the eligible physical positions.

## Independent exhaustive witness

Take five distinct cards `A,B,F1,F2,F3`. Uniformly deal two ordered, face-down Prize positions and one deck-top card, sampling without replacement. There are exactly **60** labeled physical deals.

The acting player privately observes top = `A` (12 compatible deals) and switches it with position zero. The opponent sees the swap but does not see the top identity, and receives no inference about the player's strategy.

| Quantity after swap | Acting player | Uninformed opponent |
| --- | ---: | ---: |
| P(A at face-down position 0) | 1 | 1/5 |
| P(A among both Prizes) | 1 | 2/5 |
| P(B at remaining position 1) | 1/4 | not conditioned on A |
| P(B now on deck top) | 1/4 | not conditioned on A |

The two B events in the actor's posterior are mutually exclusive because there is only one B. The outgoing Prize becomes the new deck top, so deck-top identity and Prize identity must remain correlated.

A swap into position one instead of zero produces **the same Prize-composition distribution** but places A at position one with certainty. A composition-only observer cannot distinguish the two action histories. A subsequent face-down Prize shuffle turns the actor's positional certainty into `P(A at each position)=1/2` without changing certainty that A remains Prized.

The reproducer enumerates all 60 distinct labeled outcomes as an independent oracle and checks **every grouped joint world**, including exact total-card conservation, both observers' posteriors, public reveals, shuffle effects, reversibility of a repeated swap, and zero-probability observation rejection.

## Larger 60-card illustration

Suppose seven known nonPrize cards have been removed from uncertainty, leaving a pool of **53** unseen cards, including unique groups A and B, with six Prizes and a deck top.

The position-indexed prior has just **57** grouped joint worlds. After the actor sees A on top and swaps it with one of the six Prizes, its new physical Prize position is certain; B's chance of occupying any of the other five Prize positions is `5/52`, and its chance of becoming the new deck top is `1/52`. An uninformed opponent still assigns probability `1/53` to A occupying that named position and `6/53` to A appearing anywhere among the Prizes. These are conditional information-state probabilities, **not match statistics**.

## Compatibility and limitations

The kernel exports lossless interoperation with the existing `TopPrizeJointBelief` and intentionally lossy `collapse_to_prize_belief` and `collapse_to_visibility_belief` projections. These interfaces preserve the distinction between cross-zone joint information and reduced count/visibility summaries.

- The prior assumes exchangeability of currently unseen Prize positions and the single deck-top card. It is invalid if there are earlier known positions not supplied in the joint belief.
- The model tracks **one** deck-top card, not a full ordered deck. A future draw must not automatically invent the next top card.
- A full simulator must represent different observers' known cards, the physical action's chosen position, and any new public information separately.
- The example treats the opponent's observation of the swap as strategy-independent. In a real game, an opponent may infer information from the player's choice to switch, depending on the player's policy.
- Explicit face-down shuffling removes known positional identities. No general right to reshuffle Prize positions at arbitrary times is assumed.
- These grouped, floating-point, bounded-world calculations are a research information kernel, not a complete physical card execution engine, rules adjudicator, tournament win-rate estimator, or date-aware legality validator.

## Reproduction

See `results/prize_position_top_swap/reproduce.py`. The focused `.github/workflows/validate-prize-position-top-swap.yml` workflow runs it against the real shared modules.

**Next:** compose observer-indexed visibility states and position-aware Prize-taking / information transitions, then evaluate how much exact position knowledge improves rational Prize selection where a card grants selection among face-down Prize positions.
