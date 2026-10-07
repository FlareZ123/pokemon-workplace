"""Reproduce the belief-constrained first-Secret-Box payment audit."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_secret_box_k0_policy import simulate_clean_box_audit


def main() -> None:
    result = simulate_clean_box_audit(50_000, seed=20261007)

    if result.qualifying_states != 1_265:
        raise AssertionError(result.qualifying_states)
    if result.unique_observations != 333:
        raise AssertionError(result.unique_observations)
    if result.positive_gap_states != 0:
        raise AssertionError(result.positive_gap_states)
    if result.positive_gap_observations != 0:
        raise AssertionError(result.positive_gap_observations)
    if result.oracle_success_weight != result.k0_success_weight:
        raise AssertionError("K0 and oracle weighted success differ")
    if not isclose(
        result.k0_conditional_success,
        0.96734882613,
        rel_tol=0.0,
        abs_tol=5e-12,
    ):
        raise AssertionError(result.k0_conditional_success)

    print(f"qualifying={result.qualifying_states}/{result.trials}")
    print(f"unique_observations={result.unique_observations}")
    print(f"conditional_success={result.k0_conditional_success:.9%}")
    print(f"policy_information_gap={result.conditional_gap * 100:.9f} pp")
    print("All Aichi Secret Box K0-policy checks passed.")


if __name__ == "__main__":
    main()
