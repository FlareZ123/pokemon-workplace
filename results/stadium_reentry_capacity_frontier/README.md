# Gothitelle source saturation can decrease realizable Grand Tree activations

## Question

The Stadium-entry models quantify how often Grand Tree could be activated if
the player can repeatedly move it out of play and back. Those counts ignore
that each Gothitelle Teleport Room source requires a Pokémon slot and each
Grand Tree activation requires an eligible Basic Pokémon to evolve.

Can adding another ability source reduce actual evolution opportunities?

**Yes, under a fixed-board no-release model**, even while the source-only
bound stays the same or increases.

## Exact abstract model

The legal Expanded source interaction uses Grand Tree `sv7-136`,
Gothitelle `xy3-41` (Teleport Room), and a Brooklet Hill `sm2-120`
available for one ordinary Stadium play. The first Grand Tree is already in
play. Optionally a second physical Grand Tree is in discard.

The normal board has one Active Pokémon position plus five Bench positions,
giving six total. The state allocates:

* n already-established Gothitelle source Pokémon, 0 through 4;
* r other resident non-target Pokémon, 0 through 2;
* at most 6-n-r eligible Basic Pokémon as distinct Grand Tree targets.

Every successfully executed Grand Tree effect activation evolves one
previously eligible Basic. That target remains in play but is no longer
Basic and cannot satisfy another Grand Tree activation. There is no board
release, new Basic recruitment, devolution, or target reuse during this
fixed-window experiment.

The model keeps every physical Stadium transition, source-specific
Teleport Room quota, and ordinary Stadium play quota in its original
kernel. The additional state tracks the actual identities of eligible
and already evolved targets. Search chooses exact source order, Stadium
copy, and evolution target without allowing a target to evolve twice.

The same-copy return ruling remains unresolved. Results are therefore
reported under explicitly conditional effect-use scope assumptions:
`entry` and `physical_copy`.

## Quantitative finding

With an ordinary Stadium play available, the source-only per-entry
maximum for n Gothitelle sources is
`A(n) = 1 + ceil(n/2)`.

With one physical Grand Tree, the per-entry successful distinct-Basic
evolution bound is exactly

`E(n,r) = min(A(n), max(0,6-n-r))`.

The exhaustive state search independently confirms this formula, together
with the corresponding per-physical-copy cap, for 60 combinations across
n=0..4, r=0..2, 1 or 2 Grand Tree copies, and two use-history policies.

With **one Grand Tree**, optimistic per-entry identity scope:

| Gothitelle sources | No reserved Pokémon | 1 reserved Pokémon | 2 reserved Pokémon |
|---|---:|---:|---:|
| 0 | 1 | 1 | 1 |
| 1 | 2 | 2 | 2 |
| 2 | 2 | 2 | 2 |
| 3 | **3** | 2 | 1 |
| 4 | **2** | 1 | 0 |

Thus a fourth Gothitelle **lowers** maximum distinct Basic evolutions
from 3 to 2 with no other residents. With a reserved attacker or other
supporter Pokémon, it lowers 2 to 1. When two non-target residents exist,
four Gothitelle fill all six positions, making Grand Tree's target-based
activation impossible in the modeled board state.

If the official same-copy rule proves to follow a per-physical-card limit,
a single physical Grand Tree gives at most one use regardless of source
count. With two physical Grand Tree copies, the maximum is two, further
limited by remaining target slots.

## Strategic meaning

The saturation effect demonstrates that an action can become less realizable
as its source redundancy increases because the sources occupy the same
physical space required by its targets. Counting additional Ability sources
as monotonic consistency gains is unsound without Bench and Active Spot
constraints. It also shows why a high source-only Stadium reuse count does
not establish a viable archetype line.

This is a conditional board-level upper bound. Building three usable
Gothitelle in paper Expanded, finding compatible Grand Tree evolution
targets, retaining Stadium placement resources, and surviving relevant
locks are all outside the evaluated scope. It is not a win-rate or
metagame claim.

## Reproduction

`python results/stadium_reentry_capacity_frontier/reproduce.py`

Implementation: `tools/stadium_reentry_capacity_frontier.py`.

The test explicitly enumerates physical target identities and all available
Stadium source orderings, checks 60 board and effect-use combinations, and
verifies the 3-to-2 decline when the fourth Gothitelle is added.

Rule basis: locally bundled Advanced Player's Rulebook A-04 (five Bench
slots), B-04 (Stadium action and effect), Gothitelle and Grand Tree card
texts. See the preceding
[Stadium re-entry usage](../stadium_reentry_usage_bounds/) and
[mixed-channel frontier](../stadium_mixed_entry_frontier/) results for
the official rulings and identity boundary.
