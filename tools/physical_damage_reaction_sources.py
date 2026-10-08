"""Resolve a Spiky Energy damage reaction from the physical game board."""

from __future__ import annotations

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from board_position_state import AttachmentKind
from damage_reaction_kernel import DamageReaction, DamageReactionKind


def eligible_spiky_energy_reactions(
    copy_resolution: AttackCopyPhysicalBoardResolution,
    *,
    body_event: str,
    damaged_pokemon_id: str,
    from_opponents_pokemon: bool,
) -> tuple[DamageReaction, ...]:
    """Compile attached Spiky Energy triggers during post-damage reactions.

    The physical replay establishes the damaged target and positive final
    damage. The caller supplies whether the attack comes from an opponent's
    Pokémon, as required by the specific Energy card's printed condition.
    """

    target_ids = [
        target for event, target in copy_resolution.damage_targets
        if event == body_event
    ]
    results = [
        damage for event, damage in copy_resolution.damage_results
        if event == body_event
    ]
    if target_ids != [damaged_pokemon_id] or len(results) != 1:
        raise ValueError("Spiky Energy needs one matching damage event")

    board = copy_resolution.state.board
    if board is None:
        raise ValueError("Spiky Energy requires a physical board")

    if (
        results[0].final_damage <= 0
        or not from_opponents_pokemon
        or board.active_id != damaged_pokemon_id
    ):
        return ()

    return tuple(
        DamageReaction(DamageReactionKind.FIXED_COUNTERS, fixed_counters=2)
        for attachment in board.get(damaged_pokemon_id).attachments
        if attachment.kind is AttachmentKind.ENERGY
        and attachment.name == "Spiky Energy"
    )
