"""Bridge copy-resolution turn-boundary effects into canonical turn scheduling."""

from __future__ import annotations

from attack_copy_kernel import Resolution
from canonical_turn_sequence_owner import TurnScheduleState, close_turn_with_attack
from unified_state_kernel import UnifiedState


def close_declared_attack(
    schedule: TurnScheduleState,
    current_state: UnifiedState,
    resolution: Resolution,
) -> tuple[TurnScheduleState, UnifiedState] | None:
    """Close exactly one declared attack after all nested copied bodies finish."""

    boundary = resolution.state.pending_turn_boundary
    return close_turn_with_attack(
        schedule,
        current_state,
        take_another_turn=(
            boundary.take_another_turn if boundary is not None else False
        ),
        skip_pokemon_checkup=(
            boundary.skip_pokemon_checkup if boundary is not None else False
        ),
    )
