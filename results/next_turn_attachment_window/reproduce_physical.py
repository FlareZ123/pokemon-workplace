"""Physical Dragon's Wish attachments with typed target-aware lock gating."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import initialize_snapshot_lock_state
from attack_restriction_turn_windows import create_attack_restriction_window
from attack_source_scoped_restrictions import materialize_attack_restriction
from board_object_kernel import make_board, make_pokemon
from card_action_metadata import CardActionMetadata
from energy_hand_attachment_events import (
    AttachmentChannel,
    EnergyAttachmentState,
    EnergyCard,
    attach_from_hand,
    hand_attachment_events,
)
from lock_gated_energy_attachment import execute_lock_gated_manual_energy_attachment
from next_turn_attachment_window import NextTurnAttachmentWindow
from source_scoped_restriction_activation import build_restriction_activation_profiles
from target_bound_attack_restrictions import (
    begin_target_bound_turn,
    bind_defending_pokemon_window,
)
from turn_action_budget import TurnActionBudget


def main() -> None:
    energy = tuple(EnergyCard(f"fire-{i}", "Fire Energy") for i in range(1, 5))
    state = EnergyAttachmentState(budget=TurnActionBudget(), hand=energy)
    metadata = CardActionMetadata("sm1-165", "Fire Energy", "basic_energy", frozenset())

    a_board = make_board(
        make_pokemon("target", "Target Basic", tags=("Basic",)),
        (make_pokemon("pivot", "Pivot Basic", tags=("Basic",)),),
    )
    b_board = make_board(make_pokemon("opponent", "Opponent Basic"))
    lock_state = initialize_snapshot_lock_state(a_board, b_board)
    assert lock_state.resolved

    profiles = build_restriction_activation_profiles(ROOT / "resources")
    cross = [
        profile
        for profile in profiles
        if profile.restriction.card_id == "xyp-XY75"
        and ("Cross Slicer" in profile.restriction.source
             or "Cross Slicer" in profile.restriction.text)
    ]
    assert len(cross) == 1
    restriction = materialize_attack_restriction(cross[0])
    assert restriction is not None
    pending = create_attack_restriction_window(
        cross[0], restriction, source_player="B", other_player="A"
    )
    bound = begin_target_bound_turn(
        bind_defending_pokemon_window(pending, a_board), "A"
    )

    permission = (
        NextTurnAttachmentWindow()
        .queue_dragon_wish("A")
        .on_turn_start("A")
    )
    context = {
        "actor": "A",
        "player_board": a_board,
        "opponent_board": b_board,
        "profiles": profiles,
        "lock_state": lock_state,
        "action_metadata": metadata,
        "player_id": "A",
        "opponent_id": "B",
        "target_bound_attack_windows": (bound,),
        "manual_window": permission,
    }

    # Negative restriction wins over a positive "any number" grant.
    denied = execute_lock_gated_manual_energy_attachment(
        state, copy_id="fire-1", target_object_id="target", **context
    )
    assert not denied.permission.allowed
    assert denied.attachment_state is None
    assert state.budget.manual_energy_attachments_used == 0
    assert len(state.hand) == 4

    current = state
    for count in (1, 2, 3):
        played = execute_lock_gated_manual_energy_attachment(
            current, copy_id=f"fire-{count}",
            target_object_id="pivot", **context
        )
        assert played.permission.allowed
        assert played.attachment_state is not None
        current = played.attachment_state
        assert current.budget.manual_energy_attachments_used == count
        assert len(current.attached) == count
        assert len(hand_attachment_events(current, player="A")) == count
    assert current.budget.manual_energy_attachment_limit == 1

    # Removing the attack effect stops further ordinary attachments without
    # rolling back the three physical attachments or their historical quota.
    removed_context = {**context, "manual_window": permission.remove_attack_effects()}
    after_removal = execute_lock_gated_manual_energy_attachment(
        current, copy_id="fire-4", target_object_id="pivot", **removed_context
    )
    assert after_removal.permission.allowed
    assert after_removal.attachment_state is None
    assert len(current.hand) == 1

    # Backward-compatible callers still get exactly one manual attachment.
    no_grant = {**context, "manual_window": None}
    first = execute_lock_gated_manual_energy_attachment(
        state, copy_id="fire-1", target_object_id="pivot", **no_grant
    )
    assert first.attachment_state is not None
    second = execute_lock_gated_manual_energy_attachment(
        first.attachment_state, copy_id="fire-2",
        target_object_id="pivot", **no_grant
    )
    assert second.permission.allowed and second.attachment_state is None

    # Immediate effect-based Energy attachment remains separate from the
    # ordinary manual quota, even with the new optional gateway available.
    effect = attach_from_hand(
        state, (("fire-1", "pivot"), ("fire-2", "pivot")),
        player="A", channel=AttachmentChannel.EFFECT,
        manual_window=permission,
    )
    assert effect is not None
    assert effect.budget.manual_energy_attachments_used == 0
    assert len(hand_attachment_events(effect)) == 2

    ended = replace(state, budget=replace(state.budget, turn_ended=True))
    after_end = execute_lock_gated_manual_energy_attachment(
        ended, copy_id="fire-1", target_object_id="pivot", **context
    )
    assert after_end.permission.allowed and after_end.attachment_state is None

    print("next_turn_attachment_window physical integration: PASS")
    print("3 conserving manual attachments, 3 hand events, 1 ordinary quota")
    print("Cross Slicer denial, Ranger removal, legacy, effect, turn end: PASS")


if __name__ == "__main__":
    main()
