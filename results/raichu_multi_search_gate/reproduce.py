"""Reproduce shared-search DCI gate for Harto Miki's Raichu/Electrode."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from raichu_multi_search_gate import EVENTS, brute_raichu_gate, raichu_multi_search_gate
from raichu_prize_access import raichu_access_snapshot

TOYS = (
    dict(deck_size=10, giratina=1, other_basics=2,
         energy=2, ultra=2, computer=1, opening=4, prizes=2),
    dict(deck_size=11, giratina=1, other_basics=2,
         energy=3, ultra=2, computer=1, opening=5, prizes=2),
    dict(deck_size=12, giratina=1, other_basics=3,
         energy=3, ultra=2, computer=1, opening=5, prizes=2),
)
for params in TOYS:
    for active_policy in ("preserve_giratina", "lead_giratina"):
        assert raichu_multi_search_gate(
            **params, active_policy=active_policy
        ) == brute_raichu_gate(**params, active_policy=active_policy)
print("PASS: 6 full labeled physical opener/Prize/draw/Active-policy oracles")

for energy in range(30):
    preserve = raichu_multi_search_gate(energy=energy)
    lead = raichu_multi_search_gate(energy=energy, active_policy="lead_giratina")
    for event in EVENTS:
        assert preserve[event] >= lead[event], (energy, event)
    if energy:
        earlier = raichu_multi_search_gate(energy=energy - 1)
        for event in EVENTS:
            assert preserve[event] >= earlier[event], (energy, event)
print("PASS: policy dominance and 29 discard-energy-frontier monotonicity steps")

row = raichu_multi_search_gate()
lead = raichu_multi_search_gate(active_policy="lead_giratina")
prior = raichu_access_snapshot()
assert abs(float(row["discard_two_held"]) -
           prior.connector_payable_probability) < 1e-12
assert row["either_strict"] > lead["either_strict"]
assert row["either_held"] == lead["either_held"]
assert row["either_extra_basics"] == lead["either_extra_basics"]
assert row["both_extra_basics"] == lead["both_extra_basics"]
for event in EVENTS:
    print(f"{event:25s} preserve={float(row[event])*100:.9f}%"
          f" lead={float(lead[event])*100:.9f}%")
print("PASS: agreement with corrected historical Giratina-overlap model")
