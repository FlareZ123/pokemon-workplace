"""Apply exact copied-attack Energy disruption on the physical defender board.

This bridge owns step-5 attachment removal for complete one-Energy attack bodies
already compiled by energy_disruption_profile_compiler. It verifies the exact
copied body event, preserves physical card identity through the existing
conserved executor, and updates the copy resolution before step-6
damaged-by-attack reactions are evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from energy_disruption_executor import resolve_energy_disruption
from energy_disruption_profile_compiler import (
    EnergyDisruptionProfile,
    OpponentTargetScope,
)


@dataclass(frozen=True)
class PhysicalAttackEnergyDisruptionApplication:
    updated_copy_resolution: AttackCopyPhysicalBoardResolution
    profile: EnergyDisruptionProfile
    body_event: str
    target_pokemon_id: str | None
    discarded_energy_instance_id: str | None
    coin_heads: bool | None
    blocked_by_effect_immunity: bool


def apply_physical_attack_energy_disruption(
    replay: AttackCopyPhysicalBoardResolution,
    profile: EnergyDisruptionProfile,
    *,
    target_pokemon_id: str | None = None,
    energy_instance_id: str | None = None,
    special_energy_instance_ids: frozenset[str] = frozenset(),
    coin_heads: bool | None = None,
    blocked_effect_target_ids: frozenset[str] = frozenset(),
) -> PhysicalAttackEnergyDisruptionApplication:
    """Resolve one exact attack-source Energy discard after copied damage.

    For Active-target profiles, the target is the current opposing Active.
    Selected-target profiles require the caller to identify the chosen Pokemon
    whenever the effect succeeds. Effect-immunity is an upstream board overlay:
    if the affected Pokemon is blocked, step 5 leaves all attachments in place.
    """

    if profile.source_kind != "attack" or profile.attack_index is None:
        raise ValueError("physical Energy disruption requires an exact attack profile")

    body_event = f"body:{profile.card_id}:attack:{profile.attack_index}"
    if body_event not in replay.resolution.state.events:
        raise ValueError("copy-body trace did not execute this Energy-disruption source")

    board = replay.state.board
    if board is None:
        raise ValueError("Energy disruption requires an in-play defender board")

    if profile.target_scope == OpponentTargetScope.ACTIVE:
        resolved_target_id = board.active_id
        if target_pokemon_id is not None and target_pokemon_id != resolved_target_id:
            raise ValueError("Active-target disruption cannot choose another Pokemon")
    else:
        resolved_target_id = target_pokemon_id

    if (
        resolved_target_id is not None
        and resolved_target_id in blocked_effect_target_ids
    ):
        return PhysicalAttackEnergyDisruptionApplication(
            replay,
            profile,
            body_event,
            resolved_target_id,
            None,
            coin_heads,
            True,
        )

    outcome = resolve_energy_disruption(
        profile,
        replay.state,
        target_pokemon_id=resolved_target_id,
        energy_instance_id=energy_instance_id,
        special_energy_instance_ids=special_energy_instance_ids,
        coin_heads=coin_heads,
    )
    if outcome is None:
        raise ValueError("Energy-disruption choices do not satisfy the profile")

    return PhysicalAttackEnergyDisruptionApplication(
        replace(replay, state=outcome.state),
        profile,
        body_event,
        resolved_target_id,
        outcome.discarded_instance_id,
        outcome.coin_heads,
        False,
    )
