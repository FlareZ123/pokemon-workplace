# Named Ability predicates as physical Active/Bench guards

## Question

Can a catalog of named-Pokémon Ability prerequisites be applied directly to a physical board representation while preserving the distinction between a hard capacity obstruction and an unsatisfied or suppressed Ability?

Yes. `tools/bench_named_guard_board.py` bridges `tools/bench_named_ability_dependencies.py` to the pre-existing `tools/board_object_kernel.py`. It uses `BoardState` object identities, the actual Active/Bench locations, card print IDs, the current Bench capacity, and `abilities_enabled`.

## Mechanism

Given a validated physical board, a source Pokémon object, and a cataloged Ability guard, the adapter checks:

1. whether the source name matches the cataloged source;
2. whether the source's print ID is one of the copies having that specific Ability;
3. whether the named dependency's minimum Bench slots exceed the current capacity;
4. whether all required names actually occupy the specified zone (`in play` or `on your Bench`);
5. whether the source's Ability is enabled.

The result carries one of these statuses: `source_name_mismatch`, `unverified_source_print`, `capacity_impossible`, `missing_named_requirements`, `source_ability_suppressed`, or `named_guard_satisfied`.

The status `named_guard_satisfied` deliberately does **not** claim that the entire Ability is usable. The adapter does not check additional Energy-discard costs, once-per-turn usage, target legality, changes caused by other active effects, or whether the player has an opportunity to announce that Ability.

## Concrete 2026 Expanded witnesses

### Regigigas Ancient Wisdom

The Ability is printed on Regigigas `swsh10-130` and requires five other distinct named Pokémon: Regirock, Regice, Registeel, Regieleki, and Regidrago.

The physical adapter verifies:

| Board state | Physical guard result |
| --- | --- |
| Regigigas Active plus all five named required Pokémon Benched, capacity 5 | `named_guard_satisfied` |
| Regigigas Active plus four required Pokémon Benched, capacity 4 | `capacity_impossible` |
| Regigigas Active plus three required Pokémon Benched, capacity 3 | `capacity_impossible` |

At capacities four and three, the missing prerequisites are also visible, but the capacity lower bound proves that **no legal rearrangement within that limit** could restore the condition under the ordinary distinct-name interpretation.

### Lunatone Lunar Cycle

Lunatone `me1-74` with Solrock on its Bench is reported as `named_guard_satisfied`. Replacing Solrock with an unrelated Basic changes the result to `missing_named_requirements`.

Switching the source to an alternate Lunatone print lacking this particular Ability yields `unverified_source_print`. Keeping the correct print but setting `abilities_enabled=False` produces `source_ability_suppressed`. This prevents a species-only dependency graph from mistakenly granting the Ability to every card with that species name.

## Validation

Run `python tools/bench_named_guard_board.py --self-test` for five regression tests covering the preceding cases and a controlled on-Bench-only requirement.

Run the script without flags to print a JSON example contrasting the five-, four-, and three-slot Regigigas boards.

The GitHub Actions validation passed: [run 37919658197](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37919658197).

## Research significance

The bridge creates a small but important separation of concerns:

- **Structural impossibility:** the required named set cannot fit in the allowed physical positions.
- **Absent prerequisites:** the board has enough capacity, but the required names are missing from their required positions.
- **Suppression:** the named prerequisites are present, but the source Ability is disabled.
- **Named guard satisfied:** only the named co-presence part has been established.

This structure can feed a larger constrained action-enumerator without treating an available search path or a matching species name as proof of a playable Ability.

## Limits

The adapter does not simulate any deck or turn, react to a Stadium being played, or update a board through contraction. It receives already-legal boards from the mechanical kernel. It also uses the scanner's conservative literal grammar; abilities with more complicated conditions will need their own exact guard compilations. Conditional multiple names per Pokémon, if established by a specific card effect, would require extending the name-identity model.
