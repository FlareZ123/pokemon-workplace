"""Live board-derived restriction gating for materialized paired gust Trainers.

Before playing a source, derive active continuous restrictions from physical
Pokemon positions plus causal Ability-lock state and temporal attack windows.
After the source resolves, advance that causal state and recalculate live locks.
"""
from collections.abc import Sequence
from dataclasses import dataclass

from tools.ability_lock_causal_state import (
    AbilityLockCausalState, advance_lock_state,
)
from tools.attack_restriction_turn_windows import AttackRestrictionWindow
from tools.board_derived_continuous_restrictions import (
    active_restrictions_from_boards,
)
from tools.board_object_kernel import BoardState
from tools.card_action_metadata import CardActionMetadata
from tools.identity_materialization import IdentityLedger
from tools.paired_gust_source_permissions import execute_permissioned_paired_switch
from tools.paired_switch_identity_bridge import MaterializedPairedSwitchTransaction
from tools.paired_switch_order_catalog import PairedSwitchProgram
from tools.source_scoped_action_restrictions import SourceScopedActionRestriction
from tools.source_scoped_restriction_activation import RestrictionActivationProfile
from tools.turn_action_budget import TurnActionBudget


@dataclass(frozen=True)
class LivePairedSwitchResolution:
    transaction: MaterializedPairedSwitchTransaction
    lock_state: AbilityLockCausalState
    restrictions_before: tuple[SourceScopedActionRestriction, ...]
    restrictions_after: tuple[SourceScopedActionRestriction, ...]


def execute_live_paired_switch(
    ledger: IdentityLedger,
    player_board: BoardState,
    opponent_board: BoardState,
    turn_budget: TurnActionBudget,
    lock_state: AbilityLockCausalState,
    program: PairedSwitchProgram,
    metadata: CardActionMetadata,
    *,
    profiles: Sequence[RestrictionActivationProfile],
    source_instance_ids: tuple[str, ...],
    opponent_promote_id: str | None,
    own_promote_id: str | None,
    attack_windows: Sequence[AttackRestrictionWindow] = (),
    stadium_name: str | None = None,
) -> LivePairedSwitchResolution | None:
    """A player acting against the opponent's currently active locks."""
    before = active_restrictions_from_boards(
        "player", player_board, opponent_board,
        profiles=profiles, lock_state=lock_state,
        stadium_name=stadium_name, attack_windows=attack_windows,
    )
    resolution = execute_permissioned_paired_switch(
        ledger, player_board, opponent_board, turn_budget,
        program, metadata, source_instance_ids=source_instance_ids,
        opponent_promote_id=opponent_promote_id,
        own_promote_id=own_promote_id,
        active_restrictions=before,
    )
    if resolution is None:
        return None

    new_player = resolution.board_resolution.player_board
    new_opponent = resolution.board_resolution.opponent_board
    new_lock = advance_lock_state(
        lock_state, new_player, new_opponent, stadium_name=stadium_name
    )
    after = active_restrictions_from_boards(
        "player", new_player, new_opponent,
        profiles=profiles, lock_state=new_lock,
        stadium_name=stadium_name, attack_windows=attack_windows,
    )
    return LivePairedSwitchResolution(
        transaction=resolution,
        lock_state=new_lock,
        restrictions_before=before,
        restrictions_after=after,
    )
