# Observer-aware additional Prize staging

## Question

When an E-31 effect takes an additional Prize while another Prize card is already pending, can exact physical removal and observer-relative beliefs advance together?

Yes.

Implementation: `tools/prize_pending_observer_extra.py`  
Regression: `results/prize_pending_observer_extra/reproduce.py`

## Transition

`stage_additional_prize_front_with_observers` composes the existing:

- exact `PrizePendingTakeState`;
- observer-indexed `TopPrizeJointBelief`;
- position-removal update;
- `stage_additional_prize_front` physical transition.

The function validates that every observer agrees with public face-up/face-down geometry and assigns positive probability to the exact grouped physical truth before and after the move.

The selected additional Prize leaves the remaining Prize topology and is prepended to the already-active pending queue. Its identity is revealed privately to the Prize taker when face down. Other observers update only on the public fact that the selected slot was removed.

## Correlation witness

The regression uses two possible joint worlds:

- top = Other, remaining additional Prize = Switch;
- top = Switch, remaining additional Prize = Other.

Both observers begin at 50/50.

A first Prize is already pending. Player B then takes the remaining face-down Prize as an additional Prize.

The exact card is Switch.

After the transition:

- B learns Switch and infers top = Other with probability 1;
- A sees the remaining Prize slot disappear but does not see the card identity, so A remains 50/50 on the top;
- the additional physical Prize is at the front of the pending queue;
- card-class totals remain conserved.

## Why this matters

Jirachi Prism Star and Lucky Bonus can create more Prize-taking work from inside the before-hand window. A physical-only recursive queue would lose information asymmetry if it did not update each observer at the same time.

This adapter lets recursive E-31 effects preserve the same exact-truth-versus-belief split already established for ordinary Prize takes.

## Scope

This result does not choose which Prize position a policy should take. The caller supplies the selected position.

It does not execute the triggering card text itself. `prize_before_hand_bench_entry.py` handles the narrow Chansey/Jirachi board-entry semantics, while this result handles the hidden-information consequences of the additional Prize move.

A future composition layer can combine both transitions in one atomic card-effect program.
