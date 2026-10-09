"""Pokémon Ranger dual-cancellation and action contention under Dragon's Wish."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from energy_hand_attachment_events import (
    AttachmentChannel, EnergyAttachmentState, EnergyCard, attach_from_hand,
)
from hand_attachment_turn_end import (
    from_printed_attack, resolve_committed_hand_attachments,
)
from next_turn_attachment_window import NextTurnAttachmentWindow
from pokemon_ranger_attachment_projection import (
    play_ranger_attachment_projection,
    validate_printed_ranger,
)
from turn_action_budget import TurnAction, TurnActionBudget


def attach(state, wish, howled, card, target):
    committed = attach_from_hand(
        state, ((card, target),), player="A",
        channel=AttachmentChannel.MANUAL, manual_window=wish,
    )
    assert committed is not None
    return resolve_committed_hand_attachments(state, committed, howled).state


def main() -> None:
    validate_printed_ranger(ROOT / "resources")
    target = make_pokemon("target", "Target Active")
    pivot = make_pokemon("pivot", "Pivot Bench")
    board = make_board(target, (pivot,))
    source = EnergyAttachmentState(
        budget=TurnActionBudget(),
        hand=tuple(EnergyCard(f"fire-{i}", "Fire Energy") for i in range(1, 5)),
    )
    dragon_wish = NextTurnAttachmentWindow().queue_dragon_wish("A").on_turn_start("A")

    for source_id in ("sm11-167", "sv6pt5-17"):
        howl = from_printed_attack(
            ROOT / "resources", print_id=source_id, source_player="B",
            affected_player="A", target_board=board,
        ).begin_turn("A")
        assert dragon_wish.can_manually_attach("A", source.budget)

        # Ranger FIRST: the attack on A's Active no longer ends A's turn,
        # but Dragon's Wish is simultaneously cancelled. The ordinary
        # one-per-turn attachment remains, so only the first is available.
        first_ranger = play_ranger_attachment_projection(
            source, manual_permission=dragon_wish, reactive_window=howl
        )
        assert first_ranger is not None
        assert first_ranger.state.budget.supporter_plays_used == 1
        assert not first_ranger.manual_permission.active_for
        assert first_ranger.reactive_window.phase == "expired"
        a = attach(
            first_ranger.state, first_ranger.manual_permission,
            first_ranger.reactive_window, "fire-1", "target",
        )
        assert not a.budget.turn_ended
        assert a.budget.manual_energy_attachments_used == 1
        assert a.budget.can(TurnAction.ATTACK)
        assert attach_from_hand(
            a, (("fire-2", "pivot"),), player="A",
            channel=AttachmentChannel.MANUAL,
            manual_window=first_ranger.manual_permission,
        ) is None

        # Ranger AFTER two safe manual attachments can remove Lazy Howl,
        # yet the already-spent ordinary allowance is not restored.
        b = attach(source, dragon_wish, howl, "fire-1", "pivot")
        b = attach(b, dragon_wish, howl, "fire-2", "pivot")
        after_two = play_ranger_attachment_projection(
            b, manual_permission=dragon_wish, reactive_window=howl
        )
        assert after_two is not None
        assert after_two.state.budget.manual_energy_attachments_used == 2
        assert after_two.state.budget.can(TurnAction.ATTACK)
        assert attach_from_hand(
            after_two.state, (("fire-3", "target"),),
            player="A", channel=AttachmentChannel.MANUAL,
            manual_window=after_two.manual_permission,
        ) is None
        assert len(after_two.state.attached) == 2

        # Without Ranger, triggering an attachment to the attacked target
        # itself closes the current turn despite any remaining grant.
        without = attach(source, dragon_wish, howl, "fire-1", "target")
        assert without.budget.turn_ended
        assert not without.budget.can(TurnAction.ATTACK)

        # Playing any other Supporter first ordinarily excludes Ranger.
        spent = source.budget.consume(TurnAction.SUPPORTER)
        assert spent is not None
        blocked = play_ranger_attachment_projection(
            replace(source, budget=spent),
            manual_permission=dragon_wish, reactive_window=howl,
        )
        assert blocked is None

        # Dynamic Dual-Brains-like quota allows the second Supporter and
        # preserves both attachment and Supporter usage histories.
        dual = replace(source, budget=spent.with_limit(TurnAction.SUPPORTER, 2))
        allowed_dual = play_ranger_attachment_projection(
            dual, manual_permission=dragon_wish, reactive_window=howl
        )
        assert allowed_dual is not None
        assert allowed_dual.state.budget.supporter_plays_used == 2

        # Neither available grant nor reactive attack effect => no change
        # to the modeled local game state, so the Supporter isn't playable.
        no_effect = play_ranger_attachment_projection(
            source,
            manual_permission=dragon_wish.remove_attack_effects(),
            reactive_window=howl.remove_attack_effects(),
        )
        assert no_effect is None
        print(source_id, "Ranger tradeoff: PASS")

    print("pokemon_ranger_attachment_projection regression: PASS")
    print("Ranger-first frees target but loses extra manual attachments")
    print("Ranger-late preserves existing attachments but cannot refund quota")


if __name__ == "__main__":
    main()
