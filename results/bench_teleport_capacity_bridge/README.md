# Teleport Room bridges Stadium placement and Bench-capacity restoration

## Question

Can a pre-established Gothitelle restore Bench access from a full four-of-four
Collapsed Stadium board, even when the ordinary Stadium-play quota is spent?
Does its discard-zone Stadium choice change how many entrants are executable?

**Yes, conditional on the Gothitelle Ability being live before attacking.**
This is a physical-state composition of the existing
[`stadium_entry_channels`](../stadium_entry_channels/) and
[`bench_capacity_restoration_bootstrap`](../bench_capacity_restoration_bootstrap/)
results.

- Implementation: [`tools/bench_teleport_capacity_bridge.py`](../../tools/bench_teleport_capacity_bridge.py)
- Reproduction: [`reproduce.py`](reproduce.py)
- CI: [successful run 37770598375](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37770598375)

## Card and rules anchors

- **Gothitelle** `xy3-41`, Teleport Room: once before attacking, discard any
  Stadium in play; if done, put a differently named Stadium from *your discard*
  into play. This is an Ability-based zone movement and does not consume the
  ordinary Stadium-play quota.
- **Collapsed Stadium** `swsh9-137`: maximum four Benched Pokémon.
- **Sky Field** `xy6-89`: maximum eight Benched Pokémon.
- **Area Zero Underdepths** `sv7-131`: maximum eight Benched Pokémon only
  while a Tera Pokémon is in play; otherwise the normal maximum is five.
- **Advanced Player's Rulebook** I-B-04 restricts ordinary Stadium play to one
  per turn. Its general partial-resolution rule and II-E-20 support Teleport
  Room's removal-only outcome when no eligible replacement exists.

The existing `stadium_entry_channels` investigation also cites the official
Teleport Room ruling on play-from-hand locks:
https://www.pokemon-card.com/rules/faq/details.php?id=9756

## State model

The adapter retains canonical physical Stadium-copy IDs, hand/discard/in-play
zones, source-specific once-per-turn usage, and the ordinary `TurnActionBudget`.
It adds physical Active/Bench/hand Pokémon, Tera status, an upstream Ability-lock
gate, and effective Bench capacity. When Stadium changes contract capacity,
the affected player chooses surviving own Benched Pokémon, and every legal
survivor subset is enumerated. A Teleport source removed from the Bench is also
removed from the set of available physical sources.

The example fixes **four Bench occupants and an already-established Active
Gothitelle**, under Collapsed Stadium, with the needed extra Basics already in
hand. It isolates execution from how the Stage 2 and targets were accessed.

## Verified execution cases

| Branch from four-of-four Collapsed | Effective capacity | Additional ordinary entrants possible | Stadium-play quota spent by Teleport |
| --- | ---: | ---: | ---: |
| No differently named Stadium in discard: removal only | 5 | 1 | 0 |
| Sky Field in discard: Teleport places Sky Field | 8 | 4 | 0 |
| Area Zero in discard, no Tera yet | 5 initially, then 8 if a Tera enters first | 2 tested in Tera-first branch | 0 |
| Ordinary (non-capacity-modifying) Stadium is the only discard replacement | 5 | 1 | 0 |
| Ability suppressed or source already used | 4 | 0 through this Ability | 0 |

The regression directly witnesses two entrants after Sky Field despite an
already-spent ordinary Stadium-play quota. Teleport removing Collapsed with no
replacement creates precisely one Bench slot; a second entrant is blocked.
Area Zero's initial single slot must be allocated to the Tera entrant if both
a Tera and an ordinary entrant need to enter that turn. Reversing their order
blocks the Tera before the eight-slot condition can turn on.

When several differently named Stadiums are in the discard pile, Teleport
must choose an eligible replacement. A fictitious option to discard Collapsed
and deliberately decline every available replacement is rejected. Another
physical Collapsed Stadium copy is ineligible as the replacement due to its
name.

The ordinary Stadium play may follow Teleport in the same turn because the
Ability leaves that quota unused. A separate contraction regression expands
from four to six Benched Pokémon with Sky Field, then plays Collapsed Stadium
from hand: exactly **15** four-survivor Bench subsets are enumerated, matching
`C(6,4)`, and all have final effective capacity four.

## Interpretation

An already-established Gothitelle provides a **third physical recovery
channel** beyond a new Stadium played from hand or a Stadium remover that must
first consume Bench space. Its effective output is determined by the *discard
zone at resolution* and by current Tera / Bench geometry. This is a useful
counterexample to measuring Stadium access entirely through hand-based
search-outs or treating all Stadium removal effects as interchangeable.

The cost of establishing a Stage 2 Gothitelle remains substantial. This result
does **not** claim that including Gothitelle is optimal in a competitive deck.

## Evidence and limitations

Card texts and action timing are grounded in the provided card pool and
Advanced Player's Rulebook. The named outcomes are deterministic state
transitions, tested against canonical repository Stadium and turn-budget
implementations. The successful CI test proves this bounded model's
specified cases; it is not a whole-game simulator.

The adapter treats Ability suppression as an upstream Boolean, assumes source
turn history is supplied correctly, and does not model opponents' simultaneous
Bench contraction, Stadium immunity/locks, search access, evolutions, damage,
Prize cards, or how cards reached the discard. Only the three named
Bench-capacity Stadiums have specialized capacity semantics; other Stadium
names default to ordinary capacity five.

## Next questions

1. Estimate the practical opportunity cost of pre-establishing Gothitelle
   versus drawing a direct restorative Stadium.
2. Couple Teleport access to K0/K1 Prize information and discard-zone contents.
3. Study when an obligatory discard-pile replacement is harmful under
   orientation-sensitive or other restrictive Stadium effects, after
   independently resolving those cards' placement rulings.
