"""Apply copied-attack damage reactions to conserved physical Pokémon boards.

This adapter consumes the completed copied-attack physical replay. It preserves
both players' card-instance ledgers through post-damage counter reactions and
defers every Knock Out to the existing simultaneous-batch phase.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from board_position_state import replace_pokemon
from damage_calculation_kernel import DamageResult
from damage_reaction_kernel import DamageReaction, DamageReactionKind
from simultaneous_knockout_conservation import (
    PendingKnockOutBatch,
    prepare_knock_out_batch,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class PhysicalCopyReactionResult:
    copy_resolution: AttackCopyPhysicalBoardResolution
    attacker_state: StackBoardMaterialState
    defender_state: StackBoardMaterialState
    body_event: str
    damaged_pokemon_id: str
    damage_result: DamageResult
    triggered: bool
    counters_placed_on_attacker: int
    attacker_knocked_out_ids: tuple[str, ...]
    defender_knocked_out_ids: tuple[str, ...]


def _knocked_out(
    state: StackBoardMaterialState,
    hp_by_pokemon_id: Mapping[str, int],
) -> tuple[str, ...]:
    board = state.board
    if board is None:
        raise ValueError("Knock Out detection needs an in-play board")
    result: list[str] = []
    for pokemon in board.pokemon:
        hp = hp_by_pokemon_id[pokemon.pokemon_id]
        if hp <= 0 or hp % 10:
            raise ValueError("Pokémon HP must be a positive multiple of 10")
        if pokemon.damage_counters * 10 >= hp:
            result.append(pokemon.pokemon_id)
    return tuple(result)


def _reaction_counters(reaction: DamageReaction, damage: int) -> int:
    if reaction.kind is DamageReactionKind.FIXED_COUNTERS:
        return reaction.fixed_counters
    if reaction.kind is DamageReactionKind.MIRROR_FINAL_DAMAGE:
        if damage % 10:
            raise ValueError("mirrored damage must convert to counters")
        return damage // 10
    if reaction.kind is DamageReactionKind.SCALED_COUNTERS:
        return reaction.fixed_counters * reaction.scale_count
    raise AssertionError(reaction.kind)


def resolve_physical_copy_damage_reactions(
    copy_resolution: AttackCopyPhysicalBoardResolution,
    attacker_state: StackBoardMaterialState,
    *,
    body_event: str,
    damaged_pokemon_id: str,
    reactions: tuple[DamageReaction, ...],
    attacker_hp_by_pokemon_id: Mapping[str, int],
    defender_hp_by_pokemon_id: Mapping[str, int],
) -> PhysicalCopyReactionResult:
    """Resolve one damage event's ordered reactions on the physical attacker.

    The caller supplies only reactions whose live source, position, timing,
    attached-card state, and damaged target have already been verified.
    """

    matches = [
        result
        for event, result in copy_resolution.damage_results
        if event == body_event
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected one executed damage event {body_event!r}; got {len(matches)}"
        )
    damage_result = matches[0]
    target_ids = [
        target for event, target in copy_resolution.damage_targets
        if event == body_event
    ]
    if target_ids != [damaged_pokemon_id]:
        raise ValueError("reaction source disagrees with physical damage target")
    if attacker_state.board is None or copy_resolution.state.board is None:
        raise ValueError("damage reactions require two live physical boards")

    current = attacker_state
    placed = 0
    triggered = damage_result.final_damage > 0
    if triggered:
        for reaction in reactions:
            count = _reaction_counters(reaction, damage_result.final_damage)
            if count:
                board = current.board
                assert board is not None
                active = board.get(board.active_id)
                updated = replace(
                    active,
                    damage_counters=active.damage_counters + count,
                )
                current = StackBoardMaterialState(
                    current.ledger,
                    replace_pokemon(board, updated),
                )
            placed += count

    return PhysicalCopyReactionResult(
        copy_resolution=copy_resolution,
        attacker_state=current,
        defender_state=copy_resolution.state,
        body_event=body_event,
        damaged_pokemon_id=damaged_pokemon_id,
        damage_result=damage_result,
        triggered=triggered,
        counters_placed_on_attacker=placed,
        attacker_knocked_out_ids=_knocked_out(
            current, attacker_hp_by_pokemon_id
        ),
        defender_knocked_out_ids=_knocked_out(
            copy_resolution.state, defender_hp_by_pokemon_id
        ),
    )


def prepare_reacted_physical_knockouts(
    result: PhysicalCopyReactionResult,
) -> tuple[PendingKnockOutBatch | None, PendingKnockOutBatch | None]:
    """Keep zero-HP Pokémon and attachments in play until KO triggers finish."""

    attacker = (
        prepare_knock_out_batch(
            result.attacker_state, result.attacker_knocked_out_ids
        )
        if result.attacker_knocked_out_ids
        else None
    )
    defender = (
        prepare_knock_out_batch(
            result.defender_state, result.defender_knocked_out_ids
        )
        if result.defender_knocked_out_ids
        else None
    )
    return attacker, defender
