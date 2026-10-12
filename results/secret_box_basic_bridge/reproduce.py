"""Reproduce exact Secret Box -> Quick Ball -> Basic prize-aware access."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from secret_box_basic_bridge import (
    EVENTS, brute_basic_bridge, exact_basic_bridge
)
from joint_item_payment import joint_item_payment

TOYS = (
    dict(deck_size=12, basics=2, quick=1, ultra=1, secret=1,
         filler=4, opening=7, prizes=2),
    dict(deck_size=13, basics=2, quick=1, ultra=1, secret=1,
         filler=5, opening=7, prizes=2),
    dict(deck_size=14, basics=2, quick=2, ultra=1, secret=1,
         filler=5, opening=7, prizes=2),
)
for params in TOYS:
    exact = exact_basic_bridge(**params)
    oracle = brute_basic_bridge(**params)
    assert exact == oracle, params
    assert exact["incremental_bridge"] > 0
print("PASS: 3 independent labeled opener/Prize/draw oracles")

for filler in range(32):
    now = exact_basic_bridge(filler=filler)
    if filler:
        previous = exact_basic_bridge(filler=filler - 1)
        for name in EVENTS:
            assert now[name] >= previous[name], (name, filler)
print("PASS: 31 monotonicity steps for each of five exact bridge events")

for filler in (4, 8, 12, 20, 28):
    row = exact_basic_bridge(filler=filler)
    gates = joint_item_payment(filler=filler)
    assert row["combined_basic"] <= gates["any_payable"]
    assert row["incremental_bridge"] <= gates["secret_payable"]
    assert row["secret_bridge_basic"] <= row["bridge_pre_prize"]
    print(f"F={filler} direct={float(row['direct_basic'])*100:.10f}% "
          f"bridge_increment={float(row['incremental_bridge'])*100:.10f}% "
          f"combined={float(row['combined_basic'])*100:.10f}%")
print("PASS: prize-aware bridge adds to the direct typed Basic search endpoint")
