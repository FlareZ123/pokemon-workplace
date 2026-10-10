# A guaranteed Retreat can vanish when worldwise minimal sets are intersected

## Precise question

In the existing exact physical Retreat model, eligible Counter Energy
and Reversal Energy supply more units when their player is behind on
Prize cards. Can a planner construct a robust Retreat frontier by
enumerating only inclusion-minimal payments in each possible Prize
regime and intersecting those pruned frontiers?

**No.** The minimization and information-robust intersection operations
do not commute.

## Exact physical counterexample

The Active is a non-GX/non-ex Stage 1 Pokémon with Retreat Cost 2.
It has one Counter Energy and one Basic Energy attached, and one
legal Bench promotion target. No locks apply.

- Tied Prizes: Counter provides one unit; only the two-card
  `{Counter, Basic}` payment is sufficient and minimal.
- Behind on Prizes: Counter provides two units; `{Counter}`
  and `{Counter, Basic}` are both legal, while only
  `{Counter}` is inclusion-minimal.
- Unknown Prize regime: the exact canonical action enumerator
  correctly accepts `{Counter, Basic}` as guaranteed legal.

Thus:

    robust = legal(tied) intersect legal(behind) = {{Counter, Basic}}

But:

    minimal(legal(tied)) intersect minimal(legal(behind)) = empty

The planner that intersects independently pruned frontiers declares
no safe Retreat payment, even though one exists.

## General principle

When a resource's strength can increase between possible states,
the legal action set may expand, causing an old inclusion-minimal action
to become nonminimal. Minimality describes a partial order *within*
one world, and need not be stable between worlds.

A robust planner should intersect the complete executable
world-conditioned action sets first. If an objective-specific
dominance proof applies, it may subsequently prune within the
robust frontier. For the Counter/Reversal families tested, the
existing lower-bound payment sufficiency predicate performs
this robust legality check directly.

The example is about **information-dependent action feasibility**.
Normal game Prize counts are public; the unknown-prize context
reflects an incomplete state projection or computational
abstraction rather than a claim that players cannot count Prizes.

## Validation

`reproduce.py` constructs the exact card/board fixture using
the preexisting physical action enumerator and its known and unknown
Prize contexts. It verifies the specific paradox and audits
1,792 bounded configurations of eligible/ineligible holders,
Counter/Reversal snapshots, selected Energy subsets and costs.

The script independently compares each unknown frontier to the
intersection of both fully known frontiers and measures cases
where worldwise-minimal intersection loses guaranteed minimal actions.

Reproduce:

    python results/retreat_prize_minimality_paradox/reproduce.py

The dedicated CI also runs the parent
`results/retreat_action_enumeration/robust_prize_oracle.py`.

## Scope

The underlying exact model assumes recognized printed Counter/Reversal
Energy families, resolved holder-stage/rule-box eligibility and the
existing physical Retreat payment convention. This result does not
extend to unknown costs, other stochastic effects or automatically
infer Prize counts from play history.

Its purpose is to prevent an incorrect planner optimization at
the interface between incomplete information and action enumeration.
