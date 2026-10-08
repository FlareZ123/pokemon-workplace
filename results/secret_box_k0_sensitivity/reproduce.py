"""Regression for exact K0 information-premium sensitivity and event geometry."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from secret_box_k0_sensitivity import (
    disposable_sensitivity,
    item_stadium_sensitivity,
)


def test_disposable():
    rows = disposable_sensitivity()
    assert len(rows) == 7
    expect = {
        5: Fraction(27721221786,308593555983713),
        10: Fraction(97514697510,308593555983713),
        20: Fraction(1575083016,2157996894991),
        25: Fraction(241591494492,308593555983713),
        35: Fraction(22545908415,44084793711959),
    }
    for r in rows:
        assert 0 <= r.gap <= r.gap_hand_mass
        if r.value[0] in expect:
            assert r.gap == expect[r.value[0]]
        print(f"D={r.value[0]} K0={100*float(r.nonanticipating):.6f}% gap={100*float(r.gap):.6f}pp")
    assert rows[4].gap > rows[3].gap > rows[2].gap
    assert rows[4].gap > rows[5].gap > rows[6].gap
    print("Disposable density: exact unimodal witness PASS")


def test_backups():
    rows = item_stadium_sensitivity()
    assert len(rows) == 20
    x = {(s, i):r for r in rows for s,i in (r.value,)}
    assert all(x[(1,i)].gap == 0 for i in range(5))
    expect = {
        (2,0): Fraction(6624,1740212123),
        (2,1): Fraction(1575083016,2157996894991),
        (2,3): Fraction(4393481346,4689871671485),
        (3,3): Fraction(1617019421356,1542967779918565),
        (4,3): Fraction(1615173403017,1542967779918565),
    }
    for row in rows:
        assert 0 <= row.gap <= row.gap_hand_mass
        if row.value in expect:
            assert row.gap == expect[row.value]
        print(f"S,I={row.value} K0={100*float(row.nonanticipating):.6f}% gap={100*float(row.gap):.6f}pp")
    assert x[(3,3)].gap > x[(4,3)].gap
    assert x[(3,3)].gap > x[(3,2)].gap
    assert x[(2,0)].gap < x[(2,1)].gap
    print("Item/Stadium backup geometry: exact nonmonotonic witness PASS")


if __name__ == "__main__":
    test_disposable()
    test_backups()
    print("ALL TESTS PASSED")
