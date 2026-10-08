"""Seeded regression for K1 reset-cancellation option value."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_reset_cancel_option import simulate


def main() -> None:
    result = simulate(samples=1_000_000, seed=20261008)

    assert 25_000 < result["observable_branch_states"] < 40_000

    later = result["later"]
    first = result["first"]

    assert 0.09 < later["reset_capable_fraction_branch"] < 0.14
    assert 0.08 < later["immediate_fraction_reset_capable"] < 0.15
    assert 0.007 < later["cancel_option_gain_branch"] < 0.016
    assert 0.07 < later["cancel_option_gain_reset_capable"] < 0.12

    assert 0.15 < first["reset_capable_fraction_branch"] < 0.22
    assert 0.08 < first["immediate_fraction_reset_capable"] < 0.15
    assert 0.013 < first["cancel_option_gain_branch"] < 0.023
    assert 0.07 < first["cancel_option_gain_reset_capable"] < 0.12

    assert first["cancel_option_gain_branch"] > later["cancel_option_gain_branch"]

    print("Raichu reset-cancellation option regression: PASS")


if __name__ == "__main__":
    main()
