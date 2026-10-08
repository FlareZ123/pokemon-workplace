"""Exact grouped-vs-per-target KO ordering multiplicity theorem.

For n independent KO targets, one global loss program competes with n
target-specific recovery programs. Compare that to n independently replicated
loss programs, one per target. Both produce every binary endpoint but they
induce different multiplicities of total orders.
"""

from fractions import Fraction
from math import factorial
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ko_order_outcome_space import ko_order_outcomes


def make_programs(n, *, grouped):
    if n < 1:
        raise ValueError("n must be positive")
    loss = {f"target-{i}": "lost_zone" for i in range(n)}
    programs = {
        f"recover-{i}": {f"target-{i}": "hand"}
        for i in range(n)
    }
    if grouped:
        programs["lost-all"] = loss
    else:
        programs.update({
            f"lost-{i}": {f"target-{i}": "lost_zone"}
            for i in range(n)
        })
    return programs


def outcome_mask(destinations):
    mask = 0
    for index, (instance_id, zone) in enumerate(destinations):
        assert instance_id == f"target-{index}"
        assert zone in ("hand", "lost_zone")
        if zone == "hand":
            mask |= 1 << index
    return mask


def theoretical_count(n, mask, *, grouped):
    if not 0 <= mask < (1 << n):
        raise ValueError("invalid target subset")
    if grouped:
        recovered = mask.bit_count()
        return factorial(recovered) * factorial(n - recovered)
    return factorial(2 * n) // (1 << n)


def main():
    for n in range(1, 6):
        grouped = {
            outcome_mask(row.destinations): row.order_count
            for row in ko_order_outcomes(make_programs(n, grouped=True))
        }
        per_target = {
            outcome_mask(row.destinations): row.order_count
            for row in ko_order_outcomes(make_programs(n, grouped=False))
        }
        assert set(grouped) == set(per_target) == set(range(1 << n))
        assert len(grouped) == len(per_target) == (1 << n)
        assert sum(grouped.values()) == factorial(n + 1)
        assert sum(per_target.values()) == factorial(2 * n)
        for subset in range(1 << n):
            assert grouped[subset] == theoretical_count(
                n, subset, grouped=True
            )
            assert per_target[subset] == theoretical_count(
                n, subset, grouped=False
            )

        # If an arbitrary test harness treats total effect orders as
        # uniformly likely, grouping introduces a representation-dependent
        # endpoint distribution. This is a *synthetic harness measure*, not a
        # probability of how actual players exercise effect-order choices.
        p_grouped_all_lost = Fraction(grouped[0], factorial(n + 1))
        p_separate_all_lost = Fraction(per_target[0], factorial(2 * n))
        assert p_grouped_all_lost == Fraction(1, n + 1)
        assert p_separate_all_lost == Fraction(1, 1 << n)
        print(
            f"n={n}: {1 << n} endpoints, grouped {factorial(n + 1)} "
            f"orders, per-target {factorial(2 * n)} orders; "
            f"all-lost synthetic weights {p_grouped_all_lost} vs "
            f"{p_separate_all_lost}; ratio "
            f"{p_grouped_all_lost / p_separate_all_lost}"
        )

    # The observed Tyranitar-GX two-KO fixture is the n=2 case.
    assert [theoretical_count(2, mask, grouped=True)
            for mask in range(4)] == [2, 1, 1, 2]
    assert [theoretical_count(2, mask, grouped=False)
            for mask in range(4)] == [6, 6, 6, 6]
    print("KO effect-instance granularity formulas validated against exact DP")


if __name__ == "__main__":
    main()
