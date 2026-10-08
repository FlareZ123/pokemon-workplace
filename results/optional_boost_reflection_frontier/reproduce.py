"""Reproduce all fixed optional-boost self-KO frontiers vs Strong Bash."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from optional_boost_reflection_frontier import scan_retaliation_frontier


def main() -> None:
    result = scan_retaliation_frontier(
        ROOT / "resources",
        defender_print_id="sv10-146",
    )
    assert result["defender_hp"] == 130
    assert result["legal_optional_fixed_boost_prints"] == 61
    assert result["frontier_signatures"] == 2
    assert result["frontier_prints"] == 4

    by_name = {row["card_name"]: row for row in result["frontiers"]}
    assert set(by_name) == {"Cetitan ex", "M Houndoom-EX"}

    cetitan = by_name["Cetitan ex"]
    assert cetitan["attack_name"] == "Crushing Press"
    assert cetitan["hp"] == 300
    assert (cetitan["base_final_damage"], cetitan["boosted_final_damage"]) == (
        140, 280,
    )
    assert cetitan["dangerous_prior_damage"] == tuple(range(20, 160, 10))
    assert set(cetitan["print_ids"]) == {"sv10-65", "sv10-210"}

    houndoom = by_name["M Houndoom-EX"]
    assert houndoom["attack_name"] == "Inferno Fang"
    assert houndoom["hp"] == 210
    assert (houndoom["base_final_damage"], houndoom["boosted_final_damage"]) == (
        160, 320,
    )
    assert houndoom["dangerous_prior_damage"] == tuple(range(0, 50, 10))
    assert set(houndoom["print_ids"]) == {"xy8-22", "xy8-154"}

    # The Fire weakness on 130-HP Zamazenta turns Houndoom's 80+80
    # into a 160/320 final-damage choice, even though printed base is 80.
    assert houndoom["types"] == ["Fire"]
    assert cetitan["types"] == ["Water"]

    print(json.dumps(result, indent=2))
    print("optional boost Strong Bash frontier: PASS")


if __name__ == "__main__":
    main()
