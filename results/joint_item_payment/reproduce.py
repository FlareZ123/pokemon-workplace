"""Reproduce joint Item payment probabilities and independent physical tests."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from joint_item_payment import (EVENTS, brute_labeled, joint_item_payment)
from basic_valid_discard_quota import basic_valid_discard_quota

TOYS = (
    dict(deck_size=9, basics=2, quick=1, ultra=1, secret=1,
         filler=1, opening=3, prizes=2),
    dict(deck_size=10, basics=2, quick=2, ultra=1, secret=1,
         filler=1, opening=3, prizes=2),
    dict(deck_size=10, basics=3, quick=1, ultra=1, secret=1,
         filler=2, opening=4, prizes=2),
    dict(deck_size=11, basics=2, quick=1, ultra=1, secret=1,
         filler=3, opening=3, prizes=2),
    # Nonzero sequential Quick+Ultra payment.
    dict(deck_size=11, basics=2, quick=1, ultra=1, secret=1,
         filler=3, opening=5, prizes=2),
    # Nonzero Ultra+Secret sequential payment.
    dict(deck_size=12, basics=2, quick=1, ultra=1, secret=1,
         filler=5, opening=7, prizes=2),
    # Nonzero all-three sequential payment in a larger-hand toy.
    dict(deck_size=13, basics=2, quick=1, ultra=1, secret=1,
         filler=6, opening=9, prizes=1),
)
for params in TOYS:
    exact = joint_item_payment(**params)
    physical = brute_labeled(**params)
    assert {k: v for k, v in exact.items() if k != "basic_valid"} == physical
print(f"PASS: {len(TOYS)} independently labeled full Prize/deal oracles")

for filler in range(32):
    now = joint_item_payment(filler=filler)
    if filler:
        old = joint_item_payment(filler=filler - 1)
        for event in EVENTS:
            assert now[event] >= old[event], (filler, event)
print("PASS: 31 pairwise monotonicity checks across all 18 event probabilities")

for copies, quota, name in (
    (4, 1, "quick"),
    (4, 2, "ultra"),
    (1, 3, "secret"),
):
    old = basic_valid_discard_quota(
        basics=12, source_copies=copies, disposable=8, required_discards=quota
    )
    new = joint_item_payment(filler=8)
    assert old.source_held == new[f"{name}_held"]
    assert old.strict_disposables == new[f"{name}_payable"]
print("PASS: exact source-specific marginals match independent previous engine")

row = joint_item_payment(filler=8)
assert row["all_sequential"] == 0
assert row["any_payable"] > row["two_individual"] > row["two_sequential"]
for name in EVENTS:
    print(f"{name:28s}: {float(row[name]) * 100:.9f}%")
print("PASS: all exact baseline and conservation assertions")
