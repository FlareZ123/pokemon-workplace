"""Seven-card shared-Item DCI policy frontier and physical-card regressions."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from joint_discard_policy_frontier import (
    ACTION_NAMES, POLICIES, brute_policy_frontier, exact_policy_frontier
)
from joint_item_payment import joint_item_payment
from basic_valid_discard_quota import basic_valid_discard_quota

TOYS = (
    dict(deck_size=11, basics=2, quick=1, ultra=1, secret=1,
         filler=3, opening=5, prizes=2),
    dict(deck_size=12, basics=2, quick=2, ultra=1, secret=1,
         filler=3, opening=5, prizes=2),
    dict(deck_size=13, basics=2, quick=2, ultra=1, secret=1,
         filler=4, opening=7, prizes=2),
    dict(deck_size=13, basics=2, quick=1, ultra=1, secret=1,
         filler=6, opening=9, prizes=1),
)
for config in TOYS:
    assert exact_policy_frontier(**config) == brute_policy_frontier(**config)
print("PASS: 4 labeled physical opener/Prize/draw exhaustive oracles")

for filler in range(32):
    row = exact_policy_frontier(filler=filler)
    if filler:
        earlier = exact_policy_frontier(filler=filler - 1)
        for k in row:
            assert row[k] >= earlier[k], (filler, k)
print("PASS: all 45 exact events monotone under safe-filler relaxation")

for filler in (0, 4, 8, 12, 20, 28):
    model = exact_policy_frontier(filler=filler)
    original = joint_item_payment(filler=filler)
    assert model["filler_only_any"] == original["any_payable"]
    assert model["filler_only_two"] == original["two_sequential"]
    assert model["filler_only_quick"] == original["quick_payable"]
    assert model["filler_only_ultra"] == original["ultra_payable"]
    assert model["filler_only_secret"] == original["secret_payable"]
    for name, copies, m in (("quick", 4, 1), ("ultra", 4, 2), ("secret", 1, 3)):
        previous = basic_valid_discard_quota(
            basics=12, source_copies=copies, disposable=filler, required_discards=m
        )
        assert model[f"same_source_spares_{name}"] == previous.allow_spare_source_copies
    assert model["all_sources_extra_basics_all_three"] == 0
    print(f"F={filler}:")
    for policy in POLICIES:
        print(f"  {policy:26s} any={float(model[f'{policy}_any'])*100:.9f}%"
              f" two={float(model[f'{policy}_two'])*100:.9f}%")
print("PASS: cross-validation with prior distinct Item quota engines")
