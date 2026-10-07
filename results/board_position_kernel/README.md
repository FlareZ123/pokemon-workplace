# Physical board-position kernel

## Question

What minimum state representation lets a planner distinguish normal retreat, card-effect switching, and ordinary evolution while preserving physical Pokémon identity and attached state?

Implementation: `tools/board_position_state.py` and `tools/board_position_kernel.py`  
Regression: `results/board_position_kernel/reproduce.py`

## Evidence and scope

This is a rules-derived deterministic state kernel. The mechanical source is the repository Advanced Player's Rulebook, especially A-03 Retreat, A-05 Evolution, B-02 Pokémon Tools, and C-03 Switching. Concrete database examples include `me1-1` Bulbasaur, `me1-2` Ivysaur, `me1-3` Mega Venusaur ex, `me1-130` Switch, `me1-166` Air Balloon, and Black & White-onward Double Colorless Energy.

The kernel consumes resolved values such as current effective Retreat Cost. It does not parse arbitrary card text.

## Findings

`BoardState` owns physical `BoardPokemon` instances plus one Active instance ID. Each instance carries an ordered stack of physical Pokémon cards, damage counters, typed attachments, combat flags, Special Conditions, Retreat Cost, and ordinary evolution eligibility.

**Full-Bench retreat is a position swap.** With one Active Pokémon and five Benched Pokémon, normal retreat remains legal because promotion vacates the Bench position used by the outgoing Active. A planner that treats `Active -> Bench` as a standalone insertion can reject a legal retreat.

**Retreat denial and switching require separate transitions.** In the regression, Paralysis plus a temporary retreat-denial effect blocks normal retreat. A card-effect switch still succeeds. It pays no retreat Energy, leaves the normal retreat action unused, preserves damage and attachments, and clears the outgoing Active Pokémon's transient effects when it reaches the Bench.

**Normal retreat consumes explicit physical resources.** A Bulbasaur with effective Retreat Cost 2 discards two selected one-unit Energy cards. Their physical IDs are returned by the transition. Damage and Air Balloon remain with the same Pokémon instance after movement.

**Retreat payment needs Energy units.** One Double Colorless Energy can pay a two-Colorless Retreat Cost. Payments are required to be minimally sufficient, preventing unrelated extra Energy cards from being discarded through the retreat action.

**Evolution needs stack identity.** The Bulbasaur -> Ivysaur -> Mega Venusaur ex regression appends each evolution card to the same physical stack. Damage and attachments persist. Active-only transient state clears. Same-turn ordinary double evolution is rejected, while `begin_next_turn` restores ordinary evolution eligibility.

## Relation to the unified state kernel

The current `unified_state_kernel.py` owns a canonical card-zone map but gives detailed state only to one Active Pokémon. It cannot yet represent that same damaged, Tool-bearing Pokémon moving to the Bench, another concrete Pokémon becoming Active, or several Pokémon cards forming one evolved stack.

This result supplies that missing physical identity layer. Future composition should map every card in an evolved stack and every attachment to one Pokémon instance while board-position transitions update its role.

## Limitations

The current kernel omits dynamic Retreat Cost calculation, HP and Knock Out handling, switching prevention, special evolution methods, devolution, full Energy-type semantics, turn ownership, and the complete attack lifecycle.

## Reproduction

Run `python results/board_position_kernel/reproduce.py`. The script asserts the rules-derived invariants and prints a compact JSON summary when all checks pass.
