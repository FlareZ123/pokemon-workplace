"""Reproduce the Aichi Vileplume Grand Tree -> Secret Box core comparison."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_vileplume_secret_box import simulate_swap


def main() -> None:
    result = simulate_swap(100_000, seed=20261007)

    expected = {
        "baseline_successes": 70_709,
        "secret_box_successes": 74_884,
        "incremental_successes": 4_175,
        "baseline_only_successes": 0,
        "secret_box_in_hand": 12_723,
        "secret_box_stellar_only": 1_148,
        "incremental_jet_in_hand": 978,
        "incremental_jet_needs_gnh": 3_197,
        "incremental_started_with_gnh_or_tag_call": 0,
    }
    for field, value in expected.items():
        actual = getattr(result, field)
        if actual != value:
            raise AssertionError(f"{field}: {actual} != {value}")

    print(f"baseline={result.baseline_probability:.6%}")
    print(f"secret_box={result.secret_box_probability:.6%}")
    print(f"increment={result.incremental_probability:.6%}")
    print(f"secret_box_access={result.secret_box_access_probability:.6%}")
    print(
        "incremental_jet_needs_gnh="
        f"{result.incremental_jet_needs_gnh / result.incremental_successes:.6%}"
    )
    print("All Aichi Secret Box checks passed.")


if __name__ == "__main__":
    main()
