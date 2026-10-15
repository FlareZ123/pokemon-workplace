"""Independent labeled-card brute-force oracle and named-card regression."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from shadow_rider_psychic_tech_fog_opening import psychic_tech_access
from results.competitive_deck_baselines.shadow_rider_reproduce import (
    POKEMON, TRAINERS, PRINT_IDS,
)


def oracle(n: int, b: int, f: int, h: int, p: int):
    tech = 0
    basics = set(range(b))
    fogs = set(range(b, b + f))
    total = valid = direct = via_fog = 0
    for hand in combinations(range(n), h):
        hs = set(hand)
        for prizes in combinations((x for x in range(n) if x not in hs), p):
            ps = set(prizes)
            total += 1
            allowed = bool(hs & basics)
            valid += int(allowed)
            direct += int(tech in hs)
            via_fog += int(
                allowed and tech not in hs and tech not in ps and bool(hs & fogs)
            )
    return (
        Fraction(valid, total),
        Fraction(direct, total),
        Fraction(via_fog, total),
        Fraction(direct + via_fog, valid),
    )


def card(cid: str):
    set_id = cid.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(item for item in cards if item["id"] == cid)


def main() -> None:
    for toy in (
        (10, 3, 2, 2, 3),
        (11, 4, 2, 3, 2),
        (12, 4, 3, 3, 3),
    ):
        calc = psychic_tech_access(
            deck_size=toy[0], basic_count=toy[1],
            fog_crystal_count=toy[2], opening_hand=toy[3],
            prize_count=toy[4],
        )
        assert calc == oracle(*toy), (toy, calc, oracle(*toy))

    assert TRAINERS["Fog Crystal"] == 4
    assert PRINT_IDS["Fog Crystal"] == "swsh6-140"
    fog = card("swsh6-140")
    assert any("Basic Psychic Pokémon" in rule for rule in fog["rules"])
    assert card("sv5-78")["types"] == ["Psychic"]
    assert "Basic" in card("sv5-78")["subtypes"]
    assert card("xy4-36")["types"] == ["Psychic"]
    assert "Basic" in card("xy4-36")["subtypes"]
    assert POKEMON["Lillie's Clefairy ex"] == 2

    valid, direct, via, total = psychic_tech_access(
        deck_size=60, basic_count=14, fog_crystal_count=4,
        opening_hand=7, prize_count=6,
    )
    assert round(float(direct / valid) * 100, 6) == 13.543697
    assert round(float(via / valid) * 100, 6) == 29.768008
    assert round(float(total) * 100, 6) == 43.311704
    print(json.dumps({
        "model": "initial seven, one Basic Psychic tech, 4 Fog Crystal, 6 Prizes",
        "toy_exhaustive_worlds_checked": 3,
        "initial_basic_valid_percent": round(100 * float(valid), 6),
        "tech_direct_given_valid_percent": round(100 * float(direct / valid), 6),
        "extra_fog_only_given_valid_percent": round(100 * float(via / valid), 6),
        "any_direct_or_fog_given_valid_percent": round(100 * float(total), 6),
        "match_win_rate_estimated": False,
        "result": "PASS",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
