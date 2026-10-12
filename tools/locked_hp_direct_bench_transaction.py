"""Execute printed-HP-bound direct Bench Items under source-scoped locks.

The lock engine receives already-effective restrictions on the acting player.
The existing HP-bounded adapter authenticates exact targets and the physical
Trainer transaction owns the Item lifecycle, Bench capacity and conservation.
The source-scoped projection is evaluated without mutating base channels.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from card_action_metadata import CardActionMetadata
from direct_bench_search_execution import DirectBenchPlacement, DirectBenchTarget
from direct_bench_trainer_transaction import (
    DirectBenchTrainerExecutionState,
    DirectBenchTrainerTransaction,
)
from hp_bounded_direct_bench_transaction import (
    HPBoundedDirectBenchProfile,
    execute_hp_bounded_direct_bench_trainer_transaction,
)
from pokemon_board_metadata import PokemonBoardMetadata
from pokemon_card_profile import PokemonCardProfile
from source_scoped_action_restrictions import SourceScopedActionRestriction
from source_scoped_channel_projection import (
    action_allowed,
    project_source_scoped_permissions,
)
from typed_search_target_allocator import DemandChannel, TypedTargetAction


def execute_locked_hp_direct_bench_trainer_transaction(
    state: DirectBenchTrainerExecutionState,
    profile: HPBoundedDirectBenchProfile,
    *,
    action_card_class: str,
    active_restrictions: Sequence[SourceScopedActionRestriction],
    action_metadata_by_id: Mapping[str, CardActionMetadata],
    demands: Sequence[DemandChannel],
    targets: Sequence[DirectBenchTarget],
    search_action: TypedTargetAction,
    placements: Sequence[DirectBenchPlacement],
    board_metadata_by_id: Mapping[str, PokemonBoardMetadata],
    card_profiles_by_id: Mapping[str, PokemonCardProfile],
) -> DirectBenchTrainerTransaction:
    """Check a real hand-origin Item permission before the atomic Bench search.

    A failed lock, printed-HP, or physical-capacity check raises without
    returning a mutated game state. Active restrictions are owned upstream;
    this boundary only evaluates them for the attempted hand-sourced Item.
    """

    if action_card_class != profile.direct.card_id:
        raise ValueError("played print disagrees with HP-bounded Item profile")
    action_metadata = action_metadata_by_id.get(action_card_class)
    if action_metadata is None:
        raise ValueError("no trusted exact action metadata for played Item")
    if action_metadata.card_id != action_card_class or action_metadata.card_kind != "item":
        raise ValueError("played print metadata is not an Item")

    projected = project_source_scoped_permissions(
        active_restrictions,
        base_channels=state.channels,
    )
    if not action_allowed(projected, action_metadata.attempt("hand")):
        raise ValueError("HP-bounded Item play is prohibited by active restrictions")

    return execute_hp_bounded_direct_bench_trainer_transaction(
        state,
        profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        placements=placements,
        board_metadata_by_id=board_metadata_by_id,
        card_profiles_by_id=card_profiles_by_id,
    )
