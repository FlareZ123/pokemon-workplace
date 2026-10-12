"""Reproduce exact Harto Raichu target access with paid dual-source policies."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from raichu_prize_source_policy import (
    EVENTS, POLICIES, brute_raichu_prize_policy, raichu_prize_source_policy
)
from raichu_prize_access import raichu_access_snapshot
from raichu_multi_search_gate import raichu_multi_search_gate

TOYS = (
    dict(deck_size=10, target=1, gladion=1, ultra=1, computer=1,
         giratina=1, other_basics=2, energy=2, opening=4, prizes=2),
    dict(deck_size=11, target=1, gladion=2, ultra=1, computer=1,
         giratina=1, other_basics=2, energy=2, opening=4, prizes=2),
    dict(deck_size=12, target=1, gladion=2, ultra=2, computer=1,
         giratina=1, other_basics=2, energy=2, opening=4, prizes=2),
)
for case in TOYS:
    for active_policy in ("preserve_giratina", "lead_giratina"):
        exact = raichu_prize_source_policy(**case, active_policy=active_policy)
        physical = brute_raichu_prize_policy(**case, active_policy=active_policy)
        assert exact == physical, (case, active_policy)
print("PASS: six fully labeled independent opening/Prize/draw/access oracles")

for energy in (0, 4, 8, 11, 12, 20):
    for active_policy in ("preserve_giratina", "lead_giratina"):
        row = raichu_prize_source_policy(
            energy=energy, active_policy=active_policy
        )
        for event in EVENTS:
            vals = [row[f"{p}_{event}"] for p in POLICIES]
            assert vals == sorted(vals), (energy, active_policy, event)
        assert (row["computer_can_use_ultra_adaptive"]
                == row["any_source_adaptive"])
print("PASS: strict/same-source/Computer-sacrifice/all-source dominance")

baseline = raichu_prize_source_policy()
prior = raichu_access_snapshot()
assert abs(float(baseline["strict_target_held"])
           - prior.target_in_exposed_hand_probability) < 1e-12
assert abs(float(baseline["strict_ultra_gladion"])
           - prior.ultra_plus_gladion_gated_access) < 1e-12
assert abs(float(baseline["strict_static"])
           - prior.static_computer_gated_access) < 1e-12
assert abs(float(baseline["strict_adaptive"])
           - prior.adaptive_computer_gated_access) < 1e-12
gates = raichu_multi_search_gate()
assert baseline["strict_ultra_paid"] == gates["ultra_strict"]
assert baseline["strict_computer_paid"] == gates["computer_strict"]
assert baseline["spare_ultra_ultra_paid"] == gates["ultra_spares"]
assert (baseline["computer_can_use_ultra_computer_paid"]
        == gates["computer_all_sources"])

assert (baseline["any_source_ultra_gladion"]
        > baseline["computer_can_use_ultra_ultra_gladion"])
assert (baseline["any_source_adaptive"]
        == baseline["computer_can_use_ultra_adaptive"])

for active_policy in ("preserve_giratina", "lead_giratina"):
    row = raichu_prize_source_policy(active_policy=active_policy)
    print(f"Active policy: {active_policy}")
    for policy in POLICIES:
        print(f"  {policy:26s}"
              f" static={float(row[f'{policy}_static'])*100:.9f}%"
              f" adaptive={float(row[f'{policy}_adaptive'])*100:.9f}%")
print("PASS: exact strict results agree with two earlier Raichu engines")
