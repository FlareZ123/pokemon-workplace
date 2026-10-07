from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_body_effect_kernel import (
    AddDamageCounters,
    DiscardAllEnergyOfType,
    DiscardOneEnergyOfType,
    EffectState,
    IfDid,
    execute_program,
)
from board_object_kernel import EnergyAttachment, make_board, make_pokemon


def make_state(*energy: EnergyAttachment) -> EffectState:
    actor = make_pokemon(
        "p1-copying",
        "Zoroark",
        energy=tuple(energy),
    )
    opponent_active = make_pokemon("p2-active", "Active Target")
    opponent_bench = make_pokemon("p2-bench", "Bench Target")
    return EffectState(
        actor_board=make_board(actor),
        opponent_board=make_board(opponent_active, (opponent_bench,)),
    )


CRIMSON_BLASTER = (
    DiscardAllEnergyOfType("R"),
    AddDamageCounters("p2-bench", 18),
)


def test_crimson_blaster_continues_when_discard_changes_nothing() -> None:
    result = execute_program(make_state(), CRIMSON_BLASTER)
    assert result.discarded_energy == ()
    assert result.opponent_board.get("p2-bench").damage_counters == 18
    assert result.events == ("add_18_damage_counters",)


def test_all_type_energy_counts_as_fire_for_discard() -> None:
    prism = EnergyAttachment("energy-prism", "Prism-like Energy", ("*",))
    result = execute_program(make_state(prism), CRIMSON_BLASTER)
    assert [card.instance_id for card in result.discarded_energy] == [
        "energy-prism"
    ]
    assert result.actor_board.get("p1-copying").energy == ()
    assert result.opponent_board.get("p2-bench").damage_counters == 18


def test_if_did_dependency_suppresses_consequent() -> None:
    dependent = (
        IfDid(
            DiscardOneEnergyOfType("R"),
            (AddDamageCounters("p2-bench", 18),),
        ),
    )
    without_fire = execute_program(make_state(), dependent)
    assert without_fire.opponent_board.get("p2-bench").damage_counters == 0

    fire = EnergyAttachment("energy-fire", "Fire Energy", ("R",))
    with_fire = execute_program(make_state(fire), dependent)
    assert with_fire.opponent_board.get("p2-bench").damage_counters == 18
    assert [card.instance_id for card in with_fire.discarded_energy] == [
        "energy-fire"
    ]


def main() -> None:
    test_crimson_blaster_continues_when_discard_changes_nothing()
    test_all_type_energy_counts_as_fire_for_discard()
    test_if_did_dependency_suppresses_consequent()
    print("attack-body best-effort semantics regression: PASS")


if __name__ == "__main__":
    main()
