"""Independent frozen 2026 Aichi top-32 source and opponent-plan regression."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from aichi_2026_field import available_proxies, coverage, load_field, paired_plan

SOURCE = {
    "Regidrago": 11,
    "Mega Absol Box": 5,
    "Raichu Electrode Combo": 3,
    "Iron Thorns": 3,
    "Snorlax Stall": 2,
    "Shadow Rider Calyrex": 1,
    "Vileplume Control": 1,
    "Mew Genesect": 1,
    "Mega Lopunny": 1,
    "Raging Bolt": 1,
    "Lillie's Clefairy": 1,
    "Meloetta Donk": 1,
    "Dusknoir Chimecho": 1,
}
data = load_field()
assert {g["archetype"]: g["count"] for g in data["groups"]} == SOURCE
assert data["registered_players"] == 926
c = coverage(data)
assert c["observed_top32"] == 32
assert c["provisional_proxy_top32"] == 27
assert c["archetypes"] == 13
assert c["provisional_proxy_archetypes"] == 8
assert sum(r["count"] for r in c["missing"]) == 5
assert len(c["missing"]) == 5
print("PASS: independent source transcription: 13 archetypes, 32 finishers, 8 eligible proxies")
print("PASS: 27/32 source category coverage, 5/32 missing singleton archetypes")

proxies = available_proxies(data)
assert proxies == {
    "Regidrago": "regidrago-vstar",
    "Mega Absol Box": "mega-absol-garbodor",
    "Raichu Electrode Combo": "raichu-electrode-aichi-2026",
    "Iron Thorns": "iron_thorns_aichi_english",
    "Snorlax Stall": "snorlax-stall-aichi-2026-english",
    "Shadow Rider Calyrex": "shadow-rider-calyrex",
    "Vileplume Control": "vileplume-control",
    "Mew Genesect": "mew-genesect",
}
for candidate in proxies:
    for scenario, expected_replicas in (
        ("observed_top32", 27), ("equal_archetypes", 8),
    ):
        plan = paired_plan(data, candidate, scenario)
        assert plan == paired_plan(data, candidate, scenario)
        assert len(plan) == 2 * expected_replicas
        assert [row["pair_id"] for row in plan] == [
            i for i in range(expected_replicas) for _ in range(2)]
        assert len({(x["pair_id"], x["seat_orientation"]) for x in plan}) == len(plan)
        for i in range(0, len(plan), 2):
            a, b = plan[i:i + 2]
            assert (a["seat_orientation"], b["seat_orientation"]) == ("AB", "BA")
            assert a["seed"] == b["seed"]
            assert (a["seat1_proxy"], a["seat2_proxy"]) == (
                b["seat2_proxy"], b["seat1_proxy"])
            assert a["candidate"] == b["candidate"] == candidate
            assert a["mirror_control"] == b["mirror_control"] == (
                a["candidate"] == a["opponent"])
        observed = Counter(row["opponent"] for row in plan)
        assert observed == {
            name: (2 * SOURCE[name] if scenario == "observed_top32" else 2)
            for name in proxies
        }
        for row in plan:
            assert (ROOT / "results/decks" / row["seat1_proxy"] / "README.md").is_file()
            assert (ROOT / "results/decks" / row["seat2_proxy"] / "README.md").is_file()
print("PASS: 16 deterministic two-seat scenario schedules with faithful category multiplicities")
print("PASS: each observed schedule=27 source-finish proxies x 2 seats; equal scenario=8 x 2")
print("LIMIT: eight 60-card proxy archetypes only, 5 missing finishers; no simulation or match rate")
