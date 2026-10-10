"""Card-text grounded regression for the post-Trifrost Mimikyu recovery planner."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from shadow_rider_post_trifrost_recovery import (  # noqa: E402
    RecoveryScenario, find_recovery
)


def card(set_id: str, ident: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == ident)


def main() -> None:
    mimikyu = card("sm2", "sm2-58")
    tulip = card("sv4", "sv4-181")
    stretcher = card("sv6pt5", "sv6pt5-61")
    stone = card("xy8", "xy8-137")
    acerola = card("sm3", "sm3-112")
    guzma = card("sm3", "sm3-115")
    rider = card("swsh6", "swsh6-75")
    valley = card("xy4", "xy4-93")
    latias = card("sv8", "sv8-76")

    assert mimikyu["hp"] == "70"
    assert next(a for a in mimikyu["attacks"] if a["name"] == "Copycat")["cost"] == ["Psychic", "Colorless"]
    assert tulip["subtypes"] == ["Supporter"]
    assert "up to 4 in any combination" in tulip["rules"][0]
    assert stretcher["subtypes"] == ["Item"]
    assert "Pokémon or a Basic Energy" in stretcher["rules"][0]
    assert stone["subtypes"] == ["Pokémon Tool"]
    assert "has no Retreat Cost" in stone["rules"][1]
    assert acerola["subtypes"] == ["Supporter"]
    assert "has any damage counters" in acerola["rules"][0]
    assert guzma["subtypes"] == ["Supporter"]
    assert "If you do, switch your Active" in guzma["rules"][0]
    assert "Benched Psychic Pokémon" in rider["abilities"][0]["text"]
    assert "cost Colorless less" in valley["rules"][0]
    assert "Basic Pokémon in play have no Retreat Cost" in latias["abilities"][0]["text"]

    baseline = RecoveryScenario()
    tulip_stone = find_recovery(baseline)
    assert tulip_stone is not None
    assert tulip_stone.finish.zone == "active"
    assert tulip_stone.finish.attached_energy == 2
    assert any(a.startswith("Tulip:") for a in tulip_stone.actions)
    assert any(a.startswith("Underworld Door:") for a in tulip_stone.actions)
    assert "Manual Psychic attachment to Mimikyu" in tulip_stone.actions
    assert "Free retreat using Float Stone; promote Mimikyu" in tulip_stone.actions
    assert not any(a.startswith("Guzma:") or a.startswith("Acerola:") for a in tulip_stone.actions)

    locked_items = find_recovery(replace(baseline, item_play_enabled=False))
    assert locked_items is not None
    assert "Free retreat using Float Stone; promote Mimikyu" in locked_items.actions

    no_promotion = find_recovery(replace(
        baseline, float_stone_available=False, guzma_available=False,
        acerola_available=False
    ))
    assert no_promotion is None
    no_energy = find_recovery(replace(
        baseline, underworld_door_enabled=False
    ))
    assert no_energy is None
    valley_saves_one = find_recovery(replace(
        baseline, underworld_door_enabled=False, dimension_valley=True
    ))
    assert valley_saves_one is not None
    assert valley_saves_one.finish.attached_energy == 1

    # When Item is available and energy already in hand, Night Stretcher
    # recovers Mimikyu while Acerola removes damaged Active VMAX.
    acerola_case = replace(
        baseline, psychic_in_hand=2, psychic_in_discard=0,
        tulip_available=False, guzma_available=False,
        float_stone_available=False, opponent_has_bench=False
    )
    acerola_line = find_recovery(acerola_case)
    assert acerola_line is not None
    assert "Night Stretcher: Mimikyu to hand" in acerola_line.actions
    assert "Acerola: pick up damaged incumbent; promote Mimikyu" in acerola_line.actions
    assert find_recovery(replace(acerola_case, active_damaged=False)) is None

    guzma_case = replace(
        acerola_case, guzma_available=True, acerola_available=False
    )
    assert find_recovery(guzma_case) is None
    guzma_line = find_recovery(replace(guzma_case, opponent_has_bench=True))
    assert guzma_line is not None
    assert "Guzma: opponent switch then promote Mimikyu" in guzma_line.actions

    # Tulip cannot be played after the Supporter quota is already spent;
    # Night Stretcher alone cannot return Mimikyu plus two discarded Energy.
    assert find_recovery(replace(
        baseline, supporter_spent=True
    )) is None
    assert find_recovery(replace(
        baseline, gx_spent=True
    )) is None
    assert find_recovery(replace(
        baseline, apex_exposed=False
    )) is None
    assert find_recovery(replace(
        baseline, dialga_in_discard=False
    )) is None

    print(json.dumps({
        "baseline_tulip_float_stone": list(tulip_stone.actions),
        "item_locked_tulip_float_stone": list(locked_items.actions),
        "dimension_valley_one_energy": list(valley_saves_one.actions),
        "night_stretcher_acerola": list(acerola_line.actions),
        "night_stretcher_guzma": list(guzma_line.actions),
        "all_negative_guards_passed": True
    }, indent=2))


if __name__ == "__main__":
    main()
