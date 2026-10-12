"""Reproduce real-list endpoint and independent physical-card oracle."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from raichu_target_payment_frontier import (DEFAULT, EVENTS, POLICIES,
    brute_target_payment, raichu_target_payment_frontier)

TOYS = (
    ((1, 1, 1, 1, 1, 2, 1, 2), 4, 2),
    ((1, 2, 2, 1, 1, 2, 2, 0), 4, 2),
    ((1, 2, 2, 1, 1, 3, 1, 1), 4, 2),
)
for counts, opening, prizes in TOYS:
    for active in ("preserve_giratina", "lead_giratina"):
        expected = brute_target_payment(counts=counts, opening=opening,
                                         prizes=prizes, active_policy=active)
        exact = raichu_target_payment_frontier(counts=counts, opening=opening,
                                                prizes=prizes, active_policy=active)
        assert exact == expected, (counts, opening, prizes, active)
print("PASS: six independent labeled-card opening/Prize/draw/Active exhaustive oracles")

results = {a: raichu_target_payment_frontier(active_policy=a) for a in
           ("preserve_giratina", "lead_giratina")}
for active, table in results.items():
    previous = None
    for p in POLICIES:
        row = table[p]
        assert row["adaptive_access"] >= row["static_access"] >= row["direct_access"]
        assert row["computer_prize_rescue"] == row["adaptive_access"] - row["static_access"]
        assert row["target_prized"] >= row["prized_adaptive"]
        if previous:
            assert all(row[e] >= previous[e] for e in ("source_payable", "direct_access",
                       "static_access", "adaptive_access", "prized_adaptive"))
        previous = row
        print(f"{active:19s} {p:16s} payable={float(row['source_payable'])*100:.9f}%"
              f" direct={float(row['direct_access'])*100:.9f}%"
              f" static={float(row['static_access'])*100:.9f}%"
              f" adaptive={float(row['adaptive_access'])*100:.9f}%"
              f" rescue={float(row['computer_prize_rescue'])*100:.9f}%")
assert abs(float(results["preserve_giratina"]["strict"]["adaptive_access"])
           - 0.30578700) < 2e-7
for p in POLICIES:
    assert all(results["preserve_giratina"][p][e]
               >= results["lead_giratina"][p][e]
               for e in ("source_payable", "direct_access", "static_access",
                         "adaptive_access", "prized_adaptive"))
print("PASS: nested policy dominance, prior strict access agreement, source adaptivity")
