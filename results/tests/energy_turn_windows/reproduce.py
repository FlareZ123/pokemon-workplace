"""SFT: first-turn Energy search and attack timing for paper Expanded."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from energy_turn_windows import (
    TimedEnergyState,
    advance_own_turn,
    earliest_dragon_claw_setup,
    earliest_volt_cyclone_setup,
    initial_timed_state,
)
from turn_action_budget import TurnActionBudget
from typed_energy_access import Zone, make_state


def thorns(**flags: object):
    return make_state({
        "Iron Thorns ex": Zone.ACTIVE.value,
        "Tag Call": Zone.HAND.value,
        "Guzma & Hala": Zone.DECK.value,
        "Thunder Mountain Prism Star": Zone.DECK.value,
        "Double Colorless Energy": Zone.DECK.value,
        "Fodder A": Zone.HAND.value,
        "Fodder B": Zone.HAND.value,
    }, **flags)


def bagon(**flags: object):
    return make_state({
        "Bagon": Zone.ACTIVE.value,
        "Crispin": Zone.HAND.value,
        "Fire Energy": Zone.DECK.value,
        "Water Energy": Zone.DECK.value,
    }, **flags)


def main() -> None:
    second = earliest_volt_cyclone_setup(
        initial_timed_state(thorns(), went_first=False), max_own_turns=1
    )
    assert second is not None and second.earliest_own_turn == 1
    assert len(second.actions) == 4

    first = initial_timed_state(thorns(), went_first=True)
    assert earliest_volt_cyclone_setup(first, max_own_turns=1) is None
    first_result = earliest_volt_cyclone_setup(first, max_own_turns=2)
    assert first_result is not None and first_result.earliest_own_turn == 2
    assert len(first_result.actions) == 5

    attack_exception = initial_timed_state(
        thorns(), went_first=True, first_turn_attack_exception=True
    )
    assert earliest_volt_cyclone_setup(attack_exception, max_own_turns=1) is None
    double_exception = initial_timed_state(
        thorns(), went_first=True,
        first_turn_attack_exception=True,
        first_turn_supporter_exception=True,
    )
    assert earliest_volt_cyclone_setup(double_exception, max_own_turns=1)

    for flag in ("supporter_used", "manual_attachment_used"):
        spent = initial_timed_state(thorns(**{flag: True}), went_first=False)
        assert earliest_volt_cyclone_setup(spent, max_own_turns=1) is None
        resumed = earliest_volt_cyclone_setup(spent, max_own_turns=2)
        assert resumed is not None and resumed.earliest_own_turn == 2

    locked = initial_timed_state(
        thorns(supporters_allowed=False), went_first=False
    )
    assert earliest_volt_cyclone_setup(locked, max_own_turns=3) is None

    dragon_second = earliest_dragon_claw_setup(
        initial_timed_state(bagon(), went_first=False), max_own_turns=1
    )
    assert dragon_second is not None and dragon_second.earliest_own_turn == 1
    assert len(dragon_second.actions) == 2

    dragon_first = initial_timed_state(bagon(), went_first=True)
    assert earliest_dragon_claw_setup(dragon_first, max_own_turns=1) is None
    dragon_next = earliest_dragon_claw_setup(dragon_first, max_own_turns=2)
    assert dragon_next is not None and dragon_next.earliest_own_turn == 2
    assert len(dragon_next.actions) == 3
    assert sorted(dragon_next.final_state.access.attached_units) == ["R", "W"]

    retained = advance_own_turn(dragon_second.final_state)
    assert retained.own_turn == 2
    assert not retained.budget.supporter_used
    assert not retained.budget.manual_energy_attachment_used
    assert retained.access.attached_units == dragon_second.final_state.access.attached_units
    assert retained.access.locations == dragon_second.final_state.access.locations

    already_ready = make_state(
        {"Iron Thorns ex": Zone.ACTIVE.value},
        attached_units=("L", "C", "C"),
    )
    blocked_ready = initial_timed_state(already_ready, went_first=True)
    assert earliest_volt_cyclone_setup(blocked_ready, max_own_turns=1) is None
    resumed_ready = earliest_volt_cyclone_setup(blocked_ready, max_own_turns=2)
    assert resumed_ready is not None
    assert resumed_ready.actions == (
        "End own turn; opponent turn assumed inert",
    )

    try:
        TimedEnergyState(
            access=thorns(), budget=TurnActionBudget(supporter_used=True),
            own_turn=1, went_first=False,
        )
    except ValueError as exc:
        assert "disagree" in str(exc)
    else:
        raise AssertionError("mismatched canonical quota was accepted")

    print(json.dumps({
        "thorns_second": {"turn": second.earliest_own_turn, "line": second.actions},
        "thorns_first": {"turn": first_result.earliest_own_turn, "line": first_result.actions},
        "bagon_second": {"turn": dragon_second.earliest_own_turn, "line": dragon_second.actions},
        "bagon_first": {"turn": dragon_next.earliest_own_turn, "line": dragon_next.actions},
        "scope": "known zones and inert opponent, not a win-rate estimate",
    }, indent=2))


if __name__ == "__main__":
    main()
