"""Reproduce and validate the setup hand-value policy result."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.setup_hand_value_policy import (  # noqa: E402
    SetupHandState,
    conditioned_prize_hand_distribution,
    opening_hand_distribution,
    optimize_linear_mulligan_penalty,
    specific_class_card_prize_probability,
    stationary_policy_metrics,
)


def value(state: SetupHandState) -> float:
    return float(state.feature_counts[0] > 0)


def selective(state: SetupHandState) -> float:
    return value(state)


def accept_all(state: SetupHandState) -> float:
    return 1.0


def validate_optimizer() -> None:
    def small_value(state: SetupHandState) -> float:
        return (
            0.55 * float(state.feature_counts[0] > 0)
            + 0.08 * state.feature_counts[0]
            + 0.03 * state.optional_counts[0]
        )

    optional_states = [
        state
        for state, _ in opening_hand_distribution(
            8, 2, (2,), (2,), opening_hand_size=3
        )
        if state.forced_in_hand == 0 and sum(state.optional_counts) > 0
    ]
    best = None
    best_acceptance = None
    for mask in range(2 ** len(optional_states)):
        keep = {
            state
            for index, state in enumerate(optional_states)
            if mask // (2 ** index) % 2
        }
        metrics = stationary_policy_metrics(
            8,
            2,
            (2,),
            (2,),
            small_value,
            lambda state, keep=keep: float(state in keep),
            opening_hand_size=3,
            mulligan_penalty=0.17,
        )
        if best is None or metrics.expected_utility > best + 1e-15:
            best = metrics.expected_utility
            best_acceptance = metrics.acceptance_probability
        elif abs(metrics.expected_utility - best) <= 1e-15:
            best_acceptance = max(best_acceptance, metrics.acceptance_probability)

    optimized = optimize_linear_mulligan_penalty(
        8,
        2,
        (2,),
        (2,),
        small_value,
        opening_hand_size=3,
        mulligan_penalty=0.17,
    )
    assert abs(optimized.metrics.expected_utility - best) < 1e-14
    assert abs(optimized.metrics.acceptance_probability - best_acceptance) < 1e-14


def validate_prizes() -> None:
    exact = dict(
        conditioned_prize_hand_distribution(
            10,
            2,
            forced_starters=2,
            optional_group_sizes=(2,),
            feature_group_sizes=(2,),
            optional_policy=selective,
            opening_hand_size=3,
        )
    )
    classes = [0, 0, 1, 1, 2, 2, 3, 3, 3, 3]
    cards = set(range(10))
    brute: dict[tuple[int, ...], float] = {}
    total = 0.0
    for hand_tuple in combinations(range(10), 3):
        hand = set(hand_tuple)
        hand_counts = [
            sum(classes[i] == cls for i in hand)
            for cls in range(4)
        ]
        state = SetupHandState(
            hand_counts[0],
            (hand_counts[1],),
            (hand_counts[2],),
            hand_counts[3],
        )
        keep = hand_counts[0] > 0 or (
            hand_counts[1] > 0 and selective(state) > 0
        )
        if not keep:
            continue
        for prize_tuple in combinations(sorted(cards - hand), 2):
            counts = tuple(
                sum(classes[i] == cls for i in prize_tuple)
                for cls in range(4)
            )
            brute[counts] = brute.get(counts, 0.0) + 1.0
            total += 1.0
    brute = {key: mass / total for key, mass in brute.items()}
    assert exact.keys() == brute.keys()
    for key in exact:
        assert abs(exact[key] - brute[key]) < 1e-14


def main() -> None:
    validate_optimizer()
    validate_prizes()

    selective_metrics = stationary_policy_metrics(
        60, 4, (4,), (4,), value, selective
    )
    all_metrics = stationary_policy_metrics(
        60, 4, (4,), (4,), value, accept_all
    )
    crossover = (
        selective_metrics.expected_terminal_value
        - all_metrics.expected_terminal_value
    ) / (
        selective_metrics.expected_mulligans
        - all_metrics.expected_mulligans
    )

    print("selective acceptance", selective_metrics.acceptance_probability)
    print("selective key rate", selective_metrics.expected_terminal_value)
    print("selective mulligans", selective_metrics.expected_mulligans)
    print("accept-all acceptance", all_metrics.acceptance_probability)
    print("accept-all key rate", all_metrics.expected_terminal_value)
    print("accept-all mulligans", all_metrics.expected_mulligans)
    print("crossover", crossover)

    for penalty in (0.0, 0.1, 0.25):
        result = optimize_linear_mulligan_penalty(
            60,
            4,
            (4,),
            (4,),
            value,
            mulligan_penalty=penalty,
        )
        print(
            "penalty",
            penalty,
            "utility",
            result.metrics.expected_utility,
            "acceptance",
            result.metrics.acceptance_probability,
        )

    for name, policy in (
        ("selective", selective),
        ("accept-all", accept_all),
    ):
        prize_rates = [
            specific_class_card_prize_probability(
                60,
                6,
                forced_starters=4,
                optional_group_sizes=(4,),
                feature_group_sizes=(4,),
                optional_policy=policy,
                class_index=index,
            )
            for index in range(4)
        ]
        print(name, "Prize rates", prize_rates)


if __name__ == "__main__":
    main()
