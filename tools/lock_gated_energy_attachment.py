"""Gate manual Energy-from-hand events with live source-scoped restrictions."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from ability_lock_causal_state import AbilityLockCausalState
from attack_restriction_turn_windows import AttackRestrictionWindow
from board_derived_action_permissions import (
    BoardDerivedActionPermission,
    evaluate_board_derived_action_permission,
)
from board_object_kernel import BoardState
from card_action_metadata import CardActionMetadata
from energy_hand_attachment_events import (
    AttachmentChannel,
    EnergyAttachmentState,
    attach_from_hand,
)
from source_scoped_restriction_activation import RestrictionActivationProfile
from target_bound_attack_restrictions import TargetBoundAttackRestrictionWindow


@dataclass(frozen=True)
class LockGatedEnergyAttachmentResult:
    permission: BoardDerivedActionPermission
    attachment_state: EnergyAttachmentState | None


def execute_lock_gated_manual_energy_attachment(
    state: EnergyAttachmentState,
    *,
    copy_id: str,
    target_object_id: str,
    actor: str,
    player_board: BoardState,
    opponent_board: BoardState,
    profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    action_metadata: CardActionMetadata,
    stadium_name: str | None = None,
    player_id: str = "player",
    opponent_id: str = "opponent",
    attack_windows: Sequence[AttackRestrictionWindow] = (),
    target_bound_attack_windows: Sequence[TargetBoundAttackRestrictionWindow] = (),
) -> LockGatedEnergyAttachmentResult:
    """Attempt one normal once-per-turn Energy attachment from hand."""

    if action_metadata.card_kind not in {"basic_energy", "special_energy"}:
        raise ValueError("action metadata must describe an Energy card")

    matches = tuple(card for card in state.hand if card.copy_id == copy_id)
    if len(matches) != 1:
        raise ValueError("selected Energy copy is not uniquely present in hand")
    if matches[0].name != action_metadata.name:
        raise ValueError("selected Energy copy does not match action metadata")

    permission = evaluate_board_derived_action_permission(
        action_metadata.attempt("hand", mode="attach"),
        player=actor,
        player_board=player_board,
        opponent_board=opponent_board,
        profiles=profiles,
        lock_state=lock_state,
        stadium_name=stadium_name,
        player_id=player_id,
        opponent_id=opponent_id,
        attack_windows=attack_windows,
        target_bound_attack_windows=target_bound_attack_windows,
        target_object_id=target_object_id,
    )
    if not permission.allowed:
        return LockGatedEnergyAttachmentResult(permission, None)

    next_state = attach_from_hand(
        state,
        ((copy_id, target_object_id),),
        player=actor,
        channel=AttachmentChannel.MANUAL,
    )
    return LockGatedEnergyAttachmentResult(permission, next_state)
