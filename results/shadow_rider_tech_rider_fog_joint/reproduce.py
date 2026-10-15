"""Exact labeled-world oracle for two-target one-Fog-per-target access."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from shadow_rider_tech_rider_fog_joint import two_target_fog_access
from results.competitive_deck_baselines.shadow_rider_reproduce import (
    POKEMON, TRAINERS, PRINT_IDS,
)


def labeled_oracle(n: int, b: int, r: int, f: int, h: int, p: int):
    tech = 0
    riders = set(range(1, 1+r))
    basics = set(range(b))
    fogs = set(range(b, b+f))
    total = valid = 0
    success = {0: 0, 1: 0, 2: 0}
    for hand in combinations(range(n), h):
        hs = set(hand)
        for prizes in combinations((x for x in range(n) if x not in hs), p):
            ps = set(prizes)
            total += 1
            is_valid = bool(hs & basics)
            valid += int(is_valid)
            if not is_valid:
                continue
            need_tech = int(tech not in hs)
            need_rider = int(not (riders & hs))
            searches_needed = need_tech + need_rider
            if len(hs & fogs) < searches_needed:
                continue
            if need_tech and tech in ps:
                continue
            if need_rider and riders <= ps:
                continue
            success[searches_needed] += 1
    valid_fraction = Fraction(valid, total)
    partition = {key: Fraction(v, valid) for key, v in success.items()}
    return valid_fraction, sum(partition.values(), Fraction()), partition


def source_text(cid: str):
    set_id = cid.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8")
    )
    return next(row for row in cards if row["id"] == cid)


def main() -> None:
    for toy in (
        (10, 4, 2, 2, 3, 2),
        (11, 4, 2, 2, 3, 3),
        (12, 5, 3, 2, 3, 3),
    ):
        args = dict(
            deck_size=toy[0], basic_count=toy[1], rider_count=toy[2],
            fog_count=toy[3], hand_size=toy[4], prize_count=toy[5],
        )
        analytical = two_target_fog_access(**args)
        exhaustive = labeled_oracle(*toy)
        assert analytical == exhaustive, (toy, analytical, exhaustive)

    assert POKEMON["Shadow Rider Calyrex V"] == 3
    assert TRAINERS["Fog Crystal"] == 4
    assert PRINT_IDS["Fog Crystal"] == "swsh6-140"
    fog = source_text("swsh6-140")
    assert any("Basic Psychic Pokémon" in rule for rule in fog["rules"])
    for cid in ("sv5-78", "xy4-36", "swsh6-74"):
        target = source_text(cid)
        assert "Basic" in target["subtypes"]
        assert "Psychic" in target["types"]

    valid, all_targets, partition = two_target_fog_access(
        deck_size=60, basic_count=14, rider_count=3,
        fog_count=4, hand_size=7, prize_count=6,
    )
    assert round(float(valid)*100, 6) == 86.140932
    assert round(float(all_targets)*100, 6) == 21.072697
    assert round(float(partition[0])*100, 6) == 3.784103
    assert round(float(partition[1])*100, 6) == 14.323005
    assert round(float(partition[2])*100, 6) == 2.965589

    print(json.dumps({
        "model": "first seven and six Prizes, two Basic Psychic goals, Fog only",
        "exhaustive_toy_checks": 3,
        "conditional_valid_both_targets_percent": round(float(all_targets)*100, 6),
        "conditional_search_count_partition_percent": {
            str(k): round(float(v)*100, 6) for k, v in partition.items()
        },
        "match_win_rate_measured": False,
        "status": "PASS",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
