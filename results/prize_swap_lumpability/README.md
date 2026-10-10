# Exact abstraction criterion for Prize-position swap actions

## Question

When can a Pokémon TCG simulator legitimately compress a joint physical Prize-position/top-deck state to grouped Prize counts without changing action-outcome distributions?

The relevant mathematical property is **strong lumpability**. For a fixed action and state projection `P`, every two detailed states `s,t` satisfying `P(s)=P(t)` must induce the same probability distribution over `P(next state)`. If they do, an abstract Markov transition exists for that action. Otherwise the projected state hides information that can change the abstract outcome.

This is a statement about the specified transition and abstraction, not a claim that a full game policy or win rate is reproduced.

## Exhaustive audit

`results/prize_swap_lumpability/reproduce.py` independently enumerates all **24** ordered placements of three distinct cards drawn from four labeled cards `A,B,X,Y`: two Prize positions and one deck top, without replacement. It compares transition probabilities using exact `Fraction` arithmetic.

Three abstract action kernels are tested:

- **Chosen position 0 swap:** exchange the top card with the particular physical Prize at position zero, representing the physical-choice geometry of Arc Phone.
- **Uniform random position swap:** a hypothetical operation independently choosing either Prize position with probability 1/2. This is a mathematical control case, **not Arc Phone's card text**.
- **Random Prize-position shuffle:** uniformly permute the physical Prize positions, leaving the deck top unchanged, as an isolated shuffle information operation.

| Transition | Prize counts plus top card | Prize counts alone |
| --- | --- | --- |
| Swap chosen position 0 | **Insufficient** | **Insufficient** |
| Swap a uniformly random position | Sufficient | **Insufficient** |
| Shuffle Prize positions only | Sufficient | Sufficient |

"Sufficient" here means strong lumpability across all 24 physical states for that single action.

## Witness 1: selected position matters even with top known

Consider states:

- `(Prize0=A, Prize1=B, Top=X)`
- `(Prize0=B, Prize1=A, Top=X)`

Both have the same grouped Prize counts **and** the same known top card. Swapping physical position zero gives respectively:

- `(Prize0=X, Prize1=B, Top=A)`
- `(Prize0=X, Prize1=A, Top=B)`

These have different Prize compositions and different top identities. Therefore no exact action kernel defined on Prize counts plus top alone can represent a fixed-position swap in arbitrary positional knowledge states.

For a uniformly random position choice, each original state instead gives the same two projected outcomes with probability 1/2 each. Position counting can be compressed for that particular action, **provided the top identity remains represented** and the choice is genuinely uniform independently of hidden identities.

## Witness 2: omitting the top card can break even random swapping

Consider:

- `(Prize0=A, Prize1=B, Top=X)`
- `(Prize0=A, Prize1=B, Top=Y)`

The Prize-count projection sees the same state. After swapping a uniformly random Prize slot with the top, one produces a Prize containing X and the other a Prize containing Y. Their projected successor distributions are disjoint. Thus preserving positional exchangeability alone does not justify discarding deck-top identity.

## Positive case

A Prize-only shuffle changes the position mapping but preserves Prize composition and leaves the deck top alone. Its projected successor is therefore the same abstract state in both considered count projections, regardless of the detailed original mapping.

This does **not** mean a shuffle has no strategic value. It destroys useful positional memory, as `prize_position_belief/` and `prize_position_top_swap/` show. The count abstraction simply cannot express that information loss.

## Relationship to other research

This audit formalizes where the repository's existing `PrizeBelief`, `PrizePositionBelief`, `PrizeSlotVisibilityBelief` and `TopPrizeJointBelief` abstractions can be safely compressed for individual actions. It complements the source-grounded Arc Phone studies, whose actual action selects a specific face-down Prize. The new observer-indexed `prize_position_top_swap/` regression supplies distributions over such detailed physical states.

## Limits

- The oracle uses a four-card toy pool with exactly two Prize positions and one deck-top card, rather than a full 60-card game.
- "Strong lumpability" is a stringent statewise exactness requirement. A coarse model may still be exact under **particular priors** even if it fails for arbitrary detailed states.
- The random swap is a control action for the audit, not a newly asserted printed card effect.
- A game simulator also has decision-dependent selection, public observations, locks, Energy and Supporter constraints, and rewards. This study isolates one local hidden-zone transition.
- Other abstractions may be sufficient for different restricted sets of legal actions.

## Reproduction

The standalone regression uses standard-library Python and exact rational transition probabilities. The focused `validate-prize-swap-lumpability.yml` GitHub Actions workflow checks all six action/projection combinations and the explicit counterexample pairs.
