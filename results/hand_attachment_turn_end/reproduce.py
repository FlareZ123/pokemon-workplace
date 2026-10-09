"""End-turn attachment reaction that can curtail Dragon's Wish."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import evolve, make_board, make_pokemon, switch_active
from energy_hand_attachment_events import (
    AttachmentChannel, EnergyAttachmentState, EnergyCard, attach_from_hand,
    hand_attachment_events,
)
from hand_attachment_turn_end import (
    from_printed_attack, resolve_committed_hand_attachments,
)
from next_turn_attachment_window import NextTurnAttachmentWindow
from turn_action_budget import TurnAction, TurnActionBudget

ENERGY = tuple(EnergyCard(f"fire-{i}", "Fire Energy") for i in range(1, 5))


def attach(
    state: EnergyAttachmentState,
    window,
    wish: NextTurnAttachmentWindow,
    card: str,
    target: str,
    *,
    channel: AttachmentChannel = AttachmentChannel.MANUAL,
):
    committed = attach_from_hand(
        state, ((card, target),), player="A", channel=channel,
        manual_window=wish,
    )
    assert committed is not None
    return resolve_committed_hand_attachments(state, committed, window)


def main() -> None:
    target = make_pokemon("target", "Target Active", tags=("Basic",))
    pivot = make_pokemon("pivot", "Pivot Bench", tags=("Basic",))
    board = make_board(target, (pivot,))
    base = EnergyAttachmentState(TurnActionBudget(), hand=ENERGY)
    wish = NextTurnAttachmentWindow().queue_dragon_wish("A")
    assert "A" in wish.pending_for and not wish.active_for

    for source_id in ("sm11-167", "sv6pt5-17"):
        reaction = from_printed_attack(
            ROOT / "resources", print_id=source_id,
            source_player="B", affected_player="A", target_board=board,
        )

        # A previous turn Dragon's Wish grant is pending. The attack on B's
        # turn creates a pending Lazy Howl/Daydream reaction. Both activate A.
        wish_live = wish.on_turn_start("B").on_turn_start("A")
        reaction_live = reaction.begin_turn("A")
        assert reaction_live.phase == "active"
        assert wish_live.active_for == frozenset({"A"})

        # A can avoid the trapped Defending Pokemon and manually attach to
        # a different target repeatedly before choosing whether to trigger.
        current = base
        for i in (1, 2):
            outcome = attach(current, reaction_live, wish_live, f"fire-{i}", "pivot")
            assert not outcome.ended_by_attachment
            current = outcome.state
            assert not current.budget.turn_ended
        hit = attach(current, reaction_live, wish_live, "fire-3", "target")
        assert hit.ended_by_attachment
        assert hit.trigger is not None and hit.trigger.copy_id == "fire-3"
        assert hit.state.budget.turn_ended
        assert hit.state.budget.manual_energy_attachments_used == 3
        assert len(hit.state.attached) == 3
        assert len(hand_attachment_events(hit.state, player="A")) == 3
        assert attach_from_hand(
            hit.state, (("fire-4", "pivot"),), player="A",
            channel=AttachmentChannel.MANUAL, manual_window=wish_live,
        ) is None

        # If the first attachment touches the Defending target, Dragon's
        # Wish gains zero additional opportunities on that turn.
        first = attach(base, reaction_live, wish_live, "fire-1", "target")
        assert first.ended_by_attachment
        assert first.state.budget.manual_energy_attachments_used == 1
        assert len(first.state.hand) == 3

        # The trigger tests hand provenance, not the manual channel: a
        # one-card Ability-effect attachment from hand also closes the turn.
        effect = attach(
            base, reaction_live, wish_live, "fire-1", "target",
            channel=AttachmentChannel.EFFECT,
        )
        assert effect.ended_by_attachment
        assert effect.state.budget.manual_energy_attachments_used == 0
        assert effect.state.budget.turn_ended

        # Other players cannot activate A's target-bound effect.
        from_b = attach_from_hand(
            base, (("fire-1", "target"),), player="B",
            channel=AttachmentChannel.MANUAL,
        )
        assert from_b is not None
        ignored = resolve_committed_hand_attachments(
            base, from_b, reaction_live
        )
        assert not ignored.ended_by_attachment

        # Pokémon Ranger-like removal of attack effects cancels the
        # reactive turn ending; Dragon's Wish grant can remain active if
        # it is not itself removed in this isolated test.
        cancelled = reaction_live.remove_attack_effects()
        free = attach(base, cancelled, wish_live, "fire-1", "target")
        assert not free.ended_by_attachment
        assert free.state.budget.manual_energy_attachments_used == 1

        # Switching or evolving the original Defending Pokémon makes the
        # attack-applied effect stop following that Pokémon.
        shifted = switch_active(board, "pivot")
        assert shifted is not None
        switched = reaction_live.advance_target_binding(board, shifted)
        assert not switched.target_effect_live
        switched_play = attach(base, switched, wish_live, "fire-1", "target")
        assert not switched_play.ended_by_attachment

        evolved_board = evolve(board, "target", new_card_name="Target Stage1")
        assert evolved_board is not None
        evolved_window = reaction_live.advance_target_binding(board, evolved_board)
        assert not evolved_window.target_effect_live

        assert reaction_live.end_turn("A").phase == "expired"
        after_turn = reaction_live.end_turn("A")
        next_state = replace(base, budget=base.budget)
        post = attach(next_state, after_turn, wish_live, "fire-1", "target")
        assert not post.ended_by_attachment

        # Journal extension must be monotone; old event replay cannot
        # re-trigger a later independent action.
        harmless = resolve_committed_hand_attachments(
            hit.state, hit.state, reaction_live
        )
        assert not harmless.ended_by_attachment
        try:
            resolve_committed_hand_attachments(hit.state, base, reaction_live)
        except ValueError:
            pass
        else:
            raise AssertionError("non-prefix event journal was silently accepted")

        print(source_id, "reaction with Dragon's Wish: PASS")

    print("hand_attachment_turn_end regression: PASS")
    print("turn-ending events trump remaining grant, source/target timing validated")


if __name__ == "__main__":
    main()
