# A bounded, observation-blind search-Item decision policy

**Status:** experimental pinned-engine tactic and physical-state invariance regression. The isolated SFT [passed pinned CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38607914259). This is a narrow research policy correction; it does **not** validate real match win rates, nor guarantee whole-bot observation consistency.

## Why this matters

The pinned Twinleaf `SimpleTacticsAi`'s `PlayTrainerTactic.evaluateAction` replays an Item on a copy of the *actual* hidden deck order. The [exhaustive existing audit](../twinleaf_hidden_topdeck_oracle/) establishes that the bot uses Pokégear 3.0 on every hit among the top seven and holds it on every hidden miss; likewise for Trainers' Mail among the top four. The native choice therefore depends on a fact that a paper player has not yet observed.

Added:

- [K0 topdeck policy](../../../simulation/twinleaf/blind-topdeck-trainer-tactic.cjs)
- [single runnable pinned-engine test](../../../simulation/twinleaf/test-blind-topdeck-search.cjs)
- [scoped-push CI](../../../.github/workflows/validate-twinleaf-blind-topdeck-search.yml)

It substitutes a **common observation-conditioned decision** for these *two exact pinned print implementations*: `Pokegear SVI` and `Trainers' Mail ROS`. All other Items continue to use the native tactic's speculative scoring, which may leak hidden information separately.

## Estimator and evidence type

At K0, under an exchangeable unknown allocation of unrevealed cards between the remaining deck and face-down Prizes, define:

- `N`: combined number of currently unobserved own deck and Prize cards;
- `M`: eligible search targets in that combined physical pool;
- `k`: search window, bounded by the number of remaining deck cards.

The probability that a blind next-top-`k` search sees at least one target is

`P(hit) = 1 - C(N-M,k) / C(N,k)`

with the usual zero-miss convention when fewer than `k` misses exist. The combined pool is inferable from the original 60-card list and cards already seen outside that pool. The policy does not condition on actual secret topdeck ordering or physical Prize allocation.

Eligible targets follow the exact pinned card effects: a Supporter for Pokégear 3.0; a Trainer other than Trainers' Mail for Trainers' Mail. The native [score oracle audit](../twinleaf_hidden_topdeck_oracle/) measured a `+4` score change on a target hit and `-2` on a miss in a controlled fixture. For this *provisional policy* we compare `6P(hit)-2` with a zero-score hold option. The `+4/-2` scoring should **not** be generalized as measured game value in different boards, and this resulting fixed threshold is a heuristic rather than learned optimal policy.

An invariant decision is an important prerequisite for fair deck comparisons, but this estimator is not a calibrated competitive tactic. In particular, it ignores the strategic usefulness of the found target, card-text timing, deck-order information revealed to the player, K1 Prize knowledge, and the resource value of holding an Item until later.

## Exact opening-style examples

The regression uses 60 physical cards on each side, an actor holding the Item and six Grass Energy, one Regidrago V Active, and a 46-card deck plus six Prize cards. It deliberately changes only hidden positions and keeps public state and the joint hidden-card multiset fixed.

| Held Item | Eligible copies in 52 unseen cards | Window | Blind hit probability | Model score `6p-2` | Decision in both hidden worlds |
| --- | ---: | ---: | ---: | ---: | --- |
| Pokégear 3.0 | 1 Supporter | 7 | 13.4615384615% | -1.1923076923 | Hold |
| Pokégear 3.0 | 4 Supporters | 7 | 44.9644473174% | +0.6978668390 | Play |
| Trainers' Mail | 1 Trainer | 4 | 7.6923076923% | -1.5384615385 | Hold |
| Trainers' Mail | 8 Trainers | 4 | 49.8564964447% | +0.9913897867 | Play |

One additional test places the single Boss's Orders in a face-down Prize rather than the deck. The model's K0 choice remains identical to the same otherwise unobserved pool with Boss's Orders in deck. The original native tactic's Pokégear decisions diverge on alternative deck-order worlds. The test covers five paired physical-world comparisons, full `SimpleTacticsAi` output and direct tactic output, matching existing native oracle evidence. All fixed worlds are artificial and are not tournament games.

## Exact sensitivity to Prize knowledge (K1)

An [exact reproducer](reproduce.py) conditions 52 initially unseen cards on the target count among six Prizes, verifies posterior normalization, and independently enumerates small physical cases.

For four eligible Supporters and a seven-card search, the K0 heuristic plays. With complete K1 Prize knowledge it would instead hold when at least two Supporters are Prized. This condition occupies **3292/54145 = 6.0799704497%** of the random Prize configurations.

For eight eligible Trainers and a four-card search, the K0 heuristic plays. After K1 it would hold when at least four Trainers are Prized, occupying **1227/363545 = 0.3375097993%** of configurations.

These are theoretical policy-decision reversals within the restricted model. They do not measure real-game misplays or match strength.

## Scope and remaining correctness work

The bounded tournament runner now supports the **opt-in diagnostic** `TWINLEAF_TACTIC_ORDER=blind_topdeck`. The default mode remains native. The alternate mode replaces exactly one Trainer tactic constructor, preserving all other priority slots and the existing Supporter-selection repair. Traces record `blind_k0_topdeck_item_v1` as an additional policy hook, and continue to report `unmasked_native_SimpleTacticsAi_order_oracle` because other tactics can still inspect hidden information. This mode is intended for controlled bot-behavior comparisons.

A complete repair must use each player's information history to construct an observation/belief state, mask hidden opponent hand and Prize identities, treat known deck/Prize location information accurately after a search (K1), evaluate non-search actions without secret deck order, and prevent scoring simulations from silently conditioning on unseen outcomes. It must then be validated across many different public states and real headless matches, with opponent-field and engine-semantic coverage.

**Interpretation:** this is an independently testable observation-invariance improvement for a specific hidden-information failure. No claim that any Expanded deck wins more matches follows from it.
