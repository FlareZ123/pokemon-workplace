"""Reproduce Raihan temporal KO gate with Timeless-GX's extra turn."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from canonical_turn_sequence_owner import (  # noqa: E402
    TurnScheduleState, advance_turn, close_turn_with_attack
)
from last_opponent_turn_knockout_gate import LastOpponentTurnKO  # noqa: E402
from regidrago_post_trifrost_recharge import (  # noqa: E402
    RechargeState, find_recharge_routes
)
from turn_action_budget import TurnActionBudget  # noqa: E402
from unified_state_kernel import make_state  # noqa: E402


def card(set_id: str, ident: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == ident)


def play_timeless_then_bonus(
    first_ko_victims: frozenset[str],
    second_ko_victims: frozenset[str],
) -> tuple[bool, LastOpponentTurnKO]:
    # P1 = Shadow Rider player, P2 = Regidrago.
    history = LastOpponentTurnKO()
    schedule = TurnScheduleState("P1", "P2")
    p1 = make_state({}, turn_budget=TurnActionBudget())
    p2 = make_state({}, turn_budget=TurnActionBudget())
    first = close_turn_with_attack(
        schedule, p1,
        take_another_turn=True, skip_pokemon_checkup=True,
    )
    assert first is not None
    history = history.complete_turn("P1", first_ko_victims)
    next_turn = advance_turn(first[0], first[1], p2)
    assert next_turn is not None
    assert next_turn.same_player_continues
    assert next_turn.schedule.current_player == "P1"
    assert not next_turn.pokemon_checkup_occurs

    second = close_turn_with_attack(
        next_turn.schedule, next_turn.current_state,
        take_another_turn=False
    )
    assert second is not None
    history = history.complete_turn("P1", second_ko_victims)
    final = advance_turn(second[0], second[1], next_turn.other_state)
    assert final is not None
    assert final.schedule.current_player == "P2"
    assert not final.same_player_continues
    assert final.pokemon_checkup_occurs
    assert history.last_opponent_turn_index("P1") == 2
    return history.raihan_eligible("P2", "P1"), history


def main() -> None:
    raihan = card("swsh7", "swsh7-152")
    dialga = card("sm5", "sm5-100")
    assert "during your opponent's last turn" in raihan["rules"][0]
    timeless = next(a for a in dialga["attacks"] if a["name"] == "Timeless-GX")
    assert "Take another turn after this one" in timeless["text"]
    assert "Skip the between-turns step" in timeless["text"]

    first_only, history = play_timeless_then_bonus(
        frozenset({"P2"}), frozenset()
    )
    assert not first_only
    assert history.next_turn_number == 3

    bonus_only, _ = play_timeless_then_bonus(
        frozenset(), frozenset({"P2"})
    )
    assert bonus_only
    both, _ = play_timeless_then_bonus(
        frozenset({"P2"}), frozenset({"P2"})
    )
    assert both
    none, _ = play_timeless_then_bonus(frozenset(), frozenset())
    assert not none
    own_ko, _ = play_timeless_then_bonus(
        frozenset({"P1"}), frozenset({"P1"})
    )
    assert not own_ko

    # Compare the same physical Regidrago recharge inventory with and
    # without a KO *during the last opponent turn*.
    possible = RechargeState(
        crispin_access=False, raihan_access=True,
        double_dragon_deck=1, grass_discard=1,
        knockout_last_opponent_turn=bonus_only
    )
    assert {r.label for r in find_recharge_routes(possible)} == {
        "Raihan + searched Double Dragon Energy"
    }
    impossible = replace(possible, knockout_last_opponent_turn=first_only)
    assert find_recharge_routes(impossible) == ()

    print(json.dumps({
        "first_turn_KO_only_raihan_eligible": first_only,
        "bonus_turn_KO_only_raihan_eligible": bonus_only,
        "both_turns_KO_raihan_eligible": both,
        "neither_turn_KO_raihan_eligible": none,
        "only_own_side_KO_raihan_eligible": own_ko,
        "bonus_turn_recharge_available": True,
        "first_turn_only_recharge_available": False,
    }, indent=2))


if __name__ == "__main__":
    main()
