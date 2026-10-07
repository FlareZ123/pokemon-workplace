"""Reproduce grouped Prize-belief transitions."""

from __future__ import annotations

from math import isclose, log2
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_belief_kernel import PrizeBelief  # noqa: E402


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    initial = PrizeBelief.from_hypergeometric(
        {"A": 1},
        pool_size=53,
        prize_count=6,
    )
    _assert_close(initial.probability_mass(), 1.0)
    initial_states = {
        state["A"]: probability
        for state, probability in initial.state_dicts()
    }
    _assert_close(initial_states[0], 47 / 53)
    _assert_close(initial_states[1], 6 / 53)

    observed_a = initial.observe_random_position("A")
    assert observed_a.is_exact()
    assert observed_a.state_dicts() == [({"A": 1}, 1.0)]

    exact = PrizeBelief.from_exact(
        {
            "A": 1,
            "B": 1,
            "C": 1,
            "D": 1,
            "E": 1,
            "F": 1,
            "X": 0,
        },
        prize_count=6,
    )
    assert exact.is_exact()
    _assert_close(exact.entropy_bits(), 0.0)

    arc_phone_like = exact.replace_unknown_position_with_known("X")
    _assert_close(arc_phone_like.probability_mass(), 1.0)
    assert len(arc_phone_like.masses) == 6
    for _, probability in arc_phone_like.masses:
        _assert_close(probability, 1 / 6)
    _assert_close(arc_phone_like.entropy_bits(), log2(6))

    reinspected = PrizeBelief.from_exact(
        {
            "A": 0,
            "B": 1,
            "C": 1,
            "D": 1,
            "E": 1,
            "F": 1,
            "X": 1,
        },
        prize_count=6,
    )
    assert reinspected.is_exact()
    _assert_close(reinspected.entropy_bits(), 0.0)

    redealt = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1, "C": 1},
        pool_size=52,
        prize_count=6,
    )
    _assert_close(redealt.probability_mass(), 1.0)
    assert not redealt.is_exact()

    print("Initial unseen singleton belief")
    for state, probability in initial.state_dicts():
        print(f"  {state}: {probability:.9%}")
    print()

    print("After observing singleton A at a random Prize position")
    print(f"  states: {observed_a.state_dicts()}")
    print()

    print("Exact six-Prize composition -> known incoming / unknown outgoing swap")
    print(f"  resulting states: {len(arc_phone_like.masses)}")
    print(f"  entropy: {arc_phone_like.entropy_bits():.9f} bits")
    print()

    print("After complete re-inspection")
    print(f"  exact: {reinspected.is_exact()}")
    print(f"  entropy: {reinspected.entropy_bits():.9f} bits")
    print()

    print("All grouped Prize-belief kernel checks passed.")


if __name__ == "__main__":
    main()
