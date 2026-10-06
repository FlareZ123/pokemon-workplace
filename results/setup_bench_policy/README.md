# Setup Bench policy: reserving connector slack

## Question

Should a setup simulator automatically place every extra opening Basic Pokémon onto the Bench?

## Answer

No. The setup rules make extra Bench placement optional. If a future line needs one or more free Bench slots, a player can reserve that slack during setup by declining to Bench some opening Basics. An automatic bench-all policy therefore encodes a strategic choice and can create connector failures that a different legal setup choice avoids.

This result adds `tools/setup_bench_policy.py`, which computes the exact distribution of ordinary Basic counts in an accepted seven-card opening and the exact probability that a bench-all or reserve-slots policy blocks a connector requiring a specified number of Bench slots.

The model deliberately covers openings accepted through the ordinary Basic rule. Optional setup cards such as Luxray or Snorlax Doll require the richer policy treatment already developed in `results/setup_mulligan_policy/`.

## Exact model

Consider a 60-card deck with `B` ordinary legal Basic Pokémon and a seven-card opening. Condition on the accepted opening containing at least one Basic. If `K` is the number of Basics in that opening,

`P(K=k | K>=1) = C(B,k) C(60-B,7-k) / [C(60,7) - C(60-B,7)]`.

One Basic occupies the Active Spot. Under a bench-all policy, setup Bench occupancy is

`min(K-1, 5)`.

If the player reserves `r` Bench slots, the policy instead places at most `5-r` extra Basics onto the Bench. A connector requiring `q` slots is blocked by setup occupancy exactly when current occupancy plus `q` exceeds five.

## Sensitivity

Exact block probabilities under a bench-all setup policy are:

| Ordinary Basics in deck | 1-slot line blocked | 2-slot line blocked | 3-slot line blocked |
| ---: | ---: | ---: | ---: |
| 8 | 0.000580% | 0.029997% | 0.642859% |
| 12 | 0.014442% | 0.300252% | 3.039256% |
| 16 | 0.104572% | 1.292353% | 8.221076% |
| 20 | 0.442895% | 3.732973% | 16.756197% |
| 24 | 1.373940% | 8.460579% | 28.539389% |
| 28 | 3.458281% | 16.191210% | 42.718145% |
| 32 | 7.464292% | 27.234579% | 57.831451% |

The one-slot failure rate is small for many ordinary deck compositions, while multi-slot lines become sensitive much sooner. The general lesson is about representation rather than the magnitude of any one row: automatic Benching can change line feasibility, and the size of that distortion depends on deck composition and the route's temporary slot requirement.

## Reserving slack

A deterministic policy that reserves at least `q` slots makes setup occupancy incapable of blocking a `q`-slot route. This guarantee concerns setup occupancy only. Later plays, forced effects, capacity restrictions, and opponent actions can still consume or remove the slack.

Reserving slots has an opportunity cost because an unbenched opening Basic may have immediate strategic value. The correct policy can therefore depend on matchup, turn order, target ALS, gust risk, and which Basics are in hand. A complete setup optimizer should choose the subset of Basics to Bench rather than treating their placement as automatic.

## Connection to Bench capacity geometry

The companion result in `results/bench_capacity_geometry/` represents a route by its temporary peak Bench demand. The setup policy here supplies an exact prior over starting occupancy under a specified placement policy.

Together they suggest a clean decomposition:

1. setup policy produces a distribution over initial Bench occupancy;
2. the route contributes a peak temporary slot requirement;
3. active capacity effects determine the current limit;
4. the line is mechanically available when occupancy plus peak demand stays within that limit.

This decomposition can be integrated into the repository's typed access network without conflating setup choice with later connector mechanics.

## Validation

`results/setup_bench_policy/reproduce.py` checks normalization, deterministic reserved-slot occupancy, and exact probabilities for a 12-Basic deck. It also verifies that reserving one or two slots drives the corresponding setup-block probability to zero.

## Limitations

The model conditions only on ordinary Basic setup eligibility and ignores the identity and strategic value of individual Basics. It also assumes the specified deterministic placement policy is followed whenever the opening is accepted. It does not model mulligan-visible matchup information, optional setup cards, Prize states, or later turn actions.

The exact probabilities therefore answer a narrow mechanical question: how much connector blockage can be created by a chosen setup Bench-placement policy under a given Basic count.
