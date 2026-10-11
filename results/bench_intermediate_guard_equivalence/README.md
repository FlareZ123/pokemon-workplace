# Exact state-space cost of one optional intermediate Bench-dependent action

## Problem

A pure two-stage forced Bench contraction `n -> a -> b` has `C(n,b)` distinct final survivor sets. Suppose exactly one optional action can occur **between** the contractions, depends on `d` specified original Bench occupants still being in play, and causes one fixed nontrivial change to the hand/deck/discard resource state. How many full terminal states remain after merging physically identical histories?

The answer is a closed form. It has been checked against an independent subset enumerator over **1,155** valid `(n,a,b,d)` combinations up to `n=8`.

Implementation: `tools/bench_intermediate_guard_equivalence.py`.  
[GitHub Actions validation](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132630456).

## Model contract

- `n` distinct original Bench objects are present.
- `0 <= b <= a <= n`, with a monotone first and second contraction.
- Exactly `d` distinct specified original Bench objects are required for one optional intervening action.
- The action is available at the intermediate stage precisely when those `d` objects survive.
- Whenever used, it has the same nontrivial effect on off-board resources, regardless of which other occupants survive.
- An available action may be skipped. A single use is considered, with its payment/draw resources guaranteed.
- Only specified Pokémon are removed; other state changes arise solely from that one optional action. Full stacks and attachments route to the same off-board destination during either contraction.

This is a small semantic model. It excludes other card-text conditions, changing card-draw outcomes, lock effects, opponent turns, and interactions between intermediate choices and unrelated events.

## Exact equations

Use `C(x,y)` for the binomial coefficient, equal to zero when `y < 0` or `y > x`.

Every first-stage survivor choice has `C(a,b)` second-stage choices. The histories in which the player skips the action are

`H_skip = C(n,a) C(a,b)`.

An action can occur only when all `d` required Pokémon survive the first contraction, giving

`H_use = C(n-d,a-d) C(a,b)`.

Thus the number of action-annotated histories is `H_skip + H_use`.

For a final survivor set `S` of size `b`, write `r=|S ∩ D|`, where `D` is the `d`-element requirement set. Some intermediate `a`-element survivor set can contain both `S` and all of `D` exactly when

`b + d - r <= a`.

The number of such final survivor sets is, for `a >= d`,

`R = sum_{r=max(0,b+d-a)}^{min(d,b)} C(d,r) C(n-d,b-r)`.

For `a < d`, set `R=0`.

There are `F=C(n,b)` baseline final states, one for each `S`. Each of the `R` final sets admitting at least one action-enabled intermediate history gains exactly one **additional distinguishable resource state** because using the action has a nontrivial fixed effect. The exact full-state quotient size is therefore

`Q = C(n,b) + R`.

This counts distinct terminal physical/resource states under the model, not the number of action sequences or game-winning plans.

## Results

| `n -> a -> b`, `d` | Skip histories | Use histories | Total annotated histories | Final Bench sets | Full terminal states |
| --- | ---: | ---: | ---: | ---: | ---: |
| `5 -> 4 -> 3`, `d=2` | 20 | 12 | 32 | 10 | **19** |
| `8 -> 5 -> 3`, `d=2` | 560 | 200 | 760 | 56 | **112** |

The first row is independently instantiated in the source-specific, physical-card [Lunatone/Solrock equivalence census](../bench_contraction_action_equivalence/), with exact `StackBoardMaterialState` equality and conservation checks. The second row is an exact combinatorial model result with an eight-Pokémon Bench, rather than an eight-Pokémon gameplay simulation.

The five-to-four-to-three case divides its twenty pure histories into three classes:

- Six histories retain the two required Pokémon both at the intermediate stage and at the final stage.
- Six histories keep the required Pokémon at the intermediate stage, then lose at least one in the second contraction.
- Eight histories already lack a requirement at the intermediate stage.

Exactly nine of the ten possible final Bench survivor sets can be reached through a history in which the action was available, giving `Q=10+9=19`.

## Independent validation

The regression enumerates every intermediate subset `A` and final subset `S subseteq A` for all `n=0,...,8`, all `d=0,...,n`, and all `0 <= b <= a <= n` (1,155 parameter cases). It independently counts:

1. skip histories;
2. histories whose intermediate state contains every required Pokémon;
3. final survivor sets with at least one such history;
4. the resulting two-valued resource-state quotient.

Every enumerated count agrees with the closed form. The two printed-card witness targets are asserted explicitly.

## Practical interpretation

A game-state optimizer can use the formula as a small exact diagnostic for whether a proposed Bench-only state projection discards meaningful intervening action information. In this model, the condition for increasing the final state count is structural: an intermediate Bench can hold both the ultimate survivors and the action prerequisites, even if some prerequisites are later discarded.

An optimizer would need a richer criterion when several optional actions are available, effects are resource-dependent, actions change the board, or damage/Ability histories influence continuation. A single binary action here can double the number of full terminal states for some capacity parameters, but the quotient size says nothing about their relative utility or occurrence probability.

## Linked research

- [Pure physical confluence](../bench_contraction_physical_confluence/).
- [Printed Lunatone intermediate-action witness](../bench_contraction_intermediate_action/).
- [Action-optional exhaustive physical census](../bench_contraction_action_equivalence/).
