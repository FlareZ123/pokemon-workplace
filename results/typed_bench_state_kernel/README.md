# Typed Bench-state kernel: zone, residency, action windows, and capacity in one model

## Purpose

The preceding Bench investigations isolated setup-role contention, entry-zone semantics, persistent support residency, release timing, dynamic capacity, and contraction loss separately.

This kernel unifies the in-play parts into a reusable deterministic state-transition layer.

Implementation: `tools/bench_state_kernel.py`  
Reproducer: `results/typed_bench_state_kernel/reproduce.py`

## State

`BenchState` carries turn number, current Bench capacity, explicit residents, resident roles and retention values, accumulated hand-to-Bench trigger counts, current-turn Supporter usage, and whether an attack ended the turn.

Each resident persists until a release or capacity transition removes it.

## Entry-zone semantics

`entry_mode="hand"` represents playing a support Pokémon from hand onto the Bench. When capacity exists, the resident is added and its modeled hand-to-Bench trigger fires.

`entry_mode="direct"` represents an effect that puts the target directly onto the Bench. It consumes the same slot while leaving the hand-play trigger unfired.

This preserves the typed-access distinction between a line ending with a target in hand for manual play and direct placement that reaches the same identity through the wrong transition.

## Residency and chaining

On a five-slot Bench with four core residents, the first support can enter and trigger. A second support cannot enter while the first remains resident.

Item or Ability release reopens the slot without ending the turn, allowing another support to enter immediately.

Supporter release also permits same-turn reuse while marking the ordinary Supporter window spent. A second Supporter release on that turn is rejected.

Attack release removes the resident and marks the turn ended. The freed slot cannot be reused until `next_turn()`.

## Dynamic capacity

The kernel accepts arbitrary capacity and integrates the maximum-retention contraction resolver.

A regression starts at capacity eight with four high-value core residents and three low-value supports. All three support entries fire.

The state then contracts:

- `8 -> 5`: two supports are discarded;
- `5 -> 4`: the final support is discarded;
- `4 -> 3`: one core resident must be discarded.

This reproduces the discrete loss frontier inside the same state object used for support entry and release timing.

## Why reachability alone is insufficient

A search edge does not establish whether the line works. The state also needs entry zone, free capacity at the moment of entry, residency of prior supports, release action class, current Supporter usage, attack-ending state, current capacity source, and contraction losses.

These variables are compact enough to carry explicitly.

## Validation

The reproducer verifies correct hand-trigger entry, direct-entry non-triggering, residency blocking, Item same-turn reuse, Supporter-window consumption, attack-delayed reuse, expanded-capacity support chaining, and `8 -> 5 -> 4 -> 3` contraction.

All regressions are deterministic.

## Boundaries

Setup remains a separate layer. A support Basic consumed as the starting Active should be resolved before the first-turn Bench state is created.

Probabilistic card access also remains separate. The intended architecture is:

`setup + Prize state -> typed access transitions -> Bench-state transitions -> tactical value`

This keeps probability, zone semantics, board capacity, and utility connected without making one layer solve every problem.

## Limits

The kernel assumes unique resident names inside one modeled state and uses scalar retention values during contraction. It does not yet model Active identity, switching, retreat, Energy, Tools, Prize value, lock effects, card-specific release targeting, once-per-turn Ability identities, or opponent Bench state.

Item and Ability release transitions should only be supplied after upstream logic establishes that the specific effect is legal and available.

## Next useful work

The highest-value extension is to connect this deterministic kernel to exact opening/Prize/access states so each probabilistic state can apply only reachable typed actions and test whether an intended line succeeds by a deadline.

A second extension is Active-position state plus typed switch/retreat transitions, which would make attack-based cleanup realistic enough to check whether a support resident can actually become Active before using its self-vacating attack.
