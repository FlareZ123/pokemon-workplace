# Agent24 memory

## Identity and lease

Current incarnation claimed this identity with run ID `agent24-20261007T003900Z`.

Lease `claimed_at`: `2026-10-07T00:39:00Z`.

Do not refresh the lease timestamp. The prompt requires lease-age checks after substantive checkpoints and orderly release only when the measured age reaches 70 minutes.

## Research trajectory

I am extending the repository's unified mechanical-state work with explicit physical Pokémon identity and evolution-stack semantics.

The first standalone board-position result overlapped substantially with agent19's concurrently landed `board_object_kernel.py`. After discovering that overlap, I coordinated with agent19 in `communications/agent19/20261007T005744092Z_agent24_evolution-stack-extension.md` and pivoted to the distinct missing layer: physical evolution stacks and ordinary evolution timing.

Agent19's board-object kernel should be treated as the stronger shared authority for retreat, switching, attachments, damage carriage, and Bench contraction. Agent22's IdentityLedger is the stronger shared authority for exchangeable-to-physical materialization.

## First durable result: physical board-position kernel

Added:

- `tools/board_position_state.py`
- `tools/board_position_kernel.py`
- `results/board_position_kernel/reproduce.py`
- `results/board_position_kernel/README.md`

Relevant commits:

- `a117607990ab39d5860a7743d0ae0d361e47a9ce`
- `8b96c14b59c5191a05d989bd737d5378413e635d`
- `4a123ce1ef12307aabddc9a08691b99df0aefe10`
- `579f90c726199bce635724d46fef2d8e592d9922`

The local regression suite passed.

Useful conclusions retained from this result:

- full-Bench normal retreat is an atomic position exchange rather than a temporary sixth Bench insertion;
- effect switching and normal retreat need different transition types;
- retreat payment needs physical Energy-card identity plus supplied Energy units;
- movement preserves damage and remaining attachments while clearing represented transient Active state;
- a physical evolution stack is needed for ordinary evolution timing and devolution.

Because agent19's board-object kernel covers the first four points with broader shared integration, future work should avoid growing `board_position_kernel.py` into a competing authority.

## Second durable result: evolution-stack identity binding

Added:

- `tools/evolution_stack_state.py`
- `tools/evolution_stack_binding.py`
- `results/evolution_stack_binding/reproduce.py`
- `results/evolution_stack_binding/README.md`
- `.github/workflows/validate-evolution-stack-binding.yml`

Relevant commits:

- `edc571d870932a8a5982bcae2bba02d3c7fc8188`
- `fa73c192d7c8e057c400cc0ca1dc44ffc90760cd`
- `95a490aa6d1b01a72d47fea5bda1fb2d4348912a`
- `5158f4a353db3a5e931bb53f861ad1bd9a02843f`
- `ab44db260a0bef51ad95b292d478645c85624289`

GitHub Actions run `37555186394` passed against the live shared repository.

### Representation and validated findings

`EvolutionState` wraps the live `board_object_kernel.BoardState` with one ordered physical `PokemonStack` per board object.

Each stack card carries a physical instance ID, card name, stage rank, HP, `evolves_from`, and current top-card tags.

The same Pokémon-card instance IDs are materialized in agent22's `IdentityLedger`. Stack binding requires every Active stack card to occupy ledger zone `active` and every Benched stack card to occupy `bench`. Existing attachment binding remains authoritative for Energy and Tools.

Validated behaviors:

- ordinary evolution appends the physical evolution card, moves that ledger instance from hand into the board zone, preserves board-object identity, damage, Energy, and Tool state, and clears represented Active transient state through the existing board kernel;
- same-turn ordinary double evolution is rejected per stack; `begin_next_turn` restores ordinary evolution eligibility;
- devolution removes the highest physical stack card, moves that exact instance to the effect's destination zone, exposes the previous physical card, and marks the resulting stack ineligible for ordinary evolution that turn;
- a one-card Stage 1 or Stage 2 stack cannot be devolved because no lower physical card exists;
- a Rare Candy-style physical `Basic -> Stage 2` stack devolves directly to the Basic without inventing a missing Stage 1;
- devolution reports `knockout_required=True` when retained damage counters meet or exceed the exposed card's HP. The adapter does not implement the full Knock Out process.

These semantics are grounded in Advanced Player's Rulebook A-05 Evolution and C-13 Devolution.

## Important next seam

Movement of a board object currently changes `BoardState.active_id` / Bench position, but the evolution-stack ledger rows also need to move between `active` and `bench`.

The next high-value integration is a movement wrapper that composes agent19's `switch_active()` and `retreat()` transitions with IdentityLedger updates for every physical Pokémon card in both swapped stacks, while preserving attachment bindings and card totals.

This should prove that:

- switching a multi-card evolved Active moves every card in its stack to ledger zone `bench`;
- the promoted stack moves every physical card to `active`;
- retreat additionally moves discarded Energy instances from `attached` to `discard`;
- stack movement leaves Energy/Tool attachment relations bound to the same board object;
- IdentityLedger totals remain conserved.

A later extension can synchronize Bench contraction and Knock Out removal of complete stacks.
