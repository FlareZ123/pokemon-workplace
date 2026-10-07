# Typed Bench release actions have different same-turn continuation value

## Question

The conservative Bench-release catalog finds release effects across Items, Supporters, Abilities, and attacks. Are those release edges interchangeable once a spent support Pokémon has filled the last Bench slot?

No. The release action class changes whether the slot can be reclaimed early enough to complete the rest of the turn.

This result composes persistent Bench occupancy with typed release actions and the repository's canonical turn-action budget. The test state has five Benched Pokémon including one spent support Pokémon. The same turn must both play another required Supporter and put one required Pokémon onto the Bench.

Implementation: `tools/typed_bench_release_execution.py`  
Regression: `results/typed_bench_release_execution/reproduce.py`

## Card-text anchors

The model uses representative legal paper-Expanded effects already identified by `bench_release_catalog`:

- **Penny** `sv1-183`: Supporter; returns one Basic Pokémon and all attached cards to hand.
- **Scoop Up Cyclone** `bw10-95`: deterministic Item; returns one Pokémon and attached cards to hand; ACE SPEC.
- **Super Scoop Up** `bw1-103`: Item; on heads returns one Pokémon and attached cards to hand.
- **Pelipper** `sm1-38` / Courier: attack; returns one Benched Pokémon and attached cards to hand.
- **Corviknight** `swsh3-156` / Flying Taxi: evolution-triggered Ability; can return another Pokémon and attached cards to hand.

The state model does not collapse those into one generic `release Bench slot` edge.

## Mechanical result

| Release channel | Modeled prerequisites | Same-turn required Supporter + Bench entry? |
| --- | --- | --- |
| Penny/AZ-like Supporter | ordinary Supporter limit 1 | **No** |
| Penny/AZ-like Supporter | Supporter limit 2 | Yes |
| Scoop Up Cyclone | Items allowed | Yes |
| Scoop Up Cyclone | Item lock active | **No** |
| Super Scoop Up | heads branch, Items allowed | Yes on that branch |
| Pelipper Courier | attack usable | **No** |
| Corviknight Flying Taxi | evolution/Ability release ready | Yes |
| Corviknight Flying Taxi | release infrastructure not ready | **No** |

The reasons are mechanically distinct.

A Supporter release spends the same quota needed by the second Supporter. A deterministic Item release does not spend that quota, so it can free the slot first. Under Item lock, that edge disappears. An attack can remove the spent support Pokémon, but attacking closes the ordinary action window, so the newly empty slot cannot admit the required Pokémon until a later turn. An Ability release can work before the other actions, but only if its own trigger and board infrastructure are satisfied.

This is the execution layer that the earlier catalog was missing: **release existence, release action class, release timing, and release readiness are separate state variables.**

## Stochastic Item release

Super Scoop Up gives a probabilistic release channel. If `n` independent copies are already available and legal to play, and the player can keep trying after tails, the probability of at least one heads is:

`R(n) = 1 - (1/2)^n`

Using the same exact toy setup layer as `interturn_bench_debt_policy`:

- 40 cards remain;
- four immediate setup outs;
- base line sees four random cards: `S0 = 35.545464%`;
- support line sees five random cards: `S1 = 42.707080%`.

If a future collision branch occurs with probability `c`, and the release succeeds with probability `R`, the support line has:

`joint success = S1 * (1 - c * (1 - R))`

The break-even collision probability becomes:

`c* = (1 - S0/S1) / (1 - R)`

| Super Scoop Up attempts | Release probability | Break-even collision probability |
| ---: | ---: | ---: |
| 0 | 0% | 16.769152% |
| 1 | 50% | 33.538304% |
| 2 | 75% | 67.076608% |
| 3 | 87.5% | 134.153215% |
| 4 | 93.75% | 268.306431% |

A threshold above 100% means that, inside this isolated toy model, the support line stays ahead even if the future collision branch happens every time. With three available Super Scoop Up attempts, the residual all-tails failure probability is only 1/8, so the immediate draw advantage is large enough to absorb that remaining risk.

This does **not** imply that three or four Super Scoop Up are good deck inclusions. Card slots, Item lock, hand access, coin variance, opportunity cost, and the strategic value of the cards returned to hand all remain outside this narrow calculation.

## Strategic interpretation

Bench reversibility has a typed cost structure.

A state evaluator should preserve at least:

- whether a release card/effect exists;
- action class: Item, Supporter, Ability, or attack;
- action-window cost and whether the turn remains open afterward;
- lock state for that action class;
- deterministic versus stochastic release;
- trigger/infrastructure readiness;
- target restrictions;
- deck-construction costs such as ACE SPEC exclusivity.

A graph that gives every release effect the same edge weight can therefore make a spent support Pokémon look much easier to remove than it is in the actual continuation state.

## Evidence class

- The five representative release effects and their action classes are card-text facts from the bundled legal card pool and prior conservative catalog.
- Same-turn feasibility is a deterministic planner result over typed transitions and `TurnActionBudget`.
- Super Scoop Up release probabilities and break-even thresholds are exact mathematical derivations under the stated independence/availability assumptions.

## Limitations

The model starts with the release effect already accessible. It does not model how the player searched or drew it.

Scoop Up Cyclone's ACE SPEC deck-building opportunity cost is acknowledged but not valued. Super Scoop Up attempts are assumed to be independently available in hand and legal to play, with no Item lock; the model does not price the deck slots or the value of keeping those Items for other turns.

Flying Taxi is represented as a ready Ability release only in the positive branch. A full physical model would require a valid evolution target, Corviknight in hand, legal evolution timing, Ability availability, and the resulting evolved Pokémon's continued Bench occupancy.

Attack releases may still be strategically useful for freeing the slot for a **later** turn. This result asks the stricter same-turn question where a required new Bench entrant must appear after the release.

## Relation to prior work

`bench_release_catalog` established that 16 of 20 conservative release names are Supporters or attacks and proposed adding real action-class costs to persistent Bench occupancy. `interturn_bench_debt_policy` instantiated the Supporter case with AZ and a future Supporter collision. This result generalizes that execution layer across representative action classes and a stochastic Item branch.

## Next useful work

The natural next step is deck-specific policy evaluation. For a real list using Crobat V, Dedenne-GX, Tapu Lele-GX, or another transactional support Pokémon, derive the distribution of future Bench pressure and release access instead of treating the collision probability as external.
