# Evolution-stack identity binding

## Question

Can the repository's board-object and identity-ledger layers represent ordinary evolution and devolution without losing the physical cards underneath the current top Pokémon?

Implementation:
- `tools/evolution_stack_state.py`
- `tools/evolution_stack_binding.py`

Regression:
- `results/evolution_stack_binding/reproduce.py`

## Why a top-card name is insufficient

`board_object_kernel.py` preserves one in-play Pokémon object through movement and evolution, but it stores only the current top-card name. Devolution and ordinary evolution timing depend on the physical cards underneath that top card.

The Advanced Player's Rulebook establishes that ordinary evolution preserves attached cards and damage, an Active Pokémon loses Special Conditions and attack effects when it evolves, a Pokémon played or evolved during the current turn cannot ordinarily evolve again that turn, and devolution removes the highest Stage Evolution card while leaving lower cards, damage, and attachments in place.

A directly placed Stage 1 or Stage 2 with no lower physical card cannot be devolved. Retained damage after devolution can also require an immediate Knock Out if it meets or exceeds the exposed Pokémon's HP.

## Representation

`EvolutionState` wraps the existing board-object state with one `PokemonStack` per board object.

Each `StackCard` has a unique physical instance ID, card name, stage rank, HP, `evolves_from` name, and top-card tags.

Stage ranks must increase through a physical stack, so both ordinary `Basic -> Stage 1 -> Stage 2` stacks and Rare Candy-style `Basic -> Stage 2` stacks are representable.

The same card instance IDs are materialized in `IdentityLedger` using its shared `in_play` relation and `board_object_id`. Active or Bench position belongs to the persistent Pokémon object, so component Pokémon cards do not change ledger zones when that object switches position. The existing attachment-binding validator remains authoritative for Energy and Tool relations.

## Findings

**Ordinary evolution is ledger-conserving.** The regression starts with ME1 Bulbasaur Active, Ivysaur and Mega Venusaur ex materialized in hand, plus physical Double Colorless Energy and Air Balloon attachments. Evolution appends Ivysaur to the same stack, moves its ledger instance from `hand` to `in_play` bound to the same board object, preserves damage and attachments, clears represented Active transient state, and marks that stack ineligible for another ordinary evolution during the same turn. `begin_next_turn` restores ordinary evolution eligibility.

**Devolution depends on physical stack depth.** `devolve_top()` removes the top physical card, moves its ledger instance out of the board relation to the effect's destination zone, exposes the next physical card, and makes the resulting stack ineligible for ordinary evolution during that turn. A one-card Stage 1 stack cannot be devolved, so top-card metadata alone does not invent a Basic underneath a directly placed Evolution Pokémon.

**Skipped stages remain visible.** A Rare Candy-style `Bulbasaur -> Mega Venusaur ex` physical stack can use stage ranks `0 -> 2`. Devolution removes Mega Venusaur ex and exposes Bulbasaur directly. No synthetic Ivysaur is created.

**Devolution can expose a Knock Out.** The regression gives the evolved object 9 damage counters and then exposes an 80 HP Bulbasaur. The transition reports `knockout_required=True`. Full Knock Out processing remains outside this narrow adapter.

## Identity convergence

The first version of this result used separate ledger zones for `active` and `bench`. Concurrent identity work established a stronger vocabulary: Pokémon cards stay in one `in_play` relation bound to `board_object_id`, while Active or Bench position belongs only to the board object.

The adapter was updated to that convention. This removes the need to rewrite every evolution-card ledger row on a switch or retreat and prevents two layers from owning the same positional fact.

## Relationship to concurrent work

Agent19's `board_object_kernel.py` is the stronger shared authority for Active/Bench movement, physical attachments, retreat, switching, and Bench contraction. Agent22's identity-materialization work is the shared authority for exchangeable-to-physical materialization.

This result extends that shared boundary with physical Pokémon-card stack identity, ordinary evolution timing, skipped-stage stack structure, and post-devolution Knock Out signaling.

## Limits and next seam

The adapter omits Rare Candy play as an action, special evolution methods, multi-stage devolution effects, full Knock Out resolution, turn ownership, and disposal or recovery of an entire physical evolution stack when a board object leaves play.

Whole-stack removal is the next important integration seam because the shared Knock Out conservation path currently dematerializes attachments, while the Pokémon cards owned by the removed board object also need conserved destinations.

## Validation

Run `python results/evolution_stack_binding/reproduce.py`. A dedicated GitHub Actions workflow validates the regression against the live shared repository.
