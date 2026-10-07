"""Reproduce multi-output connector one-slot marginal results."""

from __future__ import annotations

from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from multi_output_slot_marginals import (
    first_symmetric_disposable_crossover,
    fixed_size_multi_output_marginals,
)


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def _brute_labeled_access(
    deck_size: int,
    *,
    starter_cards: int,
    target_counts: tuple[int, ...],
    disposable_nonstarters: int,
    discard_cost: int,
    connector_capacity: int,
    opening_hand_size: int,
    prize_count: int,
) -> float:
    """Independently enumerate accepted hands and disjoint Prize sets."""

    deck: list[str] = []
    for target_index, count in enumerate(target_counts):
        deck.extend([f"T{target_index}"] * count)
    deck.append("C")
    deck.extend(["D"] * disposable_nonstarters)
    deck.extend(["S"] * starter_cards)
    deck.extend(["F"] * (deck_size - len(deck)))

    success = 0
    states = 0
    indices = range(deck_size)

    for hand_indices in combinations(indices, opening_hand_size):
        hand_set = set(hand_indices)
        hand = [deck[index] for index in hand_indices]
        if "S" not in hand:
            continue

        remaining = [index for index in indices if index not in hand_set]
        for prize_indices in combinations(remaining, prize_count):
            prize_set = set(prize_indices)
            states += 1

            missing = [
                target_index
                for target_index in range(len(target_counts))
                if f"T{target_index}" not in hand
            ]
            if not missing:
                success += 1
                continue

            if "C" not in hand:
                continue
            if hand.count("D") < discard_cost:
                continue
            if len(missing) > connector_capacity:
                continue

            every_missing_target_searchable = all(
                any(
                    deck[index] == f"T{target_index}"
                    and index not in prize_set
                    for index in remaining
                )
                for target_index in missing
            )
            if every_missing_target_searchable:
                success += 1

    return success / states


def _tiny_independent_regression() -> None:
    common = dict(
        deck_size=12,
        prize_count=2,
        starter_cards=2,
        disposable_nonstarters=2,
        discard_cost=2,
        connector_capacity=4,
        opening_hand_size=4,
    )
    targets = (1, 1, 1, 1)

    exact = fixed_size_multi_output_marginals(
        target_counts=targets,
        **common,
    )

    brute_baseline = _brute_labeled_access(
        12,
        starter_cards=2,
        target_counts=targets,
        disposable_nonstarters=2,
        discard_cost=2,
        connector_capacity=4,
        opening_hand_size=4,
        prize_count=2,
    )
    brute_direct = _brute_labeled_access(
        12,
        starter_cards=2,
        target_counts=(2, 1, 1, 1),
        disposable_nonstarters=2,
        discard_cost=2,
        connector_capacity=4,
        opening_hand_size=4,
        prize_count=2,
    )
    brute_disposable = _brute_labeled_access(
        12,
        starter_cards=2,
        target_counts=targets,
        disposable_nonstarters=3,
        discard_cost=2,
        connector_capacity=4,
        opening_hand_size=4,
        prize_count=2,
    )

    _assert_close(exact.baseline_joint_access, brute_baseline)
    _assert_close(exact.add_target_gains[0], brute_direct - brute_baseline)
    _assert_close(exact.add_disposable_gain, brute_disposable - brute_baseline)
    _assert_close(exact.disposable_to_strongest_direct_ratio, 4.0)


def main() -> None:
    _tiny_independent_regression()

    expected = {
        2: (
            0.0665519390431932,
            0.016971312568740654,
            0.0034506644840019,
            0.20332337113145013,
        ),
        3: (
            0.03420250478741763,
            0.0028784150098249417,
            0.0034462671357820343,
            1.1972794485919624,
        ),
        4: (
            0.0288512109606193,
            0.0005806440207880743,
            0.003412831226981189,
            5.877665324701272,
        ),
    }

    print("Channels | baseline | +1 direct | +1 disposable | disposable/direct")
    for channels, values in expected.items():
        result = fixed_size_multi_output_marginals(
            60,
            6,
            starter_cards=12,
            target_counts=(2,) * channels,
            disposable_nonstarters=20,
            discard_cost=3,
            connector_capacity=channels,
        )
        direct_gain = result.add_target_gains[0]
        _assert_close(result.baseline_joint_access, values[0])
        _assert_close(direct_gain, values[1])
        _assert_close(result.add_disposable_gain, values[2])
        _assert_close(result.disposable_to_strongest_direct_ratio, values[3])
        for gain in result.add_target_gains:
            _assert_close(gain, direct_gain)

        print(
            f"{channels:8d} | "
            f"{result.baseline_joint_access:.6%} | "
            f"{direct_gain:.6%} | "
            f"{result.add_disposable_gain:.6%} | "
            f"{result.disposable_to_strongest_direct_ratio:.6f}x"
        )

    crossovers = {
        channels: first_symmetric_disposable_crossover(channels, 2)
        for channels in (2, 3, 4)
    }
    if crossovers != {2: None, 3: 17, 4: 5}:
        raise AssertionError(crossovers)

    print()
    print(f"First disposable-dominant D: {crossovers}")
    print("All multi-output slot-marginal checks passed.")


if __name__ == "__main__":
    main()
