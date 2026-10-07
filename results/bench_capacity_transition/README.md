# Bench-capacity contraction as forced cleanup: when support debt spills into core loss

## Question

Capacity-changing cards can shrink a Bench from eight to five, five to four, or five to three. If occupancy exceeds the new maximum, which roles should be sacrificed, and when does a capacity contraction stop being a cheap way to clear transactional support Pokémon?

This result adds explicit occupants and a discard-choice optimizer to the Bench-capacity work.

Implementation: `tools/bench_capacity_transition.py`  
Reproducer: `results/bench_capacity_transition/reproduce.py`

## Model

Each Bench occupant has an identity label, a role such as `core` or `support`, and a state-specific retention value. When capacity contracts below current occupancy, the resolver keeps the subset whose total retention value is maximal.

The currently cataloged expanded-capacity effects reach eight slots, so exhaustive subset optimization is tiny. Retention value can later incorporate attack requirements, attachments, Prize liability, matchup utility, replay value, or another downstream evaluator.

## Four-core / three-support example

Start from an eight-slot board containing four core occupants valued at 10 each and three transactional support occupants valued at 2 each.

| Capacity transition | Required discards | Minimum-value choice | Value lost |
| --- | ---: | --- | ---: |
| 8 -> 5 | 2 | 2 supports | 4 |
| 8 -> 4 | 3 | 3 supports | 6 |
| 8 -> 3 | 4 | 3 supports + 1 core | 16 |

The first two contractions can repay Bench debt entirely through low-value support occupants. The third crosses a discrete boundary because every support is already gone and further contraction destroys a core slot.

## Closed-form role frontier

When every core occupant is more valuable than every support occupant, let `R` be core occupants, `S` support occupants, `C` the new capacity, and `E = max(0, R + S - C)` mandatory discards.

Then support losses are `min(S, E)` and core losses are `E - support losses`.

The reproducer checks the general optimizer against this closed form across all tested core/support compositions up to eight occupants and every capacity from zero through eight.

## Ordinary five to Collapsed Stadium four

A normal five-slot Bench with four high-value core occupants plus one low-value support can contract `5 -> 4` by discarding exactly that support and preserving the core.

Mechanically, the capacity change has performed the high-level job of a Bench-release action. Its zone result differs from pickup because a contraction normally discards the Pokémon and attached cards rather than returning them to hand or deck.

## Strategic interpretation

Support occupants can serve as a discard buffer on expanded-capacity boards. Capacity collapse can also be a release channel with semantics distinct from pickup.

The loss frontier is discrete. As long as mandatory discards fit inside low-value support occupancy, contraction can be comparatively cheap. The first discard that must touch core infrastructure creates a sharp strategic cost increase that average value-per-slot metrics can hide.

## Relation to dynamic capacity cards

`bench_capacity_effects/` identifies legal effects that create capacity 3, 4, and 8 states. Several specify forced discard when the capacity effect appears or disappears.

The present resolver supplies the transition primitive: after the card/rules layer determines a capacity change, the occupancy layer chooses survivors according to state value.

## Validation

The reproducer constructs every core/support composition up to eight total occupants with core value 10 and support value 2. For every new capacity from zero through eight, it compares the exhaustive maximum-retention optimizer against the closed-form role frontier.

It also asserts that a normal five-slot, four-core plus one-support contraction discards the support.

## Limits

The demonstration values are illustrative rather than empirical utility estimates. The optimizer assumes the player controls the discard choice and every candidate is legal to discard under the capacity effect.

It does not model simultaneous effects, opponent choice, on-discard or Knock Out effects, recovery, attached-card value separately, Prize mapping, or the cost of establishing/removing the capacity source.

## Next useful work

The strongest extension is to derive retention value from actual downstream lines. A transactional support with a replay route, an Energy-heavy attacker, a lock Pokémon, and a damaged multi-Prize liability should receive different values.

A second integration is to place this resolver inside the typed scheduler so a line can move through `8 -> 5 -> 4` states over time and compare pickup against deliberate capacity collapse as competing release methods.
