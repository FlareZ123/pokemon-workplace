# Bulk Bench refresh: core compatibility and transactional throughput

## Question

Temporary self-constriction can clear several occupied Bench slots at once. When can that line preserve a persistent core board, and how much extra transactional support capacity does it create?

## Core compatibility theorem

Let a full Bench have current capacity `C). Let `R` of those occupants be persistent core Pokémon that the player refuses to discard. The other `C-R` occupants are stale transactional residents.

Apply a temporary restriction to capacity `c`, then remove that restriction so the Bench returns to release capacity `L`.

The restriction forces

`D = max(0, C-c)`

discards.

If stale residents are always chosen first, the persistent core survives intact exactly when

`R <= c`.

For a full board this condition is sufficient because `C-R >= C-c` whenever `R <= c`.

After the restriction is removed, the number of newly open slots is

`L-c`

when `c < L`.

This gives a simple compatibility threshold for the two Stadium refresh lines:

- Parallel City facing yourself preserves a core of at most three Pokémon and can reopen two normal Bench slots after removal.
- Collapsed Stadium preserves a core of at most four Pokémon and can reopen one normal Bench slot after removal.

A larger core makes the corresponding refresh destructive because at least one protected occupant must be discarded.

Implementation: `tools/bench_bulk_refresh.py`.

## One-refresh transactional throughput

Suppose the board starts with only a persistent core, then one-shot support Pokémon are played until the Bench is full. Each successful support becomes a stale resident. The player is allowed one temporary constriction-and-release cycle during the turn.

Under the simplified assumption that every transactional support is otherwise accessible and legal, the maximum number of support entries is:

`(C-R) + (L-c)`

when `R <= c`.

The first term is the initial room before the board fills. The second term is the bulk refresh gain.

### Normal five-slot Bench

| Core occupancy | Baseline entries before full | Parallel refresh total | Collapsed refresh total |
| ---: | ---: | ---: | ---: |
| 0 | 5 | 7 | 6 |
| 1 | 4 | 6 | 5 |
| 2 | 3 | 5 | 4 |
| 3 | 2 | 4 | 3 |
| 4 | 1 | destructive | 2 |
| 5 | 0 | destructive | destructive |

Parallel City provides two additional transactional slots when the persistent core is at most three. Collapsed Stadium provides one when the core is at most four.

### Full eight-slot expansion

If an eight-slot effect such as Sky Field is active, a full eight-Pokémon board contains `8-R` non-core residents. Replacing the expansion with the restricting Stadium changes the applicable maximum to three or four, forcing enough discards to reach that lower cap. Removing the restriction then returns to the normal five-slot limit.

| Core occupancy | Initial entries to fill 8 | Parallel refresh total | Collapsed refresh total |
| ---: | ---: | ---: | ---: |
| 0 | 8 | 10 | 9 |
| 1 | 7 | 9 | 8 |
| 2 | 6 | 8 | 7 |
| 3 | 5 | 7 | 6 |
| 4 | 4 | destructive | 5 |

The bulk-refresh gain remains two for Parallel City and one for Collapsed Stadium because the post-release capacity is five. The eight-slot expansion changes how many transactional residents can accumulate before the refresh.

## Relation to the release scheduler

`results/bench_capacity_schedule/` models one-slot release resources by action class. A bulk restriction has a different capacity shape. Parallel City can discard two stale occupants from a full normal Bench in one Stadium play, while Collapsed Stadium can discard one. A later Item or Ability Stadium-removal action can then reopen the corresponding slots in the same turn.

This does not make the bulk line universally cheaper. It consumes the Stadium play plus a release action, and it requires the persistent core to fit under the temporary cap. Item lock can also remove Field Blower-like release edges. The result is best represented as a multi-resource profile rather than a generic free-slot action.

## Concrete Expanded line

Field Blower is a legal Expanded Item whose text can discard the player's own Stadium. The same card text says Items may be played repeatedly before the attack. This supports the same-turn sequence:

`fill transactional Bench -> play restricting Stadium -> discard stale residents -> Field Blower the restriction -> reuse opened slots`.

Attack-based Stadium removal cannot provide the same same-turn throughput because using the attack ends the turn.

## Strategic interpretation

This establishes a discrete threshold effect. A Parallel City refresh can be excellent beside a three-Pokémon core and unacceptable beside a four-Pokémon core, even when only one additional permanent core slot changed.

The threshold belongs in Active Move Realism. A graph that sees both the restriction and the release card as reachable still needs current core occupancy to know whether the line preserves the intended board.

## Validation

`results/bench_bulk_refresh/reproduce.py` checks the core-preservation threshold, reopened-slot counts, and representative normal and eight-slot throughput rows.

## Limits

The throughput model treats every non-core support as equally stale and every desired support entry as immediately accessible. It omits Prize placement, search costs, trigger zones, Supporter contention, Item lock, Stadium lock, opponent effects, and the strategic value of the restricting Stadium while it remains in play.

It is a capacity kernel for integration with the repository's typed connector and Bench-release models.
