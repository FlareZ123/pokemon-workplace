"""Rule-text and schedule regression for Dragon's Wish attachment permission."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality
from canonical_turn_sequence_owner import (
    TurnScheduleState,
    advance_turn,
    close_turn_voluntarily,
    close_turn_with_attack,
)
from next_turn_attachment_window import NextTurnAttachmentWindow
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import make_state


def card(print_id: str) -> dict:
    set_id = print_id.split("-", 1)[0]
    records = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(record for record in records if record["id"] == print_id)


def main() -> None:
    dragonair = card("sm1-95")
    magnezone = card("bw8-46")
    surge = (card("sm10-178"), card("sm115-60"))
    ranger = card("xy11-104")
    emboar = card("bw1-20")

    assert classify_effective_legality(dragonair)[0] == "Legal"
    assert classify_effective_legality(magnezone)[0] == "Legal"
    assert all(classify_effective_legality(c)[0] == "Banned" for c in surge)
    assert next(
        a["text"] for a in dragonair["attacks"] if a["name"] == "Dragon's Wish"
    ) == (
        "During your next turn, you may attach any number of Energy cards "
        "from your hand to your Pokémon."
    )
    assert magnezone["abilities"][0]["text"] == (
        "During your turn, you may play 2 Supporter cards."
    )
    assert "Remove all effects of attacks on each player" in ranger["rules"][0]
    assert emboar["abilities"][0]["name"] == "Inferno Fandango"

    base = TurnActionBudget()
    ordinary_first = base.consume(TurnAction.MANUAL_ENERGY_ATTACHMENT)
    assert ordinary_first is not None
    assert ordinary_first.consume(TurnAction.MANUAL_ENERGY_ATTACHMENT) is None

    a = make_state({}, turn_budget=base)
    b = make_state({}, turn_budget=base)
    original_schedule = TurnScheduleState("A", "B")
    window = NextTurnAttachmentWindow().queue_dragon_wish("A")
    assert "A" not in window.active_for
    assert not window.can_manually_attach("A", ordinary_first)

    # A attacks with Dragon's Wish, then B takes an extra turn. The
    # permission remains pending until A really begins their next turn.
    end_a = close_turn_with_attack(original_schedule, a)
    assert end_a is not None
    to_b = advance_turn(end_a[0], end_a[1], b)
    assert to_b is not None
    window = window.on_turn_start(to_b.schedule.current_player)
    assert window.pending_for == frozenset({"A"})
    assert not window.active_for

    end_b = close_turn_with_attack(
        to_b.schedule,
        to_b.current_state,
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )
    assert end_b is not None
    extra_b = advance_turn(end_b[0], end_b[1], to_b.other_state)
    assert extra_b is not None
    window = window.on_turn_start(extra_b.schedule.current_player)
    assert window.pending_for == frozenset({"A"})
    assert not window.active_for

    end_b_extra = close_turn_voluntarily(extra_b.schedule, extra_b.current_state)
    assert end_b_extra is not None
    back_to_a = advance_turn(end_b_extra[0], end_b_extra[1], extra_b.other_state)
    assert back_to_a is not None
    assert back_to_a.schedule.current_player == "A"
    window = window.on_turn_start(back_to_a.schedule.current_player)
    assert window.pending_for == frozenset()
    assert window.active_for == frozenset({"A"})

    assert back_to_a.current_state.turn_budget is not None
    budget = back_to_a.current_state.turn_budget
    for expected in (1, 2, 3):
        assert window.can_manually_attach("A", budget)
        next_budget = window.consume_manual_attachment("A", budget)
        assert next_budget is not None
        budget = next_budget
        assert budget.manual_energy_attachments_used == expected

    assert budget.manual_energy_attachment_limit == 1
    assert not budget.can(TurnAction.MANUAL_ENERGY_ATTACHMENT)
    assert window.can_manually_attach("A", budget)
    assert not window.can_manually_attach("B", budget)

    # Removing an attack effect leaves physical attachment history intact.
    cancelled = window.remove_attack_effects()
    assert not cancelled.can_manually_attach("A", budget)
    assert cancelled.consume_manual_attachment("A", budget) is None
    assert cancelled.can_manually_attach("A", base)
    once_after_removal = cancelled.consume_manual_attachment("A", base)
    assert once_after_removal is not None
    assert once_after_removal.manual_energy_attachments_used == 1

    # A fresh Dragon's Wish while the previous effect is active renews
    # the window on A's following turn, without licensing post-attack plays.
    renewed = window.queue_dragon_wish("A")
    closed = budget.consume(TurnAction.ATTACK)
    assert closed is not None
    assert renewed.consume_manual_attachment("A", closed) is None
    renewed = renewed.on_turn_start("B")
    assert not renewed.active_for and renewed.pending_for == {"A"}
    renewed = renewed.on_turn_start("A")
    assert renewed.active_for == {"A"}
    assert renewed.can_manually_attach("A", base)

    # Ability-based attachments (e.g. Inferno Fandango) are separate
    # effect actions. The generic manual-attachment quota is unchanged
    # by resolving one of them.
    assert base.manual_energy_attachments_used == 0

    print("next_turn_attachment_window regression: PASS")
    print("3 manual attachments tracked under 1 ordinary quota with temporary permission")
    print("opponent extra-turn deferral, removal, renewal, and turn close: PASS")


if __name__ == "__main__":
    main()
