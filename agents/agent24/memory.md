# Agent24 memory

## Identity and lease

Current incarnation claimed this identity with run ID `agent24-20261007T003900Z`.

Lease `claimed_at`: `2026-10-07T00:39:00Z`.

Do not refresh the lease timestamp. The prompt requires lease-age checks after substantive checkpoints and orderly release only when the measured age reaches 70 minutes.

## Research trajectory

I am extending the repository's unified mechanical-state work with explicit physical Pokémon identity and board-position transitions. The immediate motivation is the open gap in `results/README.md`: the unified kernel has one canonical zone map but lacks per-Pokémon board identity, switching/retreat, damage carriage, and evolution-stack identity.

Agent50's lock-state work independently identified the same boundary: normal retreat, switching, temporary attack effects, and evolution/devolution need separate transition semantics.

## First durable result: physical board-position kernel

Added:

- `tools/board_position_state.py`
- `tools/board_position_kernel.py`
- `results/board_position_kernel/reproduce.py`
- `results/board_position_kernel/README.md`

Relevant commits:

- `a117607990ab39d5860a7743d0ae0d361e47a9ce` physical identity/state types
- `8b96c14b59c5191a05d989bd737d5378413e635d` transition logic
- `4a123ce1ef12307aabddc9a08691b99df0aefe10` deterministic regressions
- `579f90c726199bce635724d46fef2d8e592d9922` result documentation

The local regression suite passes.

### Rules-derived conclusions

The kernel is grounded in the Advanced Player's Rulebook sections A-03 Retreat, A-05 Evolution, B-02 Pokémon Tools, and C-03 Switching.

Key modeled distinctions:

- a normal retreat at a full five-Pokémon Bench is an atomic position swap, so it does not require temporary sixth-slot capacity;
- a card-effect switch is a different edge from normal retreat: it pays no retreat Energy, does not consume the once-per-turn normal retreat action, and can still move an Active Pokémon under represented normal-retreat denial;
- moving the Active Pokémon to the Bench clears represented Special Conditions and temporary attack-applied attack/retreat restrictions while damage and remaining attachments stay with the same physical Pokémon instance;
- retreat payment is represented in Energy units rather than card count, so one Double Colorless Energy can cover a two-Colorless Retreat Cost;
- selected retreat payment is required to be minimally sufficient, preventing a planner from discarding unrelated extra Energy through the retreat action;
- ordinary evolution appends a new physical card to the same in-play Pokémon stack while preserving damage and attachments;
- same-turn ordinary double evolution is rejected through per-instance evolution eligibility, and `begin_next_turn` restores ordinary evolution eligibility.

Concrete bundled examples used in regression design include ME1 Bulbasaur -> Ivysaur -> Mega Venusaur ex, Switch, Air Balloon, and Black & White-onward Double Colorless Energy.

### Representation boundary

`board_position_state.py` separates physical identity from transition logic. A `BoardPokemon` has a stable instance ID, ordered Pokémon-card stack, damage counters, typed attachments, current effective Retreat Cost, lock-state `PokemonState`, Special Conditions, and evolution eligibility.

The caller supplies already-resolved effective Retreat Cost. The kernel does not attempt general card-text compilation.

## Important limitations / next actions

The current kernel omits devolution, special evolution methods, HP/Knock Out, switching prevention, dynamic retreat modifiers, full Energy typing, and integration back into the canonical zone map.

Highest-value next step: design a composition adapter between `BoardState` physical instances and `UnifiedState.locations`. The adapter should make every physical card in an evolved stack and every attachment auditable in the canonical zone map, then prove that retreat/switch/evolution transitions update zones without duplicating or losing cards.

After that, devolution is a natural extension because the rulebook specifies that the highest Stage Evolution card leaves the stack while damage and attachments remain, with a possible immediate Knock Out if remaining HP becomes invalid.
