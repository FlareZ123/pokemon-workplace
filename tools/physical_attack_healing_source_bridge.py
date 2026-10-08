"""Apply exact self-healing attack effects to the physical copying Pokemon.

The copied attack's printed "this Pokemon" refers to the Pokemon actually
using the copied body. This bridge consumes the actor's separate
StackBoardMaterialState, verifies the exact copy-body event, and heals that
physical object during the attack-effect step after damage and before
post-damage reactions.
"""

from __future__ import annotations

from dataclasses import dataclass

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from healing_profile_compiler import (
    HealingProfile,
    HealingTarget,
    apply_healing_profile,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class PhysicalAttackHealingApplication:
    actor_state: StackBoardMaterialState
    copy_resolution: AttackCopyPhysicalBoardResolution
    profile: HealingProfile
    body_event: str
    attacking_pokemon_id: str
    counters_removed: int


def apply_physical_attack_self_healing(
    replay: AttackCopyPhysicalBoardResolution,
    actor_state: StackBoardMaterialState,
    profile: HealingProfile,
    *,
    attacking_pokemon_id: str,
) -> PhysicalAttackHealingApplication:
    """Heal the physical Pokemon that executed an exact copied attack body."""

    if (
        profile.source_kind != "attack"
        or profile.target != HealingTarget.SOURCE_POKEMON
        or profile.attack_index is None
    ):
        raise ValueError("physical copy healing requires an exact attack profile")

    body_event = f"body:{profile.card_id}:attack:{profile.attack_index}"
    if body_event not in replay.resolution.state.events:
        raise ValueError("copy-body trace did not execute this healing source")

    board = actor_state.board
    if board is None:
        raise ValueError("healing requires an in-play actor board")
    try:
        before = board.get(attacking_pokemon_id)
    except StopIteration as exc:
        raise ValueError("attacking Pokemon is not on the actor board") from exc

    healed_board = apply_healing_profile(
        profile,
        board,
        source_pokemon_id=attacking_pokemon_id,
    )
    assert healed_board is not None
    after = healed_board.get(attacking_pokemon_id)

    return PhysicalAttackHealingApplication(
        actor_state=StackBoardMaterialState(actor_state.ledger, healed_board),
        copy_resolution=replay,
        profile=profile,
        body_event=body_event,
        attacking_pokemon_id=attacking_pokemon_id,
        counters_removed=before.damage_counters - after.damage_counters,
    )
