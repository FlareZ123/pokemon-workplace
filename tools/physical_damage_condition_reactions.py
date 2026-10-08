"""Source-verified status reactions following physical copied-attack damage.

The physical board stores ordinary Special Condition names; this module uses
the existing typed condition helper for replacement/coexistence semantics.
Irregular condition payloads are intentionally outside this narrow bridge.
"""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import re

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from board_position_state import replace_pokemon
from build_expanded_legality_baseline import classify_effective_legality
from physical_copy_damage_reaction_bridge import PhysicalCopyReactionResult
from special_condition_state import (
    ConditionKind,
    SpecialConditionState,
    apply_condition,
    legacy_name_projection,
    regular_condition,
)
from stack_knockout_conservation import StackBoardMaterialState


_CONDITION_ABILITY = re.compile(
    r"^If this Pokémon is in the Active Spot and is damaged by an attack "
    r"from your opponent's Pokémon \(even if this Pokémon is Knocked Out\), "
    r"the Attacking Pokémon is now (?P<condition>Poisoned|Burned|Confused)\.$"
)


def eligible_printed_condition_reactions(
    copy_resolution: AttackCopyPhysicalBoardResolution,
    *,
    resources: Path,
    body_event: str,
    damaged_pokemon_id: str,
    defending_print_id: str,
    ability_is_enabled: bool,
    from_opponents_pokemon: bool,
) -> tuple[ConditionKind, ...]:
    """Compile matching passive reaction Abilities from a specific legal print."""

    records = [
        row for row in copy_resolution.damage_records
        if row.event == body_event and row.target_id == damaged_pokemon_id
    ]
    if len(records) != 1:
        raise ValueError("exactly one event/target damage record is required")

    board = copy_resolution.state.board
    if board is None:
        raise ValueError("reaction-source Pokémon is no longer in play")

    source_id = defending_print_id.split("-")[0]
    all_sets = json.loads(
        (resources / "sets" / "en.json").read_text(encoding="utf-8")
    )
    set_entry = next(row for row in all_sets if row["id"] == source_id)
    if (set_entry.get("legalities") or {}).get("expanded") != "Legal":
        raise ValueError("reaction source set is outside paper Expanded")
    cards = json.loads(
        (resources / "cards" / "en" / f"{source_id}.json")
        .read_text(encoding="utf-8")
    )
    card = next(card for card in cards if card["id"] == defending_print_id)
    if classify_effective_legality(card)[0] != "Legal":
        raise ValueError("reaction source print is not effectively Expanded legal")
    if board.get(damaged_pokemon_id).name != card["name"]:
        raise ValueError("live source Pokémon and bound print disagree")

    if (
        board.active_id != damaged_pokemon_id
        or not ability_is_enabled
        or not from_opponents_pokemon
        or records[0].result.final_damage == 0
    ):
        return ()

    result = []
    for ability in card.get("abilities") or ():
        text = " ".join((ability.get("text") or "").split())
        match = _CONDITION_ABILITY.fullmatch(text)
        if match:
            result.append(ConditionKind(match.group("condition")))
    return tuple(result)


def apply_physical_condition_reactions(
    base: PhysicalCopyReactionResult,
    conditions: tuple[ConditionKind, ...],
) -> tuple[PhysicalCopyReactionResult, tuple[ConditionKind, ...]]:
    """Apply eligible regular Special Conditions to the original attacker.

    If the attacking Pokémon is now Benched, Special Conditions have no
    eligible target. Counters/Knock Outs from earlier reactions are untouched.
    The returned wrapper remains consumable by the pending-KO bridge.
    """

    board = base.attacker_state.board
    if board is None:
        raise ValueError("cannot apply a condition without a board")
    if not base.triggered or board.active_id != base.attacking_pokemon_id:
        return base, ()

    attacker = board.get(base.attacking_pokemon_id)
    typed = SpecialConditionState()
    for name in sorted(attacker.special_conditions):
        typed = apply_condition(typed, regular_condition(ConditionKind(name)))

    for condition in conditions:
        typed = apply_condition(typed, regular_condition(condition))
    next_attacker = replace(
        attacker, special_conditions=legacy_name_projection(typed),
    )
    next_board = replace_pokemon(board, next_attacker)
    next_state = StackBoardMaterialState(base.attacker_state.ledger, next_board)
    return replace(base, attacker_state=next_state), conditions
